from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import cross_val_score

from crop_recommendation_tp.config import load_config
from crop_recommendation_tp.data import load_dataset, split_dataset
from crop_recommendation_tp.tracking import log_run


def build_model(config: dict) -> RandomForestClassifier:
    """Crée une forêt aléatoire non entraînée avec les paramètres de config.yaml."""
    return RandomForestClassifier(
        **config["model"]["params"],
        random_state=config["split"]["random_seed"],
    )


def train_model(X_train, y_train, config: dict) -> RandomForestClassifier:
    """Entraîne une forêt aléatoire avec les paramètres de config.yaml."""
    return build_model(config).fit(X_train, y_train)


def cross_validate_model(X_train, y_train, config: dict) -> dict:
    """Mesure le score en validation croisée sur le jeu d'entraînement."""
    tuning = config["tuning"]
    scores = cross_val_score(
        build_model(config),
        X_train,
        y_train,
        scoring=tuning["scoring"],
        cv=tuning["cv_folds"],
    )
    metric = f"cv_{tuning['scoring']}"
    return {
        f"{metric}_mean": float(scores.mean()),
        f"{metric}_std": float(scores.std()),
    }


def evaluate(model, X_test, y_test):
    """Retourne les prédictions et les métriques sur le jeu de test."""
    predictions = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "f1_macro": f1_score(y_test, predictions, average="macro"),
    }
    return predictions, metrics


def main() -> None:
    """Charge, valide et découpe les données, entraîne, évalue et enregistre un run."""
    config = load_config()
    X_train, X_test, y_train, y_test = split_dataset(load_dataset(config), config)
    model = train_model(X_train, y_train, config)
    cv_metrics = cross_validate_model(X_train, y_train, config)
    predictions, test_metrics = evaluate(model, X_test, y_test)
    metrics = {**cv_metrics, **test_metrics}
    run_id = log_run("train", config, model, metrics, predictions, X_test, y_test)
    print(f"Run {run_id} enregistré : {metrics}")
