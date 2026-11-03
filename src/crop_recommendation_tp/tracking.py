import matplotlib
import mlflow

from crop_recommendation_tp.config import ROOT, load_yaml
from crop_recommendation_tp.data import get_data_version

matplotlib.use("Agg")  # rendu sans fenêtre, utilisable dans un script ou en CI
import subprocess

import matplotlib.pyplot as plt
from mlflow.models import infer_signature
from sklearn.metrics import ConfusionMatrixDisplay, classification_report


def setup_mlflow(config: dict) -> None:
    """Connecte MLflow à la base et à l'expérience déclarées dans config.yaml."""
    uri = config["mlflow"]["tracking_uri"]
    if uri.startswith("sqlite:///"):
        # chemin de la base calculé depuis la racine du projet
        uri = "sqlite:///" + (ROOT / uri.removeprefix("sqlite:///")).as_posix()
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])


def get_git_commit() -> str:
    """Retourne le commit courant, suffixé par -dirty si des modifications ne sont pas enregistrées."""

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    try:
        return git("rev-parse", "HEAD") + (
            "-dirty" if git("status", "--porcelain") else ""
        )
    except (OSError, subprocess.CalledProcessError):
        return "inconnu"


def log_run(
    run_name: str,
    config: dict,
    model,
    metrics: dict,
    predictions,
    X_test,
    y_test,
    tags: dict | None = None,
) -> str:
    """Enregistre un run (paramètres, métriques, modèle) et retourne son identifiant."""
    setup_mlflow(config)
    params = {**model.get_params(), "test_size": config["split"]["test_size"]}
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.set_tags({**trace_tags(config), **(tags or {})})
        mlflow.log_dict(config, "config.yaml")
        mlflow.log_dict(load_yaml(config["dataset"]["schema"]), "schema.yaml")
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            signature=infer_signature(X_test.astype("float64"), predictions),
            input_example=X_test.head().astype("float64"),
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )
        mlflow.log_text(
            classification_report(y_test, predictions), "classification_report.txt"
        )
        fig, ax = plt.subplots(figsize=(10, 10))
        ConfusionMatrixDisplay.from_predictions(
            y_test, predictions, xticks_rotation=90, colorbar=False, cmap="Blues", ax=ax
        )
        mlflow.log_figure(fig, "confusion_matrix.png")
        plt.close(fig)
    return run.info.run_id


def trace_tags(config: dict) -> dict:
    """Étiquettes qui relient un run à la version des données et au commit du code."""
    return {"data_md5": get_data_version(config), "git_commit": get_git_commit()}


def log_tuning(search, config: dict) -> str:
    """Enregistre une recherche : un run parent et un run enfant par combinaison."""
    setup_mlflow(config)
    tuning = config["tuning"]
    metric = f"cv_{tuning['scoring']}"
    results = search.cv_results_
    with mlflow.start_run(run_name="tuning") as parent:
        mlflow.set_tags(trace_tags(config))
        mlflow.log_params(
            {"cv_folds": tuning["cv_folds"], "scoring": tuning["scoring"]}
        )
        for i, params in enumerate(results["params"]):
            with mlflow.start_run(run_name=f"cv_{i}", nested=True):
                mlflow.log_params(params)
                mlflow.log_metrics(
                    {
                        f"{metric}_mean": results["mean_test_score"][i],
                        f"{metric}_std": results["std_test_score"][i],
                    }
                )
        mlflow.log_params({f"best_{k}": v for k, v in search.best_params_.items()})
        mlflow.log_metric(f"best_{metric}_mean", search.best_score_)
    return parent.info.run_id
