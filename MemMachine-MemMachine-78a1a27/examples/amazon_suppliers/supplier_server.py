import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import asyncpg
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_constructor import SupplierQueryConstructor
from database import (
    create_supplier_profiles_table,
    get_supplier_profile,
    upsert_supplier_profile,
    search_suppliers,
    find_supplier_by_name
)

load_dotenv()

MEMORY_BACKEND_URL = os.getenv("MEMORY_BACKEND_URL", "http://localhost:8080")
SUPPLIER_PORT = int(os.getenv("SUPPLIER_PORT", "8001"))

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "memmachine"),
}

app = FastAPI(title="Amazon Supplier Management", description="Supplier data management with MemMachine")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

query_constructor = SupplierQueryConstructor()
logger = logging.getLogger(__name__)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(**DB_CONFIG)
        # Create tables on startup
        await create_supplier_profiles_table(db_pool)
    return db_pool


@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup"""
    try:
        pool = await get_db_pool()
        logger.info("Database connection pool initialized successfully")

        # Auto-seed CRM supplier profiles if empty to ensure demo readiness
        try:
            async with pool.acquire() as conn:
                supplier_count = await conn.fetchval("SELECT COUNT(*) FROM supplier_profiles")

            if supplier_count == 0:
                logger.info("Supplier CRM table empty – seeding sample suppliers for demo")
                from add_sample_suppliers import SAMPLE_SUPPLIERS  # noqa: WPS433 (import inside function)

                seeded = 0
                for supplier in SAMPLE_SUPPLIERS:
                    try:
                        await upsert_supplier_profile(pool, supplier)
                        seeded += 1
                    except Exception as seed_err:  # pragma: no cover - best effort logging
                        logger.warning(
                            "Failed seeding supplier %s: %s",
                            supplier.get("supplier_id", "unknown"),
                            seed_err,
                        )

                logger.info("Seeded %s sample suppliers into CRM", seeded)
        except Exception as seed_exception:  # pragma: no cover - seeding is best-effort
            logger.warning("Supplier seeding skipped due to error: %s", seed_exception)
    except Exception as e:
        logger.warning(f"Database connection failed: {e}. CRM features will not be available. Please check PostgreSQL configuration.")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection pool on shutdown"""
    global db_pool
    if db_pool:
        await db_pool.close()


# Pydantic models for request/response
class SupplierIngestRequest(BaseModel):
    comments: str
    interaction_date: Optional[str] = None


class SupplierQueryRequest(BaseModel):
    query: str


class SupplierStoreAndQueryRequest(BaseModel):
    comments: str
    query: str


class SupplierChatRequest(BaseModel):
    messages: list[dict]
    supplier_id: str
    model_id: Optional[str] = "gpt-4.1-mini"


class SupplierProfileRequest(BaseModel):
    supplier_id: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    products: Optional[str] = None
    capacity: Optional[str] = None
    certifications: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = "Active"
    contract_value: Optional[str] = None
    last_interaction: Optional[str] = None
    notes: Optional[str] = None


@app.post("/supplier/ingest")
async def ingest_supplier_data(request: SupplierIngestRequest):
    """
    Ingest supplier comments into memory system.
    Supplier ID is extracted from comments.
    Comments are stored in episodic memory.
    Profile information is extracted and stored in profile memory.
    CRM data is fetched and merged with profile memory.
    """
    try:
        comments = request.comments
        
        # Extract supplier ID from comments
        supplier_id = _extract_supplier_id(comments)
        logger.info(f"Extracted supplier ID: {supplier_id} from comments")
        
        session_data = {
            "group_id": "amazon_suppliers",
            "agent_id": ["supplier_manager"],
            "user_id": ["amazon_admin"],
            "session_id": f"supplier_{supplier_id}",
        }
        
        # Get interaction date from request or use current timestamp
        interaction_timestamp = request.interaction_date if request.interaction_date else datetime.now().isoformat()
        interaction_date_str = request.interaction_date if request.interaction_date else datetime.now().strftime("%Y-%m-%d")
        
        # Step 1: Store comments in episodic memory (reviews/comments)
        # Include date context in the episode content
        episode_content = comments
        if request.interaction_date:
            episode_content = f"Date: {interaction_date_str}\n\n{comments}"
        
        episode_data = {
            "session": session_data,
            "producer": "amazon_admin",
            "produced_for": "supplier_manager",
            "episode_content": episode_content,
            "episode_type": "supplier_comments",
            "metadata": {
                "supplier_id": supplier_id,
                "timestamp": interaction_timestamp,
                "interaction_date": interaction_date_str,
                "data_type": "comments",
            },
        }
        
        # Store in episodic memory
        episodic_response = requests.post(
            f"{MEMORY_BACKEND_URL}/v1/memories/episodic",
            json=episode_data,
            timeout=1000
        )
        episodic_response.raise_for_status()
        
        # Step 2: Extract profile information and store in profile memory
        # The profile memory will automatically extract profile characteristics from comments
        profile_episode_data = {
            "session": session_data,
            "producer": "amazon_admin",
            "produced_for": "supplier_manager",
            "episode_content": comments,
            "episode_type": "supplier_profile",
            "metadata": {
                "supplier_id": supplier_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "profile_extraction",
            },
        }
        
        # Store in profile memory (MemMachine will extract profile characteristics)
        profile_response = requests.post(
            f"{MEMORY_BACKEND_URL}/v1/memories/profile",
            json=profile_episode_data,
            timeout=1000
        )
        profile_response.raise_for_status()
        
        # Step 3: Fetch CRM data and store in profile memory
        crm_data = await _fetch_crm_data(supplier_id)
        if crm_data:
            crm_profile_data = {
                "session": session_data,
                "producer": "amazon_admin",
                "produced_for": "supplier_manager",
                "episode_content": _format_crm_data_for_profile(crm_data),
                "episode_type": "supplier_profile",
                "metadata": {
                    "supplier_id": supplier_id,
                    "timestamp": datetime.now().isoformat(),
                    "data_type": "crm_profile",
                    "crm_data": crm_data,
                },
            }
            
            crm_profile_response = requests.post(
                f"{MEMORY_BACKEND_URL}/v1/memories/profile",
                json=crm_profile_data,
                timeout=1000
            )
            crm_profile_response.raise_for_status()
        
        return {
            "status": "success",
            "supplier_id": supplier_id,
            "message": f"Supplier data processed for {supplier_id}",
            "details": {
                "episodic_memory": "Comments stored",
                "profile_memory": "Profile information extracted",
                "crm_data": "Fetched and mapped" if crm_data else "No CRM data found"
            }
        }
    except Exception as e:
        logger.exception(f"Error ingesting supplier data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/supplier/query")
async def query_supplier(request: SupplierQueryRequest):
    """
    Query supplier information with contextual memory.
    Supplier ID is extracted from the query, and CRM data is fetched by ID or name.
    """
    try:
        query = request.query
        
        # Extract supplier identifier from query (could be ID, name, or company)
        extracted_identifier = _extract_supplier_id(query)
        logger.info(f"Extracted supplier identifier: {extracted_identifier} from query")
        
        # First, try to find the actual supplier_id from CRM database
        # This handles cases where user queries by name instead of ID
        pool = await get_db_pool()
        crm_profile = None
        
        # Try multiple lookup strategies:
        import re
        
        # Strategy 1: Try normalized query first (removes stop words) - this catches "tell me about techglobal" -> "techglobal"
        stop_words = ['the', 'and', 'for', 'with', 'about', 'tell', 'me', 'show', 'give', 'what', 'who', 'when', 'where', 'how', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'do', 'does', 'did']
        normalized_query = re.sub(r'\b(' + '|'.join(stop_words) + r')\b', '', query, flags=re.IGNORECASE)
        normalized_query = re.sub(r'\s+', ' ', normalized_query).strip()
        logger.info(f"Strategy 1: Normalized query from '{query}' -> '{normalized_query}'")
        if len(normalized_query) >= 3:  # At least 3 characters
            crm_profile = await find_supplier_by_name(pool, normalized_query)
            if crm_profile:
                logger.info(f"✅ Strategy 1 SUCCESS: Found supplier by normalized query: '{normalized_query}' -> {crm_profile.get('supplier_id')} - {crm_profile.get('company_name')}")
            else:
                logger.info(f"❌ Strategy 1 FAILED: No supplier found for normalized query: '{normalized_query}'")
        
        # Strategy 2: Try to find by extracted supplier_id
        if not crm_profile:
            crm_profile = await get_supplier_profile(pool, extracted_identifier)
            if crm_profile:
                logger.info(f"Found supplier by extracted ID: {extracted_identifier}")
        
        # Strategy 3: Try searching by the extracted identifier as a name
        if not crm_profile:
            crm_profile = await find_supplier_by_name(pool, extracted_identifier)
            if crm_profile:
                logger.info(f"Found supplier by extracted identifier as name: {extracted_identifier}")
        
        # Strategy 4: Try searching by capitalized phrases (company names)
        # This handles cases like "TechGlobal Electronics Inc." better
        if not crm_profile:
            # Look for capitalized phrases that might be company names (including compound words)
            # Pattern matches: "TechGlobal Electronics Inc.", "Premium Apparel Co.", etc.
            company_patterns = re.findall(r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*(?:\s+[A-Za-z]+\.?)?\b', query)
            for pattern in company_patterns:
                # Remove trailing punctuation but keep the pattern
                clean_pattern = pattern.rstrip('.,!?;:')
                if len(clean_pattern) > 5:  # Only try meaningful names
                    crm_profile = await find_supplier_by_name(pool, clean_pattern)
                    if crm_profile:
                        logger.info(f"Found supplier by company name pattern: {clean_pattern}")
                        break
        
        # Strategy 5: Try searching by individual words from the query (prioritize longer words)
        if not crm_profile:
            # Extract all words from the query (capitalized or not, including compound words)
            words = re.findall(r'\b[A-Za-z]{3,}\b', query)  # Words with 3+ letters
            # Sort by length (longest first) to prioritize meaningful words like "techglobal" over "tell"
            words = sorted(words, key=len, reverse=True)
            logger.info(f"Strategy 5: Trying individual words (sorted by length): {words}")
            for word in words:
                if word.lower() not in stop_words + ['inc', 'ltd', 'corp', 'co']:
                    logger.info(f"  Trying word: '{word}'")
                    crm_profile = await find_supplier_by_name(pool, word)
                    if crm_profile:
                        logger.info(f"✅ Strategy 5 SUCCESS: Found supplier by word '{word}' -> {crm_profile.get('supplier_id')} - {crm_profile.get('company_name')}")
                        break
                    else:
                        logger.info(f"  ❌ Word '{word}' did not match any supplier")
        
        # Strategy 6: Try the full query text as a last resort
        if not crm_profile and len(query) > 5:
            crm_profile = await find_supplier_by_name(pool, query)
            if crm_profile:
                logger.info(f"Found supplier by full query text")
        
        # Use the actual supplier_id from CRM if found, otherwise use extracted identifier
        if crm_profile:
            actual_supplier_id = crm_profile.get("supplier_id")
            logger.info(f"✅ Found supplier in CRM: {actual_supplier_id} - {crm_profile.get('company_name')}")
        else:
            actual_supplier_id = extracted_identifier
            logger.warning(f"⚠️ No CRM profile found for '{extracted_identifier}', using extracted identifier: {actual_supplier_id}")
            # Try one more comprehensive search with the actual query
            logger.info(f"Attempting final search with query: '{query}'")
            final_search_result = await find_supplier_by_name(pool, query)
            if final_search_result:
                crm_profile = final_search_result  # Update crm_profile so it's used later
                actual_supplier_id = crm_profile.get("supplier_id")
                logger.info(f"✅ Found supplier in final search: {actual_supplier_id} - {crm_profile.get('company_name')}")
        
        session_data = {
            "group_id": "amazon_suppliers",
            "agent_id": ["supplier_manager"],
            "user_id": ["amazon_admin"],
            "session_id": f"supplier_{actual_supplier_id}",
        }
        
        search_data = {
            "session": session_data,
            "query": f"{query} for supplier {actual_supplier_id}",
            "limit": 20,
            "filter": {},
        }
        
        response = requests.post(
            f"{MEMORY_BACKEND_URL}/v1/memories/search",
            json=search_data,
            timeout=1000
        )
        response.raise_for_status()
        
        search_results = response.json()
        content = search_results.get("content", {})
        episodic_memory = content.get("episodic_memory", [])
        profile_memory = content.get("profile_memory", [])
        
        # Fetch current CRM data using the actual supplier_id
        # But if we already found crm_profile, use it directly to avoid double lookup
        crm_data = None
        if crm_profile:
            # Use the CRM profile we already found - convert to expected format
            crm_data = {
                "supplier_id": crm_profile.get("supplier_id"),
                "company_name": crm_profile.get("company_name"),
                "contact_name": crm_profile.get("contact_name"),
                "contact_email": crm_profile.get("contact_email"),
                "contact_phone": crm_profile.get("contact_phone"),
                "address": crm_profile.get("address"),
                "products": crm_profile.get("products"),
                "capacity": crm_profile.get("capacity"),
                "certifications": crm_profile.get("certifications"),
                "website": crm_profile.get("website"),
                "status": crm_profile.get("status"),
                "contract_value": crm_profile.get("contract_value"),
                "last_interaction": str(crm_profile.get("last_interaction")) if crm_profile.get("last_interaction") else None,
                "notes": crm_profile.get("notes"),
            }
            logger.info(f"✅ Using CRM profile found by lookup: {crm_data.get('supplier_id')} - {crm_data.get('company_name')}")
        else:
            # Try to fetch CRM data if we didn't find it by lookup
            logger.info(f"⚠️ crm_profile is None, attempting to fetch CRM data for: {actual_supplier_id}")
            crm_data = await _fetch_crm_data(actual_supplier_id)
            if crm_data:
                logger.info(f"✅ Fetched CRM data via _fetch_crm_data: {crm_data.get('supplier_id')} - {crm_data.get('company_name')}")
            else:
                logger.warning(f"⚠️ No CRM data found for supplier {actual_supplier_id}")
                # Try searching by the original query one more time
                logger.info(f"🔍 Final attempt: searching by query text: '{query}'")
                final_search = await find_supplier_by_name(pool, query)
                if final_search:
                    crm_data = {
                        "supplier_id": final_search.get("supplier_id"),
                        "company_name": final_search.get("company_name"),
                        "contact_name": final_search.get("contact_name"),
                        "contact_email": final_search.get("contact_email"),
                        "contact_phone": final_search.get("contact_phone"),
                        "address": final_search.get("address"),
                        "products": final_search.get("products"),
                        "capacity": final_search.get("capacity"),
                        "certifications": final_search.get("certifications"),
                        "website": final_search.get("website"),
                        "status": final_search.get("status"),
                        "contract_value": final_search.get("contract_value"),
                        "last_interaction": str(final_search.get("last_interaction")) if final_search.get("last_interaction") else None,
                        "notes": final_search.get("notes"),
                    }
                    actual_supplier_id = final_search.get("supplier_id")
                    logger.info(f"✅ Found CRM data in final search: {crm_data.get('supplier_id')} - {crm_data.get('company_name')}")
                else:
                    # Last resort: try searching by normalized query again
                    logger.info(f"🔍 Last resort: trying normalized query again: '{normalized_query}'")
                    last_resort = await find_supplier_by_name(pool, normalized_query)
                    if last_resort:
                        crm_data = {
                            "supplier_id": last_resort.get("supplier_id"),
                            "company_name": last_resort.get("company_name"),
                            "contact_name": last_resort.get("contact_name"),
                            "contact_email": last_resort.get("contact_email"),
                            "contact_phone": last_resort.get("contact_phone"),
                            "address": last_resort.get("address"),
                            "products": last_resort.get("products"),
                            "capacity": last_resort.get("capacity"),
                            "certifications": last_resort.get("certifications"),
                            "website": last_resort.get("website"),
                            "status": last_resort.get("status"),
                            "contract_value": last_resort.get("contract_value"),
                            "last_interaction": str(last_resort.get("last_interaction")) if last_resort.get("last_interaction") else None,
                            "notes": last_resort.get("notes"),
                        }
                        actual_supplier_id = last_resort.get("supplier_id")
                        logger.info(f"✅ Found CRM data in last resort search: {crm_data.get('supplier_id')} - {crm_data.get('company_name')}")
        
        # Format episodic memory (all comments/reviews) with date context
        context_str = _format_episodic_memory_with_dates(episodic_memory)
        
        # Format profile memory (from CRM + extracted from comments)
        # Prioritize CRM data - put it first so LLM sees it clearly
        profile_str = ""
        if crm_data:
            logger.info(f"Formatting CRM data for supplier {actual_supplier_id}: {list(crm_data.keys())}")
            logger.info(f"CRM data sample: company_name={crm_data.get('company_name')}, contact_name={crm_data.get('contact_name')}")
            crm_profile_str = _format_crm_data_for_profile(crm_data)
            profile_str = crm_profile_str
            logger.info(f"CRM profile string length: {len(profile_str)}")
            logger.info(f"CRM profile string preview (first 500 chars): {profile_str[:500]}")
        else:
            logger.warning(f"No CRM data found for supplier {actual_supplier_id}")
            # Try one more time with the extracted identifier directly
            if extracted_identifier != actual_supplier_id:
                logger.info(f"Retrying CRM fetch with extracted identifier: {extracted_identifier}")
                crm_data_retry = await _fetch_crm_data(extracted_identifier)
                if crm_data_retry:
                    logger.info(f"Found CRM data with retry for {extracted_identifier}")
                    crm_profile_str = _format_crm_data_for_profile(crm_data_retry)
                    profile_str = crm_profile_str
                    crm_data = crm_data_retry
        
        # Add extracted profile memory from comments if available
        extracted_profile = _format_profile_memory(profile_memory)
        if extracted_profile:
            if profile_str:
                profile_str = f"{profile_str}\n\n--- Additional Profile Information from Comments ---\n{extracted_profile}"
            else:
                profile_str = extracted_profile
        
        # CRITICAL: Ensure CRM data is always included if it exists
        if crm_data and "=== CRM PROFILE DATA ===" not in profile_str:
            logger.warning(f"CRM data exists but not in profile_str! Forcing inclusion. CRM: {crm_data.get('company_name')}")
            crm_profile_str = _format_crm_data_for_profile(crm_data)
            if profile_str:
                profile_str = crm_profile_str + (f"\n\n--- Additional Profile Information from Comments ---\n{extracted_profile}" if extracted_profile else f"\n\n{profile_str}")
            else:
                profile_str = crm_profile_str + (f"\n\n--- Additional Profile Information from Comments ---\n{extracted_profile}" if extracted_profile else "")
        
        if not profile_str:
            if crm_data:
                # If we have CRM data but profile_str is still empty, force it
                logger.warning(f"profile_str is empty but CRM data exists! Forcing CRM data inclusion.")
                profile_str = _format_crm_data_for_profile(crm_data)
            else:
                profile_str = "No profile memory available for this supplier."
                logger.warning(f"No profile data available for supplier {actual_supplier_id}")
        
        logger.info(f"Final profile_str length: {len(profile_str)}, preview: {profile_str[:200]}...")
        logger.info(f"CRM data included: {'Yes' if crm_data else 'No'}, CRM company: {crm_data.get('company_name') if crm_data else 'N/A'}")
        
        # Create formatted query for LLM
        formatted_query = query_constructor.create_query(
            profile=profile_str,
            context=context_str,
            query=query,
            supplier_id=actual_supplier_id
        )
        
        # Verify CRM data is in formatted query
        if crm_data and "=== CRM PROFILE DATA ===" not in formatted_query:
            logger.error(f"CRITICAL: CRM data exists but not found in formatted_query!")
            logger.error(f"Formatted query preview (first 1000 chars): {formatted_query[:1000]}")
        
        # CRITICAL: Always include CRM data in response, even if LLM doesn't use it
        # This ensures frontend fallback can display it
        response_data = {
            "status": "success",
            "supplier_id": actual_supplier_id,
            "data": {
                "profile": profile_memory,
                "context": episodic_memory,
                "crm_profile": crm_data,  # Always include CRM data
            },
            "formatted_query": formatted_query,
        }
        
        # Log final response for debugging
        if crm_data:
            logger.info(f"✅ Returning CRM data in response: {crm_data.get('supplier_id')} - {crm_data.get('company_name')}")
        else:
            logger.warning(f"⚠️ No CRM data in response for supplier: {actual_supplier_id}")
        
        return response_data
    except Exception as e:
        logger.exception(f"Error querying supplier: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def supplier_health():
    """Return health information for the supplier service and dependencies."""

    memmachine_health: dict[str, str | dict] = {"status": "unknown"}
    try:
        memmachine_response = requests.get(
            f"{MEMORY_BACKEND_URL}/health", timeout=5
        )
        memmachine_response.raise_for_status()
        memmachine_health = memmachine_response.json()
        memmachine_health.setdefault("status", "healthy")
    except requests.RequestException as exc:  # pragma: no cover - best effort
        logger.warning("MemMachine health check failed: %s", exc)
        memmachine_health = {"status": "unreachable", "detail": str(exc)}

    db_status = "unknown"
    db_error: str | None = None
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
        db_status = "healthy"
    except Exception as exc:  # pragma: no cover - dependent on environment
        db_status = "unavailable"
        db_error = str(exc)
        logger.warning("PostgreSQL health check failed: %s", exc)

    return {
        "service": "amazon_supplier",
        "status": "healthy"
        if memmachine_health.get("status") == "healthy" and db_status == "healthy"
        else "degraded",
        "dependencies": {
            "memmachine": memmachine_health,
            "postgres": {"status": db_status, "detail": db_error},
        },
    }


@app.post("/supplier/chat")
async def chat_with_supplier(request: SupplierChatRequest):
    """
    Chat with LLM about supplier information.
    This endpoint handles LLM chat requests from the frontend.
    
    The messages should contain the formatted_query from /supplier/query endpoint.
    This function parses the formatted query to extract system prompt and user query.
    """
    try:
        # Import LLM functions from the frontend module
        import sys
        import os
        import re
        from dotenv import load_dotenv
        
        # Ensure .env is loaded from the supplier directory (parent of frontend)
        supplier_dir = os.path.dirname(__file__)
        env_path = os.path.join(supplier_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
        
        frontend_path = os.path.join(supplier_dir, "frontend")
        if frontend_path not in sys.path:
            sys.path.insert(0, frontend_path)
        
        from llm import chat, set_model
        
        # Set the model
        set_model(request.model_id)
        
        # Parse the formatted query if it's a single user message with XML tags
        messages_to_send = request.messages
        if len(messages_to_send) == 1 and messages_to_send[0].get("role") == "user":
            content = messages_to_send[0]["content"]
            
            # Check if content contains XML-structured prompt
            if "<SYSTEM_PROMPT>" in content and "<USER_QUERY>" in content:
                # Extract system prompt
                system_match = re.search(r'<SYSTEM_PROMPT>(.*?)</SYSTEM_PROMPT>', content, re.DOTALL)
                user_match = re.search(r'<USER_QUERY>(.*?)</USER_QUERY>', content, re.DOTALL)
                
                if system_match and user_match:
                    system_prompt = system_match.group(1).strip()
                    user_query = user_match.group(1).strip()
                    
                    # Reconstruct the full prompt (keep the XML structure for instructions)
                    # The LLM needs the full context including instructions
                    full_prompt = content  # Send the full formatted query as-is
                    
                    # For OpenAI API, we can send system prompt separately
                    messages_to_send = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ]
                    logger.info(f"Parsed system prompt ({len(system_prompt)} chars) and user query ({len(user_query)} chars)")
                else:
                    # If parsing fails, send as-is
                    logger.warning("Could not parse XML structure, sending formatted query as-is")
                    messages_to_send = [{"role": "user", "content": content}]
            else:
                # No XML structure, send as-is
                messages_to_send = [{"role": "user", "content": content}]
        
        logger.info(f"Sending {len(messages_to_send)} messages to LLM")
        
        # Call the chat function
        response_text, latency, tokens, tps = chat(messages_to_send, request.supplier_id)
        
        return {
            "status": "success",
            "response": response_text,
            "metadata": {
                "latency": latency,
                "tokens": tokens,
                "tokens_per_second": tps,
                "model": request.model_id,
            }
        }
    except Exception as e:
        logger.exception(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/supplier/store-and-query")
async def store_and_query_supplier(request: SupplierStoreAndQueryRequest):
    """
    Store supplier data and immediately get contextual response.
    """
    try:
        # Extract data from request
        comments = request.comments
        query = request.query
        
        # Create ingest request
        ingest_request = SupplierIngestRequest(
            comments=comments
        )
        
        # First ingest the data
        ingest_result = await ingest_supplier_data(ingest_request)
        supplier_id = ingest_result.get("supplier_id", "Unknown")
        
        # Create query request
        query_request = SupplierQueryRequest(
            query=query
        )
        
        # Then query
        query_result = await query_supplier(query_request)
        
        return {
            "status": "success",
            "ingest_result": ingest_result,
            "query_result": query_result,
        }
    except Exception as e:
        logger.exception(f"Error in store and query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# CRM Profile Management Endpoints
@app.post("/crm/supplier/profile")
async def add_supplier_profile(request: SupplierProfileRequest):
    """
    Add or update supplier profile in CRM database.
    """
    try:
        pool = await get_db_pool()
        
        # Convert Pydantic model to dict, excluding None values
        profile_data = request.model_dump(exclude_none=True)
        
        # Ensure supplier_id is present
        if not profile_data.get("supplier_id"):
            raise HTTPException(status_code=400, detail="supplier_id is required")
        
        result = await upsert_supplier_profile(pool, profile_data)
        
        return {
            "status": "success",
            "message": f"Supplier profile saved for {request.supplier_id}",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error saving supplier profile: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/crm/supplier/profile/{supplier_id}")
async def get_supplier_profile_endpoint(supplier_id: str):
    """
    Get supplier profile from CRM database.
    """
    try:
        pool = await get_db_pool()
        profile = await get_supplier_profile(pool, supplier_id)
        
        if profile:
            return {
                "status": "success",
                "data": profile
            }
        else:
            raise HTTPException(status_code=404, detail=f"Supplier profile not found for {supplier_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching supplier profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crm/suppliers")
async def list_suppliers(search: Optional[str] = None):
    """
    List all suppliers or search suppliers.
    """
    try:
        pool = await get_db_pool()
        suppliers = await search_suppliers(pool, search)
        
        return {
            "status": "success",
            "count": len(suppliers),
            "data": suppliers
        }
    except Exception as e:
        logger.exception(f"Error listing suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supplier/test-lookup/{search_term}")
async def test_supplier_lookup(search_term: str):
    """
    Test endpoint to verify supplier lookup is working.
    Use this to debug why suppliers aren't being found.
    """
    try:
        pool = await get_db_pool()
        
        # Try all lookup methods
        results = {
            "search_term": search_term,
            "methods": {}
        }
        
        # Method 1: find_supplier_by_name
        from database import find_supplier_by_name, get_supplier_profile, search_suppliers
        result1 = await find_supplier_by_name(pool, search_term)
        results["methods"]["find_supplier_by_name"] = {
            "found": result1 is not None,
            "data": result1
        }
        
        # Method 2: get_supplier_profile
        result2 = await get_supplier_profile(pool, search_term)
        results["methods"]["get_supplier_profile"] = {
            "found": result2 is not None,
            "data": result2
        }
        
        # Method 3: search_suppliers
        result3 = await search_suppliers(pool, search_term)
        results["methods"]["search_suppliers"] = {
            "found": len(result3) > 0,
            "count": len(result3),
            "data": result3[:5]  # First 5 results
        }
        
        # Method 4: Direct SQL query
        async with pool.acquire() as conn:
            direct_query = await conn.fetch(
                """
                SELECT supplier_id, company_name, contact_name 
                FROM supplier_profiles 
                WHERE LOWER(company_name) LIKE LOWER($1) 
                LIMIT 5
                """,
                f"%{search_term}%"
            )
            results["methods"]["direct_sql_query"] = {
                "found": len(direct_query) > 0,
                "count": len(direct_query),
                "data": [dict(row) for row in direct_query]
            }
            
            # Also check all suppliers
            all_suppliers = await conn.fetch(
                "SELECT supplier_id, company_name FROM supplier_profiles LIMIT 10"
            )
            results["all_suppliers_sample"] = [dict(row) for row in all_suppliers]
        
        return results
    except Exception as e:
        logger.exception(f"Error in test lookup: {e}")
        return {"error": str(e)}


async def _fetch_crm_data(supplier_id: str) -> Optional[dict]:
    """
    Fetch CRM data for a supplier from PostgreSQL database.
    First tries by supplier_id, then by company/contact name.
    Also tries partial matches and search.
    """
    try:
        pool = await get_db_pool()
        
        # First try to get by supplier_id
        profile = await get_supplier_profile(pool, supplier_id)
        
        # If not found, try searching by name (company name or contact name)
        if not profile:
            profile = await find_supplier_by_name(pool, supplier_id)
            if profile:
                logger.info(f"Found supplier by name '{supplier_id}': {profile.get('supplier_id')}")
        
        # If still not found, try search_suppliers for partial matches
        if not profile:
            from database import search_suppliers
            search_results = await search_suppliers(pool, supplier_id)
            if search_results and len(search_results) > 0:
                profile = search_results[0]  # Take the first match
                logger.info(f"Found supplier via search '{supplier_id}': {profile.get('supplier_id')}")
        
        if profile:
            logger.info(f"Fetched CRM data for supplier: {profile.get('supplier_id')}")
            # Convert to dict format expected by the rest of the system
            return {
                "supplier_id": profile.get("supplier_id"),
                "company_name": profile.get("company_name"),
                "contact_name": profile.get("contact_name"),
                "contact_email": profile.get("contact_email"),
                "contact_phone": profile.get("contact_phone"),
                "address": profile.get("address"),
                "products": profile.get("products"),
                "capacity": profile.get("capacity"),
                "certifications": profile.get("certifications"),
                "website": profile.get("website"),
                "status": profile.get("status"),
                "contract_value": profile.get("contract_value"),
                "last_interaction": str(profile.get("last_interaction")) if profile.get("last_interaction") else None,
                "notes": profile.get("notes"),
            }
        else:
            logger.info(f"No CRM data found for supplier: {supplier_id}")
            return None
    except Exception as e:
        logger.exception(f"Error fetching CRM data for supplier {supplier_id}: {e}")
        return None


def _extract_supplier_id(text: str) -> str:
    """
    Extract supplier ID from text using pattern matching and heuristics.
    Looks for patterns like: SUP-001, Supplier: XXX, Supplier ID: XXX, etc.
    Normalizes the ID format for database lookup.
    """
    import re
    
    # Pattern 1: SUP-XXX or SUP_XXX (with prefix)
    pattern1 = re.search(r'SUP[-_]?(\d+)', text, re.IGNORECASE)
    if pattern1:
        num = pattern1.group(1)
        # Normalize to SUP-XXX format (preserve leading zeros if present)
        return f"SUP-{num}"
    
    # Pattern 2: Just numbers after "supplier" (e.g., "supplier 002" or "supplier 2")
    pattern2 = re.search(r'supplier\s+(\d+)', text, re.IGNORECASE)
    if pattern2:
        num = pattern2.group(1)
        # Normalize: pad with leading zero if single digit, otherwise use as-is
        # This handles both "002" and "2" formats
        return f"SUP-{num.zfill(3)}"  # e.g., "2" -> "SUP-002", "002" -> "SUP-002"
    
    # Pattern 3: "Supplier ID: XXX" or "Supplier: XXX"
    pattern3 = re.search(r'Supplier\s*(?:ID)?\s*:?\s*([A-Z0-9\-_]+)', text, re.IGNORECASE)
    if pattern3:
        id_str = pattern3.group(1).strip()
        # If it's just a number, normalize it
        if id_str.isdigit():
            return f"SUP-{id_str.zfill(3)}"
        return id_str
    
    # Pattern 4: "Supplier XXX" at the beginning
    pattern4 = re.search(r'^Supplier\s+([A-Z0-9\-_]+)', text, re.IGNORECASE | re.MULTILINE)
    if pattern4:
        id_str = pattern4.group(1).strip()
        # If it's just a number, normalize it
        if id_str.isdigit():
            return f"SUP-{id_str.zfill(3)}"
        return id_str
    
    # Pattern 5: Look for company name and use it as identifier
    company_pattern = re.search(r'Company\s*:?\s*([A-Z][A-Za-z0-9\s&]+)', text, re.IGNORECASE)
    if company_pattern:
        company_name = company_pattern.group(1).strip()
        # Normalize company name to use as ID
        normalized = re.sub(r'[^A-Z0-9]', '_', company_name.upper())
        return normalized[:50]  # Limit length
    
    # Fallback: Use first few words or generate hash-based ID
    words = text.split()
    if len(words) > 0:
        # Use first capitalized word/phrase as identifier
        first_phrase = words[0]
        if len(words) > 1 and words[1][0].isupper():
            first_phrase = f"{words[0]}_{words[1]}"
        return first_phrase.upper().replace(' ', '_')[:30]
    
    # Ultimate fallback: Generate ID from hash
    import hashlib
    hash_id = hashlib.md5(text.encode()).hexdigest()[:8].upper()
    return f"SUP-{hash_id}"


def _format_crm_data_for_profile(crm_data: dict) -> str:
    """Format CRM data as structured text for profile memory storage.
    Format it in a way that's easy for LLM to copy directly."""
    parts = ["=== CRM PROFILE DATA ==="]
    parts.append("")
    parts.append("CRITICAL: You MUST include ALL of the following information in your Profile Information section.")
    parts.append("")
    parts.append("EXACT TEXT TO COPY TO PROFILE INFORMATION SECTION:")
    parts.append("")
    
    # Basic Information - only include fields that have values
    if crm_data.get("company_name"):
        parts.append("• Company Name: " + str(crm_data.get("company_name")))
    if crm_data.get("contact_name"):
        parts.append("• Contact Person: " + str(crm_data.get("contact_name")))
    if crm_data.get("contact_email"):
        parts.append("• Email: " + str(crm_data.get("contact_email")))
    if crm_data.get("contact_phone"):
        parts.append("• Phone: " + str(crm_data.get("contact_phone")))
    if crm_data.get("address"):
        parts.append("• Address: " + str(crm_data.get("address")))
    if crm_data.get("website"):
        parts.append("• Website: " + str(crm_data.get("website")))
    
    # Business Information
    if crm_data.get("products"):
        parts.append("• Products/Services: " + str(crm_data.get("products")))
    if crm_data.get("capacity"):
        parts.append("• Capacity: " + str(crm_data.get("capacity")))
    if crm_data.get("certifications"):
        parts.append("• Certifications: " + str(crm_data.get("certifications")))
    
    # CRM Information - supplier_id and status are usually present
    if crm_data.get("supplier_id"):
        parts.append("• CRM ID (Supplier ID): " + str(crm_data.get("supplier_id")))
    if crm_data.get("status"):
        parts.append("• Account Status: " + str(crm_data.get("status")))
    if crm_data.get("contract_value"):
        parts.append("• Contract Value: " + str(crm_data.get("contract_value")))
    if crm_data.get("last_interaction"):
        parts.append("• Last Interaction: " + str(crm_data.get("last_interaction")))
    if crm_data.get("notes"):
        parts.append("• Notes: " + str(crm_data.get("notes")))
    
    parts.append("")
    parts.append("CRITICAL INSTRUCTIONS:")
    parts.append("- Copy ALL the bulleted lines above (with • bullets) EXACTLY as shown")
    parts.append("- Display them in your Profile Information section")
    parts.append("- DO NOT use '(na)' for any field that appears above with a value")
    parts.append("- The Profile Information section is MANDATORY and must appear in your response")
    
    return "\n".join(parts)


def _format_profile_memory(profile_memory: list) -> str:
    """Format profile memory for display."""
    if not profile_memory:
        return ""
    if isinstance(profile_memory, list):
        return "\n".join([str(p) for p in profile_memory])
    return str(profile_memory)


def _format_episodic_memory(episodic_memory: list) -> str:
    """Format episodic memory for display."""
    if not episodic_memory:
        return ""
    if isinstance(episodic_memory, list):
        return "\n".join([str(e) for e in episodic_memory])
    return str(episodic_memory)


def _format_episodic_memory_with_dates(episodic_memory: list) -> str:
    """Format episodic memory with date context for better temporal understanding."""
    if not episodic_memory:
        return "No episodic memory available for this supplier."
    
    formatted_entries = []
    for entry in episodic_memory:
        if isinstance(entry, list):
            # Handle nested list structure
            for episode in entry:
                if isinstance(episode, dict):
                    content = episode.get("content", "")
                    timestamp = episode.get("timestamp", "")
                    metadata = episode.get("user_metadata", {})
                    interaction_date = metadata.get("interaction_date", "") or metadata.get("timestamp", "")
                    
                    # Extract date from timestamp if available
                    if timestamp:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            date_str = dt.strftime("%Y-%m-%d")
                            if date_str not in content[:50]:  # Avoid duplication if date already in content
                                formatted_entries.append(f"[Date: {date_str}] {content}")
                            else:
                                formatted_entries.append(content)
                        except:
                            formatted_entries.append(content)
                    elif interaction_date:
                        try:
                            # Try to parse interaction_date
                            if isinstance(interaction_date, str) and len(interaction_date) >= 10:
                                date_str = interaction_date[:10]  # Extract YYYY-MM-DD
                                formatted_entries.append(f"[Date: {date_str}] {content}")
                            else:
                                formatted_entries.append(content)
                        except:
                            formatted_entries.append(content)
                    else:
                        formatted_entries.append(content)
                else:
                    formatted_entries.append(str(episode))
        elif isinstance(entry, dict):
            content = entry.get("content", "")
            timestamp = entry.get("timestamp", "")
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d")
                    formatted_entries.append(f"[Date: {date_str}] {content}")
                except:
                    formatted_entries.append(content)
            else:
                formatted_entries.append(content)
        else:
            formatted_entries.append(str(entry))
    
    return "\n\n".join(formatted_entries) if formatted_entries else "No episodic memory available for this supplier."


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SUPPLIER_PORT)

