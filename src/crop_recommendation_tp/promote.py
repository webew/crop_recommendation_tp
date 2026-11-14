import mlflow
from mlflow import MlflowClient
from mlflow.entities.model_registry import ModelVersion
from mlflow.exceptions import MlflowException

from crop_recommendation_tp.config import load_config
from crop_recommendation_tp.tracking import setup_mlflow


def get_champion(client: MlflowClient, config: dict) -> ModelVersion | None:
    """Retourne la version qui porte l'alias champion, ou None s'il n'y en a pas."""
    registry = config["mlflow"]
    try:
        return client.get_model_version_by_alias(
            registry["registered_model_name"], registry["champion_alias"]
        )
    except MlflowException:
        return None


def get_run_score(client: MlflowClient, run_id: str, metric: str) -> float | None:
    """Retourne la valeur d'une métrique d'un run, ou None si le run ne l'a pas enregistrée."""
    return client.get_run(run_id).data.metrics.get(metric)


def promote_candidate(client: MlflowClient, config: dict, run_id: str) -> ModelVersion:
    """Enregistre le modèle d'un run comme nouvelle version et lui attribue l'alias champion."""
    registry = config["mlflow"]
    name = registry["registered_model_name"]
    version = mlflow.register_model(f"runs:/{run_id}/model", name)
    client.set_registered_model_alias(name, registry["champion_alias"], version.version)
    return version


def find_candidate_run_id(client: MlflowClient, config: dict) -> str | None:
    """Retourne l'identifiant du run candidat le plus récent, ou None s'il n'y en a pas."""
    experiment = client.get_experiment_by_name(config["mlflow"]["experiment_name"])
    if experiment is None:
        return None
    for run in client.search_runs([experiment.experiment_id]):
        if run.data.tags.get("stage") == "candidate":
            return run.info.run_id
    return None


def main() -> None:
    """Compare le dernier run candidat au champion et promeut le meilleur."""
    config = load_config()
    setup_mlflow(config)
    client = MlflowClient()
    metric = f"cv_{config['tuning']['scoring']}_mean"

    run_id = find_candidate_run_id(client, config)
    if run_id is None:
        print("Aucun run candidat : lancer d'abord uv run train.")
        return
    candidate_score = get_run_score(client, run_id, metric)
    if candidate_score is None:
        print(f"Le run candidat n'a pas la métrique {metric}.")
        return

    champion = get_champion(client, config)
    if champion is not None:
        if champion.run_id == run_id:
            print(f"Le candidat est déjà le champion (version {champion.version}).")
            return
        champion_score = get_run_score(client, champion.run_id, metric)
        if champion_score is not None and candidate_score <= champion_score:
            print(
                f"Candidat non promu : {candidate_score:.4f} <= {champion_score:.4f}."
            )
            return
    version = promote_candidate(client, config, run_id)
    print(f"Version {version.version} promue champion (score {candidate_score:.4f}).")
