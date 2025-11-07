#!/usr/bin/env python3
"""
Script to clear all suppliers from database and clear MemMachine memory,
then add 10 sample suppliers.
"""
import asyncio
import os
import requests
from dotenv import load_dotenv
import asyncpg
from datetime import datetime, date

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

# Sample supplier data (same as add_sample_suppliers.py)
SAMPLE_SUPPLIERS = [
    {
        "supplier_id": "SUP-001",
        "company_name": "TechGlobal Electronics Inc.",
        "contact_name": "John Smith",
        "contact_email": "john.smith@techglobal.com",
        "contact_phone": "+1-555-0101",
        "address": "123 Tech Boulevard, Silicon Valley, CA 94025, USA",
        "products": "Consumer Electronics, Smart Devices, Components",
        "capacity": "50,000 units/month",
        "certifications": "ISO 9001, CE, FCC",
        "website": "https://techglobal.com",
        "status": "Active",
        "contract_value": "$2.5M",
        "last_interaction": date(2024, 11, 1),
        "notes": "Premium supplier with excellent quality control. On-time delivery record: 98%",
    },
    {
        "supplier_id": "SUP-002",
        "company_name": "Global Logistics Solutions",
        "contact_name": "Sarah Johnson",
        "contact_email": "sarah.j@globallogistics.com",
        "contact_phone": "+1-555-0102",
        "address": "456 Commerce Drive, Chicago, IL 60601, USA",
        "products": "Packaging Materials, Shipping Supplies",
        "capacity": "100,000 units/month",
        "certifications": "ISO 14001, FSC Certified",
        "website": "https://globallogistics.com",
        "status": "Active",
        "contract_value": "$1.8M",
        "last_interaction": date(2024, 10, 28),
        "notes": "Specializes in eco-friendly packaging solutions. Strong sustainability focus.",
    },
    {
        "supplier_id": "SUP-003",
        "company_name": "Premium Apparel Co.",
        "contact_name": "Michael Chen",
        "contact_email": "m.chen@premiumapparel.com",
        "contact_phone": "+1-555-0103",
        "address": "789 Fashion Avenue, New York, NY 10001, USA",
        "products": "Clothing, Textiles, Accessories",
        "capacity": "75,000 units/month",
        "certifications": "OEKO-TEX, Fair Trade Certified",
        "website": "https://premiumapparel.com",
        "status": "Active",
        "contract_value": "$3.2M",
        "last_interaction": date(2024, 11, 3),
        "notes": "High-quality fashion supplier. Known for ethical manufacturing practices.",
    },
    {
        "supplier_id": "SUP-004",
        "company_name": "GreenGrocer Organics",
        "contact_name": "Emily Rodriguez",
        "contact_email": "emily.r@greengrocer.com",
        "contact_phone": "+1-555-0104",
        "address": "321 Farm Road, Salinas, CA 93901, USA",
        "products": "Organic Produce, Packaged Foods",
        "capacity": "200,000 units/month",
        "certifications": "USDA Organic, Non-GMO Project Verified",
        "website": "https://greengrocer.com",
        "status": "Active",
        "contract_value": "$4.5M",
        "last_interaction": date(2024, 10, 30),
        "notes": "Leading organic food supplier. Seasonal produce available. Strong quality assurance.",
    },
    {
        "supplier_id": "SUP-005",
        "company_name": "AutoParts Manufacturing Ltd.",
        "contact_name": "David Kim",
        "contact_email": "david.kim@autoparts.com",
        "contact_phone": "+1-555-0105",
        "address": "654 Industrial Park, Detroit, MI 48201, USA",
        "products": "Automotive Parts, Components",
        "capacity": "30,000 units/month",
        "certifications": "ISO/TS 16949, IATF 16949",
        "website": "https://autoparts.com",
        "status": "Active",
        "contract_value": "$1.5M",
        "last_interaction": date(2024, 10, 25),
        "notes": "Specialized automotive supplier. High precision manufacturing capabilities.",
    },
    {
        "supplier_id": "SUP-006",
        "company_name": "Home Essentials Plus",
        "contact_name": "Lisa Wang",
        "contact_email": "lisa.wang@homeessentials.com",
        "contact_phone": "+1-555-0106",
        "address": "987 Home Street, Dallas, TX 75201, USA",
        "products": "Home Goods, Kitchenware, Furniture",
        "capacity": "60,000 units/month",
        "certifications": "BIFMA, GREENGUARD",
        "website": "https://homeessentials.com",
        "status": "Active",
        "contract_value": "$2.1M",
        "last_interaction": date(2024, 11, 2),
        "notes": "Comprehensive home products supplier. Strong design and quality focus.",
    },
    {
        "supplier_id": "SUP-007",
        "company_name": "Sports Equipment Pro",
        "contact_name": "Robert Taylor",
        "contact_email": "robert.t@sportsequip.com",
        "contact_phone": "+1-555-0107",
        "address": "147 Athletic Way, Denver, CO 80201, USA",
        "products": "Sports Equipment, Fitness Gear",
        "capacity": "40,000 units/month",
        "certifications": "ASTM, CPSIA",
        "website": "https://sportsequip.com",
        "status": "Active",
        "contract_value": "$1.7M",
        "last_interaction": date(2024, 10, 27),
        "notes": "Specialized sports equipment supplier. Innovation-focused with strong R&D capabilities.",
    },
    {
        "supplier_id": "SUP-008",
        "company_name": "Beauty & Wellness Corp",
        "contact_name": "Jennifer Martinez",
        "contact_email": "j.martinez@beautywell.com",
        "contact_phone": "+1-555-0108",
        "address": "258 Cosmetic Lane, Los Angeles, CA 90001, USA",
        "products": "Beauty Products, Personal Care, Wellness Items",
        "capacity": "55,000 units/month",
        "certifications": "FDA Approved, Cruelty-Free, Vegan",
        "website": "https://beautywell.com",
        "status": "Active",
        "contract_value": "$2.8M",
        "last_interaction": date(2024, 11, 4),
        "notes": "Premium beauty supplier. Strong focus on natural and organic ingredients.",
    },
    {
        "supplier_id": "SUP-009",
        "company_name": "Books & Media Distributors",
        "contact_name": "James Anderson",
        "contact_email": "j.anderson@bookmedia.com",
        "contact_phone": "+1-555-0109",
        "address": "369 Publishing Place, Seattle, WA 98101, USA",
        "products": "Books, E-books, Digital Media",
        "capacity": "80,000 units/month",
        "certifications": "ISBN Agency, Digital Rights Management",
        "website": "https://bookmedia.com",
        "status": "Active",
        "contract_value": "$1.9M",
        "last_interaction": date(2024, 10, 29),
        "notes": "Major media distributor. Comprehensive catalog with digital and physical formats.",
    },
    {
        "supplier_id": "SUP-010",
        "company_name": "Pet Supplies Unlimited",
        "contact_name": "Amanda White",
        "contact_email": "amanda.w@petsupplies.com",
        "contact_phone": "+1-555-0110",
        "address": "741 Animal Avenue, Austin, TX 78701, USA",
        "products": "Pet Food, Toys, Accessories",
        "capacity": "90,000 units/month",
        "certifications": "AAFCO, FDA Pet Food Regulation",
        "website": "https://petsupplies.com",
        "status": "Active",
        "contract_value": "$2.3M",
        "last_interaction": date(2024, 11, 5),
        "notes": "Leading pet supplies supplier. Strong quality control and animal welfare standards.",
    },
]


async def clear_database():
    """Delete all suppliers from the database"""
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM supplier_profiles")
            print(f"📊 Found {count} suppliers in database")
            
            if count > 0:
                await conn.execute("DELETE FROM supplier_profiles")
                print(f"✅ Deleted all {count} suppliers from database")
            else:
                print("ℹ️  Database is already empty")
        
        await pool.close()
        return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


def clear_memmachine_memory():
    """Clear all memory from MemMachine backend"""
    try:
        print("\n🧹 Clearing MemMachine memory...")
        
        # Try to get all personas/entities and delete them
        # First, try to list all personas
        try:
            list_response = requests.get(f"{MEMORY_BACKEND_URL}/personas", timeout=5)
            if list_response.status_code == 200:
                personas = list_response.json().get("personas", [])
                print(f"   Found {len(personas)} personas in memory")
                
                # Delete each persona
                deleted = 0
                for persona in personas:
                    persona_id = persona.get("id") or persona.get("persona_id")
                    if persona_id:
                        try:
                            delete_response = requests.delete(
                                f"{MEMORY_BACKEND_URL}/personas/{persona_id}",
                                timeout=5
                            )
                            if delete_response.status_code in [200, 204]:
                                deleted += 1
                        except Exception as e:
                            print(f"   ⚠️  Could not delete persona {persona_id}: {e}")
                
                if deleted > 0:
                    print(f"   ✅ Deleted {deleted} personas from memory")
                else:
                    print("   ℹ️  No personas found to delete")
            else:
                print(f"   ⚠️  Could not list personas (status: {list_response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Could not connect to MemMachine backend: {e}")
            print(f"   ℹ️  Make sure MemMachine is running on {MEMORY_BACKEND_URL}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error clearing memory: {e}")
        return False


async def add_suppliers():
    """Add sample suppliers to the database"""
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        
        async with pool.acquire() as conn:
            from database import create_supplier_profiles_table, upsert_supplier_profile
            
            # Create table if it doesn't exist
            await create_supplier_profiles_table(pool)
            
            print("\n📦 Adding 10 sample suppliers to the database...\n")
            
            for idx, supplier in enumerate(SAMPLE_SUPPLIERS, 1):
                try:
                    await upsert_supplier_profile(pool, supplier)
                    print(f"✅ [{idx}/10] Added: {supplier['supplier_id']} - {supplier['company_name']}")
                except Exception as e:
                    print(f"❌ [{idx}/10] Error adding {supplier['supplier_id']}: {e}")
            
            print("\n✅ Successfully added all suppliers!")
            
            # Verify by counting
            count = await conn.fetchval("SELECT COUNT(*) FROM supplier_profiles")
            print(f"\n📊 Total suppliers in database: {count}")
            
        await pool.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function to clear everything and add sample data"""
    print("=" * 60)
    print("🔄 CLEARING AND RESETTING SUPPLIER DATA")
    print("=" * 60)
    
    # Step 1: Clear database
    print("\n📋 Step 1: Clearing database...")
    db_success = await clear_database()
    
    # Step 2: Clear MemMachine memory
    print("\n🧠 Step 2: Clearing MemMachine memory...")
    memory_success = clear_memmachine_memory()
    
    # Step 3: Add sample suppliers
    print("\n📦 Step 3: Adding sample suppliers...")
    add_success = await add_suppliers()
    
    print("\n" + "=" * 60)
    print("✅ RESET COMPLETE")
    print("=" * 60)
    print(f"Database cleared: {'✅' if db_success else '❌'}")
    print(f"Memory cleared: {'✅' if memory_success else '⚠️'}")
    print(f"Sample data added: {'✅' if add_success else '❌'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

