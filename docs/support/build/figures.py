"""Schémas du guide (SVG)."""

from diagrams import (
    FOREST, GREY, INK, LINE, MOSS, MOSS_BG, RED, WHEAT, WHEAT_BG, WHITE, BLUE, BLUE_BG,
    arrow, box, circle, path_arrow, rect, svg, text,
)


def fig_pillars():
    cols = [
        ("Code", "Git", "historique de chaque\nmodification", "main"),
        ("Environnement", "uv + uv.lock", "mêmes versions\nsur chaque poste", "main"),
        ("Données", "DVC", "version exacte du\nfichier utilisé", "main"),
        ("Expériences\net modèles", "MLflow", "paramètres, scores,\nmodèles, registre", "main"),
    ]
    els = []
    w, gap, x0 = 172, 24, 8
    for i, (what, tool, why, st) in enumerate(cols):
        x = x0 + i * (w + gap)
        els.append(box(x, 10, w, 62, what, style="soft", size=15))
        els.append(arrow(x + w / 2, 74, x + w / 2, 96, color=GREY))
        els.append(box(x, 98, w, 46, tool, style="main", size=16))
        els.append(text(x + w / 2, 166, why.split("\n")[0], size=12, color=GREY))
        els.append(text(x + w / 2, 182, why.split("\n")[1], size=12, color=GREY))
    els.append(rect(8, 200, 760, 40, WHEAT_BG, WHEAT, rx=10))
    els.append(text(388, 225, "Qualité : tests automatisés (pytest) + vérification du style (Ruff) + intégration continue (GitHub Actions)", size=13, color=INK, weight="bold"))
    return svg(776, 248, *els)


def fig_cycle():
    els = []
    # config au-dessus
    els.append(rect(10, 8, 756, 40, MOSS_BG, MOSS, rx=10, dashed=True))
    els.append(text(388, 33, "config/config.yaml  +  config/schema.yaml : tous les réglages, lus par chaque étape", size=13, weight="bold"))
    y1, h = 78, 92
    row1 = [
        ("1. Données", "data/raw/*.csv\nversionnées par DVC", "soft"),
        ("2. Validation", "schema.yaml\nvalidation.py", "soft"),
        ("3. Découpage", "data.py\n80 % / 20 %", "soft"),
        ("4. Entraînement", "train.py · tune.py\nvalidation croisée", "soft"),
    ]
    w, gap = 170, 25
    for i, (t, s, st) in enumerate(row1):
        x = 10 + i * (w + gap)
        els.append(box(x, y1, w, h, t, s, style=st, size=14))
        if i < 3:
            els.append(arrow(x + w + 2, y1 + h / 2, x + w + gap - 2, y1 + h / 2))
    y2 = 222
    row2 = [
        ("8. Utilisateur", "requête JSON\n→ culture conseillée", "file"),
        ("7. API", "api.py\nFastAPI", "main"),
        ("6. Promotion", "promote.py\nalias « champion »", "soft"),
        ("5. Suivi", "tracking.py\nserveur MLflow", "soft"),
    ]
    for i, (t, s, st) in enumerate(row2):
        x = 10 + i * (w + gap)
        els.append(box(x, y2, w, h, t, s, style=st, size=14))
        if i < 3:
            els.append(arrow(x + w + gap - 2, y2 + h / 2, x + w + 2, y2 + h / 2))
    # descente 4 -> 5
    x4 = 10 + 3 * (w + gap) + w / 2
    els.append(arrow(x4, y1 + h + 2, x4, y2 - 2))
    els.append(rect(10, 334, 756, 36, WHEAT_BG, WHEAT, rx=10))
    els.append(text(388, 357, "À chaque modification : tests (tests/) + Ruff + CI (.github/workflows/ci.yml)", size=13, weight="bold"))
    return svg(776, 378, *els)


def fig_modules():
    els = []
    top = [("train.py", "uv run train"), ("tune.py", "uv run tune"), ("promote.py", "uv run promote"), ("api.py", "uv run fastapi dev")]
    w, gap = 166, 30
    xs = [12 + i * (w + gap) for i in range(4)]
    for x, (t, s) in zip(xs, top):
        els.append(box(x, 34, w, 58, t, s, style="main", size=15))
    els.append(text(12, 22, "Points d'entrée (commandes)", size=12, color=GREY, anchor="start", weight="bold"))
    mid_y = 172
    data_x, track_x, mw = 150, 452, 176
    els.append(text(12, mid_y - 12, "Modules de service", size=12, color=GREY, anchor="start", weight="bold"))
    els.append(box(data_x, mid_y, mw, 58, "data.py", "charger · découper · md5", style="soft", size=15, mono_sub=False))
    els.append(box(track_x, mid_y, mw, 58, "tracking.py", "connexion · enregistrer les runs", style="soft", size=15, mono_sub=False))
    bot_y = 300
    els.append(text(12, bot_y - 12, "Briques de base", size=12, color=GREY, anchor="start", weight="bold"))
    els.append(box(data_x, bot_y, mw, 54, "validation.py", "contrôle du schéma", style="file", size=15, mono_sub=False))
    els.append(box(track_x, bot_y, mw, 54, "config.py", "lire les fichiers YAML", style="file", size=15, mono_sub=False))
    dc, tc = data_x + mw / 2, track_x + mw / 2
    # commandes -> services
    els.append(arrow(xs[0] + 60, 94, dc - 30, mid_y - 2))
    els.append(arrow(xs[0] + 120, 94, tc - 50, mid_y - 2))
    els.append(arrow(xs[1] + 60, 94, dc + 20, mid_y - 2))
    els.append(arrow(xs[1] + 110, 94, tc - 20, mid_y - 2))
    els.append(arrow(xs[2] + 80, 94, tc + 20, mid_y - 2))
    els.append(arrow(xs[3] + 60, 94, tc + 60, mid_y - 2))
    # services -> base
    els.append(arrow(dc, mid_y + 60, dc, bot_y - 2))
    els.append(arrow(track_x - 2, mid_y + 29, data_x + mw + 2, mid_y + 29, label="get_data_version", label_dy=-7))
    els.append(arrow(tc, mid_y + 60, tc, bot_y - 2))
    els.append(arrow(data_x + mw + 2, bot_y + 27, track_x - 2, bot_y + 27, label="load_yaml, ROOT", label_dy=-7))
    els.append(text(388, 382, "Une flèche A → B signifie « A importe B ». Les dépendances descendent toujours : pas de boucle.", size=12, color=GREY, italic=True))
    return svg(776, 392, *els)


def fig_git_dvc():
    els = []
    # Git
    els.append(rect(8, 30, 220, 250, "#F4F6F3", LINE, rx=12))
    els.append(text(118, 20, "Dépôt Git (GitHub)", size=14, weight="bold", color=FOREST))
    for i, (f, s_) in enumerate([("src/ · tests/ · config/", "code et réglages"), ("pyproject.toml · uv.lock", "environnement"), ("crop_recommendation.csv.dvc", "md5 : 5e743dd4… · 150 Ko"), ("data/raw/.gitignore", "« ignore le CSV »")]):
        st = "wheat" if "dvc" in f else "file"
        els.append(box(20, 48 + i * 56, 196, 46, f, s_, style=st, size=11.5, sub_size=10))
    # Poste
    els.append(rect(288, 30, 200, 250, MOSS_BG, MOSS, rx=12))
    els.append(text(388, 20, "Poste de travail", size=14, weight="bold", color=FOREST))
    els.append(box(300, 56, 176, 70, "data/raw/", "crop_recommendation.csv\n(le vrai fichier)", style="file", size=13, sub_size=10))
    els.append(box(300, 186, 176, 70, ".dvc/cache/", "copie rangée\npar empreinte md5", style="file", size=13, sub_size=10))
    els.append(arrow(388, 128, 388, 184, label="dvc add", label_dx=32, label_dy=4))
    # Remote
    els.append(rect(548, 30, 220, 250, BLUE_BG, BLUE, rx=12))
    els.append(text(658, 20, "Stockage DVC (remote)", size=14, weight="bold", color=BLUE))
    els.append(text(658, 74, "Aujourd'hui : un dossier", size=11.5, color=GREY))
    els.append(text(658, 90, "à côté du dépôt.", size=11.5, color=GREY))
    els.append(text(658, 116, "Phase 2 : S3, Google Drive,", size=11.5, color=GREY))
    els.append(text(658, 132, "serveur SSH…", size=11.5, color=GREY))
    els.append(box(560, 186, 196, 70, "crop_recommendation_\nstorage/", style="file", size=12.5))
    # flèches Git <-> poste
    els.append(arrow(286, 78, 230, 78, label="git push", label_dy=-7))
    els.append(arrow(230, 110, 286, 110, label="git pull", label_dy=17))
    # flèches cache <-> remote
    els.append(arrow(478, 206, 558, 206, label="dvc push", label_dy=-7))
    els.append(arrow(558, 238, 478, 238, label="dvc pull", label_dy=17))
    els.append(text(388, 306, "Git garde l'étiquette (le fichier .dvc, quelques lignes) ; DVC range et transporte le contenu.", size=12.5, color=GREY, italic=True))
    return svg(776, 316, *els)


def fig_split():
    els = []
    X, W = 20, 736
    wt = W * 0.8
    els.append(text(388, 18, "2 200 lignes (100 par culture), découpage stratifié avec la graine 42", size=13, weight="bold"))
    els.append(rect(X, 30, wt, 44, MOSS, rx=6))
    els.append(rect(X + wt + 4, 30, W - wt - 4, 44, WHEAT, rx=6))
    els.append(text(X + wt / 2, 58, "Entraînement : 1 760 lignes (80 %)", size=14, color=INK, weight="bold"))
    els.append(text(X + wt + (W - wt) / 2 + 2, 58, "Test : 440 lignes", size=14, color=WHITE, weight="bold"))
    els.append(text(X, 104, "Validation croisée à 5 plis, sur l'entraînement seulement :", size=13, anchor="start", weight="bold", color=FOREST))
    fw = wt / 5
    for r in range(5):
        y = 116 + r * 30
        for c in range(5):
            val = c == r
            els.append(rect(X + c * fw + 2, y, fw - 4, 24, WHITE if val else MOSS_BG, FOREST if val else MOSS, rx=4))
            if val:
                els.append(text(X + c * fw + fw / 2, y + 17, "évaluation", size=11.5, color=FOREST, weight="bold"))
            else:
                els.append(text(X + c * fw + fw / 2, y + 17, "apprentissage", size=11, color=GREY))
        els.append(text(X + wt + 14, y + 17, f"pli {r + 1} → score", size=12, color=GREY, anchor="start"))
    els.append(text(X, 286, "Score de validation croisée = moyenne des 5 scores (cv_f1_macro_mean). C'est lui qui sert à comparer et à choisir.", size=12.5, anchor="start", color=INK))
    els.append(text(X, 306, "Le jeu de test reste dans le coffre : il sert une seule fois, à la fin, pour estimer la performance réelle.", size=12.5, anchor="start", color=WHEAT, weight="bold"))
    return svg(776, 316, *els).replace('<text x="681.6" y="196"', '<text x="681.6" y="196"')


def fig_mlflow():
    els = []
    els.append(rect(8, 8, 760, 384, "#F7F9F6", LINE, rx=14))
    els.append(text(24, 32, "Serveur de suivi MLflow  (http://localhost:5002)", size=14, weight="bold", color=FOREST, anchor="start"))
    # Expérience
    els.append(rect(24, 48, 420, 330, WHITE, MOSS, rx=12))
    els.append(text(40, 72, "Expérience « crop-recommendation »", size=13.5, weight="bold", anchor="start"))
    els.append(box(40, 86, 180, 46, "Run « train »", "stage = candidate", style="soft", size=13))
    els.append(box(40, 142, 180, 46, "Run « train »", "stage = candidate", style="soft", size=13))
    els.append(box(40, 198, 180, 46, "Run « tuning »", "run parent", style="soft", size=13))
    for i in range(3):
        els.append(box(64 + i * 52, 256, 46, 30, f"cv_{i}", style="file", size=11))
    els.append(text(64 + 3 * 52 + 18, 276, "… cv_11", size=11, color=GREY, anchor="start"))
    els.append(path_arrow("M130,246 L130,254", color=GREY))
    # contenu d'un run
    els.append(rect(240, 86, 190, 280, MOSS_BG, MOSS, rx=10))
    els.append(text(335, 106, "Contenu d'un run", size=13, weight="bold"))
    items = [("Paramètres", "n_estimators, max_depth…"), ("Métriques", "cv_f1_macro_mean, accuracy…"), ("Étiquettes (tags)", "data_md5, git_commit, stage"), ("Artefacts", "config, schéma, rapport,\nmatrice de confusion"), ("Modèle", "modèle + signature")]
    for i, (t, s) in enumerate(items):
        els.append(box(250, 118 + i * 49, 170, 43, t, s, style="file", size=12, sub_size=9.5))
    els.append(arrow(222, 109, 248, 109, color=GREY))
    # Registre
    els.append(rect(470, 48, 282, 330, WHITE, BLUE, rx=12))
    els.append(text(486, 72, "Registre de modèles", size=13.5, weight="bold", anchor="start", color=BLUE))
    els.append(box(486, 86, 250, 46, "Modèle « crop-recommendation »", style="blue", size=12.5))
    els.append(box(500, 150, 100, 40, "Version 1", style="file", size=12.5))
    els.append(box(500, 204, 100, 40, "Version 2", style="file", size=12.5))
    els.append(box(500, 258, 100, 40, "Version 3", style="file", size=12.5))
    els.append(box(636, 204, 100, 40, "@champion", style="main", size=13))
    els.append(arrow(634, 224, 602, 224, color=FOREST))
    els.append(text(611, 330, "L'alias est une étiquette mobile :", size=11.5, color=GREY))
    els.append(text(611, 346, "promote la déplace vers la", size=11.5, color=GREY))
    els.append(text(611, 362, "meilleure version.", size=11.5, color=GREY))
    els.append(path_arrow("M422,335 C462,335 462,236 498,226", color=FOREST, dashed=True))
    els.append(text(457, 389, "promote : register_model", size=10.5, color=FOREST, italic=True))
    return svg(776, 400, *els)


def fig_trace():
    els = []
    els.append(box(8, 92, 150, 70, "Prédiction", '{"culture": "rice",\n "version": "1"}', style="main", size=14, sub_size=10))
    els.append(arrow(160, 127, 192, 127))
    els.append(box(194, 92, 140, 70, "Registre", "version 1\n→ run_id 4c4afe…", style="blue", size=14, sub_size=10.5))
    els.append(arrow(336, 127, 368, 127))
    els.append(box(370, 82, 160, 90, "Run MLflow", "paramètres, scores,\nconfig.yaml,\nschema.yaml", style="soft", size=14, sub_size=10.5))
    els.append(arrow(532, 110, 572, 52))
    els.append(arrow(532, 144, 572, 200))
    els.append(box(574, 10, 194, 84, "git_commit", "7e8606e…\n→ git checkout 7e8606e\n= le code exact", style="wheat", size=13.5, sub_size=10.5))
    els.append(box(574, 160, 194, 84, "data_md5", "5e743dd4…\n→ fichier .dvc + dvc checkout\n= les données exactes", style="wheat", size=13.5, sub_size=10.5))
    els.append(text(388, 268, "De n'importe quelle prédiction, on remonte au code, aux données et aux réglages qui l'ont produite.", size=12.5, color=GREY, italic=True))
    return svg(776, 278, *els)


def fig_docker():
    els = []
    els.append(rect(8, 30, 240, 300, MOSS_BG, MOSS, rx=12))
    els.append(text(128, 20, "Votre poste (hors Docker)", size=13.5, weight="bold", color=FOREST))
    els.append(box(22, 52, 212, 60, "uv run train / tune", "envoient des runs", style="file", size=13, mono_sub=False))
    els.append(box(22, 140, 212, 60, "uv run promote", "gère le registre", style="file", size=13, mono_sub=False))
    els.append(box(22, 228, 212, 60, "Navigateur, curl", "interface MLflow, API", style="file", size=13, mono_sub=False))
    els.append(rect(290, 30, 478, 300, BLUE_BG, BLUE, rx=12))
    els.append(text(529, 20, "Docker Compose (compose.yaml)", size=13.5, weight="bold", color=BLUE))
    els.append(box(306, 46, 190, 70, "api", "Dockerfile.api\nfastapi run · port 8000", style="wheat", size=15, sub_size=10.5))
    els.append(text(512, 74, "charge le champion", size=11.5, color=GREY, anchor="start"))
    els.append(text(512, 90, "au démarrage", size=11.5, color=GREY, anchor="start"))
    els.append(box(306, 158, 190, 82, "mlflow", "Dockerfile.mlflow\nport 5000 · --allowed-hosts", style="main", size=15, sub_size=10.5))
    els.append(box(566, 158, 186, 82, "postgres", "postgres:18 · port 5432\nidentifiants : .env", style="blue", size=15, sub_size=10.5))
    els.append(arrow(401, 118, 401, 156, label="http://mlflow:5000", label_dx=62, label_dy=4))
    els.append(arrow(498, 199, 564, 199, label="SQL", label_dy=-8))
    els.append(box(306, 268, 190, 48, "volume mlflow_artifacts", "modèles, images", style="file", size=11.5, sub_size=10))
    els.append(box(566, 268, 186, 48, "volume postgres_data", "scores, registre", style="file", size=11.5, sub_size=10))
    els.append(arrow(401, 242, 401, 266))
    els.append(arrow(659, 242, 659, 266))
    els.append(arrow(236, 82, 304, 190, color=FOREST))
    els.append(arrow(236, 170, 304, 200, color=FOREST))
    els.append(arrow(236, 250, 304, 212, color=FOREST))
    els.append(arrow(236, 244, 304, 96, color=FOREST))
    els.append(text(388, 352, "Ports publiés sur 127.0.0.1 seulement : 5002 → mlflow (5000), 8000 → api (8000).", size=12, color=GREY, italic=True))
    return svg(776, 362, *els)


def fig_promote():
    els = []
    cx, w = 40, 300
    ox, ow = 470, 290
    q = [
        ("Existe-t-il un run « candidat » ?", "le plus récent avec stage = candidate"),
        ("A-t-il la métrique cv_f1_macro_mean ?", None),
        ("Existe-t-il déjà un champion ?", None),
        ("Le candidat est-il déjà le champion ?", "même run_id"),
        ("Score candidat > score champion ?", "(ou le champion n'a pas de score)"),
    ]
    outs = [
        ("non", "Message : lancer d'abord uv run train", "red"),
        ("non", "Message : métrique absente", "red"),
        ("non", "PROMOUVOIR", "main"),
        ("oui", "Rien à faire : déjà champion", "ghostbox"),
        ("non", "Champion conservé (non promu)", "red"),
    ]
    els.append(box(cx + 60, 6, 180, 38, "uv run promote", style="main", size=14, mono_sub=True))
    y0, step, h = 66, 82, 54
    down = [None, "oui", "oui", "oui", "non"]  # réponse qui mène à la question suivante
    for i, ((t, s), (lab, o, st)) in enumerate(zip(q, outs)):
        y = y0 + i * step
        start = 46 if i == 0 else y - step + h + 2
        els.append(arrow(cx + w / 2, start, cx + w / 2, y - 2, label=down[i], label_dx=18, label_dy=4))
        els.append(box(cx, y, w, h, t, s, style="wheat", size=13, sub_size=10.5, mono_sub=False))
        style = "file" if st == "ghostbox" else st
        els.append(box(ox, y + 6, ow, h - 12, o, style=style, size=13))
        els.append(arrow(cx + w + 2, y + h / 2, ox - 2, y + h / 2, label=lab, label_dy=-7))
    y_last = y0 + 4 * step
    els.append(arrow(cx + w / 2, y_last + h + 2, cx + w / 2, y_last + h + 34, label="oui", label_dx=18, label_dy=4))
    els.append(box(cx, y_last + h + 36, w, 46, "PROMOUVOIR", "register_model + alias champion", style="main", size=14, sub_size=10.5))
    return svg(776, y_last + h + 92, *els)


def fig_api():
    els = []
    els.append(text(10, 18, "Au démarrage (lifespan), une seule fois :", size=13, weight="bold", anchor="start", color=FOREST))
    steps = [("config.yaml", "lire les réglages"), ("setup_mlflow", "se connecter"), ("alias champion", "→ version n"), ("load_model", "charger en mémoire"), ("app.state", "model, version,\nrun_id")]
    w, gap = 136, 19
    for i, (t, s) in enumerate(steps):
        x = 10 + i * (w + gap)
        els.append(box(x, 30, w, 58, t, s, style="soft", size=13, sub_size=10.5, mono_sub=False))
        if i < 4:
            els.append(arrow(x + w + 1, 59, x + w + gap - 1, 59))
    els.append(text(10, 126, "À chaque requête POST /predict :", size=13, weight="bold", anchor="start", color=FOREST))
    req = [("Requête JSON", "7 mesures", "file"), ("Validation", "CropInput (Pydantic)\nbornes de schema.yaml", "wheat"), ("Tableau float64", "pd.DataFrame", "soft"), ("model.predict", "modèle du champion", "soft"), ("Réponse JSON", "culture + version", "main")]
    for i, (t, s, st) in enumerate(req):
        x = 10 + i * (w + gap)
        els.append(box(x, 138, w, 62, t, s, style=st, size=13, sub_size=10, mono_sub=False))
        if i < 4:
            els.append(arrow(x + w + 1, 169, x + w + gap - 1, 169))
    vx = 10 + 1 * (w + gap) + w / 2
    els.append(arrow(vx, 202, vx, 236, color=RED, label="invalide", label_dx=30, label_dy=4))
    els.append(box(vx - 100, 238, 200, 40, "Erreur 422 + détail", style="red", size=13))
    els.append(text(560, 262, "Le modèle n'est jamais appelé avec des données invalides.", size=12, color=GREY, italic=True))
    return svg(776, 288, *els)


def fig_tests():
    els = []
    rows = [
        ("test_validation.py", "9 tests", "validation.py", "règles du schéma"),
        ("test_data.py", "4 tests", "data.py", "variables, découpage, plis"),
        ("test_train.py", "1 test", "train.py + tune.py", "mêmes plis, même score"),
        ("test_promote.py", "11 tests", "promote.py", "règle de promotion"),
        ("test_api.py", "5 tests", "api.py", "routes et validation"),
    ]
    for i, (t, n, m, what) in enumerate(rows):
        y = 10 + i * 62
        els.append(box(10, y, 210, 50, t, n, style="wheat", size=13.5, sub_size=11, mono_sub=False))
        els.append(arrow(222, y + 25, 300, y + 25, label="vérifie", label_dy=-7))
        els.append(box(302, y, 190, 50, m, what, style="soft", size=13.5, sub_size=11, mono_sub=False))
    els.append(rect(540, 10, 226, 298, BLUE_BG, BLUE, rx=12))
    els.append(text(653, 36, "tests/conftest.py", size=13.5, weight="bold", color=BLUE, mono=True))
    lines = ["fixture « config » partagée :", "", "• base MLflow SQLite", "  neuve pour chaque test", "• dossier temporaire", "• aucun serveur requis", "• état remis à zéro", "  après le test"]
    for i, l in enumerate(lines):
        els.append(text(556, 62 + i * 21, l, size=12, anchor="start", color=INK))
    els.append(path_arrow("M538,214 C516,214 516,221 494,221", color=BLUE, dashed=True))
    els.append(path_arrow("M538,276 C516,276 516,283 494,283", color=BLUE, dashed=True))
    return svg(776, 320, *els)


def fig_ci():
    els = []
    steps = [("git push", None, "file"), ("checkout", "récupère le code", "soft"), ("setup-uv", "installe uv", "soft"), ("uv sync\n--locked", "environnement exact", "soft"), ("ruff check", "erreurs, imports", "soft"), ("ruff format\n--check", "mise en forme", "soft"), ("pytest", "30 tests", "soft"), ("✓ / ✗", "badge du commit", "main")]
    w, gap = 84, 11
    for i, (t, s, st) in enumerate(steps):
        x = 4 + i * (w + gap)
        els.append(box(x, 26, w, 70, t, s, style=st, size=11.5, sub_size=9, mono_sub=False, rx=8))
        if i < len(steps) - 1:
            els.append(arrow(x + w + 1, 61, x + w + gap - 1, 61))
    els.append(text(388, 14, "GitHub Actions (.github/workflows/ci.yml) — à chaque push et pull request, sur une machine neuve", size=12, color=GREY, italic=True))
    els.append(text(388, 118, "Une seule étape en échec → le commit est marqué en rouge. On corrige avant de continuer.", size=12, color=GREY, italic=True))
    return svg(776, 126, *els)


TUNING = [
    ("200", "None", 0.9943, 0.0048), ("100", "10", 0.9943, 0.0060), ("100", "None", 0.9937, 0.0061),
    ("50", "None", 0.9931, 0.0087), ("200", "10", 0.9931, 0.0065), ("50", "10", 0.9930, 0.0102),
    ("200", "5", 0.9884, 0.0097), ("100", "5", 0.9755, 0.0154), ("50", "5", 0.9753, 0.0157),
    ("200", "3", 0.9047, 0.0143), ("100", "3", 0.8944, 0.0289), ("50", "3", 0.8841, 0.0148),
]


def fig_tuning():
    els = []
    lo, hi = 0.85, 1.0
    X0, W = 220, 420
    def sx(v):
        return X0 + (v - lo) / (hi - lo) * W
    for t in (0.85, 0.90, 0.95, 1.0):
        x = sx(t)
        els.append(f'<line x1="{x}" y1="16" x2="{x}" y2="{16 + 12 * 26}" stroke="{LINE}" stroke-width="1"/>')
        els.append(text(x, 16 + 12 * 26 + 18, f"{t:.2f}".replace(".", ","), size=11.5, color=GREY))
    for i, (n, d, m, s) in enumerate(TUNING):
        y = 20 + i * 26
        best = i == 0
        col = FOREST if best else (MOSS if m > 0.98 else WHEAT)
        els.append(text(X0 - 10, y + 14, f"{n} arbres · profondeur {'illimitée' if d == 'None' else d}", size=12, anchor="end", color=INK, weight="bold" if best else "normal"))
        els.append(rect(X0, y, sx(m) - X0, 18, col, rx=3))
        els.append(text(sx(m) + 8, y + 14, f"{m:.4f}".replace(".", ",") + f"  (± {s:.3f})".replace(".", ","), size=11.5, anchor="start", color=INK))
    els.append(text(X0 + W / 2, 16 + 12 * 26 + 40, "cv_f1_macro_mean (axe tronqué à 0,85 pour voir les écarts)", size=11.5, color=GREY, italic=True))
    return svg(776, 16 + 12 * 26 + 50, *els)
