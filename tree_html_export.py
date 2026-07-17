"""
tree_html_export.py
==========================================================
Exporte l'arbre enregistré par ai.tree_logger vers une page HTML
autonome et interactive : vous vous déplacez dedans vous-même
(glisser pour déplacer, molette pour zoomer, clic sur un noeud
pour déplier/replier ses enfants). Aucune dépendance externe
(pas de connexion internet nécessaire pour l'ouvrir).

Ne fait pas partie du TP (pas de logique MinMax ici) : ce module
se contente d'afficher ce que VOTRE algorithme a enregistré via
TreeLogger.
"""

import json
import webbrowser
from pathlib import Path


def _num_to_js(value):
    """Convertit une valeur Python (dont +/-inf) en littéral JS valide."""
    if value is None:
        return "null"
    if value == float("inf"):
        return "Infinity"
    if value == float("-inf"):
        return "-Infinity"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return json.dumps(value)


def _build_nested(nodes, node_id, seen=None):
    """Construit une structure imbriquée (JSON-like) à partir du dict
    plat de TreeLogger, en repartant de la racine."""
    if seen is None:
        seen = set()
    if node_id in seen:
        return None  # sécurité anti-boucle
    seen.add(node_id)

    node = nodes[node_id]
    children = [
        _build_nested(nodes, c, seen)
        for c in node["children"] if c in nodes
    ]
    children = [c for c in children if c is not None]

    return {
        "id": node["id"],
        "move": node["move"],
        "alpha": node["alpha"],
        "beta": node["beta"],
        "score": node["score"],
        "maximizing": node["maximizing"],
        "pruned": node["pruned"],
        "children": children,
    }


def _to_js_literal(node):
    """Sérialise la structure imbriquée en littéral JS (gère +/-inf)."""
    parts = []
    parts.append("{")
    parts.append(f'"id":{node["id"]},')
    parts.append(f'"move":{json.dumps(node["move"])},')
    parts.append(f'"alpha":{_num_to_js(node["alpha"])},')
    parts.append(f'"beta":{_num_to_js(node["beta"])},')
    parts.append(f'"score":{_num_to_js(node["score"])},')
    parts.append(f'"maximizing":{_num_to_js(node["maximizing"])},')
    parts.append(f'"pruned":{_num_to_js(node["pruned"])},')
    parts.append('"children":[')
    parts.append(",".join(_to_js_literal(c) for c in node["children"]))
    parts.append("]}")
    return "".join(parts)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Arbre MinMax / Alpha-Beta</title>
<style>
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden;
               font-family: -apple-system, Segoe UI, Arial, sans-serif; background: #1b1b1b; }
  #toolbar { position: fixed; top: 0; left: 0; right: 0; height: 52px;
             background: #111; color: #eee; display: flex; align-items: center;
             gap: 10px; padding: 0 14px; z-index: 10; box-shadow: 0 2px 6px rgba(0,0,0,.4); }
  #toolbar button { background: #333; color: #eee; border: 1px solid #555; border-radius: 6px;
                     padding: 6px 12px; cursor: pointer; font-size: 13px; }
  #toolbar button:hover { background: #444; }
  #info { margin-left: auto; font-size: 13px; color: #aaa; }
  #canvas-wrap { position: absolute; top: 52px; left: 0; right: 0; bottom: 0; cursor: grab; }
  #canvas-wrap.grabbing { cursor: grabbing; }
  svg { width: 100%; height: 100%; display: block; }
  .node-box { stroke: #000; stroke-width: 1; cursor: pointer; }
  .node-text { fill: #fff; font-size: 11px; text-anchor: middle; pointer-events: none; }
  .node-move { fill: #ddd; font-size: 11px; text-anchor: middle; pointer-events: none; font-weight: bold; }
  .edge { stroke: #666; stroke-width: 1.3; fill: none; }
  .pruned-label { fill: #ff8080; font-size: 10px; text-anchor: middle; font-style: italic; pointer-events: none; }
  .expand-hint { fill: #ffd166; font-size: 15px; text-anchor: middle; pointer-events: none; font-weight: bold; }
  .legend { position: fixed; bottom: 14px; right: 14px; background: rgba(20,20,20,.9);
            color: #ddd; font-size: 12px; padding: 10px 14px; border-radius: 8px; line-height: 1.7;
            border: 1px solid #444; }
  .swatch { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: middle; }
</style>
</head>
<body>

<div id="toolbar">
  <button id="btn-expand-all">Tout déplier</button>
  <button id="btn-collapse-all">Tout replier</button>
  <button id="btn-reset-view">Réinitialiser la vue</button>
  <div id="info"></div>
</div>

<div id="canvas-wrap">
  <svg id="svg">
    <g id="viewport"></g>
  </svg>
</div>

<div class="legend">
  <div><span class="swatch" style="background:#3b6fa0"></span>Noeud MAX</div>
  <div><span class="swatch" style="background:#a04b3b"></span>Noeud MIN</div>
  <div><span class="swatch" style="background:#6f6f6f"></span>Branche coupée</div>
  <div><span class="swatch" style="background:#2a2a2a;border:1px dashed #ffd166"></span>Cliquez un noeud (+N) pour déplier</div>
</div>

<script>
const TREE = __TREE_DATA__;

const BOX_W = 96, BOX_H = 46;
const X_GAP = 26, Y_GAP = 90;

// --- Etat de dépliage : un Set d'ids de noeuds "dépliés" ---
const expanded = new Set();

function collectAllIds(node, out) {
  out.push(node.id);
  node.children.forEach(c => collectAllIds(c, out));
}

function expandDefault(node, depth) {
  // Déplié par défaut jusqu'à la profondeur 1, le reste replié.
  if (depth <= 1) expanded.add(node.id);
  node.children.forEach(c => expandDefault(c, depth + 1));
}
expandDefault(TREE, 0);

let totalNodes = 0;
(function countAll(n){ totalNodes++; n.children.forEach(countAll); })(TREE);

// --- Layout : assigne x (position horizontale) et y (profondeur) ---
function layout(node, depth, leafCounter, positions) {
  const isExpanded = expanded.has(node.id);
  const visibleChildren = isExpanded ? node.children : [];

  let x;
  if (visibleChildren.length === 0) {
    x = leafCounter.value;
    leafCounter.value += 1;
  } else {
    const xs = visibleChildren.map(c => layout(c, depth + 1, leafCounter, positions));
    x = (Math.min(...xs) + Math.max(...xs)) / 2;
  }
  positions[node.id] = { x, y: depth, node };
  return x;
}

function fmt(v) {
  if (v === Infinity) return "+inf";
  if (v === -Infinity) return "-inf";
  if (v === null || v === undefined) return "?";
  return Number(v).toFixed(1);
}

const svg = document.getElementById("svg");
const viewport = document.getElementById("viewport");
const info = document.getElementById("info");

let scale = 1, panX = 80, panY = 40;

function applyTransform() {
  viewport.setAttribute("transform", `translate(${panX},${panY}) scale(${scale})`);
}

function render() {
  const positions = {};
  layout(TREE, 0, { value: 0 }, positions);

  let visibleCount = 0;
  Object.keys(positions).forEach(() => visibleCount++);
  info.textContent = `${visibleCount} / ${totalNodes} noeuds affichés`;

  let svgHtml = "";

  // Arêtes
  Object.values(positions).forEach(({ x, y, node }) => {
    if (!expanded.has(node.id)) return;
    node.children.forEach(child => {
      const cp = positions[child.id];
      if (!cp) return;
      const x1 = x * (BOX_W + X_GAP) + BOX_W / 2;
      const y1 = y * Y_GAP + BOX_H;
      const x2 = cp.x * (BOX_W + X_GAP) + BOX_W / 2;
      const y2 = cp.y * Y_GAP;
      const midY = (y1 + y2) / 2;
      svgHtml += `<path class="edge" d="M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}"/>`;
    });
  });

  // Noeuds
  Object.values(positions).forEach(({ x, y, node }) => {
    const px = x * (BOX_W + X_GAP);
    const py = y * Y_GAP;
    let fill = node.maximizing ? "#3b6fa0" : "#a04b3b";
    if (node.pruned) fill = "#6f6f6f";

    const hiddenCount = expanded.has(node.id) ? 0 : node.children.length;

    svgHtml += `<g class="node" data-id="${node.id}">`;
    svgHtml += `<rect class="node-box" x="${px}" y="${py}" width="${BOX_W}" height="${BOX_H}" rx="8" fill="${fill}"></rect>`;
    svgHtml += `<text class="node-text" x="${px + BOX_W/2}" y="${py + BOX_H/2 - 4}">a=${fmt(node.alpha)} b=${fmt(node.beta)}</text>`;
    svgHtml += `<text class="node-text" x="${px + BOX_W/2}" y="${py + BOX_H/2 + 10}">score=${fmt(node.score)}</text>`;
    if (node.move) {
      svgHtml += `<text class="node-move" x="${px + BOX_W/2}" y="${py - 6}">${node.move}</text>`;
    }
    if (node.pruned) {
      svgHtml += `<text class="pruned-label" x="${px + BOX_W/2}" y="${py + BOX_H + 13}">✂ coupé (β≤α)</text>`;
    }
    if (hiddenCount > 0) {
      svgHtml += `<text class="expand-hint" x="${px + BOX_W/2}" y="${py + BOX_H + 13}">(+${hiddenCount}) cliquer</text>`;
    }
    svgHtml += `</g>`;
  });

  viewport.innerHTML = svgHtml;

  viewport.querySelectorAll(".node").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = parseInt(el.getAttribute("data-id"), 10);
      if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
      render();
    });
  });
}

// --- Pan (glisser) ---
const wrap = document.getElementById("canvas-wrap");
let dragging = false, lastX = 0, lastY = 0;

wrap.addEventListener("mousedown", (e) => {
  dragging = true;
  wrap.classList.add("grabbing");
  lastX = e.clientX; lastY = e.clientY;
});
window.addEventListener("mouseup", () => { dragging = false; wrap.classList.remove("grabbing"); });
window.addEventListener("mousemove", (e) => {
  if (!dragging) return;
  panX += (e.clientX - lastX);
  panY += (e.clientY - lastY);
  lastX = e.clientX; lastY = e.clientY;
  applyTransform();
});

// --- Zoom (molette) ---
wrap.addEventListener("wheel", (e) => {
  e.preventDefault();
  const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
  const rect = wrap.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  // Zoom centré sur le curseur
  panX = mx - (mx - panX) * zoomFactor;
  panY = my - (my - panY) * zoomFactor;
  scale *= zoomFactor;
  applyTransform();
}, { passive: false });

// --- Boutons ---
document.getElementById("btn-expand-all").addEventListener("click", () => {
  const all = [];
  collectAllIds(TREE, all);
  all.forEach(id => expanded.add(id));
  render();
});
document.getElementById("btn-collapse-all").addEventListener("click", () => {
  expanded.clear();
  expanded.add(TREE.id);
  render();
});
document.getElementById("btn-reset-view").addEventListener("click", () => {
  scale = 1; panX = 80; panY = 40;
  applyTransform();
});

applyTransform();
render();
</script>
</body>
</html>
"""


def export_tree_html(tree_data, output_path: str = "tree_view.html", open_browser: bool = True) -> str:
    """
    tree_data : tuple (nodes, root_id, truncated) tel que renvoyé par
                ai.tree_logger.TreeLogger.get_data()
    output_path : où écrire le fichier HTML
    open_browser : si True, ouvre automatiquement le fichier dans le
                   navigateur par défaut après l'avoir écrit

    Retourne le chemin absolu du fichier écrit.
    """
    nodes, root_id, _truncated = tree_data

    if root_id is None or not nodes:
        print("Aucun arbre à exporter (lancez une partie contre 'Mon IA' d'abord).")
        return ""

    nested = _build_nested(nodes, root_id)
    js_literal = _to_js_literal(nested)

    html = _HTML_TEMPLATE.replace("__TREE_DATA__", js_literal)

    path = Path(output_path).resolve()
    path.write_text(html, encoding="utf-8")

    if open_browser:
        webbrowser.open(path.as_uri())

    return str(path)
