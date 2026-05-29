#!/usr/bin/env python3
"""Régénère dist/ (HTML + CSS + JS éclatés) depuis le monolithe canonique.

Source : « Simulation Revolty Publique.html » (CSS inline dans <style>, JS dans
<script>). Sortie dans dist/ :
  - revolty-styles.css / revolty-app.js  (référencés en chemins RELATIFS,
    servis via GitHub Pages)
  - Simulation_Revolty.html              (images pics/ réécrites vers jsDelivr)
"""
import re
from pathlib import Path


def deindent8(text):
    """Retire jusqu'à 8 espaces en tête de chaque ligne (indentation de base
    héritée du HTML). Sûr pour les template literals (ne retire jamais plus que
    l'indentation présente)."""
    return "\n".join(re.sub(r"^ {1,8}", "", ln) for ln in text.split("\n"))

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Simulation Revolty Publique.html"
DIST = ROOT / "dist"
PICS_CDN = "https://cdn.jsdelivr.net/gh/Revolty-code/Simulation@main/pics/"

def write_lf(path, text):
    """Écrit en UTF-8 avec fins de ligne LF (convention du dist/)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


html = SRC.read_text(encoding="utf-8")

style_m = re.search(r"<style>(.*?)</style>", html, re.S)
script_m = re.search(r"<script>(.*?)</script>", html, re.S)
if not style_m or not script_m:
    raise SystemExit("Bloc <style> ou <script> introuvable dans la source")

# Le contenu inline porte une indentation de base (8 espaces, hérité du HTML) ;
# le dist/ est désindenté à la racine → on retire la base pour un diff propre.
css = deindent8(style_m.group(1)).strip("\n") + "\n"
js = deindent8(script_m.group(1)).strip("\n") + "\n"
write_lf(DIST / "revolty-styles.css", css)
write_lf(DIST / "revolty-app.js", js)

# HTML éclaté : on remplace les blocs inline par des références externes.
out = (html[:style_m.start()]
       + '<link rel="stylesheet" href="revolty-styles.css" />'
       + html[style_m.end():])
# Les indices ont bougé après la 1re substitution : on re-cherche le <script>.
script_m2 = re.search(r"<script>.*?</script>", out, re.S)
out = (out[:script_m2.start()]
       + '<script src="revolty-app.js"></script>'
       + out[script_m2.end():])

n_pics = out.count('src="pics/')
out = out.replace('src="pics/', 'src="' + PICS_CDN)
write_lf(DIST / "Simulation_Revolty.html", out)

print(f"OK · css={len(css)} o · js={len(js)} o · html={len(out)} o · pics réécrits={n_pics}")
