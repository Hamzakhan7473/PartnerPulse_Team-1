import os
from typing import cast
from datetime import datetime

import streamlit as st
from gateway_client import ingest_supplier_data, query_supplier, add_supplier_profile, get_supplier_profile, list_suppliers
from llm import chat, set_model
from model_config import MODEL_CHOICES, MODEL_TO_PROVIDER

# Set page config
st.set_page_config(page_title="Amazon Supplier Management", layout="wide")

# Session state
if "supplier_data" not in st.session_state:
    st.session_state.supplier_data = {}
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Sidebar
with st.sidebar:
    st.title("Amazon Supplier Management")
    st.markdown("---")
    
    # Model selection
    st.markdown("#### Choose Model")
    model_id = st.selectbox(
        "Choose Model", MODEL_CHOICES, index=0, label_visibility="collapsed"
    )
    provider = MODEL_TO_PROVIDER[model_id]
    set_model(model_id)
    
    st.markdown("---")
    
    if st.button("Clear History", use_container_width=True):
        st.session_state.query_history = []
        st.rerun()

# Main content
st.title("Amazon Supplier Management System")
st.markdown("Enter supplier information and query contextual supplier data")

# Tabs
tab1, tab2, tab3 = st.tabs(["Add Supplier Data", "Query Supplier", "Add Supplier Profile (CRM)"])

with tab1:
    st.header("Add Supplier Information")
    st.markdown("Enter comments about the supplier. The system will automatically extract the supplier identifier and process the data into profile and episodic memory.")
    
    st.markdown("**Enter comments, reviews, or notes about the supplier:**")
    comments = st.text_area(
        "Supplier Comments/Notes",
        placeholder="Enter comments about the supplier. Include supplier identifier (ID, name, or company name). For example:\n\nSupplier: SUP-001\nCompany: Acme Corp\nContact: John Doe, email: john@acme.com\nProducts: Electronics, Components\n\nRecent interaction: Met with supplier on 2024-01-15. Discussed pricing for bulk orders. Very responsive company.\nQuality: High quality products, on-time delivery\nCapacity: Can handle orders up to 10,000 units/month",
        height=250,
        key="comments_input"
    )
    
    if st.button("Submit Supplier Data", use_container_width=True, key="submit_button"):
        if not comments or not comments.strip():
            st.error("Please enter comments about the supplier")
        else:
            with st.spinner("Processing supplier data..."):
                try:
                    result = ingest_supplier_data(comments)
                    extracted_id = result.get("supplier_id", "Unknown")
                    st.success(f"✓ Supplier data successfully processed!")
                    st.info(f"**Supplier ID extracted:** {extracted_id}\n\n**What happened:**\n- Supplier identifier extracted from comments\n- Comments stored in episodic memory\n- Profile information extracted and stored in profile memory\n- CRM data fetched and mapped")
                    if "supplier_data" not in st.session_state:
                        st.session_state.supplier_data = {}
                    st.session_state.supplier_data[extracted_id] = {"comments": comments}
                except Exception as e:
                    st.error(f"Error ingesting supplier data: {e}")

with tab2:
    st.header("Query Supplier Information")
    st.markdown("Enter your query about a supplier. The system will automatically identify the supplier from your query.")
    
    user_query = st.text_area(
        "Enter your query",
        placeholder="Tell me everything about supplier SUP-001\nor\nWhat's the status of Acme Corp?\nor\nTell me about the supplier we discussed last week",
        height=150,
        key="query_input"
    )
    
    if st.button("Query Supplier", use_container_width=True):
        if not user_query or not user_query.strip():
            st.error("Please enter a query about the supplier")
        else:
            with st.spinner("Querying supplier information..."):
                try:
                    result = query_supplier(user_query)
                    
                    extracted_id = result.get("supplier_id", "Unknown")
                    
                    # Display raw results
                    with st.expander("Raw Memory Data"):
                        st.json(result)
                    
                    # Get LLM response
                    formatted_query = result.get("formatted_query", "")
                    if formatted_query:
                        # The formatted_query already contains everything: system prompt, profile memory,
                        # episodic memory, user query, and instructions. Send it as a single user message.
                        messages = [
                            {"role": "user", "content": formatted_query}
                        ]
                        
                        response_text, latency, tokens, tps = chat(messages, extracted_id)
                        
                        st.markdown("### Contextual Response")
                        st.markdown(response_text)
                        
                        # Add to history
                        st.session_state.query_history.append({
                            "supplier_id": extracted_id,
                            "query": user_query,
                            "response": response_text,
                        })
                    else:
                        st.warning("No formatted query available")
                        
                except Exception as e:
                    st.error(f"Error querying supplier: {e}")
    
    # Query History
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("Query History")
        for i, entry in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {entry['supplier_id']}"):
                st.markdown(f"**Query:** {entry['query']}")
                st.markdown(f"**Response:** {entry['response']}")

with tab3:
    st.header("Add Supplier Profile (CRM)")
    st.markdown("Enter supplier profile information to store in the CRM database. This data will be automatically retrieved when querying suppliers.")
    
    # Search existing suppliers
    st.subheader("Search Existing Suppliers")
    search_term = st.text_input("Search by Supplier ID, Company Name, or Contact", key="supplier_search")
    
    if search_term:
        try:
            search_results = list_suppliers(search_term)
            if search_results.get("data"):
                st.write(f"Found {search_results.get('count', 0)} suppliers:")
                for supplier in search_results["data"][:10]:  # Show first 10
                    with st.expander(f"{supplier.get('supplier_id')} - {supplier.get('company_name', 'N/A')}"):
                        st.json(supplier)
            else:
                st.info("No suppliers found")
        except Exception as e:
            st.error(f"Error searching suppliers: {e}")
    
    st.markdown("---")
    st.subheader("Add/Update Supplier Profile")
    
    with st.form("supplier_profile_form"):
        supplier_id = st.text_input("Supplier ID *", placeholder="SUP-001", key="profile_supplier_id")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", key="profile_company_name")
            contact_name = st.text_input("Contact Name", key="profile_contact_name")
            contact_email = st.text_input("Contact Email", key="profile_contact_email")
            contact_phone = st.text_input("Contact Phone", key="profile_contact_phone")
            address = st.text_area("Address", key="profile_address")
        
        with col2:
            products = st.text_input("Products/Services", key="profile_products")
            capacity = st.text_input("Capacity", key="profile_capacity")
            certifications = st.text_input("Certifications", key="profile_certifications")
            website = st.text_input("Website", key="profile_website")
            status = st.selectbox("Status", ["Active", "Inactive", "Pending", "Suspended"], key="profile_status")
            contract_value = st.text_input("Contract Value", key="profile_contract_value")
            last_interaction = st.date_input("Last Interaction Date", key="profile_last_interaction")
        
        notes = st.text_area("Notes", key="profile_notes")
        
        submitted = st.form_submit_button("Save Supplier Profile", use_container_width=True)
        
        if submitted:
            if not supplier_id:
                st.error("Please enter a Supplier ID")
            else:
                profile_data = {
                    "supplier_id": supplier_id,
                    "company_name": company_name if company_name else None,
                    "contact_name": contact_name if contact_name else None,
                    "contact_email": contact_email if contact_email else None,
                    "contact_phone": contact_phone if contact_phone else None,
                    "address": address if address else None,
                    "products": products if products else None,
                    "capacity": capacity if capacity else None,
                    "certifications": certifications if certifications else None,
                    "website": website if website else None,
                    "status": status,
                    "contract_value": contract_value if contract_value else None,
                    "last_interaction": last_interaction.isoformat() if last_interaction else None,
                    "notes": notes if notes else None,
                }
                
                try:
                    result = add_supplier_profile(profile_data)
                    st.success(f"✓ Supplier profile saved for {supplier_id}!")
                    st.info("This profile will be automatically retrieved when querying this supplier.")
                except Exception as e:
                    st.error(f"Error saving supplier profile: {e}")
    
    # Load existing profile
    if supplier_id:
        if st.button("Load Existing Profile", key="load_profile"):
            try:
                existing_profile = get_supplier_profile(supplier_id)
                if existing_profile.get("status") == "success":
                    st.json(existing_profile.get("data"))
            except Exception as e:
                if "404" in str(e):
                    st.info("No existing profile found for this supplier ID")
                else:
                    st.error(f"Error loading profile: {e}")

