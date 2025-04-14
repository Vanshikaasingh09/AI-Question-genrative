import streamlit as st
import requests
from shared import switch_to_login

st.set_page_config(page_title="Signup", layout="centered")

st.header("👤 Create an Account")

username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Signup"):
    res = requests.post(
        "http://127.0.0.1:8000/signup",
        data={"username": username, "email": email, "password": password}
    )
    if res.status_code == 200:
        st.success("🎉 Signup successful! Please log in.")
        switch_to_login()
    else:
        st.error(res.text)

if st.button("Already have an account? Login"):
    switch_to_login()
