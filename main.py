# =========================
# INSTALL REQUIRED PACKAGES
# =========================
# pip install sqlalchemy google-generativeai

# =========================
# IMPORTS
# =========================
from sqlalchemy import create_engine, inspect
import google.generativeai as genai
import sqlite3
import json
import re


# =========================
# GEMINI API KEY
# =========================
# Get API Key:
# https://aistudio.google.com/app/apikey

genai.configure(api_key="")


# =========================
# DATABASE PATH
# =========================
db_url = "sqlite:///amazon.db"


# =========================
# STEP 1: EXTRACT DATABASE SCHEMA
# =========================
def extract_schema(db_url):

    engine = create_engine(db_url)

    inspector = inspect(engine)

    schema = {}

    for table_name in inspector.get_table_names():

        columns = inspector.get_columns(table_name)

        schema[table_name] = [
            col['name'] for col in columns
        ]

    return json.dumps(schema, indent=2)


# =========================
# STEP 2: CONVERT TEXT TO SQL USING GEMINI
# =========================
def text_to_sql(schema, user_prompt):

    SYSTEM_PROMPT = """
    You are an expert SQL query generator.

    Your task is to generate ONLY a valid SQLite SQL query.

    RULES:
    - Use only tables and columns provided in schema
    - Use SQLite syntax only
    - Do not explain anything
    - Do not generate markdown
    - Do not generate ```sql
    - Output ONLY SQL query
    """

    final_prompt = f"""
    DATABASE SCHEMA:
    {schema}

    USER QUESTION:
    {user_prompt}

    SQL QUERY:
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash"
    )

    response = model.generate_content(
        SYSTEM_PROMPT + final_prompt
    )

    sql_query = response.text.strip()

    # Remove markdown if model returns it
    sql_query = re.sub(r"```sql|```", "", sql_query).strip()

    return sql_query


# =========================
# STEP 3: EXECUTE SQL QUERY
# =========================
def execute_sql_query(sql_query):

    conn = sqlite3.connect("amazon.db")

    cursor = conn.cursor()

    try:

        cursor.execute(sql_query)

        results = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ] if cursor.description else []

        conn.close()

        return {
            "columns": column_names,
            "results": results
        }

    except Exception as e:

        conn.close()

        return {
            "error": str(e)
        }


# =========================
# STEP 4: MAIN FUNCTION
# =========================
def ask_database(question):

    print("\nExtracting schema...")

    schema = extract_schema(db_url)

    print("\nGenerating SQL query using Gemini...\n")

    sql_query = text_to_sql(schema, question)

    print("Generated SQL Query:\n")
    print(sql_query)

    print("\nExecuting query...\n")

    result = execute_sql_query(sql_query)

    return result


# =========================
# STEP 5: USER INPUT LOOP
# =========================
if __name__ == "__main__":

    while True:

        print("\n==============================")
        print("TEXT TO SQL USING GEMINI")
        print("==============================")

        user_question = input("\nAsk your question (or type exit): ")

        if user_question.lower() == "exit":
            break

        output = ask_database(user_question)

        print("\n==============================")
        print("RESULT")
        print("==============================")

        if "error" in output:

            print("Error:", output["error"])

        else:

            print("\nColumns:")
            print(output["columns"])

            print("\nRows:")

            for row in output["results"]:
                print(row)