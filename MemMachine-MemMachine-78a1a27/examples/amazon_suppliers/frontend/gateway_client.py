import os
import requests

SUPPLIER_SERVER_URL = os.getenv("SUPPLIER_SERVER_URL", "http://localhost:8001")


def ingest_supplier_data(comments: str) -> dict:
    """Ingest supplier comments into memory system. Supplier ID will be extracted from comments."""
    response = requests.post(
        f"{SUPPLIER_SERVER_URL}/supplier/ingest",
        json={
            "comments": comments
        },
        timeout=1000
    )
    response.raise_for_status()
    return response.json()


def query_supplier(query: str) -> dict:
    """Query supplier information with contextual memory. Supplier ID will be extracted from query."""
    response = requests.post(
        f"{SUPPLIER_SERVER_URL}/supplier/query",
        json={
            "query": query
        },
        timeout=1000
    )
    response.raise_for_status()
    return response.json()


def store_and_query_supplier(supplier_id: str, supplier_data: dict, query: str, crm_data: dict | None = None) -> dict:
    """Store supplier data and immediately query."""
    response = requests.post(
        f"{SUPPLIER_SERVER_URL}/supplier/store-and-query",
        json={
            "supplier_id": supplier_id,
            "supplier_data": supplier_data,
            "query": query,
            "crm_data": crm_data
        },
        timeout=1000
    )
    response.raise_for_status()
    return response.json()


def add_supplier_profile(profile_data: dict) -> dict:
    """Add or update supplier profile in CRM database."""
    response = requests.post(
        f"{SUPPLIER_SERVER_URL}/crm/supplier/profile",
        json=profile_data,
        timeout=1000
    )
    response.raise_for_status()
    return response.json()


def get_supplier_profile(supplier_id: str) -> dict:
    """Get supplier profile from CRM database."""
    response = requests.get(
        f"{SUPPLIER_SERVER_URL}/crm/supplier/profile/{supplier_id}",
        timeout=1000
    )
    response.raise_for_status()
    return response.json()


def list_suppliers(search: str | None = None) -> dict:
    """List all suppliers or search suppliers."""
    params = {"search": search} if search else {}
    response = requests.get(
        f"{SUPPLIER_SERVER_URL}/crm/suppliers",
        params=params,
        timeout=1000
    )
    response.raise_for_status()
    return response.json()

