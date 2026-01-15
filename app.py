import streamlit as st
from utils import load_data
from tabs.schedule import render_schedule
from tabs.analytics import render_analytics
from tabs.forecast import render_forecast
from tabs.order import render_order

# --- CONFIG ---
st.set_page_config(page_title="Zulja Operations OS", layout="wide", page_icon="🍱")

def main():
    st.set_page_config(page_title="Zulja Operations OS", layout="wide", page_icon="🍱")
    
    # --- 🔐 SECURITY CHECK ---
    # Check if the user is already logged in
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Login Logic
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔒 Login Required</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # We use st.secrets for the password if deployed, or a fallback for local testing
            correct_password = st.secrets.get("APP_PASSWORD", "admin") 
            
            pwd_input = st.text_input("Enter Access Password:", type="password")
            if st.button("Login", use_container_width=True):
                if pwd_input == correct_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password")
        return  # <--- STOPS the app here if not logged in

    # --- 🚀 MAIN APP STARTS HERE (Only runs if logged in) ---
    st.title("🍱 Zulja Operations OS")
    st.caption("v2026.1 - Live Operations Dashboard")
    
    # 1. Load Data
    full_df = load_data()
    
    if full_df.empty:
        st.error("⚠️ Database not found. Please check 'cleaned_revenue_data.csv'.")
        return

    # 2. Filter Valid Data
    df_valid = full_df[full_df['Date_Valid']].copy()

    # 3. Sidebar Logout
    with st.sidebar:
        st.write(f"Logged in as: **Manager**")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # 4. Create Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Schedule", 
        "📊 Analytics", 
        "🔮 Forecast (ML)", 
        "➕ New Order"
    ])

    # 5. Render Tabs
    with tab1:
        render_schedule(df_valid, full_df)
    
    with tab2:
        render_analytics(df_valid)
        
    with tab3:
        render_forecast(df_valid)
        
    with tab4:
        render_order(full_df)

if __name__ == "__main__":
    main()