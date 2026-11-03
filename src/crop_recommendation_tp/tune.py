from crop_recommendation_tp.config import load_config
from crop_recommendation_tp.data import load_dataset, split_dataset
from crop_recommendation_tp.tracking import log_tuning

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold


def tune(X_train, y_train, config: dict) -> GridSearchCV:
    """Évalue chaque combinaison de la grille par validation croisée sur le jeu d'entraînement."""
    seed = config["split"]["random_seed"]
    tuning = config["tuning"]
    search = GridSearchCV(
        RandomForestClassifier(random_state=seed),
        param_grid=tuning["param_grid"],
        scoring=tuning["scoring"],
        cv=StratifiedKFold(n_splits=tuning["cv_folds"], shuffle=True, random_state=seed),
        n_jobs=-1,
    )
    return search.fit(X_train, y_train)

def main() -> None:
    """Recherche d'hyperparamètres : enregistre les runs et affiche la meilleure combinaison."""
    config = load_config()
    X_train, _, y_train, _ = split_dataset(load_dataset(config), config)
    search = tune(X_train, y_train, config)
    run_id = log_tuning(search, config)
    print(f"Run {run_id} enregistré")
    print(f"Meilleurs paramètres : {search.best_params_}")
    print("Reporter ces paramètres dans model.params de config/config.yaml, puis lancer : uv run train")