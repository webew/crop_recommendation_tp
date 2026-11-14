from contextlib import asynccontextmanager

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from pydantic import Field, create_model

from crop_recommendation_tp.config import load_config, load_yaml
from crop_recommendation_tp.tracking import setup_mlflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    setup_mlflow(config)
    registry = config["mlflow"]
    name = registry["registered_model_name"]
    alias = registry["champion_alias"]
    try:
        version = MlflowClient().get_model_version_by_alias(name, alias)
    except MlflowException as erreur:
        raise RuntimeError(
            f"Alias {alias} introuvable pour {name} : vérifier que le serveur "
            "MLflow tourne, puis lancer uv run train et uv run promote."
        ) from erreur
    app.state.model = mlflow.pyfunc.load_model(f"models:/{name}/{version.version}")
    app.state.version = str(version.version)
    app.state.run_id = version.run_id
    yield


TYPES = {"int": int, "float": float}


def build_input_model(config):
    schema = load_yaml(config["dataset"]["schema"])
    target = config["dataset"]["target"]
    fields = {}
    for name, rules in schema["columns"].items():
        if name == target:
            continue
        fields[name] = (
            TYPES[rules["dtype"]],
            Field(ge=rules.get("min"), le=rules.get("max")),
        )
    return create_model("CropInput", **fields)


CropInput = build_input_model(load_config())

app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": app.state.version,
        "run_id": app.state.run_id,
    }


@app.post("/predict")
def predict(entree: CropInput):  # pyright: ignore[reportInvalidTypeForm]
    donnees = pd.DataFrame([entree.model_dump()]).astype("float64")
    prediction = app.state.model.predict(donnees)
    return {"culture": str(prediction[0]), "version": app.state.version}
