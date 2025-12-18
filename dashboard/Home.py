import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
import uuid
from sqlalchemy import create_engine

# --------------------------------------------------
# 1. SETUP
# --------------------------------------------------
st.set_page_config(page_title="AeroStream Analytics", layout="wide")

# --------------------------------------------------
# 2. DATABASE
# --------------------------------------------------
DB_URL = os.getenv("DB_URL", "postgresql://airflow:airflow@aerostream_postgres:5432/airflow")

@st.cache_resource
def get_engine():
    if not DB_URL:
        return None
    return create_engine(DB_URL)

engine = get_engine()

# --------------------------------------------------
# 3. HELPER: MOCK DATA (Fallback)
# --------------------------------------------------
def get_mock_data():
    kpis = pd.DataFrame([{"total_tweets": 14502, "pct_negative": 34.5, "total_airlines": 6}])
    airlines = pd.DataFrame({
        "airline": ["Delta", "United", "American", "Southwest", "JetBlue", "Spirit"],
        "total_tweets": [4000, 3500, 3000, 2000, 1500, 500],
        "positive_tweets": [2000, 800, 500, 1200, 800, 50],
        "neutral_tweets": [1500, 1200, 1000, 500, 500, 150],
        "negative_tweets": [500, 1500, 1500, 300, 200, 300],
        "satisfaction_score": [85, 45, 40, 90, 88, 20]
    })
    reasons = pd.DataFrame({
        "negative_reason": ["Late Flight", "Lost Luggage", "Customer Service", "Cancelled", "Booking Issue", "Food", "Fees"],
        "reason_count": [1200, 950, 800, 600, 400, 200, 100]
    })
    return kpis, airlines, reasons

# --------------------------------------------------
# 4. MAIN APP
# --------------------------------------------------
st.title("AeroStream Analytics")
st.caption("Real-time sentiment intelligence")

dashboard = st.empty()

while True:
    loop_id = str(uuid.uuid4())
    
    with dashboard.container():
        # Fetch Data
        try:
            if engine:
                kpis = pd.read_sql("SELECT * FROM global_sentiment_stats", engine)
                airlines = pd.read_sql("SELECT * FROM airline_sentiment_kpis ORDER BY total_tweets DESC", engine)
                # Grouping reasons for a cleaner global view
                reasons = pd.read_sql("SELECT negative_reason, SUM(reason_count) as reason_count FROM negative_reason_analysis GROUP BY negative_reason", engine)
            else:
                raise Exception("No DB")
        except:
            kpis, airlines, reasons = get_mock_data()

        if kpis.empty:
            st.warning("Waiting for data...")
            time.sleep(5)
            continue

        # --- Metrics ---
        if not airlines.empty:
            top_airline = airlines.loc[airlines['satisfaction_score'].idxmax()]
            best_name = f"{top_airline['airline']} ({top_airline['satisfaction_score']}%)"
        else:
            best_name = "N/A"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tweets", f"{int(kpis.iloc[0]['total_tweets']):,}")
        c2.metric("Negative Sentiment", f"{kpis.iloc[0]['pct_negative']}%")
        c3.metric("Airlines Monitored", kpis.iloc[0]['total_airlines'])
        c4.metric("Top Performer", best_name)

        st.divider()

        # --- Charts ---
        col_charts_1, col_charts_2 = st.columns([1.5, 1], gap="large")

        # Chart 1: Sentiment Stacked Bar
        with col_charts_1:
            st.subheader("Sentiment by Airline")
            if not airlines.empty:
                df_long = airlines.melt(
                    id_vars="airline",
                    value_vars=["negative_tweets", "neutral_tweets", "positive_tweets"],
                    var_name="sentiment", 
                    value_name="count"
                )
                
                fig_sent = px.bar(
                    df_long, x="airline", y="count", color="sentiment",
                    color_discrete_map={
                        "negative_tweets": "#FF6B6B",
                        "neutral_tweets":  "#7D8597",
                        "positive_tweets": "#4ECDC4"
                    },
                    template="streamlit"
                )
                fig_sent.update_layout(yaxis_title="Volume", xaxis_title=None, legend_title=None)
                st.plotly_chart(fig_sent, use_container_width=True, key=f"chart1_{loop_id}")

        with col_charts_2:
            st.subheader("Top Negative Drivers")
            if not reasons.empty:
                # 1. Clean the text (Capitalize first letters)
                reasons['negative_reason'] = reasons['negative_reason'].str.title()
                
                # 2. Sort Data: Largest values at the bottom of the DF appear at the top of the chart in Plotly
                top_reasons = reasons.sort_values("reason_count", ascending=True).tail(10)
                
                # 3. Create Chart with improved visibility
                fig_reasons = px.bar(
                    top_reasons, 
                    x="reason_count", 
                    y="negative_reason", 
                    orientation="h",
                    text="reason_count",
                    # Use a solid color or a higher contrast gradient
                    color="reason_count",
                    color_continuous_scale=["#ffacac", "#FF6B6B"], # Darker start color for better visibility
                )
                
                # 4. Clean Layout
                fig_reasons.update_layout(
                    xaxis_title=None, 
                    yaxis_title=None, 
                    coloraxis_showscale=False,
                    # Remove chart junk (backgrounds, borders)
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=30, b=0),
                    # Hide bottom numbers, keep vertical alignment clean
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    yaxis=dict(showgrid=False) 
                )
                
                # 5. Make the text labels (numbers) easier to read
                fig_reasons.update_traces(
                    texttemplate='%{text}', 
                    textposition="outside",
                    cliponaxis=False # Prevents numbers from being cut off at the right edge
                )
                
                st.plotly_chart(fig_reasons, use_container_width=True, key=f"chart2_{loop_id}")
    time.sleep(30)