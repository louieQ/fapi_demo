import pickle
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

MODEL_FOLDER = Path("models/")
model_wrapper_list: list[dict] = []

class FlowerData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

app = FastAPI(
    title="IRIS classifier",
    description="A simple API that classifies IRIS flowers",
    version="0.1",
)

@app.on_event("startup")
def load_models():
    for model_path in MODEL_FOLDER.glob("*.pkl"):
        with open(model_path, "rb") as model_file:
            model_wrapper_list.append(pickle.load(model_file))

@app.get("/")
def root():
    return {"message": "Welcome to the IRIS classifier API!"}

@app.get("/models")
def get_models():
    model_list = [model["type"] for model in model_wrapper_list]
    return {"models": model_list}


@app.post("/models/{model_type}")
def predict(flower_data: FlowerData, model_type: str):
    for model_wrapper in model_wrapper_list:
        if model_wrapper["type"] == model_type:
            model = model_wrapper["model"]
            break
    else:
        return {
            "status-code": "400",
            "message": "Model not found."
            }

    prediction = model.predict([[flower_data.sepal_length, flower_data.sepal_width, flower_data.petal_length, flower_data.petal_width]])
    return {
        "status-code": "200",
        "prediction": int(prediction[0])
        }