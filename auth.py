import streamlit as st
import requests
import os
import json

SERVER_URL = "http://192.168.20.46:8000"  # Cambia esto por la IP del servidor en red
SESSION_FILE = ".session"

def save_session(user):
    with open(SESSION_FILE, "w") as f:
        json.dump(user, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

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
            user = {"username": username, "token": result["access_token"], "type": result["user_type"]}
            st.session_state["user"] = user
            save_session(user)
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
        clear_session()
        st.rerun()

def get_user_type(user):
    return user.get("type", "usuario")
