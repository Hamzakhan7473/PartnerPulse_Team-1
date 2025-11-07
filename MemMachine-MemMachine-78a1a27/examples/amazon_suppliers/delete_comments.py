#!/usr/bin/env python3
"""
Script to delete all supplier comments/interactions from episodic memory.
This will clear all comments stored in MemMachine but keep the CRM profiles in the database.
"""
import asyncio
import os
import requests
from dotenv import load_dotenv
import asyncpg

load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "memmachine"),
}

# MemMachine backend URL
MEMORY_BACKEND_URL = os.getenv("MEMORY_BACKEND_URL", "http://localhost:8080")


async def get_all_supplier_ids():
    """Get all supplier IDs from the database"""
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        async with pool.acquire() as conn:
            supplier_ids = await conn.fetch("SELECT DISTINCT supplier_id FROM supplier_profiles")
            ids = [row['supplier_id'] for row in supplier_ids]
        await pool.close()
        return ids
    except Exception as e:
        print(f"❌ Error fetching supplier IDs: {e}")
        return []


def delete_supplier_comments(supplier_id: str) -> bool:
    """Delete all comments/memories for a specific supplier"""
    try:
        # Construct the session data matching how supplier_server.py stores data
        # Note: user_id is "amazon_admin", not the supplier_id
        session_data = {
            "group_id": "amazon_suppliers",
            "agent_id": ["supplier_manager"],
            "user_id": ["amazon_admin"],
            "session_id": f"supplier_{supplier_id}",
        }
        
        delete_request = {
            "session": session_data
        }
        
        # Call the DELETE endpoint with longer timeout for large deletions
        response = requests.delete(
            f"{MEMORY_BACKEND_URL}/v1/memories",
            json=delete_request,
            timeout=30  # Increased timeout for large deletions
        )
        
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            # Session doesn't exist - that's okay, no comments to delete
            return True
        else:
            print(f"   ⚠️  Unexpected status code {response.status_code} for {supplier_id}")
            if response.text:
                print(f"      Response: {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout deleting {supplier_id} (may still be processing)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error deleting comments for {supplier_id}: {e}")
        return False


async def main():
    """Main function to delete all supplier comments"""
    print("=" * 60)
    print("🗑️  DELETING ALL SUPPLIER COMMENTS FROM MEMORY")
    print("=" * 60)
    
    # Step 1: Get all supplier IDs
    print("\n📋 Step 1: Fetching supplier IDs from database...")
    supplier_ids = await get_all_supplier_ids()
    
    if not supplier_ids:
        print("ℹ️  No suppliers found in database. Nothing to delete.")
        return
    
    print(f"   Found {len(supplier_ids)} suppliers")
    
    # Step 2: Delete comments for each supplier
    print("\n🧹 Step 2: Deleting comments from MemMachine memory...")
    print(f"   MemMachine URL: {MEMORY_BACKEND_URL}\n")
    
    deleted_count = 0
    failed_count = 0
    
    for idx, supplier_id in enumerate(supplier_ids, 1):
        print(f"   [{idx}/{len(supplier_ids)}] Deleting comments for {supplier_id}...", end=" ")
        success = delete_supplier_comments(supplier_id)
        if success:
            print("✅")
            deleted_count += 1
        else:
            print("❌")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print("✅ DELETION COMPLETE")
    print("=" * 60)
    print(f"Total suppliers processed: {len(supplier_ids)}")
    print(f"Successfully deleted: {deleted_count}")
    print(f"Failed: {failed_count}")
    print("\nℹ️  Note: CRM profiles in the database are NOT deleted.")
    print("   Only episodic memory (comments/interactions) has been cleared.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

