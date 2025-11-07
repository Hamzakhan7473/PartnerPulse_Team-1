# Amazon Supplier Management System

A supplier management application for Amazon that leverages MemMachine to store and retrieve contextual supplier information.

## Features

- **Supplier Data Ingestion**: Enter supplier information and map it to CRM data
- **Contextual Querying**: Retrieve supplier information with summaries from episodic memory and contextual data from profile memory
- **Memory Integration**: Automatically stores supplier data in both episodic and profile memory

## Architecture

The system consists of:
1. **Supplier Server** (`supplier_server.py`): FastAPI middleware that interfaces with MemMachine backend
2. **Query Constructor** (`query_constructor.py`): Formats queries using episodic and profile memory
3. **Frontend** (`frontend/app.py`): Streamlit UI for entering and querying supplier data

## Setup

### Prerequisites

1. Ensure MemMachine backend is running on `http://localhost:8080`
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn streamlit requests python-dotenv boto3 openai
   ```

### Environment Variables

Create a `.env` file or set the following environment variables:

```bash
export MEMORY_BACKEND_URL=http://localhost:8080
export SUPPLIER_PORT=8001
export SUPPLIER_SERVER_URL=http://localhost:8001
export MODEL_API_KEY=your_api_key_here  # For LLM integration
```

### Running the Application

1. **Start the supplier server:**
   ```bash
   cd examples/amazon_suppliers
   python supplier_server.py
   ```

2. **Start the frontend:**
   ```bash
   cd examples/amazon_suppliers/frontend
   streamlit run app.py
   ```

3. **Access the application:**
   - Frontend: http://localhost:8501
   - Supplier API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## Usage

### Adding Supplier Data

1. Navigate to the "Add Supplier Data" tab
2. Fill in supplier information:
   - **Supplier ID**: Unique identifier (e.g., SUP-001)
   - **Company Name**: Required
   - Contact details, products, capacity, certifications
   - Optional CRM integration data
3. Click "Submit Supplier Data"

The system will:
- Store supplier information in episodic memory (what has been recorded)
- Extract profile information into profile memory (persistent characteristics)

### Querying Suppliers

1. Navigate to the "Query Supplier" tab
2. Enter:
   - **Supplier ID**: The supplier to query
   - **Query**: Natural language question (e.g., "Tell me everything about this supplier")
3. Click "Query Supplier"

The system will:
- Search both episodic and profile memory
- Generate a contextual response combining:
  - Summary from episodic memory (what has been recorded)
  - Contextual information from profile memory (persistent characteristics)

## API Endpoints

### POST `/supplier/ingest`
Ingest supplier information into memory system.

**Request Body:**
```json
{
  "supplier_id": "SUP-001",
  "supplier_data": {
    "company_name": "Acme Corp",
    "contact_name": "John Doe",
    "email": "john@acme.com",
    ...
  },
  "crm_data": {
    "crm_id": "CRM-123",
    "status": "Active",
    ...
  }
}
```

### POST `/supplier/query`
Query supplier information with contextual memory.

**Request Body:**
```json
{
  "supplier_id": "SUP-001",
  "query": "Tell me about this supplier"
}
```

## Memory Types

- **Episodic Memory**: Stores individual supplier data entries and interactions
- **Profile Memory**: Stores persistent supplier characteristics and facts extracted from episodes

## Integration with MemMachine

The application uses MemMachine's REST API:
- `POST /v1/memories`: Store supplier data
- `POST /v1/memories/search`: Search both episodic and profile memory

All data is organized by:
- `group_id`: "amazon_suppliers"
- `agent_id`: ["supplier_manager"]
- `user_id`: ["amazon_admin"]
- `session_id`: "supplier_{supplier_id}"

