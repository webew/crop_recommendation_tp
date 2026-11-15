// Support de présentation : la démarche MLOps (phase 1, en local)
const path = require("path");
const fs = require("fs");
const { makeDeck, HEX } = require("./deck_lib.js");

const REPO = path.resolve(__dirname, "..", "..", "..");
const OUT = process.argv[2] || path.join(__dirname, "..", "cours_mlops_phase1.pptx");
const RUN = path.join(__dirname, "assets");

const {
  pres, C, icon, oname, txt, box, arrow, code, iconCircle, iconRow, card, numCircle, stat, table, sub, hbars,
  section, content, divider, currentSection, save,
} = makeDeck({ title: "Du notebook à l'application : la démarche MLOps", subject: "Support de cours, phase 1 (en local)" });

// =================================================================== DIAPOSITIVES
async function build() {
  // ---------------------------------------------------------------- Ouverture
  section("Ouverture");
  {
    const s = pres.addSlide({ masterName: "TITRE", sectionTitle: currentSection() });
    s.addText("Du notebook à l'application", { placeholder: "title" });
    s.addText("La démarche MLOps pas à pas · Phase 1 : en local", { placeholder: "body" });
    const tools = [["FaBoxOpen", "uv"], ["FaDatabase", "DVC"], ["FaFlask", "MLflow"], ["FaBolt", "FastAPI"], ["FaVial", "pytest"]];
    for (let i = 0; i < tools.length; i++) {
      const x = 0.8 + i * 1.75;
      await iconCircle(s, x, 5.45, 0.62, tools[i][0], C.background1, HEX.forest);
      txt(s, tools[i][1], { x: x + 0.72, y: 5.6, w: 1.0, h: 0.35, fontSize: 16, bold: true, color: C.background1 });
    }
    s.addImage({ data: await icon("FaSeedling", HEX.moss, 512), x: 9.9, y: 1.7, w: 2.6, h: 2.6, altText: "Pousse", objectName: oname("illustration") });
    txt(s, "Recommandation de cultures · un cas concret de bout en bout", { x: 0.8, y: 6.55, w: 9, h: 0.4, fontSize: 14, color: HEX.paleMoss });
    s.addNotes("Présenter l'objectif du cours : on ne cherche pas le meilleur modèle possible, mais tout ce qu'il faut autour d'un modèle pour qu'il soit reproductible, traçable, testé et utilisable. Le cas d'étude (recommander une culture) est volontairement simple. Le guide PDF reprend tout le contenu en détail et permet de reconstruire l'application.");
  }
  {
    const s = content("Au programme", "Six parties. Les parties 1 et 2 donnent la vue d'ensemble ; les parties 3 à 5 suivent l'ordre de construction de l'application ; la partie 6 traite de la qualité et fait le bilan, avec des exercices.");
    const parts = [
      ["Pourquoi le MLOps ?", "Les limites du notebook seul"],
      ["Architecture", "Un fichier, un rôle"],
      ["Environnement et données", "uv, configuration, DVC, validation"],
      ["Entraîner et suivre", "Validation croisée, MLflow, Docker"],
      ["Registre, promotion, API", "Le meilleur modèle, servi par HTTP"],
      ["Qualité et bilan", "Tests, CI, leçons, phase 2"],
    ];
    parts.forEach(([t, d], i) => {
      const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.55;
      card(s, x, y, 3.8, 2.25, i % 2 ? "file" : "soft");
      numCircle(s, x + 0.3, y + 0.3, 0.62, i + 1, C.accent1, 20);
      txt(s, t, { x: x + 0.3, y: y + 1.07, w: 3.3, h: 0.45, fontSize: 19, bold: true, color: C.accent1 });
      txt(s, d, { x: x + 0.3, y: y + 1.55, w: 3.3, h: 0.5, fontSize: 15, color: C.accent6 });
    });
  }

  // ---------------------------------------------------------------- 1. Pourquoi
  section("1. Pourquoi le MLOps ?");
  divider(1, "Pourquoi le MLOps ?", "Du « ça marche sur mon poste » au « ça marche partout, et on sait pourquoi ».",
    "Faire réagir les étudiants : qui a déjà eu un notebook qui ne marchait plus chez quelqu'un d'autre ?");
  {
    const s = content("« Ça marchait sur mon poste »", "Raconter le scénario « six mois plus tard ». Chaque problème correspond à un outil que l'on verra : versions → uv ; données → DVC ; réglages oubliés → MLflow ; copier-coller → paquet + API ; régressions → tests et CI.");
    const pbs = [
      ["FaBoxOpen", "Les versions ont changé", "Un collègue n'a pas les mêmes pandas et scikit-learn : le code plante."],
      ["FaDatabase", "Les données ont changé", "Sur quelle version du fichier le « bon » modèle a-t-il été entraîné ?"],
      ["FaMagnifyingGlass", "Les réglages sont perdus", "Lequel des vingt essais donnait 0,99 ? Cellules relancées dans le désordre."],
      ["FaCopy", "Le code est recopié", "L'application qui utilise le modèle recopie le notebook, sans garantie."],
      ["FaBug", "Rien ne prévient", "Une fonction modifiée casse tout le reste, sans que personne le voie."],
    ];
    for (let i = 0; i < pbs.length; i++) await iconRow(s, 0.6, 1.5 + i * 1.04, 7.4, pbs[i][0], pbs[i][1], pbs[i][2], { bg: C.accent5, bodyH: 0.55, bSize: 14, tSize: 16 });
    card(s, 8.5, 1.55, 4.2, 4.95, "soft");
    txt(s, "Aucun de ces problèmes ne vient du modèle.", { x: 8.8, y: 1.85, w: 3.6, h: 1.2, fontSize: 22, bold: true, italic: true, color: C.accent1, fontFace: "Cambria" });
    txt(s, [
      { text: "MLOps", options: { bold: true, breakLine: false } },
      { text: " : les pratiques qui rendent un projet de machine learning ", options: {} },
      { text: "reproductible, traçable, testé et déployable", options: { bold: true } },
      { text: ".", options: {} },
    ], { x: 8.8, y: 3.25, w: 3.6, h: 1.6, fontSize: 16 });
    txt(s, "Comme le DevOps, avec deux difficultés en plus : les données changent, et le modèle est produit par l'entraînement.", { x: 8.8, y: 4.9, w: 3.6, h: 1.4, fontSize: 14, color: C.accent6 });
  }
  {
    const s = content("Un modèle = code + données + environnement", "Pour reproduire un modèle, il faut retrouver les trois ingrédients. Un outil par ingrédient, plus MLflow pour la trace des expériences. La qualité (tests, Ruff, CI) vérifie l'ensemble en continu.");
    const cols = [["Code", "Git", "l'historique de chaque modification", "FaCodeBranch"], ["Environnement", "uv + uv.lock", "les mêmes versions sur chaque poste", "FaBoxOpen"], ["Données", "DVC", "la version exacte du fichier utilisé", "FaDatabase"], ["Expériences et modèles", "MLflow", "paramètres, scores, modèles, registre", "FaFlask"]];
    for (let i = 0; i < 4; i++) {
      const x = 0.6 + i * 3.05;
      box(s, x, 1.65, 2.8, 0.85, cols[i][0], null, "soft", { size: 17 });
      arrow(s, x + 1.4, 2.55, x + 1.4, 3.0);
      await iconCircle(s, x + 1.05, 3.08, 0.7, cols[i][3]);
      box(s, x, 3.9, 2.8, 0.8, cols[i][1], null, "main", { size: 20 });
      txt(s, cols[i][2], { x, y: 4.8, w: 2.8, h: 0.6, fontSize: 14, color: C.accent6, align: "center" });
    }
    box(s, 0.6, 5.7, 12.1, 0.75, "Qualité : tests automatisés (pytest) + style vérifié (Ruff) + intégration continue (GitHub Actions)", null, "wheat", { size: 16 });
  }
  {
    const s = content("Du notebook à l'application", "Insister : le notebook ne disparaît pas, il reste l'outil d'exploration. Ce qui doit être relancé, partagé ou testé quitte le notebook pour rejoindre des modules.");
    table(s, 0.6, 1.55, 12.1, ["Dans un notebook", "Dans l'application", "Ce que l'on gagne"], [
      ["Cellules dans un ordre libre", "Fonctions dans des modules, lancées par une commande", "Le même résultat à chaque fois"],
      ["Valeurs écrites en dur", "Réglages dans config/config.yaml", "Changer un réglage sans toucher au code"],
      ["pip install au fil de l'eau", "pyproject.toml + uv.lock", "Les mêmes versions partout"],
      ["CSV posé dans un dossier", "Fichier versionné par DVC, contrôlé par un schéma", "On sait quelles données ont servi"],
      ["Scores affichés puis perdus", "Runs enregistrés dans MLflow", "Historique complet et comparable"],
      ["Modèle copié à la main", "Registre + alias champion", "On sait quel modèle est en service"],
      ["Vérification « à l'œil »", "Tests automatisés + CI", "Une régression est vue tout de suite"],
    ], [3.6, 4.6, 3.9], { size: 16, rowH: 0.62 });
  }
  {
    const s = content("Le cas d'étude : recommander une culture", "Jeu de données public Crop Recommendation. Classes parfaitement équilibrées. On suit l'accuracy et le F1 macro ; c'est le F1 macro en validation croisée qui sert à choisir. Expliquer pourquoi le F1 macro protège des classes rares en général.");
    stat(s, 0.6, 1.45, 2.9, "2 200", "parcelles décrites");
    stat(s, 3.65, 1.45, 2.9, "7", "mesures du sol et du climat");
    stat(s, 6.7, 1.45, 2.9, "22", "cultures possibles");
    stat(s, 9.75, 1.45, 2.9, "100", "lignes par culture : classes équilibrées", C.accent3);
    const vars = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"];
    vars.forEach((v, i) => box(s, 0.6 + i * 1.42, 3.75, 1.3, 0.6, v, null, "file", { size: 14 }));
    arrow(s, 10.5, 4.05, 11.05, 4.05, { color: C.accent1, width: 2 });
    box(s, 11.1, 3.7, 1.6, 0.7, "label", "rice, maize…", "main", { size: 15, subSize: 11 });
    txt(s, "Entrées : azote, phosphore, potassium, température, humidité, pH, pluviométrie", { x: 0.6, y: 4.45, w: 10, h: 0.35, fontSize: 13, color: C.accent6 });
    card(s, 0.6, 5.15, 12.1, 1.35, "wheat");
    txt(s, [
      { text: "Mesure retenue : le F1 macro. ", options: { bold: true, color: C.accent3 } },
      { text: "Un score F1 par culture, puis la moyenne : chaque culture compte autant. Avec des données déséquilibrées, l'accuracy seule peut cacher un modèle qui ignore les cultures rares.", options: {} },
    ], { x: 0.9, y: 5.35, w: 11.5, h: 1.0, fontSize: 16 });
  }

  // ---------------------------------------------------------------- 2. Architecture
  section("2. Architecture");
  divider(2, "L'architecture de l'application", "Chaque fichier a un rôle, et un seul.", "Montrer le dépôt dans VS Code en parallèle.");
  {
    const s = content("Le cycle de l'application", "Lire le schéma dans l'ordre des numéros. Chaque boîte correspond à un fichier. Les réglages (bandeau du haut) sont lus par chaque étape ; les tests et la CI (bandeau du bas) vérifient chaque maillon.");
    box(s, 0.6, 1.4, 12.1, 0.55, "config/config.yaml + config/schema.yaml : tous les réglages, lus par chaque étape", null, "soft", { size: 14, dashed: true });
    const r1 = [["1. Données", "data/raw/*.csv · DVC"], ["2. Validation", "schema.yaml · validation.py"], ["3. Découpage", "data.py · 80 % / 20 %"], ["4. Entraînement", "train.py · tune.py"]];
    const r2 = [["8. Utilisateur", "requête → culture"], ["7. API", "api.py · FastAPI"], ["6. Promotion", "promote.py · champion"], ["5. Suivi", "tracking.py · MLflow"]];
    const w = 2.75, gap = 0.37;
    r1.forEach(([t, d], i) => { const x = 0.6 + i * (w + gap); box(s, x, 2.35, w, 1.15, t, d, "soft", { size: 17, subSize: 12, mono: true }); if (i < 3) arrow(s, x + w + 0.03, 2.92, x + w + gap - 0.03, 2.92); });
    r2.forEach(([t, d], i) => { const x = 0.6 + i * (w + gap); box(s, x, 4.3, w, 1.15, t, d, i === 1 ? "main" : (i === 0 ? "file" : "soft"), { size: 17, subSize: 12, mono: true }); if (i < 3) arrow(s, x + w + gap - 0.03, 4.87, x + w + 0.03, 4.87); });
    const x4 = 0.6 + 3 * (w + gap) + w / 2;
    arrow(s, x4, 3.52, x4, 4.28);
    box(s, 0.6, 5.9, 12.1, 0.55, "À chaque modification : tests (tests/) + Ruff + CI (.github/workflows/ci.yml)", null, "wheat", { size: 14 });
  }
  {
    const s = content("Une arborescence qui sépare les rôles", "Le code (src), les réglages (config), les données (data) et les vérifications (tests) vivent dans des dossiers différents : on change l'un sans toucher aux autres.");
    code(s, 0.6, 1.45, 6.9, 5.25, [
      "crop_recommendation_tp/",
      "├── pyproject.toml   uv.lock   .python-version",
      "├── config/",
      "│   ├── config.yaml       # tous les réglages",
      "│   └── schema.yaml       # contrat des données",
      "├── data/raw/",
      "│   ├── crop_recommendation.csv      # ignoré par Git",
      "│   └── crop_recommendation.csv.dvc  # étiquette DVC",
      "├── notebooks/01_exploration.ipynb",
      "├── src/crop_recommendation_tp/",
      "│   ├── config.py  validation.py  data.py",
      "│   ├── tracking.py",
      "│   └── train.py  tune.py  promote.py  api.py",
      "├── tests/  conftest.py + 5 fichiers test_*.py",
      "├── compose.yaml  Dockerfile.mlflow  Dockerfile.api",
      "└── .github/workflows/ci.yml",
    ].join("\n"), "Arborescence du dépôt", { size: 12 });
    const zones = [["FaSliders", "config/", "Les réglages, lisibles et versionnés"], ["FaDatabase", "data/", "Les données, versionnées par DVC"], ["FaCode", "src/", "Le code : un paquet Python installable"], ["FaVial", "tests/", "Les vérifications automatiques"]];
    for (let i = 0; i < zones.length; i++) await iconRow(s, 7.9, 1.6 + i * 1.28, 4.8, zones[i][0], zones[i][1], zones[i][2], { bodyH: 0.5 });
  }
  {
    const s = content("Cinq principes d'architecture", "Ces cinq principes justifient presque tous les choix du projet. Les rappeler à chaque fois qu'on rencontre un choix dans la suite.");
    const pr = [
      ["FaLayerGroup", "Séparer code, réglages et données", "src/, config/ et data/ évoluent indépendamment."],
      ["FaBullseye", "Une seule source de vérité", "Les bornes des variables sont dans schema.yaml : la validation et l'API les lisent là."],
      ["FaPuzzlePiece", "Une responsabilité par module", "validation.py ne fait que valider ; tracking.py ne fait que parler à MLflow."],
      ["FaRoute", "Tout est traçable", "Chaque run garde la version des données, le commit du code et la configuration."],
      ["FaTriangleExclamation", "Échouer tôt et clairement", "Données invalides : l'entraînement s'arrête. Requête invalide : l'API la refuse."],
    ];
    for (let i = 0; i < pr.length; i++) await iconRow(s, 0.6, 1.5 + i * 1.04, 12, pr[i][0], pr[i][1], pr[i][2], { bodyH: 0.45, bSize: 15 });
  }
  {
    const s = content("Qui utilise qui ?", "Organisation en couches : les briques de base ne dépendent de rien, les commandes assemblent les services. Si l'on remplace MLflow, seul tracking.py change. Pas de dépendance circulaire.");
    txt(s, "Commandes", { x: 0.6, y: 1.45, w: 3, h: 0.3, fontSize: 13, bold: true, color: C.accent6 });
    const top = [["train.py", "uv run train"], ["tune.py", "uv run tune"], ["promote.py", "uv run promote"], ["api.py", "uv run fastapi dev"]];
    const xs = top.map((_, i) => 0.6 + i * 3.1);
    top.forEach(([t, d], i) => box(s, xs[i], 1.8, 2.8, 0.9, t, d, "main", { size: 18, subSize: 12, mono: true }));
    txt(s, "Services", { x: 0.6, y: 3.25, w: 3, h: 0.3, fontSize: 13, bold: true, color: C.accent6 });
    box(s, 2.6, 3.6, 3.0, 0.9, "data.py", "charger · découper · md5", "soft", { size: 18, subSize: 12 });
    box(s, 7.6, 3.6, 3.0, 0.9, "tracking.py", "connexion · enregistrer les runs", "soft", { size: 18, subSize: 12 });
    txt(s, "Briques de base", { x: 0.6, y: 5.0, w: 3, h: 0.3, fontSize: 13, bold: true, color: C.accent6 });
    box(s, 2.6, 5.35, 3.0, 0.85, "validation.py", "contrôle du schéma", "file", { size: 18, subSize: 12 });
    box(s, 7.6, 5.35, 3.0, 0.85, "config.py", "lire les fichiers YAML", "file", { size: 18, subSize: 12 });
    arrow(s, 1.6, 2.72, 3.3, 3.58); arrow(s, 2.4, 2.72, 7.9, 3.58);
    arrow(s, 4.4, 2.72, 4.2, 3.58); arrow(s, 4.9, 2.72, 8.4, 3.58);
    arrow(s, 7.9, 2.72, 8.9, 3.58); arrow(s, 10.6, 2.72, 9.9, 3.58);
    arrow(s, 4.1, 4.52, 4.1, 5.33); arrow(s, 9.1, 4.52, 9.1, 5.33);
    arrow(s, 7.58, 4.05, 5.62, 4.05, { label: "get_data_version", ldy: -0.32 });
    arrow(s, 5.62, 5.78, 7.58, 5.78, { label: "load_yaml, ROOT", ldy: -0.32 });
    txt(s, "A → B : « A importe B ». Les dépendances descendent toujours.", { x: 0.6, y: 6.45, w: 12.1, h: 0.35, fontSize: 13, italic: true, color: C.accent6, align: "center" });
  }
  {
    const s = content("Un script, une responsabilité", "Faire le lien avec la diapositive précédente : quatre commandes, deux services, deux briques de base. Chaque fonction est courte et testable.");
    table(s, 0.6, 1.5, 12.1, ["Fichier", "Rôle", "Fonctions principales"], [
      ["config.py", "Lire les fichiers YAML depuis la racine du projet", "load_yaml, load_config, ROOT"],
      ["validation.py", "Comparer un tableau au schéma, lister les erreurs", "validate"],
      ["data.py", "Charger et valider, choisir les variables, découper, calculer l'empreinte", "load_dataset, split_dataset, build_cv"],
      ["tracking.py", "Se connecter à MLflow, enregistrer un run ou une recherche", "setup_mlflow, log_run, log_tuning"],
      ["train.py", "Commande train : entraîner et enregistrer un candidat", "build_model, cross_validate_model, evaluate"],
      ["tune.py", "Commande tune : comparer des hyperparamètres", "tune"],
      ["promote.py", "Commande promote : comparer au champion, déplacer l'alias", "find_candidate_run_id, promote_candidate"],
      ["api.py", "Servir le champion par HTTP", "lifespan, health, predict"],
    ], [2.2, 5.6, 4.3], { size: 15, codeCols: [0, 2], rowH: 0.58 });
  }

  // ---------------------------------------------------------------- 3. Environnement et données
  section("3. Environnement et données");
  divider(3, "Environnement, configuration et données", "Le socle : les mêmes versions, les mêmes réglages, les mêmes données.", "");
  {
    const s = content("uv : le même environnement partout", "Un environnement virtuel isole les bibliothèques du projet ; uv.lock fige les versions exactes, y compris les dépendances indirectes. Montrer uv sync sur un poste neuf.");
    await iconRow(s, 0.6, 1.55, 5.6, "FaTriangleExclamation", "Le problème", "Une version différente de scikit-learn peut changer les résultats, ou casser le code.", { bg: C.accent5, bodyH: 0.75 });
    await iconRow(s, 0.6, 2.85, 5.6, "FaBoxOpen", "L'environnement virtuel", "Le dossier .venv/ : Python et les bibliothèques du projet, isolés du reste.", { bodyH: 0.75 });
    await iconRow(s, 0.6, 4.15, 5.6, "FaLock", "Le fichier de verrouillage", "uv.lock note la version exacte de chaque bibliothèque. À commiter, jamais à modifier à la main.", { bodyH: 0.75 });
    code(s, 6.6, 1.5, 6.1, 4.0, [
      "# Créer un projet « paquet » (dossier src/)",
      "uv init --package crop_recommendation_tp",
      "uv python pin 3.13",
      "",
      "# Dépendances de l'application",
      "uv add pandas scikit-learn pyyaml dvc \\",
      "       mlflow matplotlib \"fastapi[standard]\"",
      "",
      "# Outils de développement",
      "uv add --dev jupyterlab pytest ruff",
      "",
      "# Sur un autre poste : tout réinstaller",
      "uv sync",
    ].join("\n"), "Terminal", { size: 13 });
    card(s, 6.6, 5.75, 6.1, 0.8, "wheat");
    txt(s, [{ text: "uv run train", options: { fontFace: "Courier New", bold: true } }, { text: " lance une commande dans l'environnement, sans l'activer.", options: {} }], { x: 6.85, y: 5.95, w: 5.7, h: 0.45, fontSize: 15 });
  }
  {
    const s = content("Aucune valeur en dur : config.yaml", "Tous les réglages au même endroit, lisibles et versionnés par Git. La configuration est aussi enregistrée dans chaque run MLflow : on retrouve les réglages exacts d'un ancien résultat.");
    code(s, 0.6, 1.45, 5.7, 5.3, fs.readFileSync(REPO + "/config/config.yaml", "utf8").trimEnd(), "config/config.yaml", { size: 12 });
    const rows = [["dataset", "chemins du CSV et du schéma, colonne cible"], ["split", "20 % pour le test, graine 42"], ["mlflow", "serveur, expérience, modèle, alias"], ["model.params", "hyperparamètres de train"], ["tuning", "plis, mesure, grille de recherche"]];
    rows.forEach(([k, v], i) => {
      box(s, 6.7, 1.5 + i * 0.86, 2.0, 0.66, k, null, "soft", { size: 14 });
      txt(s, v, { x: 8.9, y: 1.66 + i * 0.86, w: 3.8, h: 0.4, fontSize: 15 });
    });
    card(s, 6.7, 5.95, 6.0, 0.8, "soft");
    txt(s, [{ text: "config.py", options: { fontFace: "Courier New", bold: true } }, { text: " lit ce fichier ; ROOT rend les chemins valables depuis n'importe quel dossier.", options: {} }], { x: 6.95, y: 6.08, w: 5.6, h: 0.6, fontSize: 14 });
  }
  {
    const s = content("DVC : Git pour les données", "Git garde l'étiquette (quelques lignes : empreinte md5 et taille), DVC range le contenu dans un cache puis dans un stockage distant. Aujourd'hui un dossier local ; en phase 2, un stockage partagé : seule l'URL changera.");
    card(s, 0.6, 1.75, 3.7, 4.35, "file"); txt(s, "Dépôt Git", { x: 0.6, y: 1.4, w: 3.7, h: 0.3, fontSize: 15, bold: true, color: C.accent1, align: "center" });
    box(s, 0.8, 1.95, 3.3, 0.75, "src/ · tests/ · config/", "code et réglages", "file", { size: 13, subSize: 11 });
    box(s, 0.8, 2.85, 3.3, 0.75, "pyproject.toml · uv.lock", "environnement", "file", { size: 13, subSize: 11 });
    box(s, 0.8, 3.75, 3.3, 0.85, "crop_recommendation.csv.dvc", "md5 5e743dd4… · 150 Ko", "wheat", { size: 13, subSize: 11, mono: true });
    box(s, 0.8, 4.75, 3.3, 0.75, "data/raw/.gitignore", "« ignore le CSV »", "file", { size: 13, subSize: 11 });
    card(s, 4.95, 1.75, 3.4, 4.35, "soft"); txt(s, "Poste de travail", { x: 4.95, y: 1.4, w: 3.4, h: 0.3, fontSize: 15, bold: true, color: C.accent1, align: "center" });
    box(s, 5.2, 2.1, 2.9, 1.0, "data/raw/", "le vrai fichier CSV", "file", { size: 15, subSize: 12 });
    box(s, 5.2, 4.3, 2.9, 1.0, ".dvc/cache/", "copie rangée par md5", "file", { size: 15, subSize: 12 });
    arrow(s, 6.65, 3.15, 6.65, 4.25, { label: "dvc add", ldx: 0.75, ldy: -0.12 });
    card(s, 9.0, 1.75, 3.7, 4.35, "blue"); txt(s, "Stockage DVC (remote)", { x: 9.0, y: 1.4, w: 3.7, h: 0.3, fontSize: 15, bold: true, color: C.accent4, align: "center" });
    txt(s, "Aujourd'hui : un dossier à côté du dépôt\nPhase 2 : S3, Google Drive, SSH…", { x: 9.2, y: 2.15, w: 3.3, h: 1.0, fontSize: 13, color: C.accent6, align: "center" });
    box(s, 9.2, 4.3, 3.3, 1.0, "crop_recommendation_storage/", null, "file", { size: 13 });
    arrow(s, 4.9, 2.4, 4.35, 2.4, { label: "git push", ldy: -0.3 });
    arrow(s, 4.35, 2.95, 4.9, 2.95, { label: "git pull", ldy: 0.05 });
    arrow(s, 8.12, 4.6, 9.18, 4.6, { label: "dvc push", ldy: -0.32 });
    arrow(s, 9.18, 5.0, 8.12, 5.0, { label: "dvc pull", ldy: 0.05 });
    txt(s, "Git versionne l'étiquette ; DVC range et transporte le contenu.", { x: 0.6, y: 6.35, w: 12.1, h: 0.35, fontSize: 15, italic: true, color: C.accent6, align: "center" });
  }
  {
    const s = content("DVC en pratique", "Les commandes DVC imitent celles de Git. L'empreinte des données est aussi enregistrée dans chaque run MLflow (data_md5), avec le suffixe -modified si le fichier lu ne correspond pas au .dvc.");
    table(s, 0.6, 1.5, 7.3, ["Commande", "Effet", "Comme"], [
      ["dvc add", "Empreinte + cache + fichier .dvc", "git add"],
      ["dvc push", "Envoie les données au stockage", "git push"],
      ["dvc pull", "Récupère les données du commit", "git pull"],
      ["dvc status", "Compare les données aux .dvc", "git status"],
      ["dvc checkout", "Remet les données décrites par les .dvc", "git checkout"],
    ], [1.9, 3.5, 1.9], { size: 15, codeCols: [0, 2], rowH: 0.52 });
    code(s, 8.3, 1.5, 4.4, 2.0, fs.readFileSync(REPO + "/data/raw/crop_recommendation.csv.dvc", "utf8").trimEnd(), "crop_recommendation.csv.dvc", { size: 13 });
    card(s, 8.3, 3.75, 4.4, 1.55, "wheat");
    txt(s, "Une empreinte md5 est une empreinte digitale du fichier : un seul caractère modifié, et elle change complètement.", { x: 8.5, y: 3.9, w: 4.0, h: 1.3, fontSize: 15 });
    code(s, 0.6, 4.85, 7.3, 1.75, ["# Nouveau poste", "git clone <url> && cd crop_recommendation_tp", "uv sync && uv run dvc pull", "uv run dvc status   # → Data and pipelines are up to date."].join("\n"), "Terminal", { size: 13 });
    card(s, 8.3, 5.5, 4.4, 1.1, "red");
    txt(s, "Ne jamais commiter le CSV dans Git : dvc add l'ajoute à .gitignore.", { x: 8.5, y: 5.65, w: 4.0, h: 0.85, fontSize: 15 });
  }
  {
    const s = content("Valider les données avant tout", "Un modèle entraîné sur des données fausses donne des résultats faux, sans message d'erreur. Le schéma est un contrat écrit ; validate renvoie la liste de toutes les erreurs (vide = conforme), ce qui la rend très facile à tester.");
    code(s, 0.6, 1.45, 5.6, 3.55, fs.readFileSync(REPO + "/config/schema.yaml", "utf8").split("\n").slice(0, 11).join("\n") + "\n            [apple, banana, … 22 cultures]", "config/schema.yaml", { size: 12 });
    txt(s, "validate(df, schema) vérifie, pour chaque colonne :", { x: 6.6, y: 1.5, w: 6.1, h: 0.4, fontSize: 16, bold: true, color: C.accent1 });
    const checks = ["la colonne existe", "son type est connu du validateur", "aucune valeur manquante", "le type des valeurs est le bon", "les valeurs sont autorisées (cultures)", "les bornes min et max sont respectées"];
    checks.forEach((c, i) => { numCircle(s, 6.6, 2.0 + i * 0.46, 0.36, i + 1, C.accent1, 12); txt(s, c, { x: 7.1, y: 2.02 + i * 0.46, w: 5.5, h: 0.35, fontSize: 15 }); });
    txt(s, "… puis les colonnes en trop.", { x: 7.1, y: 4.78, w: 5.5, h: 0.35, fontSize: 15, italic: true, color: C.accent6 });
    code(s, 0.6, 5.3, 12.1, 1.4, ["$ uv run train      # avec un pH à 75 dans le CSV", "ValueError: Données non conformes au schéma :", "ph : 1 valeur(s) > 14"].join("\n"), "Échouer tôt et clairement : load_dataset arrête tout", { size: 13 });
  }
  {
    const s = content("Un découpage stratifié et reproductible", "Stratifier garde 20 lignes de chaque culture dans le test. La graine fige le hasard : même découpage partout. La validation croisée découpe l'entraînement en 5 plis ; le jeu de test reste dans le coffre.");
    txt(s, "2 200 lignes (100 par culture), graine 42", { x: 0.6, y: 1.45, w: 12.1, h: 0.35, fontSize: 15, bold: true, align: "center" });
    s.addText("Entraînement : 1 760 lignes (80 %)", { shape: pres.shapes.ROUNDED_RECTANGLE, x: 0.6, y: 1.9, w: 9.6, h: 0.7, rectRadius: 0.06, fill: { color: C.accent2 }, line: { color: C.accent2 }, bold: true, fontSize: 17, color: C.text1, align: "center", valign: "middle", objectName: oname("barre") });
    s.addText("Test : 440 lignes", { shape: pres.shapes.ROUNDED_RECTANGLE, x: 10.3, y: 1.9, w: 2.4, h: 0.7, rectRadius: 0.06, fill: { color: C.accent3 }, line: { color: C.accent3 }, bold: true, fontSize: 17, color: C.background1, align: "center", valign: "middle", objectName: oname("barre") });
    txt(s, "Validation croisée à 5 plis, sur l'entraînement seulement :", { x: 0.6, y: 2.85, w: 9, h: 0.35, fontSize: 15, bold: true, color: C.accent1 });
    const fw = 9.6 / 5;
    for (let r = 0; r < 5; r++) {
      for (let c = 0; c < 5; c++) {
        const ev = r === c;
        s.addText(ev ? "évaluation" : "apprentissage", { shape: pres.shapes.ROUNDED_RECTANGLE, x: 0.6 + c * fw + 0.04, y: 3.3 + r * 0.46, w: fw - 0.08, h: 0.38, rectRadius: 0.05, fill: { color: ev ? C.background1 : C.background2 }, line: { color: ev ? C.accent1 : C.accent2, width: ev ? 1.75 : 1 }, fontSize: 12, bold: ev, color: ev ? C.accent1 : C.accent6, align: "center", valign: "middle", margin: 0, objectName: oname("pli") });
      }
      txt(s, `pli ${r + 1} → score`, { x: 10.35, y: 3.35 + r * 0.46, w: 2.3, h: 0.3, fontSize: 13, color: C.accent6 });
    }
    txt(s, [
      { text: "Score de validation croisée = moyenne des 5 scores. ", options: { bold: true } },
      { text: "C'est lui qui sert à comparer et à choisir. ", options: {} },
      { text: "Le jeu de test sert une seule fois, à la fin.", options: { bold: true, color: C.accent3 } },
    ], { x: 0.6, y: 5.75, w: 12.1, h: 0.8, fontSize: 16 });
  }

  // ---------------------------------------------------------------- 4. Entraîner et suivre
  section("4. Entraîner et suivre");
  divider(4, "Entraîner et suivre", "Mesurer honnêtement, et tout garder en mémoire.", "");
  {
    const s = content("train.py : produire un candidat", "Les six étapes de uv run train. Les plis viennent de build_cv (data.py), les mêmes que ceux de tune : pour les mêmes réglages, les deux commandes annoncent le même score. Deux scores, deux rôles : la validation croisée choisit, le test estime. build_model est une fonction à part pour que la validation croisée utilise exactement les mêmes réglages.");
    const steps = [["Charger", "et valider"], ["Découper", "80 % / 20 %"], ["Entraîner", "model.params"], ["Valider", "5 plis (CV)"], ["Tester", "jeu de test"], ["Enregistrer", "run candidat"]];
    steps.forEach(([t, d], i) => {
      const x = 0.6 + i * 2.05;
      numCircle(s, x + 0.72, 1.5, 0.5, i + 1, C.accent1, 16);
      box(s, x, 2.1, 1.85, 1.0, t, d, i === 5 ? "main" : "soft", { size: 16, subSize: 12 });
      if (i < 5) arrow(s, x + 1.87, 2.6, x + 2.03, 2.6);
    });
    card(s, 0.6, 3.6, 5.9, 2.9, "soft");
    txt(s, "Validation croisée", { x: 0.9, y: 3.8, w: 5.3, h: 0.4, fontSize: 19, bold: true, color: C.accent1 });
    txt(s, "cv_f1_macro_mean, cv_f1_macro_std", { x: 0.9, y: 4.25, w: 5.3, h: 0.35, fontSize: 14, fontFace: "Courier New" });
    txt(s, "Calculée sur l'entraînement, en 5 plis.\nSert à COMPARER et à CHOISIR (tune, promote).", { x: 0.9, y: 4.75, w: 5.3, h: 1.2, fontSize: 16 });
    card(s, 6.8, 3.6, 5.9, 2.9, "wheat");
    txt(s, "Jeu de test", { x: 7.1, y: 3.8, w: 5.3, h: 0.4, fontSize: 19, bold: true, color: C.accent3 });
    txt(s, "accuracy, f1_macro", { x: 7.1, y: 4.25, w: 5.3, h: 0.35, fontSize: 14, fontFace: "Courier New" });
    txt(s, "Calculé une seule fois, sur 440 lignes jamais vues.\nSert à ESTIMER la performance réelle.", { x: 7.1, y: 4.75, w: 5.3, h: 1.2, fontSize: 16 });
  }
  {
    const s = content("Le piège : choisir avec le jeu de test", "Dans le notebook, les configurations sont comparées sur X_test : sans faute tant qu'on regarde, mais si l'on choisit d'après ces scores, le test a servi à décider et son score devient trop optimiste. Avec 12 combinaisons, l'effet est réel. Un encadré a été ajouté dans le notebook.");
    card(s, 0.6, 1.5, 5.75, 4.6, "red");
    await iconCircle(s, 0.9, 1.75, 0.6, "FaXmark", C.accent5);
    txt(s, "Notebook (exploration)", { x: 1.65, y: 1.83, w: 4.5, h: 0.45, fontSize: 19, bold: true, color: C.accent5 });
    ["Entraîner plusieurs configurations", "Mesurer chacune sur X_test", "Garder la meilleure", "Annoncer son score sur X_test"].forEach((t, i) => {
      box(s, 0.95, 2.6 + i * 0.82, 5.05, 0.6, t, null, i === 1 || i === 3 ? "red" : "file", { size: 15 });
      if (i < 3) arrow(s, 3.47, 3.21 + i * 0.82, 3.47, 3.41 + i * 0.82);
    });
    card(s, 6.95, 1.5, 5.75, 4.6, "soft");
    await iconCircle(s, 7.25, 1.75, 0.6, "FaCheck", C.accent1);
    txt(s, "Application (train, tune)", { x: 8.0, y: 1.83, w: 4.5, h: 0.45, fontSize: 19, bold: true, color: C.accent1 });
    ["Entraîner plusieurs configurations", "Mesurer chacune en validation croisée", "Garder la meilleure", "Mesurer une seule fois sur X_test"].forEach((t, i) => {
      box(s, 7.3, 2.6 + i * 0.82, 5.05, 0.6, t, null, i === 1 ? "soft" : (i === 3 ? "wheat" : "file"), { size: 15 });
      if (i < 3) arrow(s, 9.82, 3.21 + i * 0.82, 9.82, 3.41 + i * 0.82);
    });
    txt(s, "Le jeu de test ne sert jamais à décider : son score reste une estimation honnête.", { x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 17, bold: true, color: C.accent1, align: "center" });
  }
  {
    const s = content("Résultats du candidat", "Résultats réels de uv run train (environ 7 secondes). Les scores en validation croisée et sur le test sont proches : le modèle généralise bien. Deux erreurs sur 440 dans la matrice de confusion, enregistrée comme artefact du run.");
    stat(s, 0.6, 1.35, 3.0, "0,9943", "F1 macro en validation croisée");
    stat(s, 3.8, 1.35, 2.6, "± 0,0048", "écart-type sur 5 plis", C.accent6);
    stat(s, 0.6, 3.25, 3.0, "0,9955", "accuracy sur le jeu de test", C.accent3);
    stat(s, 3.8, 3.25, 2.6, "2 / 440", "erreurs sur le jeu de test", C.accent3);
    card(s, 0.6, 5.3, 5.8, 1.3, "soft");
    txt(s, "Forêt aléatoire, 200 arbres, profondeur illimitée : les réglages trouvés par tune.", { x: 0.85, y: 5.45, w: 5.3, h: 1.0, fontSize: 15 });
    s.addImage({ path: path.join(RUN, "confusion_matrix.png"), x: 6.9, y: 1.35, w: 5.4, h: 5.4, altText: "Matrice de confusion : presque tout est sur la diagonale", objectName: oname("matrice") });
  }
  {
    const s = content("MLflow : un cahier de laboratoire automatique", "La philosophie de MLflow : c'est le code qui note, pas l'humain ; tout est comparable ; on sépare l'expérimentation (suivi) de la mise en service (registre) ; le format est indépendant de la bibliothèque de ML.");
    const ph = [
      ["FaPenToSquare", "Tout noter, automatiquement", "Le code enregistre paramètres, scores et fichiers : rien n'est oublié."],
      ["FaChartColumn", "Comparer", "Tous les runs d'une expérience côte à côte, triables par score."],
      ["FaTrophy", "Séparer essais et mise en service", "Le suivi garde tout ; le registre ne garde que les modèles retenus."],
      ["FaCubes", "Indépendant de la bibliothèque", "Le même format pour scikit-learn, PyTorch, XGBoost…"],
    ];
    for (let i = 0; i < ph.length; i++) await iconRow(s, 0.6, 1.55 + i * 1.2, 7.6, ph[i][0], ph[i][1], ph[i][2], { bodyH: 0.55, bSize: 15 });
    card(s, 8.7, 1.55, 4.0, 4.6, "soft");
    s.addImage({ data: await icon("FaFlask", HEX.forest, 512), x: 9.95, y: 1.85, w: 1.5, h: 1.5, altText: "Laboratoire", objectName: oname("illustration") });
    txt(s, "« Quel réglage donnait 0,99 ? »", { x: 8.95, y: 3.6, w: 3.5, h: 0.9, fontSize: 19, italic: true, color: C.accent1, fontFace: "Cambria", align: "center" });
    txt(s, "On ne se pose plus la question : on le retrouve.", { x: 8.95, y: 4.6, w: 3.5, h: 0.9, fontSize: 15, color: C.accent6, align: "center" });
  }
  {
    const s = content("Les concepts de MLflow", "Expérience = dossier de runs comparables. Run = une exécution, avec paramètres, métriques, tags, artefacts et modèle. Registre = versions des modèles retenus ; l'alias champion est une étiquette mobile que promote déplace.");
    card(s, 0.6, 1.45, 6.8, 5.25, "file");
    txt(s, "Expérience « crop-recommendation »", { x: 0.85, y: 1.58, w: 6.3, h: 0.35, fontSize: 15, bold: true });
    box(s, 0.85, 2.1, 2.9, 0.75, "Run « train »", "stage = candidate", "soft", { size: 14, subSize: 11, mono: true });
    box(s, 0.85, 3.0, 2.9, 0.75, "Run « train »", "stage = candidate", "soft", { size: 14, subSize: 11, mono: true });
    box(s, 0.85, 3.9, 2.9, 0.75, "Run « tuning »", "run parent", "soft", { size: 14, subSize: 11 });
    ["cv_0", "cv_1", "…", "cv_11"].forEach((t, i) => box(s, 0.95 + i * 0.7, 4.95, 0.62, 0.45, t, null, "file", { size: 10 }));
    arrow(s, 2.3, 4.67, 2.3, 4.93);
    card(s, 4.1, 2.0, 3.1, 4.5, "soft");
    txt(s, "Contenu d'un run", { x: 4.1, y: 2.1, w: 3.1, h: 0.35, fontSize: 14, bold: true, align: "center" });
    [["Paramètres", "n_estimators…"], ["Métriques", "cv_f1_macro_mean…"], ["Tags", "data_md5, git_commit"], ["Artefacts", "config, rapport, images"], ["Modèle", "+ signature"]].forEach(([t, d], i) => box(s, 4.3, 2.55 + i * 0.77, 2.7, 0.65, t, d, "file", { size: 13, subSize: 10, mono: true }));
    arrow(s, 3.77, 2.47, 4.08, 2.47);
    card(s, 7.8, 1.45, 4.9, 5.25, "blue");
    txt(s, "Registre de modèles", { x: 8.05, y: 1.58, w: 4.4, h: 0.35, fontSize: 15, bold: true, color: C.accent4 });
    box(s, 8.05, 2.1, 4.4, 0.65, "Modèle « crop-recommendation »", null, "blue", { size: 14 });
    ["Version 1", "Version 2", "Version 3"].forEach((t, i) => box(s, 8.3, 3.05 + i * 0.85, 1.9, 0.6, t, null, "file", { size: 14 }));
    box(s, 10.7, 3.85, 1.7, 0.7, "@champion", null, "main", { size: 15 });
    arrow(s, 10.68, 4.2, 10.22, 4.17, { color: C.accent1, width: 2 });
    txt(s, "L'alias est une étiquette mobile : promote la déplace vers la meilleure version.", { x: 8.05, y: 5.65, w: 4.4, h: 0.85, fontSize: 13, color: C.accent6 });
    arrow(s, 7.0, 6.0, 8.28, 4.2, { color: C.accent1, dashed: true });
  }
  {
    const s = content("Ce qu'enregistre chaque run", "log_run (tracking.py) enregistre tout en une fois. La signature décrit les entrées attendues (7 colonnes float64) : c'est pourquoi l'API convertit les mesures en float64.");
    const items = [["FaSliders", "Paramètres", "tous les réglages du modèle + test_size"], ["FaChartLine", "Métriques", "validation croisée, accuracy, F1 macro"], ["FaTag", "Tags", "data_md5, git_commit, stage"], ["FaFileLines", "Artefacts", "config, schéma, rapport, matrice"], ["FaCube", "Modèle", "sérialisé, avec signature et exemple"]];
    for (let i = 0; i < items.length; i++) {
      const x = 0.6 + i * 2.46;
      card(s, x, 1.5, 2.25, 2.6, "soft");
      await iconCircle(s, x + 0.78, 1.72, 0.7, items[i][0]);
      txt(s, items[i][1], { x: x + 0.1, y: 2.55, w: 2.05, h: 0.4, fontSize: 17, bold: true, color: C.accent1, align: "center" });
      txt(s, items[i][2], { x: x + 0.15, y: 3.0, w: 1.95, h: 0.95, fontSize: 13, align: "center" });
    }
    code(s, 0.6, 4.4, 12.1, 2.2, [
      "with mlflow.start_run(run_name=run_name) as run:",
      "    mlflow.log_params(params)",
      "    mlflow.set_tags({**trace_tags(config), **(tags or {})})   # data_md5, git_commit, stage",
      "    mlflow.log_dict(config, \"config.yaml\")",
      "    mlflow.log_metrics(metrics)",
      "    mlflow.sklearn.log_model(model, name=\"model\", signature=…, input_example=…)",
    ].join("\n"), "src/crop_recommendation_tp/tracking.py (extrait de log_run)", { size: 13 });
  }
  {
    const s = content("La traçabilité de bout en bout", "Exercice en direct : partir de /health, retrouver le run dans l'interface MLflow, lire git_commit et data_md5, puis git show et le fichier .dvc. Le suffixe -dirty signale des modifications non commitées.");
    box(s, 0.6, 2.6, 2.3, 1.3, "Prédiction", "culture : rice\nversion : 1", "main", { size: 17, subSize: 12, mono: true });
    arrow(s, 2.95, 3.25, 3.4, 3.25);
    box(s, 3.45, 2.6, 2.3, 1.3, "Registre", "version 1\n→ run 4c4afe…", "blue", { size: 17, subSize: 12, mono: true });
    arrow(s, 5.8, 3.25, 6.25, 3.25);
    box(s, 6.3, 2.4, 2.6, 1.7, "Run MLflow", "paramètres, scores,\nconfig.yaml, schema.yaml", "soft", { size: 17, subSize: 12 });
    arrow(s, 8.95, 2.9, 9.55, 2.1); arrow(s, 8.95, 3.6, 9.55, 4.4);
    box(s, 9.6, 1.45, 3.1, 1.35, "git_commit", "7e8606e…\n→ le code exact", "wheat", { size: 17, subSize: 12, mono: true });
    box(s, 9.6, 3.75, 3.1, 1.35, "data_md5", "5e743dd4…\n→ les données exactes", "wheat", { size: 17, subSize: 12, mono: true });
    card(s, 0.6, 5.55, 12.1, 1.0, "soft");
    txt(s, "De n'importe quelle prédiction, on remonte au code, aux données et aux réglages qui l'ont produite.", { x: 0.9, y: 5.8, w: 11.5, h: 0.5, fontSize: 18, bold: true, color: C.accent1, align: "center" });
  }
  {
    const s = content("tune : comparer 12 combinaisons", "GridSearchCV essaie 3 × 4 = 12 combinaisons sur 5 plis (60 entraînements, environ 7 secondes). La profondeur compte bien plus que le nombre d'arbres. tune n'enregistre pas de modèle : chercher et décider sont deux actes séparés ; le report dans config.yaml est fait à la main et commité.");
    const data = [["50 · prof. 3", 0.8841], ["100 · prof. 3", 0.8944], ["200 · prof. 3", 0.9047], ["50 · prof. 5", 0.9753], ["100 · prof. 5", 0.9755], ["200 · prof. 5", 0.9884], ["50 · prof. 10", 0.9930], ["200 · prof. 10", 0.9931], ["50 · illimitée", 0.9931], ["100 · illimitée", 0.9937], ["100 · prof. 10", 0.9943], ["200 · illimitée", 0.9943]];
    const fr = (v, d) => v.toFixed(d).replace(".", ",");
    const rows = data.slice().reverse().map(([l, v], i) => [l.replace("prof. ", "profondeur "), v, i === 0 ? C.accent1 : (v > 0.98 ? C.accent2 : C.accent3), i === 0]);
    hbars(s, 0.6, 1.45, 7.7, 5.3, rows, { title: "F1 macro en validation croisée (arbres · profondeur)", labelW: 2.35, valueW: 0.85, min: 0.85, max: 1.0, ticks: [0.85, 0.9, 0.95, 1.0], fmtTick: (t) => fr(t, 2), fmt: (v) => fr(v, 4), labelSize: 13, valueSize: 12 });
    txt(s, "Le circuit de travail", { x: 8.6, y: 1.45, w: 4.1, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
    [["uv run tune", "la recherche affiche la meilleure combinaison"], ["config.yaml", "on reporte model.params, puis on commite"], ["uv run train", "on entraîne le candidat"], ["uv run promote", "on le compare au champion"]].forEach(([t, d], i) => {
      numCircle(s, 8.6, 2.05 + i * 1.12, 0.45, i + 1, C.accent1, 14);
      txt(s, t, { x: 9.2, y: 2.03 + i * 1.12, w: 3.5, h: 0.35, fontSize: 15, bold: true, fontFace: "Courier New" });
      txt(s, d, { x: 9.2, y: 2.4 + i * 1.12, w: 3.5, h: 0.6, fontSize: 14, color: C.accent6 });
    });
  }
  {
    const s = content("PostgreSQL, MLflow et l'API avec Docker", "Trois services dans compose.yaml. L'API rejoint MLflow par son nom dans le réseau Docker (http://mlflow:5000) ; depuis MLflow 3, il faut --allowed-hosts, sinon le serveur répond 403. Les ports ne sont publiés que sur 127.0.0.1. Les identifiants sont dans .env, ignoré par Git. Les scripts restent sur le poste : ils ont besoin des données DVC et de Git. Après une promotion : docker compose restart api.");
    card(s, 0.6, 1.75, 3.6, 4.55, "soft"); txt(s, "Votre poste", { x: 0.6, y: 1.4, w: 3.6, h: 0.3, fontSize: 15, bold: true, color: C.accent1, align: "center" });
    [["uv run train / tune", "envoient des runs"], ["uv run promote", "gère le registre"], ["Navigateur, curl", "interface MLflow, API"]].forEach(([t, d], i) => box(s, 0.8, 2.0 + i * 1.4, 3.2, 0.95, t, d, "file", { size: 14, subSize: 12 }));
    card(s, 4.9, 1.75, 7.8, 4.55, "blue"); txt(s, "Docker Compose (compose.yaml)", { x: 4.9, y: 1.4, w: 7.8, h: 0.3, fontSize: 15, bold: true, color: C.accent4, align: "center" });
    box(s, 5.2, 1.95, 3.2, 0.95, "api", "Dockerfile.api · fastapi run", "wheat", { size: 18, subSize: 12 });
    txt(s, "charge le champion au démarrage\nport 8000", { x: 8.7, y: 2.05, w: 3.8, h: 0.75, fontSize: 13, color: C.accent6 });
    box(s, 5.2, 3.35, 3.2, 1.15, "mlflow", "Dockerfile.mlflow · port 5000\n--allowed-hosts", "main", { size: 18, subSize: 12 });
    box(s, 9.2, 3.35, 3.2, 1.15, "postgres", "postgres:18 · port 5432\nidentifiants : .env", "blue", { size: 18, subSize: 12 });
    arrow(s, 6.8, 2.92, 6.8, 3.33, { label: "http://mlflow:5000", ldx: 1.25, ldy: -0.15 });
    arrow(s, 8.45, 3.92, 9.15, 3.92, { label: "SQL", ldy: -0.3 });
    box(s, 5.2, 4.95, 3.2, 1.05, "volume mlflow_artifacts", "modèles, images, rapports", "file", { size: 13, subSize: 11 });
    box(s, 9.2, 4.95, 3.2, 1.05, "volume postgres_data", "paramètres, scores, registre", "file", { size: 13, subSize: 11 });
    arrow(s, 6.8, 4.52, 6.8, 4.93); arrow(s, 10.8, 4.52, 10.8, 4.93);
    arrow(s, 4.02, 2.47, 5.18, 3.75, { color: C.accent1 });
    arrow(s, 4.02, 3.87, 5.18, 3.92, { color: C.accent1 });
    arrow(s, 4.02, 5.15, 5.18, 4.1, { color: C.accent1 });
    arrow(s, 4.02, 5.0, 5.18, 2.6, { color: C.accent1 });
    code(s, 0.6, 6.45, 12.1, 0.45, "docker compose up -d --build     # ports publiés sur 127.0.0.1 : 5002 → MLflow, 8000 → API", null, { size: 12 });
  }
  // ---------------------------------------------------------------- 5. Registre, promotion, API
  section("5. Registre, promotion et API");
  divider(5, "Registre, promotion et API", "Décider automatiquement quel modèle sert les utilisateurs.", "");
  {
    const s = content("Registre de modèles et alias champion", "Le suivi garde tous les essais, le registre seulement les modèles retenus. L'API demande « le champion », pas « la version 3 » : changer de modèle revient à déplacer l'alias. Les anciens stages (Staging, Production) sont dépréciés au profit des alias. Piège fréquent dans l'interface : l'onglet Models d'une expérience liste les modèles enregistrés par les runs, qui n'ont jamais d'alias ; l'alias champion se voit dans Model registry (barre de gauche), colonne Aliased versions. Le montrer en direct.");
    txt(s, "Suivi : tous les essais", { x: 0.6, y: 1.5, w: 5, h: 0.35, fontSize: 16, bold: true, color: C.accent6 });
    for (let i = 0; i < 6; i++) box(s, 0.6 + (i % 3) * 1.75, 1.95 + Math.floor(i / 3) * 0.75, 1.6, 0.6, `run ${i + 1}`, null, "file", { size: 13 });
    arrow(s, 5.85, 2.55, 6.6, 2.55, { color: C.accent1, label: "promote", ldy: -0.32 });
    txt(s, "Registre : les modèles retenus", { x: 6.7, y: 1.5, w: 6, h: 0.35, fontSize: 16, bold: true, color: C.accent4 });
    ["Version 1", "Version 2", "Version 3"].forEach((t, i) => box(s, 6.7 + i * 2.0, 1.95, 1.8, 0.7, t, null, "blue", { size: 15 }));
    box(s, 8.75, 3.35, 1.7, 0.7, "@champion", null, "main", { size: 16 });
    arrow(s, 9.6, 3.33, 9.6, 2.68, { color: C.accent1, width: 2 });
    card(s, 0.6, 4.55, 12.1, 2.0, "wheat");
    await iconCircle(s, 0.9, 4.85, 0.65, "FaArrowsRotate", C.accent3);
    txt(s, "L'alias est une étiquette mobile", { x: 1.8, y: 4.82, w: 10.6, h: 0.45, fontSize: 19, bold: true, color: C.accent3 });
    txt(s, "L'API charge toujours « le champion ». Pour mettre un nouveau modèle en service, promote déplace l'alias : l'API n'a pas besoin d'être modifiée.", { x: 1.8, y: 5.35, w: 10.6, h: 1.0, fontSize: 16 });
  }
  {
    const s = content("La règle de promotion", "Strictement supérieur : à égalité, on garde le modèle en place, car changer a un coût (vérifications, redémarrage de l'API). Chaque cas particulier a son message et son test.");
    const q = ["Un run candidat existe ?", "A-t-il le score cv_f1_macro_mean ?", "Un champion existe ?", "Le candidat est-il déjà le champion ?", "Score candidat > score champion ?"];
    const out = [["non", "Message : lancer d'abord uv run train", "red"], ["non", "Message : métrique absente", "red"], ["non", "PROMOUVOIR", "main"], ["oui", "Rien à faire : déjà champion", "file"], ["non", "Champion conservé (non promu)", "red"]];
    const down = ["oui", "oui", "oui", "non", "oui"];
    box(s, 2.0, 1.35, 2.6, 0.45, "uv run promote", null, "main", { size: 14 });
    q.forEach((t, i) => {
      const y = 2.0 + i * 0.86;
      arrow(s, 3.3, i === 0 ? 1.82 : y - 0.26, 3.3, y - 0.02, { label: i === 0 ? null : down[i - 1], ldx: 0.3, ldy: -0.15 });
      box(s, 0.9, y, 4.8, 0.6, t, null, "wheat", { size: 15 });
      box(s, 7.0, y + 0.03, 4.9, 0.54, out[i][1], null, out[i][2], { size: 14 });
      arrow(s, 5.72, y + 0.3, 6.98, y + 0.3, { label: out[i][0], ldy: -0.3 });
    });
    arrow(s, 3.3, 2.0 + 4 * 0.86 + 0.62, 3.3, 6.1, { label: "oui", ldx: 0.3, ldy: -0.15 });
    box(s, 0.9, 6.12, 4.8, 0.55, "PROMOUVOIR : nouvelle version + alias", null, "main", { size: 15 });
  }
  {
    const s = content("promote en action", "Sorties réelles, obtenues sur une base MLflow temporaire. Le candidat volontairement faible (20 arbres, profondeur 3) obtient 0,8472 et n'est pas promu.");
    table(s, 0.6, 1.55, 12.1, ["Situation", "Sortie de uv run promote"], [
      ["Base vide", "Aucun run candidat : lancer d'abord uv run train."],
      ["Premier candidat (0,9943)", "Version 1 promue champion (score 0.9943)."],
      ["Relance sans nouvel entraînement", "Le candidat est déjà le champion (version 1)."],
      ["Candidat moins bon (20 arbres, profondeur 3)", "Candidat non promu : 0.8472 <= 0.9943."],
    ], [4.6, 7.5], { size: 16, codeCols: [1], rowH: 0.6 });
    card(s, 0.6, 4.85, 12.1, 1.75, "soft");
    await iconCircle(s, 0.9, 5.1, 0.65, "FaShieldHalved");
    txt(s, "Une commande d'automatisation doit être prévisible dans tous les cas", { x: 1.8, y: 5.08, w: 10.6, h: 0.45, fontSize: 18, bold: true, color: C.accent1 });
    txt(s, "Pas de candidat, candidat sans score, déjà champion, champion sans score : chaque cas a son message clair et son test automatisé (11 tests pour promote.py).", { x: 1.8, y: 5.58, w: 10.6, h: 0.9, fontSize: 16 });
  }
  {
    const s = content("Une API pour servir le champion", "Au démarrage (lifespan, une seule fois) l'API résout l'alias et charge le modèle en mémoire. Sans champion, elle refuse de démarrer avec un message qui dit quoi faire. À chaque requête : validation, conversion float64, prédiction, réponse avec la version.");
    txt(s, "Au démarrage, une seule fois", { x: 0.6, y: 1.45, w: 6, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
    [["config.yaml", "réglages"], ["setup_mlflow", "connexion"], ["alias champion", "→ version n"], ["load_model", "en mémoire"], ["app.state", "modèle, version"]].forEach(([t, d], i) => {
      const x = 0.6 + i * 2.48;
      box(s, x, 1.9, 2.2, 0.95, t, d, "soft", { size: 15, subSize: 12 });
      if (i < 4) arrow(s, x + 2.22, 2.37, x + 2.46, 2.37);
    });
    txt(s, "À chaque requête POST /predict", { x: 0.6, y: 3.3, w: 6, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
    [["Requête JSON", "7 mesures", "file"], ["Validation", "CropInput (Pydantic)", "wheat"], ["float64", "pd.DataFrame", "soft"], ["predict", "modèle champion", "soft"], ["Réponse JSON", "culture + version", "main"]].forEach(([t, d, st], i) => {
      const x = 0.6 + i * 2.48;
      box(s, x, 3.75, 2.2, 0.95, t, d, st, { size: 15, subSize: 12 });
      if (i < 4) arrow(s, x + 2.22, 4.22, x + 2.46, 4.22);
    });
    arrow(s, 3.78, 4.72, 3.78, 5.35, { color: C.accent5, label: "invalide", ldx: 0.55, ldy: -0.15 });
    box(s, 2.6, 5.4, 2.4, 0.65, "Erreur 422", "+ détail du champ", "red", { size: 15, subSize: 12 });
    txt(s, "Le modèle n'est jamais appelé avec des données invalides.", { x: 5.6, y: 5.55, w: 7, h: 0.4, fontSize: 16, italic: true, color: C.accent6 });
  }
  {
    const s = content("Valider les entrées depuis le schéma", "build_input_model construit la classe Pydantic à partir de schema.yaml : une seule source de vérité pour l'entraînement et l'API. L'annotation entree: CropInput est lue par FastAPI à l'exécution ; Pylance ne peut pas connaître une classe créée dynamiquement, d'où le commentaire pyright: ignore. Alternative : écrire la classe à la main + un test de cohérence.");
    code(s, 0.6, 1.45, 7.0, 3.9, [
      "def build_input_model(config):",
      "    schema = load_yaml(config[\"dataset\"][\"schema\"])",
      "    target = config[\"dataset\"][\"target\"]",
      "    fields = {}",
      "    for name, rules in schema[\"columns\"].items():",
      "        if name == target:",
      "            continue",
      "        fields[name] = (",
      "            TYPES[rules[\"dtype\"]],",
      "            Field(ge=rules.get(\"min\"), le=rules.get(\"max\")),",
      "        )",
      "    return create_model(\"CropInput\", **fields)",
    ].join("\n"), "src/crop_recommendation_tp/api.py (extrait)", { size: 13 });
    code(s, 0.6, 5.55, 7.0, 1.1, "@app.post(\"/predict\")\ndef predict(entree: CropInput):  # pyright: ignore[reportInvalidTypeForm]", null, { size: 11 });
    txt(s, "POST /predict avec un pH de 15 :", { x: 8.0, y: 1.5, w: 4.7, h: 0.35, fontSize: 15, bold: true });
    code(s, 8.0, 1.95, 4.7, 2.5, ["→ 422", "{\"detail\": [{", "  \"type\": \"less_than_equal\",", "  \"loc\": [\"body\", \"ph\"],", "  \"msg\": \"Input should be less", "          than or equal to 14\"", "}]}"].join("\n"), null, { size: 13 });
    card(s, 8.0, 4.7, 4.7, 1.95, "soft");
    txt(s, "L'annotation n'est pas décorative : FastAPI s'en sert pour lire le JSON, le valider, renvoyer 422 et documenter /docs.", { x: 8.25, y: 4.88, w: 4.2, h: 1.6, fontSize: 15 });
  }
  {
    const s = content("Interroger l'API", "Démonstration en direct : docker compose up -d (ou uv run fastapi dev pour développer sans conteneur), puis /docs pour tester sans écrire de code. La réponse contient la version du modèle : chaque prédiction est traçable. Après une nouvelle promotion, redémarrer l'API.");
    code(s, 0.6, 1.45, 12.1, 1.75, [
      "docker compose up -d          # API sur http://127.0.0.1:8000  ·  documentation : /docs",
      "curl -X POST http://127.0.0.1:8000/predict -H \"Content-Type: application/json\" \\",
      "     -d '{\"N\": 90, \"P\": 42, \"K\": 43, \"temperature\": 20.8, \"humidity\": 82.0, \"ph\": 6.5, \"rainfall\": 202.9}'",
    ].join("\n"), "Terminal", { size: 13 });
    table(s, 0.6, 3.45, 12.1, ["Requête", "Réponse réelle"], [
      ["GET /health", "{\"status\": \"ok\", \"version\": \"1\", \"run_id\": \"4c4afe99…\"}"],
      ["N=90, P=42, K=43, 20,8 °C, 82 %, pH 6,5, 202,9 mm", "{\"culture\": \"rice\", \"version\": \"1\"}"],
      ["N=20, P=130, K=200, 22,5 °C, 92 %, pH 6,0, 110 mm", "{\"culture\": \"apple\", \"version\": \"1\"}"],
      ["pH = 15", "422 : Input should be less than or equal to 14"],
    ], [5.4, 6.7], { size: 15, codeCols: [1], rowH: 0.46 });
    card(s, 0.6, 5.95, 12.1, 0.7, "red");
    txt(s, "Le modèle est chargé au démarrage : après une promotion, docker compose restart api (vérifier avec /health).", { x: 0.85, y: 6.08, w: 11.6, h: 0.45, fontSize: 16 });
  }

  // ---------------------------------------------------------------- 6. Qualité et bilan
  section("6. Qualité et bilan");
  divider(6, "Qualité et bilan", "Des garde-fous automatiques, et ce qu'il reste à faire.", "");
  {
    const s = content("Pourquoi des tests automatisés ?", "Un test exécute un bout de code dans une situation précise et vérifie le résultat. On les lance tous en une commande. Présenter les notions pytest utilisées dans le projet.");
    const b = [["FaBell", "Détecter les régressions", "Ce qui marchait et ne marche plus est signalé immédiatement."], ["FaBookOpen", "Documenter", "Un test se lit comme un exemple du comportement attendu."], ["FaPersonRunning", "Oser modifier", "On améliore le code sans crainte de tout casser."]];
    for (let i = 0; i < 3; i++) {
      const x = 0.6 + i * 4.1;
      card(s, x, 1.5, 3.8, 2.4, "soft");
      await iconCircle(s, x + 0.3, 1.75, 0.7, b[i][0]);
      txt(s, b[i][1], { x: x + 0.3, y: 2.6, w: 3.3, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
      txt(s, b[i][2], { x: x + 0.3, y: 3.05, w: 3.3, h: 0.75, fontSize: 15 });
    }
    txt(s, "Les notions de pytest utilisées", { x: 0.6, y: 4.2, w: 12, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
    const n = [["test_…", "une fonction de test"], ["assert", "la vérification"], ["fixture", "prépare le test"], ["conftest.py", "fixtures partagées"], ["tmp_path", "dossier temporaire"], ["monkeypatch", "remplacer un réglage"], ["capsys", "capturer l'affichage"], ["TestClient", "appeler l'API"]];
    n.forEach(([t, d], i) => box(s, 0.6 + (i % 4) * 3.07, 4.75 + Math.floor(i / 4) * 0.95, 2.85, 0.8, t, d, "file", { size: 14, subSize: 12 }));
  }
  {
    const s = content("Stratégie de test", "Données fabriquées, petites et lisibles : les tests ne dépendent pas du vrai CSV et tournent partout, y compris en CI. Modèle factice (DummyClassifier) pour tester la logique, pas la qualité. Une base MLflow SQLite neuve pour chaque test.");
    [["test_validation.py", "9 tests", "validation.py", "règles du schéma"], ["test_data.py", "4 tests", "data.py", "découpage, plis"], ["test_train.py", "1 test", "train.py + tune.py", "même score"], ["test_promote.py", "11 tests", "promote.py", "règle de promotion"], ["test_api.py", "5 tests", "api.py", "routes et validation"]].forEach(([t, n, m, d], i) => {
      const y = 1.45 + i * 0.95;
      box(s, 0.6, y, 3.2, 0.8, t, n, "wheat", { size: 16, subSize: 13 });
      arrow(s, 3.85, y + 0.4, 4.75, y + 0.4, { label: "vérifie", ldy: -0.3 });
      box(s, 4.8, y, 3.0, 0.8, m, d, "soft", { size: 16, subSize: 13 });
    });
    card(s, 8.4, 1.5, 4.3, 4.55, "blue");
    txt(s, "tests/conftest.py", { x: 8.65, y: 1.68, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: C.accent4, fontFace: "Courier New" });
    txt(s, [
      { text: "Fixture config partagée :", options: { bold: true, breakLine: true } },
      { text: "base MLflow SQLite neuve pour chaque test", options: { bullet: true, breakLine: true } },
      { text: "dossier temporaire", options: { bullet: true, breakLine: true } },
      { text: "aucun serveur nécessaire", options: { bullet: true, breakLine: true } },
      { text: "état remis à zéro après le test", options: { bullet: true } },
    ], { x: 8.65, y: 2.2, w: 3.8, h: 3.6, fontSize: 15, paraSpaceAfter: 6 });
    arrow(s, 8.38, 4.6, 7.82, 4.7, { color: C.accent4, dashed: true });
    arrow(s, 8.38, 5.5, 7.82, 5.65, { color: C.accent4, dashed: true });
    txt(s, "Un test par cas, y compris les cas d'erreur : c'est là que se cachent les bugs.", { x: 0.6, y: 6.35, w: 12.1, h: 0.4, fontSize: 16, italic: true, color: C.accent6, align: "center" });
  }
  {
    const s = content("Résultats : 30 tests sur 30", "Exécution réelle : 30 passed en 36,5 s. Les tests de promote sont les plus lents (enregistrement de modèles MLflow). Ruff : aucune erreur, code correctement formaté. Ce qui n'est pas testé : train et tune de bout en bout, log_run, et la qualité du modèle (voir exercices). Le plan de test détaillé est dans le guide.");
    txt(s, "30 / 30", { x: 0.6, y: 1.5, w: 4.5, h: 1.4, fontSize: 80, bold: true, color: C.accent1, fontFace: "Cambria", valign: "middle" });
    txt(s, "tests réussis", { x: 0.6, y: 2.9, w: 4.5, h: 0.4, fontSize: 18, color: C.accent6 });
    stat(s, 0.6, 3.6, 2.2, "37 s", "pour toute la suite", C.accent3);
    stat(s, 2.9, 3.6, 2.2, "0", "erreur Ruff", C.accent3);
    hbars(s, 5.6, 1.5, 7.1, 3.9, [["test_validation.py", 9, C.accent1], ["test_data.py", 4, C.accent1], ["test_train.py", 1, C.accent1], ["test_promote.py", 11, C.accent1], ["test_api.py", 5, C.accent1]], { title: "Nombre de tests par fichier (tous réussis)", labelW: 2.4, valueW: 0.6, min: 0, max: 11, fmt: (v) => String(v), labelSize: 16, valueSize: 18 });
    code(s, 0.6, 5.75, 12.1, 0.85, "$ uv run pytest\n======================== 30 passed, 1 warning in 36.54s ========================", null, { size: 13 });
  }
  {
    const s = content("Un bug instructif : l'état global", "Le test passait seulement parce qu'il était exécuté en premier. mlflow.set_tracking_uri est global et l'emporte sur la variable d'environnement : le test suivant héritait de la base du précédent. Correction : régler l'adresse au début, l'effacer à la fin. Leçon : un test doit donner le même résultat seul, en premier ou en dernier.");
    card(s, 0.6, 1.5, 5.85, 4.1, "red");
    txt(s, "Avant : dépend de l'ordre", { x: 0.85, y: 1.65, w: 5.4, h: 0.4, fontSize: 17, bold: true, color: C.accent5 });
    code(s, 0.85, 2.15, 5.35, 3.2, ["@pytest.fixture", "def config(tmp_path, monkeypatch):", "    ...", "    monkeypatch.setenv(", "        \"MLFLOW_TRACKING_URI\", uri)", "    return {...}", "", "# le réglage global du test", "# précédent reste actif !"].join("\n"), null, { size: 13 });
    card(s, 6.85, 1.5, 5.85, 4.1, "soft");
    txt(s, "Après : chaque test est isolé", { x: 7.1, y: 1.65, w: 5.4, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
    code(s, 7.1, 2.15, 5.35, 3.2, ["@pytest.fixture", "def config(tmp_path, monkeypatch):", "    ...", "    monkeypatch.setenv(", "        \"MLFLOW_TRACKING_URI\", uri)", "    mlflow.set_tracking_uri(uri)", "    yield {...}", "    mlflow.set_tracking_uri(None)", "# avant / après le test"].join("\n"), null, { size: 13 });
    txt(s, "Un test ne doit jamais dépendre de l'ordre d'exécution.", { x: 0.6, y: 5.95, w: 12.1, h: 0.5, fontSize: 20, bold: true, color: C.accent1, align: "center" });
  }
  {
    const s = content("Ruff et intégration continue", "Ruff analyse le code sans l'exécuter ; dans VS Code, il trie les imports et corrige à chaque enregistrement. La CI rejoue tout sur une machine neuve à chaque push : uv sync --locked échoue si uv.lock n'est pas à jour. Avant chaque commit, lancer les trois mêmes commandes en local.");
    const steps = [["git push", null, "file"], ["checkout", "le code", "soft"], ["setup-uv", "installe uv", "soft"], ["uv sync --locked", "environnement", "soft"], ["ruff check", "erreurs, imports", "soft"], ["ruff format --check", "mise en forme", "soft"], ["pytest", "30 tests", "soft"], ["✓ / ✗", "statut du commit", "main"]];
    txt(s, "GitHub Actions, à chaque push et pull request", { x: 0.6, y: 1.45, w: 12, h: 0.35, fontSize: 16, bold: true, color: C.accent1 });
    steps.forEach(([t, d, st], i) => {
      const x = 0.6 + i * 1.53;
      box(s, x, 1.95, 1.38, 1.1, t, d, st, { size: 13, subSize: 11 });
      if (i < 7) arrow(s, x + 1.39, 2.5, x + 1.52, 2.5);
    });
    table(s, 0.6, 3.5, 7.4, ["Règles Ruff", "Ce qu'elles vérifient"], [
      ["F", "imports inutilisés ou en double"],
      ["I", "ordre des imports"],
      ["E4, E7, E9", "erreurs de syntaxe et de style graves"],
      ["SIM", "code simplifiable"],
      ["RUF", "règles propres à Ruff"],
    ], [2.0, 5.4], { size: 15, codeCols: [0], rowH: 0.45 });
    code(s, 8.4, 3.5, 4.3, 2.4, ["# avant chaque commit", "uv run ruff check .", "uv run ruff format --check .", "uv run pytest", "", "# corriger", "uv run ruff check . --fix"].join("\n"), "Terminal", { size: 13 });
  }
  {
    const s = content("Rejouer toute la chaîne", "Le parcours complet ; chaque commande a été exécutée pour obtenir les résultats montrés dans ce cours. Bon exercice de début de séance pratique.");
    const st = [["Installer", "uv sync"], ["Récupérer les données", "uv run dvc pull"], ["Tester", "uv run pytest"], ["Démarrer les services", "docker compose up -d --build"], ["Chercher (facultatif)", "uv run tune"], ["Entraîner", "uv run train"], ["Promouvoir", "uv run promote"], ["Recharger l'API", "docker compose restart api"]];
    st.forEach(([t, c], i) => {
      const col = Math.floor(i / 4), row = i % 4;
      const x = 0.6 + col * 6.2, y = 1.5 + row * 1.25;
      numCircle(s, x, y + 0.1, 0.62, i + 1, C.accent1, 18);
      txt(s, t, { x: x + 0.85, y: y + 0.02, w: 4.9, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
      code(s, x + 0.85, y + 0.45, 4.9, 0.5, c, null, { size: 14 });
    });
  }
  {
    const s = content("Les leçons des problèmes rencontrés", "Chaque problème rencontré pendant la construction illustre une bonne pratique. Le guide détaille symptôme, cause et correction pour chacun.");
    const L = [
      ["FaKey", ".env manquant", "Les secrets ne sont jamais dans le dépôt ; un modèle les documente."],
      ["FaPlug", "Deux ports différents", "Une information écrite deux fois finit par diverger."],
      ["FaShuffle", "Test dépendant de l'ordre", "Un test doit être isolé."],
      ["FaArrowDownAZ", "Imports en désordre", "Automatiser ce qui peut l'être."],
      ["FaEye", "Avertissement de l'éditeur", "L'éditeur analyse sans exécuter ; ignorer de façon ciblée."],
      ["FaScaleBalanced", "Deux découpages en plis", "Une même règle écrite deux fois diverge : build_cv."],
    ];
    for (let i = 0; i < L.length; i++) {
      const x = 0.6 + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.6;
      card(s, x, y, 3.8, 2.35, i % 2 ? "file" : "soft");
      await iconCircle(s, x + 0.3, y + 0.3, 0.62, L[i][0], C.accent3);
      txt(s, L[i][1], { x: x + 1.1, y: y + 0.42, w: 2.6, h: 0.45, fontSize: 17, bold: true, color: C.accent1 });
      txt(s, L[i][2], { x: x + 0.3, y: y + 1.15, w: 3.3, h: 1.0, fontSize: 16 });
    }
  }
  {
    const s = content("Vers la phase 2 : la mise en production", "Ce qui manque avant une vraie mise en production. Les améliorations repérées dans le code (tri implicite dans promote, erreur lente de l'API quand le serveur est arrêté) sont reprises en exercices.");
    table(s, 0.6, 1.5, 12.1, ["Aujourd'hui (phase 1)", "Conséquence", "Piste pour la phase 2"], [
      ["Stockage DVC dans un dossier local", "Données accessibles sur un seul poste", "Stockage partagé (S3, Drive, SSH)"],
      ["API en conteneur sur un seul poste", "Inaccessible de l'extérieur, pas de HTTPS", "VPS, proxy inverse, HTTPS"],
      ["Champion chargé au démarrage", "Promotion prise en compte au redémarrage", "Rechargement ou redéploiement automatique"],
      ["Pas de surveillance", "Dérive des données invisible", "Journaliser et surveiller les requêtes"],
      ["train → promote à la main", "Risque d'oubli", "Pipeline automatisé (CI/CD)"],
      ["Pas d'authentification", "Tout le réseau peut appeler l'API", "Authentification, HTTPS"],
    ], [4.0, 4.0, 4.1], { size: 16, rowH: 0.64 });
  }
  {
    const s = content("À vous de jouer", "Exercices détaillés dans le guide (9 au total), avec ce qu'il faut observer. Les trois derniers du guide portent sur les améliorations du code.");
    const E = [
      ["★", "Le schéma protège", "Passer max de ph à 8 : train s'arrête, l'API répond 422."],
      ["★", "Un candidat moins bon", "20 arbres, profondeur 3 : promote refuse (0,8472)."],
      ["★", "Remonter la piste", "De /health au commit et aux données."],
      ["★★", "Données modifiées", "dvc status, puis data_md5 se termine par -modified."],
      ["★★", "Un test de plus", "N = 12,5 → 422 : écrire le test."],
      ["★★", "Casser l'alignement des plis", "Remettre cv=5 dans train : quel test échoue, et pourquoi ?"],
    ];
    E.forEach(([lvl, t, d], i) => {
      const x = 0.6 + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.6;
      card(s, x, y, 3.8, 2.35, "file");
      numCircle(s, x + 0.3, y + 0.3, 0.55, i + 1, C.accent1, 16);
      txt(s, lvl, { x: x + 2.6, y: y + 0.35, w: 0.95, h: 0.4, fontSize: 18, color: C.accent3, align: "right" });
      txt(s, t, { x: x + 0.3, y: y + 1.0, w: 3.3, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
      txt(s, d, { x: x + 0.3, y: y + 1.45, w: 3.3, h: 0.8, fontSize: 15 });
    });
  }
  {
    const s = pres.addSlide({ masterName: "TITRE", sectionTitle: currentSection() });
    s.addText("À retenir", { placeholder: "title" });
    s.addText("La démarche MLOps en cinq idées", { placeholder: "body" });
    const K = ["Un modèle = code + données + environnement : on versionne les trois.", "Les réglages et le contrat des données sont écrits une seule fois.", "On choisit en validation croisée ; le test ne sert qu'une fois.", "Chaque run, chaque prédiction remonte au code et aux données.", "Des tests et une CI vérifient tout, à chaque modification."];
    K.forEach((k, i) => {
      s.addText(String(i + 1), { shape: pres.shapes.OVAL, x: 0.8, y: 4.95 + i * 0.47, w: 0.36, h: 0.36, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, color: C.text1, bold: true, fontSize: 12, align: "center", valign: "middle", margin: 0, objectName: oname("numéro") });
      txt(s, k, { x: 1.35, y: 4.96 + i * 0.47, w: 11, h: 0.36, fontSize: 16, color: C.background1, valign: "middle" });
    });
    s.addImage({ data: await icon("FaWheatAwn", HEX.moss, 512), x: 10.2, y: 1.4, w: 2.3, h: 2.3, altText: "Épi de blé", objectName: oname("illustration") });
    s.addNotes("Conclure sur la phase 2 : la mise en production s'appuiera sur tout ce socle (conteneur de l'API, stockage partagé, pipeline automatisé, surveillance).");
  }

  await save(OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
