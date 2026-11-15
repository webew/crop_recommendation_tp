// Thème, mises en page et outils de dessin communs aux supports de présentation.
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require("./apply_theme.js");

const THEME = {
  name: "Champs MLOps",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2A1F", lt1: "FFFFFF", dk2: "2C5F2D", lt2: "EEF4E6",
    accent1: "2C5F2D", accent2: "97BC62", accent3: "B7791F", accent4: "2F5D7C",
    accent5: "B5452B", accent6: "5B6B5B", hlink: "2F5D7C", folHlink: "6D2E46",
  },
};
const HEX = {
  forest: "2C5F2D", moss: "97BC62", mossBg: "EEF4E6", wheat: "B7791F", wheatBg: "FBF1DF",
  blue: "2F5D7C", blueBg: "E5EEF4", red: "B5452B", redBg: "F8E6E1", grey: "5B6B5B",
  line: "D5DDD1", codeBg: "F6F8F4", ink: "1F2A1F", white: "FFFFFF", paleMoss: "DCEBD0",
};


// Crée une présentation au thème du cours et renvoie les outils pour la remplir.
function makeDeck(meta) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13,33 x 7,5 pouces
  pres.title = meta.title;
  pres.subject = meta.subject;
  pres.author = "Support de cours MLOps";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ------------------------------------------------------------------ couleurs par style
  const STY = {
    main: { fill: C.accent1, line: C.accent1, text: C.background1, sub: HEX.paleMoss },
    soft: { fill: C.background2, line: C.accent2, text: C.text1, sub: C.accent6 },
    file: { fill: C.background1, line: HEX.line, text: C.text1, sub: C.accent6 },
    wheat: { fill: HEX.wheatBg, line: C.accent3, text: C.text1, sub: C.accent6 },
    blue: { fill: HEX.blueBg, line: C.accent4, text: C.text1, sub: C.accent6 },
    red: { fill: HEX.redBg, line: C.accent5, text: C.text1, sub: C.accent6 },
  };

  // ------------------------------------------------------------------ mises en page
  pres.defineSlideMaster({
    title: "TITRE",
    background: { color: C.accent1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.55, w: 8.6, h: 2.2, fontSize: 50, bold: true, color: C.background1, valign: "bottom", align: "left" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.85, w: 8.6, h: 1.1, fontSize: 24, italic: true, color: HEX.paleMoss, valign: "top", align: "left" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "SECTION",
    background: { color: C.accent1 },
    objects: [
      { placeholder: { options: { name: "num", type: "body", x: 0.8, y: 1.6, w: 3, h: 1.6, fontSize: 96, bold: true, color: C.accent2, valign: "bottom", align: "left" }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 3.25, w: 11.5, h: 1.3, fontSize: 44, bold: true, color: C.background1, valign: "top", align: "left" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.55, w: 11.5, h: 0.9, fontSize: 22, italic: true, color: HEX.paleMoss, valign: "top", align: "left" }, text: "" } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.6, h: 0.3, fontSize: 11, color: HEX.paleMoss, align: "right" },
  });
  pres.defineSlideMaster({
    title: "CONTENU",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.32, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.accent1, valign: "middle", align: "left" }, text: "" } },
      { text: { text: "Du notebook à l'application · La démarche MLOps", options: { x: 0.6, y: 7.0, w: 7, h: 0.3, fontSize: 10, color: C.accent6, isTextBox: true } } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.6, h: 0.3, fontSize: 11, color: C.accent6, align: "right" },
  });

  // ------------------------------------------------------------------ icônes
  const ICON_CACHE = {};
  async function icon(name, color = "FFFFFF", size = 256) {
    const key = `${name}-${color}`;
    if (ICON_CACHE[key]) return ICON_CACHE[key];
    const Comp = fa[name];
    if (!Comp) throw new Error("icône inconnue " + name);
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
    const png = await sharp(Buffer.from(svg)).png().toBuffer();
    ICON_CACHE[key] = "image/png;base64," + png.toString("base64");
    return ICON_CACHE[key];
  }

  // ------------------------------------------------------------------ aides de dessin
  let OBJ = 0;
  const oname = (p) => `${p}-${++OBJ}`;

  function txt(s, text, o) {
    s.addText(text, { isTextBox: true, fontSize: 16, color: C.text1, valign: "top", margin: 0, objectName: oname("texte"), ...o });
  }

  function box(s, x, y, w, h, title, sub, style = "soft", o = {}) {
    const st = STY[style];
    const runs = [{ text: title, options: { bold: true, fontSize: o.size || 14, color: st.text, breakLine: !!sub } }];
    if (sub) runs.push({ text: sub, options: { fontSize: o.subSize || 11, color: st.sub, fontFace: o.mono ? "Courier New" : undefined } });
    s.addText(runs, {
      shape: pres.shapes.ROUNDED_RECTANGLE, x, y, w, h, rectRadius: o.radius ?? 0.1,
      fill: { color: st.fill }, line: { color: st.line, width: o.lineW || 1.25, dashType: o.dashed ? "dash" : "solid" },
      align: "center", valign: "middle", margin: 3, objectName: oname("boîte"), paraSpaceAfter: 2,
    });
  }

  function arrow(s, x1, y1, x2, y2, o = {}) {
    const color = o.color || C.accent6;
    s.addShape(pres.shapes.LINE, {
      x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
      flipH: x2 < x1, flipV: y2 < y1,
      line: { color, width: o.width || 1.5, endArrowType: o.noHead ? undefined : "triangle", dashType: o.dashed ? "dash" : "solid" },
      objectName: oname("flèche"),
    });
    if (o.label) {
      const lx = (x1 + x2) / 2 + (o.ldx || 0), ly = (y1 + y2) / 2 + (o.ldy ?? -0.3);
      txt(s, o.label, { x: lx - 0.8, y: ly, w: 1.6, h: 0.26, fontSize: 11, italic: true, color, align: "center" });
    }
  }

  function code(s, x, y, w, h, src, title, o = {}) {
    const fs_ = o.size || 12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: HEX.codeBg }, line: { color: HEX.line, width: 1 }, objectName: oname("code-fond") });
    let top = y + 0.08;
    if (title) {
      txt(s, title, { x: x + 0.15, y: y + 0.06, w: w - 0.3, h: 0.26, fontSize: 11, color: C.accent6, fontFace: "Courier New" });
      s.addShape(pres.shapes.LINE, { x, y: y + 0.36, w, h: 0, line: { color: HEX.line, width: 1 }, objectName: oname("code-ligne") });
      top = y + 0.44;
    }
    const lines = src.split("\n");
    const runs = lines.map((l, i) => {
      const t = l.trimStart();
      const isComment = t.startsWith("#") || t.startsWith("//");
      const isOut = t.startsWith("→") || t.startsWith("$");
      return { text: l.length ? l : " ", options: { color: isComment ? "7A887A" : (isOut ? C.accent1 : C.text1), italic: isComment, breakLine: i < lines.length - 1 } };
    });
    s.addText(runs, { isTextBox: true, x: x + 0.15, y: top, w: w - 0.3, h: y + h - top - 0.06, fontFace: "Courier New", fontSize: fs_, valign: "top", margin: 0, objectName: oname("code"), lineSpacingMultiple: 1.0 });
  }

  async function iconCircle(s, x, y, d, name, bg = C.accent1, fg = "FFFFFF") {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg, width: 0 }, objectName: oname("rond") });
    const pad = d * 0.25;
    s.addImage({ data: await icon(name, fg), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, altText: name, objectName: oname("icône") });
  }

  async function iconRow(s, x, y, w, name, title, body, o = {}) {
    const d = o.d || 0.62;
    await iconCircle(s, x, y, d, name, o.bg || C.accent1);
    txt(s, title, { x: x + d + 0.22, y: y - 0.02, w: w - d - 0.22, h: 0.36, fontSize: o.tSize || 17, bold: true, color: o.tColor || C.accent1 });
    if (body) txt(s, body, { x: x + d + 0.22, y: y + 0.34, w: w - d - 0.22, h: o.bodyH || 0.6, fontSize: o.bSize || 14, color: C.text1 });
  }

  function card(s, x, y, w, h, style = "soft") {
    const st = STY[style];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: st.fill }, line: { color: st.line, width: 1.25 }, objectName: oname("carte") });
  }

  function numCircle(s, x, y, d, n, bg = C.accent1, size = 16) {
    s.addText(String(n), { shape: pres.shapes.OVAL, x, y, w: d, h: d, fill: { color: bg }, line: { color: bg, width: 0 }, color: C.background1, bold: true, fontSize: size, align: "center", valign: "middle", margin: 0, objectName: oname("numéro") });
  }

  function stat(s, x, y, w, value, label, color = C.accent1) {
    txt(s, value, { x, y, w, h: 0.95, fontSize: 48, bold: true, color, fontFace: "Cambria", valign: "bottom" });
    txt(s, label, { x, y: y + 0.98, w, h: 0.6, fontSize: 14, color: C.accent6 });
  }

  function table(s, x, y, w, header, rows, colW, o = {}) {
    const fsz = o.size || 14;
    const head = header.map((h) => ({ text: h, options: { bold: true, color: C.background1, fill: { color: C.accent1 }, fontSize: fsz } }));
    const body = rows.map((r, i) => r.map((c, j) => {
      const isCode = o.codeCols && o.codeCols.includes(j);
      return { text: c, options: { fontSize: isCode ? fsz - 1 : fsz, fontFace: isCode ? "Courier New" : undefined, color: C.text1, fill: { color: i % 2 ? "F7F9F5" : "FFFFFF" }, bold: o.boldFirst && j === 0 } };
    }));
    s.addTable([head, ...body], { x, y, w, colW, rowH: o.rowH, border: { type: "solid", color: HEX.line, pt: 0.75 }, margin: [4, 6, 4, 6], valign: "middle", objectName: oname("tableau") });
  }

  function sub(s, text) {
    txt(s, text, { x: 0.6, y: 1.12, w: 12.1, h: 0.4, fontSize: 16, italic: true, color: C.accent6 });
  }


  function hbars(s, x, y, w, h, rows, o) {
    const titleH = o.title ? 0.45 : 0, axisH = o.ticks ? 0.4 : 0;
    if (o.title) txt(s, o.title, { x, y, w, h: 0.35, fontSize: 14, bold: true, color: C.text1 });
    const lw = o.labelW, valW = o.valueW || 1.0;
    const bx = x + lw + 0.12, bw = w - lw - 0.12 - valW;
    const top = y + titleH, rh = (h - titleH - axisH) / rows.length;
    const sx = (v) => bx + ((v - o.min) / (o.max - o.min)) * bw;
    if (o.ticks) o.ticks.forEach((t) => {
      s.addShape(pres.shapes.LINE, { x: sx(t), y: top, w: 0, h: rows.length * rh, line: { color: "E3E8E0", width: 0.75 }, objectName: oname("grille") });
      txt(s, o.fmtTick(t), { x: sx(t) - 0.4, y: top + rows.length * rh + 0.06, w: 0.8, h: 0.3, fontSize: 11, color: C.accent6, align: "center" });
    });
    rows.forEach(([label, v, color, bold], i) => {
      const yy = top + i * rh;
      txt(s, label, { x, y: yy, w: lw, h: rh, fontSize: o.labelSize || 13, color: C.text1, align: "right", valign: "middle", bold: !!bold });
      s.addShape(pres.shapes.RECTANGLE, { x: bx, y: yy + rh * 0.16, w: Math.max(0.02, sx(v) - bx), h: rh * 0.68, fill: { color }, line: { color, width: 0 }, objectName: oname("barre") });
      txt(s, o.fmt(v), { x: sx(v) + 0.08, y: yy, w: valW, h: rh, fontSize: o.valueSize || 12, color: C.text1, valign: "middle", bold: !!bold });
    });
  }

  let SECTION = "";
  function section(title) { SECTION = title; pres.addSection({ title }); }
  function content(title, notes) {
    const s = pres.addSlide({ masterName: "CONTENU", sectionTitle: SECTION });
    s.addText(title, { placeholder: "title" });
    if (notes) s.addNotes(notes);
    return s;
  }
  function divider(num, title, subtitle, notes) {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle: SECTION });
    s.addText(String(num).padStart(2, "0"), { placeholder: "num" });
    s.addText(title, { placeholder: "title" });
    s.addText(subtitle, { placeholder: "body" });
    if (notes) s.addNotes(notes);
    return s;
  }

  const currentSection = () => SECTION;
  async function save(out) {
    await pres.writeFile({ fileName: out });
    await applyTheme(out, THEME);
    console.log("écrit :", out);
  }
  return { pres, C, STY, icon, oname, txt, box, arrow, code, iconCircle, iconRow, card, numCircle, stat, table, sub, hbars, section, content, divider, currentSection, save };
}

module.exports = { makeDeck, THEME, HEX };
