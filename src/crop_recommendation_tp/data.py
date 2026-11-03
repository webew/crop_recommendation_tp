import hashlib

import pandas as pd
from sklearn.model_selection import train_test_split

from crop_recommendation_tp.config import ROOT, load_yaml
from crop_recommendation_tp.validation import validate


def load_dataset(config: dict) -> pd.DataFrame:
    """Lit le CSV, le valide avec le schéma et retourne le tableau."""
    df = pd.read_csv(ROOT / config["dataset"]["path"])
    schema = load_yaml(config["dataset"]["schema"])
    errors = validate(df, schema)
    if errors:
        raise ValueError("Données non conformes au schéma :\n" + "\n".join(errors))
    return df


def get_features(config: dict) -> list[str]:
    """Retourne les variables explicatives : colonnes du schéma, cible exclue."""
    schema = load_yaml(config["dataset"]["schema"])
    return [c for c in schema["columns"] if c != config["dataset"]["target"]]


def split_dataset(df: pd.DataFrame, config: dict):
    """Découpe en jeux d'entraînement et de test (X_train, X_test, y_train, y_test)."""
    y = df[config["dataset"]["target"]]
    return train_test_split(
        df[get_features(config)],
        y,
        test_size=config["split"]["test_size"],
        random_state=config["split"]["random_seed"],
        stratify=y,
    )


def get_data_version(config: dict) -> str:
    """Retourne l'empreinte md5 du fichier de données utilisé.

    Le suffixe -modified signale un fichier différent de celui enregistré dans le .dvc.
    """
    dvc_file = load_yaml(config["dataset"]["path"] + ".dvc")
    expected = dvc_file["outs"][0]["md5"]
    actual = hashlib.md5((ROOT / config["dataset"]["path"]).read_bytes()).hexdigest()
    return actual if actual == expected else actual + "-modified"
