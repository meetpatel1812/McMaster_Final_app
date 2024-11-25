from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import streamlit as st
from urllib.parse import quote
import pandas as pd

hide_streamlit_style = """
    <style>
    #GithubIcon {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {overflow: hidden;}
    header {visibility: hidden;}
    </style>
"""

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    # URL encode the password
    encoded_password = quote(password)
    db_uri = f"mysql+mysqlconnector://{user}:{encoded_password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
    You are a data analyst at a University. You are interacting with a user who is asking you questions about the students's database. Use database sql3747402.resume_ai.
Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    <SCHEMA>{schema}</SCHEMA>
    =

    Conversation History: {chat_history}

    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.

    For example:
    Question: Give me all students details
    SQL Query: SELECT * FROM sql3747402.resume_ai;

    Your turn:

    Question: {question}
    SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)

    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)

    template = """
    You are a data analyst at a University. You are interacting with a user who is asking you questions about the student's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model='llama3-8b-8192', temperature=0)

    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response=lambda vars: db.run(vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

# Load environment variables
load_dotenv()

# Set up Streamlit page
st.set_page_config(page_title="AI Powered Admin Chatbot", page_icon="mcmaster.png")
st.image("mcmaster.png",width=220)
# Automatically connect to the database
st.title("AI Powered :red[McMaster Chatbot]")


# Database connection parameters (set your own values here)
# db_params = {
#     "Host": "localhost",
#     "Port": "3306",
#     "User": "root",
#     "Password": "Meet@2001",
#     "Database": "testdb"
# }
db_params = {
    "Host": "sql3.freesqldatabase.com",
    "Port": "3306",
    "User": "sql3747402",
    "Password": "4JBhsn93F1",
    "Database": "sql3747402"
}

# Initialize database connection
# db = init_database(
#     db_params["User"],
#     db_params["Password"],
#     db_params["Host"],
#     db_params["Port"],
#     db_params["Database"]
# )
# st.session_state.db = db

db = init_database(
    db_params["User"],
    db_params["Password"],
    db_params["Host"],
    db_params["Port"],
    db_params["Database"]
)
st.session_state.db = db

# Initialize chat history if not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm a AI Powered McMaster chatbot, I will provide information based on Report."),
    ]

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

# Example prompts and their help texts
example_prompts = [
    "Give me Details about all students",
    "who Has CGPA more than 3.8",
    "Give me all students details, just Skills",
    # "what is MTD sales for 1707 as of 28 june 2024 ?",
    # "The famous 'Black Lotus' card",
    # "Wizard card with Vigilance ability",
]

example_prompts_help = [
    "Give me Details about all students",
    "who Has CGPA more than 3.8",
    "Give me all students details, just Skills",
    # "Specific card effect to another mana color",
    # "Search for card names",
    # "Search for card types with specific abilities",
]

# Display buttons for example prompts
button_cols = st.columns(3)
button_cols_2 = st.columns(3)

button_pressed = ""

if button_cols[0].button(example_prompts[0], help=example_prompts_help[0]):
    button_pressed = example_prompts[0]
elif button_cols[1].button(example_prompts[1], help=example_prompts_help[1]):
    button_pressed = example_prompts[1]
elif button_cols[2].button(example_prompts[2], help=example_prompts_help[2]):
    button_pressed = example_prompts[2]

# elif button_cols_2[0].button(example_prompts[3], help=example_prompts_help[3]):
#     button_pressed = example_prompts[3]
# elif button_cols_2[1].button(example_prompts[4], help=example_prompts_help[4]):
#     button_pressed = example_prompts[4]
# elif button_cols_2[2].button(example_prompts[5], help=example_prompts_help[5]):
#     button_pressed = example_prompts[5]




# Get user input
user_query = st.chat_input("Type a message...")

if button_pressed:
    user_query = button_pressed

if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)

        # Display the response as a table if it is a DataFrame, otherwise as text
        if isinstance(response, pd.DataFrame):
            st.dataframe(response)
        else:
            st.markdown(response)

    st.session_state.chat_history.append(AIMessage(content=response))
