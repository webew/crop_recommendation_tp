from crop_recommendation_tp.config import load_config
from crop_recommendation_tp.data import load_dataset, split_dataset
from crop_recommendation_tp.tracking import log_run, log_tuning
from crop_recommendation_tp.train import evaluate

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
    """Recherche d'hyperparamètres, puis évaluation et enregistrement du meilleur modèle."""
    config = load_config()
    X_train, X_test, y_train, y_test = split_dataset(load_dataset(config), config)
    search = tune(X_train, y_train, config)
    tuning_run_id = log_tuning(search, config)
    best_model = search.best_estimator_
    effective_config = {**config, "model": {"params": search.best_params_}}
    predictions, metrics = evaluate(best_model, X_test, y_test)
    run_id = log_run(
        "best_model",
        effective_config,
        best_model,
        metrics,
        predictions,
        X_test,
        y_test,
        tags={"tuning_run_id": tuning_run_id},
    )
    print(f"Meilleurs paramètres : {search.best_params_}")
    print(f"Run {run_id} enregistré : {metrics}")