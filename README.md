# Recommandation de cultures : projet MLOps

Modèle de classification qui recommande une culture (22 classes) à partir de 7 mesures du sol et du climat : azote (`N`), phosphore (`P`), potassium (`K`), température, humidité, pH et pluviométrie.

Le projet sert de support à un cours sur la démarche MLOps. Il montre comment un notebook devient une application :

- **environnement reproductible** : uv et `uv.lock` ;
- **données versionnées et validées** : DVC et un schéma ;
- **configuration externalisée** : `config/config.yaml` ;
- **expériences suivies** : serveur MLflow et base PostgreSQL ;
- **choix automatique du meilleur modèle** : registre MLflow et alias `champion` ;
- **modèle servi par une API** : FastAPI, dans un conteneur Docker ;
- **qualité vérifiée en continu** : pytest, Ruff, GitHub Actions.

Le guide du cours et les diapositives se trouvent dans [`docs/support/`](docs/support/) (voir la [section 13](#13-supports-de-cours)).

```text
Poste de travail                          Docker Compose
────────────────                          ─────────────────────────────────
uv run tune / train / promote  ───────►   mlflow (:5002)  ──►  postgres
données DVC, dépôt Git                       ▲
                                             │ http://mlflow:5000
navigateur, curl  ──────────────────────►   api (:8000)
```

## Sommaire

1. [Prérequis](#1-prérequis)
2. [Installation](#2-installation)
3. [Données](#3-données)
4. [Démarrer les services](#4-démarrer-les-services)
5. [Entraîner et promouvoir un modèle](#5-entraîner-et-promouvoir-un-modèle)
6. [API de prédiction](#6-api-de-prédiction)
7. [Notebook d'exploration](#7-notebook-dexploration)
8. [Tests et qualité du code](#8-tests-et-qualité-du-code)
9. [Intégration continue](#9-intégration-continue)
10. [Configuration](#10-configuration)
11. [Structure du projet](#11-structure-du-projet)
12. [Résolution de problèmes](#12-résolution-de-problèmes)
13. [Supports de cours](#13-supports-de-cours)

## 1. Prérequis

| Outil | Rôle |
| --- | --- |
| [Git](https://git-scm.com/) | Historique du code |
| [uv](https://docs.astral.sh/uv/) | Python, environnement virtuel et dépendances |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Serveur MLflow, base PostgreSQL et API |
| [VS Code](https://code.visualstudio.com/) | Éditeur, avec les extensions *Python*, *Jupyter* et *Ruff* |

La version de Python (3.13) est indiquée dans `.python-version` : uv l'installe si elle est absente du poste.

## 2. Installation

```bash
git clone <url-du-dépôt>
cd crop_recommendation_tp
uv sync
cp .env.example .env        # Windows (PowerShell) : Copy-Item .env.example .env
```

- `uv sync` crée l'environnement virtuel `.venv` et installe les versions exactes de `uv.lock`.
- Dans `.env`, renseigner `POSTGRES_PASSWORD` : PostgreSQL refuse de démarrer avec un mot de passe vide. Ce fichier contient des secrets : il est ignoré par Git.

Il reste ensuite à récupérer les données (section 3).

## 3. Données

Le fichier `data/raw/crop_recommendation.csv` (2 200 lignes, 100 par culture) est versionné avec DVC. Git conserve seulement son étiquette, `data/raw/crop_recommendation.csv.dvc`, qui contient son empreinte md5 et sa taille. Le contenu est rangé dans le cache DVC (`.dvc/cache/`) et dans le stockage distant.

Le stockage distant est un **dossier local**, `crop_recommendation_storage`, situé à côté du dépôt. Dans `.dvc/config`, son chemin est `../../crop_recommendation_storage`, relatif au dossier `.dvc/`. Ce dossier reste sur le poste où il a été créé. Sur un autre poste, deux méthodes permettent de récupérer les données.

### Méthode A : copier le dossier de stockage

1. Copier le dossier `crop_recommendation_storage` du poste d'origine, à côté du dépôt cloné.
2. Lancer :

   ```bash
   uv run dvc pull
   ```

### Méthode B : replacer le fichier CSV

1. Copier le CSV d'origine dans `data/raw/`, sous le nom `crop_recommendation.csv` (en minuscules).
2. Vérifier l'empreinte et la taille :

   ```bash
   uv run python -c "import hashlib; d = open('data/raw/crop_recommendation.csv','rb').read(); print(hashlib.md5(d).hexdigest(), len(d))"
   ```

   Résultat attendu : `5e743dd4cf49f84d23a904cd51c9b5b8 150034`

3. Remplir le cache DVC :

   ```bash
   uv run dvc add data/raw/crop_recommendation.csv
   ```

### Contrôles

```bash
uv run dvc status
```

Résultat attendu : `Data and pipelines are up to date.`

Les données sont aussi contrôlées par le schéma `config/schema.yaml` (colonnes, types, bornes, cultures autorisées). Les commandes `train` et `tune` le vérifient à chaque chargement et s'arrêtent, avec la liste des erreurs, si les données ne sont pas conformes. Pour lancer ce contrôle seul :

```bash
uv run python -c "import pandas as pd, yaml; from crop_recommendation_tp.validation import validate; print(validate(pd.read_csv('data/raw/crop_recommendation.csv'), yaml.safe_load(open('config/schema.yaml'))))"
```

Résultat attendu : `[]` (aucune erreur).

## 4. Démarrer les services

Docker Compose (`compose.yaml`) lance trois services :

| Service | Image | Rôle | Adresse sur le poste |
| --- | --- | --- | --- |
| `postgres` | `postgres:18` | Base de données de MLflow : paramètres, scores, registre | non publiée |
| `mlflow` | `Dockerfile.mlflow` | Serveur MLflow : suivi des runs, artefacts, registre | <http://localhost:5002> |
| `api` | `Dockerfile.api` | API de prédiction, qui sert le modèle `champion` | <http://localhost:8000/docs> |

```bash
docker compose up -d --build
docker compose ps            # les trois services doivent être « healthy »
```

- Les ports ne sont publiés que sur `127.0.0.1` : ils ne sont accessibles que depuis le poste. Les variables d'environnement `MLFLOW_PORT` et `API_PORT` permettent d'en choisir d'autres.
- L'API joint MLflow par son nom dans le réseau Docker (`http://mlflow:5000`). Depuis MLflow 3, le serveur n'accepte que les noms d'hôte autorisés : c'est le rôle de l'option `--allowed-hosts`.
- Les données de PostgreSQL et les artefacts de MLflow sont conservés dans les volumes Docker `postgres_data` et `mlflow_artifacts`.
- **Au premier démarrage, le registre est vide** : l'API s'arrête, avec un message qui demande de lancer `uv run train` puis `uv run promote`. C'est normal. On la relance après la promotion (section 5).

| Commande | Effet |
| --- | --- |
| `docker compose ps` | État des services |
| `docker compose logs --tail 20 api` | Dernières lignes du journal d'un service |
| `docker compose restart api` | Redémarrer l'API, par exemple pour charger un nouveau champion |
| `docker compose down` | Arrêter les services ; les données sont conservées |
| `docker compose down -v` | Arrêter les services **et supprimer** les runs, les modèles et le registre |

## 5. Entraîner et promouvoir un modèle

Les commandes `tune`, `train` et `promote` s'exécutent **sur le poste** : elles ont besoin des données DVC et du dépôt Git. Elles envoient leurs résultats au serveur MLflow (`tracking_uri` dans `config/config.yaml`).

```bash
uv run tune       # occasionnel : chercher les meilleurs hyperparamètres
uv run train      # entraîner un modèle candidat
uv run promote    # le comparer au champion, et le promouvoir s'il est meilleur
docker compose restart api   # servir le nouveau champion
```

### `tune` : chercher les hyperparamètres

`tune` compare toutes les combinaisons de `tuning.param_grid` par validation croisée sur le jeu d'entraînement (12 combinaisons × 5 plis). Il enregistre un run « tuning » avec un run enfant par combinaison, et affiche la meilleure.

On reporte ensuite cette combinaison dans `model.params` de `config/config.yaml`, puis on enregistre la modification dans un commit. `tune` n'enregistre aucun modèle et ne modifie pas la configuration : chercher et décider restent deux étapes distinctes.

### `train` : entraîner un candidat

`train` effectue les étapes suivantes :

1. charge les données et les valide avec le schéma ;
2. les découpe en entraînement (80 %) et test (20 %), de façon stratifiée, avec la graine `split.random_seed` ;
3. entraîne une forêt aléatoire avec `model.params` ;
4. mesure le score en validation croisée sur l'entraînement (`cv_f1_macro_mean` et `cv_f1_macro_std`) ;
5. mesure le modèle sur le jeu de test (`accuracy`, `f1_macro`) ;
6. enregistre un run étiqueté `stage=candidate`, avec les paramètres, les scores, le modèle et sa signature, la configuration, le schéma, le rapport de classification et la matrice de confusion.

Chaque run enregistre aussi la version des données (`data_md5`) et celle du code (`git_commit`). Le suffixe `-dirty` signale des modifications non commitées, et `-modified` des données différentes de l'étiquette `.dvc` : **commiter avant d'entraîner** un modèle que l'on veut garder.

Les plis de validation croisée sont fabriqués par une seule fonction, `build_cv` (dans `data.py`), utilisée par `train` et par `tune`. Pour les mêmes réglages, les deux commandes annoncent donc le même score. Le jeu de test, lui, ne sert jamais à choisir un modèle.

### `promote` : élire le champion

Le registre MLflow conserve les versions du modèle `crop-recommendation`. L'alias `champion` désigne la version servie par l'API.

`promote` compare le score de validation croisée (`cv_<tuning.scoring>_mean`) du **dernier** run candidat à celui du champion :

| Situation | Résultat |
| --- | --- |
| Aucun run candidat | Message : lancer d'abord `uv run train` |
| Le candidat n'a pas la métrique | Message, aucune promotion |
| Registre sans champion | Candidat promu |
| Candidat déjà champion | Aucune action |
| Score inférieur ou égal à celui du champion | Champion conservé |
| Score strictement supérieur, ou champion sans score | Nouvelle version, qui reçoit l'alias `champion` |

Dans l'interface MLflow (section *Models*), le modèle `crop-recommendation` affiche l'alias `champion` sur la version promue.

## 6. API de prédiction

Au démarrage, l'API demande au registre quelle version porte l'alias `champion` et charge ce modèle en mémoire. Une promotion n'est donc prise en compte qu'après un redémarrage : `docker compose restart api`.

| Route | Rôle |
| --- | --- |
| `GET /health` | État de l'API, version et run du modèle chargé |
| `POST /predict` | Culture recommandée pour 7 mesures |
| `GET /docs` | Documentation interactive, pour tester les routes depuis le navigateur |

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
     -d '{"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9}'
# → {"culture": "rice", "version": "1"}
```

Les entrées sont validées d'après `config/schema.yaml` : une valeur hors bornes, un type incorrect ou une variable absente renvoie une erreur **422** qui précise le champ concerné. Le modèle n'est jamais appelé avec des données invalides.

Pour développer l'API sans reconstruire l'image, la lancer sur le poste (le serveur MLflow doit tourner) :

```bash
docker compose stop api      # libérer le port 8000
uv run fastapi dev           # rechargement automatique à chaque modification
```

`fastapi dev` trouve l'application grâce à `[tool.fastapi]` dans `pyproject.toml`.

## 7. Notebook d'exploration

`notebooks/01_exploration.ipynb` est le point de départ du projet : exploration des données et premiers essais de modèles, suivis dans MLflow. Ce n'est pas la version de référence : le code utile a été déplacé dans `src/crop_recommendation_tp/`, où il est réutilisable et testé.

1. Démarrer les services (section 4) : le notebook envoie ses runs au serveur MLflow.
2. Ouvrir le notebook dans VS Code.
3. Choisir le noyau : *Sélectionner un noyau* → *Environnements Python* → `.venv` du projet.
4. Lancer toutes les cellules (*Run All*).

## 8. Tests et qualité du code

```bash
uv run pytest                 # 30 tests
uv run ruff check .           # erreurs probables, ordre des imports
uv run ruff format --check .  # mise en forme
```

| Fichier | Tests | Ce qui est vérifié |
| --- | --- | --- |
| `tests/test_validation.py` | 9 | Règles du schéma : colonnes, types, valeurs manquantes, bornes, cultures autorisées |
| `tests/test_data.py` | 4 | Variables explicatives, découpage stratifié et reproductible, plis de validation croisée |
| `tests/test_train.py` | 1 | `train` et `tune` donnent le même score pour les mêmes réglages |
| `tests/test_promote.py` | 11 | Règle de promotion, dans tous les cas du tableau de la section 5 |
| `tests/test_api.py` | 5 | Routes `/health` et `/predict`, erreurs 422, démarrage sans champion |

Les tests utilisent de petits tableaux fabriqués et une base MLflow SQLite temporaire (fixture `config` de `tests/conftest.py`). Ils s'exécutent sans les données, sans Docker et sans serveur MLflow.

`uv run ruff check . --fix` et `uv run ruff format .` corrigent automatiquement la plupart des écarts. Dans VS Code, avec l'extension Ruff, `.vscode/settings.json` trie les imports, applique les corrections et met en forme le code à chaque enregistrement.

## 9. Intégration continue

Le workflow `.github/workflows/ci.yml` s'exécute à chaque `push` et `pull_request`, sur une machine neuve. Il installe l'environnement (`uv sync --locked`), puis lance :

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

`uv sync --locked` échoue si `uv.lock` ne correspond pas à `pyproject.toml`. Avant chaque commit, lancer les trois mêmes commandes en local.

Les numéros de version des actions (`actions/checkout`, `astral-sh/setup-uv`) se vérifient sur la page GitHub de chaque action.

## 10. Configuration

### `config/config.yaml`

| Clé | Rôle |
| --- | --- |
| `dataset.path`, `dataset.schema`, `dataset.target` | Fichier de données, schéma, colonne cible (`label`) |
| `split.test_size`, `split.random_seed` | Part du jeu de test (0,2) et graine aléatoire (42), utilisée partout |
| `mlflow.tracking_uri` | Adresse du serveur MLflow (`http://localhost:5002`) |
| `mlflow.experiment_name` | Expérience qui regroupe les runs |
| `mlflow.registered_model_name`, `mlflow.champion_alias` | Nom du modèle dans le registre et nom de l'alias |
| `model.params` | Hyperparamètres utilisés par `train` |
| `tuning.cv_folds`, `tuning.scoring` | Nombre de plis et mesure de score (`f1_macro`) de la validation croisée |
| `tuning.param_grid` | Combinaisons essayées par `tune` |

### Variables d'environnement

| Variable | Rôle |
| --- | --- |
| `MLFLOW_TRACKING_URI` | Remplace `mlflow.tracking_uri` (utilisée par l'API dans Docker et par les tests) |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Identifiants de la base, lus dans `.env` |
| `MLFLOW_PORT`, `API_PORT` | Ports publiés sur le poste (5002 et 8000 par défaut) |

## 11. Structure du projet

| Élément | Rôle |
| --- | --- |
| `pyproject.toml`, `uv.lock`, `.python-version` | Dépendances, commandes (`train`, `tune`, `promote`), réglages de Ruff et de FastAPI |
| `config/config.yaml` | Réglages du projet (section 10) |
| `config/schema.yaml` | Schéma des données : colonnes, types, bornes, cultures autorisées |
| `data/raw/` | Données brutes ; seul le fichier `.dvc` est versionné par Git |
| `notebooks/` | Notebook d'exploration |
| `src/crop_recommendation_tp/config.py` | Lecture des fichiers YAML, racine du projet (`ROOT`) |
| `src/crop_recommendation_tp/validation.py` | Contrôle d'un tableau par rapport au schéma |
| `src/crop_recommendation_tp/data.py` | Chargement et validation, découpage, plis de validation croisée, empreinte des données |
| `src/crop_recommendation_tp/tracking.py` | Connexion à MLflow, enregistrement des runs |
| `src/crop_recommendation_tp/train.py` | Commande `train` |
| `src/crop_recommendation_tp/tune.py` | Commande `tune` |
| `src/crop_recommendation_tp/promote.py` | Commande `promote` |
| `src/crop_recommendation_tp/api.py` | API de prédiction |
| `tests/` | Tests automatisés (section 8) |
| `compose.yaml`, `.env.example` | Services Docker et modèle du fichier des secrets |
| `Dockerfile.mlflow`, `Dockerfile.api`, `.dockerignore` | Images du serveur MLflow et de l'API ; fichiers exclus des images |
| `.dvc/` | Configuration de DVC, dont l'adresse du stockage |
| `.github/workflows/ci.yml` | Intégration continue |
| `.vscode/settings.json` | Ruff à l'enregistrement |
| `docs/support/` | Supports de cours et leurs générateurs (section 13) |

## 12. Résolution de problèmes

| Message ou symptôme | Cause | Solution |
| --- | --- | --- |
| `env file … .env not found`, `The "POSTGRES_USER" variable is not set` | Fichier des secrets absent | `cp .env.example .env`, puis renseigner `POSTGRES_PASSWORD` |
| `Bind for 127.0.0.1:5002 failed: port is already allocated` | Un autre projet utilise déjà le port | Arrêter l'autre projet (`docker compose -p <projet> stop`), ou choisir un autre port : `MLFLOW_PORT=5003 docker compose up -d` |
| Le service `api` s'arrête au démarrage : `Alias champion introuvable…` | Registre sans champion, ou serveur MLflow indisponible | `uv run train`, `uv run promote`, puis `docker compose restart api` |
| `403` et `Invalid Host header - possible DNS rebinding attack detected` | Nom d'hôte non autorisé par le serveur MLflow | Ajouter ce nom à `--allowed-hosts` dans `compose.yaml` |
| `Données non conformes au schéma` | Le CSV ne respecte pas `config/schema.yaml` | Lire la liste des erreurs ; corriger les données ou le schéma |
| `Some of the cache files do not exist` ou `Checkout failed` lors de `dvc pull` | Stockage DVC absent sur ce poste | Méthode A ou B de la section 3 |
| `FileNotFoundError: 'config/config.yaml'` dans le notebook | Le noyau ne tourne pas depuis la racine du projet | Vérifier la première cellule (`os.chdir("..")` si l'on est dans `notebooks/`), redémarrer le noyau, relancer toutes les cellules |
| Noyau introuvable dans VS Code | Environnement `.venv` non sélectionné | `uv sync`, puis sélectionner le noyau `.venv` |
| `UntrustedTypesFoundException` à l'enregistrement d'un modèle | MLflow enregistre les modèles scikit-learn au format skops, qui exige la liste des types autorisés | Passer `skops_trusted_types=["sklearn.tree._tree.Tree"]` à `mlflow.sklearn.log_model` |
| `LF will be replaced by CRLF` | Conversion des fins de ligne par Git sous Windows | Information sans conséquence |

## 13. Supports de cours

| Fichier | Contenu |
| --- | --- |
| `docs/support/guide_mlops_phase1.pdf` | Guide de l'étudiant : reconstruction pas à pas de l'application, choix justifiés, plan de test, exercices, glossaire |
| `docs/support/seance1_demarche_mlops.pptx` | Ouverture de la séance 1 : la chaîne MLOps (local, GitHub, production) et le cycle de vie du modèle |
| `docs/support/cours_mlops_phase1.pptx` | Diapositives de la phase 1, avec les notes du formateur |
| `docs/support/script_formateur.md` | Script formateur : déroulé de chaque étape du dépôt de cours `crop_recommendation_cours` |

Ces fichiers sont générés par les scripts de `docs/support/build/`. Ce dossier a son propre [README](docs/support/build/README.md), qui explique comment les régénérer après une modification du code.
