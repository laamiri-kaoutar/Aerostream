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

ASSETS_DIR = "assets" if os.path.exists("assets") else "../assets"
metrics_path = os.path.join(ASSETS_DIR, "training_metrics.json")
cm_path = os.path.join(ASSETS_DIR, "confusion_matrix.png")
roc_path = os.path.join(ASSETS_DIR, "roc_curve.png")

if os.path.exists(metrics_path):
    with open(metrics_path, 'r') as f:
        data = json.load(f)

    acc = data.get("accuracy", 0)
    f1 = data.get("macro_avg_f1", 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Accuracy", f"{acc:.2%}")
    col2.metric("Macro F1-Score", f"{f1:.2%}")
    col3.metric("Total Classes", "3")

    st.divider()

    st.subheader("Detailed Class Metrics")

    # Simplified Data Processing
    # Convert JSON directly to DF and drop summary rows in one go
    df = pd.DataFrame(data.get("classes", {})).T
    df = df.drop(['accuracy', 'macro avg', 'weighted avg'], errors='ignore')
    df = df[['precision', 'recall', 'f1-score', 'support']]
    
    c_table, c_graph = st.columns([1, 1])

    with c_table:
        st.caption("Metric Values")
        st.dataframe(df.style.format("{:.2f}"), use_container_width=True)

    with c_graph:
        st.caption("Metric Comparison")
        df_plot = df.reset_index().melt(id_vars='index', value_vars=['precision', 'recall', 'f1-score'])
        
        fig = px.bar(
            df_plot, 
            x='index', 
            y='value', 
            color='variable', 
            barmode='group',
            height=300,
            color_discrete_sequence=["#68D391", "#A0AEC0", "#FF8087"]
        )
        fig.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None)
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
    st.error(f"Artifacts not found in {ASSETS_DIR}. Please run the training notebook.")