import uvicorn
from fastapi import FastAPI
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import os
import json
from fastapi.responses import JSONResponse

app = FastAPI()

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
df = pd.read_sql_query("SELECT * FROM input_table", engine)

@app.post("/predict")
def get_recommendations(input_title):
    
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['genres'] + " " + df['actor_1_name'] + " " + df['director_name'] + " " + df['language'] + " " + df['country'])
    
    scaler = MinMaxScaler()
    numerical_features = scaler.fit_transform(df[['imdb_score', 'duration']])
    
    combined_features = pd.concat([pd.DataFrame(tfidf_matrix.toarray()), pd.DataFrame(numerical_features)], axis=1)
    
    cosine_sim = cosine_similarity(combined_features, combined_features)
    
    idx = df.index[df['movie_title'] == input_title].tolist()[0]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    sim_indices = [i[0] for i in sim_scores[1:6]]  
    
    output = df['movie_title'].iloc[sim_indices]
    
    response_data = output.tolist()
    
    return JSONResponse(content=response_data)

