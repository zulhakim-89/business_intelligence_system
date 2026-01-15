import pandas as pd
import numpy as np
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- 1. AI STRATEGIC ADVICE (The Upgrade) ---
def get_strategic_advice(context_text, analysis_type="forecast"):
    """
    Sends data to OpenAI to get a strategic business insight.
    analysis_type: 'forecast' or 'analytics'
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if analysis_type == "forecast":
            # UPGRADED PROMPT: Asking for structured, professional report
            system_role = """
            You are an Operations Director presenting a forecast to the CEO. 
            Format your response using Markdown. 
            Structure it into 3 distinct sections with bold headers:
            1. **📉 Executive Summary**: One sentence summary of the outlook.
            2. **⚠️ Operational Risk Analysis**: Compare the prediction vs historical max. Is it too high (capacity risk) or too low (revenue risk)?
            3. **🚀 Strategic Action Plan**: Provide 2-3 specific, actionable bullet points for the manager.
            """
        else:
            # Analytics Prompt (Already working well)
            system_role = "You are a Business Analyst. Summarize the yearly performance, highlight the biggest win, and suggest one improvement area. Use bold headers and bullet points."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": context_text}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

# --- 2. WHATSAPP EXTRACTION ---
def get_ai_extraction(text_input):
    """Uses OpenAI to convert raw text into structured JSON"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"""
        Extract catering order details into JSON.
        Fields:
        - Date (YYYY-MM-DD)
        - Customer_Name (Person's Name)
        - Phone_Number (digits only)
        - Order_Title (Event Name)
        - Pax (Integer)
        - Staff_Count (Integer, default 0)
        - Event_Type (Wedding, Corporate, Packet, Buffet, Other)
        - Location (City/Area)
        - Menu_Items (List of food items)
        - Total_Price (Float, total contract value)
        
        Text: "{text_input}"
        Return ONLY valid JSON.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception:
        return None

# --- 3. DATA LOADING ---
def load_data():
    """Loads and cleans the database with robust error handling"""
    try:
        df = pd.read_csv(
            'cleaned_revenue_data.csv', 
            encoding='utf-8', 
            engine='python',
            on_bad_lines='skip',
            quotechar='"'
        )
        
        # Standard Clean-up
        df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
        df['Date_Valid'] = df['Date'].notna()
        df['Row_ID'] = df.index
        df = df.sort_values('Date', na_position='last')
        df['Month_Year'] = df['Date'].dt.to_period('M')

        # Ensure Columns Exist
        cols = ['Customer_Name', 'Phone_Number', 'Pramusaji', 'Revenue', 'Pax', 'Event_Type', 'Location', 'Order_Title', 'Details', 'Menu_Items']
        for c in cols:
            if c not in df.columns:
                df[c] = 0 if c in ['Pramusaji', 'Revenue', 'Pax'] else ""

        # Force Numbers
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        df['Pax'] = pd.to_numeric(df['Pax'], errors='coerce').fillna(0)
        df['Pramusaji'] = pd.to_numeric(df['Pramusaji'], errors='coerce').fillna(0)
        df['Phone_Clean'] = df['Phone_Number'].astype(str).str.replace(r'\D', '', regex=True)

        # Estimate missing revenue
        def estimate_revenue(row):
            if pd.notna(row['Revenue']) and row['Revenue'] > 0: return row['Revenue']
            rates = {"Wedding": 18, "Corporate": 25, "Packet": 10, "Buffet": 22}
            return row['Pax'] * rates.get(str(row['Event_Type']), 15)

        df['Revenue'] = df.apply(estimate_revenue, axis=1)
        return df
    except Exception as e:
        print(f"❌ Error Loading CSV: {e}")
        return pd.DataFrame()

# --- 4. CRUD HELPERS ---
def delete_order(row_id):
    try:
        df_raw = pd.read_csv('cleaned_revenue_data.csv', encoding='utf-8', engine='python', quotechar='"')
        if row_id in df_raw.index:
            df_raw = df_raw.drop(row_id)
            df_raw.to_csv('cleaned_revenue_data.csv', index=False)
            return True, "Deleted."
        return False, "ID not found."
    except Exception as e: return False, str(e)

def update_order(row_id, updated_data):
    try:
        df_raw = pd.read_csv('cleaned_revenue_data.csv', encoding='utf-8', engine='python', quotechar='"')
        if row_id in df_raw.index:
            for key, value in updated_data.items():
                df_raw.at[row_id, key] = value
            df_raw.to_csv('cleaned_revenue_data.csv', index=False)
            return True, "Updated."
        return False, "ID not found."
    except Exception as e: return False, str(e)

def mask_phone_number(phone):
    s = str(phone)
    if len(s) > 4: return "*" * (len(s) - 4) + s[-4:]
    return s