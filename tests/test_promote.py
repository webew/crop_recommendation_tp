import mlflow
import pytest
from mlflow import MlflowClient
from sklearn.dummy import DummyClassifier

from crop_recommendation_tp.promote import (
    find_candidate_run_id,
    get_champion,
    promote_candidate,
)
from crop_recommendation_tp.promote import main as promote_main
from crop_recommendation_tp.tracking import setup_mlflow


def log_candidate(config, score):
    """Enregistre un run candidat avec un modèle minimal et retourne son run_id."""
    setup_mlflow(config)
    model = DummyClassifier().fit([[0], [1]], [0, 1])
    with mlflow.start_run() as run:
        mlflow.set_tag("stage", "candidate")
        if score is not None:
            mlflow.log_metric("cv_f1_macro_mean", score)
        mlflow.sklearn.log_model(model, name="model")
    return run.info.run_id


def test_find_candidate_without_experiment(config):
    assert find_candidate_run_id(MlflowClient(), config) is None


def test_find_candidate_returns_latest(config):
    log_candidate(config, 0.90)
    latest = log_candidate(config, 0.95)
    assert find_candidate_run_id(MlflowClient(), config) == latest


def test_get_champion_without_alias(config):
    setup_mlflow(config)
    assert get_champion(MlflowClient(), config) is None


def test_promote_candidate_sets_champion(config):
    run_id = log_candidate(config, 0.95)
    client = MlflowClient()
    version = promote_candidate(client, config, run_id)
    champion = get_champion(client, config)
    assert champion.version == version.version
    assert champion.run_id == run_id


@pytest.fixture
def run_promote(config, monkeypatch, capsys):
    """Exécute promote.main avec la configuration de test et retourne son affichage."""
    monkeypatch.setattr("crop_recommendation_tp.promote.load_config", lambda: config)

    def run():
        promote_main()
        return capsys.readouterr().out

    return run


def test_main_without_candidate(run_promote):
    assert "Aucun run candidat" in run_promote()


def test_main_promotes_first_candidate(config, run_promote):
    run_id = log_candidate(config, 0.90)
    assert "promue champion" in run_promote()
    assert get_champion(MlflowClient(), config).run_id == run_id


def test_main_keeps_better_champion(config, run_promote):
    champion_id = log_candidate(config, 0.95)
    run_promote()
    log_candidate(config, 0.90)
    assert "non promu" in run_promote()
    assert get_champion(MlflowClient(), config).run_id == champion_id


def test_main_promotes_better_candidate(config, run_promote):
    log_candidate(config, 0.90)
    run_promote()
    better_id = log_candidate(config, 0.95)
    assert "promue champion" in run_promote()
    assert get_champion(MlflowClient(), config).run_id == better_id


def test_main_detects_candidate_already_champion(config, run_promote):
    log_candidate(config, 0.90)
    run_promote()
    assert "déjà le champion" in run_promote()


def test_main_rejects_candidate_without_metric(config, run_promote):
    log_candidate(config, None)
    assert "n'a pas la métrique" in run_promote()
    assert get_champion(MlflowClient(), config) is None


def test_main_replaces_champion_without_metric(config, run_promote):
    old_id = log_candidate(config, None)
    promote_candidate(MlflowClient(), config, old_id)
    new_id = log_candidate(config, 0.90)
    assert "promue champion" in run_promote()
    assert get_champion(MlflowClient(), config).run_id == new_id
