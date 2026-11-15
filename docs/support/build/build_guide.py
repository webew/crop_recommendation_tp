"""Construit le guide PDF : HTML + SVG, rendu par Chrome, sommaire numéroté en deux passes."""

import ast
import base64
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

import figures as F

HERE = Path(__file__).parent
REPO = HERE.parents[2]
RUN = HERE / "assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_HTML = HERE / "guide.html"
OUT_PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "guide_mlops_phase1.pdf"

# ----------------------------------------------------------------- helpers


def md(s: str) -> str:
    """Mini-markdown : `code`, **gras**, *italique*."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def P(*parts):
    return "".join(f"<p>{md(p)}</p>" for p in parts)


def UL(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{md(i)}</li>" for i in items) + "</ul>"


def OL(items):
    return "<ol>" + "".join(f"<li>{md(i)}</li>" for i in items) + "</ol>"


CHAPTERS = []


def H1(title, kicker=None):
    n = len(CHAPTERS) + 1
    cid = f"ch{n}"
    CHAPTERS.append((cid, f"{n}. {title}"))
    k = f'<div class="kicker">{md(kicker)}</div>' if kicker else ""
    return f'<h1 id="{cid}"><span class="num">{n}</span>{md(title)}</h1>{k}'


def H2(title):
    return f"<h2>{md(title)}</h2>"


def H3(title):
    return f"<h3>{md(title)}</h3>"


def code(src: str, lang="python", title=None, keep=None):
    src = src.rstrip("\n")
    lexer = get_lexer_by_name(lang)
    body = highlight(src, lexer, HtmlFormatter(nowrap=True))
    n = src.count("\n") + 1
    keep = (n <= 45) if keep is None else keep
    t = f'<div class="code-title">{html.escape(title)}</div>' if title else ""
    return f'<div class="code{" keep" if keep else ""}">{t}<pre>{body}</pre></div>'


def repo_file(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def FILE(rel, lang="python", title=None, keep=None):
    return code(repo_file(rel), lang, title or rel, keep)


def FUNC(rel, *names, title=None):
    """Extrait une ou plusieurs fonctions d'un fichier Python (décorateurs compris)."""
    src = repo_file(rel)
    lines = src.splitlines()
    tree = ast.parse(src)
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names:
            start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1
            chunks.append("\n".join(lines[start:node.end_lineno]))
    return code("\n\n\n".join(chunks), "python", title or f"{rel} (extrait)")


def LINES(rel, start, end, lang="python", title=None):
    lines = repo_file(rel).splitlines()[start - 1 : end]
    return code("\n".join(lines), lang, title or f"{rel} (lignes {start} à {end})")


ICONS = {"concept": "Concept", "why": "Pourquoi ce choix ?", "warn": "Attention", "tip": "Astuce", "try": "À vous de jouer", "result": "Résultat obtenu"}


def BOX(kind, body, title=None):
    t = title or ICONS[kind]
    return f'<div class="box {kind}"><div class="box-title">{md(t)}</div>{body}</div>'


def TABLE(headers, rows, widths=None, cls=""):
    cols = ""
    if widths:
        cols = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>"
    th = "".join(f"<th>{md(h)}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{md(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}">{cols}<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


FIG_N = [0]


def FIG(svg, caption):
    FIG_N[0] += 1
    return f'<figure>{svg}<figcaption><b>Figure {FIG_N[0]}.</b> {md(caption)}</figcaption></figure>'


def IMG(path, caption, width="70%"):
    FIG_N[0] += 1
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{data}" style="width:{width}"/><figcaption><b>Figure {FIG_N[0]}.</b> {md(caption)}</figcaption></figure>'


def RAW(s):
    return s


# ----------------------------------------------------------------- contenu

S = []  # sections HTML
add = S.append

# ============ Avant de commencer
add('<section class="front">')
add('<h1 class="unnumbered" id="intro">Avant de commencer</h1>')
add(P(
    "Ce guide accompagne le cours sur la **démarche MLOps**. Il raconte, étape par étape, comment un projet de machine learning qui tenait dans un notebook devient une **application** : un programme que l'on peut installer sur n'importe quel poste, relancer à l'identique, tester automatiquement et interroger à distance.",
    "Le fil rouge est un cas concret : recommander une culture agricole (riz, maïs, café…) à partir de 7 mesures du sol et du climat. Le modèle lui-même est volontairement simple (une forêt aléatoire). **Ce qui nous intéresse, c'est tout ce qu'il y a autour du modèle.**",
))
add(H2("Ce que vous saurez faire à la fin"))
add(UL([
    "Expliquer ce qu'apporte la démarche MLOps par rapport à un notebook seul.",
    "Organiser un projet Python en paquet, avec un environnement reproductible (**uv**).",
    "Versionner un jeu de données avec **DVC** et savoir quelle version a servi à entraîner un modèle.",
    "Valider automatiquement des données avant de s'en servir.",
    "Suivre ses expériences avec **MLflow** : paramètres, scores, modèles, traçabilité.",
    "Choisir un modèle sans tricher (validation croisée, jeu de test mis de côté).",
    "Gérer des versions de modèles dans un **registre** et promouvoir le meilleur automatiquement.",
    "Exposer le modèle dans une **API** (FastAPI) qui contrôle les données reçues.",
    "Écrire des **tests** automatisés et les faire tourner en **intégration continue**.",
]))
add(H2("Comment lire ce guide"))
add(P(
    "Les chapitres 1 à 3 donnent la vue d'ensemble : pourquoi, quoi, et comment c'est organisé. Les chapitres 4 à 17 reconstruisent l'application **dans l'ordre où elle a été construite**, fichier par fichier. Chaque fichier y est montré en entier ou presque : en suivant ces étapes, vous pouvez reconstituer tout le projet. Les derniers chapitres proposent un parcours complet à rejouer, un retour d'expérience sur les problèmes rencontrés, les limites actuelles, des exercices et un glossaire.",
    "Tous les résultats cités (scores, messages, durées) sont **réels** : ils ont été obtenus en exécutant le projet.",
))
add(H2("Les encadrés"))
add(BOX("concept", P("Une notion à comprendre et à retenir.")))
add(BOX("why", P("La justification d'un choix d'architecture ou d'outil, et ce qu'on aurait pu faire autrement.")))
add(BOX("warn", P("Un piège classique ou une erreur fréquente.")))
add(BOX("tip", P("Une astuce pratique pour gagner du temps.")))
add(BOX("try", P("Une manipulation à faire vous-même pour vérifier que vous avez compris.")))
add(H2("Prérequis"))
add(TABLE(["Outil", "À quoi il sert ici", "Installation"], [
    ["Git", "Historique du code", "git-scm.com"],
    ["uv", "Python, environnement virtuel et dépendances", "docs.astral.sh/uv"],
    ["Docker Desktop", "Faire tourner le serveur MLflow et sa base de données", "docker.com"],
    ["VS Code", "Éditeur, notebooks (extensions Python, Jupyter, Ruff)", "code.visualstudio.com"],
], widths=[20, 50, 30]))
add(P("Connaissances supposées : Python, pandas, scikit-learn et les notebooks Jupyter. Aucune connaissance préalable de DVC, MLflow, Docker, FastAPI ou pytest n'est nécessaire : tout est expliqué."))
add("</section>")

# ============ 1. Pourquoi
add("<section>")
add(H1("Pourquoi le MLOps ?", "Du « ça marche sur mon poste » au « ça marche partout, et on sait pourquoi »."))
add(H2("Le problème du notebook seul"))
add(P(
    "Le notebook est un excellent outil pour **explorer** : on charge les données, on trace des graphiques, on essaie un modèle, on regarde le score. Mais imaginez la situation suivante, six mois plus tard :",
))
add(UL([
    "Un collègue veut relancer votre notebook : il n'a pas les mêmes versions de pandas et scikit-learn, et le code plante.",
    "Le fichier de données a été corrigé entre-temps : impossible de savoir sur quelle version le « bon » modèle avait été entraîné.",
    "Vous aviez essayé vingt réglages : lequel donnait le score de 0,99 ? Les cellules ont été réexécutées dans le désordre.",
    "Une application doit utiliser le modèle : il faut copier du code depuis le notebook, sans garantie que ce soit le même.",
    "Quelqu'un modifie une fonction : rien ne prévient qu'elle ne fonctionne plus.",
]))
add(P("Aucun de ces problèmes ne vient du modèle. Ils viennent de **tout ce qui entoure le modèle**. C'est précisément le terrain du MLOps."))
add(BOX("concept", P(
    "Le **MLOps** (Machine Learning Operations) est l'ensemble des pratiques qui rendent un projet de machine learning **reproductible**, **traçable**, **testé** et **déployable**. Le mot vient de *DevOps*, la même démarche appliquée au développement logiciel, à laquelle le ML ajoute deux difficultés : les **données** changent, et les **modèles** sont des objets produits par l'entraînement, pas écrits à la main.",
)))
add(H2("La démarche en une image"))
add(P("Un modèle est le produit de trois ingrédients : du **code**, des **données** et un **environnement** (les versions des bibliothèques). Pour reproduire un modèle, il faut pouvoir retrouver les trois. La démarche MLOps associe un outil à chaque ingrédient, plus un outil pour garder la trace des expériences :"))
add(FIG(F.fig_pillars(), "Un outil par ingrédient, et la qualité vérifiée en continu."))
add(H2("Du notebook à l'application"))
add(TABLE(["Dans un notebook", "Dans l'application", "Ce que l'on gagne"], [
    ["Cellules exécutées dans un ordre libre", "Fonctions dans des modules, lancées par une commande (`uv run train`)", "Le même résultat à chaque exécution"],
    ["Valeurs écrites en dur dans les cellules", "Réglages dans `config/config.yaml`", "On change un réglage sans toucher au code"],
    ["`pip install` au fil de l'eau", "`pyproject.toml` + `uv.lock`", "Les mêmes versions sur tous les postes"],
    ["Fichier CSV posé dans un dossier", "Fichier versionné par DVC, contrôlé par un schéma", "On sait quelles données ont servi, et qu'elles sont valides"],
    ["Scores affichés puis perdus", "Runs enregistrés dans MLflow", "Historique complet et comparable"],
    ["Modèle copié à la main", "Registre de modèles + alias `champion`", "On sait quel modèle est en service"],
    ["On vérifie « à l'œil »", "Tests automatisés + CI", "Une régression est détectée immédiatement"],
    ["Résultat lisible par vous seul", "API HTTP documentée", "N'importe quelle application peut utiliser le modèle"],
], widths=[30, 38, 32]))
add(BOX("warn", P("Le notebook ne disparaît pas ! Il reste l'outil idéal pour **explorer**. Ce qui change, c'est que le code qui doit être relancé, partagé et testé quitte le notebook pour rejoindre des modules Python.")))
add(H2("Ce que nous construisons"))
add(P("Voici le cycle complet de l'application. Chaque boîte correspond à un fichier que nous écrirons dans la suite du guide."))
add(FIG(F.fig_cycle(), "Le cycle de l'application, des données brutes à la prédiction servie par l'API."))
add(P(
    "Lecture du schéma : les **données** (1) sont contrôlées par un **schéma** (2), puis **découpées** en jeu d'entraînement et jeu de test (3). L'**entraînement** (4) produit un modèle et des scores, **enregistrés** dans MLflow (5). La **promotion** (6) compare le nouveau modèle au modèle en service et garde le meilleur. L'**API** (7) charge ce meilleur modèle et répond aux **utilisateurs** (8). Les réglages sont centralisés, et les tests vérifient chaque maillon.",
))
add("</section>")

# ============ 2. Cas d'étude
add("<section>")
add(H1("Le cas d'étude : recommander une culture", "Un problème de classification simple, pour se concentrer sur la démarche."))
add(P(
    "Le jeu de données public *Crop Recommendation* décrit 2 200 parcelles. Pour chacune, on connaît 7 mesures et la culture qui y est adaptée. Le but : **à partir des 7 mesures d'une nouvelle parcelle, recommander une culture**. C'est une **classification** à 22 classes.",
))
add(TABLE(["Variable", "Signification", "Min", "Moyenne", "Max", "Type"], [
    ["`N`", "Azote dans le sol", "0", "50,6", "140", "entier"],
    ["`P`", "Phosphore dans le sol", "5", "53,4", "145", "entier"],
    ["`K`", "Potassium dans le sol", "5", "48,1", "205", "entier"],
    ["`temperature`", "Température moyenne (°C)", "8,8", "25,6", "43,7", "décimal"],
    ["`humidity`", "Humidité relative (%)", "14,3", "71,5", "100", "décimal"],
    ["`ph`", "Acidité du sol", "3,5", "6,5", "9,9", "décimal"],
    ["`rainfall`", "Pluviométrie (mm)", "20,2", "103,5", "298,6", "décimal"],
    ["`label`", "Culture recommandée (cible)", "", "", "", "texte, 22 valeurs"],
], widths=[15, 33, 9, 12, 9, 22]))
add(P(
    "Les 22 cultures : *apple, banana, blackgram, chickpea, coconut, coffee, cotton, grapes, jute, kidneybeans, lentil, maize, mango, mothbeans, mungbean, muskmelon, orange, papaya, pigeonpeas, pomegranate, rice, watermelon*. Chacune apparaît **exactement 100 fois** : les classes sont parfaitement équilibrées.",
))
add(H2("Quelle mesure de performance ?"))
add(P(
    "Nous suivons deux mesures. L'**accuracy** (exactitude) est la part de prédictions correctes : simple à comprendre. Le **F1 macro** calcule un score F1 (compromis entre précision et rappel) **pour chaque culture**, puis en fait la moyenne : chaque culture compte autant, même si elle est rare. C'est le F1 macro, mesuré en validation croisée, qui sert à **choisir** les modèles (`tuning.scoring: f1_macro` dans la configuration).",
))
add(BOX("why", P(
    "Ici les classes sont équilibrées, donc accuracy et F1 macro donnent des valeurs proches. Mais en agriculture comme ailleurs, les données réelles sont souvent déséquilibrées (beaucoup de riz, peu de café). Avec une accuracy seule, un modèle qui ignore les cultures rares peut sembler excellent. Prendre l'habitude du F1 macro protège de ce piège.",
)))
add(BOX("result", P(
    "Le modèle retenu (forêt aléatoire de 200 arbres) obtient **0,9943** de F1 macro en validation croisée, et **0,9955** d'accuracy sur le jeu de test (438 bonnes réponses sur 440). Le problème est donc « facile » : tant mieux, cela nous laisse toute l'attention pour la démarche.",
)))
add("</section>")

# ============ 3. Architecture
add("<section>")
add(H1("L'architecture de l'application", "Chaque fichier a un rôle, et un seul."))
add(H2("L'arborescence commentée"))
add(code("""crop_recommendation_tp/
├── pyproject.toml            # identité du projet, dépendances, commandes, réglages des outils
├── uv.lock                   # versions exactes de toutes les dépendances (généré par uv)
├── .python-version           # version de Python du projet (3.13)
├── README.md                 # mode d'emploi
│
├── config/
│   ├── config.yaml           # tous les réglages : chemins, découpage, MLflow, modèle, recherche
│   └── schema.yaml           # contrat des données : colonnes, types, bornes, cultures autorisées
│
├── data/raw/
│   ├── crop_recommendation.csv       # les données (ignorées par Git)
│   └── crop_recommendation.csv.dvc   # leur « étiquette » DVC (versionnée par Git)
│
├── notebooks/
│   └── 01_exploration.ipynb  # exploration et premiers essais
│
├── src/crop_recommendation_tp/       # le code de l'application (un paquet Python)
│   ├── config.py             # lire les fichiers YAML
│   ├── validation.py         # vérifier un tableau par rapport au schéma
│   ├── data.py               # charger, valider, découper, calculer la version des données
│   ├── tracking.py           # se connecter à MLflow et enregistrer les runs
│   ├── train.py              # commande « train » : entraîner un modèle candidat
│   ├── tune.py               # commande « tune » : chercher les meilleurs hyperparamètres
│   ├── promote.py            # commande « promote » : élire le modèle champion
│   └── api.py                # API web qui sert le champion
│
├── tests/                    # tests automatisés (pytest)
│   ├── conftest.py           # fixtures partagées
│   ├── test_validation.py · test_data.py · test_train.py · test_promote.py · test_api.py
│
├── compose.yaml              # services : PostgreSQL, serveur MLflow, API
├── Dockerfile.mlflow · Dockerfile.api · .dockerignore · .env.example
├── .github/workflows/ci.yml  # intégration continue
├── .vscode/settings.json     # Ruff à l'enregistrement
└── .dvc/                     # configuration de DVC (dont l'adresse du stockage)""", "text", "Arborescence du dépôt", keep=True))
add(H2("Les grands principes"))
add(P("Cinq principes guident toute l'organisation. Gardez-les en tête : ils justifient presque tous les choix du guide."))
add(TABLE(["Principe", "Ce que cela veut dire ici"], [
    ["**Séparer le code, les réglages et les données**", "Le code est dans `src/`, les réglages dans `config/`, les données dans `data/` (gérées par DVC). On peut changer l'un sans toucher aux autres."],
    ["**Une seule source de vérité**", "Chaque information est écrite à un seul endroit. Les bornes des variables sont dans `schema.yaml` : la validation des données *et* l'API les lisent là."],
    ["**Une responsabilité par module**", "`validation.py` ne fait que valider, `tracking.py` ne fait que parler à MLflow. Chaque module est petit, lisible et testable seul."],
    ["**Tout est traçable**", "Chaque run enregistre la version des données (`data_md5`), celle du code (`git_commit`) et la configuration utilisée."],
    ["**Échouer tôt et clairement**", "Des données invalides arrêtent l'entraînement avec la liste des erreurs. Une requête invalide est refusée par l'API avant d'atteindre le modèle."],
], widths=[32, 68]))
add(H2("Pourquoi un paquet dans src/ ?"))
add(BOX("why", P(
    "Le code est rangé dans `src/crop_recommendation_tp/` et installé comme un **paquet**. Conséquences : on peut écrire `from crop_recommendation_tp.data import load_dataset` depuis n'importe où (notebook, tests, API) ; les commandes `train`, `tune`, `promote` sont déclarées dans `pyproject.toml` et lancées par `uv run train`. Le dossier intermédiaire `src/` évite un piège classique : sans lui, Python pourrait importer le code du dossier courant au lieu du paquet installé, et les tests passeraient « par accident ».",
    "Alternative : des scripts isolés (`python train.py`). Plus simple au départ, mais les imports entre fichiers deviennent fragiles et le code ne peut pas être réutilisé proprement par l'API ou les tests.",
)))
add(H2("Qui utilise qui ?"))
add(FIG(F.fig_modules(), "Les dépendances entre modules : les commandes s'appuient sur des services, qui s'appuient sur des briques de base."))
add(P(
    "Cette organisation en **couches** est essentielle. Les briques de base (`config.py`, `validation.py`) ne dépendent de rien dans le projet : on peut les tester avec de petits tableaux fabriqués. Les commandes (`train.py`, `promote.py`…) se contentent d'**assembler** les services. Si demain on remplace MLflow par un autre outil, seul `tracking.py` change.",
))
add(H2("Le rôle de chaque script de src/"))
add(TABLE(["Fichier", "Rôle", "Fonctions principales", "Utilisé par"], [
    ["`config.py`", "Lire les fichiers YAML depuis la racine du projet", "`load_yaml`, `load_config`, `ROOT`", "tous"],
    ["`validation.py`", "Comparer un tableau au schéma, lister les erreurs", "`validate`", "`data.py`"],
    ["`data.py`", "Charger et valider le CSV, choisir les variables, découper, calculer l'empreinte", "`load_dataset`, `split_dataset`, `build_cv`, `get_data_version`", "`train`, `tune`, `tracking`"],
    ["`tracking.py`", "Se connecter à MLflow, enregistrer un run complet ou une recherche", "`setup_mlflow`, `log_run`, `log_tuning`, `trace_tags`", "`train`, `tune`, `promote`, `api`"],
    ["`train.py`", "Commande `train` : entraîner, mesurer, enregistrer un candidat", "`build_model`, `cross_validate_model`, `evaluate`, `main`", "utilisateur"],
    ["`tune.py`", "Commande `tune` : comparer des hyperparamètres par validation croisée", "`tune`, `main`", "utilisateur"],
    ["`promote.py`", "Commande `promote` : comparer candidat et champion, déplacer l'alias", "`find_candidate_run_id`, `get_champion`, `promote_candidate`, `main`", "utilisateur"],
    ["`api.py`", "Servir le champion par HTTP", "`lifespan`, `build_input_model`, `health`, `predict`", "clients HTTP"],
], widths=[15, 33, 32, 20]))
add("</section>")

# ============ 4. uv
add("<section>")
add(H1("Étape 1 : créer le projet avec uv", "Un environnement identique sur tous les postes."))
add(H2("Le problème à résoudre"))
add(P(
    "Votre code dépend de bibliothèques (pandas, scikit-learn, MLflow…) qui évoluent sans cesse. Un code écrit avec scikit-learn 1.9 peut se comporter différemment avec la version suivante. Pour reproduire un résultat, il faut donc **les mêmes versions**, de toutes les bibliothèques, y compris celles dont dépendent vos bibliothèques.",
))
add(BOX("concept", P(
    "Un **environnement virtuel** est un dossier (`.venv/`) qui contient un Python et des bibliothèques propres au projet, isolés du reste de la machine. Un **fichier de verrouillage** (*lock file*, ici `uv.lock`) note la version exacte de chaque bibliothèque installée. Avec les deux, n'importe qui recrée exactement le même environnement.",
)))
add(BOX("why", P(
    "**uv** remplace en un seul outil `pip`, `venv`, `pip-tools` et même l'installation de Python. Il est très rapide et produit automatiquement le fichier `uv.lock`. Alternatives : `pip` + `requirements.txt` (pas de verrouillage des dépendances indirectes sans outil supplémentaire), conda, Poetry.",
)))
add(H2("Reconstruire le projet"))
add(code("""# 1. Créer un projet de type « paquet » (dossier src/ et système de construction)
uv init --package crop_recommendation_tp
cd crop_recommendation_tp
uv python pin 3.13                      # écrit .python-version

# 2. Dépendances de l'application
uv add pandas scikit-learn pyyaml dvc mlflow matplotlib "fastapi[standard]"

# 3. Dépendances de développement (inutiles en production)
uv add --dev jupyterlab pytest ruff

# 4. Installer / mettre à jour l'environnement depuis uv.lock
uv sync""", "bash", "Terminal"))
add(P("`uv add` fait trois choses : il ajoute la dépendance dans `pyproject.toml`, met à jour `uv.lock` et installe la bibliothèque dans `.venv/`. Sur un autre poste, un simple `uv sync` suffit à tout réinstaller à l'identique."))
add(H2("Le fichier pyproject.toml"))
add(FILE("pyproject.toml", "toml"))
add(UL([
    "`[project]` : l'identité du projet et ses dépendances, avec une version **minimale** (`>=`). Les versions **exactes** sont dans `uv.lock`.",
    "`[project.scripts]` : chaque ligne crée une **commande**. `train = \"crop_recommendation_tp.train:main\"` signifie : « la commande `train` appelle la fonction `main` du module `crop_recommendation_tp.train` ». On la lance avec `uv run train`. Ces lignes sont à ajouter à la main.",
    "`[dependency-groups] dev` : les outils utiles au développement seulement (notebook, tests, Ruff).",
    "`[tool.ruff.lint]` et `[tool.fastapi]` : les réglages des outils sont centralisés au même endroit.",
]))
add(BOX("tip", P("`uv run <commande>` exécute une commande **dans l'environnement du projet**, sans avoir à l'« activer ». Si l'environnement n'est pas à jour, uv le synchronise d'abord.")))
add(BOX("warn", P("On ne modifie jamais `uv.lock` à la main, et on le **commite** toujours avec `pyproject.toml`. Sans lui, deux postes n'auraient pas les mêmes versions.")))
add("</section>")

# ============ 5. config
add("<section>")
add(H1("Étape 2 : externaliser la configuration", "Aucune valeur « magique » dans le code."))
add(P(
    "Dans un notebook, on écrit souvent `test_size=0.2` ou `n_estimators=200` directement dans une cellule. Si la même valeur est utilisée à trois endroits, il faut penser à la changer trois fois. Et rien ne garde la trace de la valeur utilisée pour un résultat donné.",
    "Ici, **tous les réglages** sont dans un fichier YAML, lisible par un humain et versionné par Git :",
))
add(FILE("config/config.yaml", "yaml"))
add(TABLE(["Section", "Contenu", "Utilisée par"], [
    ["`dataset`", "chemin du CSV, chemin du schéma, nom de la colonne cible", "`data.py`, `api.py`"],
    ["`split`", "part du jeu de test (20 %), graine aléatoire (42)", "`data.py`, `train.py`, `tune.py`"],
    ["`mlflow`", "adresse du serveur, nom de l'expérience, nom du modèle et de l'alias", "`tracking.py`, `promote.py`, `api.py`"],
    ["`model.params`", "hyperparamètres du modèle entraîné par `train`", "`train.py`"],
    ["`tuning`", "nombre de plis, mesure de score, grille de recherche", "`train.py`, `tune.py`, `promote.py`"],
], widths=[18, 52, 30]))
add(H2("Lire la configuration : config.py"))
add(FILE("src/crop_recommendation_tp/config.py"))
add(BOX("concept", P(
    "`ROOT` est la **racine du projet**, calculée à partir de l'emplacement du fichier `config.py` : `Path(__file__)` est `…/src/crop_recommendation_tp/config.py`, et `.parents[2]` remonte de trois niveaux. Grâce à `ROOT`, les chemins de la configuration fonctionnent quel que soit le dossier depuis lequel on lance la commande : terminal, notebook ou tests.",
)))
add(BOX("why", P(
    "Le format YAML est lisible et accepte les commentaires. `yaml.safe_load` (et non `yaml.load`) refuse d'exécuter du code caché dans un fichier : une bonne habitude de sécurité.",
    "La configuration est aussi **enregistrée dans chaque run MLflow** (artefact `config.yaml`). Même si le fichier change plus tard, on retrouve les réglages exacts d'un ancien résultat.",
)))
add("</section>")

# ============ 6. DVC
add("<section>")
add(H1("Étape 3 : versionner les données avec DVC", "Git pour le code, DVC pour les données."))
add(H2("Pourquoi Git ne suffit pas"))
add(P(
    "Git est conçu pour du texte : il garde chaque version de chaque fichier, pour toujours. Pour un fichier de données de plusieurs centaines de mégaoctets, modifié de temps en temps, le dépôt grossirait sans fin et deviendrait inutilisable. GitHub refuse d'ailleurs les fichiers de plus de 100 Mo.",
    "Pourtant, on a besoin de savoir **quelle version des données** a servi à entraîner chaque modèle. DVC (*Data Version Control*) résout ce dilemme.",
))
add(BOX("concept", P(
    "DVC remplace le fichier de données, dans Git, par une **petite étiquette** : un fichier texte `.dvc` qui contient l'**empreinte** (*hash* md5) des données. L'empreinte est une sorte d'empreinte digitale : deux fichiers identiques ont la même, et la moindre modification (un seul caractère) la change complètement. Le contenu réel est rangé dans un **cache** local et copié dans un **stockage distant** (*remote*).",
)))
add(FIG(F.fig_git_dvc(), "Git versionne l'étiquette, DVC range et transporte le contenu."))
add(H2("L'étiquette .dvc"))
add(FILE("data/raw/crop_recommendation.csv.dvc", "yaml"))
add(P("C'est tout ce que Git voit des données : leur empreinte md5, leur taille (150 034 octets) et leur nom. Quand les données changent, ce fichier change, et le changement apparaît dans l'historique Git comme n'importe quelle modification de code."))
add(H2("Reconstruire : les commandes DVC"))
add(code("""# Une seule fois : initialiser DVC dans le dépôt Git (crée le dossier .dvc/)
uv run dvc init
git commit -m "Ajout de DVC"

# Placer les données, puis les confier à DVC
mkdir -p data/raw
cp <chemin>/Crop_recommendation.csv data/raw/crop_recommendation.csv
uv run dvc add data/raw/crop_recommendation.csv
#   → calcule le md5, range une copie dans .dvc/cache/,
#     crée crop_recommendation.csv.dvc et ajoute le CSV à data/raw/.gitignore
git add data/raw/crop_recommendation.csv.dvc data/raw/.gitignore
git commit -m "Versionnage des données avec DVC"

# Déclarer le stockage distant (ici un dossier à côté du dépôt) et y envoyer les données
uv run dvc remote add -d local_storage ../crop_recommendation_storage
git add .dvc/config
git commit -m "Ajout du remote DVC"
uv run dvc push""", "bash", "Terminal"))
add(TABLE(["Commande", "Effet", "Équivalent Git"], [
    ["`dvc add <fichier>`", "Calcule l'empreinte, met le fichier en cache, crée le `.dvc`", "`git add`"],
    ["`dvc push`", "Envoie les données du cache vers le stockage distant", "`git push`"],
    ["`dvc pull`", "Récupère les données correspondant aux fichiers `.dvc` du commit courant", "`git pull`"],
    ["`dvc status`", "Compare les données présentes aux étiquettes `.dvc`", "`git status`"],
    ["`dvc checkout`", "Remet les données dans l'état décrit par les `.dvc`", "`git checkout`"],
], widths=[24, 54, 22]))
add(H2("Les deux scénarios à connaître"))
add(H3("Nouveau poste"))
add(code("""git clone <url-du-dépôt> && cd crop_recommendation_tp
uv sync              # l'environnement
uv run dvc pull      # les données (le stockage doit être accessible)
uv run dvc status    # → Data and pipelines are up to date.""", "bash", "Terminal"))
add(H3("Les données changent"))
add(code("""uv run dvc add data/raw/crop_recommendation.csv   # nouvelle empreinte
git add data/raw/crop_recommendation.csv.dvc
git commit -m "Données corrigées : …"
uv run dvc push""", "bash", "Terminal"))
add(P("Pour revenir à une ancienne version des données : `git checkout <commit> -- data/raw/crop_recommendation.csv.dvc` puis `uv run dvc checkout`."))
add(H2("Le lien avec l'application"))
add(P("Lors de chaque entraînement, l'application calcule l'empreinte du fichier réellement lu et la compare à celle de l'étiquette :"))
add(FUNC("src/crop_recommendation_tp/data.py", "get_data_version"))
add(P("Cette empreinte est enregistrée dans le run MLflow sous l'étiquette `data_md5`. Si quelqu'un a modifié le CSV sans passer par `dvc add`, la valeur se termine par `-modified` : le run signale lui-même qu'il a été entraîné sur des données qui ne correspondent à aucune version connue."))
add(BOX("why", P(
    "Le stockage est ici un **dossier local** (`crop_recommendation_storage`, à côté du dépôt) : rien à installer, idéal pour apprendre. Son défaut : il reste sur le poste où il a été créé. En phase 2, on le remplacera par un stockage partagé (S3, Google Drive, serveur SSH) : seule la ligne `url` de `.dvc/config` changera.",
)))
add(BOX("warn", P("Ne commitez jamais le CSV lui-même dans Git. `dvc add` l'ajoute à `data/raw/.gitignore` pour vous en protéger : ne retirez pas cette ligne.")))
add(BOX("try", P("Modifiez une valeur du CSV, puis lancez `uv run dvc status` : DVC signale le fichier comme modifié. Remettez la version d'origine avec `uv run dvc checkout`.")))
add("</section>")

# ============ 7. Validation
add("<section>")
add(H1("Étape 4 : valider les données", "Un contrat écrit entre les données et le code."))
add(P(
    "Un modèle entraîné sur des données fausses donne des résultats faux, **sans message d'erreur**. Un pH de 75 (impossible : l'échelle va de 0 à 14), une culture mal orthographiée (« ricee »), une colonne manquante : ces erreurs passent inaperçues si personne ne les cherche.",
    "La solution : écrire **ce que l'on attend** des données dans un fichier, le **schéma**, et vérifier automatiquement chaque fichier avant de s'en servir.",
))
add(H2("Le schéma : config/schema.yaml"))
add(LINES("config/schema.yaml", 1, 14, "yaml", "config/schema.yaml (début ; la liste complète compte 22 cultures)"))
add(P("Pour chaque colonne : un **type** (`int`, `float` ou `str`), des **bornes** facultatives (`min`, `max`), et pour la cible la liste des **valeurs autorisées**. Les bornes sont des valeurs *physiquement possibles* (un pH entre 0 et 14), pas les valeurs observées."))
add(H2("Le validateur : validation.py"))
add(FILE("src/crop_recommendation_tp/validation.py"))
add(P("La fonction `validate` vérifie, pour chaque colonne du schéma, dans cet ordre :"))
add(OL([
    "que la colonne **existe** ;",
    "que son type est connu du validateur (une faute de frappe dans le schéma, comme `integer`, est signalée) ;",
    "qu'il n'y a pas de **valeur manquante** ;",
    "que le **type** des valeurs est le bon (`TYPE_CHECKS`) ;",
    "que les valeurs font partie des **valeurs autorisées**, s'il y en a ;",
    "que les valeurs respectent les **bornes** `min` et `max`.",
]))
add(P("Enfin, elle signale les colonnes présentes dans les données mais **absentes du schéma**."))
add(BOX("why", P(
    "`validate` **renvoie la liste de toutes les erreurs** au lieu de s'arrêter à la première. On voit tous les problèmes d'un coup, et une liste vide signifie « conforme ». C'est aussi très facile à tester : on compare la liste obtenue à la liste attendue.",
    "Détail : le type `float` accepte aussi les entiers (une température de 21 est valide), mais refuse les booléens, que pandas considère pourtant comme des nombres. Chaque règle de ce genre est couverte par un test.",
    "Alternatives : des bibliothèques spécialisées comme **Pandera** ou **Great Expectations**. Écrire notre propre validateur, en 50 lignes, permet de comprendre ce qu'elles font.",
)))
add(H2("Où la validation est-elle appelée ?"))
add(FUNC("src/crop_recommendation_tp/data.py", "load_dataset"))
add(P("Toute commande qui charge les données passe par `load_dataset`. Des données non conformes **arrêtent** l'entraînement avec la liste des erreurs : c'est le principe « échouer tôt et clairement »."))
add(BOX("try", P("Dans `schema.yaml`, passez la borne `max` de `ph` à 8, puis lancez `uv run train`. L'entraînement s'arrête : `ValueError: Données non conformes au schéma : ph : … valeur(s) > 8`. Remettez 14.")))
add("</section>")

# ============ 8. Notebook
add("<section>")
add(H1("Étape 5 : explorer dans un notebook", "Le point de départ, et ses limites."))
add(P(
    "Le notebook `notebooks/01_exploration.ipynb` est la première version du travail : charger les données, les valider, les découper, entraîner deux forêts aléatoires et suivre les essais avec MLflow. Il **réutilise déjà** deux briques du paquet (`load_config`, `validate`) : le notebook et l'application partagent le même code.",
))
add(H2("Un premier contact avec MLflow"))
add(P("La cellule centrale entraîne un modèle, le mesure et enregistre tout dans un **run** MLflow :"))
nb = json.loads((REPO / "notebooks/01_exploration.ipynb").read_text(encoding="utf-8"))
cell = next(c for c in nb["cells"] if c["cell_type"] == "code" and "def train_and_log" in "".join(c["source"]))
add(code("".join(cell["source"]), "python", "notebooks/01_exploration.ipynb (cellule train_and_log)"))
add(P("Au début du projet, MLflow enregistrait tout dans une base locale (`mlflow.db`) et un dossier `mlruns/`, consultables avec `uv run mlflow ui --backend-store-uri sqlite:///mlflow.db`. Depuis l'étape 10, les runs partent vers le serveur MLflow."))
add(H2("Le piège caché dans ce notebook"))
add(BOX("warn", P(
    "Cette cellule mesure chaque configuration **sur le jeu de test** (`X_test`), et les scores sont comparés dans MLflow. Tant qu'on se contente de regarder, il n'y a pas de faute. Mais si l'on **choisit** la meilleure configuration d'après ces scores, le jeu de test a servi à décider : son score n'est plus une mesure sur des données jamais vues, il devient **trop optimiste**.",
    "Avec deux essais, l'effet est négligeable. Avec une grille de 12 combinaisons, il devient réel. Le chapitre 10 montre comment l'application évite ce piège.",
), "Attention : le jeu de test ne doit pas servir à choisir"))
add(P("Un encadré rappelant ce piège a été ajouté à la fin du notebook, ainsi qu'une introduction qui précise son rôle : **explorer**, pas servir de version de référence."))
add(H2("Ce qui fait passer du notebook au paquet"))
add(P("Le notebook recopie le chargement et le découpage des données. C'est justement ce code qui a été sorti du notebook pour devenir `data.py` : une fois dans un module, il est réutilisé par `train`, `tune` et l'API, et vérifié par des tests. **Règle pratique** : dès qu'un bout de code doit être relancé, partagé ou testé, il quitte le notebook."))
add("</section>")

# ============ 9. data.py
add("<section>")
add(H1("Étape 6 : préparer les données (data.py)", "Charger, choisir les variables, découper : toujours de la même façon."))
add(FILE("src/crop_recommendation_tp/data.py"))
add(H2("Les variables viennent du schéma"))
add(P("`get_features` prend les colonnes **dans l'ordre du schéma**, sauf la cible. Le schéma est donc la seule source de vérité sur les variables : si l'on en ajoute une, il suffit de modifier `schema.yaml`."))
add(H2("Un découpage stratifié et reproductible"))
add(FIG(F.fig_split(), "Découpage en entraînement et test, puis validation croisée sur l'entraînement seulement."))
add(UL([
    "**`test_size: 0.2`** : 20 % des lignes (440) sont mises de côté pour le test final.",
    "**`stratify=y`** : chaque culture garde la même proportion dans les deux jeux (exactement 20 lignes par culture dans le test). Sans stratification, le hasard pourrait laisser une culture presque absente du test.",
    "**`random_state` (graine 42)** : le hasard est « figé ». Le même découpage est produit à chaque exécution, sur chaque poste. Sans graine, deux entraînements ne seraient pas comparables.",
]))
add(P("`build_cv` prépare les **plis de validation croisée** à partir de la même graine : on y revient au chapitre suivant."))
add(BOX("concept", P("Une **graine aléatoire** (*random seed*) est le point de départ du générateur de nombres pseudo-aléatoires. Avec la même graine, la même suite de « hasards » est produite. Le projet utilise une seule graine, `split.random_seed`, pour le découpage, les plis et la forêt aléatoire.")))
add("</section>")

# ============ 10. train.py
add("<section>")
add(H1("Étape 7 : entraîner et évaluer (train.py)", "Produire un modèle candidat, mesuré honnêtement."))
add(FILE("src/crop_recommendation_tp/train.py"))
add(H2("Ce que fait la commande uv run train"))
add(OL([
    "lit la configuration et **charge les données** (validées par le schéma) ;",
    "les **découpe** en entraînement (80 %) et test (20 %) ;",
    "**entraîne** une forêt aléatoire avec les hyperparamètres de `model.params` ;",
    "mesure le score en **validation croisée** sur le jeu d'entraînement (`cross_validate_model`) ;",
    "mesure le modèle sur le **jeu de test** (`evaluate`) ;",
    "**enregistre** le tout dans un run MLflow, étiqueté `stage = candidate`.",
]))
add(H2("Deux scores, deux rôles"))
add(TABLE(["Score", "Calculé sur", "Sert à"], [
    ["`cv_f1_macro_mean` (et `_std`)", "le jeu d'entraînement, en 5 plis", "**comparer et choisir** les modèles (promotion)"],
    ["`accuracy`, `f1_macro`", "le jeu de test, une seule fois", "**estimer** la performance sur des données nouvelles"],
], widths=[30, 30, 40]))
add(BOX("concept", P(
    "La **validation croisée** découpe le jeu d'entraînement en 5 parts (*plis*). On entraîne 5 fois le modèle, en gardant à chaque fois un pli différent pour l'évaluer, puis on fait la moyenne des 5 scores. On obtient une mesure plus fiable qu'un seul découpage, et un écart-type (`_std`) qui indique sa stabilité, **sans jamais toucher au jeu de test**.",
)))
add(BOX("why", P(
    "C'est la réponse au piège du chapitre 8 : les choix (hyperparamètres, promotion) se font sur le score de validation croisée, calculé sur l'entraînement. Le jeu de test reste « dans le coffre » : il n'influence aucune décision, son score reste donc une estimation honnête.",
)))
add(BOX("why", P(
    "Les plis sont fabriqués par une seule fonction, `build_cv` (dans `data.py`) : les lignes sont mélangées avec la graine, puis réparties en 5 plis stratifiés. `train` **et** `tune` l'utilisent : ils évaluent donc une configuration sur exactement les mêmes plis, et annoncent le même score pour les mêmes réglages. Ce n'était pas le cas au début du projet (voir chapitre 19) ; le test `test_train.py` le vérifie désormais.",
)))
add(BOX("result", RAW(code("""Run 4c4afe99b58d4386944a6b3976431c89 enregistré : {'cv_f1_macro_mean': 0.9942924887437211,
'cv_f1_macro_std': 0.004782482693809713, 'accuracy': 0.9954545454545455, 'f1_macro': 0.9954517027687758}""", "text", "uv run train (environ 7 secondes)")) + P("Score de validation croisée 0,9943 ± 0,0048 ; sur le jeu de test : 0,9955 d'accuracy. Les deux scores sont proches : signe que le modèle généralise bien.")))
add(BOX("why", P("`build_model` est séparée de `train_model` : la validation croisée a besoin d'un modèle **non entraîné** (elle l'entraîne elle-même 5 fois), avec exactement les mêmes réglages. Une seule fonction crée le modèle : impossible que les deux divergent.")))
add("</section>")

# ============ 11. MLflow
add("<section>")
add(H1("Étape 8 : suivre les expériences avec MLflow", "Un cahier de laboratoire automatique."))
add(H2("La philosophie de MLflow"))
add(P(
    "Un chercheur en laboratoire note dans son cahier chaque expérience : le protocole, les réglages, les résultats. MLflow joue ce rôle pour le machine learning : **chaque entraînement laisse une trace complète et consultable**. On ne se demande plus « quel réglage donnait 0,99 ? » : on le retrouve.",
    "MLflow repose sur quelques idées simples :",
))
add(UL([
    "**Tout noter, automatiquement** : c'est le code qui enregistre, pas l'humain. Rien n'est oublié.",
    "**Comparer** : tous les runs d'une expérience sont côte à côte dans l'interface web, triables par score.",
    "**Séparer l'expérimentation de la mise en service** : le *suivi* (tracking) garde tous les essais, le *registre* ne garde que les modèles retenus, avec un alias pour celui qui est en service.",
    "**Être indépendant de la bibliothèque** : le même format sert pour scikit-learn, PyTorch, XGBoost…",
]))
add(FIG(F.fig_mlflow(), "Les concepts de MLflow : expérience, runs et leur contenu, registre de modèles."))
add(TABLE(["Concept", "Définition", "Dans le projet"], [
    ["Expérience", "Un dossier qui regroupe des runs comparables", "`crop-recommendation`"],
    ["Run", "Une exécution : un entraînement ou une recherche", "un run par `uv run train`, un run parent + 12 enfants par `uv run tune`"],
    ["Paramètre", "Un réglage d'entrée (texte)", "`n_estimators`, `max_depth`, `test_size`…"],
    ["Métrique", "Un résultat chiffré", "`cv_f1_macro_mean`, `accuracy`, `f1_macro`"],
    ["Étiquette (tag)", "Une information libre sur le run", "`data_md5`, `git_commit`, `stage`"],
    ["Artefact", "Un fichier joint au run", "`config.yaml`, `schema.yaml`, rapport, matrice de confusion"],
    ["Modèle", "Le modèle sérialisé, avec sa signature", "la forêt aléatoire entraînée"],
    ["Registre", "Les versions des modèles retenus, avec des alias", "modèle `crop-recommendation`, alias `champion`"],
], widths=[17, 40, 43]))
add(H2("Le module tracking.py"))
add(FUNC("src/crop_recommendation_tp/tracking.py", "setup_mlflow", "log_run", "trace_tags"))
add(H3("Se connecter : setup_mlflow"))
add(P("L'adresse du serveur vient de la configuration (`tracking_uri`), sauf si la variable d'environnement `MLFLOW_TRACKING_URI` est définie : elle est alors prioritaire. C'est ce qui permet aux tests d'utiliser une base temporaire sans toucher au serveur."))
add(H3("Enregistrer un run : log_run"))
add(UL([
    "**Paramètres** : tous les réglages du modèle (`model.get_params()`), plus `test_size`.",
    "**Étiquettes** : `data_md5` et `git_commit` (traçabilité), et `stage = candidate` pour la promotion.",
    "**Artefacts** : la configuration et le schéma utilisés, le rapport de classification et la matrice de confusion.",
    "**Modèle** : sérialisé avec sa **signature** (les colonnes et types attendus en entrée, ici 7 colonnes `float64`) et un **exemple d'entrée**.",
]))
add(BOX("concept", P("La **signature** d'un modèle décrit ses entrées et ses sorties. MLflow s'en sert pour vérifier les données qu'on lui donne à prédire. C'est pourquoi l'API convertit les mesures en `float64` avant d'appeler le modèle.")))
add(IMG(RUN / "confusion_matrix.png", "Matrice de confusion du modèle candidat, enregistrée comme artefact du run (440 lignes de test).", width="62%"))
add(P("Lecture : chaque ligne est la culture réelle, chaque colonne la culture prédite. Tout est sur la diagonale, sauf deux erreurs (sur 440). L'image est produite par le code (`matplotlib`, mode sans fenêtre `Agg`) et jointe au run : pas besoin de relancer le notebook pour la revoir."))
add(H2("La traçabilité de bout en bout"))
add(FIG(F.fig_trace(), "De la prédiction jusqu'au code et aux données qui l'ont produite."))
add(P("`get_git_commit` ajoute `-dirty` si des fichiers étaient modifiés sans être commités : le run avoue lui-même qu'il ne correspond exactement à aucun commit. **Bonne pratique** : commiter avant d'entraîner un modèle que l'on veut garder."))
add(BOX("result", RAW(TABLE(["Étiquette", "Valeur réelle"], [
    ["`data_md5`", "`5e743dd4cf49f84d23a904cd51c9b5b8`"],
    ["`git_commit`", "`7e8606eda26790280fc56e68e30a68d41d0eb36a-dirty`"],
    ["`stage`", "`candidate`"],
], widths=[25, 75]))))
add(BOX("tip", P("Avec MLflow 3, le modèle d'un run apparaît dans l'onglet **Models** de l'expérience (un *logged model* relié au run), et non plus dans la liste des artefacts du run. L'adresse `runs:/<run_id>/model` continue de le désigner.")))
add("</section>")

# ============ 12. tune
add("<section>")
add(H1("Étape 9 : chercher les hyperparamètres (tune.py)", "Comparer des réglages, sans tricher."))
add(P("Un **hyperparamètre** est un réglage choisi avant l'entraînement (le nombre d'arbres, leur profondeur maximale). Pour trouver les meilleurs, on en essaie plusieurs combinaisons et on compare leurs scores **en validation croisée**."))
add(FILE("src/crop_recommendation_tp/tune.py"))
add(P("`GridSearchCV` essaie **toutes** les combinaisons de la grille `tuning.param_grid` : 3 valeurs de `n_estimators` × 4 valeurs de `max_depth` = 12 combinaisons, chacune évaluée sur les 5 plis de `build_cv` (les mêmes que `train`), soit 60 entraînements. `n_jobs=-1` utilise tous les cœurs du processeur."))
add(H2("L'enregistrement : un run parent et 12 enfants"))
add(FUNC("src/crop_recommendation_tp/tracking.py", "log_tuning"))
add(P("Les **runs imbriqués** (`nested=True`) rangent les 12 essais sous un même run « tuning » : l'interface reste lisible, et la meilleure combinaison est notée sur le parent (`best_n_estimators`, `best_max_depth`)."))
add(H2("Résultats réels"))
add(FIG(F.fig_tuning(), "Score en validation croisée des 12 combinaisons (uv run tune, environ 7 secondes)."))
add(P("La profondeur compte beaucoup plus que le nombre d'arbres : des arbres limités à 3 niveaux ne savent pas distinguer 22 cultures (0,88 à 0,90). Au-delà de 10 niveaux, les scores se tiennent à quelques millièmes. La meilleure combinaison, **200 arbres de profondeur illimitée** (0,9943), est celle reportée dans `model.params`."))
add(H2("Le circuit de travail"))
add(OL([
    "`uv run tune` : la recherche affiche la meilleure combinaison.",
    "On **reporte** cette combinaison dans `model.params` de `config/config.yaml`, et on **commite** la modification (le choix est tracé dans Git).",
    "`uv run train` : on entraîne le candidat avec ces réglages.",
    "`uv run promote` : on le compare au champion.",
]))
add(BOX("why", P(
    "`tune` **n'enregistre pas de modèle** et ne modifie pas la configuration tout seul : chercher et décider sont deux actes séparés. Une recherche est occasionnelle et coûteuse ; l'entraînement doit pouvoir être relancé à l'identique à partir de la seule configuration. Le report à la main garde un humain dans la boucle et une trace dans Git.",
)))
add("</section>")

# ============ 13. Docker
add("<section>")
add(H1("Étape 10 : le serveur MLflow avec Docker", "Un serveur partagé plutôt qu'un fichier sur un poste."))
add(H2("Pourquoi un serveur ?"))
add(P(
    "Avec une base SQLite locale (`mlflow.db`), chaque poste a ses propres runs : impossible de comparer son travail avec celui d'un collègue, et le **registre de modèles** (étape suivante) doit être consultable par l'API. Un **serveur MLflow** centralise tout : les scripts et l'API lui parlent par HTTP.",
))
add(BOX("concept", P(
    "**Docker** fait tourner des logiciels dans des **conteneurs** : des environnements isolés, décrits par une **image**, qui fonctionnent de la même façon sur tous les ordinateurs. **Docker Compose** lance plusieurs conteneurs qui travaillent ensemble, décrits dans un seul fichier `compose.yaml`. Un **volume** est un espace de stockage qui survit à l'arrêt des conteneurs.",
)))
add(FIG(F.fig_docker(), "PostgreSQL, le serveur MLflow et l'API, lancés par Docker Compose."))
add(FILE("compose.yaml", "yaml"))
add(UL([
    "**`postgres`** : la base de données qui stocke les métadonnées (paramètres, métriques, registre). Le `healthcheck` vérifie toutes les 5 secondes qu'elle est prête.",
    "**`mlflow`** : le serveur, construit à partir de `Dockerfile.mlflow`. `depends_on … service_healthy` : il ne démarre que lorsque la base est prête.",
    "**`ports: \"127.0.0.1:${MLFLOW_PORT:-5002}:5000\"`** : le port 5000 du conteneur est accessible sur le port 5002 de votre poste, et **seulement depuis votre poste** (`127.0.0.1`). C'est l'adresse `tracking_uri` de `config.yaml`. La variable `MLFLOW_PORT` permet d'en choisir un autre.",
    "**`--allowed-hosts`** : depuis MLflow 3, le serveur n'accepte que les noms d'hôte autorisés, pour se protéger d'une attaque appelée *DNS rebinding*. Sans cette option, il refusait l'API, qui l'appelle sous le nom `mlflow` (erreur 403).",
    "**`healthcheck` de `mlflow`** : interroge `/health` toutes les 5 secondes. C'est ce qui permet à l'API d'attendre un serveur prêt.",
    "**`api`** : l'API de prédiction, construite à partir de `Dockerfile.api` (voir plus bas). Elle démarre quand MLflow est prêt et le joint **par son nom dans le réseau Docker** : `MLFLOW_TRACKING_URI=http://mlflow:5000`. Elle écoute sur le port 8000 (`API_PORT`).",
    "**`--artifacts-destination /mlartifacts`** : les fichiers (modèles, images) sont stockés dans le volume `mlflow_artifacts`, et les clients les envoient *au serveur*, qui les range : les scripts n'ont pas besoin d'accès direct au stockage.",
]))
add(FILE("Dockerfile.mlflow", "docker"))
add(P("L'image part d'un Python 3.13 minimal, y copie uv et installe MLflow **à une version figée** (`3.17.2`, la même que dans le projet) avec le pilote PostgreSQL."))
add(H2("L'API dans un conteneur"))
add(FILE("Dockerfile.api", "docker"))
add(UL([
    "**Les dépendances d'abord, le code ensuite** : Docker garde chaque étape en cache. Tant que `uv.lock` ne change pas, la longue installation des dépendances n'est pas refaite ; modifier le code ne relance que la fin.",
    "**`--no-dev`** : ni Jupyter, ni pytest, ni Ruff dans l'image.",
    "**`useradd` puis `USER app`** : l'API ne tourne pas avec les droits d'administrateur. Si elle était compromise, l'attaquant aurait moins de pouvoir.",
    "**`HEALTHCHECK`** : Docker interroge `/health` ; le conteneur est déclaré « en bonne santé » seulement quand l'API répond.",
    "**`fastapi run`** (et non `fastapi dev`) : le mode production, qui écoute sur toutes les interfaces du conteneur.",
    "Le projet est installé en mode modifiable dans `/app` : la constante `ROOT` de `config.py` y retrouve `config/config.yaml` et `config/schema.yaml`.",
]))
add(FILE(".dockerignore", "text"))
add(P("Ce fichier liste ce qui ne doit **jamais** entrer dans une image : les secrets (`.env`), les données, l'environnement virtuel, les runs MLflow, et ce qui ne sert pas à l'API."))
add(BOX("why", P(
    "L'image contient le **code**, mais pas le **modèle** : l'API le charge depuis le registre au démarrage. Changer de champion ne demande donc pas de reconstruire l'image, seulement de redémarrer le conteneur (`docker compose restart api`).",
    "Les scripts `train`, `tune` et `promote` restent sur le poste : ils ont besoin des données DVC et du dépôt Git (pour `git_commit`), et ils ne tournent que ponctuellement. Seuls les **services**, qui doivent rester disponibles, sont en conteneur.",
)))
add(H2("Les secrets : .env"))
add(FILE(".env.example", "bash"))
add(P("Les identifiants de la base ne sont **jamais écrits dans `compose.yaml`** : Compose les lit dans un fichier `.env`, ignoré par Git. Le dépôt ne contient que le modèle `.env.example`, sans mot de passe."))
add(code("""cp .env.example .env          # puis renseigner POSTGRES_PASSWORD
docker compose up -d --build  # construit les images et démarre postgres, mlflow et l'API
docker compose ps             # état des services
docker compose restart api    # recharger le champion après une promotion
# interface web : http://localhost:5002
docker compose down           # arrêt, données conservées (volumes)
docker compose down -v        # arrêt ET suppression des données""", "bash", "Terminal"))
add(BOX("warn", P("Si `.env` est absent, Compose affiche `The \"POSTGRES_USER\" variable is not set` et `env file … .env not found`. C'est le premier problème rencontré pendant le projet (voir chapitre 19). Un mot de passe vide empêche aussi PostgreSQL de démarrer.")))
add(BOX("why", P("PostgreSQL plutôt que SQLite côté serveur : plusieurs clients peuvent écrire en même temps sans bloquer la base, et c'est la configuration qu'on retrouve en production. Docker évite d'installer PostgreSQL et MLflow sur chaque poste, avec des versions différentes.")))
add("</section>")

# ============ 14. promote
add("<section>")
add(H1("Étape 11 : registre et promotion (promote.py)", "Décider automatiquement quel modèle est en service."))
add(H2("Le registre de modèles"))
add(P(
    "Le **suivi** garde *tous* les essais. Le **registre** ne garde que les modèles que l'on a décidé de conserver, sous un nom (`crop-recommendation`) et avec des **versions** numérotées (1, 2, 3…). Un **alias** est une étiquette mobile posée sur une version : `@champion` désigne le modèle en service.",
))
add(BOX("why", P(
    "L'API ne demande pas « la version 3 », mais « le **champion** ». Changer de modèle en service revient à **déplacer l'alias** : l'API n'a pas besoin d'être modifiée. MLflow proposait autrefois des *stages* fixes (Staging, Production) ; ils sont dépréciés au profit des alias, plus souples.",
)))
add(H2("La règle de promotion"))
add(FIG(F.fig_promote(), "La logique de décision de uv run promote."))
add(P("Le candidat devient champion seulement si son score de validation croisée est **strictement supérieur**. À score égal, on garde le modèle en place : changer de modèle a un coût (vérifications, redémarrage de l'API) qui n'est pas justifié sans gain."))
add(FILE("src/crop_recommendation_tp/promote.py"))
add(UL([
    "`find_candidate_run_id` : le run étiqueté `stage = candidate` **le plus récent** (MLflow renvoie les runs du plus récent au plus ancien).",
    "`get_champion` : la version qui porte l'alias, ou `None` s'il n'y a pas encore de champion.",
    "`get_run_score` : `.get(metric)` renvoie `None` si un run n'a pas la métrique (par exemple un run créé avant l'ajout de la validation croisée), au lieu de planter.",
    "`promote_candidate` : crée une nouvelle version dans le registre à partir du modèle du run (`runs:/<run_id>/model`) et y déplace l'alias.",
]))
add(BOX("why", P("Chaque cas particulier a son message clair, et chacun est couvert par un test : pas de candidat, candidat sans métrique, candidat déjà champion, champion sans score. Une commande d'automatisation doit se comporter de façon prévisible dans **tous** les cas, pas seulement le cas normal.")))
add(H2("Résultats réels"))
add(TABLE(["Situation", "Commande", "Sortie obtenue"], [
    ["Base vide", "`uv run promote`", "`Aucun run candidat : lancer d'abord uv run train.`"],
    ["Premier candidat (0,9943)", "`uv run promote`", "`Version 1 promue champion (score 0.9943).`"],
    ["Relance sans nouvel entraînement", "`uv run promote`", "`Le candidat est déjà le champion (version 1).`"],
    ["Candidat moins bon (20 arbres, profondeur 3)", "`uv run promote`", "`Candidat non promu : 0.8472 <= 0.9943.`"],
], widths=[30, 18, 52]))
add("</section>")

# ============ 15. API
add("<section>")
add(H1("Étape 12 : servir le modèle avec une API (api.py)", "Le modèle devient utilisable par n'importe quelle application."))
add(BOX("concept", P(
    "Une **API web** (interface de programmation) permet à un programme d'en appeler un autre par le réseau, avec le protocole HTTP. Le client envoie une **requête** à une **route** (`POST /predict` avec les 7 mesures en JSON) ; l'API renvoie une **réponse** (la culture recommandée, en JSON) et un **code** : 200 = succès, 422 = données invalides, 500 = erreur du serveur.",
)))
add(BOX("why", P("**FastAPI** est simple, rapide, et s'appuie sur **Pydantic** pour valider les données reçues. Il génère aussi une documentation interactive (`/docs`) à partir du code. Alternatives : Flask (plus ancien, validation à écrire soi-même), ou le serveur intégré `mlflow models serve` (sans contrôle fin des entrées).")))
add(FILE("src/crop_recommendation_tp/api.py"))
add(FIG(F.fig_api(), "Démarrage de l'API, puis traitement d'une requête de prédiction."))
add(H2("Le démarrage : lifespan"))
add(P(
    "`lifespan` s'exécute **une seule fois**, au démarrage. Il demande au registre quelle version porte l'alias `champion`, charge ce modèle en mémoire et range dans `app.state` le modèle, son numéro de version et son run. Charger le modèle à chaque requête serait beaucoup trop lent.",
    "S'il n'y a pas de champion, l'API **refuse de démarrer**, avec un message qui dit quoi faire (`uv run train` puis `uv run promote`). Mieux vaut ne pas démarrer que servir sans modèle.",
))
add(H2("La validation des entrées, depuis le schéma"))
add(P("`build_input_model` construit la classe Pydantic `CropInput` **à partir de `schema.yaml`** : chaque variable devient un champ, avec son type et ses bornes (`ge` = supérieur ou égal, `le` = inférieur ou égal). Les règles des données d'entraînement et celles de l'API restent donc toujours identiques : une seule source de vérité."))
add(BOX("concept", P(
    "Dans `def predict(entree: CropInput)`, l'annotation de type n'est pas décorative : **FastAPI la lit pendant l'exécution**. Elle lui indique de lire le corps JSON, de le valider avec `CropInput`, de renvoyer une erreur 422 si les données sont invalides, et de documenter les champs dans `/docs`.",
    "L'analyseur de VS Code (Pylance), lui, ne peut pas connaître une classe créée pendant l'exécution par `create_model` : le commentaire `# pyright: ignore[reportInvalidTypeForm]` lui demande d'ignorer cette ligne. FastAPI n'est pas concerné par ce commentaire.",
)))
add(BOX("why", P("Autre solution possible : écrire la classe `CropInput` à la main (7 champs). C'est plus lisible et mieux compris par l'éditeur, mais les bornes seraient écrites deux fois. Il faudrait alors un test qui vérifie qu'elles correspondent à `schema.yaml`. Les deux choix se défendent ; celui du projet privilégie la source unique.")))
add(H2("Lancer et interroger l'API"))
add(code("""docker compose up -d      # l'API tourne dans son conteneur : http://127.0.0.1:8000/docs
# pour développer sans conteneur : uv run fastapi dev

curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" \\
     -d '{"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9}'""", "bash", "Terminal"))
add(BOX("result", RAW(TABLE(["Requête", "Réponse réelle"], [
    ["`GET /health`", "`{\"status\": \"ok\", \"version\": \"1\", \"run_id\": \"4c4afe99b58d4386944a6b3976431c89\"}`"],
    ["`POST /predict` N=90, P=42, K=43, 20,8 °C, 82 %, pH 6,5, 202,9 mm", "`{\"culture\": \"rice\", \"version\": \"1\"}`"],
    ["`POST /predict` N=20, P=130, K=200, 22,5 °C, 92 %, pH 6,0, 110 mm", "`{\"culture\": \"apple\", \"version\": \"1\"}`"],
    ["`POST /predict` avec `ph: 15`", "code **422** : `Input should be less than or equal to 14` (champ `ph`)"],
], widths=[45, 55]))))
add(P("La réponse contient le **numéro de version** du modèle : chaque prédiction est traçable jusqu'au run, donc jusqu'aux données et au code (voir la figure de traçabilité au chapitre 11)."))
add(BOX("warn", P("Le modèle est chargé au démarrage. Après une nouvelle promotion, il faut **redémarrer l'API** (`docker compose restart api`) pour qu'elle serve le nouveau champion : `/health` permet de vérifier quelle version tourne.")))
add("</section>")

# ============ 16. Tests
add("<section>")
add(H1("Étape 13 : tester l'application", "Des vérifications automatiques, relancées à chaque modification."))
add(H2("Pourquoi des tests ?"))
add(P(
    "Dans un notebook, on vérifie « à l'œil » en regardant les sorties. Mais quand on modifie une fonction, qui revérifie toutes les autres ? Un **test automatisé** est une petite fonction qui exécute un bout de code dans une situation précise et **vérifie le résultat**. On les lance tous en une commande, en quelques secondes, aussi souvent qu'on veut.",
    "Les tests servent à trois choses : **détecter les régressions** (ce qui marchait et ne marche plus), **documenter** le comportement attendu (un test se lit comme un exemple), et **oser modifier** le code sans crainte.",
))
add(H2("Les notions de pytest utilisées"))
add(TABLE(["Notion", "Rôle", "Exemple dans le projet"], [
    ["Fonction `test_…`", "Un test ; pytest les trouve tout seul dans les fichiers `test_*.py`", "`test_ph_hors_bornes`"],
    ["`assert`", "La vérification : le test échoue si la condition est fausse", "`assert validate(df, schema) == []`"],
    ["Fixture", "Prépare ce dont un test a besoin ; injectée par le nom du paramètre", "`df`, `schema`, `config`, `client`"],
    ["`conftest.py`", "Fixtures partagées par tous les fichiers de tests", "la fixture `config` (base temporaire)"],
    ["`tmp_path`", "Un dossier temporaire neuf, propre à chaque test", "accueille la base SQLite"],
    ["`monkeypatch`", "Remplace temporairement une variable ou une fonction", "`MLFLOW_TRACKING_URI`, `load_config`"],
    ["`capsys`", "Capture ce que le code affiche", "messages de `promote`"],
    ["`pytest.raises`", "Vérifie qu'une erreur est bien levée", "API sans champion"],
    ["`TestClient`", "Appelle l'API sans lancer de serveur", "`client.post(\"/predict\", …)`"],
], widths=[18, 47, 35]))
add(H2("Stratégie de test"))
add(FIG(F.fig_tests(), "Chaque fichier de test vérifie un module ; les tests MLflow utilisent une base temporaire."))
add(UL([
    "**Des données fabriquées, petites et lisibles** : 2 lignes pour la validation, 20 pour le découpage. Les tests ne dépendent pas du vrai CSV : ils tournent partout, y compris en CI, sans `dvc pull`.",
    "**Un modèle factice** (`DummyClassifier`) pour la promotion et l'API : on teste la *logique* (qui devient champion ?), pas la qualité d'un modèle.",
    "**Une base MLflow SQLite neuve pour chaque test** : aucun serveur nécessaire, et les tests ne se perturbent pas entre eux.",
    "**Un test par cas**, y compris les cas d'erreur : c'est souvent là que se cachent les bugs.",
]))
add(H2("L'isolation des tests : conftest.py"))
add(FILE("tests/conftest.py"))
add(P("Le `yield` coupe la fixture en deux : ce qui précède s'exécute **avant** le test, ce qui suit **après**. La dernière ligne efface le réglage de MLflow, pour que le test suivant ne reparte pas avec la base de celui-ci."))
add(BOX("warn", P(
    "Cette remise à zéro a été ajoutée après un vrai bug (chapitre 19). `mlflow.set_tracking_uri` est un réglage **global**, qui survit d'un test à l'autre et qui l'emporte sur la variable d'environnement. Un test passait seulement parce qu'il était exécuté en premier ; lancé après un autre, il lisait la base du test précédent et échouait.",
    "Leçon : **un test ne doit jamais dépendre de l'ordre d'exécution**. Pour le vérifier, on peut lancer deux tests dans l'ordre inverse.",
), "Attention : l'état global"))
add(H2("Plan de test"))
add(P("Le tableau suivant liste les 30 tests : ce qu'ils vérifient, la situation créée et le résultat attendu."))
plan = [
    ["V1", "`test_donnees_conformes`", "2 lignes conformes", "aucune erreur (`[]`)"],
    ["V2", "`test_colonne_absente`", "colonne `ph` supprimée", "`Colonne absente : ph`"],
    ["V3", "`test_ph_hors_bornes`", "pH = 75", "`ph : 1 valeur(s) > 14`"],
    ["V4", "`test_valeur_manquante_et_valeur_hors_bornes`", "N vide sur une ligne, N = −5 sur l'autre", "les deux erreurs, dans l'ordre"],
    ["V5", "`test_culture_inconnue`", "culture « ricee »", "`valeurs non autorisées ['ricee']`"],
    ["V6", "`test_colonne_non_declaree`", "colonne `extra` ajoutée", "colonne non déclarée signalée"],
    ["V7", "`test_type_inconnu_dans_le_schema`", "type `integer` dans le schéma", "type inconnu signalé"],
    ["V8", "`test_entiers_acceptes_pour_un_float`", "températures entières", "aucune erreur"],
    ["V9", "`test_booleens_refuses_pour_un_float`", "pH = True / False", "`ph : type bool, attendu float`"],
    ["D1", "`test_variables_sans_la_cible`", "schéma réel", "les 7 variables, dans l'ordre, sans `label`"],
    ["D2", "`test_decoupage_taille_et_stratification`", "20 lignes, 2 cultures", "16 / 4 lignes, 2 de chaque culture en test"],
    ["D3", "`test_decoupage_reproductible`", "deux découpages successifs", "exactement les mêmes lignes"],
    ["D4", "`test_plis_reproductibles_et_melanges`", "40 lignes rangées par culture", "5 plis, identiques d'un appel à l'autre, lignes mélangées"],
    ["T1", "`test_train_et_tune_donnent_le_meme_score`", "mêmes réglages dans `train` et `tune`", "exactement le même score de validation croisée"],
    ["P1", "`test_find_candidate_without_experiment`", "base vide", "aucun candidat (`None`)"],
    ["P2", "`test_find_candidate_returns_latest`", "deux candidats", "le plus récent"],
    ["P3", "`test_get_champion_without_alias`", "pas d'alias", "`None`"],
    ["P4", "`test_promote_candidate_sets_champion`", "promotion d'un run", "l'alias pointe sur la nouvelle version et le bon run"],
    ["P5", "`test_main_without_candidate`", "`promote` sur base vide", "message « Aucun run candidat »"],
    ["P6", "`test_main_promotes_first_candidate`", "premier candidat", "promu champion"],
    ["P7", "`test_main_keeps_better_champion`", "champion 0,95 puis candidat 0,90", "« non promu », champion inchangé"],
    ["P8", "`test_main_promotes_better_candidate`", "champion 0,90 puis candidat 0,95", "le nouveau candidat devient champion"],
    ["P9", "`test_main_detects_candidate_already_champion`", "`promote` relancé", "« déjà le champion »"],
    ["P10", "`test_main_rejects_candidate_without_metric`", "candidat sans score", "message clair, aucun champion créé"],
    ["P11", "`test_main_replaces_champion_without_metric`", "champion sans score, candidat 0,90", "le candidat devient champion"],
    ["A1", "`test_health`", "API avec un champion", "200, `status: ok`, version `1`"],
    ["A2", "`test_predict`", "7 mesures valides", "200, `{\"culture\": \"rice\", \"version\": \"1\"}`"],
    ["A3", "`test_predict_valeur_hors_bornes`", "pH = 15", "422"],
    ["A4", "`test_predict_champ_manquant`", "`ph` absent", "422"],
    ["A5", "`test_demarrage_sans_champion`", "registre vide", "l'API refuse de démarrer, message citant `uv run promote`"],
]
add(TABLE(["N°", "Test", "Situation", "Résultat attendu"], plan, widths=[6, 38, 27, 29], cls="small"))
add(H2("Résultats"))
add(code("""$ uv run pytest -v
tests/test_api.py::test_health PASSED                                    [  3%]
tests/test_api.py::test_predict PASSED                                   [  6%]
…
tests/test_validation.py::test_booleens_refuses_pour_un_float PASSED     [100%]
======================== 30 passed, 1 warning in 36.54s ========================""", "text", "Exécution réelle de la suite de tests", keep=True))
add(TABLE(["Fichier", "Tests", "Réussis", "Durée indicative"], [
    ["`test_validation.py`", "9", "9", "< 0,1 s"],
    ["`test_data.py`", "4", "4", "< 0,1 s"],
    ["`test_train.py`", "1", "1", "≈ 2 s"],
    ["`test_promote.py`", "11", "11", "≈ 25 s (enregistrement de modèles MLflow)"],
    ["`test_api.py`", "5", "5", "≈ 10 s"],
    ["**Total**", "**30**", "**30**", "**≈ 37 s**"],
], widths=[30, 12, 12, 46]))
add(P("L'unique avertissement (`SADeprecationWarning`) vient de MLflow lui-même, pas du projet. Ruff ne signale aucune erreur, et tous les fichiers sont correctement mis en forme."))
add(H2("Ce qui n'est pas (encore) testé"))
add(UL([
    "Les commandes `train` et `tune` de bout en bout, et `log_run` / `log_tuning` : elles demandent les vraies données et un serveur MLflow. Seul l'accord entre leurs validations croisées est testé (`test_train.py`) ; le reste se vérifie en lançant les commandes.",
    "`get_data_version` (empreinte des données et suffixe `-modified`).",
    "La **qualité** du modèle : aucun test ne garantit un score minimal. Un test « le score dépasse 0,95 » serait un bon ajout (voir exercices).",
]))
add(BOX("try", P("Lancez `uv run pytest tests/test_validation.py -v`, puis cassez volontairement une règle dans `validation.py` (par exemple remplacez `>` par `>=` dans la borne `max`). Relancez : quels tests échouent ? Lisez le message d'erreur, puis annulez la modification.")))
add("</section>")

# ============ 17. Qualité & CI
add("<section>")
add(H1("Étape 14 : qualité du code et intégration continue", "Des garde-fous qui travaillent pour vous."))
add(H2("Ruff : vérifier et mettre en forme"))
add(P("**Ruff** analyse le code sans l'exécuter. Il signale les erreurs probables et uniformise la mise en forme. Les règles choisies dans `pyproject.toml` :"))
add(TABLE(["Règles", "Ce qu'elles vérifient", "Exemple rencontré"], [
    ["`F` (Pyflakes)", "imports inutilisés ou en double, variables non définies", "`load_config` importé deux fois dans `api.py`"],
    ["`I` (isort)", "ordre des imports : standard, externes, projet", "`import os` placé après `import subprocess`"],
    ["`E4`, `E7`, `E9`", "erreurs de syntaxe et de style graves", ""],
    ["`SIM`", "code qui peut être simplifié", "deux `with` imbriqués → un seul"],
    ["`RUF`", "règles propres à Ruff", ""],
], widths=[20, 45, 35]))
add(code("""uv run ruff check .            # signale les problèmes
uv run ruff check . --fix      # corrige ce qui peut l'être automatiquement
uv run ruff format .           # met en forme tout le code""", "bash", "Terminal"))
add(P("Dans VS Code, l'extension Ruff et le fichier `.vscode/settings.json` appliquent ces corrections **à chaque enregistrement** (`Cmd+S` / `Ctrl+S`) :"))
add(FILE(".vscode/settings.json", "json"))
add(H2("L'intégration continue (CI)"))
add(BOX("concept", P("L'**intégration continue** consiste à vérifier automatiquement chaque modification envoyée sur le dépôt, sur une machine neuve. Si quelque chose casse, on le sait immédiatement, et on sait quel commit l'a cassé.")))
add(FILE(".github/workflows/ci.yml", "yaml"))
add(FIG(F.fig_ci(), "Les étapes de la CI, exécutées par GitHub Actions à chaque push."))
add(BOX("why", P(
    "`uv sync --locked` échoue si `uv.lock` ne correspond pas à `pyproject.toml` : impossible d'oublier de commiter le fichier de verrouillage. La CI part d'une machine vierge : elle prouve que le projet s'installe et fonctionne **ailleurs que sur votre poste**. C'est l'esprit même du MLOps.",
    "`permissions: contents: read` donne à la CI le minimum de droits : elle peut lire le code, pas le modifier.",
)))
add(BOX("tip", P("Avant chaque commit, lancez en local les trois mêmes commandes que la CI : `uv run ruff check .`, `uv run ruff format --check .` et `uv run pytest`. Si elles passent chez vous, elles passeront en CI.")))
add("</section>")

# ============ 18. Parcours
add("<section>")
add(H1("Rejouer toute la chaîne", "Le parcours complet, de l'installation à la prédiction."))
add(P("Ce parcours reprend toutes les étapes dans l'ordre d'utilisation. Les sorties indiquées sont celles obtenues réellement."))
steps = [
    ("Installer l'environnement", "uv sync", "Installe Python 3.13 si besoin, crée `.venv/` et les dépendances de `uv.lock`."),
    ("Récupérer les données", "uv run dvc pull\nuv run dvc status", "`Data and pipelines are up to date.`"),
    ("Lancer les tests", "uv run pytest", "`30 passed`"),
    ("Démarrer les services", "cp .env.example .env    # renseigner le mot de passe\ndocker compose up -d --build", "PostgreSQL, MLflow (http://localhost:5002) et l'API ; sans champion, l'API s'arrête avec un message clair."),
    ("(Facultatif) Chercher les hyperparamètres", "uv run tune", "`Meilleurs paramètres : {'max_depth': None, 'n_estimators': 200}`"),
    ("Entraîner un candidat", "uv run train", "`Run 4c4afe… enregistré : {'cv_f1_macro_mean': 0.9942…, 'accuracy': 0.9954…}`"),
    ("Promouvoir", "uv run promote", "`Version 1 promue champion (score 0.9943).`"),
    ("Charger le champion dans l'API", "docker compose restart api", "API sur http://127.0.0.1:8000, documentation sur /docs"),
    ("Interroger l'API", "curl http://127.0.0.1:8000/health", "`{\"status\": \"ok\", \"version\": \"1\", \"run_id\": \"4c4afe…\"}`"),
]
for i, (t, c, r) in enumerate(steps, 1):
    add(f'<div class="step keep"><div class="step-num">{i}</div><div class="step-body"><div class="step-title">{md(t)}</div>{code(c, "bash")}<div class="step-result">{md("→ " + r)}</div></div></div>')
add(BOX("try", P("Vérifiez la traçabilité : depuis la réponse de `/health`, retrouvez le run dans l'interface MLflow (recherche par `run_id`), lisez ses étiquettes `git_commit` et `data_md5`, puis comparez-les à `git log` et au fichier `.dvc`.")))
add("</section>")

# ============ 19. Retour d'expérience
add("<section>")
add(H1("Retour d'expérience : les problèmes rencontrés", "Les erreurs sont normales. Ce qui compte, c'est ce qu'elles apprennent."))
add(P("Pendant la construction du projet, plusieurs problèmes sont apparus. Chacun illustre une bonne pratique."))
cases = [
    ("Le fichier .env manquant", "`docker compose` affiche : `The \"POSTGRES_USER\" variable is not set` puis `env file … .env not found`.",
     "Le fichier des secrets n'avait pas été créé sur ce poste : il est volontairement ignoré par Git.",
     "`cp .env.example .env` puis renseigner un mot de passe.",
     "Les secrets ne sont jamais dans le dépôt ; un fichier modèle (`.env.example`) documente ce qu'il faut fournir."),
    ("Deux ports différents pour le même serveur", "Les scripts ne trouvaient pas le serveur MLflow.",
     "`config.yaml` pointait sur le port 5002, alors que `compose.yaml` publiait le port 5001.",
     "Aligner les deux fichiers sur 5002.",
     "Une même information écrite à deux endroits finit par diverger. Quand c'est inévitable, on vérifie leur cohérence (par un test ou une relecture)."),
    ("Un test qui dépendait de l'ordre d'exécution", "Tous les tests passaient… sauf quand on changeait leur ordre.",
     "`mlflow.set_tracking_uri` est un réglage global, qui survivait d'un test à l'autre.",
     "La fixture règle l'adresse au début du test et l'efface à la fin (`yield`).",
     "Un test doit être isolé : même résultat seul, en premier ou en dernier."),
    ("Des imports dans le désordre", "Ruff signalait `I001` (imports non triés) et `F811` (import en double) : la CI aurait échoué.",
     "Des imports ajoutés au fil de l'eau, sans relecture.",
     "`uv run ruff check --fix`, puis le tri automatique à l'enregistrement dans VS Code.",
     "Automatiser ce qui peut l'être : les humains oublient, les outils non."),
    ("Un avertissement de l'éditeur sur un code qui fonctionne", "Pylance : « Variable non autorisée dans l'expression de type » sur `CropInput`.",
     "La classe est créée pendant l'exécution (`create_model`) : l'analyse statique ne peut pas la connaître.",
     "Un commentaire ciblé `# pyright: ignore[reportInvalidTypeForm]`.",
     "Distinguer ce que voit l'éditeur (analyse sans exécution) de ce que fait le programme. Ignorer un avertissement, oui, mais de façon ciblée et en sachant pourquoi."),
    ("Deux scores pour les mêmes réglages", "Pour une même configuration, `tune` et `train` n'évaluaient pas le modèle sur les mêmes plis : les scores pli par pli n'avaient rien à voir.",
     "La façon de découper les plis était écrite deux fois, et différemment : `train` passait `cv=5` (plis sans mélange), `tune` un `StratifiedKFold` avec mélange et graine.",
     "Une seule fonction, `build_cv` dans `data.py`, utilisée par les deux commandes ; un test vérifie qu'elles donnent le même score.",
     "Une règle de mesure doit être unique. Sinon, on compare des chiffres qui ne sont pas obtenus dans les mêmes conditions."),
    ("Une fixture copiée dans deux fichiers", "La même fixture `config` existait dans `test_promote.py` et `test_api.py`.",
     "Le second fichier de tests avait été écrit en copiant le premier.",
     "La fixture a été déplacée dans `tests/conftest.py`, partagé par tous les tests.",
     "Ne pas dupliquer : une correction future ne devra être faite qu'une fois."),
]
for t, sym, cause, fix, lesson in cases:
    add(f'<div class="case keep"><div class="case-title">{md(t)}</div>' + TABLE(["", ""], [["**Symptôme**", sym], ["**Cause**", cause], ["**Correction**", fix], ["**Leçon**", lesson]], widths=[18, 82], cls="case-table") + "</div>")
add("</section>")

# ============ 20. Limites
add("<section>")
add(H1("Limites actuelles et phase 2", "Ce qui manque encore avant une vraie mise en production."))
add(P("L'application de la phase 1 fonctionne **en local**. Voici ce qu'il faudra traiter pour la mettre en production, et quelques améliorations repérées pendant la relecture du code."))
add(H2("Vers la mise en production"))
add(TABLE(["Limite", "Conséquence", "Piste pour la phase 2"], [
    ["Stockage DVC dans un dossier local", "Les données ne sont accessibles que sur un poste", "Stockage partagé (S3, Google Drive, SSH)"],
    ["API en conteneur, sur un seul poste", "Inaccessible depuis l'extérieur, pas de HTTPS", "Déploiement sur un serveur (VPS), proxy inverse avec HTTPS"],
    ["Champion chargé au démarrage", "Une promotion n'est prise en compte qu'au redémarrage", "Rechargement périodique de l'alias, ou redéploiement automatique"],
    ["Pas de surveillance en production", "On ne voit pas si les données reçues changent (dérive)", "Journaliser les requêtes, surveiller les distributions"],
    ["Enchaînement manuel train → promote", "Risque d'oubli, pas de reprise automatique", "Pipeline automatisé (CI/CD, orchestrateur)"],
    ["Pas d'authentification", "N'importe qui sur le réseau peut appeler l'API et le serveur MLflow", "Authentification, HTTPS"],
], widths=[28, 36, 36]))
add(H2("Améliorations repérées dans le code"))
add(UL([
    "`find_candidate_run_id` s'appuie sur l'ordre par défaut de MLflow et filtre les runs en Python ; un filtre `tags.stage = 'candidate'` avec un tri explicite serait plus sûr et plus rapide.",
    "Si le serveur MLflow est arrêté, l'API attend plusieurs minutes avant d'afficher l'erreur brute de MLflow : la connexion (`setup_mlflow`) est faite avant le bloc `try` qui produit le message clair.",
    "L'image de l'API pèse 2,6 Go : elle embarque toutes les dépendances du projet (DVC, matplotlib…). Séparer les dépendances de l'API de celles de l'entraînement l'allégerait nettement.",
]))
add(P("Ces points sont repris dans les exercices du chapitre suivant."))
add("</section>")

# ============ 21. Exercices
add("<section>")
add(H1("Exercices", "Manipuler pour comprendre. Du plus simple au plus ambitieux."))
ex = [
    ("Le schéma protège l'entraînement", "★",
     "Dans `config/schema.yaml`, passez la borne `max` de `ph` à 8. Lancez `uv run train`, puis démarrez l'API et envoyez un pH de 9.",
     "L'entraînement s'arrête avec la liste des valeurs > 8. L'API répond 422. Une seule modification a changé les deux comportements : pourquoi ?"),
    ("Un candidat moins bon", "★",
     "Dans `model.params`, mettez `n_estimators: 20` et `max_depth: 3`. Lancez `uv run train` puis `uv run promote`.",
     "`Candidat non promu : 0.8472 <= 0.9943.` Remettez les réglages d'origine. Comparez les deux runs dans l'interface MLflow."),
    ("Remonter la piste", "★",
     "À partir de `/health`, retrouvez le run du champion dans MLflow, puis son commit et sa version de données.",
     "Utilisez `git show <commit>` et comparez `data_md5` au contenu du fichier `.dvc`."),
    ("Données modifiées", "★★",
     "Modifiez une ligne du CSV, lancez `uv run dvc status` puis `uv run train`. Regardez l'étiquette `data_md5` du nouveau run.",
     "Elle se termine par `-modified`. Restaurez les données avec `uv run dvc checkout`."),
    ("Un test de plus pour l'API", "★★",
     "Écrivez dans `tests/test_api.py` un test qui envoie `N = 12.5` et vérifie la réponse.",
     "422 : `N` est déclaré entier dans le schéma. Votre test doit passer avec `uv run pytest`."),
    ("Un test de qualité", "★★",
     "Écrivez un test qui entraîne le modèle sur le vrai jeu de données et vérifie que l'accuracy sur le test dépasse 0,95.",
     "Ce test a besoin du CSV : comment faire pour qu'il ne fasse pas échouer la CI, où les données ne sont pas disponibles ? (piste : `pytest.mark.skipif`)"),
    ("Casser l'alignement des plis", "★★",
     "Dans `cross_validate_model` (`train.py`), remplacez `cv=build_cv(config)` par `cv=5`, puis lancez `uv run pytest`.",
     "`test_train_et_tune_donnent_le_meme_score` échoue (0,51 contre 0,71 sur ses petites données). Expliquez pourquoi, puis remettez `build_cv`."),
    ("Chercher les candidats proprement", "★★★",
     "Réécrivez `find_candidate_run_id` avec `filter_string=\"tags.stage = 'candidate'\"`, `order_by=[\"attributes.start_time DESC\"]` et `max_results=1`.",
     "Les 11 tests de `test_promote.py` doivent toujours passer : c'est tout l'intérêt de les avoir."),
    ("Une erreur claire quand le serveur est arrêté", "★★★",
     "Arrêtez Docker et lancez l'API. Modifiez `lifespan` pour que le message clair s'affiche rapidement.",
     "Piste : faire la connexion dans le bloc `try`, et réduire les tentatives de MLflow avec la variable `MLFLOW_HTTP_REQUEST_MAX_RETRIES`."),
]
for i, (t, lvl, todo, expect) in enumerate(ex, 1):
    add(f'<div class="exercise keep"><div class="ex-head"><span class="ex-num">Exercice {i}</span> {md(t)} <span class="ex-lvl">{lvl}</span></div>'
        f'<p>{md(todo)}</p><p class="ex-expect"><b>Ce que vous devez observer :</b> {md(expect)}</p></div>')
add("</section>")

# ============ 22. Glossaire
add("<section>")
add(H1("Glossaire"))
gloss = [
    ("Accuracy", "Part des prédictions correctes."),
    ("Alias (MLflow)", "Étiquette mobile posée sur une version de modèle du registre (ici `champion`)."),
    ("API", "Interface qui permet à un programme d'en appeler un autre, ici par HTTP."),
    ("Artefact", "Fichier joint à un run MLflow : modèle, image, rapport, configuration."),
    ("Candidat / champion", "Le candidat est le dernier modèle entraîné ; le champion est celui en service."),
    ("CI (intégration continue)", "Vérification automatique de chaque modification sur une machine neuve."),
    ("Commit", "Enregistrement d'un état du code dans l'historique Git."),
    ("Conteneur, image (Docker)", "Une image décrit un environnement logiciel ; un conteneur est une image en cours d'exécution."),
    ("Docker Compose", "Outil qui lance plusieurs conteneurs décrits dans un fichier `compose.yaml`."),
    ("DVC", "*Data Version Control* : versionne les données à côté de Git."),
    ("Empreinte (hash md5)", "Courte suite de caractères calculée à partir d'un fichier ; change si le fichier change."),
    ("Environnement virtuel", "Dossier (`.venv`) contenant Python et les bibliothèques propres au projet."),
    ("Expérience (MLflow)", "Groupe de runs comparables."),
    ("F1 macro", "Moyenne des scores F1 de chaque classe : chaque classe compte autant."),
    ("Fixture", "Fonction pytest qui prépare ce dont un test a besoin."),
    ("Graine aléatoire", "Valeur de départ qui rend le « hasard » reproductible."),
    ("Hyperparamètre", "Réglage d'un modèle choisi avant l'entraînement (nombre d'arbres, profondeur)."),
    ("Jeu de test", "Données mises de côté, utilisées une seule fois pour estimer la performance finale."),
    ("Lock file", "Fichier de verrouillage des versions exactes (`uv.lock`)."),
    ("Métrique", "Résultat chiffré enregistré dans un run."),
    ("MLOps", "Pratiques qui rendent un projet de ML reproductible, traçable, testé et déployable."),
    ("Paquet (package)", "Code Python organisé pour être installé et importé."),
    ("Pli (fold)", "Une des parts du jeu d'entraînement en validation croisée."),
    ("Promotion", "Désignation d'un nouveau modèle comme champion."),
    ("Pydantic", "Bibliothèque de validation de données utilisée par FastAPI."),
    ("Registre de modèles", "Catalogue des versions de modèles retenues, avec leurs alias."),
    ("Remote (DVC)", "Stockage distant où DVC envoie les données."),
    ("Run", "Une exécution enregistrée dans MLflow."),
    ("Schéma", "Description des données attendues : colonnes, types, bornes."),
    ("Signature", "Description des entrées et sorties d'un modèle."),
    ("Stratification", "Découpage qui conserve les proportions de chaque classe."),
    ("Tag (étiquette)", "Information libre attachée à un run (`data_md5`, `git_commit`, `stage`)."),
    ("Test automatisé", "Fonction qui exécute du code et vérifie le résultat."),
    ("uv", "Outil qui gère Python, l'environnement virtuel et les dépendances."),
    ("Validation croisée", "Évaluation répétée sur plusieurs plis du jeu d'entraînement."),
    ("Volume (Docker)", "Stockage qui survit à l'arrêt des conteneurs."),
    ("YAML", "Format de fichier texte lisible, utilisé pour la configuration."),
]
add(TABLE(["Terme", "Définition"], [[f"**{a}**", b] for a, b in gloss], widths=[28, 72], cls="small"))
add("</section>")

# ============ Annexe
add("<section>")
add(H1("Annexe : commandes et dépannage"))
add(H2("Aide-mémoire des commandes"))
add(TABLE(["Commande", "Effet"], [
    ["`uv sync`", "Installer l'environnement depuis `uv.lock`"],
    ["`uv add <paquet>` / `uv add --dev <paquet>`", "Ajouter une dépendance (de développement)"],
    ["`uv run dvc pull` / `uv run dvc status`", "Récupérer / contrôler les données"],
    ["`docker compose up -d --build` / `docker compose down`", "Démarrer / arrêter PostgreSQL, MLflow et l'API"],
    ["`uv run tune`", "Rechercher les hyperparamètres"],
    ["`uv run train`", "Entraîner un modèle candidat"],
    ["`uv run promote`", "Comparer au champion et promouvoir"],
    ["`docker compose restart api`", "Recharger le champion dans l'API (http://127.0.0.1:8000/docs)"],
    ["`uv run fastapi dev`", "Lancer l'API hors conteneur, pour développer"],
    ["`uv run pytest`", "Lancer les tests"],
    ["`uv run ruff check . --fix` / `uv run ruff format .`", "Corriger et mettre en forme le code"],
], widths=[45, 55]))
add(H2("Dépannage"))
add(TABLE(["Message", "Cause", "Solution"], [
    ["`env file … .env not found`", "Fichier des secrets absent", "`cp .env.example .env`, renseigner le mot de passe"],
    ["Connexion refusée sur le port 5002", "Serveur MLflow arrêté ou port différent", "`docker compose ps` ; comparer `config.yaml` et `compose.yaml`"],
    ["`Alias champion introuvable …` au démarrage de l'API", "Aucun modèle promu", "`uv run train` puis `uv run promote`"],
    ["`Some of the cache files do not exist` (DVC)", "Stockage DVC absent sur ce poste", "Copier le dossier de stockage, ou replacer le CSV puis `dvc add`"],
    ["`Données non conformes au schéma`", "Le CSV ne respecte pas `schema.yaml`", "Lire la liste des erreurs ; corriger les données ou le schéma"],
    ["`FileNotFoundError: 'config/config.yaml'` (notebook)", "Le notebook ne tourne pas depuis la racine", "Première cellule : `os.chdir(\"..\")` si on est dans `notebooks/`"],
    ["`UntrustedTypesFoundException`", "Format skops de MLflow", "`skops_trusted_types=[\"sklearn.tree._tree.Tree\"]`"],
    ["Ruff `I001`, `F401`, `F811`", "Imports mal triés, inutilisés ou en double", "`uv run ruff check . --fix`"],
], widths=[34, 30, 36], cls="small"))
add("</section>")

# ----------------------------------------------------------------- page HTML

CSS = (HERE / "guide.css").read_text(encoding="utf-8")
PYG = HtmlFormatter(style="friendly").get_style_defs(".code pre")


def toc_html(pages):
    rows = []
    rows.append(f'<div class="toc-row front"><a href="#intro">Avant de commencer</a><span class="dots"></span><span class="pg">{pages.get("intro", "")}</span></div>')
    for cid, title in CHAPTERS:
        rows.append(f'<div class="toc-row"><a href="#{cid}">{md(title)}</a><span class="dots"></span><span class="pg">{pages.get(cid, "")}</span></div>')
    return "".join(rows)


def cover():
    return f"""<section class="cover">
<div class="cover-top">Support de cours · Phase 1 : en local</div>
<div class="cover-title">Du notebook<br/>à l'application</div>
<div class="cover-sub">La démarche MLOps pas à pas</div>
<div class="cover-desc">Recommandation de cultures avec uv, DVC, MLflow, FastAPI et pytest</div>
<div class="cover-svg">{F.fig_cycle()}</div>
<div class="cover-foot">Guide de l'étudiant · Novembre 2026</div>
</section>"""


def build(pages):
    body = "\n".join(S)
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Du notebook à l'application : la démarche MLOps pas à pas</title>
<style>{CSS}\n{PYG}</style></head><body>
{cover()}
<section class="toc"><h1 class="unnumbered">Sommaire</h1>{toc_html(pages)}</section>
{body}
</body></html>"""


def render(html_text):
    OUT_HTML.write_text(html_text, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=5000",
                    f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()], check=True, capture_output=True)


def find_pages():
    from pypdf import PdfReader
    reader = PdfReader(str(OUT_PDF))
    texts = [re.sub(r"\s+", " ", p.extract_text() or "") for p in reader.pages]
    pages = {}
    targets = [("intro", "Avant de commencer")] + [(cid, t.split(". ", 1)[1]) for cid, t in CHAPTERS]
    start = 2  # après couverture et sommaire
    for cid, title in targets:
        key = re.sub(r"\s+", " ", title)[:28]
        for i in range(start, len(texts)):
            if key in texts[i]:
                pages[cid] = i + 1
                start = i
                break
    return pages, len(texts)


render(build({}))
pages, n = find_pages()
render(build(pages))
pages2, n2 = find_pages()
if pages2 != pages:
    render(build(pages2))
    pages2, n2 = find_pages()
print("pages:", n2, pages2)
