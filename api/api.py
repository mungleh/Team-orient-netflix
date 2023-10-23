import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.post("/predict")
def predict_recommendations(input):
    output = input
    return output
