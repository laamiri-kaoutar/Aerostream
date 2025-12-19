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

# --- Main Display ---
if os.path.exists(metrics_path):
    with open(metrics_path, 'r') as f:
        data = json.load(f)

    # 1. Top Level Metrics
    acc = data.get("accuracy", 0)
    f1 = data.get("macro_avg_f1", 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Accuracy", f"{acc:.2%}")
    col2.metric("Macro F1-Score", f"{f1:.2%}")
    col3.metric("Total Classes", "3 (Pos, Neu, Neg)")

    st.divider()

    # 2. Detailed Analysis (Table + Graph)
    st.subheader("Detailed Class Metrics")

    # Data Processing
    classes = data.get("classes", {})
    clean_data = {k: v for k, v in classes.items() if k not in ['accuracy', 'macro avg', 'weighted avg']}
    
    df = pd.DataFrame(clean_data).T
    df = df[['precision', 'recall', 'f1-score', 'support']]
    
    # Layout: Table on Left, Graph on Right
    c_table, c_graph = st.columns([1, 1])

    with c_table:
        st.markdown("**Metric Values**")
        st.dataframe(
            df.style.highlight_max(axis=0, color='#e6e6e6').format("{:.2f}"),
            use_container_width=True
        )

    with c_graph:
        st.markdown("**Metric Comparison**")
        # Transform data for plotting
        df_plot = df.reset_index().melt(id_vars='index', value_vars=['precision', 'recall', 'f1-score'])
        df_plot.columns = ['Class', 'Metric', 'Score']
        
        # Create Professional Bar Chart
        fig = px.bar(
            df_plot, 
            x='Class', 
            y='Score', 
            color='Metric', 
            barmode='group',
            height=300,
            color_discrete_sequence=px.colors.qualitative.G10
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

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
    st.error(f"Artifacts not found in directory: {ASSETS_DIR}. Please run the training notebook.")