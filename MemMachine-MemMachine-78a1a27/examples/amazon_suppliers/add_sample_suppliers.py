#!/usr/bin/env python3
"""
Script to add 10 sample suppliers to the database.
"""
import asyncio
import os
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

# Sample supplier data
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

async def add_suppliers():
    """Add sample suppliers to the database"""
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(**DB_CONFIG)
        
        async with pool.acquire() as conn:
            # Import database functions
            from database import create_supplier_profiles_table, upsert_supplier_profile
            
            # Create table if it doesn't exist
            await create_supplier_profiles_table(pool)
            
            print("Adding 10 sample suppliers to the database...\n")
            
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
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_suppliers())

