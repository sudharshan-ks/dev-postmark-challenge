# Postmark Webhook FastAPI Project

## Features
- Webhook endpoint at `/webhook` to receive parsed emails from Postmark
- Converts natural language queries to SQL using Gemini API (Google)
- Executes SQL on a local Northwind SQLite database
- Visualizes results using Gemini-generated Plotly code (auto-saves PNG)
- Replies to incoming emails with the SQL result and attached visualization
- Exposes the webhook to the internet using ngrok

## Setup

1. **Install dependencies** (if not already):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn httpx pyngrok matplotlib pandas plotly requests
   ```

2. **Set environment variables**:
   ```bash
   export POSTMARK_TOKEN=your-postmark-server-token
   export POSTMARK_FROM=your-verified-sender@example.com
   export GEMINI_API_KEY=your-gemini-api-key
   ```

3. **Prepare the Northwind database**:
   - Use the provided `northwind_schema.sql` and `northwind_synth_20.sql` to create and populate `northwind.db`:
   ```bash
   sqlite3 northwind.db < northwind_schema.sql
   sqlite3 northwind.db < northwind_synth_20.sql
   ```

4. **Run the server with ngrok**:
   ```bash
   python run_with_ngrok.py
   ```
   The public ngrok URL will be printed in the terminal.

5. **Configure Postmark** to send parsed emails to the ngrok URL + `/webhook`.

## Files
- `main.py`: FastAPI app with the webhook, Gemini, SQL, visualization, and email logic
- `northwind_schema.sql`: Northwind DB schema
- `northwind_synth_20.sql`: Synthetic sample data (~20 records/table, 40 orders)
- `northwind.db`: SQLite database (created after import)
- `run_with_ngrok.py`: Script to start FastAPI with ngrok tunnel

---

**Note:**
- Make sure your API keys and tokens are kept secret.
- For production, use a more robust deployment and secure your endpoints.
- Visualizations are generated using Gemini-generated Plotly code and saved as PNGs.
- The system supports natural language to SQL and auto-visualization for Northwind data.
