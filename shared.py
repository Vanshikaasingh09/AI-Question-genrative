import streamlit as st

def switch_to_signup():
    st.switch_page("pages/signup.py")

def switch_to_login():
    st.switch_page("pages/login.py")

def switch_to_main():
    st.switch_page("app.py")
