import streamlit as st
import requests

st.set_page_config(page_title="Inference Test", layout="centered")

st.title("Manual Inference")

# Input
text_input = st.text_area("Review Text", height=150)

if st.button("Run Prediction", type="primary"):
    if not text_input.strip():
        st.warning("Input required.")
    else:
        try:
            # API Call
            response = requests.post(
                "http://aerostream_api:8000/predict",
                json={"texts": [text_input]},
                timeout=5
            )
            response.raise_for_status()
            
            # Parse
            data = response.json()[0]
            sentiment = data.get('sentiment', 'Unknown').capitalize()
            confidence = data.get('confidence', 0.0)

            # Display Results
            st.markdown("### Results")
            col1, col2 = st.columns(2)
            col1.metric("Sentiment", sentiment)
            col2.metric("Confidence", f"{confidence:.4f}")
            st.progress(confidence)

        except Exception as e:
            st.error(f"Error: {str(e)}")