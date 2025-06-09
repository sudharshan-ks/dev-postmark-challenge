from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os
import requests
import sqlite3
import matplotlib.pyplot as plt
import tempfile
import base64
import smtplib
from email.message import EmailMessage
import json
import pandas as pd
from datetime import datetime

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Northwind schema (shortened for brevity, expand as needed)
NORTHWIND_SCHEMA = '''
CREATE TABLE Customers (
    CustomerID TEXT PRIMARY KEY,
    CompanyName TEXT,
    ContactName TEXT,
    ContactTitle TEXT,
    Address TEXT,
    City TEXT,
    Region TEXT,
    PostalCode TEXT,
    Country TEXT,
    # Phone TEXT,
    Fax TEXT
);
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID TEXT,
    EmployeeID INTEGER,
    OrderDate TEXT,
    RequiredDate TEXT,
    ShippedDate TEXT,
    ShipVia INTEGER,
    Freight REAL,
    ShipName TEXT,
    ShipAddress TEXT,
    ShipCity TEXT,
    ShipRegion TEXT,
    ShipPostalCode TEXT,
    ShipCountry TEXT
);
CREATE TABLE [Order Details] (
    OrderID INTEGER,
    ProductID INTEGER,
    UnitPrice REAL,
    Quantity INTEGER,
    Discount REAL
);
CREATE TABLE Products (
    ProductID INTEGER PRIMARY KEY,
    ProductName TEXT,
    SupplierID INTEGER,
    CategoryID INTEGER,
    QuantityPerUnit TEXT,
    UnitPrice REAL,
    UnitsInStock INTEGER,
    UnitsOnOrder INTEGER,
    ReorderLevel INTEGER,
    Discontinued INTEGER
);
'''

# Helper: Compose prompt for Gemini

def compose_gemini_prompt(schema, nl_query):
    return f"""
You are an expert SQL assistant. Given the following database schema:
{schema}

Convert the following natural language question into a valid SQLite SQL query. Only return the SQL query, nothing else.

Question: {nl_query}

SQL: 

Note: Ensure the SQL query is valid for SQLite and does not include any comments or explanations or is marked in markdown format.
"""

# Helper: Call Gemini API with a prompt and return the response text

def call_gemini_api(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

# Update: Compose prompt for Gemini SQL

def call_gemini(nl_query):
    prompt = compose_gemini_prompt(NORTHWIND_SCHEMA, nl_query)
    sql = call_gemini_api(prompt)
    sql = sql.replace("sqlite", "").replace("`", "").replace("sql", "").strip()
    print("Generated SQL query:\n--------------------\n" + sql)
    return sql

# Helper: Run SQL and get results

def run_sql(sql):
    print("\n\nRunning SQL query:")
    print("--------------------")
    print(sql)
    print("--------------------")

    conn = sqlite3.connect("northwind.db")
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    conn.close()
    print("Successfully executed SQL query.")
    print(f"Columns returned: {columns}")
    print(f"rows returned: {rows}")
    return columns, rows

# Update: Ask Gemini to generate plotly viz code and execute it

def prompt_gemini_for_plotly_viz(nl_query, columns, rows, img_filename):
    print("\n\nGenerating plotly visualization code:")
    print("--------------------")
    sample_rows = rows[:10] if len(rows) > 10 else rows
    prompt = f'''
You are a Python data visualization expert. Given the following SQL query result for the question: "{nl_query}",
with columns: {columns}
and sample rows: {sample_rows}
Write Python code using the plotly library to visualize the result in the most appropriate way (bar, pie, line, table, etc). Save the visualization as a PNG file in the current directory with the filename: {img_filename}. Do not show the plot, just save it. Assume the data is available as a pandas DataFrame named df. Only return the code, nothing else.
'''
    code = call_gemini_api(prompt)
    code = code.replace('```python', '').replace('```', '').strip()
    print("Generated plotly code:\n--------------------\n" + code)
    return code

# Helper: Visualise and save results

def visualise_and_save(columns, rows, nl_query):
    df = pd.DataFrame(rows, columns=columns)
    img_filename = f"img-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    code = prompt_gemini_for_plotly_viz(nl_query, columns, rows, img_filename)
    # Prepare the local namespace for exec
    local_vars = {'df': df, 'pd': pd}
    try:
        exec(code, {}, local_vars)
    except Exception as e:
        print("Error executing Gemini-generated plotly code:", e)
        # fallback: save as table using matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.axis('off')
        table = ax.table(cellText=rows, colLabels=columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        plt.savefig(img_filename, bbox_inches='tight')
        plt.close(fig)
    return img_filename, 'plotly'

# Helper: Send email with attachment via Postmark

def send_email_with_attachment(to, subject, body, attachment_path):
    postmark_token = os.getenv("POSTMARK_TOKEN")
    if not postmark_token:
        raise Exception("POSTMARK_TOKEN not set")
    with open(attachment_path, "rb") as f:
        img_data = f.read()
    img_b64 = base64.b64encode(img_data).decode()
    payload = {
        "From": os.getenv("POSTMARK_FROM", "ask@sudharshanks.in"),
        "To": to,
        "Subject": subject,
        "TextBody": body,
        "Attachments": [
            {
                "Name": "result.png",
                "Content": img_b64,
                "ContentType": "image/png"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": postmark_token
    }
    resp = requests.post("https://api.postmarkapp.com/email", headers=headers, data=json.dumps(payload))
    if not resp.ok:
        print("Postmark error response:", resp.status_code, resp.text)
    resp.raise_for_status()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    sender = data.get("From")
    subject = data.get("Subject")
    # Extract the natural language query from the email body
    nl_query = data.get("TextBody") or data.get("stripped-text") or data.get("Body")
    if not nl_query:
        return JSONResponse({"error": "No query found in email."}, status_code=400)
    # try:
    sql = call_gemini(nl_query)
    columns, rows = run_sql(sql)
    img_path, chart_type = visualise_and_save(columns, rows, nl_query)
    body = f"Your query: {nl_query}\n\nSQL: {sql}\n\nResult: {len(rows)} rows. See attached {chart_type} visualization."
    print(body)
    # send_email_with_attachment(sender, f"Re: {subject}", body, img_path)
    # os.unlink(img_path)
    return JSONResponse({"status": "ok", "sql": sql, "rows": len(rows)})
    # except Exception as e:
        # print(f"Error processing request: {e}")
        
        # return JSONResponse({"error": str(e)}, status_code=500)
