import streamlit as st
import pandas as pd
import plotly.express as px
import time
from sqlalchemy import create_engine, text

# 1. Config & Connection
st.set_page_config(page_title="AeroStream Analytics", layout="wide")

DB_URL = "postgresql://airflow:airflow@aerostream_postgres:5432/airflow"

@st.cache_resource
def get_connection():
    return create_engine(DB_URL)

engine = get_connection()

# 2. Main Title
st.title("✈️ AeroStream Analytics")
st.caption("Real-time sentiment intelligence")

# 3. Fetch Data Container
placeholder = st.empty()

# Main Loop
while True:
    try:
        with engine.connect() as conn:
            kpis = pd.read_sql(text("SELECT * FROM global_sentiment_stats"), conn)
            airlines = pd.read_sql(text("SELECT * FROM airline_sentiment_kpis ORDER BY total_tweets DESC"), conn)
            reasons = pd.read_sql(text("SELECT negative_reason, SUM(reason_count) as reason_count FROM negative_reason_analysis GROUP BY negative_reason"), conn)
            
        with placeholder.container():
            # A. Metrics Section
            if not kpis.empty:
                total = int(kpis.iloc[0]['total_tweets'])
                neg_pct = kpis.iloc[0]['pct_negative']
                count_airlines = kpis.iloc[0]['total_airlines']
                
                top_airline = "N/A"
                if not airlines.empty:
                    best = airlines.loc[airlines['satisfaction_score'].idxmax()]
                    top_airline = f"{best['airline']} ({best['satisfaction_score']}%)"

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Tweets", f"{total:,}")
                c2.metric("Negative Sentiment", f"{neg_pct}%")
                c3.metric("Airlines Monitored", count_airlines)
                c4.metric("Top Performer", top_airline)
                
                st.divider()

            # B. Charts Section
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Sentiment Distribution")
                if not airlines.empty:
                    df_long = airlines.melt(
                        id_vars="airline",
                        value_vars=["negative_tweets", "neutral_tweets", "positive_tweets"],
                        var_name="sentiment", 
                        value_name="count"
                    )
                    
                    # RESTORED YOUR COLORS HERE
                    fig1 = px.bar(
                        df_long, x="airline", y="count", color="sentiment",
                        color_discrete_map={
                            "negative_tweets": "#FF6B6B",  # Your Red
                            "neutral_tweets":  "#7D8597",  # Your Grey
                            "positive_tweets": "#4ECDC4"   # Your Teal
                        }
                    )
                    st.plotly_chart(fig1, use_container_width=True)

            with col2:
                st.subheader("Top Negative Drivers")
                if not reasons.empty:
                    # Clean text and sort
                    reasons['negative_reason'] = reasons['negative_reason'].str.title()
                    top_reasons = reasons.sort_values("reason_count", ascending=True).tail(10)
                    
                    # RESTORED YOUR GRADIENT HERE
                    fig2 = px.bar(
                        top_reasons, 
                        x="reason_count", 
                        y="negative_reason", 
                        orientation="h",
                        text_auto=True,
                        color="reason_count",
                        color_continuous_scale=["#ffacac", "#FF6B6B"]
                    )
                    fig2.update_layout(xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
                    st.plotly_chart(fig2, use_container_width=True)

        time.sleep(30)

    except Exception as e:
        st.error(f"Waiting for Database... ({e})")
        time.sleep(5)