import os
import base64
import requests
import pandas as pd
import streamlit as st
import streamlit_nested_layout
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


# # app
# st.set_page_config(
#     layout="wide"
# )


def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('walle.jpg')

st.markdown(f"<h1 style='color: white;'>What film de you like ?</h1>", unsafe_allow_html=True)
option = st.selectbox('', df)


st.markdown(f"<h6 style='color: white;'>You chose {option}</h6>", unsafe_allow_html=True)

st.markdown('#')

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

    else:
        st.write(f"Error - Status code: {response.status_code}")

st.markdown('#')

for idx, movie in enumerate(st.session_state.recommendations_movies, 1):
    checkbox_value = movie in st.session_state.selected_movies
    # checked = st.checkbox(f"{idx}. {movie}", value=checkbox_value)

    checkbox_label = f"<h6 style='color: white;'>{idx}. {movie}</h6>"

    col1, col2 = st.columns(2, gap="small")

    with col2:
        checked = st.checkbox(label="", key=idx)

    with col1:
        st.markdown(checkbox_label, unsafe_allow_html=True)

    if checked and movie not in st.session_state.selected_movies:
        st.session_state.selected_movies.append(movie)
    elif not checked and movie in st.session_state.selected_movies:
        st.session_state.selected_movies.remove(movie)

st.markdown('#')

st.markdown(f"<h6 style='color: white;'>You selected: {st.session_state.selected_movies}</h6>", unsafe_allow_html=True)

st.markdown('#')

if st.button("OK"):
    if st.session_state.selected_movies:
        selected_movies_str = ', '.join(st.session_state.selected_movies)
        st.markdown(f"<h6 style='color: white;'>You selected: {selected_movies_str}</h6>", unsafe_allow_html=True)
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

    st.markdown(f"<h6 style='color: white;'>Preferences saved to database!</h6>", unsafe_allow_html=True)
else:
    st.markdown(f"<h6 style='color: white;'>You haven't selected any movies.</h6>", unsafe_allow_html=True)
