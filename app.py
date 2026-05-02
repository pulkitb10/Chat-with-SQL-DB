import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_classic.sql_database import SQLDatabase
from langchain_classic.agents.agent_types import AgentType
from langchain_classic.callbacks import StreamlitCallbackHandler
from langchain_classic.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="Langchain - Chat with SQL DB", page_icon=":robot_face:")
st.title("Langchain - Chat with SQL DB")

INJECTION_WARNING = """
            SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.Read more [here](https://python.langchain.com/docs/security).
            """

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

## Radio button to select the database
radio_opt = ["Use SQLLite3 database - Student.db","Connect to your SQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MYSQL host")
    mysql_user = st.sidebar.text_input("Provide MYSQL username")
    mysql_password = st.sidebar.text_input("Provide MYSQL password",type="password")
    mysql_db = st.sidebar.text_input("Provide MYSQL database name")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input("Enter your Groq API Key:", type="password")

if not db_uri:
    st.info("Please enter the Database information and uri")

if not api_key:
    st.info("Please add the groq api key")

## LLM Model
if api_key:
    llm = ChatGroq(groq_api_key=api_key,model_name="llama-3.3-70b-versatile",streaming=True)
@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri == LOCALDB:
        db_filepath = (Path(__file__).parent/"student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all the MYSQL connection details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    

if db_uri == MYSQL:
    db = configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db = configure_db(db_uri)

#Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    max_iterations=30,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role":"assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything about the database")

if "insert" or "delete" in user_query.lower():
    st.warning("The query seems to be trying to modify the database. Please note that the agent is configured to only read from the database and not make any modifications for security reasons.")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)