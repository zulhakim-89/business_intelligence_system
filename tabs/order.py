import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import get_ai_extraction

def render_order(full_df):
    st.header("➕ Add New Order")
    
    # 1. AI Extraction
    with st.expander("✨ Autofill from WhatsApp", expanded=True):
        raw = st.text_area("Paste WhatsApp text here:")
        if st.button("Extract Data"):
            data = get_ai_extraction(raw)
            if data:
                # Save ALL fields to session state
                st.session_state.update({
                    'f_name': data.get('Customer_Name'), 'f_phone': data.get('Phone_Number'),
                    'f_date': data.get('Date'), 'f_title': data.get('Order_Title'),
                    'f_pax': data.get('Pax'), 'f_loc': data.get('Location'),
                    'f_type': data.get('Event_Type'), 'f_menu': ", ".join(data.get('Menu_Items', [])),
                    'f_price': data.get('Total_Price', 0.0), 'f_staff': data.get('Staff_Count', 0)
                })
                st.success("Data extracted successfully!")

    # 2. The Form
    with st.form("entry_form"):
        st.write("### 👤 Customer Details")
        c1, c2 = st.columns(2)
        name = c1.text_input("Customer Name", value=st.session_state.get('f_name', ''))
        phone = c2.text_input("Phone Number", value=st.session_state.get('f_phone', ''))
        
        st.write("### 📦 Order Details")
        c3, c4 = st.columns(2)
        # Handle date parsing safely
        def_date = datetime.now().date()
        if st.session_state.get('f_date'):
            try: def_date = datetime.strptime(st.session_state.get('f_date'), "%Y-%m-%d").date()
            except: pass
        
        date_val = c3.date_input("Date", value=def_date)
        title = c4.text_input("Order Title", value=st.session_state.get('f_title', ''))
        
        c5, c6 = st.columns(2)
        pax = c5.number_input("Pax", value=int(st.session_state.get('f_pax', 100)))
        staff = c6.number_input("👨‍🍳 Staff Required", min_value=0, value=int(st.session_state.get('f_staff', 0)))
        
        c7, c8 = st.columns(2)
        etype = c7.selectbox("Type", ["Wedding", "Corporate", "Packet", "Buffet", "Other"], index=0)
        rev = c8.number_input("💰 Total Value (RM)", min_value=0.0, step=50.0, value=float(st.session_state.get('f_price', 0.0)))
        
        loc = st.text_input("Location", value=st.session_state.get('f_loc', ''))
        menu = st.text_area("Menu Details", value=st.session_state.get('f_menu', ''))
        
        if st.form_submit_button("💾 Save Order"):
            # Create Row
            new_row = pd.DataFrame({
                'Date': [date_val.strftime("%Y-%m-%d")], 'Customer_Name': [name],
                'Phone_Number': [phone], 'Order_Title': [title], 'Pax': [pax],
                'Pramusaji': [staff], 'Event_Type': [etype], 'Revenue': [rev],
                'Location': [loc], 'Details': [f"AI: {menu}"], 'Menu_Items': [f"['{menu}']"]
            })
            
            # Save to CSV
            updated = pd.concat([full_df, new_row], ignore_index=True)
            cols = ['Date', 'Customer_Name', 'Phone_Number', 'Order_Title', 'Details', 'Pax', 'Pramusaji', 'Event_Type', 'Location', 'Menu_Items', 'Revenue']
            try:
                updated[cols].to_csv('cleaned_revenue_data.csv', index=False)
                st.success(f"✅ Saved Order for {name}!")
                time.sleep(1.0)
                st.rerun()
            except Exception as e:
                st.error(f"Error saving: {e}")