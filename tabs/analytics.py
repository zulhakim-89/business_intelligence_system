import streamlit as st
import altair as alt
import pandas as pd
from utils import get_strategic_advice

def render_analytics(df):
    st.header("📊 Business Snapshot")
    
    # Year Filter
    years = sorted(df['Date'].dt.year.unique(), reverse=True)
    sel_year = st.selectbox("📅 Pick a Year:", years)
    ydf = df[df['Date'].dt.year == sel_year]
    
    if ydf.empty:
        st.info("No Data for this year."); return

    # --- ROW 1: METRICS ---
    tot_rev = ydf['Revenue'].sum()
    tot_pax = ydf['Pax'].sum()
    tot_staff = ydf['Pramusaji'].sum()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Money In", f"RM {tot_rev:,.0f}")
    k2.metric("👥 Guests Fed", f"{tot_pax:,}")
    k3.metric("👨‍🍳 Staff Shifts", f"{tot_staff:,}")
    
    if not ydf.empty:
        busy_month = ydf.groupby(ydf['Date'].dt.month_name())['Revenue'].sum().idxmax()
    else:
        busy_month = "-"
    k4.metric("🔥 Busiest Month", busy_month)
    
    # --- LLM INSIGHT BUTTON ---
    with st.expander("🧠 Generate AI Year Report", expanded=False):
        if st.button("Analyze Performance"):
            top_client = ydf.groupby('Customer_Name')['Revenue'].sum().idxmax()
            top_event = ydf['Event_Type'].mode()[0]
            
            context = f"""
            Year: {sel_year}
            Total Revenue: RM {tot_rev}
            Total Guests: {tot_pax}
            Busiest Month: {busy_month}
            Top Client: {top_client}
            Most Common Event: {top_event}
            """
            
            with st.spinner("Consulting AI..."):
                insight = get_strategic_advice(context, analysis_type="analytics")
                st.markdown(f"**EXECUTIVE SUMMARY:**\n\n{insight}")

    st.divider()
    
    # --- ROW 2: MAIN CHARTS ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📅 Monthly Income")
        m_data = ydf.groupby(ydf['Date'].dt.month_name())['Revenue'].sum().reindex([
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]).reset_index()
        m_data.columns = ['Month', 'Sales']
        
        # MODERN CHART: Removed Grid, Cleaned Axes
        chart = alt.Chart(m_data).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
            x=alt.X('Month', sort=None, axis=alt.Axis(labelAngle=0, title=None)),
            y=alt.Y('Sales', axis=None),
            color=alt.value("#FF4B4B"),
            tooltip=['Month', 'Sales']
        ).properties(height=300, background='transparent').configure_axis(grid=False, domain=False).configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)
    
    with c2:
        st.subheader("🎭 Event Types")
        e_data = ydf['Event_Type'].value_counts().reset_index()
        e_data.columns = ['Type', 'Count']
        
        # MODERN DONUT CHART
        chart = alt.Chart(e_data).mark_arc(innerRadius=80, outerRadius=120).encode(
            theta='Count', 
            color=alt.Color('Type', scale=alt.Scale(scheme='magma')), 
            tooltip=['Type', 'Count']
        ).properties(height=300, background='transparent').configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)

    st.divider()

    # --- ROW 3: VIPs & STAFF ---
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🏆 Top VIP Clients")
        client_df = ydf[ydf['Customer_Name'] != "Unknown"]
        if not client_df.empty:
            top = client_df.groupby('Customer_Name')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(5)
            
            chart = alt.Chart(top).mark_bar(color='#FFD700', cornerRadius=5).encode(
                x=alt.X('Revenue', axis=None), 
                y=alt.Y('Customer_Name', sort='-x', title=None),
                tooltip=['Customer_Name', 'Revenue']
            ).properties(height=300, background='transparent').configure_axis(grid=False, domain=False).configure_view(strokeWidth=0)
            
            st.altair_chart(chart, use_container_width=True)
            
    with c4:
        st.subheader("👨‍🍳 Staffing Intensity")
        staff_stats = ydf.groupby('Event_Type')['Pramusaji'].mean().reset_index()
        
        chart = alt.Chart(staff_stats).mark_bar(color='#008080', cornerRadius=5).encode(
            x=alt.X('Event_Type', title=None, axis=alt.Axis(labelAngle=0)), 
            y=alt.Y('Pramusaji', title="Avg Staff", axis=None), 
            tooltip=['Event_Type', 'Pramusaji']
        ).properties(height=300, background='transparent').configure_axis(grid=False, domain=False).configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)

    st.divider()

    # --- ROW 4: FOOD & MAP ---
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("🍗 Top 5 Dishes")
        all_text = " ".join(ydf['Menu_Items'].astype(str))
        clean_text = all_text.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        menu_list = [x.strip() for x in clean_text.split(",") if len(x.strip()) > 2]
        if menu_list:
            from collections import Counter
            menu_counts = pd.DataFrame(Counter(menu_list).most_common(5), columns=['Menu', 'Count'])
            
            chart = alt.Chart(menu_counts).mark_bar(color='#FF914D', cornerRadius=5).encode(
                x=alt.X('Count', axis=None), 
                y=alt.Y('Menu', sort='-x', title=None), 
                tooltip=['Menu', 'Count']
            ).properties(height=300, background='transparent').configure_axis(grid=False, domain=False).configure_view(strokeWidth=0)
            
            st.altair_chart(chart, use_container_width=True)
            
    with c6:
        st.subheader("🗺️ Delivery Heatmap")
        coords = {
            "gombak": [3.2252, 101.7224], "bidara": [3.2380, 101.6840], "selayang": [3.2514, 101.6599],
            "puchong": [3.0346, 101.6166], "kl": [3.1390, 101.6869], "kuala lumpur": [3.1390, 101.6869],
            "dbkl": [3.1510, 101.6930], "batu caves": [3.2379, 101.6840], "shah alam": [3.0738, 101.5183],
            "ampang": [3.1578, 101.7619], "petaling": [3.1073, 101.6067], "damansara": [3.1543, 101.6033],
            "cheras": [3.0645, 101.7589], "kajang": [2.9935, 101.7874]
        }
        def map_loc(txt):
            txt = str(txt).lower()
            for k, v in coords.items():
                if k in txt: return v
            return None
        
        ydf['Coords'] = ydf['Location'].apply(map_loc)
        map_data = ydf.dropna(subset=['Coords'])
        if not map_data.empty:
            st.map(pd.DataFrame(map_data['Coords'].tolist(), columns=['lat', 'lon']), size=20, zoom=10, color='#ffaa00')
        else:
            st.warning("No matched locations for map.")