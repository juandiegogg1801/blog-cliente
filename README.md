# Cliente - Gestión de Blog

## Requisitos
- Python 3.8+
- Entorno virtual recomendado

## Instalación
1. Crear y activar entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   pip install streamlit
   ```

## Ejecución
1. Edita `auth.py` y cambia `SERVER_URL` por la IP del servidor:
   ```python
   SERVER_URL = "http://<IP_DEL_SERVIDOR>:8000"
   ```
2. Ejecuta el cliente:
   ```bash
   streamlit run app.py
   ```
3. Accede a la URL que muestra Streamlit (por defecto `http://localhost:8501`).

## Notas
- Usa el usuario admin para gestionar usuarios y publicaciones.
