# Amazon Supplier Management - React UI

Modern React-based frontend for the Amazon Supplier Management System.

## Features

- **Add Supplier Data**: Enter comments about suppliers, automatically extracts supplier ID and stores in memory
- **Query Supplier**: Query supplier information with contextual responses from episodic and profile memory
- **Add Supplier Profile (CRM)**: Manage supplier profiles in the CRM database
- **Model Selection**: Choose from multiple LLM providers (OpenAI, Anthropic, DeepSeek, Meta, Mistral)
- **Query History**: View recent queries and responses

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8001`

### Installation

```bash
cd examples/amazon_suppliers/frontend/react-ui
npm install
```

### Environment Variables

Create a `.env` file in the `react-ui` directory:

```bash
VITE_API_URL=http://localhost:8001
```

### Running the Application

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Markdown**: Markdown rendering for LLM responses
- **Lucide React**: Icons

## Project Structure

```
react-ui/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx          # Navigation sidebar
│   │   ├── AddSupplierData.jsx  # Add supplier comments
│   │   ├── QuerySupplier.jsx    # Query supplier information
│   │   └── AddSupplierProfile.jsx # CRM profile management
│   ├── services/
│   │   └── api.js               # API client
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Endpoints Used

- `POST /supplier/ingest` - Ingest supplier comments
- `POST /supplier/query` - Query supplier information
- `POST /supplier/chat` - Chat with LLM about supplier
- `POST /crm/supplier/profile` - Add/update supplier profile
- `GET /crm/supplier/profile/{supplier_id}` - Get supplier profile
- `GET /crm/suppliers` - List/search suppliers

