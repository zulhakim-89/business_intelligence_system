import streamlit as st
import pandas as pd
import time
from utils import update_order, delete_order, mask_phone_number

def render_schedule(df, full_df):
    c1, c2 = st.columns([3, 1])
    with c1: st.header("📅 Operational Schedule")
    with c2: view_mode = st.radio("View Mode:", ["Upcoming", "Past History"], horizontal=True)

    today = pd.Timestamp.now().normalize()
    if view_mode == "Upcoming":
        orders = df[df['Date'] >= today].sort_values('Date', ascending=True)
    else:
        orders = df[df['Date'] < today].sort_values('Date', ascending=False)
    
    if orders.empty:
        st.info(f"No {view_mode.lower()} orders found.")
        return

    # Cards Display
    st.caption(f"Showing {len(orders)} orders.")
    for i, row in orders.head(3).iterrows():
        with st.container():
            c_a, c_b, c_c, c_d = st.columns([2, 3, 2, 2])
            c_a.markdown(f"**{row['Date'].strftime('%d %b %Y')}**")
            title = row['Customer_Name'] if row['Customer_Name'] != "Unknown" else row['Order_Title']
            c_b.markdown(f"**{title}**")
            staff_txt = f" | 👨‍🍳 {int(row['Pramusaji'])}" if row['Pramusaji'] > 0 else ""
            c_c.write(f"📍 {row['Location']}")
            c_d.caption(f"RM {row['Revenue']:,.0f}{staff_txt}")
            st.divider()

    # Table View
    with st.expander(f"📋 {view_mode} List", expanded=True):
        display_df = orders[['Date', 'Customer_Name', 'Phone_Number', 'Order_Title', 'Pax', 'Pramusaji', 'Location', 'Revenue', 'Row_ID']].copy()
        display_df['Phone_Number'] = display_df['Phone_Number'].apply(mask_phone_number)
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"RM {x:,.2f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True, column_config={"Row_ID": st.column_config.NumberColumn("ID", format="%d")})

    # MANAGER CONTROL PANEL (FULL RESTORE)
    with st.expander(f"🛠️ Manager Control Panel (Edit/Delete)", expanded=False):
        st.info("Select an ID below to modify.")
        
        # Selector
        opts = orders.apply(lambda x: f"ID {x['Row_ID']}: {x['Order_Title']} ({x['Date'].strftime('%Y-%m-%d')})", axis=1)
        sel_opt = st.selectbox("Select Order:", opts)
        sel_id = int(sel_opt.split(":")[0].replace("ID ", ""))
        curr = full_df.loc[sel_id]
        
        with st.form("edit_form"):
            st.subheader(f"Editing ID: {sel_id}")
            c1, c2 = st.columns(2)
            e_date = c1.date_input("Date", value=pd.to_datetime(curr['Date']).date())
            e_name = c2.text_input("Name", value=curr['Customer_Name'])
            
            c3, c4 = st.columns(2)
            e_phone = c3.text_input("Phone", value=curr['Phone_Number'])
            e_title = c4.text_input("Title", value=curr['Order_Title'])
            
            c5, c6, c7 = st.columns(3)
            e_pax = c5.number_input("Pax", value=int(curr['Pax']))
            e_staff = c6.number_input("Staff", value=int(curr['Pramusaji']))
            
            types = ["Wedding", "Corporate", "Packet", "Buffet", "Other"]
            try: t_idx = types.index(curr['Event_Type'])
            except: t_idx = 4
            e_type = c7.selectbox("Type", types, index=t_idx)
            
            e_rev = st.number_input("Revenue", value=float(curr['Revenue']))
            e_loc = st.text_input("Location", value=curr['Location'])
            e_menu = st.text_area("Menu", value=str(curr['Details']).replace("AI: ", ""))
            
            b1, b2 = st.columns([3, 1])
            if b1.form_submit_button("💾 Save Changes"):
                updates = {
                    'Date': e_date.strftime("%Y-%m-%d"), 'Customer_Name': e_name,
                    'Phone_Number': e_phone, 'Order_Title': e_title, 'Pax': e_pax,
                    'Pramusaji': e_staff, 'Event_Type': e_type, 'Revenue': e_rev,
                    'Location': e_loc, 'Details': f"AI: {e_menu}", 'Menu_Items': f"['{e_menu}']"
                }
                success, msg = update_order(sel_id, updates)
                if success: st.success("Updated!"); time.sleep(1); st.rerun()
                else: st.error(msg)
                
            if b2.form_submit_button("❌ Delete"):
                success, msg = delete_order(sel_id)
                if success: st.warning("Deleted!"); time.sleep(1); st.rerun()
                else: st.error(msg)