# generate_interface.py
# Ce script lit le CSV, calcule toutes les métriques, et génère interface.html

import pandas as pd
import json
import os

# ══════════════════════════════════════════════════════════════════════════════
# GRILLE XT
# ══════════════════════════════════════════════════════════════════════════════
grille_xt = [
    [0.00,0.00,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.00,0.00],
    [0.00,0.01,0.01,0.01,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.01,0.01,0.01,0.00],
    [0.01,0.01,0.02,0.02,0.02,0.02,0.03,0.03,0.03,0.03,0.02,0.02,0.02,0.02,0.01,0.01],
    [0.01,0.02,0.02,0.02,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.02,0.02,0.02,0.01],
    [0.01,0.02,0.02,0.03,0.03,0.04,0.04,0.04,0.04,0.04,0.04,0.03,0.03,0.02,0.02,0.01],
    [0.02,0.02,0.03,0.03,0.04,0.05,0.05,0.05,0.05,0.05,0.05,0.04,0.03,0.03,0.02,0.02],
    [0.02,0.03,0.03,0.04,0.05,0.06,0.07,0.07,0.07,0.07,0.06,0.05,0.04,0.03,0.03,0.02],
    [0.02,0.03,0.04,0.05,0.06,0.08,0.10,0.10,0.10,0.10,0.08,0.06,0.05,0.04,0.03,0.02],
    [0.03,0.04,0.05,0.07,0.09,0.12,0.15,0.17,0.17,0.15,0.12,0.09,0.07,0.05,0.04,0.03],
    [0.04,0.05,0.07,0.10,0.14,0.19,0.24,0.27,0.27,0.24,0.19,0.14,0.10,0.07,0.05,0.04],
    [0.05,0.07,0.11,0.16,0.22,0.31,0.40,0.47,0.47,0.40,0.31,0.22,0.16,0.11,0.07,0.05],
    [0.07,0.11,0.17,0.26,0.38,0.54,0.68,0.76,0.76,0.68,0.54,0.38,0.26,0.17,0.11,0.07],
]

# ══════════════════════════════════════════════════════════════════════════════
# LECTURE CSV
# ══════════════════════════════════════════════════════════════════════════════
df = pd.read_csv("fus_FAR.csv", low_memory=False)
noms_equipes = df["team_name"].dropna().unique()
nom_fus = noms_equipes[0]
nom_far = noms_equipes[1]

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION JOUEURS
# ══════════════════════════════════════════════════════════════════════════════
joueurs_data = {}
equipes_data = {nom_fus: [], nom_far: []}

for _, ligne in df.iterrows():
    nom = ligne["player_name"]
    equipe_nom = ligne["team_name"]
    if pd.isna(nom) or pd.isna(equipe_nom):
        continue
    if nom in joueurs_data:
        continue
    pos_x = float(ligne["location_x"]) if not pd.isna(ligne["location_x"]) else 0.0
    pos_y = float(ligne["location_y"]) if not pd.isna(ligne["location_y"]) else 0.0
    joueurs_data[nom] = {
        "nom": nom, "equipe": equipe_nom,
        "pos_x": pos_x, "pos_y": pos_y,
        "xg": 0.0, "vaep": 0.0, "nb_actions": 0,
        "buts": 0, "tirs": 0, "passes": 0, "dribbles": 0
    }
    if equipe_nom in equipes_data:
        equipes_data[equipe_nom].append(nom)

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION ACTIONS & POSSESSIONS
# ══════════════════════════════════════════════════════════════════════════════
types_valides = ["Pass", "Shot", "Dribble"]
possessions = {}
ids_vus = set()
actions_list = []

for _, ligne in df.iterrows():
    event_id = ligne["id"]
    if event_id in ids_vus:
        continue
    ids_vus.add(event_id)

    type_action = ligne["event_type_name"]
    if type_action not in types_valides:
        continue

    nom_joueur = ligne["player_name"]
    if pd.isna(nom_joueur) or nom_joueur not in joueurs_data:
        continue

    start_x = float(ligne["location_x"])     if not pd.isna(ligne["location_x"])     else 0.0
    start_y = float(ligne["location_y"])     if not pd.isna(ligne["location_y"])     else 0.0
    end_x   = float(ligne["end_location_x"]) if not pd.isna(ligne["end_location_x"]) else 0.0
    end_y   = float(ligne["end_location_y"]) if not pd.isna(ligne["end_location_y"]) else 0.0
    minute  = int(ligne["minute"])           if not pd.isna(ligne["minute"])          else 0
    partie_corps   = ligne["body_part_name"]       if not pd.isna(ligne["body_part_name"])   else "inconnu"
    resultat       = ligne["outcome_name"]         if not pd.isna(ligne["outcome_name"])     else "inconnu"
    possession_eq  = ligne["possession_team_name"] if not pd.isna(ligne["possession_team_name"]) else ""
    equipe_action  = ligne["team_name"]            if not pd.isna(ligne["team_name"])         else ""
    xg_csv         = float(ligne["statsbomb_xg"])  if not pd.isna(ligne["statsbomb_xg"])      else 0.0
    marquer_but    = (type_action == "Shot" and resultat == "Goal")
    gagner_poss    = (equipe_action == possession_eq)

    # Calcul XT
    xt = 0.0
    ligne_xt  = int(end_y / 8)
    col_xt    = int(end_x / 10.5)
    if 0 <= ligne_xt < 12 and 0 <= col_xt < 16:
        xt = grille_xt[ligne_xt][col_xt]

    # Calcul XT début
    xt_debut = 0.0
    lig_d = int(start_y / 8)
    col_d = int(start_x / 10.5)
    if 0 <= lig_d < 12 and 0 <= col_d < 16:
        xt_debut = grille_xt[lig_d][col_d]
    dxt = xt - xt_debut

    action = {
        "type": type_action, "corps": partie_corps,
        "joueur": nom_joueur, "equipe": equipe_action,
        "minute": minute, "resultat": resultat,
        "xg": xg_csv, "dxg": 0.0, "xt": xt, "dxt": dxt, "vaep": 0.0,
        "start_x": start_x, "start_y": start_y,
        "end_x": end_x, "end_y": end_y,
        "marquer_but": marquer_but, "gagner_possession": gagner_poss,
        "possession_equipe": possession_eq
    }
    actions_list.append(action)

    # Stats joueur
    if xg_csv > 0:
        joueurs_data[nom_joueur]["xg"] += xg_csv
    joueurs_data[nom_joueur]["nb_actions"] += 1
    if type_action == "Shot":
        joueurs_data[nom_joueur]["tirs"] += 1
    elif type_action == "Pass":
        joueurs_data[nom_joueur]["passes"] += 1
    elif type_action == "Dribble":
        joueurs_data[nom_joueur]["dribbles"] += 1
    if marquer_but:
        joueurs_data[nom_joueur]["buts"] += 1

    # Possession
    num_poss = int(ligne["possession"]) if not pd.isna(ligne["possession"]) else 0
    if num_poss not in possessions:
        possessions[num_poss] = {"equipe": possession_eq, "actions": [], "vaep": 0.0, "gagnee": False}
    possessions[num_poss]["actions"].append(len(actions_list) - 1)

# ══════════════════════════════════════════════════════════════════════════════
# CALCUL DXG & VAEP
# ══════════════════════════════════════════════════════════════════════════════
for num, poss in possessions.items():
    idxs = poss["actions"]
    k = len(idxs)
    if k < 2:
        continue

    # DXG
    for i, idx in enumerate(idxs):
        xg_avant = actions_list[idxs[i-1]]["xg"] if i > 0 else 0.0
        actions_list[idx]["dxg"] = actions_list[idx]["xg"] - xg_avant

    # VAEP
    somme_xg = sum(actions_list[i]["xg"] for i in idxs)
    nb_adverse = sum(1 for i in idxs if not actions_list[i]["gagner_possession"] and actions_list[i]["xg"] > 0)
    p_marquer   = somme_xg / k
    p_encaisser = nb_adverse / k
    vaep_poss   = p_marquer - p_encaisser

    for idx in idxs:
        actions_list[idx]["vaep"] = vaep_poss
        joueurs_data[actions_list[idx]["joueur"]]["vaep"] += vaep_poss

    # Gagnée/perdue
    poss["gagnee"] = any(actions_list[i]["gagner_possession"] for i in idxs)
    poss["vaep"]   = vaep_poss

# ══════════════════════════════════════════════════════════════════════════════
# STATS ÉQUIPES
# ══════════════════════════════════════════════════════════════════════════════
equipes_stats = {}
for eq_nom in [nom_fus, nom_far]:
    joueurs_eq = [joueurs_data[n] for n in equipes_data[eq_nom]]
    equipes_stats[eq_nom] = {
        "nom": eq_nom,
        "vaep_total": round(sum(j["vaep"] for j in joueurs_eq), 3),
        "xg_total":   round(sum(j["xg"]   for j in joueurs_eq), 3),
        "buts":       sum(j["buts"] for j in joueurs_eq),
        "tirs":       sum(j["tirs"] for j in joueurs_eq),
        "passes":     sum(j["passes"] for j in joueurs_eq),
        "nb_joueurs": len(joueurs_eq),
    }

# ══════════════════════════════════════════════════════════════════════════════
# TOP POSSESSIONS
# ══════════════════════════════════════════════════════════════════════════════
top_poss = sorted(
    [(num, p) for num, p in possessions.items() if len(p["actions"]) >= 2],
    key=lambda x: x[1]["vaep"], reverse=True
)[:10]

top_poss_data = []
for num, p in top_poss:
    acts = [actions_list[i] for i in p["actions"]]
    top_poss_data.append({
        "num": num,
        "equipe": p["equipe"],
        "nb_actions": len(p["actions"]),
        "vaep": round(p["vaep"], 4),
        "gagnee": p["gagnee"],
        "actions": [{"joueur": a["joueur"], "type": a["type"],
                     "minute": a["minute"], "resultat": a["resultat"],
                     "xg": round(a["xg"],3)} for a in acts]
    })

# BUTS
buts_data = []
seen_buts = set()
for a in actions_list:
    if a["marquer_but"]:
        cle = (a["joueur"], a["minute"])
        if cle not in seen_buts:
            seen_buts.add(cle)
            buts_data.append({
                "joueur": a["joueur"], "equipe": a["equipe"],
                "minute": a["minute"], "corps": a["corps"],
                "xg": round(a["xg"], 3), "vaep": round(a["vaep"], 4)
            })

# TIRS
tirs_data = []
seen_tirs = set()
for a in actions_list:
    if a["type"] == "Shot" and a["xg"] > 0:
        cle = (a["joueur"], a["minute"], a["resultat"])
        if cle not in seen_tirs:
            seen_tirs.add(cle)
            tirs_data.append({
                "joueur": a["joueur"], "equipe": a["equipe"],
                "minute": a["minute"], "corps": a["corps"],
                "resultat": a["resultat"],
                "xg": round(a["xg"], 3), "dxg": round(a["dxg"], 3),
                "xt": round(a["xt"], 4), "dxt": round(a["dxt"], 4),
                "vaep": round(a["vaep"], 4)
            })
tirs_data.sort(key=lambda x: x["xg"], reverse=True)

# JOUEURS JSON
joueurs_json = {n: {
    "nom": d["nom"], "equipe": d["equipe"],
    "xg":   round(d["xg"],   4),
    "vaep": round(d["vaep"], 4),
    "nb_actions": d["nb_actions"],
    "buts": d["buts"], "tirs": d["tirs"],
    "passes": d["passes"], "dribbles": d["dribbles"]
} for n, d in joueurs_data.items()}

joueurs_fus = sorted(
    [joueurs_json[n] for n in equipes_data[nom_fus]],
    key=lambda x: x["xg"], reverse=True
)
joueurs_far = sorted(
    [joueurs_json[n] for n in equipes_data[nom_far]],
    key=lambda x: x["xg"], reverse=True
)

# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION HTML
# ══════════════════════════════════════════════════════════════════════════════
data_js = f"""
const NOM_FUS = {json.dumps(nom_fus)};
const NOM_FAR = {json.dumps(nom_far)};
const EQUIPES_STATS = {json.dumps(equipes_stats)};
const JOUEURS_FUS   = {json.dumps(joueurs_fus)};
const JOUEURS_FAR   = {json.dumps(joueurs_far)};
const TOUS_JOUEURS  = {json.dumps(joueurs_json)};
const BUTS_DATA     = {json.dumps(buts_data)};
const TIRS_DATA     = {json.dumps(tirs_data)};
const TOP_POSS      = {json.dumps(top_poss_data)};
const NB_POSSESSIONS = {len(possessions)};
"""

html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚽ FUS Rabat vs FAR Rabat — Botola Maroc Pro</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;600;700&family=Rajdhani:wght@300;400;500;600;700&family=Barlow+Condensed:wght@300;400;500;600;700&display=swap');

:root {
  --bg:        #060b14;
  --bg2:       #0c1526;
  --bg3:       #111e35;
  --card:      #0f1d32;
  --border:    #1e3055;
  --green:     #00e676;
  --green2:    #00c853;
  --gold:      #ffd600;
  --red:       #ff1744;
  --blue:      #40c4ff;
  --purple:    #e040fb;
  --white:     #f0f4ff;
  --grey:      #8899bb;
  --fus:       #006400;
  --far:       #8b0000;
  --fus-light: #00e676;
  --far-light: #ff5252;
}

* { margin:0; padding:0; box-sizing:border-box; }

body {
  font-family: 'Rajdhani', sans-serif;
  background: var(--bg);
  color: var(--white);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── PITCH BACKGROUND ── */
body::before {
  content:'';
  position:fixed; inset:0; z-index:0;
  background:
    repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(0,230,118,.04) 60px),
    repeating-linear-gradient(0deg,  transparent, transparent 59px, rgba(0,230,118,.04) 60px),
    radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,100,0,.12) 0%, transparent 70%),
    linear-gradient(180deg, #060b14 0%, #060f1a 100%);
  pointer-events:none;
}

/* ── HEADER ── */
.header {
  position:relative; z-index:10;
  background: linear-gradient(180deg, rgba(0,0,0,.95) 0%, rgba(6,11,20,.9) 100%);
  border-bottom: 2px solid var(--green);
  padding: 0;
}

.scoreboard {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 18px 40px 14px;
  gap: 20px;
}

.team-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.team-header.right { align-items: flex-end; }

.team-badge {
  width: 56px; height: 56px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 700;
  font-family: 'Oswald', sans-serif;
  letter-spacing: 1px;
  border: 2px solid;
  flex-shrink: 0;
}
.badge-fus { background: rgba(0,100,0,.3); border-color: var(--fus-light); color: var(--fus-light); }
.badge-far { background: rgba(139,0,0,.3); border-color: var(--far-light); color: var(--far-light); }

.team-row { display: flex; align-items: center; gap: 12px; }
.team-row.right { flex-direction: row-reverse; }

.team-name {
  font-family: 'Oswald', sans-serif;
  font-size: 22px; font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.team-name.fus { color: var(--fus-light); }
.team-name.far { color: var(--far-light); }

.team-sub { font-size: 12px; color: var(--grey); letter-spacing: 1px; text-transform: uppercase; }

.score-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-num {
  font-family: 'Oswald', sans-serif;
  font-size: 52px;
  font-weight: 700;
  line-height: 1;
  text-shadow: 0 0 30px currentColor;
}
.score-num.fus { color: var(--fus-light); }
.score-num.far { color: var(--far-light); }

.score-sep {
  font-family: 'Oswald', sans-serif;
  font-size: 36px;
  color: var(--grey);
  font-weight: 300;
}

.match-info {
  font-size: 11px;
  color: var(--grey);
  letter-spacing: 2px;
  text-transform: uppercase;
  text-align: center;
}

.live-dot {
  display: inline-block;
  width: 8px; height: 8px;
  background: var(--green);
  border-radius: 50%;
  margin-right: 6px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

/* ── STATS BAR ── */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--border);
}
.stat-item {
  padding: 10px 16px;
  text-align: center;
  border-right: 1px solid var(--border);
  position: relative;
}
.stat-item:last-child { border-right: none; }
.stat-val { font-family:'Oswald',sans-serif; font-size:20px; font-weight:600; }
.stat-val.green  { color: var(--green); }
.stat-val.gold   { color: var(--gold); }
.stat-val.blue   { color: var(--blue); }
.stat-val.purple { color: var(--purple); }
.stat-lbl { font-size:11px; color:var(--grey); letter-spacing:1px; text-transform:uppercase; margin-top:2px; }

/* ── NAV ── */
.nav {
  position:relative; z-index:10;
  display: flex;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 0 40px;
  gap: 4px;
  overflow-x: auto;
}
.nav-btn {
  padding: 14px 20px;
  background: none;
  border: none;
  color: var(--grey);
  font-family: 'Oswald', sans-serif;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all .2s;
  white-space: nowrap;
}
.nav-btn:hover { color: var(--white); border-bottom-color: rgba(0,230,118,.4); }
.nav-btn.active { color: var(--green); border-bottom-color: var(--green); }

/* ── MAIN ── */
.main {
  position: relative; z-index:5;
  padding: 30px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.view { display: none; }
.view.active { display: block; }

/* ── SECTION TITLE ── */
.section-title {
  font-family: 'Oswald', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-title::after {
  content:'';
  flex:1;
  height:1px;
  background: linear-gradient(90deg, var(--border), transparent);
}

/* ── PITCH GRID ── */
.pitch-container {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  align-items: start;
}

.pitch-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-top: 20px;
}
.pitch-line {
  width: 2px;
  height: 100%;
  min-height: 400px;
  background: linear-gradient(180deg, transparent, var(--border), var(--border), transparent);
}
.pitch-circle {
  width: 40px; height: 40px;
  border: 2px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

/* ── PLAYER CARD ── */
.players-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.player-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all .2s;
  position: relative;
  overflow: hidden;
}
.player-card::before {
  content:'';
  position:absolute;
  left:0; top:0; bottom:0;
  width:3px;
}
.player-card.fus::before { background: var(--fus-light); }
.player-card.far::before { background: var(--far-light); }
.player-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0,230,118,.4);
  box-shadow: 0 8px 24px rgba(0,0,0,.4);
}
.player-card.selected {
  border-color: var(--green);
  box-shadow: 0 0 20px rgba(0,230,118,.2);
}

.player-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.player-avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Oswald', sans-serif;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-fus { background: rgba(0,230,118,.15); color: var(--fus-light); border: 1px solid rgba(0,230,118,.3); }
.avatar-far { background: rgba(255,82,82,.15); color: var(--far-light); border: 1px solid rgba(255,82,82,.3); }

.player-info { flex: 1; min-width: 0; }
.player-name {
  font-family: 'Oswald', sans-serif;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: .5px;
}
.player-pos { font-size: 11px; color: var(--grey); }

.player-xg-badge {
  font-family: 'Oswald', sans-serif;
  font-size: 13px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(255,214,0,.1);
  color: var(--gold);
  border: 1px solid rgba(255,214,0,.2);
}

.player-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}
.mini-stat {
  text-align: center;
  padding: 4px;
  background: rgba(255,255,255,.03);
  border-radius: 4px;
}
.mini-stat-val {
  font-family: 'Oswald', sans-serif;
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
}
.mini-stat-lbl { font-size: 9px; color: var(--grey); text-transform: uppercase; letter-spacing: .5px; }

/* ── DETAIL PANEL ── */
.detail-panel {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px;
  margin-top: 20px;
  display: none;
}
.detail-panel.show { display: block; }

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.detail-avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Oswald', sans-serif;
  font-size: 24px;
  font-weight: 700;
}

.detail-metrics {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.metric-box {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}
.metric-val {
  font-family: 'Oswald', sans-serif;
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}
.metric-lbl { font-size: 11px; color: var(--grey); text-transform: uppercase; letter-spacing: 1px; }

/* ── TABLE ── */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  font-family: 'Oswald', sans-serif;
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--grey);
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  background: var(--bg3);
}
.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(30,48,85,.5);
}
.data-table tr:hover td { background: rgba(0,230,118,.04); }
.data-table tr.goal-row td { background: rgba(255,214,0,.07); }

/* ── POSSESSION CARD ── */
.poss-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all .2s;
}
.poss-card:hover { border-color: rgba(0,230,118,.4); transform: translateX(4px); }
.poss-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.poss-num {
  font-family: 'Oswald', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: var(--grey);
}
.vaep-badge {
  font-family: 'Oswald', sans-serif;
  font-size: 14px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
}
.vaep-pos { background: rgba(0,230,118,.15); color: var(--green); border: 1px solid rgba(0,230,118,.3); }
.vaep-neg { background: rgba(255,23,68,.1); color: var(--red); border: 1px solid rgba(255,23,68,.2); }
.vaep-neu { background: rgba(136,153,187,.1); color: var(--grey); border: 1px solid rgba(136,153,187,.2); }

.poss-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.act-chip {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 3px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 500;
  letter-spacing: .5px;
  text-transform: uppercase;
}
.chip-pass   { background: rgba(64,196,255,.1);  color: var(--blue); }
.chip-shot   { background: rgba(255,214,0,.1);   color: var(--gold); }
.chip-drib   { background: rgba(224,64,251,.1);  color: var(--purple); }
.chip-goal   { background: rgba(255,214,0,.2);   color: var(--gold); border: 1px solid rgba(255,214,0,.4); }

/* ── GOAL CARD ── */
.goal-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  padding-left: 40px;
}
.goal-timeline::before {
  content:'';
  position:absolute;
  left:15px; top:0; bottom:0;
  width:2px;
  background: linear-gradient(180deg, var(--gold), var(--green));
}
.goal-item {
  background: var(--card);
  border: 1px solid rgba(255,214,0,.3);
  border-radius: 8px;
  padding: 14px 16px;
  position: relative;
}
.goal-item::before {
  content:'⚽';
  position:absolute;
  left:-32px; top:50%;
  transform:translateY(-50%);
  font-size:18px;
  background: var(--bg);
  padding: 2px;
}
.goal-min {
  font-family:'Oswald',sans-serif;
  font-size:28px;
  font-weight:700;
  color: var(--gold);
  line-height:1;
}
.goal-player {
  font-family:'Oswald',sans-serif;
  font-size:17px;
  font-weight:600;
  margin-top:2px;
}

/* ── BAR CHART ── */
.bar-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.bar-fus {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, transparent, var(--fus-light));
  transition: width .6s ease;
}
.bar-far {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--far-light), transparent);
  transition: width .6s ease;
}
.bar-label {
  font-family:'Oswald',sans-serif;
  font-size:11px;
  letter-spacing:1px;
  text-transform:uppercase;
  color:var(--grey);
  text-align:center;
  white-space:nowrap;
}

/* ── COMPARE ── */
.compare-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: start;
}
.compare-select {
  background: var(--bg3);
  border: 1px solid var(--border);
  color: var(--white);
  padding: 10px 14px;
  border-radius: 6px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  width: 100%;
  cursor: pointer;
  margin-bottom: 16px;
}
.vs-badge {
  font-family:'Oswald',sans-serif;
  font-size:24px;
  font-weight:700;
  color:var(--grey);
  text-align:center;
  padding-top:50px;
}
.compare-result {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-top: 16px;
  display: none;
}
.compare-result.show { display: block; }
.compare-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(30,48,85,.5);
}
.compare-val {
  font-family:'Oswald',sans-serif;
  font-size:18px;
  font-weight:600;
}
.compare-val.left { text-align:right; }
.compare-val.winner { color: var(--green); }
.compare-metric-name {
  font-size:11px;
  color:var(--grey);
  text-transform:uppercase;
  letter-spacing:1px;
  text-align:center;
}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .pitch-container { grid-template-columns:1fr; }
  .pitch-divider { display:none; }
  .scoreboard { grid-template-columns:1fr; text-align:center; }
  .team-row.right { flex-direction:row; }
  .detail-metrics { grid-template-columns:repeat(3,1fr); }
  .main { padding:16px; }
  .nav { padding:0 16px; }
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }

/* ── ANIMATIONS ── */
@keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:none} }
.view.active { animation: fadeIn .25s ease; }

.chip-type {
  display:inline-block;
  font-family:'Barlow Condensed',sans-serif;
  font-size:10px;
  padding:2px 7px;
  border-radius:3px;
  font-weight:600;
  letter-spacing:.5px;
  text-transform:uppercase;
}
.chip-Shot { background:rgba(255,214,0,.15); color:var(--gold); }
.chip-Pass { background:rgba(64,196,255,.15); color:var(--blue); }
.chip-Dribble { background:rgba(224,64,251,.15); color:var(--purple); }
.chip-Goal { background:rgba(255,214,0,.3); color:var(--gold); font-weight:700; }
</style>
</head>
<body>

<!-- ══ HEADER ══ -->
<header class="header">
  <div class="scoreboard">
    <div class="team-header">
      <div class="team-row">
        <div class="team-badge badge-fus" id="badgeFus">FUS</div>
        <div>
          <div class="team-name fus" id="nameFus">FUS Rabat</div>
          <div class="team-sub">Botola Maroc Pro</div>
        </div>
      </div>
    </div>

    <div class="score-center">
      <div class="score-display">
        <span class="score-num fus" id="scoreFus">0</span>
        <span class="score-sep">—</span>
        <span class="score-num far" id="scoreFar">0</span>
      </div>
      <div class="match-info">
        <span class="live-dot"></span>Match Analysé
      </div>
      <div class="match-info" id="matchInfo">Chargement...</div>
    </div>

    <div class="team-header right">
      <div class="team-row right">
        <div class="team-badge badge-far" id="badgeFar">FAR</div>
        <div style="text-align:right">
          <div class="team-name far" id="nameFar">FAR Rabat</div>
          <div class="team-sub">Botola Maroc Pro</div>
        </div>
      </div>
    </div>
  </div>

  <div class="stats-bar" id="statsBar">
    <div class="stat-item">
      <div class="stat-val green" id="statPoss">—</div>
      <div class="stat-lbl">Possessions</div>
    </div>
    <div class="stat-item">
      <div class="stat-val gold" id="statTirs">—</div>
      <div class="stat-lbl">Tirs</div>
    </div>
    <div class="stat-item">
      <div class="stat-val blue" id="statJoueurs">—</div>
      <div class="stat-lbl">Joueurs</div>
    </div>
    <div class="stat-item">
      <div class="stat-val purple" id="statActions">—</div>
      <div class="stat-lbl">Actions</div>
    </div>
  </div>
</header>

<!-- ══ NAV ══ -->
<nav class="nav">
  <button class="nav-btn active" onclick="showView('terrain')">⚽ Terrain</button>
  <button class="nav-btn" onclick="showView('buts')">🥅 Buts</button>
  <button class="nav-btn" onclick="showView('tirs')">🎯 Tirs & XG</button>
  <button class="nav-btn" onclick="showView('possessions')">🔄 Possessions</button>
  <button class="nav-btn" onclick="showView('comparer')">⚖️ Comparer</button>
  <button class="nav-btn" onclick="showView('equipes')">📊 Équipes</button>
</nav>

<!-- ══ MAIN ══ -->
<div class="main">

  <!-- VIEW: TERRAIN -->
  <div class="view active" id="view-terrain">
    <div class="section-title">Terrain — Cartes Joueurs</div>
    <div class="pitch-container">

      <!-- FUS -->
      <div>
        <div class="section-title" style="color:var(--fus-light)">
          🟢 <span id="titleFus">FUS Rabat</span>
        </div>
        <div class="players-grid" id="playersFus"></div>
      </div>

      <!-- Séparateur terrain -->
      <div class="pitch-divider">
        <div class="pitch-line"></div>
        <div class="pitch-circle">⚽</div>
        <div class="pitch-line"></div>
      </div>

      <!-- FAR -->
      <div>
        <div class="section-title" style="color:var(--far-light)">
          🔴 <span id="titleFar">FAR Rabat</span>
        </div>
        <div class="players-grid" id="playersFar"></div>
      </div>
    </div>

    <!-- Détail joueur -->
    <div class="detail-panel" id="detailPanel">
      <div class="detail-header">
        <div class="detail-avatar" id="detailAvatar"></div>
        <div>
          <div style="font-family:'Oswald',sans-serif;font-size:22px;font-weight:700" id="detailName"></div>
          <div style="color:var(--grey);font-size:13px" id="detailSub"></div>
        </div>
      </div>
      <div class="detail-metrics" id="detailMetrics"></div>
      <div class="section-title" style="margin-top:8px">Actions du joueur</div>
      <table class="data-table" id="detailActions">
        <thead>
          <tr>
            <th>Min</th><th>Type</th><th>Corps</th><th>Résultat</th>
            <th>XG</th><th>DXG</th><th>XT</th><th>DXT</th><th>VAEP</th>
          </tr>
        </thead>
        <tbody id="detailActionsBody"></tbody>
      </table>
    </div>
  </div>

  <!-- VIEW: BUTS -->
  <div class="view" id="view-buts">
    <div class="section-title">Buts du Match</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:start">
      <div>
        <div id="goalTimeline" class="goal-timeline"></div>
      </div>
      <div>
        <div class="section-title">Statistiques comparées</div>
        <div id="teamBarsContainer"></div>
      </div>
    </div>
  </div>

  <!-- VIEW: TIRS -->
  <div class="view" id="view-tirs">
    <div class="section-title">Tirs avec XG > 0 — classés par danger</div>
    <table class="data-table">
      <thead>
        <tr>
          <th>#</th><th>Joueur</th><th>Équipe</th><th>Min</th>
          <th>Corps</th><th>Résultat</th><th>XG</th><th>DXG</th>
          <th>XT</th><th>DXT</th><th>VAEP</th>
        </tr>
      </thead>
      <tbody id="tirsBody"></tbody>
    </table>
  </div>

  <!-- VIEW: POSSESSIONS -->
  <div class="view" id="view-possessions">
    <div class="section-title">Top 10 Possessions par VAEP</div>
    <div id="possessionsList"></div>
  </div>

  <!-- VIEW: COMPARER -->
  <div class="view" id="view-comparer">
    <div class="section-title">Comparer deux joueurs</div>
    <div class="compare-grid">
      <div>
        <div style="font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:2px;color:var(--green);margin-bottom:8px;text-transform:uppercase">Joueur 1</div>
        <select class="compare-select" id="compareJ1" onchange="updateCompare()"></select>
      </div>
      <div class="vs-badge">VS</div>
      <div>
        <div style="font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:2px;color:var(--far-light);margin-bottom:8px;text-transform:uppercase">Joueur 2</div>
        <select class="compare-select" id="compareJ2" onchange="updateCompare()"></select>
      </div>
    </div>
    <div class="compare-result" id="compareResult"></div>
  </div>

  <!-- VIEW: ÉQUIPES -->
  <div class="view" id="view-equipes">
    <div class="section-title">Statistiques par équipe</div>
    <div id="equipesContent"></div>
  </div>

</div>

<script>
""" + data_js + """

// ── INIT ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const fus = EQUIPES_STATS[NOM_FUS];
  const far = EQUIPES_STATS[NOM_FAR];

  // Header
  document.getElementById('nameFus').textContent = NOM_FUS;
  document.getElementById('nameFar').textContent = NOM_FAR;
  document.getElementById('titleFus').textContent = NOM_FUS;
  document.getElementById('titleFar').textContent = NOM_FAR;
  document.getElementById('badgeFus').textContent = NOM_FUS.split(' ')[0].substring(0,3).toUpperCase();
  document.getElementById('badgeFar').textContent = NOM_FAR.split(' ')[0].substring(0,3).toUpperCase();
  document.getElementById('scoreFus').textContent = fus.buts;
  document.getElementById('scoreFar').textContent = far.buts;
  document.getElementById('matchInfo').textContent = `${NOM_FUS}  ${fus.buts} — ${far.buts}  ${NOM_FAR}`;
  document.getElementById('statPoss').textContent = NB_POSSESSIONS;
  document.getElementById('statTirs').textContent = TIRS_DATA.length;
  document.getElementById('statJoueurs').textContent = JOUEURS_FUS.length + JOUEURS_FAR.length;
  document.getElementById('statActions').textContent = Object.values(TOUS_JOUEURS).reduce((s,j)=>s+j.nb_actions,0);

  buildPlayerCards('playersFus', JOUEURS_FUS, 'fus');
  buildPlayerCards('playersFar', JOUEURS_FAR, 'far');
  buildButs();
  buildTirs();
  buildPossessions();
  buildCompare();
  buildEquipes();
});

// ── NAVIGATION ─────────────────────────────────────────────────────────────
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('view-'+name).classList.add('active');
  event.target.classList.add('active');
}

// ── PLAYER CARDS ────────────────────────────────────────────────────────────
function initials(name) {
  return name.split(' ').map(w=>w[0]).join('').substring(0,2).toUpperCase();
}

function vaepColor(v) {
  if (v > 0.01)  return '#00e676';
  if (v < -0.5)  return '#ff5252';
  if (v < -0.1)  return '#ff9100';
  return '#8899bb';
}

function xgColor(v) {
  if (v > 0.5)  return '#ffd600';
  if (v > 0.1)  return '#ffab40';
  if (v > 0.01) return '#40c4ff';
  return '#8899bb';
}

function buildPlayerCards(containerId, players, side) {
  const cont = document.getElementById(containerId);
  cont.innerHTML = '';
  players.forEach(p => {
    const card = document.createElement('div');
    card.className = `player-card ${side}`;
    card.onclick = () => showPlayerDetail(p.nom, card);

    const vaepC = vaepColor(p.vaep);
    const xgC   = xgColor(p.xg);

    card.innerHTML = `
      <div class="player-card-top">
        <div class="player-avatar avatar-${side}">${initials(p.nom)}</div>
        <div class="player-info">
          <div class="player-name">${p.nom}</div>
          <div class="player-pos">${p.equipe} · ${p.nb_actions} actions</div>
        </div>
        <div class="player-xg-badge" style="color:${xgC};border-color:${xgC}40">xG ${p.xg.toFixed(3)}</div>
      </div>
      <div class="player-stats-row">
        <div class="mini-stat">
          <div class="mini-stat-val" style="color:${vaepC}">${p.vaep.toFixed(3)}</div>
          <div class="mini-stat-lbl">VAEP</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-val" style="color:#ffd600">${p.buts}</div>
          <div class="mini-stat-lbl">Buts</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-val" style="color:#40c4ff">${p.tirs}</div>
          <div class="mini-stat-lbl">Tirs</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-val" style="color:#8899bb">${p.passes}</div>
          <div class="mini-stat-lbl">Passes</div>
        </div>
      </div>`;
    cont.appendChild(card);
  });
}

// ── PLAYER DETAIL ────────────────────────────────────────────────────────────
let selectedCard = null;
function showPlayerDetail(nom, card) {
  if (selectedCard) selectedCard.classList.remove('selected');
  if (selectedCard === card) {
    selectedCard = null;
    document.getElementById('detailPanel').classList.remove('show');
    return;
  }
  selectedCard = card;
  card.classList.add('selected');

  const p = TOUS_JOUEURS[nom];
  const side = p.equipe === NOM_FUS ? 'fus' : 'far';
  const vaepC = vaepColor(p.vaep);
  const xgC   = xgColor(p.xg);

  const panel = document.getElementById('detailPanel');
  const avatar = document.getElementById('detailAvatar');
  avatar.className = `detail-avatar avatar-${side}`;
  avatar.style.width = '64px';
  avatar.style.height = '64px';
  avatar.style.fontSize = '24px';
  avatar.style.fontFamily = "'Oswald', sans-serif";
  avatar.style.fontWeight = '700';
  avatar.textContent = initials(nom);
  if (side==='fus') {
    avatar.style.background='rgba(0,230,118,.15)';
    avatar.style.color='var(--fus-light)';
    avatar.style.border='2px solid rgba(0,230,118,.4)';
  } else {
    avatar.style.background='rgba(255,82,82,.15)';
    avatar.style.color='var(--far-light)';
    avatar.style.border='2px solid rgba(255,82,82,.4)';
  }

  document.getElementById('detailName').textContent = nom;
  document.getElementById('detailSub').textContent  = p.equipe + ' · ' + p.nb_actions + ' actions analysées';

  const metrics = [
    {lbl:'XG',      val: p.xg.toFixed(4),   col: xgC},
    {lbl:'VAEP',    val: p.vaep.toFixed(4),  col: vaepC},
    {lbl:'Buts',    val: p.buts,             col:'#ffd600'},
    {lbl:'Tirs',    val: p.tirs,             col:'#40c4ff'},
    {lbl:'Passes',  val: p.passes,           col:'#8899bb'},
  ];
  document.getElementById('detailMetrics').innerHTML = metrics.map(m => `
    <div class="metric-box">
      <div class="metric-val" style="color:${m.col}">${m.val}</div>
      <div class="metric-lbl">${m.lbl}</div>
    </div>`).join('');

  // Actions du joueur depuis TIRS_DATA + filtrage
  const rows = TIRS_DATA.filter(a => a.joueur === nom);
  // Aussi afficher passes et dribbles depuis TOP_POSS
  const allActs = [];
  TOP_POSS.forEach(poss => {
    poss.actions.forEach(a => {
      if (a.joueur === nom) allActs.push({...a, vaep:poss.vaep, dxg:0, xt:0, dxt:0});
    });
  });

  const displayRows = rows.length > 0 ? rows : allActs.slice(0,10);
  document.getElementById('detailActionsBody').innerHTML = displayRows.length === 0
    ? '<tr><td colspan="9" style="text-align:center;color:var(--grey);padding:20px">Aucun tir enregistré</td></tr>'
    : displayRows.map(a => `
      <tr class="${a.resultat==='Goal'?'goal-row':''}">
        <td>${a.minute}'</td>
        <td><span class="chip-type chip-${a.resultat==='Goal'?'Goal':a.type||'Pass'}">${a.resultat==='Goal'?'⚽ GOAL':a.type||'Pass'}</span></td>
        <td>${a.corps||'—'}</td>
        <td>${a.resultat}</td>
        <td style="color:${xgColor(a.xg||0)};font-weight:600">${(a.xg||0).toFixed(3)}</td>
        <td>${(a.dxg||0).toFixed(3)}</td>
        <td>${(a.xt||0).toFixed(4)}</td>
        <td>${(a.dxt||0).toFixed(4)}</td>
        <td style="color:${vaepColor(a.vaep||0)};font-weight:600">${(a.vaep||0).toFixed(4)}</td>
      </tr>`).join('');

  panel.classList.add('show');
  panel.scrollIntoView({behavior:'smooth', block:'nearest'});
}

// ── BUTS ──────────────────────────────────────────────────────────────────────
function buildButs() {
  const tl = document.getElementById('goalTimeline');
  if (BUTS_DATA.length === 0) {
    tl.innerHTML = '<p style="color:var(--grey)">Aucun but trouvé.</p>';
    return;
  }
  tl.innerHTML = BUTS_DATA.map(b => {
    const isFus = b.equipe === NOM_FUS;
    return `
    <div class="goal-item">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div class="goal-min">${b.minute}'</div>
          <div class="goal-player" style="color:${isFus?'var(--fus-light)':'var(--far-light)'}">${b.joueur}</div>
          <div style="font-size:13px;color:var(--grey);margin-top:4px">${b.equipe} · ${b.corps}</div>
        </div>
        <div style="text-align:right">
          <div style="font-family:'Oswald',sans-serif;font-size:28px;font-weight:700;color:var(--gold)">
            xG ${b.xg.toFixed(3)}
          </div>
          <div style="font-size:12px;color:var(--grey)">VAEP ${b.vaep.toFixed(4)}</div>
        </div>
      </div>
    </div>`;
  }).join('');

  // Barres comparaison
  const fus = EQUIPES_STATS[NOM_FUS];
  const far = EQUIPES_STATS[NOM_FAR];
  const bars = [
    {lbl:'Buts',   fusV:fus.buts,   farV:far.buts,   max:Math.max(fus.buts,far.buts,1)},
    {lbl:'XG',     fusV:fus.xg_total,farV:far.xg_total,max:Math.max(fus.xg_total,far.xg_total,.1)},
    {lbl:'Tirs',   fusV:fus.tirs,   farV:far.tirs,   max:Math.max(fus.tirs,far.tirs,1)},
    {lbl:'Passes', fusV:fus.passes, farV:far.passes, max:Math.max(fus.passes,far.passes,1)},
  ];
  document.getElementById('teamBarsContainer').innerHTML = bars.map(b => `
    <div class="bar-row" style="margin-bottom:16px">
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
        <span style="font-family:'Oswald',sans-serif;font-size:15px;font-weight:600;color:var(--fus-light)">${typeof b.fusV==='number'&&b.fusV%1!==0?b.fusV.toFixed(2):b.fusV}</span>
        <div class="bar-fus" style="width:${Math.round(b.fusV/b.max*100)}%;min-width:4px"></div>
      </div>
      <div class="bar-label">${b.lbl}</div>
      <div style="display:flex;flex-direction:column;align-items:flex-start;gap:4px">
        <span style="font-family:'Oswald',sans-serif;font-size:15px;font-weight:600;color:var(--far-light)">${typeof b.farV==='number'&&b.farV%1!==0?b.farV.toFixed(2):b.farV}</span>
        <div class="bar-far" style="width:${Math.round(b.farV/b.max*100)}%;min-width:4px"></div>
      </div>
    </div>`).join('');
}

// ── TIRS ──────────────────────────────────────────────────────────────────────
function buildTirs() {
  document.getElementById('tirsBody').innerHTML = TIRS_DATA.map((t,i) => `
    <tr class="${t.resultat==='Goal'?'goal-row':''}">
      <td style="color:var(--grey)">${i+1}</td>
      <td style="font-weight:600">${t.joueur}</td>
      <td style="color:${t.equipe===NOM_FUS?'var(--fus-light)':'var(--far-light)'}">${t.equipe}</td>
      <td>${t.minute}'</td>
      <td>${t.corps}</td>
      <td><span class="chip-type chip-${t.resultat==='Goal'?'Goal':'Pass'}">${t.resultat}</span></td>
      <td style="color:${xgColor(t.xg)};font-weight:700">${t.xg.toFixed(3)}</td>
      <td style="color:${t.dxg>0?'var(--green)':t.dxg<0?'var(--red)':'var(--grey)'}">${t.dxg>0?'+':''}${t.dxg.toFixed(3)}</td>
      <td>${t.xt.toFixed(4)}</td>
      <td style="color:${t.dxt>0?'var(--green)':t.dxt<0?'var(--red)':'var(--grey)'}">${t.dxt>0?'+':''}${t.dxt.toFixed(4)}</td>
      <td style="color:${vaepColor(t.vaep)};font-weight:600">${t.vaep>0?'+':''}${t.vaep.toFixed(4)}</td>
    </tr>`).join('');
}

// ── POSSESSIONS ───────────────────────────────────────────────────────────────
function buildPossessions() {
  document.getElementById('possessionsList').innerHTML = TOP_POSS.map(p => {
    const vaepClass = p.vaep > 0.01 ? 'vaep-pos' : p.vaep < -0.01 ? 'vaep-neg' : 'vaep-neu';
    const isFus = p.equipe === NOM_FUS;
    const chips = p.actions.map(a => {
      const isGoal = a.resultat === 'Goal';
      const cls = isGoal ? 'chip-goal' : `chip-${a.type.toLowerCase().substring(0,4) === 'pass' ? 'pass' : a.type.toLowerCase().substring(0,4) === 'shot' ? 'shot' : 'drib'}`;
      return `<span class="act-chip ${cls}">${isGoal?'⚽ GOAL ':a.type} ${a.minute}'</span>`;
    }).join('');
    return `
    <div class="poss-card">
      <div class="poss-header">
        <div>
          <span class="poss-num">Possession #${p.num}</span>
          <span style="font-size:12px;color:${isFus?'var(--fus-light)':'var(--far-light)'};margin-left:10px">${p.equipe}</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <span style="font-size:12px;color:var(--grey)">${p.nb_actions} actions</span>
          <span class="vaep-badge ${vaepClass}">${p.vaep>0?'+':''}${p.vaep.toFixed(4)}</span>
        </div>
      </div>
      <div class="poss-actions">${chips}</div>
    </div>`;
  }).join('');
}

// ── COMPARER ──────────────────────────────────────────────────────────────────
function buildCompare() {
  const allNames = Object.keys(TOUS_JOUEURS).sort();
  ['compareJ1','compareJ2'].forEach((id,i) => {
    const sel = document.getElementById(id);
    sel.innerHTML = allNames.map(n => `<option value="${n}">${n}</option>`).join('');
    sel.selectedIndex = i;
  });
  updateCompare();
}

function updateCompare() {
  const n1 = document.getElementById('compareJ1').value;
  const n2 = document.getElementById('compareJ2').value;
  if (!n1 || !n2 || n1 === n2) return;
  const j1 = TOUS_JOUEURS[n1];
  const j2 = TOUS_JOUEURS[n2];
  const metrics = [
    {lbl:'XG',      v1:j1.xg,        v2:j2.xg,        higher:true,  fmt:(v)=>v.toFixed(4)},
    {lbl:'VAEP',    v1:j1.vaep,      v2:j2.vaep,      higher:true,  fmt:(v)=>v.toFixed(4)},
    {lbl:'Buts',    v1:j1.buts,      v2:j2.buts,      higher:true,  fmt:(v)=>v},
    {lbl:'Tirs',    v1:j1.tirs,      v2:j2.tirs,      higher:true,  fmt:(v)=>v},
    {lbl:'Passes',  v1:j1.passes,    v2:j2.passes,    higher:true,  fmt:(v)=>v},
    {lbl:'Dribbles',v1:j1.dribbles,  v2:j2.dribbles,  higher:true,  fmt:(v)=>v},
    {lbl:'Actions', v1:j1.nb_actions,v2:j2.nb_actions, higher:true,  fmt:(v)=>v},
  ];

  const isFus1 = j1.equipe === NOM_FUS;
  const isFus2 = j2.equipe === NOM_FUS;
  const c1 = isFus1 ? 'var(--fus-light)' : 'var(--far-light)';
  const c2 = isFus2 ? 'var(--fus-light)' : 'var(--far-light)';

  const res = document.getElementById('compareResult');
  res.classList.add('show');
  res.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;margin-bottom:16px">
      <div style="text-align:center">
        <div style="font-family:'Oswald',sans-serif;font-size:18px;font-weight:700;color:${c1}">${n1}</div>
        <div style="font-size:12px;color:var(--grey)">${j1.equipe}</div>
      </div>
      <div style="font-family:'Oswald',sans-serif;font-size:20px;color:var(--grey);text-align:center;line-height:2">VS</div>
      <div style="text-align:center">
        <div style="font-family:'Oswald',sans-serif;font-size:18px;font-weight:700;color:${c2}">${n2}</div>
        <div style="font-size:12px;color:var(--grey)">${j2.equipe}</div>
      </div>
    </div>
    ${metrics.map(m => {
      const w1 = m.higher ? m.v1 > m.v2 : m.v1 < m.v2;
      const w2 = m.higher ? m.v2 > m.v1 : m.v2 < m.v1;
      return `
      <div class="compare-row">
        <div class="compare-val left ${w1?'winner':''}" style="color:${w1?'var(--green)':c1}">${m.fmt(m.v1)}</div>
        <div class="compare-metric-name">${m.lbl}</div>
        <div class="compare-val ${w2?'winner':''}" style="color:${w2?'var(--green)':c2}">${m.fmt(m.v2)}</div>
      </div>`;
    }).join('')}
    <div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--border);text-align:center;font-family:'Oswald',sans-serif;font-size:14px;color:var(--green)">
      ${j1.vaep > j2.vaep ? '✓ ' + n1 + ' a un meilleur VAEP' : j2.vaep > j1.vaep ? '✓ ' + n2 + ' a un meilleur VAEP' : '= VAEP identique'}
    </div>`;
}

// ── ÉQUIPES ────────────────────────────────────────────────────────────────────
function buildEquipes() {
  const fus = EQUIPES_STATS[NOM_FUS];
  const far = EQUIPES_STATS[NOM_FAR];
  const metrics = [
    {lbl:'VAEP Total',   fusV:fus.vaep_total,  farV:far.vaep_total,  fmt:(v)=>v.toFixed(3)},
    {lbl:'XG Total',     fusV:fus.xg_total,    farV:far.xg_total,    fmt:(v)=>v.toFixed(3)},
    {lbl:'Buts',         fusV:fus.buts,         farV:far.buts,         fmt:(v)=>v},
    {lbl:'Tirs',         fusV:fus.tirs,         farV:far.tirs,         fmt:(v)=>v},
    {lbl:'Passes',       fusV:fus.passes,       farV:far.passes,       fmt:(v)=>v},
    {lbl:'Joueurs',      fusV:fus.nb_joueurs,   farV:far.nb_joueurs,   fmt:(v)=>v},
  ];
  document.getElementById('equipesContent').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-bottom:24px">
      <div style="text-align:center;padding:20px;background:var(--card);border:1px solid rgba(0,230,118,.3);border-radius:10px">
        <div style="font-family:'Oswald',sans-serif;font-size:28px;font-weight:700;color:var(--fus-light)">${NOM_FUS}</div>
        <div style="font-size:48px;font-family:'Oswald',sans-serif;font-weight:700;color:var(--fus-light);text-shadow:0 0 30px var(--fus-light)">${fus.buts}</div>
        <div style="color:var(--grey);font-size:13px">Buts marqués</div>
      </div>
      <div style="font-family:'Oswald',sans-serif;font-size:24px;color:var(--grey);text-align:center">—</div>
      <div style="text-align:center;padding:20px;background:var(--card);border:1px solid rgba(255,82,82,.3);border-radius:10px">
        <div style="font-family:'Oswald',sans-serif;font-size:28px;font-weight:700;color:var(--far-light)">${NOM_FAR}</div>
        <div style="font-size:48px;font-family:'Oswald',sans-serif;font-weight:700;color:var(--far-light);text-shadow:0 0 30px var(--far-light)">${far.buts}</div>
        <div style="color:var(--grey);font-size:13px">Buts marqués</div>
      </div>
    </div>
    ${metrics.map(m => {
      const max = Math.max(Math.abs(m.fusV), Math.abs(m.farV), 0.001);
      const pFus = Math.round(Math.abs(m.fusV)/max*100);
      const pFar = Math.round(Math.abs(m.farV)/max*100);
      return `
      <div class="bar-row" style="margin-bottom:20px">
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">
          <span style="font-family:'Oswald',sans-serif;font-size:17px;font-weight:700;color:var(--fus-light)">${m.fmt(m.fusV)}</span>
          <div class="bar-fus" style="width:${pFus}%;min-width:4px;height:10px"></div>
        </div>
        <div class="bar-label" style="font-size:12px">${m.lbl}</div>
        <div style="display:flex;flex-direction:column;align-items:flex-start;gap:6px">
          <span style="font-family:'Oswald',sans-serif;font-size:17px;font-weight:700;color:var(--far-light)">${m.fmt(m.farV)}</span>
          <div class="bar-far" style="width:${pFar}%;min-width:4px;height:10px"></div>
        </div>
      </div>`;
    }).join('')}`;
}
</script>
</body>
</html>"""

# Écriture du fichier HTML
with open("interface.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✓ interface.html généré avec succès !")
print("✓ Ouvrez interface.html dans votre navigateur (Chrome/Edge).")