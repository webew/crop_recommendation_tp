# Script formateur : phase 1

Déroulé détaillé de la phase 1, étape par étape. Chaque étape correspond à un commit et à une étiquette Git du dépôt de cours `crop_recommendation_cours`.

Pour chaque étape : objectif, passage à l'étape, fichiers concernés, explication du code, démonstration, vérification, transition.

## Sommaire

| Étape | Étiquette | Notion | Durée indicative |
| --- | --- | --- | --- |
| Préparation | — | postes, dépôt, MLflow | avant la séance |
| 0 | `etape-0` | point de départ : projet uv, configuration, notebook, MLflow | 40 min |
| 1 | `etape-1` | validation des données | 20 min |
| 2 | `etape-2` | versionnage des données (DVC) | 30 min |
| … | | étapes suivantes à venir | |
| Fin | | démonstration de traçabilité | 15 min |

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

- Vérifier que le port 5001 est libre (`lsof -i :5001` sur macOS) : sinon, adapter le port dans la commande MLflow et dans `config/config.yaml`.
- Supprimer les essais d'une séance précédente : `rm -f mlflow.db && rm -rf mlartifacts`.
- Ouvrir VS Code sur le dossier, avec les extensions *Python* et *Jupyter*.

**Postes des étudiants**

- Git, uv et VS Code installés.
- Adresse du dépôt de cours communiquée.

### Changer d'étape

Commandes identiques à chaque étape, à afficher en début de séance :

```bash
git checkout -f etape-N      # -f : abandonne les modifications locales des fichiers suivis
uv sync                      # dépendances de l'étape
uv run dvc pull              # à partir de l'étape 2 : restaure les données
```

- `-f` évite les conflits si un étudiant a modifié des fichiers en suivant la démonstration. Ses modifications sont perdues : le prévenir.
- Le serveur MLflow et ses essais (`mlflow.db`, `mlartifacts/`) ne sont pas suivis par Git : ils sont conservés d'une étape à l'autre. Le serveur peut rester démarré.
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

## Démonstration finale de traçabilité

À rédiger avec l'étape d'entraînement en script (`train.py`), qui enregistre dans chaque run la configuration, le schéma, l'empreinte des données (`data_md5`) et le commit du code (`git_commit`).
