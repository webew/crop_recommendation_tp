import mlflow
import mlflow.sklearn
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.dummy import DummyClassifier

from crop_recommendation_tp import api
from crop_recommendation_tp.tracking import setup_mlflow

MESURES = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.8,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.9,
}


@pytest.fixture
def champion(config):
    """Enregistre un modèle minimal et lui attribue l'alias champion."""
    X = pd.DataFrame([MESURES, MESURES]).astype("float64")
    model = DummyClassifier(strategy="most_frequent").fit(X, ["rice", "rice"])
    setup_mlflow(config)
    name = config["mlflow"]["registered_model_name"]
    with mlflow.start_run():
        mlflow.sklearn.log_model(
            model,
            name="model",
            signature=infer_signature(X, model.predict(X)),
            registered_model_name=name,
        )
    MlflowClient().set_registered_model_alias(name, "champion", "1")


@pytest.fixture
def client(config, champion, monkeypatch):
    monkeypatch.setattr(api, "load_config", lambda: config)
    with TestClient(api.app) as client:
        yield client


def test_health(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.json()["status"] == "ok"
    assert reponse.json()["version"] == "1"


def test_predict(client):
    reponse = client.post("/predict", json=MESURES)
    assert reponse.status_code == 200
    assert reponse.json() == {"culture": "rice", "version": "1"}


def test_predict_valeur_hors_bornes(client):
    reponse = client.post("/predict", json={**MESURES, "ph": 15})
    assert reponse.status_code == 422


def test_predict_champ_manquant(client):
    mesures = {nom: valeur for nom, valeur in MESURES.items() if nom != "ph"}
    reponse = client.post("/predict", json=mesures)
    assert reponse.status_code == 422


def test_demarrage_sans_champion(config, monkeypatch):
    monkeypatch.setattr(api, "load_config", lambda: config)
    with pytest.raises(RuntimeError, match="uv run promote"), TestClient(api.app):
        pass
