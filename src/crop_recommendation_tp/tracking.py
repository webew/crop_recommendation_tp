import mlflow

from crop_recommendation_tp.config import ROOT
import matplotlib

matplotlib.use("Agg")  # rendu sans fenêtre, utilisable dans un script ou en CI
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, classification_report

def setup_mlflow(config: dict) -> None:
    """Connecte MLflow à la base et à l'expérience déclarées dans config.yaml."""
    uri = config["mlflow"]["tracking_uri"]
    if uri.startswith("sqlite:///"):
        # chemin de la base calculé depuis la racine du projet
        uri = "sqlite:///" + (ROOT / uri.removeprefix("sqlite:///")).as_posix()
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])


def log_run(run_name: str, config: dict, model, metrics: dict, predictions, y_test) -> str:
    """Enregistre un run (paramètres, métriques, modèle) et retourne son identifiant."""
    setup_mlflow(config)
    params = {**config["model"]["params"], "random_state": config["split"]["random_seed"]}
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
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