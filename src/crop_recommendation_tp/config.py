from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str) -> dict:
    """Lit un fichier YAML dont le chemin est relatif à la racine du projet."""
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(path: str = "config/config.yaml") -> dict:
    """Retourne la configuration du projet."""
    return load_yaml(path)