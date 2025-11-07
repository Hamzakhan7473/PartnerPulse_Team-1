# API Key Setup Guide

## Issue
You're seeing this error:
```
LLM API error: Error code: 401 - Incorrect API key provided: your_api*****here
```

## Solution

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the API key (it starts with `sk-`)

### Step 2: Update Your .env File

1. Open the `.env` file` in `examples/amazon_suppliers/` directory
2. Find the line:
   ```
   MODEL_API_KEY=your_api_key_here
   ```
3. Replace `your_api_key_here` with your actual API key:
   ```
   MODEL_API_KEY=sk-your-actual-api-key-here
   ```
4. Save the file

### Step 3: Restart the Backend Server

After updating the API key, restart the supplier server:

```bash
# Stop the current server (Ctrl+C or kill the process)
# Then restart:
cd examples/amazon_suppliers
python supplier_server.py
```

### Step 4: Test

Try querying a supplier again in the React UI. The LLM should now work correctly.

## Alternative: Using Environment Variable

Instead of editing the `.env` file, you can also set the environment variable directly:

```bash
export MODEL_API_KEY=sk-your-actual-api-key-here
cd examples/amazon_suppliers
python supplier_server.py
```

## Security Note

⚠️ **Never commit your API key to git!** The `.env` file should be in `.gitignore`.

## Troubleshooting

- **Still getting 401 error?** Make sure you restarted the server after updating the API key
- **403 Forbidden?** Your API key might not have the right permissions or might be expired
- **Rate limit errors?** You may have exceeded your OpenAI API usage limits

