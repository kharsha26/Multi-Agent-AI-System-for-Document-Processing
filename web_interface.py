import streamlit as st
import requests
import os
import json
from io import BytesIO

st.set_page_config(page_title="Document Processor", layout="wide")
st.title("Multi-Agent Document Processor")

def process_file(uploaded_file):
    try:
        file_bytes = uploaded_file.read()
        file_for_upload = (uploaded_file.name, BytesIO(file_bytes))
        response = requests.post(
            "http://localhost:8000/process",
            files={"file": file_for_upload}
        )
        return response
    except Exception as e:
        st.error(f"File processing error: {str(e)}")
        return None

uploaded_file = st.file_uploader(
    "Choose a document file",
    type=["pdf", "json", "eml", "txt"],
    accept_multiple_files=False
)

if uploaded_file:
    st.success(f"File ready: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

    if st.button("Process Document"):
        with st.spinner("Processing..."):
            response = process_file(uploaded_file)

            if response and response.status_code == 200:
                result = response.json()
                st.session_state.result = result
                st.success("Processing successful!")
                st.json(result)
            else:
                st.error("Processing failed. See server logs for details.")

if 'result' in st.session_state:
    st.download_button(
        label="Download Results",
        data=json.dumps(st.session_state.result, indent=2),
        file_name="processing_results.json",
        mime="application/json"
    )
