import pandas as pd
import pytest

from crop_recommendation_tp.data import build_cv, get_features, split_dataset


@pytest.fixture
def config():
    return {
        "dataset": {"schema": "config/schema.yaml", "target": "label"},
        "split": {"test_size": 0.2, "random_seed": 42},
        "tuning": {"cv_folds": 5},
    }


@pytest.fixture
def df():
    """20 lignes, 2 cultures de 10 lignes chacune."""
    n = 20
    return pd.DataFrame(
        {
            "N": range(n),
            "P": range(n),
            "K": range(n),
            "temperature": [20.0] * n,
            "humidity": [60.0] * n,
            "ph": [6.5] * n,
            "rainfall": [100.0] * n,
            "label": ["rice", "apple"] * (n // 2),
        }
    )


def test_variables_sans_la_cible(config):
    attendues = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    assert get_features(config) == attendues


def test_decoupage_taille_et_stratification(df, config):
    X_train, X_test, _y_train, y_test = split_dataset(df, config)
    assert len(X_train) == 16
    assert len(X_test) == 4
    assert y_test.value_counts().to_dict() == {"rice": 2, "apple": 2}


def test_decoupage_reproductible(df, config):
    premier = split_dataset(df, config)
    second = split_dataset(df, config)
    assert premier[0].index.equals(second[0].index)


def test_plis_reproductibles_et_melanges(config):
    X = pd.DataFrame({"a": range(40)})
    y = pd.Series(["rice"] * 20 + ["apple"] * 20)  # rangé par culture, comme le CSV
    premiers = [test.tolist() for _, test in build_cv(config).split(X, y)]
    seconds = [test.tolist() for _, test in build_cv(config).split(X, y)]
    assert len(premiers) == 5
    assert premiers == seconds
    # sans mélange, le premier pli prendrait les 4 premières lignes de chaque culture
    assert premiers[0] != [0, 1, 2, 3, 20, 21, 22, 23]
