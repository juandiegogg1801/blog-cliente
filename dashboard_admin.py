import streamlit as st

import requests
from auth import SERVER_URL

def admin_dashboard():
    st.title("Dashboard Admin")
    user = st.session_state.get("user")
    if not user:
        st.error("No has iniciado sesión")
        return
    token = user["token"]

    st.subheader("Gestión de usuarios")
    resp = requests.get(f"{SERVER_URL}/users/list", params={"token": token})
    users = resp.json() if resp.status_code == 200 else []
    for u in users:
        st.write(f"Usuario: {u['username']} | Tipo: {u['type']}")
        with st.expander(f"Editar/Eliminar {u['username']}"):
            new_username = st.text_input(f"Nuevo nombre de usuario", value=u['username'], key=f"edit_username_{u['id']}")
            new_password = st.text_input(f"Nueva contraseña", type="password", key=f"edit_password_{u['id']}")
            new_type = st.selectbox(f"Tipo", ["usuario", "admin"], index=0 if u['type']=="usuario" else 1, key=f"edit_type_{u['id']}")
            if st.button(f"Actualizar usuario {u['id']}"):
                r = requests.post(f"{SERVER_URL}/users/update", data={"user_id": u['id'], "username": new_username, "password": new_password, "type": new_type, "token": token})
                if r.status_code == 200:
                    st.success("Usuario actualizado")
                    st.experimental_rerun()
                else:
                    st.error(r.json().get("detail", "Error al actualizar usuario"))
            if st.button(f"Eliminar usuario {u['id']}"):
                r = requests.post(f"{SERVER_URL}/users/delete", data={"user_id": u['id'], "token": token})
                if r.status_code == 200:
                    st.success("Usuario eliminado")
                    st.experimental_rerun()
                else:
                    st.error(r.json().get("detail", "Error al eliminar usuario"))

    st.subheader("Crear usuario")
    new_username = st.text_input("Nuevo usuario")
    new_password = st.text_input("Contraseña", type="password")
    new_type = st.selectbox("Tipo", ["usuario", "admin"])
    if st.button("Crear usuario"):
        r = requests.post(f"{SERVER_URL}/users/create", data={"username": new_username, "password": new_password, "type": new_type, "token": token})
        if r.status_code == 200:
            st.success("Usuario creado")
            st.experimental_rerun()
        else:
            st.error(r.json().get("detail", "Error al crear usuario"))

    st.subheader("Gestión de publicaciones de todos")
    resp = requests.get(f"{SERVER_URL}/posts/list", params={"token": token})
    posts = resp.json() if resp.status_code == 200 else []
    for post in posts:
        st.write(f"[{post['id']}] {post['title']} - {post['content']} (Usuario: {post['user_id']})")

    st.subheader("Logs de auditoría")
    resp = requests.get(f"{SERVER_URL}/audit/logs")
    logs = resp.json().get("logs", []) if resp.status_code == 200 else []
    st.table([l.split('|') for l in logs])

    st.subheader("Perfil")
    st.write(f"Usuario: {user['username']}")
    new_password = st.text_input("Nueva contraseña", type="password")
    if st.button("Cambiar contraseña"):
        r = requests.post(f"{SERVER_URL}/users/update_password", data={"new_password": new_password, "token": token})
        if r.status_code == 200:
            st.success("Contraseña actualizada")
        else:
            st.error(r.json().get("detail", "Error al cambiar contraseña"))
