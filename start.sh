#!/bin/bash

# Lanzar FastAPI backend
uvicorn code.main:app --host 0.0.0.0 --port 8000 &

# Lanzar Streamlit frontend
streamlit run code/app.py --server.port=8502 --server.address=0.0.0.0

# Importante: el último comando se queda en foreground
