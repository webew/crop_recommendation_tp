import pandas as pd
import pytest

from crop_recommendation_tp.train import cross_validate_model
from crop_recommendation_tp.tune import tune


@pytest.fixture
def config():
    """Une seule combinaison dans la grille, identique aux paramètres du modèle."""
    return {
        "split": {"random_seed": 42},
        "model": {"params": {"n_estimators": 5, "max_depth": 2}},
        "tuning": {
            "cv_folds": 5,
            "scoring": "f1_macro",
            "param_grid": {"n_estimators": [5], "max_depth": [2]},
        },
    }


@pytest.fixture
def donnees():
    """40 lignes rangées par classe, comme le CSV (20 « rice » puis 20 « apple »)."""
    n = 20
    X = pd.DataFrame(
        {
            "a": list(range(n)) + list(range(10, 10 + n)),
            "b": [i % 7 for i in range(2 * n)],
        }
    )
    y = pd.Series(["rice"] * n + ["apple"] * n)
    return X, y


def test_train_et_tune_donnent_le_meme_score(config, donnees):
    X, y = donnees
    score_train = cross_validate_model(X, y, config)["cv_f1_macro_mean"]
    score_tune = tune(X, y, config).best_score_
    assert score_train == pytest.approx(score_tune)
