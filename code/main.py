from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from fastapi.responses import JSONResponse, FileResponse
import uuid
from langchain.agents import AgentExecutor
from code.tools_agent import user_wants_download, generate_prompt_descargar, generate_prompt_responder
import traceback

# Config .env
from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")

app = FastAPI()

# CORS to allow connection with Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: str

# SQLite database connection
sqlite_db_path = os.path.join(os.getcwd(), "data", "db_scoring_ai.db")


db_sqlite = SQLDatabase.from_uri(
    f"sqlite:///{sqlite_db_path}",
    include_tables=["table_scoring_ai"] 
)

# LLM
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
DATABRICKS_ENDPOINT = os.getenv('DATABRICKS_ENDPOINT')
DATABRICKS_MODEL = os.getenv('DATABRICKS_MODEL')

llm = ChatOpenAI(
    openai_api_key=DATABRICKS_TOKEN,
    openai_api_base=DATABRICKS_ENDPOINT,
    model_name=DATABRICKS_MODEL,
    temperature=0
)

# Toolkit and SQL Agent for SQLite
toolkit_sqlite = SQLDatabaseToolkit(db=db_sqlite, llm=llm)  # SQLite toolkit

@app.post("/chat")
async def chat_with_sql(input: QueryInput):
    try:
        if user_wants_download(input.query):
            # Mode: Generate SQL for download
            selected_prompt = generate_prompt_descargar(input)
            selected_toolkit = toolkit_sqlite 
        else:
            # Mode: Execute and respond
            selected_prompt = generate_prompt_responder(input)
            selected_toolkit = toolkit_sqlite

        agent = create_sql_agent(llm=llm, toolkit=selected_toolkit, verbose=True)

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent.agent,
            tools=selected_toolkit.get_tools(),
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
            early_stopping_method="generate"
        )

        result = agent_executor.run(selected_prompt)

        return JSONResponse(content={"response": result})

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Detailed error:\n{tb}")
        return JSONResponse(status_code=500, content={"error": f"Internal error: {str(e)}"})


@app.post("/execute_sql")
async def execute_sql(input: QueryInput):
    try:
        query = input.query
        print(f"🟡 Executing SQL:\n{query}")
        df = pd.read_sql(query, db_sqlite._engine)
        file_id = str(uuid.uuid4())
        file_path = f"downloads/{file_id}.csv"
        os.makedirs("downloads", exist_ok=True)
        df.to_csv(file_path, index=False)
        return {"file_path": file_path}
    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Error in execute_sql:\n", tb)
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download")
async def download_file(path: str):
    return FileResponse(path, media_type='text/csv', filename=os.path.basename(path))