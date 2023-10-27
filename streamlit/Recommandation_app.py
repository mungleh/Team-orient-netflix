import os
import json
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote

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

if 'recommendations_movies' not in st.session_state:
    st.session_state.recommendations_movies = []
if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = []


if st.button("Give me recomendations !"):

    response = requests.post(f"http://{ngrok}/predict?input_title={option}")

    # Check the response status code
    if response.status_code == 200:

        recommendations = response.json()

        st.session_state.recommendations_movies = recommendations

        recommendations_movies = ', '.join(recommendations)

        st.write(recommendations_movies)

    else:
        st.write(f"Error - Status code: {response.status_code}")

for idx, movie in enumerate(st.session_state.recommendations_movies, 1):
    checkbox_value = movie in st.session_state.selected_movies
    checked = st.checkbox(f"{idx}. {movie}", value=checkbox_value)
    if checked and movie not in st.session_state.selected_movies:
        st.session_state.selected_movies.append(movie)
    elif not checked and movie in st.session_state.selected_movies:
        st.session_state.selected_movies.remove(movie)

st.write(f"You selected: {st.session_state.selected_movies}")

if st.button("OK"):
    if st.session_state.selected_movies:
        selected_movies_str = ', '.join(st.session_state.selected_movies)
        st.write(f"You selected: {selected_movies_str}")
        recommendations_movies = ', '.join(st.session_state.recommendations_movies)
    else:
        selected_movies_str = 'no selections'
        st.write("You haven't selected any movies.")

    data = {
            'User_Input_Movie': [option],
            'Recommended_Movies': [recommendations_movies],
            'Selected_Movies': [selected_movies_str]
        }

    df_to_save = pd.DataFrame(data)

    st.write(df_to_save)

    # Ajoutez les données à votre table MySQL
    df_to_save.to_sql('table_prediction', con=engine, if_exists='append', index=False)

    st.session_state.selected_movies = []
    st.session_state.recommendations_movies = []

    st.write("Preferences saved to database!")
else:
    st.write("You haven't selected any movies.")
