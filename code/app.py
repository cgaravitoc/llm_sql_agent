import streamlit as st
import requests

# Configuración inicial
st.set_page_config(page_title="Chat SQL", layout="centered")
st.title("💬 Chatbot IA - from natural language to SQL")

API_URL = "http://localhost:8000"

# Sidebar con instrucciones
st.sidebar.title("Instrucciones")
st.sidebar.markdown(""" 
    Welcome to the database query assistant for undestanding sales database. You can ask questions about the available tables and columns in the database.   

    You can ask questions like:

    - "How many clients have bougth a product?"
    - "Which are the prefferd products for a specific client?"

    To generate a CSV file, include "download" or "generate file" in your question:

    - ""How many clients have bougth a product? Download"
    - "Which are the prefferd products for a specific client? Generate file"
    """)


# Inicializar el historial de chat si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar historial del chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario tipo chatbot
if prompt := st.chat_input("Do your question in natural language..."):
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
                st.chat_message("assistant").markdown("❌ " + data.get("error", "Unknown Error."))
                st.session_state.chat_history.append({
                    "role": "assistant", "content": "❌ " + data.get("error", "Unknown Error.")
                })

        except Exception as e:
            st.chat_message("assistant").markdown("❌ It was not possible to connect with the API.")
            st.session_state.chat_history.append({
                "role": "assistant", "content": "❌ It was not possible to connect with the API."
            })
