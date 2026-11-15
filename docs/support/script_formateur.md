# Script formateur : phases 1 et 2

Déroulé détaillé des phases 1 et 2, étape par étape. Chaque étape correspond à un commit et à une étiquette Git du dépôt de cours [`crop_recommendation_cours`](https://github.com/webew/crop_recommendation_cours).

Pour chaque étape : objectif, passage à l'étape, fichiers concernés, explication du code, démonstration, vérification, transition.

## Sommaire

| Étape | Étiquette | Notion | Durée indicative |
| --- | --- | --- | --- |
| Préparation | — | postes, dépôt, MLflow | avant la séance |
| 0 | `etape-0` | point de départ : projet uv, configuration, notebook, MLflow | 40 min |
| 1 | `etape-1` | validation des données | 20 min |
| 2 | `etape-2` | versionnage des données (DVC) | 30 min |
| 3 | `etape-3` | du notebook au paquet : `data.py` | 20 min |
| 4 | `etape-4` | tests et qualité du code | 30 min |
| 5 | `etape-5` | entraînement en script : `tune`, `train` | 40 min |
| 6 | `etape-6` | intégration continue | 15 min |
| Fin de phase 1 | | traçabilité d'un run d'entraînement | 15 min |
| 7 | `etape-7` | serveur MLflow : Docker Compose, PostgreSQL | 30 min |
| 8 | `etape-8` | registre et promotion | 30 min |
| 9 | `etape-9` | API de prédiction | 30 min |
| 10 | `etape-10` | API en conteneur | 30 min |
| Fin de phase 2 | | traçabilité d'une prédiction | 15 min |

---

## Préparation

### Avant la séance

**Poste du formateur**

```bash
git clone <url-du-dépôt-de-cours> crop_recommendation_cours
cd crop_recommendation_cours
git checkout -f etape-0
uv sync
```

- Vérifier que les ports 5001 (MLflow) et 8000 (API) sont libres (`lsof -i :5001` sur macOS) : sinon, adapter le port dans la commande MLflow et dans `config/config.yaml`.
- Supprimer les essais d'une séance précédente : `rm -f mlflow.db && rm -rf mlartifacts` (phase 1), `docker compose down -v` (phase 2).
- Ouvrir VS Code sur le dossier, avec les extensions *Python*, *Jupyter* et *Ruff*.
- **Phase 2** : construire les images à l'avance sur le poste du formateur (`git checkout -f etape-10`, `cp .env.example .env`, mot de passe, `docker compose build`). La construction de l'image de l'API prend plusieurs minutes et l'image pèse environ 2,6 Go.

**Postes des étudiants**

- Git, uv et VS Code installés ; Docker Desktop pour la phase 2.
- Adresse du dépôt de cours communiquée : <https://github.com/webew/crop_recommendation_cours>.

### Changer d'étape

Commandes identiques à chaque étape, à afficher en début de séance :

```bash
git checkout -f etape-N      # -f : abandonne les modifications locales des fichiers suivis
uv sync                      # dépendances de l'étape
uv run dvc pull              # à partir de l'étape 2 : restaure les données
```

- `-f` évite les conflits si un étudiant a modifié des fichiers en suivant la démonstration. Ses modifications sont perdues : le prévenir.
- Les essais MLflow ne sont pas suivis par Git : ils sont conservés d'une étape à l'autre. Le serveur peut rester démarré.
- Après `git checkout`, recharger le notebook dans VS Code si son contenu a changé, puis redémarrer le noyau.
- Pour montrer ce qui a changé entre deux étapes : `git diff etape-0 etape-1 --stat`, puis `git diff etape-0 etape-1 -- <fichier>`.

---

## Étape 0 : point de départ

### Objectif

Partir d'une démarche de modélisation complète et correcte, réalisée dans un notebook, avec les essais enregistrés dans MLflow. La suite du cours industrialise cette démarche.

### Mise en place

```bash
git clone <url-du-dépôt-de-cours> crop_recommendation_cours
cd crop_recommendation_cours
uv sync
```

Dans un second terminal, laissé ouvert :

```bash
uv run mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5001
```

Interface : <http://127.0.0.1:5001>.

### Fichiers à présenter

| Fichier | Message |
| --- | --- |
| `pyproject.toml` | identité du projet et dépendances, avec une version minimale (`>=`) |
| `uv.lock` | versions **exactes** de toutes les dépendances, y compris indirectes : tout le monde a le même environnement |
| `.python-version` | version de Python ; uv l'installe si besoin |
| `config/config.yaml` | tous les réglages hors du code : chemin des données, découpage, MLflow, grille de recherche |
| `src/crop_recommendation_tp/config.py` | lecture de la configuration |
| `notebooks/01_demarche_modelisation.ipynb` | la démarche |

### Explication du code : `config.py`

```python
ROOT = Path(__file__).resolve().parents[2]
```

- `__file__` est le chemin de `config.py` : `…/src/crop_recommendation_tp/config.py`.
- `.parents[2]` remonte de trois niveaux : `crop_recommendation_tp` (0), `src` (1), racine du projet (2).
- Les chemins de la configuration deviennent indépendants du dossier de lancement : terminal, notebook ou tests.

```python
return yaml.safe_load(f)
```

- `safe_load` (et non `load`) refuse d'exécuter du code contenu dans un fichier YAML : bonne pratique de sécurité.

**Pourquoi un paquet dans `src/`** : `uv sync` installe le projet ; le notebook importe `from crop_recommendation_tp.config import load_config` comme une bibliothèque. Le même code servira aux scripts et aux tests.

### Parcours du notebook

Exécuter le notebook en entier (*Run All*, environ 15 secondes), puis le commenter section par section.

| Section | Point à souligner |
| --- | --- |
| Environnement | première cellule : retour à la racine du projet si le notebook est lancé depuis `notebooks/` |
| 1. Données et objectif | mesure de succès choisie **avant** de modéliser : F1 macro, chaque culture compte autant |
| 2. Qualité des données | aucune valeur manquante, aucun doublon, 100 lignes par culture |
| 3. Analyse exploratoire | distributions à plusieurs pics ; profil par culture (carte de couleurs) ; seule corrélation notable `P`–`K` |
| 4. Protocole d'évaluation | fixé **avant** toute modélisation : test de 20 % mis de côté, validation croisée à 5 plis sur l'entraînement |
| 5. Comparaison de modèles | trois familles comparées sur le même protocole ; forêt aléatoire retenue |
| 6. Réglage | grille de la configuration ; écarts inférieurs à l'écart-type entre plis : combinaisons équivalentes |
| 7. Évaluation finale | **une seule** mesure sur le test : 0,9955, deux erreurs sur 440 |
| 8. Importance des variables | `rainfall`, `humidity`, `K`, `P` ; lien avec la surveillance de la dérive en phase 3 |
| 9. Conclusions | tableau « Industrialisation » : feuille de route des étapes suivantes |

### Explication du code : passages du notebook

**Découpage et validation croisée (section 4)**

```python
train_test_split(..., test_size=..., random_state=seed, stratify=df[target])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
```

- `stratify` : chaque culture garde la même proportion dans l'entraînement et le test.
- `random_state` : le hasard est figé ; même découpage sur tous les postes.
- `StratifiedKFold(shuffle=True)` : 5 plis stratifiés, lignes mélangées avant le découpage (le CSV est rangé par culture).

**Mise à l'échelle dans un pipeline (section 5)**

```python
make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
```

- La régression logistique et les k plus proches voisins sont sensibles aux échelles (`rainfall` jusqu'à 300, `ph` jusqu'à 10).
- Dans un pipeline, la mise à l'échelle est **apprise sur chaque pli d'entraînement** puis appliquée au pli d'évaluation : aucune information du pli d'évaluation ne fuit dans l'entraînement.

**Fonction `evaluer` (section 4)**

```python
scores = cross_validate(
    modele, X_train, y_train, cv=cv, scoring=["f1_macro", "accuracy"]
)
with mlflow.start_run(run_name=nom):
    mlflow.set_tag("etape", "comparaison")
    mlflow.log_params(...)
    mlflow.log_metrics(...)
```

- `cross_validate` renvoie les scores des 5 plis ; on enregistre la moyenne et l'écart-type.
- `start_run` ouvre un **run** : une exécution enregistrée. Tout ce qui est journalisé dans le bloc `with` lui est rattaché.
- Paramètres : réglages en entrée. Métriques : résultats chiffrés. Tags : informations libres (ici, l'étape de la démarche).

**Run du modèle final (section 7)**

- `log_text` et `log_figure` joignent des **artefacts** au run : rapport de classification, matrice de confusion.
- `run_final` conserve l'identifiant du run pour y ajouter ensuite l'importance des variables (section 8).

### Démonstration MLflow

1. Ouvrir l'expérience `crop-recommendation-exploration`.
2. Montrer la liste des runs et la colonne de tag `etape`.
3. Sélectionner les trois runs de comparaison → *Compare* : comparaison des scores.
4. Ouvrir le run « modèle final » → onglet *Artifacts* : matrice de confusion, rapport, importance des variables.

### Vérification

- Notebook exécuté sans erreur.
- Cinq runs dans l'expérience `crop-recommendation-exploration`.

### Transition

« La démarche est correcte, mais tout repose sur ce notebook. Première fragilité : rien ne garantit que les données lues sont celles qu'on attend. »

---

## Étape 1 : validation des données

### Objectif

Écrire ce que l'on attend des données dans un fichier (le **schéma**) et vérifier automatiquement chaque fichier avant de s'en servir. Un pH de 75 ou une culture mal orthographiée faussent un modèle sans produire d'erreur.

### Passage à l'étape

```bash
git checkout -f etape-1
uv sync
git diff etape-0 etape-1 --stat
```

### Fichiers

| Fichier | Changement |
| --- | --- |
| `config/schema.yaml` | nouveau |
| `src/crop_recommendation_tp/validation.py` | nouveau |
| `config/config.yaml` | ajout de `dataset.schema` |
| notebook | section 2 : validation par le schéma ; variables explicatives déduites du schéma |

### Explication du code : `schema.yaml`

```yaml
columns:
    N: { dtype: int, min: 0 }
    ph: { dtype: float, min: 0, max: 14 }
    label:
        dtype: str
        allowed: [apple, banana, …]
```

- Pour chaque colonne : un type, des bornes facultatives, une liste de valeurs autorisées pour la cible.
- Les bornes sont des valeurs **physiquement possibles** (pH entre 0 et 14), et non les valeurs observées.

### Explication du code : `validation.py`

```python
TYPE_CHECKS = {
    "int": types.is_integer_dtype,
    "float": is_number,
    "str": types.is_string_dtype,
}
```

- Dictionnaire de **fonctions** : à chaque type du schéma correspond la fonction pandas qui le vérifie. `TYPE_CHECKS[rules["dtype"]](values)` appelle la bonne fonction.
- `is_number` accepte entiers et décimaux (une température de 21 est valide) et refuse les booléens, que pandas considère comme numériques.

```python
values = df[name].dropna()
n_missing = len(df) - len(values)
if n_missing:
    errors.append(...)
elif not TYPE_CHECKS[rules["dtype"]](values):
    errors.append(...)
    continue
```

- Les valeurs manquantes sont comptées puis écartées avant le contrôle de type.
- `continue` : si le type est faux, inutile de contrôler les bornes de cette colonne.

```python
unknown = sorted(set(values) - set(rules["allowed"]))
```

- Différence d'ensembles : les valeurs présentes qui ne figurent pas dans la liste autorisée.

```python
extra = set(df.columns) - set(schema["columns"])
```

- Colonnes présentes dans les données mais absentes du schéma.

**Choix de conception** : `validate` renvoie la **liste de toutes les erreurs** au lieu de s'arrêter à la première. Une liste vide signifie « conforme ». Cette forme rend la fonction simple à tester (étape 4).

### Démonstration

Dans un terminal :

```bash
uv run python
```

```python
import pandas as pd
from crop_recommendation_tp.config import load_config, load_yaml
from crop_recommendation_tp.validation import validate

c = load_config()
df = pd.read_csv(c["dataset"]["path"])
schema = load_yaml(c["dataset"]["schema"])
validate(df, schema)  # → []

df.loc[0, "ph"] = 15
df.loc[1, "label"] = "ricee"
df.loc[2, "N"] = None
validate(df, schema)
```

Résultat :

```text
['N : 1 valeur(s) manquante(s)', 'ph : 1 valeur(s) > 14', "label : valeurs non autorisées ['ricee']"]
```

### Vérification

- Commande de contrôle du README : résultat `[]`.
- Notebook : section 2, « Erreurs de schéma : [] ».

### Transition

« Les données sont contrôlées. Mais quelle version du fichier a servi à entraîner le modèle ? Si le CSV est corrigé, plus rien ne permet de le savoir. »

---

## Étape 2 : versionnage des données (DVC)

### Objectif

Savoir à tout moment quelle version des données a servi, sans stocker les données dans Git. Git conserve chaque version de chaque fichier : pour des données volumineuses, le dépôt grossirait sans fin (GitHub refuse les fichiers de plus de 100 Mo).

**Principe de DVC** : Git conserve une petite étiquette (fichier `.dvc` contenant l'empreinte md5 des données) ; DVC range le contenu dans un cache et l'envoie vers un stockage.

### Passage à l'étape

```bash
git checkout -f etape-2
uv sync
```

Le CSV disparaît du dossier `data/raw/` : il n'est plus suivi par Git. **Première mise en place** (une seule fois par poste) :

```bash
git show etape-1:data/raw/crop_recommendation.csv > data/raw/crop_recommendation.csv
uv run dvc add data/raw/crop_recommendation.csv
uv run dvc push
uv run dvc status              # → Data and pipelines are up to date.
git status                     # → aucune modification
```

- `git show etape-1:<fichier>` extrait le fichier tel qu'il était dans le commit de l'étape 1.
- `dvc add` calcule l'empreinte : identique à celle de l'étiquette `.dvc` du dépôt, d'où l'absence de modification pour Git.
- `dvc push` crée le stockage `../crop_recommendation_cours_storage` sur le poste.

Aux passages suivants, `uv run dvc pull` suffit.

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `pyproject.toml`, `uv.lock` | ajout de DVC |
| `.dvc/config` | configuration de DVC : stockage par défaut `local_storage` |
| `.dvc/.gitignore`, `.dvcignore` | fichiers internes de DVC, exclus de Git |
| `data/raw/crop_recommendation.csv.dvc` | étiquette des données |
| `data/raw/.gitignore` | exclut le CSV de Git |

### Comment l'étape a été construite

Commandes exécutées pour produire le commit, à commenter :

```bash
uv add dvc                                         # dépendance
uv run dvc init                                    # crée .dvc/ et .dvcignore
git rm --cached data/raw/crop_recommendation.csv   # Git cesse de suivre le CSV (le fichier reste sur le disque)
uv run dvc add data/raw/crop_recommendation.csv    # étiquette .dvc + exclusion dans data/raw/.gitignore
uv run dvc remote add -d local_storage ../crop_recommendation_cours_storage
uv run dvc push
git add .dvc .dvcignore data/raw pyproject.toml uv.lock
git commit -m "Étape 2 : versionnage des données"
```

### Explication : l'étiquette `.dvc`

```yaml
outs:
- md5: 5e743dd4cf49f84d23a904cd51c9b5b8
  size: 150034
  hash: md5
  path: crop_recommendation.csv
```

- L'**empreinte md5** est calculée à partir du contenu du fichier : deux fichiers identiques ont la même empreinte ; la moindre modification la change entièrement.
- Quand les données changent, ce fichier change : la modification apparaît dans l'historique Git comme une modification de code.

### Explication : cache et stockage

```bash
find .dvc/cache -type f
# .dvc/cache/files/md5/5e/743dd4cf49f84d23a904cd51c9b5b8
find ../crop_recommendation_cours_storage -type f
# ../crop_recommendation_cours_storage/files/md5/5e/743dd4cf49f84d23a904cd51c9b5b8
```

- Le contenu est rangé **par empreinte** : les deux premiers caractères forment le dossier, le reste le nom du fichier.
- Le chemin du stockage dans `.dvc/config` (`../../crop_recommendation_cours_storage`) est relatif au dossier `.dvc/`, d'où le double `../`.
- Stockage local en phase 1 ; en phase 3, stockage objet (S3) partagé : seule l'adresse change dans `.dvc/config`.

### Démonstration

```bash
echo '1,2,3,4,5,6,7,inconnu' >> data/raw/crop_recommendation.csv
uv run dvc status                  # → modified: data/raw/crop_recommendation.csv
uv run dvc checkout --force        # restaure la version décrite par le .dvc
uv run dvc status                  # → Data and pipelines are up to date.
```

- Montrer que Git ne voit pas la modification (`git status`) : le CSV est ignoré par Git, seul DVC le surveille.
- `--force` est nécessaire : DVC refuse d'écraser une modification locale sans confirmation.

### Correspondance Git / DVC

| DVC | Effet | Équivalent Git |
| --- | --- | --- |
| `dvc add` | empreinte, cache, étiquette | `git add` |
| `dvc push` | envoi vers le stockage | `git push` |
| `dvc pull` | récupération depuis le stockage | `git pull` |
| `dvc status` | comparaison avec l'étiquette | `git status` |
| `dvc checkout` | restauration de la version décrite | `git checkout` |

### Vérification

- `uv run dvc status` : `Data and pipelines are up to date.`
- `git status` : aucune modification.

### Transition

« Code, environnement et données sont versionnés. Le code de préparation des données reste toutefois enfermé dans le notebook : il faut le rendre réutilisable par d'autres scripts. »

---

## Étape 3 : du notebook au paquet

### Objectif

Sortir du notebook le code qui devra être réutilisé : chargement validé des données, choix des variables, découpage, plis de validation croisée. Une fois dans un module, ce code sert au notebook, aux scripts d'entraînement et aux tests.

### Passage à l'étape

```bash
git checkout -f etape-3
uv sync
uv run dvc pull
git diff etape-2 etape-3 --stat
```

Recharger le notebook dans VS Code, puis redémarrer le noyau.

### Fichiers

| Fichier | Changement |
| --- | --- |
| `src/crop_recommendation_tp/data.py` | nouveau : `load_dataset`, `get_features`, `split_dataset`, `build_cv` |
| notebook | utilise ces quatre fonctions au lieu de son propre code |

### Explication du code : `data.py`

```python
def load_dataset(config: dict) -> pd.DataFrame:
    df = pd.read_csv(ROOT / config["dataset"]["path"])
    schema = load_yaml(config["dataset"]["schema"])
    errors = validate(df, schema)
    if errors:
        raise ValueError("Données non conformes au schéma :\n" + "\n".join(errors))
    return df
```

- Toute lecture des données passe par la validation : des données non conformes **arrêtent** le traitement, avec la liste des erreurs. Principe : échouer tôt et clairement.

```python
def get_features(config: dict) -> list[str]:
    schema = load_yaml(config["dataset"]["schema"])
    return [c for c in schema["columns"] if c != config["dataset"]["target"]]
```

- Les variables explicatives viennent du schéma, dans son ordre : une seule source de vérité. Ajouter une variable revient à modifier `schema.yaml`.

```python
def build_cv(config: dict) -> StratifiedKFold:
    return StratifiedKFold(
        n_splits=config["tuning"]["cv_folds"],
        shuffle=True,
        random_state=config["split"]["random_seed"],
    )
```

- Une seule fonction fabrique les plis. À l'étape 5, `train` et `tune` l'utiliseront toutes deux : elles évalueront un modèle sur exactement les mêmes plis.

### Démonstration

- `git diff etape-2 etape-3 -- notebooks/` : le notebook perd son code de chargement et de découpage, remplacé par des appels de fonctions.
- Exécuter le notebook : résultats identiques (test : 0,9955).

### Vérification

- Notebook exécuté sans erreur, mêmes résultats qu'à l'étape 0.

### Transition

« Le code est réutilisable. Comment savoir qu'il fonctionne encore après une modification ? En l'exécutant à la main à chaque fois, ou en écrivant des tests. »

---

## Étape 4 : tests et qualité du code

### Objectif

Vérifier automatiquement, en quelques secondes, que le code fait ce qu'il doit faire. Un test exécute un bout de code dans une situation précise et compare le résultat au résultat attendu. Ruff vérifie et met en forme le code sans l'exécuter.

### Passage à l'étape

```bash
git checkout -f etape-4
uv sync
uv run dvc pull
uv run pytest
```

Installer l'extension *Ruff* dans VS Code si ce n'est pas fait.

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `pyproject.toml`, `uv.lock` | pytest et Ruff dans les dépendances de développement ; règles de Ruff |
| `tests/test_validation.py` | 9 tests de `validate` |
| `tests/test_data.py` | 4 tests de `data.py` |
| `.vscode/settings.json` | Ruff appliqué à chaque enregistrement |

### Explication du code : un test et ses fixtures

```python
@pytest.fixture
def df():
    """Tableau de deux lignes conformes au schéma."""
    return pd.DataFrame({"N": [90, 20], ...})


def test_ph_hors_bornes(df, schema):
    df.loc[0, "ph"] = 75.0
    assert validate(df, schema) == ["ph : 1 valeur(s) > 14"]
```

- **Découverte** : pytest trouve les fichiers `test_*.py`, puis les fonctions `test_…`.
- **Fixture** : pytest lit le nom des paramètres (`df`, `schema`), exécute la fixture du même nom et passe son résultat au test. Chaque test reçoit un tableau neuf : une modification dans un test n'affecte pas les autres.
- **`assert`** : le test échoue si la condition est fausse, avec le détail de la différence.
- Les tests utilisent de **petits tableaux fabriqués** : ils tournent sans le vrai fichier de données.

```python
def test_plis_reproductibles_et_melanges(config):
    ...
    assert premiers == seconds
    assert premiers[0] != [0, 1, 2, 3, 20, 21, 22, 23]
```

- Deux appels de `build_cv` donnent les mêmes plis (reproductibilité).
- Le premier pli diffère de celui qu'on obtiendrait sans mélange (lignes rangées par culture).

### Explication : règles de Ruff

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "SIM", "RUF"]
```

| Règle | Vérification |
| --- | --- |
| `F` | imports inutilisés ou en double, noms non définis |
| `I` | ordre des imports |
| `E4`, `E7`, `E9` | erreurs de syntaxe et de style graves |
| `SIM` | code simplifiable |
| `RUF` | règles propres à Ruff |

### Démonstration

1. Casser une règle de `validation.py` : dans `TYPE_CHECKS`, remplacer `"float": is_number` par `"float": types.is_float_dtype`, puis `uv run pytest` : `test_entiers_acceptes_pour_un_float` échoue, avec le détail. Le test protège la règle « une température entière est valide ». Annuler la modification (`git checkout -- src`).
2. Dans un fichier, placer `import os` en fin de bloc d'imports, puis `uv run ruff check .` : erreur `I001`. Enregistrer le fichier dans VS Code : Ruff remet les imports dans l'ordre.

### Vérification

```bash
uv run pytest                 # → 13 passed
uv run ruff check .           # → All checks passed!
uv run ruff format --check .
```

### Transition

« Le code est vérifié. Reste à sortir l'entraînement du notebook : une commande qui entraîne le modèle et enregistre tout dans MLflow, à l'identique sur chaque poste. »

---

## Étape 5 : entraînement en script

### Objectif

Remplacer les cellules d'entraînement du notebook par deux commandes reproductibles : `uv run tune` cherche les hyperparamètres, `uv run train` entraîne le modèle retenu. Chaque run enregistre la version des données et celle du code : c'est la base de la traçabilité.

### Passage à l'étape

```bash
git checkout -f etape-5
uv sync
uv run dvc pull
```

Serveur MLflow démarré (commande de l'étape 0).

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `src/crop_recommendation_tp/tracking.py` | connexion à MLflow, enregistrement des runs |
| `src/crop_recommendation_tp/train.py` | commande `train` |
| `src/crop_recommendation_tp/tune.py` | commande `tune` |
| `src/crop_recommendation_tp/data.py` | ajout de `get_data_version` (empreinte des données) |
| `config/config.yaml` | ajout de `model.params` |
| `pyproject.toml` | commandes `train` et `tune` (`[project.scripts]`) |
| `tests/test_train.py` | `train` et `tune` donnent le même score |

### Explication : les commandes

```toml
[project.scripts]
train = "crop_recommendation_tp.train:main"
tune = "crop_recommendation_tp.tune:main"
```

- « La commande `train` appelle la fonction `main` du module `crop_recommendation_tp.train` ». `uv sync` installe ces commandes ; `uv run train` les lance dans l'environnement du projet.

### Explication du code : `train.py`

```python
def build_model(config: dict) -> RandomForestClassifier:
    return RandomForestClassifier(
        **config["model"]["params"],
        random_state=config["split"]["random_seed"],
    )
```

- `**config["model"]["params"]` déplie le dictionnaire de la configuration en arguments nommés : `n_estimators=200, max_depth=None`.
- Fonction séparée de l'entraînement : la validation croisée a besoin d'un modèle **non entraîné**, avec exactement les mêmes réglages.

```python
def cross_validate_model(X_train, y_train, config: dict) -> dict:
    scores = cross_val_score(
        build_model(config), X_train, y_train, scoring=..., cv=build_cv(config)
    )
```

- Score de validation croisée sur l'entraînement : il sert à **comparer** les modèles. Le score sur le test sert seulement à **estimer** la performance.

### Explication du code : `tracking.py`

```python
uri = os.environ.get("MLFLOW_TRACKING_URI") or config["mlflow"]["tracking_uri"]
```

- La variable d'environnement, si elle existe, l'emporte sur la configuration. Les tests s'en servent pour pointer vers une base temporaire.

```python
def get_git_commit() -> str:
    ...
    return git("rev-parse", "HEAD") + ("-dirty" if git("status", "--porcelain") else "")
```

- Identifiant du commit courant ; suffixe `-dirty` si des fichiers suivis sont modifiés sans être commités. Le run signale ainsi lui-même qu'il ne correspond exactement à aucun commit.

```python
with mlflow.start_run(run_name=run_name) as run:
    mlflow.log_params(params)
    mlflow.set_tags({**trace_tags(config), **(tags or {})})
    mlflow.log_dict(config, "config.yaml")
    mlflow.log_dict(load_yaml(config["dataset"]["schema"]), "schema.yaml")
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, name="model", signature=..., input_example=...)
```

- `trace_tags` ajoute `data_md5` (empreinte des données) et `git_commit`.
- `log_dict` enregistre la configuration et le schéma **tels qu'ils étaient** au moment de l'entraînement.
- La **signature** décrit les entrées attendues par le modèle (7 colonnes `float64`).
- `matplotlib.use("Agg")`, en tête du module : rendu des figures sans fenêtre, utilisable dans un script ou en CI.

### Explication du code : `get_data_version`

```python
expected = dvc_file["outs"][0]["md5"]
actual = hashlib.md5((ROOT / config["dataset"]["path"]).read_bytes()).hexdigest()
return actual if actual == expected else actual + "-modified"
```

- Empreinte du fichier réellement lu, comparée à celle de l'étiquette `.dvc`. Suffixe `-modified` si quelqu'un a modifié le CSV sans `dvc add`.

### Explication du code : `tune.py` et `log_tuning`

- `GridSearchCV` essaie les 12 combinaisons de `tuning.param_grid`, chacune sur les 5 plis de `build_cv` ; `n_jobs=-1` utilise tous les cœurs.
- `log_tuning` crée un run parent « tuning » et un run **enfant** par combinaison (`nested=True`) : l'interface reste lisible.
- `tune` n'enregistre pas de modèle et ne modifie pas la configuration : chercher et décider restent deux étapes. On reporte la meilleure combinaison dans `model.params`, puis on commite.

### Démonstration

```bash
uv run tune      # → Meilleurs paramètres : {'max_depth': None, 'n_estimators': 200}
uv run train     # → Run … enregistré : {'cv_f1_macro_mean': 0.9942…, 'accuracy': 0.9954…}
```

Dans MLflow, expérience `crop-recommendation` :

1. Run « tuning » : déplier ses 12 runs enfants, trier par `cv_f1_macro_mean`.
2. Run « train » : onglet *Overview* (paramètres, métriques, tags `data_md5` et `git_commit`), onglet *Artifacts* (configuration, schéma, rapport, matrice de confusion).
3. Faire comparer le score de `tune` pour 200 arbres et profondeur illimitée (0,9943) avec celui de `train` : identiques, grâce à `build_cv`.

### Vérification

- `uv run pytest` : 14 tests réussis.
- Tag `git_commit` du run sans suffixe `-dirty`, égal à `git rev-parse HEAD`.

### Transition

« Tout est vérifiable en local. Mais rien n'oblige à lancer les tests avant de pousser du code. L'intégration continue s'en charge sur une machine neuve. »

---

## Étape 6 : intégration continue

### Objectif

Vérifier automatiquement chaque modification envoyée sur GitHub, sur une machine neuve : installation de l'environnement exact, Ruff, tests. Un commit qui casse quelque chose est signalé immédiatement.

### Passage à l'étape

```bash
git checkout -f etape-6
uv sync
uv run dvc pull
```

### Fichier : `.github/workflows/ci.yml`

```yaml
on:
    push:
    pull_request:
jobs:
    tests:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v7
            - uses: astral-sh/setup-uv@v10.3.3
            - run: uv sync --locked
            - run: uv run ruff check .
            - run: uv run ruff format --check .
            - run: uv run pytest
```

- `on` : déclencheurs (chaque push, chaque pull request).
- `runs-on` : machine virtuelle neuve, fournie par GitHub.
- `uv sync --locked` échoue si `uv.lock` ne correspond pas à `pyproject.toml` : impossible d'oublier de commiter le fichier de verrouillage.
- Les tests ne demandent ni les données, ni MLflow : ils tournent sur cette machine vierge.

### Démonstration

- Onglet *Actions* du dépôt de cours sur GitHub : exécution sur le commit de l'étape 6, chaque étape du workflow en vert.
- Les étudiants ne peuvent pas pousser sur le dépôt de cours. Pour qu'ils voient leur propre CI : *Fork* du dépôt sur leur compte, puis un commit ; l'onglet *Actions* de leur fork montre l'exécution.

### Vérification

- Exécution verte dans l'onglet *Actions*.

### Transition

« La phase 1 est terminée. Vérifions qu'on sait retrouver, pour un modèle entraîné, le code, les données et les réglages qui l'ont produit. »

---

## Fin de phase 1 : traçabilité d'un run d'entraînement

Objectif : partir d'un run de `train` et retrouver le code, les données et les réglages qui l'ont produit.

1. **Le run** : dans MLflow, ouvrir le dernier run « train » de l'expérience `crop-recommendation`.
2. **Les réglages** : onglet *Artifacts*, `config.yaml` et `schema.yaml` tels qu'ils étaient lors de l'entraînement.
3. **Le code** : tag `git_commit`.

   ```bash
   git log -1 --format='%h %s' <git_commit>
   git describe --tags --exact-match <git_commit>     # → etape-6
   ```

4. **Les données** : tag `data_md5`, comparé à l'étiquette DVC de ce commit.

   ```bash
   git show <git_commit>:data/raw/crop_recommendation.csv.dvc     # → md5: 5e743dd4…
   ```

5. **Reproduire** : revenir à ce commit et à ces données, puis réentraîner.

   ```bash
   git checkout -f <git_commit>
   uv sync
   uv run dvc checkout --force
   uv run train                  # → mêmes scores : 0,9943 en validation croisée, 0,9955 sur le test
   ```

Message : **code** (Git), **données** (DVC), **environnement** (`uv.lock`) et **réglages** (configuration enregistrée dans le run) sont tous retrouvables. Le modèle est reproductible.

---

## Étape 7 : serveur MLflow

### Objectif

Remplacer le serveur MLflow local, lancé dans un terminal avec une base SQLite, par un serveur durable : conteneurs Docker, base PostgreSQL, volumes. C'est l'architecture qu'on retrouvera en production.

### Passage à l'étape

1. Arrêter le serveur MLflow local (`Ctrl+C` dans son terminal) : il occupe le port 5001.
2. Changer d'étape et démarrer les services :

   ```bash
   git checkout -f etape-7
   uv sync
   uv run dvc pull
   cp .env.example .env          # puis renseigner POSTGRES_PASSWORD
   docker compose up -d --build
   docker compose ps             # postgres et mlflow « healthy »
   ```

L'adresse du serveur ne change pas (<http://127.0.0.1:5001>) : `config.yaml`, le notebook et les scripts fonctionnent sans modification. Les essais de la base SQLite ne sont pas repris : relancer le notebook et `uv run train`.

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `compose.yaml` | services `postgres` et `mlflow`, volumes |
| `Dockerfile.mlflow` | image du serveur MLflow |
| `.env.example` | modèle du fichier des secrets |
| `.gitignore` | `.env` exclu de Git |

### Explication : notions Docker

| Notion | Définition |
| --- | --- |
| Image | environnement logiciel figé, décrit par un `Dockerfile` |
| Conteneur | image en cours d'exécution, isolée du poste |
| Volume | espace de stockage qui survit à l'arrêt des conteneurs |
| Docker Compose | plusieurs conteneurs décrits dans un seul fichier, lancés ensemble |

### Explication du code : `compose.yaml`

```yaml
postgres:
    image: postgres:18
    env_file: .env
    volumes:
        - postgres_data:/var/lib/postgresql
    healthcheck:
        test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
```

- Image officielle de PostgreSQL ; identifiants lus dans `.env`.
- `$$` : Compose transmet un `$` littéral ; la variable est lue **dans** le conteneur.
- `healthcheck` : Docker vérifie toutes les 5 secondes que la base accepte les connexions.

```yaml
mlflow:
    depends_on:
        postgres:
            condition: service_healthy
    ports:
        - "127.0.0.1:${MLFLOW_PORT:-5001}:5000"
    command: >
        mlflow server --backend-store-uri postgresql+psycopg2://... --artifacts-destination /mlartifacts
```

- `depends_on … service_healthy` : MLflow attend que la base soit prête.
- `ports` : le port 5000 du conteneur est publié sur le port 5001 du poste, **seulement** sur `127.0.0.1`. `${MLFLOW_PORT:-5001}` : valeur de la variable, 5001 par défaut.
- `--backend-store-uri` : paramètres, métriques et registre dans PostgreSQL. Le nom d'hôte `postgres` est le nom du service : Compose crée un réseau où chaque service est joignable par son nom.
- `--artifacts-destination` : fichiers (modèles, figures) dans le volume `mlflow_artifacts`. Les clients envoient leurs fichiers **au serveur**, qui les range.

### Explication du code : `Dockerfile.mlflow`

```dockerfile
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.15 /uv /uvx /bin/
RUN uv pip install --system mlflow==3.18.0 psycopg2-binary
```

- Version de MLflow **figée**, identique à celle du projet (`uv.lock`) : client et serveur sont compatibles.
- `psycopg2-binary` : pilote PostgreSQL.

### Explication : les secrets

- Les identifiants ne sont **jamais** écrits dans `compose.yaml` : Compose les lit dans `.env`, ignoré par Git.
- Le dépôt contient seulement `.env.example`, sans mot de passe, qui documente les variables à fournir.

### Démonstration

1. `docker compose ps` : deux services en bonne santé.
2. `docker volume ls` : volumes `…_postgres_data` et `…_mlflow_artifacts`.
3. Relancer le notebook, puis `uv run train` : les runs apparaissent dans le nouveau serveur.
4. `docker compose down`, puis `docker compose up -d` : les runs sont conservés (volumes). Ne pas utiliser `down -v`, qui supprime les volumes.

### Vérification

- Interface MLflow accessible, nouveaux runs visibles.

### Transition

« Chaque `train` produit un modèle. Lequel doit-on mettre en service ? Il faut une règle, appliquée automatiquement. »

---

## Étape 8 : registre et promotion

### Objectif

Distinguer **tous les essais** (le suivi) des **modèles retenus** (le registre). Un alias, `champion`, désigne le modèle en service. La commande `promote` applique une règle : le dernier candidat devient champion seulement s'il fait mieux.

### Passage à l'étape

```bash
git checkout -f etape-8
uv sync
uv run dvc pull
uv run promote      # → Aucun run candidat : lancer d'abord uv run train.
uv run train
uv run promote      # → Version 1 promue champion (score 0.9943).
uv run promote      # → Le candidat est déjà le champion (version 1).
```

Le premier `promote` ne trouve aucun candidat : les runs des étapes précédentes ne portaient pas l'étiquette `stage = candidate`.

### Fichiers

| Fichier | Changement |
| --- | --- |
| `src/crop_recommendation_tp/promote.py` | nouveau |
| `src/crop_recommendation_tp/train.py` | runs étiquetés `stage = candidate` |
| `config/config.yaml` | `registered_model_name`, `champion_alias` |
| `pyproject.toml` | commande `promote` |
| `tests/conftest.py`, `tests/test_promote.py` | 11 tests de la règle de promotion |

### Explication : registre, versions, alias

- **Registre** : catalogue des modèles retenus, sous un nom (`crop-recommendation`), avec des **versions** numérotées.
- **Alias** : étiquette mobile posée sur une version. L'API demandera « le champion », pas « la version 3 » : changer de modèle en service revient à déplacer l'alias.

### Explication du code : `promote.py`

```python
for run in client.search_runs([experiment.experiment_id]):
    if run.data.tags.get("stage") == "candidate":
        return run.info.run_id
```

- MLflow renvoie les runs du plus récent au plus ancien : le premier run candidat est le dernier entraîné.

```python
try:
    return client.get_model_version_by_alias(...)
except MlflowException:
    return None
```

- Sans champion, MLflow lève une exception : elle est convertie en `None`, que `main` sait traiter.

```python
version = mlflow.register_model(f"runs:/{run_id}/model", name)
client.set_registered_model_alias(name, registry["champion_alias"], version.version)
```

- `runs:/<run_id>/model` désigne le modèle enregistré par ce run. `register_model` en crée une nouvelle version dans le registre ; l'alias y est ensuite déplacé.

```python
if champion_score is not None and candidate_score <= champion_score:
    print(f"Candidat non promu : ...")
    return
```

- Promotion seulement si le score est **strictement** supérieur : à égalité, on garde le modèle en place.

### Explication du code : `conftest.py`

```python
@pytest.fixture
def config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{db}")
    mlflow.set_tracking_uri(f"sqlite:///{db}")
    yield {...}
    mlflow.set_tracking_uri(None)
```

- `conftest.py` : fixtures partagées par tous les fichiers de tests.
- Chaque test reçoit une base MLflow **neuve**, dans un dossier temporaire : aucun serveur nécessaire.
- `yield` coupe la fixture en deux : avant le test, puis après. `set_tracking_uri(None)` efface un réglage **global** de MLflow ; sans cette ligne, le test suivant hériterait de la base du précédent.

### Démonstration

1. Interface MLflow, *Model registry* (barre de gauche) : `crop-recommendation`, version 1, colonne *Aliased versions* : `@champion`.
2. Piège à signaler : l'onglet *Models* d'une expérience liste les modèles enregistrés par les runs ; ils n'ont jamais d'alias.
3. Candidat moins bon : dans `config.yaml`, `n_estimators: 20` et `max_depth: 3`, puis `uv run train` et `uv run promote` → `Candidat non promu : 0.84… <= 0.9943.` Annuler la modification (`git checkout -- config`).

### Vérification

- `uv run pytest` : 25 tests réussis.

### Transition

« Le champion est désigné. Reste à le rendre utilisable par une application : une API. »

---

## Étape 9 : API de prédiction

### Objectif

Exposer le champion par une API web : une application envoie 7 mesures et reçoit la culture recommandée. Les entrées sont contrôlées avec le schéma avant d'atteindre le modèle.

### Passage à l'étape

```bash
git checkout -f etape-9
uv sync
uv run dvc pull
uv run fastapi dev           # http://127.0.0.1:8000/docs
```

Prérequis : services Docker démarrés et champion existant (étape 8).

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `src/crop_recommendation_tp/api.py` | API |
| `pyproject.toml` | FastAPI ; `[tool.fastapi]` désigne l'application |
| `tests/test_api.py` | 5 tests |

### Explication : notions

- **API web** : un programme en appelle un autre par HTTP. **Route** : `POST /predict`. **Code de réponse** : 200 succès, 422 données invalides.
- **FastAPI** : valide les données reçues avec Pydantic et produit une documentation interactive (`/docs`).

### Explication du code : `api.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    version = MlflowClient().get_model_version_by_alias(name, alias)
    app.state.model = mlflow.pyfunc.load_model(f"models:/{name}/{version.version}")
    ...
    yield
```

- `lifespan` s'exécute **une fois**, au démarrage : le modèle est chargé en mémoire, pas à chaque requête.
- L'alias est résolu en numéro de version : `/health` indique la version réellement chargée.
- Sans champion, l'API refuse de démarrer avec un message clair (`RuntimeError`).

```python
fields[name] = (TYPES[rules["dtype"]], Field(ge=rules.get("min"), le=rules.get("max")))
return create_model("CropInput", **fields)
```

- La classe de validation `CropInput` est **construite à partir de `schema.yaml`** : mêmes bornes pour l'entraînement et pour l'API (`ge` : supérieur ou égal, `le` : inférieur ou égal).

```python
@app.post("/predict")
def predict(entree: CropInput):  # pyright: ignore[reportInvalidTypeForm]
    donnees = pd.DataFrame([entree.model_dump()]).astype("float64")
```

- L'annotation `entree: CropInput` est lue par **FastAPI à l'exécution** : lecture du JSON, validation, erreur 422, documentation.
- Le commentaire `pyright: ignore` concerne seulement l'éditeur, qui ne peut pas connaître une classe créée à l'exécution.
- `astype("float64")` : la signature du modèle attend des décimaux.

### Démonstration

1. <http://127.0.0.1:8000/docs> : tester `/health`, puis `/predict` avec l'exemple ci-dessous.

   ```json
   {"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9}
   ```

   Réponse : `{"culture": "rice", "version": "1"}`.

2. Même requête avec `"ph": 15` : erreur 422, `Input should be less than or equal to 14`.
3. Arrêter l'API (`Ctrl+C`).

### Vérification

- `uv run pytest` : 30 tests réussis.

### Transition

« L'API tourne sur le poste, lancée à la main. Pour la déployer, il faut l'empaqueter dans un conteneur, comme MLflow. »

---

## Étape 10 : API en conteneur

### Objectif

Empaqueter l'API dans une image Docker et l'ajouter à Docker Compose : toute la pile (base, serveur MLflow, API) démarre en une commande, identique sur tous les postes. C'est ce qui sera déployé en phase 3.

### Passage à l'étape

1. Arrêter `uv run fastapi dev` s'il tourne : il occupe le port 8000.
2. Changer d'étape et reconstruire :

   ```bash
   git checkout -f etape-10
   uv sync
   uv run dvc pull
   docker compose up -d --build      # plusieurs minutes la première fois
   docker compose ps                 # postgres, mlflow et api « healthy »
   ```

### Fichiers

| Fichier | Rôle |
| --- | --- |
| `Dockerfile.api` | image de l'API |
| `.dockerignore` | fichiers exclus des images |
| `compose.yaml` | service `api` ; option `--allowed-hosts` du serveur MLflow |

### Explication du code : `Dockerfile.api`

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY README.md ./
COPY src/ src/
COPY config/ config/
RUN uv sync --locked --no-dev
```

- Docker garde chaque étape en cache. Les dépendances sont installées **avant** de copier le code : tant que `uv.lock` ne change pas, cette longue étape n'est pas refaite.
- `--no-dev` : ni Jupyter, ni pytest, ni Ruff dans l'image.

```dockerfile
RUN useradd --create-home app
USER app
HEALTHCHECK ... CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
```

- L'API tourne sans droits d'administrateur.
- Contrôle de santé sur `/health`.
- `fastapi run` : mode production, à l'écoute de toutes les interfaces du conteneur.

### Explication : `.dockerignore`

- Exclut des images les secrets (`.env`), les données, l'environnement virtuel, les essais MLflow, les notebooks et les tests.

### Explication du code : `compose.yaml`

```yaml
api:
    depends_on:
        mlflow:
            condition: service_healthy
    environment:
        MLFLOW_TRACKING_URI: http://mlflow:5000
```

- Dans le conteneur, `127.0.0.1` désigne le conteneur lui-même : l'API joint MLflow **par son nom de service**, `mlflow`. La variable d'environnement l'emporte sur `config.yaml` (fonction `setup_mlflow`, étape 5).

```yaml
--allowed-hosts mlflow:5000,localhost:*,127.0.0.1:*
```

- Depuis MLflow 3, le serveur n'accepte que les noms d'hôte autorisés (protection contre le *DNS rebinding*). Sans cette option, il refuse l'API avec une erreur 403 : `Invalid Host header`.

### Démonstration

1. `docker compose ps` : trois services en bonne santé.
2. `curl http://127.0.0.1:8000/health`, puis une prédiction depuis `/docs`.
3. `docker compose exec api whoami` → `app`.
4. Facultatif : retirer `--allowed-hosts`, `docker compose up -d`, puis `docker compose logs api` : erreur 403. Remettre l'option.
5. Nouvelle promotion, puis `docker compose restart api` : `/health` affiche la nouvelle version.

### Vérification

- `/health` répond, `/predict` renvoie une culture.

### Transition

« Toute la chaîne tourne en local. Dernière vérification : peut-on expliquer d'où vient une prédiction ? »

---

## Fin de phase 2 : traçabilité d'une prédiction

Objectif : partir d'une prédiction de l'API et remonter jusqu'au code, aux données et aux réglages qui l'ont produite.

1. **La prédiction** : `POST /predict` → `{"culture": "rice", "version": "1"}`. La réponse contient la version du modèle.
2. **Le modèle chargé** :

   ```bash
   curl http://127.0.0.1:8000/health
   # → {"status": "ok", "version": "1", "run_id": "b1049297…"}
   ```

3. **Le registre** : *Model registry*, `crop-recommendation`, version 1 (`@champion`) → lien vers le run source.
4. **Le run** : tags `data_md5`, `git_commit` et `stage` ; métriques (0,9943 en validation croisée, 0,9955 sur le test) ; artefacts `config.yaml` et `schema.yaml`. En ligne de commande :

   ```bash
   MLFLOW_TRACKING_URI=http://127.0.0.1:5001 uv run mlflow artifacts download --run-id <run_id> --artifact-path config.yaml
   ```

5. **Le code** :

   ```bash
   git log -1 --format='%h %s' <git_commit>     # → a84477a Étape 8 : registre et promotion
   git describe --tags --exact-match <git_commit>  # → etape-8
   ```

6. **Les données** :

   ```bash
   git show <git_commit>:data/raw/crop_recommendation.csv.dvc   # → md5: 5e743dd4…, identique à data_md5
   ```

Chaîne complète : **prédiction → version du modèle → run → réglages, commit du code, version des données**. Chaque maillon est enregistré automatiquement ; aucun ne dépend de la mémoire d'une personne.
