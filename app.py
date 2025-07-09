import streamlit as st
from langchain_groq import ChatGroq
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from pathlib import Path
import sqlite3
import urllib.parse
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.agents import create_sql_agent
from langchain.callbacks import StreamlitCallbackHandler
LOCALDB = 'USE_LOCALDB'
MYSQL = 'USE_MYSQL'


# Title
st.title('AskSQL')

# db config

with st.sidebar:
    st.header('Config')
    config = st.selectbox('config', options=['Sqlite', 'MySQL'],)
    if config == 'MySQL':
        my_sqlhost = st.text_input('mysql host')
        username = st.text_input('Username')
        dbname = st.text_input('Database Name')
        password = st.text_input('Password', type='password')

        db_uri = MYSQL
    else:
        db_uri = LOCALDB

groq_api_key = st.sidebar.text_input('groq_api_key', type='password')


# Hnadling config
if not groq_api_key:
    st.warning('Enter your groq api key')
if db_uri == MYSQL:
    if not my_sqlhost or not username or not password or not dbname:
        st.warning('Fill complete details before proceeding')

# llm model
if groq_api_key:
    llm = ChatGroq(groq_api_key=groq_api_key,
                   model_name='Llama3-8b-8192', streaming=True)

# db configure function


@st.cache_resource(ttl='2h')
def configure_db(db_uri, db_host=None, db_user=None, db_pass=None, db_name=None):
    if db_uri == LOCALDB:

        db_file_path = (Path(__file__).parent/'Student.db').absolute()

        def creator(): return sqlite3.connect(
            f"file:{db_file_path}?mode=ro", uri=True)
        return SQLDatabase(create_engine('sqlite:///', creator=creator))
    elif db_uri == MYSQL:
        if not (my_sqlhost and username and password and dbname):
            st.warning('Fill complete details before proceeding')
            st.stop()
        else:
            encoded_pass = urllib.parse.quote_plus(db_pass)
            return SQLDatabase(
                create_engine(
                    f"mysql+mysqlconnector://{db_user}:{encoded_pass}@{db_host}/{db_name}")
            )


if db_uri == LOCALDB:
    db = configure_db(db_uri=db_uri)
else:
    db = configure_db(
        db_uri=MYSQL,
        db_host=my_sqlhost,
        db_user=username,             # or your actual username
        db_pass=password,
        db_name=dbname
    )
# sql toolkit
if groq_api_key:
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(toolkit=sql_toolkit, verbose=True,llm=llm,
                            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)


    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages=[{'role':'🤖','content':'Ask me anything from your table'}]
        
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])


    query=st.chat_input('Tell me all records')

    if query:
        st.session_state.messages.append({'role':'👤','content':query})
        with st.chat_message('👤'):
            st.markdown(query)
        st_cb=StreamlitCallbackHandler(st.container())
        response=agent.run(query,callbacks=[st_cb])
        st.session_state.messages.append({'role':'🤖','content':response})
        with st.chat_message('🤖'):
            st.markdown(response)