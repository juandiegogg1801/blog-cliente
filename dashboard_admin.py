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
    search_username = st.text_input("Buscar usuario por nombre (contiene)")
    resp = requests.get(f"{SERVER_URL}/users/list", params={"token": token})
    users = resp.json() if resp.status_code == 200 else []
    if search_username:
        users = [u for u in users if search_username.lower() in u["username"].lower()]
    import pandas as pd
    user_df = pd.DataFrame(users)
    if not user_df.empty:
        st.markdown("**Usuarios**")
        header_cols = st.columns([2,2,2,2,2])
        header_cols[0].markdown("**Usuario**")
        header_cols[1].markdown("**Tipo**")
        header_cols[2].markdown("**Editar datos**")
        header_cols[3].markdown("**Actualizar**")
        header_cols[4].markdown("**Eliminar**")
        for idx, u in user_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2,2,2,2,2])
            col1.write(u["username"])
            col2.write(u["type"])
            new_username = col3.text_input("Nuevo usuario", value=u["username"], key=f"edit_username_{u['id']}")
            new_password = col3.text_input("Nueva contraseña", type="password", key=f"edit_password_{u['id']}")
            new_type = col3.selectbox("Tipo", ["usuario", "admin"], index=0 if u["type"]=="usuario" else 1, key=f"edit_type_{u['id']}")
            if col4.button("Actualizar", key=f"update_{u['id']}"):
                r = requests.post(
                    f"{SERVER_URL}/users/update",
                    json={"username": new_username, "password": new_password, "type": new_type},
                    params={"user_id": u["id"], "token": token}
                )
                if r.status_code == 200:
                    st.session_state["usuario_actualizado"] = True
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error al actualizar usuario"))
            if col5.button("Eliminar", key=f"delete_{u['id']}"):
                r = requests.post(
                    f"{SERVER_URL}/users/delete",
                    params={"user_id": u["id"], "token": token}
                )
                if r.status_code == 200:
                    st.success("Usuario eliminado")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error al eliminar usuario"))
    else:
        st.info("No hay usuarios para mostrar.")

    st.subheader("Crear usuario")
    new_username = st.text_input("Nuevo usuario")
    new_password = st.text_input("Contraseña", type="password")
    new_type = st.selectbox("Tipo", ["usuario", "admin"])
    if st.button("Crear usuario"):
        r = requests.post(f"{SERVER_URL}/users/create", json={"username": new_username, "password": new_password, "type": new_type}, params={"token": token})
        if r.status_code == 200:
            st.success("Usuario creado")
            st.rerun()
        else:
            error_detail = r.json().get("detail", "Error al crear usuario")
            st.error(f"Error al crear usuario: {error_detail}")

    st.markdown("---")
    st.subheader("Gestión de publicaciones de todos")
    resp = requests.get(f"{SERVER_URL}/posts/list", params={"token": token})
    posts = resp.json() if resp.status_code == 200 else []
    post_df = pd.DataFrame(posts)
    if not post_df.empty:
        st.markdown("**Publicaciones**")
        post_header = st.columns([2,2,2,2,2])
        post_header[0].markdown("**Título**")
        post_header[1].markdown("**Contenido**")
        post_header[2].markdown("**Usuario**")
        post_header[3].markdown("**Actualizar**")
        post_header[4].markdown("**Eliminar**")
        for idx, post in post_df.iterrows():
            pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns([2,2,2,2,2])
            pcol1.write(post["title"])
            pcol2.write(post["content"])
            pcol3.write(post["user_id"])
            new_title = pcol4.text_input("Nuevo título", value=post["title"], key=f"edit_title_{post['id']}pub")
            new_content = pcol4.text_area("Nuevo contenido", value=post["content"], key=f"edit_content_{post['id']}pub")
            if pcol4.button("Actualizar", key=f"update_post_{post['id']}pub"):
                r = requests.post(f"{SERVER_URL}/posts/update", params={"post_id": post['id'], "title": new_title, "content": new_content, "token": token})
                if r.status_code == 200:
                    st.success("Publicación actualizada")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error al actualizar publicación"))
            if pcol5.button("Eliminar", key=f"delete_post_{post['id']}pub"):
                r = requests.post(f"{SERVER_URL}/posts/delete", params={"post_id": post['id'], "token": token})
                if r.status_code == 200:
                    st.success("Publicación eliminada")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error al eliminar publicación"))
    else:
        st.info("No hay publicaciones para mostrar.")

    st.markdown("---")
    st.subheader("Logs de auditoría")
    resp = requests.get(f"{SERVER_URL}/audit/logs")
    logs = resp.json().get("logs", []) if resp.status_code == 200 else []
    st.table([l.split('|') for l in logs])

    st.markdown("---")
    st.subheader("Perfil")
    st.write(f"Usuario: {user['username']}")
    new_password = st.text_input("Nueva contraseña", type="password", key="perfil_new_password")
    if st.button("Cambiar contraseña", key="perfil_btn"):
        r = requests.post(f"{SERVER_URL}/users/update_password", params={"new_password": new_password, "token": token})
        if r.status_code == 200:
            st.success("Contraseña actualizada")
        else:
            st.error(r.json().get("detail", "Error al cambiar contraseña"))
