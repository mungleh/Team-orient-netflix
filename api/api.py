import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.post("/predict")
def predict_recommendations(input):
    output = model.predict(input)
    return output
