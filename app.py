import streamlit as st
import requests
from shared import switch_to_login

st.set_page_config(page_title="📄 Quiz Generator", layout="centered")

if "token" not in st.session_state:
    st.warning("🔐 Please login to access the application.")
    switch_to_login()

else:
    st.title("📄 PDF Question Generator")
    st.success(f"Welcome, {st.session_state['username']} 👋")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        switch_to_login()

    pdf_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])
    if pdf_file is not None:
        filename = pdf_file.name

        if st.button("🧠 Generate Questions"):
            with st.spinner("Processing PDF..."):
                response = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files={"pdf_file": (filename, pdf_file, "application/pdf")},
                    data={"filename": filename},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                if response.status_code == 200:
                    st.success("✅ Questions generated!")
                    st.download_button("⬇ Download QA CSV", data=response.content, file_name="QA.csv", mime="text/csv")
                else:
                    st.error(f"❌ Upload failed: {response.status_code} - {response.text}")