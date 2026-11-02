# Recommandation de cultures : projet MLOps

Modèle de classification qui recommande une culture (22 classes) à partir de 7 variables : azote (N), phosphore (P), potassium (K), température, humidité, pH et pluviométrie.

Le projet suit une démarche MLOps : environnement reproductible, données versionnées et validées, configuration externalisée.

## Prérequis

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/) (gestionnaire d'environnement et de dépendances Python)

## Installation

```bash
git clone <url-du-dépôt>
cd crop_recommendation_tp
uv sync
uv run dvc pull
```

- `uv sync` crée l'environnement virtuel et installe les versions de bibliothèques enregistrées dans `uv.lock`.
- `uv run dvc pull` récupère le fichier de données depuis le stockage DVC.

Le stockage DVC configuré est un dossier local (`../dvc_storage`, à côté du dépôt). Sur un autre poste, ce dossier est à copier à cet emplacement, ou à remplacer par un stockage partagé.

## Structure

| Élément | Rôle |
|---|---|
| `config/config.yaml` | Paramètres du projet : chemins, colonne cible, découpage, graine aléatoire |
| `config/schema.yaml` | Schéma des données : colonnes, types, bornes, cultures autorisées |
| `data/raw/` | Données brutes, versionnées avec DVC (fichier `.dvc` dans Git) |
| `src/crop_recommendation_tp/` | Code du projet (validation des données) |

## Données

Le fichier `data/raw/crop_recommendation.csv` contient 2 200 lignes et 8 colonnes (7 variables et la culture `label`). Son empreinte est enregistrée dans `data/raw/crop_recommendation.csv.dvc`.

Validation des données avec le schéma :

```bash
uv run python -c "import pandas as pd, yaml; from crop_recommendation_tp.validation import validate; print(validate(pd.read_csv('data/raw/crop_recommendation.csv'), yaml.safe_load(open('config/schema.yaml'))))"
```

Résultat attendu : `[]` (liste d'erreurs vide).