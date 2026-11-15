# Génération des supports de cours

Ce dossier produit les supports de `docs/support/` :

| Fichier produit | Générateur |
|---|---|
| `seance1_demarche_mlops.pptx` | `build_seance1.js` a produit la première version. **Le fichier a depuis été retouché dans PowerPoint : il est la référence et se modifie directement ; ne pas le régénérer.** |
| `cours_mlops_phase1.pptx` | `build_deck.js` (pptxgenjs) : toute la phase 1, en local |
| `guide_mlops_phase1.pdf` | `build_guide.py` (HTML + SVG, mis en page par Google Chrome) |

## Fichiers

| Fichier | Rôle |
|---|---|
| `deck_lib.js` | Commun aux diapositives : thème, mises en page, outils de dessin (boîtes, flèches, code, tableaux…) |
| `build_seance1.js` | Diapositives d'ouverture de la séance 1, avec les notes du formateur |
| `build_deck.js` | Diapositives de la phase 1, avec les notes du formateur |
| `apply_theme.js` | Écrit les couleurs du thème dans le `.pptx` (appelé par `deck_lib.js`) |
| `build_guide.py` | Texte du guide, chapitre par chapitre ; sommaire numéroté en deux passes |
| `figures.py` | Schémas du guide (SVG) |
| `diagrams.py` | Outils de dessin SVG (boîtes, flèches, textes) |
| `guide.css` | Mise en page du guide (A4, encadrés, code, tableaux) |
| `collect_results.py` | Relance toute la chaîne sur une base MLflow temporaire et affiche les résultats cités |
| `render_pages.py` | Convertit un PDF en images, pour la relecture visuelle |
| `assets/confusion_matrix.png` | Matrice de confusion du candidat, reprise dans les deux supports |

Le code montré dans le guide est lu directement dans les fichiers du projet : il se met à jour tout seul.
Les **résultats** (scores, sorties des commandes, réponses de l'API, nombre de tests) sont écrits dans le texte :
il faut les reporter à la main après une modification du code.

## Mettre à jour après une modification du code

Prérequis : Node.js, Google Chrome (`/Applications/Google Chrome.app`), l'environnement du projet (`uv sync`).

```bash
cd docs/support/build
npm install                                            # une seule fois

# 1. Recalculer les résultats (n'utilise pas le serveur MLflow)
uv run --project ../../.. python collect_results.py

# 2. Reporter les valeurs qui ont changé dans build_guide.py et build_deck.js
#    (chercher par exemple 0,9943, 0.8472, 4c4afe, 30 passed…)

# 3. Régénérer les supports
node build_deck.js
uv run --project ../../.. --with pypdf python build_guide.py
```

## Relecture visuelle

```bash
uv run --with pypdfium2 --with pillow python render_pages.py ../guide_mlops_phase1.pdf qa/g 1.3
```

Les images (pages et planches de 6 pages) sont écrites dans `qa/`, ignoré par Git.
Pour les diapositives, exporter d'abord le `.pptx` en PDF (PowerPoint ou Keynote), puis utiliser la même commande.

## Remarques

- **Avant de régénérer un `.pptx`, vérifier qu'il n'a pas été retouché dans PowerPoint** (`git status docs/support`) : la régénération écraserait ces retouches. Si c'est le cas, les reporter dans le générateur, ou modifier directement le `.pptx`.
- Ce dossier est exclu de Ruff (`[tool.ruff] extend-exclude` dans `pyproject.toml`) : ce n'est pas du code de l'application.
- Les graphiques des diapositives sont dessinés en formes, et non en graphiques natifs : Keynote n'affiche pas les graphiques produits par pptxgenjs.
