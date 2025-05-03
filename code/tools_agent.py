import yaml
import os

sqlite_db_path = os.path.join(os.getcwd(), "data", "sales_dimensional.db")


with open(sqlite_db_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

metadata = config["metadata"]
examples = config["examples"]


def user_wants_download(prompt: str) -> bool:
    return "download" in prompt.lower() \
        or "generate file" in prompt.lower() \
        or "generates file" in prompt.lower()



def generate_prompt_descargar(input: str) -> str:
    return f"""
            You are an expert in SQL generation. Always respond in Spanish.
            Instructions:
            - Generate only the SQL code based on the user's question.
            - DO NOT execute the SQL.
            - DO NOT analyze the results.
            - DO NOT return the response explained in natural language.
            - Do not use ORDER BY unless the user specifies it.
            - DO NOT answer questions by analyzing data.
            - Do not write Thought, Action, or Observation.
            - Every query must include all columns of the table.
            - When you finish constructing the SQL, you must always respond in this format:

                Final Answer: "generate the file".
                ```sql
                [Your SQL query here]

            Tables and columns:
            {metadata}

            examples:
            {examples}

            User's question:
            {input.query}

        """

def generate_prompt_responder(input: str) -> str: 
    return f"""
                You are an expert assistant in financial data analysis. Always respond in English.

                Instructions:
                - Construct an SQL query that answers the user's question.
                - Execute the SQL query.
                - Analyze the results.
                - Return the response explained in natural language.
                - Do not include the final SQL code in the response unless the user explicitly requests it.

                Tables and columns:
                {metadata}

                Examples:
                {examples}

                User's question:
                {input.query}
            """
