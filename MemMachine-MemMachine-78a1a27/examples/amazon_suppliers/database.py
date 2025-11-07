"""
Database schema and utilities for supplier CRM profiles
"""
import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def create_supplier_profiles_table(pool: asyncpg.Pool):
    """Create the supplier_profiles table if it doesn't exist"""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS supplier_profiles (
                id SERIAL PRIMARY KEY,
                supplier_id VARCHAR(255) UNIQUE NOT NULL,
                company_name VARCHAR(255),
                contact_name VARCHAR(255),
                contact_email VARCHAR(255),
                contact_phone VARCHAR(100),
                address TEXT,
                products TEXT,
                capacity VARCHAR(255),
                certifications TEXT,
                website VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Active',
                contract_value VARCHAR(100),
                last_interaction DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on supplier_id for faster lookups
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_supplier_id ON supplier_profiles(supplier_id)
        """)
        
        # Create case-insensitive index on company_name for faster lookups
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_name_lower ON supplier_profiles(LOWER(company_name))
        """)
        
        logger.info("Supplier profiles table created/verified")


async def get_supplier_profile(pool: asyncpg.Pool, supplier_id: str) -> Optional[dict]:
    """Get supplier profile by supplier_id (case-insensitive, handles numeric ID variations)"""
    import re
    async with pool.acquire() as conn:
        # First try exact match (case-insensitive)
        row = await conn.fetchrow(
            """
            SELECT 
                supplier_id, company_name, contact_name, contact_email, contact_phone,
                address, products, capacity, certifications, website, status,
                contract_value, last_interaction, notes, created_at, updated_at
            FROM supplier_profiles
            WHERE LOWER(supplier_id) = LOWER($1)
            """,
            supplier_id
        )
        
        if row:
            return dict(row)
        
        # If not found, try to match by numeric part (handles SUP-002 vs Sup-02 vs Sup-2)
        # Extract numeric part and prefix from the search ID
        numeric_match = re.search(r'(\d+)', supplier_id)
        prefix_match = re.search(r'^([A-Za-z\-_]+)', supplier_id)
        search_prefix = prefix_match.group(1).upper() if prefix_match else ""
        
        if numeric_match:
            search_num_str = numeric_match.group(1)
            search_num_int = int(search_num_str)
            
            # Get all suppliers and find one that matches
            all_rows = await conn.fetch(
                """
                SELECT 
                    supplier_id, company_name, contact_name, contact_email, contact_phone,
                    address, products, capacity, certifications, website, status,
                    contract_value, last_interaction, notes, created_at, updated_at
                FROM supplier_profiles
                """
            )
            
            # First, try to find exact prefix match with numeric match
            for row in all_rows:
                db_id = row['supplier_id']
                db_prefix_match = re.search(r'^([A-Za-z\-_]+)', db_id)
                db_prefix = db_prefix_match.group(1).upper() if db_prefix_match else ""
                
                # Extract numeric part from database ID
                db_numeric_match = re.search(r'(\d+)', db_id)
                if db_numeric_match:
                    db_num_str = db_numeric_match.group(1)
                    db_num_int = int(db_num_str)
                    
                    # Prefer exact prefix match (SUP matches SUP, Sup matches Sup)
                    if db_prefix == search_prefix and db_num_int == search_num_int:
                        return dict(row)
            
            # If no prefix match, try just numeric match (fallback)
            for row in all_rows:
                db_id = row['supplier_id']
                db_numeric_match = re.search(r'(\d+)', db_id)
                if db_numeric_match:
                    db_num_str = db_numeric_match.group(1)
                    db_num_int = int(db_num_str)
                    # Match if numeric parts are equal (handles 002 = 2 = 02)
                    if db_num_int == search_num_int:
                        return dict(row)
        
        return None


async def find_supplier_by_name(pool: asyncpg.Pool, name: str) -> Optional[dict]:
    """Find supplier profile by company name or contact name (supports partial word matches)"""
    import re
    
    # Normalize the search term: remove punctuation, extra spaces, convert to lowercase
    normalized_search = re.sub(r'[^\w\s]', '', name.lower().strip())
    
    async with pool.acquire() as conn:
        # First try exact match or substring match (case-insensitive)
        row = await conn.fetchrow(
            """
            SELECT 
                supplier_id, company_name, contact_name, contact_email, contact_phone,
                address, products, capacity, certifications, website, status,
                contract_value, last_interaction, notes, created_at, updated_at
            FROM supplier_profiles
            WHERE 
                LOWER(company_name) = LOWER($1) OR
                LOWER(contact_name) = LOWER($1) OR
                LOWER(company_name) LIKE LOWER($2) OR
                LOWER(contact_name) LIKE LOWER($2) OR
                LOWER(REPLACE(REPLACE(company_name, '.', ''), ',', '')) LIKE LOWER($3) OR
                LOWER(REPLACE(REPLACE(contact_name, '.', ''), ',', '')) LIKE LOWER($3)
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            name,
            f"%{name}%",
            f"%{normalized_search}%"
        )
        
        if row:
            return dict(row)
        
        # If not found, try word-level matching (e.g., "Premium" should match "Premium Apparel Co.")
        # Split the search term into words and try matching each word
        words = normalized_search.split()
        for word in words:
            if len(word) >= 3:  # Only try words with 3+ characters
                # Try matching word boundaries in company name
                row = await conn.fetchrow(
                    """
                    SELECT 
                        supplier_id, company_name, contact_name, contact_email, contact_phone,
                        address, products, capacity, certifications, website, status,
                        contract_value, last_interaction, notes, created_at, updated_at
                    FROM supplier_profiles
                    WHERE 
                        LOWER(company_name) LIKE LOWER($1) OR
                        LOWER(contact_name) LIKE LOWER($1) OR
                        LOWER(REPLACE(REPLACE(company_name, '.', ''), ',', '')) LIKE LOWER($2) OR
                        LOWER(REPLACE(REPLACE(contact_name, '.', ''), ',', '')) LIKE LOWER($2)
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    f"%{word}%",
                    f"%{word}%"
                )
                if row:
                    logger.info(f"Found supplier by partial word match: '{word}' matched '{row['company_name']}'")
                    return dict(row)
        
        # Try matching compound words (e.g., "TechGlobal" should match "TechGlobal Electronics Inc.")
        # Split camelCase/PascalCase words - normalize to lowercase for case-insensitive matching
        compound_words = re.findall(r'[A-Z][a-z]+|[a-z]+', name)
        for word in compound_words:
            if len(word) >= 3:
                # Normalize word to lowercase for case-insensitive matching
                word_lower = word.lower()
                row = await conn.fetchrow(
                    """
                    SELECT 
                        supplier_id, company_name, contact_name, contact_email, contact_phone,
                        address, products, capacity, certifications, website, status,
                        contract_value, last_interaction, notes, created_at, updated_at
                    FROM supplier_profiles
                    WHERE 
                        LOWER(company_name) LIKE LOWER($1) OR
                        LOWER(contact_name) LIKE LOWER($1)
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    f"%{word_lower}%"
                )
                if row:
                    logger.info(f"Found supplier by compound word match: '{word}' matched '{row['company_name']}'")
                    return dict(row)
        
        return None


async def upsert_supplier_profile(pool: asyncpg.Pool, profile_data: dict) -> dict:
    """Insert or update supplier profile"""
    from datetime import datetime
    
    async with pool.acquire() as conn:
        # Parse last_interaction if it's a string
        last_interaction = profile_data.get("last_interaction")
        if last_interaction:
            if isinstance(last_interaction, str):
                try:
                    # Try to parse ISO format date string
                    last_interaction = datetime.fromisoformat(last_interaction.replace('Z', '+00:00')).date()
                except (ValueError, AttributeError):
                    # If parsing fails, try other formats or set to None
                    try:
                        last_interaction = datetime.strptime(last_interaction, "%Y-%m-%d").date()
                    except (ValueError, AttributeError):
                        logger.warning(f"Could not parse last_interaction: {last_interaction}, setting to None")
                        last_interaction = None
        
        row = await conn.fetchrow(
            """
            INSERT INTO supplier_profiles (
                supplier_id, company_name, contact_name, contact_email, contact_phone,
                address, products, capacity, certifications, website, status,
                contract_value, last_interaction, notes, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, CURRENT_TIMESTAMP)
            ON CONFLICT (supplier_id) 
            DO UPDATE SET
                company_name = EXCLUDED.company_name,
                contact_name = EXCLUDED.contact_name,
                contact_email = EXCLUDED.contact_email,
                contact_phone = EXCLUDED.contact_phone,
                address = EXCLUDED.address,
                products = EXCLUDED.products,
                capacity = EXCLUDED.capacity,
                certifications = EXCLUDED.certifications,
                website = EXCLUDED.website,
                status = EXCLUDED.status,
                contract_value = EXCLUDED.contract_value,
                last_interaction = EXCLUDED.last_interaction,
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
            RETURNING 
                supplier_id, company_name, contact_name, contact_email, contact_phone,
                address, products, capacity, certifications, website, status,
                contract_value, last_interaction, notes, created_at, updated_at
            """,
            profile_data.get("supplier_id"),
            profile_data.get("company_name"),
            profile_data.get("contact_name"),
            profile_data.get("contact_email"),
            profile_data.get("contact_phone"),
            profile_data.get("address"),
            profile_data.get("products"),
            profile_data.get("capacity"),
            profile_data.get("certifications"),
            profile_data.get("website"),
            profile_data.get("status", "Active"),
            profile_data.get("contract_value"),
            last_interaction,
            profile_data.get("notes")
        )
        
        return dict(row)


async def search_suppliers(pool: asyncpg.Pool, search_term: str = None) -> list:
    """Search suppliers by various fields"""
    async with pool.acquire() as conn:
        if search_term:
            rows = await conn.fetch(
                """
                SELECT 
                    supplier_id, company_name, contact_name, contact_email, status
                FROM supplier_profiles
                WHERE 
                    supplier_id ILIKE $1 OR
                    company_name ILIKE $1 OR
                    contact_name ILIKE $1 OR
                    contact_email ILIKE $1
                ORDER BY updated_at DESC
                LIMIT 50
                """,
                f"%{search_term}%"
            )
        else:
            rows = await conn.fetch(
                """
                SELECT 
                    supplier_id, company_name, contact_name, contact_email, status
                FROM supplier_profiles
                ORDER BY updated_at DESC
                LIMIT 50
                """
            )
        
        return [dict(row) for row in rows]

