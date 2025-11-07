# Starting the React UI

## Quick Start

1. **Stop Streamlit (if running):**
   ```bash
   # Find and kill Streamlit process
   pkill -f streamlit
   # OR find the port and kill it
   lsof -ti:8501 | xargs kill
   lsof -ti:8502 | xargs kill
   ```

2. **Navigate to React UI directory:**
   ```bash
   cd examples/amazon_suppliers/frontend/react-ui
   ```

3. **Install dependencies (first time only):**
   ```bash
   npm install
   ```

4. **Start the React development server:**
   ```bash
   npm run dev
   ```

5. **Access the React UI:**
   - Open your browser to: **http://localhost:3000**
   - The React app runs on port **3000**, NOT port 8502

## Ports

- **Streamlit (old UI)**: Port 8501 or 8502
- **React (new UI)**: Port 3000
- **Backend API**: Port 8001

## Both Can Run Simultaneously

You can run both Streamlit and React at the same time if needed:
- Streamlit: http://localhost:8501
- React: http://localhost:3000

But typically you'll only want one running.

