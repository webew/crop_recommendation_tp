"""Relance toute la chaîne sur une base MLflow temporaire et affiche les résultats cités dans les supports.

Le serveur MLflow n'est pas utilisé : tout se passe dans un dossier temporaire.
Met aussi à jour assets/confusion_matrix.png.

    cd docs/support/build
    uv run --project ../../.. python collect_results.py
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)  # garder l'ordre des sorties avec les sous-commandes

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WORK = Path(tempfile.mkdtemp(prefix="support-mlops-"))
os.environ["MLFLOW_TRACKING_URI"] = f"sqlite:///{WORK / 'mlflow.db'}"
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
os.chdir(WORK)  # les artefacts (mlruns/) restent dans le dossier temporaire


def title(t):
    print(f"\n===== {t}")


def command(*args):
    """Lance une commande du projet et affiche sa sortie utile."""
    out = subprocess.run(["uv", "run", "--project", str(REPO), *args], capture_output=True, text=True)
    lines = [line for line in (out.stdout + out.stderr).splitlines() if not any(k in line for k in ("WARN", "INFO", "alembic", "warn"))]
    print("\n".join(lines))


title("promote sur une base vide")
command("promote")
title("train")
command("train")
title("promote (premier candidat)")
command("promote")
title("promote (relance)")
command("promote")
title("tune")
command("tune")

import mlflow  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from mlflow import MlflowClient  # noqa: E402

from crop_recommendation_tp import api, promote  # noqa: E402
from crop_recommendation_tp.config import load_config  # noqa: E402
from crop_recommendation_tp.data import load_dataset, split_dataset  # noqa: E402
from crop_recommendation_tp.tracking import log_run, setup_mlflow  # noqa: E402
from crop_recommendation_tp.train import cross_validate_model, evaluate, train_model  # noqa: E402

cfg = load_config()
setup_mlflow(cfg)
client = MlflowClient()
experiment = client.get_experiment_by_name(cfg["mlflow"]["experiment_name"])

title("données")
df = load_dataset(cfg)
print("forme", df.shape, "· cultures", df[cfg["dataset"]["target"]].nunique())
print(df.describe().round(1).T[["min", "mean", "max"]])

title("tune : les combinaisons (triées)")
children = client.search_runs([experiment.experiment_id], filter_string="tags.mlflow.parentRunId != ''")
for r in sorted(children, key=lambda r: -r.data.metrics["cv_f1_macro_mean"]):
    print(r.data.params["n_estimators"], r.data.params["max_depth"], round(r.data.metrics["cv_f1_macro_mean"], 4), round(r.data.metrics["cv_f1_macro_std"], 4))

title("run du candidat")
run = client.search_runs([experiment.experiment_id], filter_string="tags.stage = 'candidate'")[0]
print("tags", {k: v for k, v in run.data.tags.items() if not k.startswith("mlflow.")})
print("métriques", run.data.metrics)
mlflow.artifacts.download_artifacts(run_id=run.info.run_id, artifact_path="confusion_matrix.png", dst_path=str(WORK))
shutil.copy(WORK / "confusion_matrix.png", HERE / "assets" / "confusion_matrix.png")
print("matrice de confusion copiée dans assets/")

title("candidat volontairement faible (20 arbres, profondeur 3)")
weak = copy.deepcopy(cfg)
weak["model"]["params"] = {"n_estimators": 20, "max_depth": 3}
X_train, X_test, y_train, y_test = split_dataset(df, weak)
model = train_model(X_train, y_train, weak)
cv = cross_validate_model(X_train, y_train, weak)
predictions, test_metrics = evaluate(model, X_test, y_test)
log_run("train", weak, model, {**cv, **test_metrics}, predictions, X_test, y_test, tags={"stage": "candidate"})
print("scores", cv, test_metrics)
promote.main()

title("API")
mesures = [
    {"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9},
    {"N": 20, "P": 130, "K": 200, "temperature": 22.5, "humidity": 92.0, "ph": 6.0, "rainfall": 110.0},
]
with TestClient(api.app) as c:
    print("GET /health", c.get("/health").json())
    for m in mesures:
        print("POST /predict", json.dumps(m), "->", c.post("/predict", json=m).json())
    r = c.post("/predict", json={**mesures[0], "ph": 15})
    print("POST /predict ph=15 ->", r.status_code, json.dumps(r.json(), ensure_ascii=False))

title("tests et Ruff")
subprocess.run(["uv", "run", "pytest", "-q"], cwd=REPO)
subprocess.run(["uv", "run", "ruff", "check", "."], cwd=REPO)
subprocess.run(["uv", "run", "ruff", "format", "--check", "."], cwd=REPO)

print(f"\nDossier temporaire : {WORK}")
