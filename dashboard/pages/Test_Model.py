import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(
    page_title="Manual Inference",
    layout="centered"
)

st.title("Manual Inference Testing")
st.markdown("Test the classification model model by sending a custom text string to the inference API.")
st.markdown("---")

# --- Input Area ---
st.subheader("Input Data")
user_input = st.text_area(
    "Review Text",
    placeholder="Enter the customer review text here to analyze sentiment...",
    height=150
)

# --- Prediction Logic ---
if st.button("Run Prediction", type="primary"):
    if not user_input.strip():
        st.warning("Input text cannot be empty.")
    else:
        # Define API Endpoint (Internal Docker Network)
        API_URL = "http://aerostream_api:8000/predict"
        
        try:
            with st.spinner("Processing request..."):
                # Prepare Payload
                payload = {"texts": [user_input]}
                
                # Send Request
                response = requests.post(API_URL, json=payload, timeout=5)
                response.raise_for_status()
                
                # Parse Response
                predictions = response.json()
                result = predictions[0] 
                
                sentiment = result.get('sentiment', 'Unknown').capitalize()
                confidence = result.get('confidence', 0.0)

            # --- Display Results ---
            st.markdown("### Analysis Results")
            
            # Use columns for a clean metric layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="Predicted Sentiment", value=sentiment)
            
            with col2:
                st.metric(label="Confidence Score", value=f"{confidence:.4f}")

            # Visual Indicator
            st.markdown("**Confidence Level**")
            st.progress(confidence)

            # Contextual Status Box
            if sentiment.lower() == "positive":
                st.success(f"Classified as {sentiment} with {confidence:.1%} confidence.")
            elif sentiment.lower() == "negative":
                st.error(f"Classified as {sentiment} with {confidence:.1%} confidence.")
            else:
                st.info(f"Classified as {sentiment} with {confidence:.1%} confidence.")

        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Unable to reach the API service at http://aerostream_api:8000.")
        except Exception as e:
            st.error(f"System Error: {str(e)}")