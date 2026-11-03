from crop_recommendation_tp.config import load_config
from crop_recommendation_tp.data import load_dataset, split_dataset
from crop_recommendation_tp.tracking import log_run

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score


def train_model(X_train, y_train, config: dict) -> RandomForestClassifier:
    """Entraîne une forêt aléatoire avec les paramètres de config.yaml."""
    model = RandomForestClassifier(
        **config["model"]["params"],
        random_state=config["split"]["random_seed"],
    )
    return model.fit(X_train, y_train)


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
    predictions, metrics = evaluate(model, X_test, y_test)
    run_id = log_run("train", config, model, metrics, predictions, X_test, y_test)
    print(f"Run {run_id} enregistré : {metrics}")