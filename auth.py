import streamlit as st

PASSWORD = "1234"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Stop the app if user not logged in
    if not st.session_state.logged_in:
        password = st.text_input("Enter password", type="password", key="password_input")
        if st.button("Login"):
            if password == PASSWORD:
                st.session_state.logged_in = True
                st.experimental_rerun()  # Optional: refresh to hide input
            else:
                st.error("Incorrect password")
                st.stop()
