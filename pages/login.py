import streamlit as st
import requests
from shared import switch_to_main, switch_to_signup

st.set_page_config(page_title="Login", layout="centered")

st.header("🔑 Login to your account")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = requests.post(
        "http://127.0.0.1:8000/login",
        data={"username": username, "password": password}
    )
    if res.status_code == 200:
        st.session_state["token"] = res.json()["access_token"]
        st.session_state["username"] = username
        st.success("✅ Logged in successfully!")
        switch_to_main()
    else:
        st.error("❌ Invalid credentials")

if st.button("Don't have an account? Signup"):
    switch_to_signup()
