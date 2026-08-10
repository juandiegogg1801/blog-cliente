import streamlit as st

import requests
from auth import SERVER_URL
from dashboard_user import show_flash, confirm_delete_dialog

def admin_dashboard():
    st.title("Dashboard Admin")
    user = st.session_state.get("user")
    if not user:
        st.error("No has iniciado sesión")
        return
    token = user["token"]

    flash = st.session_state.pop("flash", None)
    if flash:
        show_flash(*flash)
    if st.session_state.get("confirm_delete"):
        confirm_delete_dialog()


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
            edit_version = st.session_state.get(f"edit_version_user_{u['id']}", 0)
            new_username = col3.text_input("Nuevo usuario", value=u["username"], key=f"edit_username_{u['id']}_{edit_version}")
            new_password = col3.text_input("Nueva contraseña", type="password", key=f"edit_password_{u['id']}_{edit_version}")
            new_type = col3.selectbox("Tipo", ["usuario", "admin"], index=0 if u["type"]=="usuario" else 1, key=f"edit_type_{u['id']}_{edit_version}")
            changed = new_username != u["username"] or new_password or new_type != u["type"]
            update_col, cancel_col = col4.columns(2)
            if update_col.button("Actualizar", key=f"update_{u['id']}"):
                if changed:
                    r = requests.post(
                        f"{SERVER_URL}/users/update",
                        params={"user_id": u["id"], "username": new_username, "password": new_password, "type": new_type, "token": token}
                    )
                    if r.status_code == 200:
                        st.session_state["flash"] = ("success", "Usuario actualizado")
                        st.session_state[f"edit_version_user_{u['id']}"] = edit_version + 1
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "Error al actualizar usuario"))
            if changed and cancel_col.button("Cancelar", key=f"cancel_user_{u['id']}"):
                st.session_state[f"edit_version_user_{u['id']}"] = edit_version + 1
                st.session_state["flash"] = ("info", "No se modificaron campos")
                st.rerun()
            if col5.button("Eliminar", key=f"delete_{u['id']}"):
                st.session_state["confirm_delete"] = {
                    "url": f"{SERVER_URL}/users/delete",
                    "params": {"user_id": u["id"], "token": token},
                    "label": f'el usuario "{u["username"]}"',
                    "success_msg": "Usuario eliminado",
                    "error_msg": "Error al eliminar usuario",
                }
                st.rerun()
    else:
        st.info("No hay usuarios para mostrar.")

    st.subheader("Crear usuario")
    new_user_form_version = st.session_state.get("new_user_form_version", 0)
    new_username = st.text_input("Nuevo usuario", key=f"new_username_{new_user_form_version}")
    new_password = st.text_input("Contraseña", type="password", key=f"new_password_{new_user_form_version}")
    new_type = st.selectbox("Tipo", ["usuario", "admin"], key=f"new_type_{new_user_form_version}")
    if st.button("Crear usuario"):
        r = requests.post(f"{SERVER_URL}/users/create", json={"username": new_username, "password": new_password, "type": new_type}, params={"token": token})
        if r.status_code == 200:
            st.session_state["flash"] = ("success", "Usuario creado")
            st.session_state["new_user_form_version"] = new_user_form_version + 1
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
            edit_post_version = st.session_state.get(f"edit_version_post_{post['id']}pub", 0)
            new_title = pcol4.text_input("Nuevo título", value=post["title"], key=f"edit_title_{post['id']}pub_{edit_post_version}")
            new_content = pcol4.text_area("Nuevo contenido", value=post["content"], key=f"edit_content_{post['id']}pub_{edit_post_version}")
            changed = new_title != post["title"] or new_content != post["content"]
            update_post_col, cancel_post_col = pcol4.columns(2)
            if update_post_col.button("Actualizar", key=f"update_post_{post['id']}pub"):
                if changed:
                    r = requests.post(f"{SERVER_URL}/posts/update", params={"post_id": post['id'], "title": new_title, "content": new_content, "token": token})
                    if r.status_code == 200:
                        st.session_state["flash"] = ("success", "Publicación actualizada")
                        st.session_state[f"edit_version_post_{post['id']}pub"] = edit_post_version + 1
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "Error al actualizar publicación"))
            if changed and cancel_post_col.button("Cancelar", key=f"cancel_post_{post['id']}pub"):
                st.session_state[f"edit_version_post_{post['id']}pub"] = edit_post_version + 1
                st.session_state["flash"] = ("info", "No se modificaron campos")
                st.rerun()
            if pcol5.button("Eliminar", key=f"delete_post_{post['id']}pub"):
                st.session_state["confirm_delete"] = {
                    "url": f"{SERVER_URL}/posts/delete",
                    "params": {"post_id": post['id'], "token": token},
                    "label": f'la publicación "{post["title"]}"',
                    "success_msg": "Publicación eliminada",
                    "error_msg": "Error al eliminar publicación",
                }
                st.rerun()
    else:
        st.info("No hay publicaciones para mostrar.")

    st.subheader("Crear publicación")
    new_post_form_version = st.session_state.get("new_post_form_version", 0)
    new_post_title = st.text_input("Título", key=f"new_post_title_{new_post_form_version}")
    new_post_content = st.text_area("Contenido", key=f"new_post_content_{new_post_form_version}")
    if st.button("Crear publicación"):
        r = requests.post(f"{SERVER_URL}/posts/create", params={"title": new_post_title, "content": new_post_content, "token": token})
        if r.status_code == 200:
            st.session_state["flash"] = ("success", "Publicación creada")
            st.session_state["new_post_form_version"] = new_post_form_version + 1
            st.rerun()
        else:
            error_detail = r.json().get("detail", "Error al crear publicación")
            st.error(f"Error al crear publicación: {error_detail}")

    st.markdown("---")
    st.subheader("Logs de auditoría")
    resp = requests.get(f"{SERVER_URL}/audit/logs", params={"token": token})
    logs = resp.json().get("logs", []) if resp.status_code == 200 else []
    log_df = pd.DataFrame(
        [l.strip().split('|') for l in logs],
        columns=["Fecha", "Usuario", "Acción", "IP"],
    )
    if not log_df.empty:
        st.download_button(
            "Exportar CSV",
            data=log_df.to_csv(index=False).encode("utf-8"),
            file_name="audit_logs.csv",
            mime="text/csv",
        )

        audit_search_col, audit_user_col, audit_date_col = st.columns(3)
        audit_search = audit_search_col.text_input("Buscar en la tabla", key="audit_search")
        audit_user_filter = audit_user_col.text_input("Filtrar por usuario", key="audit_user_filter")
        audit_date_filter = audit_date_col.text_input("Filtrar por fecha (YYYY-MM-DD)", key="audit_date_filter")

        filtered_df = log_df
        if audit_user_filter:
            filtered_df = filtered_df[filtered_df["Usuario"].str.contains(audit_user_filter, case=False, na=False)]
        if audit_date_filter:
            filtered_df = filtered_df[filtered_df["Fecha"].str.contains(audit_date_filter, case=False, na=False)]
        if audit_search:
            mask = filtered_df.apply(
                lambda row: row.astype(str).str.contains(audit_search, case=False, na=False).any(), axis=1
            )
            filtered_df = filtered_df[mask]

        # Reinicia a la página 1 cuando cambian los filtros de búsqueda
        audit_filter_key = (audit_search, audit_user_filter, audit_date_filter)
        if st.session_state.get("audit_filter_key") != audit_filter_key:
            st.session_state["audit_filter_key"] = audit_filter_key
            st.session_state["audit_page"] = 1

        PAGE_SIZE = 20
        total_rows = len(filtered_df)
        total_pages = max(1, -(-total_rows // PAGE_SIZE))
        audit_page = min(st.session_state.get("audit_page", 1), total_pages)
        start = (audit_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE

        if total_rows == 0:
            st.info("No hay logs que coincidan con la búsqueda.")
        else:
            st.table(filtered_df.iloc[start:end])

        prev_col, page_col, next_col = st.columns([1, 2, 1])
        if prev_col.button("← Anterior", key="audit_prev", disabled=audit_page <= 1):
            st.session_state["audit_page"] = audit_page - 1
            st.rerun()
        page_col.markdown(
            f"<div style='text-align:center'>Página {audit_page} de {total_pages}</div>",
            unsafe_allow_html=True,
        )
        if next_col.button("Siguiente →", key="audit_next", disabled=audit_page >= total_pages):
            st.session_state["audit_page"] = audit_page + 1
            st.rerun()
    else:
        st.info("No hay logs de auditoría para mostrar.")

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
