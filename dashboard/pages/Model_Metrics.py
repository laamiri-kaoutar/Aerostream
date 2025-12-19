import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="Model Evaluation", layout="wide")

st.title("Model Performance Report")
st.markdown("### Logistic Regression Evaluation Metrics")
st.markdown("---")

# --- Path Setup ---
ASSETS_DIR = "assets" if os.path.exists("assets") else "../assets"
metrics_path = os.path.join(ASSETS_DIR, "training_metrics.json")
cm_path = os.path.join(ASSETS_DIR, "confusion_matrix.png")
roc_path = os.path.join(ASSETS_DIR, "roc_curve.png")

# --- Main Logic ---
if os.path.exists(metrics_path):
    with open(metrics_path, 'r') as f:
        data = json.load(f)

    # 1. Top Level KPIs
    acc = data.get("accuracy", 0)
    f1 = data.get("macro_avg_f1", 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Accuracy", f"{acc:.2%}")
    col2.metric("Macro F1-Score", f"{f1:.2%}")
    col3.metric("Total Classes", "3")

    st.divider()

    # 2. Dual Charts (Averages vs Classes)
    st.subheader("Performance Breakdown")

    # --- Data Processing ---
    raw_classes = data.get("classes", {})
    if 'accuracy' in raw_classes:
        del raw_classes['accuracy']
        
    df_full = pd.DataFrame(raw_classes).T
    df_full = df_full[['precision', 'recall', 'f1-score']] # We don't need 'support' for the graph

    # Split into two datasets
    df_avgs = df_full.loc[['macro avg', 'weighted avg']]
    df_classes = df_full.drop(['macro avg', 'weighted avg'], errors='ignore')

    # Color Palette (Vibrant Pastel)
    # Precision=Mint, Recall=Grey, F1=Coral
    colors = ["#68D391", "#A0AEC0", "#FF8087"]

    c_avg, c_class = st.columns(2)

    with c_avg:
        st.caption("Global Averages (Macro vs Weighted)")
        # Plot Averages
        df_plot_avg = df_avgs.reset_index().melt(id_vars='index', value_vars=['precision', 'recall', 'f1-score'])
        
        fig1 = px.bar(
            df_plot_avg, 
            x='index', 
            y='value', 
            color='variable', 
            barmode='group',
            height=300,
            color_discrete_sequence=colors
        )
        fig1.update_layout(xaxis_title=None, yaxis_title="Score", legend_title=None)
        st.plotly_chart(fig1, use_container_width=True)

    with c_class:
        st.caption("Per-Class Performance")
        # Plot Classes
        df_plot_class = df_classes.reset_index().melt(id_vars='index', value_vars=['precision', 'recall', 'f1-score'])
        
        fig2 = px.bar(
            df_plot_class, 
            x='index', 
            y='value', 
            color='variable', 
            barmode='group',
            height=300,
            color_discrete_sequence=colors
        )
        fig2.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # 3. Diagnostic Images
    st.subheader("Diagnostic Plots")
    c1, c2 = st.columns(2)
    
    with c1:
        st.caption("Confusion Matrix")
        if os.path.exists(cm_path):
            st.image(Image.open(cm_path), use_container_width=True)
        else:
            st.warning("Confusion Matrix missing")

    with c2:
        st.caption("ROC-AUC Curve")
        if os.path.exists(roc_path):
            st.image(Image.open(roc_path), use_container_width=True)
        else:
            st.warning("ROC Curve missing")

else:
    st.error(f"Artifacts not found in {ASSETS_DIR}. Please run the training notebook.")