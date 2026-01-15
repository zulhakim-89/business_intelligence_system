import streamlit as st
import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LinearRegression
from utils import get_strategic_advice

def render_forecast(df):
    st.header("🔮 AI Operational Forecast")
    st.caption("Predicts future demand and asks LLM for strategic preparation.")
    
    # Prepare Data
    ml_df = df.groupby(df['Date'].dt.to_period('M')).agg({'Revenue': 'sum', 'Pramusaji': 'sum'}).reset_index()
    ml_df['Month_Num'] = ml_df['Date'].dt.month
    ml_df['Time_Index'] = np.arange(len(ml_df))
    
    with st.container(border=True):
        # --- ROW 1: SELECTORS ---
        c1, c2 = st.columns(2)
        f_year = c1.selectbox("Target Year:", [2025, 2026, 2027])
        f_month = c2.selectbox("Target Month:", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        
        # --- ROW 2: BUTTON (Bottom) ---
        st.write("") # Spacer
        if st.button("🚀 Run AI Prediction", type="primary", use_container_width=True):
            
            month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            target_month_num = month_map[f_month]
            
            if len(ml_df) < 6:
                st.error("⚠️ Need more data (> 6 months) for accurate ML predictions.")
                return

            # --- 1. RUN REGRESSION MODELS ---
            model_rev = LinearRegression()
            model_rev.fit(ml_df[['Time_Index']], ml_df['Revenue'])
            
            model_staff = LinearRegression()
            model_staff.fit(ml_df[['Time_Index']], ml_df['Pramusaji'])
            
            # Predict Future
            last_date = ml_df['Date'].max()
            target_date = pd.Period(f"{f_year}-{target_month_num:02d}", freq='M')
            months_diff = (target_date - last_date).n
            future_idx = ml_df['Time_Index'].max() + months_diff
            
            pred_rev = model_rev.predict([[future_idx]])[0]
            pred_staff = model_staff.predict([[future_idx]])[0]
            
            # Seasonality logic
            avg_month = ml_df[ml_df['Month_Num'] == target_month_num]['Revenue'].mean()
            global_avg = ml_df['Revenue'].mean()
            factor = (avg_month / global_avg) if global_avg > 0 else 1.0
            if pd.isna(factor): factor = 1.0
            
            final_rev = max(0, pred_rev * factor)
            final_staff = max(0, math.ceil(pred_staff * factor))
            
            # --- 2. DISPLAY NUMBERS ---
            st.divider()
            st.subheader(f"📊 Forecast Results: {f_month} {f_year}")
            
            r1, r2, r3 = st.columns(3)
            r1.metric("💰 Predicted Revenue", f"RM {final_rev:,.0f}", f"{factor:.2f}x Seasonality")
            r2.metric("👨‍🍳 Staff Needed", f"{final_staff} Pax", "Min. Roster")
            eff = final_rev / final_staff if final_staff > 0 else 0
            r3.metric("⚡ Efficiency Target", f"RM {eff:,.0f} / Staff", "Revenue per Head")
            
            # --- 3. GENERATE LLM STRATEGY ---
            st.subheader("🤖 AI Strategic Advice (Live Generation)")
            
            # Build the context string for the LLM
            history_max_rev = ml_df['Revenue'].max()
            history_max_staff = ml_df['Pramusaji'].max()
            
            context_prompt = f"""
            Context:
            - Target Month: {f_month} {f_year}
            - Predicted Revenue: RM {final_rev}
            - Predicted Staff Need: {final_staff}
            - Historical Max Revenue: RM {history_max_rev}
            - Historical Max Staff Used: {history_max_staff}
            
            Task:
            Compare the prediction against history. 
            If predicted staff > history max, warn about hiring.
            If predicted revenue is huge, warn about kitchen capacity.
            If revenue is low, suggest marketing.
            """
            
            with st.spinner("🧠 AI is analyzing the numbers..."):
                advice = get_strategic_advice(context_prompt, analysis_type="forecast")
                
                # UPDATED: Use a formal container with Markdown for beautiful formatting
                with st.container(border=True):
                    st.markdown(advice)