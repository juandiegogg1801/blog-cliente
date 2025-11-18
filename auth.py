import streamlit as st

import requests

SERVER_URL = "http://localhost:8000"  # Cambia esto por la IP del servidor en red

def login():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if not username or not password:
            st.error("Debes ingresar usuario y contraseña")
            return
        data = {"username": username, "password": password}
        response = requests.post(f"{SERVER_URL}/login", data=data)
        if response.status_code == 200:
            result = response.json()
            st.session_state["user"] = {"username": username, "token": result["access_token"], "type": result["user_type"]}
            st.success("Ingreso exitoso")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

def logout():
    user = st.session_state.get("user")
    if user:
        try:
            requests.post(f"{SERVER_URL}/logout", json={"username": user["username"]})
        except Exception:
            pass
    st.session_state["user"] = None

def get_user_type(user):
    return user.get("type", "usuario")
