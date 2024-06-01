import streamlit as st

from frontend.utils import clear_all_but_first_page

st.title("Logout")
st.session_state["logged_in"] = False
st.success("Logged Out Successfully")
clear_all_but_first_page()
