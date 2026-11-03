# Recommandation de cultures : projet MLOps

Modèle de classification qui recommande une culture (22 classes) à partir de 7 variables : azote (N), phosphore (P), potassium (K), température, humidité, pH et pluviométrie.

Le projet suit une démarche MLOps : environnement reproductible, données versionnées et validées, expériences suivies avec MLflow, configuration externalisée.

## 1. Prérequis

| Outil | Rôle | Installation |
|---|---|---|
| [Git](https://git-scm.com/) | Historique du code | Voir le site |
| [uv](https://docs.astral.sh/uv/) | Environnement Python et dépendances | Voir le site |
| [VS Code](https://code.visualstudio.com/) | Éditeur et notebooks | Extensions *Python* et *Jupyter* |

La version de Python (3.13) est indiquée dans `.python-version` ; `uv` l'installe si elle est absente du poste.

## 2. Installation sur un nouveau poste

```bash
git clone <url-du-dépôt>
cd crop_recommendation_tp
uv sync
```

`uv sync` crée l'environnement virtuel `.venv` et installe les versions exactes de `uv.lock`.

Les données sont ensuite à récupérer (section 3).

## 3. Données

Le fichier `data/raw/crop_recommendation.csv` est versionné avec DVC : Git conserve son empreinte (`data/raw/crop_recommendation.csv.dvc`), et les données se trouvent dans le cache DVC et dans le remote.

Le remote configuré est un dossier local : `crop_recommendation_storage`, situé à côté du dépôt (chemin `../../crop_recommendation_storage` dans `.dvc/config`, relatif au dossier `.dvc/`). Ce dossier reste sur le poste où il a été créé ; sur un autre poste, deux méthodes permettent de récupérer les données.

### Méthode A : copier le dossier de stockage

1. Copier le dossier `crop_recommendation_storage` du poste d'origine, à côté du dépôt cloné.
2. Lancer :

```bash
uv run dvc pull
```

### Méthode B : replacer le fichier CSV

1. Copier le CSV d'origine dans `data/raw/` sous le nom `crop_recommendation.csv` (minuscules).
2. Vérifier l'empreinte et la taille :

```bash
uv run python -c "import hashlib; d = open('data/raw/crop_recommendation.csv','rb').read(); print(hashlib.md5(d).hexdigest(), len(d))"
```

Résultat attendu : `5e743dd4cf49f84d23a904cd51c9b5b8 150034`

3. Remplir le cache DVC :

```bash
uv run dvc add data/raw/crop_recommendation.csv
```

### Contrôle

```bash
uv run dvc status
```

Résultat attendu : `Data and pipelines are up to date.`

## 4. Validation des données

```bash
uv run python -c "import pandas as pd, yaml; from crop_recommendation_tp.validation import validate; print(validate(pd.read_csv('data/raw/crop_recommendation.csv'), yaml.safe_load(open('config/schema.yaml'))))"
```

Résultat attendu : `[]` (liste d'erreurs vide).

## 5. Notebook et suivi MLflow

1. Ouvrir `notebooks/01_exploration.ipynb` dans VS Code.
2. Sélectionner le noyau : *Sélectionner un noyau* → *Environnements Python* → l'environnement `.venv` du projet.
3. Lancer toutes les cellules (*Run All*).

Les runs sont enregistrés dans `mlflow.db` (base SQLite) et `mlruns/` (artefacts), à la racine du projet. Ces deux éléments ne sont pas versionnés : chaque poste possède ses propres runs.

Interface web de MLflow (dans un second terminal, à la racine du projet) :

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Adresse : `http://127.0.0.1:5000`

## 6. Entraîner un modèle

Workflow d'expérimentation :

1. **Rechercher les hyperparamètres** (occasionnel) : comparaison des combinaisons de `tuning.param_grid` par validation croisée.

   ```bash
   uv run tune
   ```

2. **Reporter** la meilleure combinaison affichée dans `model.params` de `config/config.yaml`, puis enregistrer la modification dans un commit.
3. **Entraîner le modèle candidat** : validation des données, entraînement, mesure sur le jeu de test, enregistrement d'un run MLflow.

   ```bash
   uv run train
   ```

La commande `train` se relance quand les données (fichier `.dvc`), les paramètres ou le code changent. Chaque run enregistre la version des données (`data_md5`) et celle du code (`git_commit`).

## 7. Structure du projet

| Élément | Rôle |
|---|---|
| `config/config.yaml` | Paramètres : chemins, colonne cible, découpage, graine aléatoire, MLflow |
| `config/schema.yaml` | Schéma des données : colonnes, types, bornes, cultures autorisées |
| `data/raw/` | Données brutes (fichier `.dvc` versionné dans Git) |
| `notebooks/` | Notebooks d'exploration et de suivi |
| `src/crop_recommendation_tp/` | Code du projet (validation des données) |
| `.dvc/` | Configuration de DVC et cache local |

## 8. Commandes utiles

| Commande | Effet |
|---|---|
| `uv sync` | Installer les dépendances de `uv.lock` |
| `uv add <paquet>` | Ajouter une dépendance |
| `uv run <commande>` | Exécuter une commande dans l'environnement du projet |
| `uv run dvc pull` | Récupérer les données depuis le remote |
| `uv run dvc status` | Comparer les données au fichier `.dvc` |
| `git status --short` | Lister les fichiers modifiés |

## 9. Résolution de problèmes

| Message | Cause | Solution |
|---|---|---|
| `FileNotFoundError: 'config/config.yaml'` dans le notebook | Le dossier courant du noyau n'est pas la racine du projet | Remplacer la première cellule par la version qui ne remonte d'un dossier qu'une fois (`if Path.cwd().name == "notebooks": os.chdir("..")`), redémarrer le noyau, puis relancer toutes les cellules |
| `Some of the cache files do not exist` ou `Checkout failed` lors de `dvc pull` | Le remote est absent sur ce poste | Méthode A ou B de la section 3 |
| Noyau introuvable dans VS Code | Environnement `.venv` non sélectionné | Lancer `uv sync`, puis sélectionner le noyau `.venv` |
| `UntrustedTypesFoundException` à l'enregistrement du modèle | MLflow enregistre les modèles scikit-learn au format skops, qui exige la liste des types autorisés | Passer `skops_trusted_types=["sklearn.tree._tree.Tree"]` à `mlflow.sklearn.log_model` |
| `LF will be replaced by CRLF` | Conversion des fins de ligne par Git sous Windows | Information sans conséquence |