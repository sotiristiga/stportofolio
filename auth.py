import streamlit as st

PASSWORD = "1234"

def check_login():
    if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Function to handle login
    def login():
        if st.session_state.password_input == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("Incorrect password")
            st.session_state.logged_in = False

# Only show input if not logged in
    if not st.session_state.logged_in:
        st.text_input("Enter password", type="password", key="password_input")
        st.button("Login", on_click=login)
        if not st.session_state.logged_in:
            st.stop()
