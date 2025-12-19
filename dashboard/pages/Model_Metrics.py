import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="Model Performance Report",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS for Professional Styling ---
st.markdown("""     
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
    }
    .metric-card {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Model Performance Report")
st.markdown("Offline evaluation metrics for the Logistic Regression classification model.")
st.markdown("---")

# --- Path Configuration ---
# Looks for the 'assets' folder inside the container
ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR) and os.path.exists("../assets"):
    ASSETS_DIR = "../assets"

metrics_file = os.path.join(ASSETS_DIR, "training_metrics.json")
cm_file = os.path.join(ASSETS_DIR, "confusion_matrix.png")
roc_file = os.path.join(ASSETS_DIR, "roc_curve.png")

# --- Main Logic ---
if os.path.exists(metrics_file):
    with open(metrics_file, 'r') as f:
        raw_metrics = json.load(f)
    
    # 1. GLOBAL METRICS SECTION
    st.subheader("Global Performance")
    
    # Extract Global Stats
    accuracy = raw_metrics.get("accuracy", 0)
    macro_f1 = raw_metrics.get("macro_avg_f1", 0)
    weighted_f1 = raw_metrics.get("classes", {}).get("weighted avg", {}).get("f1-score", 0)
    total_samples = raw_metrics.get("classes", {}).get("macro avg", {}).get("support", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Accuracy", f"{accuracy:.2%}")
    c2.metric("Macro F1-Score", f"{macro_f1:.2%}")
    c3.metric("Weighted F1-Score", f"{weighted_f1:.2%}")
    c4.metric("Test Samples", int(total_samples))

    st.markdown("---")

    # 2. DETAILED CLASS PERFORMANCE (Dataframe & Charts)
    st.subheader("Per-Class Analysis")

    # Process JSON into DataFrame
    report_dict = raw_metrics.get("classes", {})
    # Filter out summary keys to get only classes (negative, neutral, positive)
    class_keys = [k for k in report_dict.keys() if k not in ['accuracy', 'macro avg', 'weighted avg']]
    
    data = []
    for k in class_keys:
        row = report_dict[k]
        row['Sentiment'] = k.title() # Capitalize
        data.append(row)
    
    df_metrics = pd.DataFrame(data)
    
    # Reorder columns
    df_metrics = df_metrics[['Sentiment', 'precision', 'recall', 'f1-score', 'support']]

    col_table, col_chart = st.columns([1, 1])

    with col_table:
        st.markdown("**Detailed Metrics Table**")
        # Display as a styled dataframe
        st.dataframe(
            df_metrics,
            column_config={
                "Sentiment": "Class",
                "precision": st.column_config.ProgressColumn("Precision", format="%.2f", min_value=0, max_value=1),
                "recall": st.column_config.ProgressColumn("Recall", format="%.2f", min_value=0, max_value=1),
                "f1-score": st.column_config.ProgressColumn("F1-Score", format="%.2f", min_value=0, max_value=1),
                "support": st.column_config.NumberColumn("Support (Count)", format="%d"),
            },
            hide_index=True,
            use_container_width=True
        )

    with col_chart:
        st.markdown("**Precision vs Recall Comparison**")
        # Reshape for plotting
        df_melted = df_metrics.melt(id_vars="Sentiment", value_vars=["precision", "recall", "f1-score"], var_name="Metric", value_name="Score")
        
        fig = px.bar(
            df_melted, 
            x="Sentiment", 
            y="Score", 
            color="Metric", 
            barmode="group",
            color_discrete_sequence=["#3498db", "#2ecc71", "#9b59b6"],
            height=350
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 3. DIAGNOSTIC PLOTS
    st.subheader("Diagnostic Plots")
    
    col_img1, col_img2 = st.columns(2)

    with col_img1:
        st.markdown("**Confusion Matrix**")
        if os.path.exists(cm_file):
            st.image(Image.open(cm_file), caption="Actual vs Predicted Labels", use_container_width=True)
        else:
            st.warning("Confusion Matrix image not found.")

    with col_img2:
        st.markdown("**ROC-AUC Curve**")
        if os.path.exists(roc_file):
            st.image(Image.open(roc_file), caption="True Positive Rate vs False Positive Rate", use_container_width=True)
        else:
            st.warning("ROC Curve image not found.")

else:
    st.error("Metrics data not found. Please ensure the training pipeline has executed successfully and artifacts are saved in the 'assets' directory.")