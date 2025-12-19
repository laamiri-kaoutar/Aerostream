import streamlit as st
import json
import os
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Model Evaluation", layout="wide")

st.title("Model Performance Report")
st.markdown("### Logistic Regression Evaluation Metrics")
st.markdown("---")

# --- Path Setup ---
# Simple fallback logic for Docker vs Local
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

    # 2. Per-Class Data Table
    st.subheader("Detailed Class Metrics")
    
    # Convert JSON to DataFrame and clean it up
    classes = data.get("classes", {})
    # Filter out the summary rows
    clean_data = {k: v for k, v in classes.items() if k not in ['accuracy', 'macro avg', 'weighted avg']}
    
    df = pd.DataFrame(clean_data).T # Transpose
    df = df[['precision', 'recall', 'f1-score', 'support']] # Reorder
    
    # Display with simple highlighting
    st.dataframe(
        df.style.highlight_max(axis=0, color='#e6e6e6').format("{:.2f}"),
        use_container_width=True
    )

    st.divider()

    # 3. Visualization Images
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