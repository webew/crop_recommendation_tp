import mlflow
import pytest


@pytest.fixture
def config(tmp_path, monkeypatch):
    """Configuration qui pointe vers une base SQLite temporaire."""
    monkeypatch.chdir(tmp_path)
    db = (tmp_path / "mlflow.db").as_posix()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{db}")
    mlflow.set_tracking_uri(f"sqlite:///{db}")
    yield {
        "mlflow": {
            "tracking_uri": "inutilisé : MLFLOW_TRACKING_URI est prioritaire",
            "experiment_name": "test-experiment",
            "registered_model_name": "test-model",
            "champion_alias": "champion",
        },
        "tuning": {"scoring": "f1_macro"},
    }
    mlflow.set_tracking_uri(None)
