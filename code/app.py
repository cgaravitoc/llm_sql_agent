import streamlit as st
import requests

# Configuración inicial
st.set_page_config(page_title="Chat SQL", layout="centered")
st.title("💬 Chatbot IA para campañas de crédito")

API_URL = "http://localhost:8000"

# Sidebar con instrucciones
st.sidebar.title("Instrucciones")
st.sidebar.markdown(""" 
    Bienvenido al asistente de consultas a bases de datos para generar campañas de crédito focalizadas. Puedes hacer preguntas sobre las tablas y columnas disponibles en la base de datos.   

    Puedes hacer preguntas como:

    - "¿Cuántos clientes tienen un resultado de prospectación aprobado?"
    - "¿Cuáles son los resultados de las ofertas de crédito para un cliente específico?"

    Para generar un archivo CSV, incluye "descargar" o "generar archivo" en tu pregunta:

    - "¿Cuántos clientes tienen un resultado de prospectación aprobado? Descargar"
    - "¿Cuáles son los resultados de las ofertas de crédito para un cliente específico? Generar archivo"
    """)

# Inicializar el historial de chat si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar historial del chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario tipo chatbot
if prompt := st.chat_input("Haz tu pregunta en lenguaje natural"):
    # Mostrar el mensaje del usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Procesar la consulta
    with st.spinner("Pensando..."):
        try:
            response = requests.post(f"{API_URL}/chat", json={"query": prompt})
            data = response.json()

            if "response" in data:
                respuesta = data["response"]
                st.chat_message("assistant").markdown(respuesta)
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta})

                # Si incluye solicitud de archivo
                if "generar el archivo" in respuesta.lower():
                    try:
                        sql_code = respuesta.split("```sql")[1].split("```")[0]
                        exec_response = requests.post(f"{API_URL}/execute_sql", json={"query": sql_code})
                        file_info = exec_response.json()
                        download_url = f"{API_URL}/download?path={file_info['file_path']}"

                        if "file_path" in file_info:
                            st.success("✅ Archivo generado")
                            st.markdown(f"[📥 Descargar archivo CSV]({download_url})")

                    except Exception as e:
                        st.error("Error generando el archivo.")
            else:
                st.chat_message("assistant").markdown("❌ " + data.get("error", "Error desconocido."))
                st.session_state.chat_history.append({
                    "role": "assistant", "content": "❌ " + data.get("error", "Error desconocido.")
                })

        except Exception as e:
            st.chat_message("assistant").markdown("❌ No se pudo conectar con la API.")
            st.session_state.chat_history.append({
                "role": "assistant", "content": "❌ No se pudo conectar con la API."
            })
