#!/usr/bin/env python3
"""
Quick script to verify if a supplier exists in the database
"""
import asyncio
import os
from dotenv import load_dotenv
import asyncpg

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "memmachine"),
}

async def verify_supplier(search_term: str = "techglobal"):
    """Verify if supplier exists in database"""
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        
        async with pool.acquire() as conn:
            # Check all suppliers
            all_suppliers = await conn.fetch(
                "SELECT supplier_id, company_name FROM supplier_profiles ORDER BY supplier_id LIMIT 20"
            )
            print(f"\n📊 Total suppliers in database: {len(all_suppliers)}")
            print("\nFirst 10 suppliers:")
            for row in all_suppliers[:10]:
                print(f"  - {row['supplier_id']}: {row['company_name']}")
            
            # Try to find the specific supplier
            print(f"\n🔍 Searching for: '{search_term}'")
            
            # Method 1: Direct LIKE query
            results = await conn.fetch(
                "SELECT supplier_id, company_name FROM supplier_profiles WHERE LOWER(company_name) LIKE LOWER($1) LIMIT 5",
                f"%{search_term}%"
            )
            print(f"\nMethod 1 - Direct LIKE query:")
            if results:
                for row in results:
                    print(f"  ✅ Found: {row['supplier_id']} - {row['company_name']}")
            else:
                print(f"  ❌ No results found")
            
            # Method 2: Exact match (case insensitive)
            exact = await conn.fetchrow(
                "SELECT supplier_id, company_name FROM supplier_profiles WHERE LOWER(company_name) = LOWER($1)",
                search_term
            )
            print(f"\nMethod 2 - Exact match (case insensitive):")
            if exact:
                print(f"  ✅ Found: {exact['supplier_id']} - {exact['company_name']}")
            else:
                print(f"  ❌ No exact match found")
            
            # Method 3: Test find_supplier_by_name function
            from database import find_supplier_by_name
            result = await find_supplier_by_name(pool, search_term)
            print(f"\nMethod 3 - find_supplier_by_name function:")
            if result:
                print(f"  ✅ Found: {result['supplier_id']} - {result['company_name']}")
            else:
                print(f"  ❌ No result found")
        
        await pool.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    search = sys.argv[1] if len(sys.argv) > 1 else "techglobal"
    asyncio.run(verify_supplier(search))

