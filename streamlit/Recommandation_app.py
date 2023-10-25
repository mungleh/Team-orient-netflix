import os
import json
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# connection
load_dotenv()

username = os.getenv("username")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname")

connection_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{dbname}"
engine = create_engine(connection_string)

api_ip = os.getenv("api_ip")
api_port = os.getenv("api_port")

ngrok = f"{api_ip}:{api_port}"


# requests
df = pd.read_sql_query("SELECT * FROM movie_table", engine)


# app
st.set_page_config(
    layout="wide"
)


option = st.selectbox('What film de you like ?', df)

st.write(f"You chose {option}")


if st.button("Give me recomendations !"):

    response = requests.post(f"http://{ngrok}/predict?input_title={option}")

    # Check the response status code
    if response.status_code == 200:
        # Print the response content

        recomendations = response.json()

        st.json(recomendations)

        recomendations_dict = json.loads(recomendations)

        formatted_json = json.dumps(recomendations_dict, indent=4)

        # put = pd.read_sql_query(f"INSERT INTO `inputs-table` (input, output) VALUES ('{option}', '[{formatted_json}]')", engine)

        # with engine.connect() as conn:
        #     conn.execute(put)

        # st.write(f"INSERT INTO `inputs-table` (input, output) VALUES ('{option}', [{formatted_json}])")

    else:
        st.write(f"Error - Status code: {response.status_code}")
