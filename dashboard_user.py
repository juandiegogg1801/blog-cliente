import json
import streamlit as st
import streamlit.components.v1 as components

import requests
from auth import SERVER_URL

def show_flash(level, message):
    styles = {
        "success": ("✅", "#e6f4ea", "#1e7e34"),
        "error": ("⚠️", "#fdecea", "#a94442"),
        "info": ("ℹ️", "#e8f0fe", "#1a56db"),
    }
    icon, bg, color = styles.get(level, styles["info"])
    text = json.dumps(f"{icon} {message}")
    components.html(
        f"""
        <script>
        (function() {{
            const doc = window.parent.document;
            // Limpia cualquier aviso anterior que haya quedado pegado en la página.
            doc.querySelectorAll('.app-flash-banner').forEach((el) => el.remove());

            if (!doc.getElementById('app-flash-style')) {{
                const style = doc.createElement('style');
                style.id = 'app-flash-style';
                style.textContent = `
                    @keyframes app-flash-fade {{
                        0% {{ opacity: 0; }}
                        10% {{ opacity: 1; }}
                        85% {{ opacity: 1; }}
                        100% {{ opacity: 0; }}
                    }}
                `;
                doc.head.appendChild(style);
            }}

            const div = doc.createElement('div');
            div.className = 'app-flash-banner';
            div.textContent = {text};
            Object.assign(div.style, {{
                position: 'fixed',
                top: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: '{bg}',
                color: '{color}',
                padding: '12px 24px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                zIndex: 999999,
                fontWeight: '600',
                fontFamily: 'sans-serif',
                animation: 'app-flash-fade 4s ease forwards',
                pointerEvents: 'none',
            }});
            doc.body.appendChild(div);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )

@st.dialog("Confirmar eliminación")
def confirm_delete_dialog():
    info = st.session_state.get("confirm_delete")
    if not info:
        return
    st.write(f"¿Seguro que deseas eliminar {info['label']}? Esta acción no se puede deshacer.")
    col1, col2 = st.columns(2)
    if col1.button("Cancelar"):
        st.session_state.pop("confirm_delete", None)
        st.rerun()
    if col2.button("Eliminar", type="primary"):
        r = requests.post(info["url"], params=info["params"])
        st.session_state.pop("confirm_delete", None)
        if r.status_code == 200:
            st.session_state["flash"] = ("success", info["success_msg"])
        else:
            try:
                detail = r.json().get("detail", info["error_msg"])
            except Exception:
                detail = info["error_msg"]
            st.session_state["flash"] = ("error", detail)
        st.rerun()

def user_dashboard():
    st.title("Dashboard Usuario")
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

    st.subheader("Tus publicaciones")
    resp = requests.get(f"{SERVER_URL}/posts/list", params={"token": token})
    posts = resp.json() if resp.status_code == 200 else []
    for post in posts:
        st.write(f"**{post['title']}**")
        edit_version = st.session_state.get(f"edit_version_{post['id']}", 0)
        new_title = st.text_input("Nuevo título", value=post['title'], key=f"title_{post['id']}_{edit_version}")
        new_content = st.text_area("Nuevo contenido", value=post['content'], key=f"content_{post['id']}_{edit_version}")
        changed = new_title != post["title"] or new_content != post["content"]
        col1, col2, col3 = st.columns(3)
        if col1.button("Guardar cambios", key=f"save_{post['id']}"):
            if changed:
                r = requests.post(f"{SERVER_URL}/posts/update", params={"post_id": post['id'], "title": new_title, "content": new_content, "token": token})
                if r.status_code == 200:
                    st.session_state["flash"] = ("success", "Publicación actualizada")
                    st.session_state[f"edit_version_{post['id']}"] = edit_version + 1
                    st.rerun()
                else:
                    st.error("Error al actualizar")
        if changed and col2.button("Cancelar", key=f"cancel_{post['id']}"):
            st.session_state[f"edit_version_{post['id']}"] = edit_version + 1
            st.session_state["flash"] = ("info", "No se modificaron campos")
            st.rerun()
        if col3.button("Eliminar", key=f"delete_{post['id']}"):
            st.session_state["confirm_delete"] = {
                "url": f"{SERVER_URL}/posts/delete",
                "params": {"post_id": post['id'], "token": token},
                "label": f'la publicación "{post["title"]}"',
                "success_msg": "Publicación eliminada",
                "error_msg": "Error al eliminar",
            }
            st.rerun()

    st.subheader("Crear nueva publicación")
    form_version = st.session_state.get("new_post_form_version", 0)
    title = st.text_input("Título", key=f"new_post_title_{form_version}")
    content = st.text_area("Contenido", key=f"new_post_content_{form_version}")
    if st.button("Crear publicación"):
        r = requests.post(f"{SERVER_URL}/posts/create", params={"title": title, "content": content, "token": token})
        if r.status_code == 200:
            st.session_state["flash"] = ("success", "Publicación creada")
            st.session_state["new_post_form_version"] = form_version + 1
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
