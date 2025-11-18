import streamlit as st
from dashboard_admin import admin_dashboard
from dashboard_user import user_dashboard
from auth import login, logout, get_user_type

st.set_page_config(page_title="Gestión de Blog", layout="wide")


from auth import load_session

if "user" not in st.session_state:
    st.session_state["user"] = load_session()

if st.session_state["user"] is None:
    login()
else:
    user_type = get_user_type(st.session_state["user"])
    if user_type == "admin":
        admin_dashboard()
    else:
        user_dashboard()
    if st.button("Cerrar sesión"):
        logout()
