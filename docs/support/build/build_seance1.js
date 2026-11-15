// Séance 1 : ouverture du cours — la chaîne MLOps complète et le cycle de vie du modèle
const path = require("path");
const { makeDeck, HEX } = require("./deck_lib.js");

const OUT = process.argv[2] || path.join(__dirname, "..", "seance1_demarche_mlops.pptx");

const {
  pres, C, icon, oname, txt, box, arrow, code, iconCircle, iconRow, card, numCircle, stat, table,
  section, content, divider, currentSection, save,
} = makeDeck({ title: "Séance 1 : la démarche MLOps", subject: "Ouverture du cours : la chaîne complète et le cycle de vie du modèle" });

// Étiquette de statut : en place / à construire
function badge(s, x, y, label, done) {
  s.addText(label, {
    shape: pres.shapes.ROUNDED_RECTANGLE, x, y, w: 1.55, h: 0.34, rectRadius: 0.17,
    fill: { color: done ? C.accent1 : HEX.wheatBg }, line: { color: done ? C.accent1 : C.accent3, width: 1 },
    color: done ? C.background1 : C.accent3, bold: true, fontSize: 11, align: "center", valign: "middle", margin: 0, objectName: oname("statut"),
  });
}

// Histogramme dessiné en formes (s'affiche dans PowerPoint, Keynote et Google Slides)
function histogram(s, x, y, w, h, series, o) {
  const bins = o.bins, n = bins.length, bw = w / n;
  const max = Math.max(...series.flatMap((se) => se.values));
  s.addShape(pres.shapes.LINE, { x, y: y + h, w, h: 0, line: { color: HEX.grey, width: 1 }, objectName: oname("axe") });
  series.forEach((se) => se.values.forEach((v, i) => {
    const bh = (v / max) * (h - 0.1);
    if (bh < 0.01) return;
    s.addShape(pres.shapes.RECTANGLE, { x: x + i * bw + 0.02, y: y + h - bh, w: bw - 0.04, h: bh, fill: { color: se.color, transparency: se.transparency || 0 }, line: { color: se.color, width: 0 }, objectName: oname("barre") });
  }));
  bins.forEach((b, i) => { if (i % o.labelEvery === 0) txt(s, String(b), { x: x + i * bw - 0.25, y: y + h + 0.05, w: 0.5 + bw, h: 0.28, fontSize: 11, color: C.accent6, align: "center" }); });
  if (o.axisLabel) txt(s, o.axisLabel, { x, y: y + h + 0.32, w, h: 0.3, fontSize: 12, color: C.accent6, align: "center", italic: true });
}
const gauss = (mu, sd, bins) => bins.map((b) => Math.exp(-0.5 * ((b - mu) / sd) ** 2));

async function build() {
  // ================================================================ Ouverture
  section("Ouverture");
  {
    const s = pres.addSlide({ masterName: "TITRE", sectionTitle: currentSection() });
    s.addText("La démarche MLOps", { placeholder: "title" });
    s.addText("Séance 1 · Toute la chaîne, du poste de travail à la production", { placeholder: "body" });
    s.addImage({ data: await icon("FaSeedling", HEX.moss, 512), x: 9.9, y: 1.7, w: 2.6, h: 2.6, altText: "Pousse", objectName: oname("illustration") });
    txt(s, "Cas d'étude : recommander une culture à partir de 7 mesures du sol et du climat", { x: 0.8, y: 6.4, w: 10, h: 0.4, fontSize: 15, color: HEX.paleMoss });
    s.addNotes("Ouverture : avant d'écrire une ligne de code, on montre la destination. À la fin des trois séances, les étudiants auront construit et automatisé toute cette chaîne. Cette introduction dure 30 à 45 minutes ; le reste de la séance est consacré à rendre le projet reproductible.");
  }
  {
    const s = content("Au programme de la séance", "Deux temps de présentation (la chaîne complète, puis le cycle de vie), puis l'atelier : transformer un notebook en projet reproductible.");
    const parts = [
      ["FaRoute", "La chaîne MLOps", "Ce que nous allons construire, en local et en production, et avec quels outils"],
      ["FaArrowsRotate", "Le cycle de vie", "Pourquoi un modèle n'est jamais « fini » : les événements qui le remettent en cause"],
      ["FaLaptopCode", "Atelier", "Du notebook à un projet reproductible : uv, configuration, DVC, schéma, tests"],
    ];
    for (let i = 0; i < 3; i++) {
      const x = 0.6 + i * 4.1;
      card(s, x, 1.6, 3.8, 4.6, i === 2 ? "wheat" : "soft");
      numCircle(s, x + 0.3, 1.9, 0.62, i + 1, i === 2 ? C.accent3 : C.accent1, 20);
      await iconCircle(s, x + 2.85, 1.9, 0.62, parts[i][0], i === 2 ? C.accent3 : C.accent1);
      txt(s, parts[i][1], { x: x + 0.3, y: 2.85, w: 3.2, h: 0.5, fontSize: 22, bold: true, color: i === 2 ? C.accent3 : C.accent1 });
      txt(s, parts[i][2], { x: x + 0.3, y: 3.5, w: 3.2, h: 2.4, fontSize: 16 });
    }
  }
  {
    const s = content("Le modèle n'est qu'une petite partie du système", "Idée tirée de l'article « Hidden Technical Debt in Machine Learning Systems » (Google, 2015) : dans un système de ML réel, le code du modèle est une toute petite partie. Tout le reste, c'est l'objet du MLOps. Demander aux étudiants ce qui leur manquerait pour mettre leur notebook en service.");
    const ring = [
      ["Données", "versionnées"], ["Validation", "des données"], ["Configuration", "externalisée"], ["Environnement", "reproductible"],
      ["Suivi", "des expériences"], ["Choix", "du modèle"], ["Service", "API"], ["Surveillance", "en production"], ["Tests", "et CI/CD"],
    ];
    const cx = 6.66, cy = 3.85, rx = 4.6, ry = 2.0;
    ring.forEach(([t, d], i) => {
      const a = -Math.PI / 2 + (i * 2 * Math.PI) / ring.length;
      const bx = cx + rx * Math.cos(a) - 1.15, by = cy + ry * Math.sin(a) - 0.4;
      box(s, bx, by, 2.3, 0.8, t, d, "file", { size: 15, subSize: 12 });
    });
    box(s, cx - 0.95, cy - 0.45, 1.9, 0.9, "Code du modèle", null, "main", { size: 15 });
    txt(s, "Tout ce qui entoure le modèle, c'est le MLOps.", { x: 0.6, y: 6.55, w: 12.1, h: 0.4, fontSize: 18, bold: true, color: C.accent1, align: "center" });
  }
  {
    const s = content("Trois séances, une chaîne complète", "Chaque séance s'appuie sur la précédente. On part du poste de l'étudiant et on finit sur un serveur, avec une chaîne automatisée.");
    const S = [
      ["1", "Du notebook à un projet reproductible", "uv · configuration · DVC · schéma · tests", "local"],
      ["2", "Suivre, choisir et servir un modèle", "MLflow · registre · promotion · API · Docker", "local"],
      ["3", "Déployer et automatiser la chaîne", "VPS · CI/CD · surveillance · réentraînement", "production"],
    ];
    s.addShape(pres.shapes.LINE, { x: 1.2, y: 2.25, w: 10.9, h: 0, line: { color: C.accent2, width: 3 }, objectName: oname("frise") });
    S.forEach(([n, t, d, zone], i) => {
      const x = 0.6 + i * 4.1;
      numCircle(s, x + 1.55, 1.9, 0.7, n, zone === "production" ? C.accent4 : C.accent1, 22);
      card(s, x, 2.9, 3.8, 3.0, zone === "production" ? "blue" : "soft");
      txt(s, `Séance ${n}`, { x: x + 0.3, y: 3.1, w: 3.2, h: 0.35, fontSize: 14, bold: true, color: C.accent6 });
      txt(s, t, { x: x + 0.3, y: 3.5, w: 3.2, h: 1.0, fontSize: 19, bold: true, color: zone === "production" ? C.accent4 : C.accent1 });
      txt(s, d, { x: x + 0.3, y: 4.6, w: 3.2, h: 0.8, fontSize: 14 });
      txt(s, zone === "production" ? "en production" : "en local", { x: x + 0.3, y: 5.4, w: 3.2, h: 0.35, fontSize: 13, italic: true, color: C.accent6 });
    });
  }

  // ================================================================ Partie A
  section("1. La chaîne MLOps");
  divider(1, "La chaîne MLOps", "Ce que nous allons construire, et avec quels outils.", "Rappeler la règle : en local on construit et on expérimente ; en production on sert, on surveille et on réagit.");
  {
    const s = content("La chaîne complète", "C'est la carte de tout le cours : on y reviendra à chaque séance pour situer ce qu'on construit. Lire de gauche à droite : le poste de travail, GitHub qui fait le pont automatiquement, puis le serveur de production. La surveillance, à droite, renvoie vers le poste : c'est elle qui déclenche de nouveaux entraînements. Les commandes train et promote envoient leurs runs et leurs modèles au serveur MLflow (local en séance 2, celui du VPS en séance 3).");
    // zones
    card(s, 0.5, 1.45, 4.3, 4.85, "soft");
    txt(s, "LOCAL · poste de travail", { x: 0.5, y: 1.55, w: 4.3, h: 0.35, fontSize: 14, bold: true, color: C.accent1, align: "center" });
    card(s, 5.15, 1.45, 2.9, 4.85, "file");
    txt(s, "GITHUB", { x: 5.15, y: 1.55, w: 2.9, h: 0.35, fontSize: 14, bold: true, color: C.text1, align: "center" });
    card(s, 8.4, 1.45, 4.45, 4.85, "blue");
    txt(s, "PRODUCTION · VPS OVH", { x: 8.4, y: 1.55, w: 4.45, h: 0.35, fontSize: 14, bold: true, color: C.accent4, align: "center" });
    // local
    [["Notebook → paquet src/", "explorer, puis industrialiser"], ["uv · config · schéma", "environnement, réglages, contrat"], ["Données · DVC", "versionnées et validées"], ["tune · train · promote", "entraîner, choisir (runs → MLflow)"], ["MLflow · PostgreSQL · API", "Docker Compose"], ["pytest · Ruff", "vérifier avant de pousser"]]
      .forEach(([t, d], i) => box(s, 0.7, 2.0 + i * 0.7, 3.9, 0.6, t, d, "file", { size: 13, subSize: 11 }));
    // github
    box(s, 5.35, 2.0, 2.5, 0.8, "Dépôt Git", "code, config, .dvc", "file", { size: 14, subSize: 11 });
    box(s, 5.35, 3.1, 2.5, 0.8, "CI", "Ruff + tests", "main", { size: 15, subSize: 11 });
    box(s, 5.35, 4.2, 2.5, 0.8, "CD", "image + déploiement", "main", { size: 15, subSize: 11 });
    box(s, 5.35, 5.3, 2.5, 0.8, "Registre d'images", "GHCR", "file", { size: 14, subSize: 11 });
    arrow(s, 6.6, 2.82, 6.6, 3.08); arrow(s, 6.6, 3.92, 6.6, 4.18); arrow(s, 6.6, 5.02, 6.6, 5.28);
    // production
    box(s, 8.6, 2.0, 4.05, 0.6, "Caddy : HTTPS, nom de domaine", null, "file", { size: 13 });
    box(s, 8.6, 2.8, 1.95, 0.85, "API", "conteneur", "wheat", { size: 15, subSize: 11 });
    box(s, 10.7, 2.8, 1.95, 0.85, "MLflow", "+ PostgreSQL", "main", { size: 15, subSize: 11 });
    box(s, 8.6, 3.85, 4.05, 0.7, "Stockage objet (S3)", "données DVC · artefacts · sauvegardes", "file", { size: 13, subSize: 11 });
    box(s, 8.6, 4.75, 1.95, 0.85, "Surveillance", "modèle : Evidently", "red", { size: 13, subSize: 11 });
    box(s, 10.7, 4.75, 1.95, 0.85, "Surveillance", "service (perspective)", "red", { size: 13, subSize: 11, dashed: true });
    // flux
    arrow(s, 4.82, 2.4, 5.33, 2.4, { color: C.accent1, width: 2, label: "git push", ldy: -0.32 });
    arrow(s, 7.87, 4.6, 8.58, 3.2, { color: C.accent1, width: 2, label: "déploie", ldx: 0.45, ldy: -0.05 });
    // retour de la surveillance vers le poste, sous les trois zones
    arrow(s, 10.6, 5.62, 10.6, 6.55, { color: C.accent5, width: 2, noHead: true });
    arrow(s, 10.6, 6.55, 2.65, 6.55, { color: C.accent5, width: 2, noHead: true });
    arrow(s, 2.65, 6.55, 2.65, 6.33, { color: C.accent5, width: 2 });
    txt(s, "alerte de dérive → nouvelles données, nouvel entraînement", { x: 3.0, y: 6.6, w: 7.4, h: 0.3, fontSize: 12, italic: true, bold: true, color: C.accent5, align: "center" });
  }
  {
    const s = content("En local : construire et expérimenter", "Tout ce qui se fait sur le poste du data scientist. C'est le contenu des séances 1 et 2 : à la fin de la séance 2, toute cette colonne fonctionne sur le poste de chaque étudiant.");
    const rows = [
      ["FaBoxOpen", "uv", "Le même environnement Python sur tous les postes (uv.lock)", 1],
      ["FaSliders", "config.yaml · schema.yaml", "Les réglages et le contrat des données, écrits une seule fois", 1],
      ["FaDatabase", "DVC", "Les données versionnées à côté du code", 1],
      ["FaVial", "pytest · Ruff", "Des vérifications automatiques à chaque modification", 1],
      ["FaFlask", "MLflow", "Chaque entraînement tracé ; le meilleur modèle désigné par un alias", 2],
      ["FaDocker", "Docker Compose", "MLflow, PostgreSQL et l'API lancés en une commande", 2],
      ["FaBolt", "FastAPI", "Le modèle interrogeable par n'importe quelle application", 2],
    ];
    for (let i = 0; i < rows.length; i++) {
      const [ic, t, d, n] = rows[i];
      const y = 1.45 + i * 0.75;
      await iconCircle(s, 0.6, y, 0.55, ic);
      txt(s, t, { x: 1.35, y: y + 0.1, w: 3.4, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
      txt(s, d, { x: 4.8, y: y + 0.1, w: 6.4, h: 0.4, fontSize: 16 });
      txt(s, `séance ${n}`, { x: 11.3, y: y + 0.1, w: 1.4, h: 0.4, fontSize: 14, color: C.accent6, align: "right" });
    }
  }
  {
    const s = content("GitHub : le pont automatisé", "La CI existe déjà dans le projet : à chaque push, une machine neuve installe l'environnement et lance Ruff et les tests. La CD sera construite en séance 3 : construire l'image de l'API, la publier, puis la déployer sur le VPS. Un commit qui casse un test n'atteint jamais la production.");
    const st = [["git push", null, "file"], ["CI", "Ruff · tests", "main"], ["Image Docker", "de l'API", "soft"], ["Registre d'images", "GHCR", "soft"], ["Déploiement", "sur le VPS", "blue"]];
    st.forEach(([t, d, sty], i) => {
      const x = 0.6 + i * 2.5;
      box(s, x, 1.75, 2.2, 1.1, t, d, sty, { size: 17, subSize: 13 });
      if (i < 4) arrow(s, x + 2.22, 2.3, x + 2.48, 2.3);
    });
    txt(s, "Intégration continue (CI)", { x: 0.6, y: 3.05, w: 4.7, h: 0.35, fontSize: 15, bold: true, color: C.accent1, align: "center" });
    txt(s, "Déploiement continu (CD)", { x: 5.6, y: 3.05, w: 7.1, h: 0.35, fontSize: 15, bold: true, color: C.accent4, align: "center" });
    badge(s, 2.2, 3.5, "en place", true);
    badge(s, 8.35, 3.5, "séance 3", false);
    card(s, 0.6, 4.35, 5.85, 2.2, "soft");
    txt(s, "CI : « le code est-il correct ? »", { x: 0.85, y: 4.5, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
    txt(s, "À chaque push, sur une machine neuve : installer exactement l'environnement, vérifier le code, lancer les tests. Si une étape échoue, le commit est marqué en rouge.", { x: 0.85, y: 5.0, w: 5.4, h: 1.4, fontSize: 15 });
    card(s, 6.85, 4.35, 5.85, 2.2, "blue");
    txt(s, "CD : « le livrer automatiquement »", { x: 7.1, y: 4.5, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.accent4 });
    txt(s, "Si la CI passe : construire l'image de l'API, la publier, et mettre à jour le serveur. Aucune manipulation à la main sur la production.", { x: 7.1, y: 5.0, w: 5.4, h: 1.4, fontSize: 15 });
  }
  {
    const s = content("En production : servir, surveiller, réagir", "Proposition d'architecture pour la séance 3, sur un VPS OVH. Seul Caddy est exposé à Internet ; MLflow est protégé par un mot de passe ; les données et les sauvegardes sont hors du serveur, dans un stockage objet. La surveillance du service (Prometheus, Grafana) est présentée comme une perspective.");
    card(s, 0.6, 1.45, 7.6, 5.15, "blue");
    txt(s, "VPS OVH (Docker Compose)", { x: 0.6, y: 1.55, w: 7.6, h: 0.35, fontSize: 14, bold: true, color: C.accent4, align: "center" });
    box(s, 0.85, 2.0, 7.1, 0.7, "Caddy", "seul point d'entrée : HTTPS automatique, mot de passe devant MLflow", "file", { size: 15, subSize: 12 });
    box(s, 0.85, 3.05, 2.2, 1.0, "API", "sert le champion", "wheat", { size: 16, subSize: 12 });
    box(s, 3.3, 3.05, 2.2, 1.0, "MLflow", "suivi, registre", "main", { size: 16, subSize: 12 });
    box(s, 5.75, 3.05, 2.2, 1.0, "PostgreSQL", "non exposé", "blue", { size: 16, subSize: 12 });
    arrow(s, 1.95, 2.72, 1.95, 3.03); arrow(s, 4.4, 2.72, 4.4, 3.03); arrow(s, 3.07, 3.55, 3.28, 3.55); arrow(s, 5.52, 3.55, 5.73, 3.55);
    box(s, 0.85, 4.4, 3.4, 1.0, "Journal des requêtes", "ce que l'API reçoit", "file", { size: 15, subSize: 12 });
    box(s, 4.55, 4.4, 3.4, 1.0, "Evidently", "rapport de dérive, chaque jour", "red", { size: 15, subSize: 12 });
    arrow(s, 1.95, 4.07, 1.95, 4.38); arrow(s, 4.27, 4.9, 4.53, 4.9);
    box(s, 0.85, 5.65, 7.1, 0.7, "Sauvegardes quotidiennes", "base PostgreSQL et artefacts, copiés hors du serveur", "file", { size: 14, subSize: 12 });
    box(s, 8.75, 1.45, 3.95, 1.45, "Stockage objet (S3)", "OVH Object Storage\ndonnées DVC · artefacts · sauvegardes", "file", { size: 16, subSize: 12 });
    box(s, 8.75, 3.2, 3.95, 1.45, "Utilisateurs", "applications qui appellent\nhttps://api.…/predict", "soft", { size: 16, subSize: 12 });
    box(s, 8.75, 4.95, 3.95, 1.4, "Prometheus + Grafana", "surveillance du service\n(perspective)", "red", { size: 16, subSize: 12, dashed: true });
    arrow(s, 8.73, 3.9, 8.0, 2.4, { color: C.accent1 });
  }
  {
    const s = content("Un outil, deux rôles : local et production", "Le tableau montre que les mêmes outils changent de rôle selon la zone. La dernière colonne situe chaque élément dans le cours.");
    table(s, 0.6, 1.45, 12.1, ["Besoin", "Technologie", "En local", "En production", "Séance"], [
      ["Environnement reproductible", "uv · uv.lock", "uv sync", "image Docker", "1"],
      ["Données versionnées", "DVC", "dossier local", "stockage objet (S3)", "1 → 3"],
      ["Données valides", "schéma", "à l'entraînement", "aussi à l'entrée de l'API", "1"],
      ["Qualité du code", "pytest · Ruff", "avant chaque commit", "CI GitHub Actions", "1 → 3"],
      ["Suivi des expériences", "MLflow + PostgreSQL", "Docker Compose", "conteneurs sur le VPS", "2 → 3"],
      ["Choix du modèle", "registre · alias", "uv run promote", "automatisé", "2 → 3"],
      ["Service du modèle", "FastAPI · Docker", "localhost:8000", "HTTPS, nom de domaine", "2 → 3"],
      ["Déploiement", "GitHub Actions", "à la main", "automatique (CD)", "3"],
      ["Surveillance", "Evidently", "—", "rapports de dérive", "3"],
    ], [3.0, 2.4, 2.3, 3.2, 1.2], { size: 15, rowH: 0.52, boldFirst: true });
  }
  {
    const s = content("Surveiller le modèle n'est pas surveiller le service", "Point clé : un modèle peut se tromper alors que le service fonctionne parfaitement. Les deux surveillances sont complémentaires. Dans le cours, on met en place celle du modèle (Evidently) ; celle du service est présentée comme perspective.");
    card(s, 0.6, 1.5, 5.85, 4.25, "red");
    await iconCircle(s, 0.9, 1.75, 0.65, "FaChartArea", C.accent5);
    txt(s, "Le modèle · Evidently", { x: 1.75, y: 1.85, w: 4.5, h: 0.45, fontSize: 20, bold: true, color: C.accent5 });
    txt(s, "« Le modèle est-il toujours fiable ? »", { x: 0.9, y: 2.6, w: 5.3, h: 0.4, fontSize: 16, italic: true });
    txt(s, [
      { text: "Compare les entrées reçues aux données d'entraînement", options: { bullet: true, breakLine: true } },
      { text: "Tests statistiques, rapport chaque jour", options: { bullet: true, breakLine: true } },
      { text: "Voit : parcelles d'une région plus chaude", options: { bullet: true } },
    ], { x: 0.9, y: 3.15, w: 5.3, h: 2.4, fontSize: 16, paraSpaceAfter: 8 });
    card(s, 6.85, 1.5, 5.85, 4.25, "file");
    await iconCircle(s, 7.15, 1.75, 0.65, "FaGaugeHigh", C.accent4);
    txt(s, "Le service · Prometheus + Grafana", { x: 8.0, y: 1.85, w: 4.6, h: 0.45, fontSize: 20, bold: true, color: C.accent4 });
    txt(s, "« Le service fonctionne-t-il ? »", { x: 7.15, y: 2.6, w: 5.3, h: 0.4, fontSize: 16, italic: true });
    txt(s, [
      { text: "Compte requêtes, temps de réponse, erreurs", options: { bullet: true, breakLine: true } },
      { text: "Courbes en temps réel, alertes", options: { bullet: true, breakLine: true } },
      { text: "Voit : API lente, erreurs 500", options: { bullet: true } },
    ], { x: 7.15, y: 3.15, w: 5.3, h: 2.4, fontSize: 16, paraSpaceAfter: 8 });
    card(s, 0.6, 6.0, 12.1, 0.7, "wheat");
    txt(s, "Une région plus chaude ? L'API répond vite et sans erreur… mais ses conseils ne valent plus rien.", { x: 0.85, y: 6.12, w: 11.6, h: 0.45, fontSize: 16, bold: true, align: "center" });
  }

  // ================================================================ Partie B
  section("2. Le cycle de vie");
  divider(2, "Le cycle de vie du modèle", "Un modèle n'est jamais « fini » : le monde change, le modèle doit suivre.", "Transition : la chaîne n'est pas un trajet à sens unique, c'est une boucle. Ce sont les événements qui la font tourner.");
  {
    const s = content("Le cycle de vie : une boucle, pas une ligne", "Les six étapes de la boucle, et les événements qui la relancent (à droite). Chaque événement fait repartir la boucle à un endroit différent : un nouveau code repart des tests, de nouvelles données repartent de la validation, une dérive repart de la collecte de données.");
    const steps = [["Données", "collecter, versionner"], ["Validation", "schéma"], ["Entraînement", "train, tune"], ["Promotion", "meilleur modèle"], ["Déploiement", "API en service"], ["Surveillance", "dérive, erreurs"]];
    const cx = 4.3, cy = 4.0, r = 2.15;
    steps.forEach(([t, d], i) => {
      const a = -Math.PI / 2 + (i * 2 * Math.PI) / steps.length;
      box(s, cx + r * 1.15 * Math.cos(a) - 1.05, cy + r * Math.sin(a) - 0.42, 2.1, 0.84, t, d, i === 5 ? "red" : (i === 4 ? "wheat" : "soft"), { size: 15, subSize: 11 });
    });
    for (let i = 0; i < 6; i++) {
      const a1 = -Math.PI / 2 + ((i + 0.5) * 2 * Math.PI) / 6;
      const a0 = a1 - 0.22, a2 = a1 + 0.22;
      arrow(s, cx + r * 1.15 * Math.cos(a0) * 0.98, cy + r * Math.sin(a0) * 0.98, cx + r * 1.15 * Math.cos(a2) * 0.98, cy + r * Math.sin(a2) * 0.98, { color: C.accent1, width: 2 });
    }
    txt(s, "MLOps", { x: cx - 0.9, y: cy - 0.3, w: 1.8, h: 0.6, fontSize: 24, bold: true, color: C.accent1, fontFace: "Cambria", align: "center" });
    txt(s, "Ce qui relance la boucle", { x: 8.7, y: 1.5, w: 4.0, h: 0.4, fontSize: 17, bold: true, color: C.accent5 });
    const ev = [["FaCodeBranch", "Nouveau code"], ["FaDatabase", "Nouvelles données"], ["FaTemperatureHigh", "Data drift"], ["FaShuffle", "Concept drift"], ["FaTriangleExclamation", "Données invalides"], ["FaBug", "Modèle défaillant"], ["FaShieldHalved", "Faille de sécurité"]];
    for (let i = 0; i < ev.length; i++) {
      await iconCircle(s, 8.7, 2.05 + i * 0.66, 0.48, ev[i][0], C.accent5);
      txt(s, ev[i][1], { x: 9.35, y: 2.12 + i * 0.66, w: 3.4, h: 0.38, fontSize: 16 });
    }
  }
  {
    const s = content("Les événements liés au code et aux données", "Ces événements viennent de l'équipe ou des fournisseurs de données : on sait quand ils arrivent. La chaîne doit y répondre de façon automatique et prévisible.");
    table(s, 0.6, 1.45, 12.1, ["Événement", "Exemple", "Détection", "Réaction"], [
      ["Nouveau code", "correction d'un bug, nouvelle fonctionnalité", "un commit", "CI, puis déploiement"],
      ["Nouvelles données", "campagne de mesures 2027", "nouvelle version DVC", "validation, train, promote"],
      ["Données invalides en entrée", "capteur de pH défaillant (pH = 15)", "erreurs 422 de l'API", "alerte, vérifier la source"],
      ["Changement de schéma", "nouvelle culture, nouvelle variable", "demande métier", "schéma, code et tests modifiés"],
      ["Modèle défaillant", "un nouveau champion se trompe", "surveillance, /health", "remettre l'alias sur l'ancienne version"],
      ["Faille de sécurité", "vulnérabilité dans une bibliothèque", "alerte (Dependabot)", "mettre à jour uv.lock, CI"],
    ], [2.7, 3.4, 2.7, 3.3], { size: 15, rowH: 0.75, boldFirst: true });
  }
  {
    const s = content("Data drift : les entrées changent", "Exemple : l'API est utilisée dans une région plus chaude que celle des données d'entraînement. Le modèle n'a presque jamais vu de telles températures : ses prédictions deviennent incertaines. On le détecte tout de suite, sur les seules entrées, sans attendre de connaître la bonne réponse.");
    const bins = Array.from({ length: 19 }, (_, i) => 8 + i * 2);
    histogram(s, 0.8, 1.7, 6.6, 3.5, [
      { values: gauss(25.6, 5, bins), color: HEX.moss, transparency: 10 },
      { values: gauss(33, 4, bins), color: HEX.red, transparency: 45 },
    ], { bins, labelEvery: 2, axisLabel: "température (°C)" });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 5.85, w: 0.3, h: 0.25, fill: { color: HEX.moss }, line: { color: HEX.moss, width: 0 }, objectName: oname("légende") });
    txt(s, "données d'entraînement", { x: 1.3, y: 5.82, w: 2.6, h: 0.32, fontSize: 13 });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.0, y: 5.85, w: 0.3, h: 0.25, fill: { color: HEX.red, transparency: 45 }, line: { color: HEX.red, width: 0 }, objectName: oname("légende") });
    txt(s, "requêtes reçues (nouvelle région)", { x: 4.4, y: 5.82, w: 3.2, h: 0.32, fontSize: 13 });
    const rows = [["Ce qui change", "la distribution des entrées P(X)"], ["Détection", "immédiate : comparer les entrées reçues aux données d'entraînement (tests statistiques, Evidently)"], ["Réaction", "alerte, collecter des données de la nouvelle région, réentraîner"]];
    rows.forEach(([t, d], i) => {
      txt(s, t, { x: 8.0, y: 1.7 + i * 1.5, w: 4.7, h: 0.4, fontSize: 18, bold: true, color: C.accent5 });
      txt(s, d, { x: 8.0, y: 2.12 + i * 1.5, w: 4.7, h: 1.0, fontSize: 16 });
    });
  }
  {
    const s = content("Concept drift : la relation change", "Exemple : avec le changement climatique, la culture la mieux adaptée à des mesures identiques n'est plus la même. Les entrées ne bougent pas, c'est la bonne réponse qui change. On ne peut le voir qu'en comparant les prédictions à la réalité du terrain, qui n'arrive qu'après une saison.");
    box(s, 0.6, 1.6, 3.4, 1.4, "Mêmes mesures", "N=90 · 21 °C · pH 6,5\n203 mm de pluie", "file", { size: 17, subSize: 13 });
    arrow(s, 4.05, 2.0, 5.0, 1.75, { color: C.accent1, width: 2, label: "hier", ldy: -0.35 });
    arrow(s, 4.05, 2.6, 5.0, 2.85, { color: C.accent5, width: 2, label: "aujourd'hui", ldy: 0.05 });
    box(s, 5.05, 1.4, 2.4, 0.75, "riz ✓", null, "soft", { size: 18 });
    box(s, 5.05, 2.5, 2.4, 0.75, "maïs ✓ (riz ✗)", null, "red", { size: 18 });
    txt(s, "La vérité terrain arrive tard", { x: 0.6, y: 3.65, w: 7, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
    const tl = [["Prédiction", "avril"], ["Semis", "mai"], ["Récolte", "septembre"], ["Bilan", "la culture était-elle adaptée ?"]];
    s.addShape(pres.shapes.LINE, { x: 0.9, y: 4.75, w: 6.3, h: 0, line: { color: C.accent2, width: 3 }, objectName: oname("frise") });
    tl.forEach(([t, d], i) => {
      const x = 0.6 + i * 2.1;
      numCircle(s, x + 0.3, 4.48, 0.55, i + 1, i === 3 ? C.accent5 : C.accent1, 15);
      txt(s, t, { x, y: 5.15, w: 2.0, h: 0.35, fontSize: 15, bold: true });
      txt(s, d, { x, y: 5.5, w: 2.0, h: 0.8, fontSize: 13, color: C.accent6 });
    });
    const rows = [["Ce qui change", "la relation entre entrées et bonne réponse P(Y|X)"], ["Détection", "tardive : baisse de performance mesurée avec les retours du terrain"], ["Réaction", "réentraîner sur des données récentes, étiquetées"]];
    rows.forEach(([t, d], i) => {
      txt(s, t, { x: 8.0, y: 1.6 + i * 1.5, w: 4.7, h: 0.4, fontSize: 18, bold: true, color: C.accent5 });
      txt(s, d, { x: 8.0, y: 2.02 + i * 1.5, w: 4.7, h: 1.0, fontSize: 16 });
    });
    card(s, 8.0, 6.0, 4.7, 0.75, "wheat");
    txt(s, "D'où l'intérêt de surveiller d'abord les entrées.", { x: 8.2, y: 6.12, w: 4.3, h: 0.5, fontSize: 15, bold: true });
  }
  {
    const s = content("Ce qui existe déjà, ce qui reste à construire", "Le projet de départ couvre déjà une bonne partie de la chaîne en local. Les étudiants vont la reconstruire pas à pas, puis la compléter en séance 3 par le déploiement, l'automatisation et la surveillance.");
    const items = [
      ["Environnement, configuration, données versionnées et validées", true, "1"],
      ["Tests automatisés et CI", true, "1"],
      ["Suivi des expériences, registre, promotion", true, "2"],
      ["API dans un conteneur, en local", true, "2"],
      ["Déploiement sur le VPS, HTTPS", false, "3"],
      ["Déploiement continu (CD)", false, "3"],
      ["Réentraînement automatique sur nouvelles données", false, "3"],
      ["Surveillance de la dérive (Evidently)", false, "3"],
    ];
    items.forEach(([t, done, n], i) => {
      const y = 1.5 + i * 0.64;
      badge(s, 0.6, y + 0.04, done ? "en place" : `séance ${n}`, done);
      txt(s, t, { x: 2.4, y, w: 8.6, h: 0.42, fontSize: 17, valign: "middle" });
      if (done) txt(s, `séance ${n}`, { x: 11.3, y, w: 1.4, h: 0.42, fontSize: 14, color: C.accent6, align: "right", valign: "middle" });
    });
  }
  {
    const s = pres.addSlide({ masterName: "TITRE", sectionTitle: currentSection() });
    s.addText("À retenir", { placeholder: "title" });
    s.addText("Avant de commencer l'atelier", { placeholder: "body" });
    const K = ["Le modèle n'est qu'une petite partie du système.", "En local on construit ; en production on sert, on surveille, on réagit.", "GitHub fait le pont : la CI vérifie, la CD livre.", "Un modèle vit dans une boucle, relancée par des événements.", "Data drift : les entrées changent. Concept drift : la bonne réponse change."];
    K.forEach((k, i) => {
      s.addText(String(i + 1), { shape: pres.shapes.OVAL, x: 0.8, y: 4.95 + i * 0.47, w: 0.36, h: 0.36, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, color: C.text1, bold: true, fontSize: 12, align: "center", valign: "middle", margin: 0, objectName: oname("numéro") });
      txt(s, k, { x: 1.35, y: 4.96 + i * 0.47, w: 11, h: 0.36, fontSize: 16, color: C.background1, valign: "middle" });
    });
    s.addImage({ data: await icon("FaArrowsRotate", HEX.moss, 512), x: 10.2, y: 1.4, w: 2.3, h: 2.3, altText: "Cycle", objectName: oname("illustration") });
    s.addNotes("Transition vers l'atelier : on commence par le socle, rendre le projet reproductible. Montrer sur la carte de la chaîne la colonne « local » : c'est elle qu'on construit aujourd'hui.");
  }

  await save(OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
