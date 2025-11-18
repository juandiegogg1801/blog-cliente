import streamlit as st

import requests
from auth import SERVER_URL

def user_dashboard():
    st.title("Dashboard Usuario")
    user = st.session_state.get("user")
    if not user:
        st.error("No has iniciado sesión")
        return
    token = user["token"]

    st.subheader("Tus publicaciones")
    resp = requests.get(f"{SERVER_URL}/posts/list", params={"token": token})
    posts = resp.json() if resp.status_code == 200 else []
    for post in posts:
        st.write(f"**{post['title']}**")
        st.write(post['content'])
        if st.button(f"Editar {post['id']}"):
            new_title = st.text_input("Nuevo título", value=post['title'], key=f"title_{post['id']}")
            new_content = st.text_area("Nuevo contenido", value=post['content'], key=f"content_{post['id']}")
            if st.button(f"Guardar cambios {post['id']}"):
                r = requests.post(f"{SERVER_URL}/posts/update", data={"post_id": post['id'], "title": new_title, "content": new_content, "token": token})
                if r.status_code == 200:
                    st.success("Publicación actualizada")
                    st.experimental_rerun()
                else:
                    st.error("Error al actualizar")
        if st.button(f"Eliminar {post['id']}"):
            r = requests.post(f"{SERVER_URL}/posts/delete", data={"post_id": post['id'], "token": token})
            if r.status_code == 200:
                st.success("Publicación eliminada")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar")

    st.subheader("Crear nueva publicación")
    title = st.text_input("Título")
    content = st.text_area("Contenido")
    if st.button("Crear publicación"):
        r = requests.post(f"{SERVER_URL}/posts/create", params={"title": title, "content": content, "token": token})
        if r.status_code == 200:
            st.success("Publicación creada")
            st.rerun()
        else:
            st.error("Error al crear publicación")

    st.subheader("Perfil")
    st.write(f"Usuario: {user['username']}")
    new_password = st.text_input("Nueva contraseña", type="password")
    if st.button("Cambiar contraseña"):
        r = requests.post(f"{SERVER_URL}/users/update_password", params={"new_password": new_password, "token": token})
        if r.status_code == 200:
            st.success("Contraseña actualizada")
        else:
            st.error(r.json().get("detail", "Error al cambiar contraseña"))
