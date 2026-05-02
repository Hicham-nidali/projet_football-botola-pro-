# main.py

import pandas as pd
from balle import Balle
from joueur import Joueur
from equipe import Equipe
from action import Action
from possession import Possession

# ============================================================
# GRILLE XT (12 lignes x 16 colonnes)
# Représente la dangerosité de chaque zone du terrain
# Valeurs plus élevées = zones plus dangereuses (près du but)
# ============================================================
grille_xt = [
    [0.00, 0.00, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.00, 0.00],
    [0.00, 0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01, 0.00],
    [0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01],
    [0.01, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.01],
    [0.01, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.03, 0.03, 0.02, 0.02, 0.01],
    [0.02, 0.02, 0.03, 0.03, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02],
    [0.02, 0.03, 0.03, 0.04, 0.05, 0.06, 0.07, 0.07, 0.07, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03, 0.02],
    [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.10, 0.10, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02],
    [0.03, 0.04, 0.05, 0.07, 0.09, 0.12, 0.15, 0.17, 0.17, 0.15, 0.12, 0.09, 0.07, 0.05, 0.04, 0.03],
    [0.04, 0.05, 0.07, 0.10, 0.14, 0.19, 0.24, 0.27, 0.27, 0.24, 0.19, 0.14, 0.10, 0.07, 0.05, 0.04],
    [0.05, 0.07, 0.11, 0.16, 0.22, 0.31, 0.40, 0.47, 0.47, 0.40, 0.31, 0.22, 0.16, 0.11, 0.07, 0.05],
    [0.07, 0.11, 0.17, 0.26, 0.38, 0.54, 0.68, 0.76, 0.76, 0.68, 0.54, 0.38, 0.26, 0.17, 0.11, 0.07],
]


# ============================================================
# ETAPE 1 : Lire le fichier CSV
# ============================================================
print("=" * 60)
print("   ANALYSE MATCH FUS RABAT vs FAR — Botola Maroc Pro")
print("=" * 60)

df = pd.read_csv("fus_FAR.csv", low_memory=False)
print(f"\n✓ CSV chargé : {len(df)} lignes, {len(df.columns)} colonnes")


# ============================================================
# ETAPE 2 : Créer les deux équipes
# ============================================================
equipe_fus = Equipe("FUS Rabat")
equipe_far = Equipe("FAR")

equipes = {
    "FUS Rabat": equipe_fus,
    "FAR": equipe_far
}

print(f"\n✓ Equipes créées : {equipe_fus.get_nom()} | {equipe_far.get_nom()}")


# ============================================================
# ETAPE 3 : Créer les joueurs depuis le CSV
# ============================================================
joueurs = {}

for i, ligne in df.iterrows():
    nom = ligne["player_name"]
    equipe_nom = ligne["team_name"]
    pos_x = ligne["location_x"]
    pos_y = ligne["location_y"]

    if pd.isna(nom) or pd.isna(equipe_nom):
        continue
    if nom in joueurs:
        continue
    if pd.isna(pos_x):
        pos_x = 0.0
    if pd.isna(pos_y):
        pos_y = 0.0

    j = Joueur(nom, equipe_nom, float(pos_x), float(pos_y))
    joueurs[nom] = j

    if equipe_nom in equipes:
        equipes[equipe_nom].ajouter_joueur(j)

print(f"✓ Joueurs créés : {len(joueurs)}")
print(f"   {equipe_fus.get_nom()} : {len(equipe_fus.get_joueurs())} joueurs")
print(f"   {equipe_far.get_nom()} : {len(equipe_far.get_joueurs())} joueurs")


# ============================================================
# ETAPE 4 : Créer les actions et les possessions
# ============================================================

# Types d'actions qu'on garde (Passe, Tir, Dribble)
types_valides = ["Pass", "Shot", "Dribble"]

possessions = {}
liste_actions = []

for i, ligne in df.iterrows():

    type_action = ligne["event_type_name"]
    if type_action not in types_valides:
        continue

    nom_joueur = ligne["player_name"]
    if pd.isna(nom_joueur):
        continue
    if nom_joueur not in joueurs:
        continue

    # Récupérer les données depuis le CSV
    start_x = ligne["location_x"] if not pd.isna(ligne["location_x"]) else 0.0
    start_y = ligne["location_y"] if not pd.isna(ligne["location_y"]) else 0.0
    end_x   = ligne["end_location_x"] if not pd.isna(ligne["end_location_x"]) else 0.0
    end_y   = ligne["end_location_y"] if not pd.isna(ligne["end_location_y"]) else 0.0
    minute  = int(ligne["minute"]) if not pd.isna(ligne["minute"]) else 0

    # Partie du corps
    partie_corps = ligne["body_part_name"] if not pd.isna(ligne["body_part_name"]) else "inconnu"

    # Résultat de l'action
    resultat = ligne["outcome_name"] if not pd.isna(ligne["outcome_name"]) else "inconnu"

    # Equipe en possession
    possession_equipe = ligne["possession_team_name"] if not pd.isna(ligne["possession_team_name"]) else ""

    # Marquer un but ?
    marquer_but = (type_action == "Shot" and resultat == "Goal")

    # Gagner possession ?
    equipe_action = ligne["team_name"] if not pd.isna(ligne["team_name"]) else ""
    gagner_possession = (equipe_action == possession_equipe)

    # xG depuis le CSV
    xg_csv = ligne["statsbomb_xg"] if not pd.isna(ligne["statsbomb_xg"]) else 0.0

    # Créer la Balle
    balle = Balle(float(start_x), float(start_y))

    # Créer l'Action
    a = Action(
        type_action,
        partie_corps,
        joueurs[nom_joueur],
        balle,
        float(start_x), float(start_y),
        float(end_x), float(end_y),
        minute,
        resultat,
        possession_equipe,
        marquer_but,
        gagner_possession
    )

    # Calculer les métriques
    xg_avant = liste_actions[-1].xg if len(liste_actions) > 0 else 0.0
    a.calculer_xg(float(xg_csv))
    a.calculer_dxg(xg_avant)
    a.calculer_xt(grille_xt)
    a.calculer_dxt(grille_xt)

    # Mettre à jour le xG du joueur
    joueurs[nom_joueur].set_xg(float(xg_csv))

    liste_actions.append(a)

    # Gérer la possession
    num_poss = int(ligne["possession"]) if not pd.isna(ligne["possession"]) else 0
    equipe_poss_nom = possession_equipe

    if num_poss not in possessions:
        equipe_obj = equipes.get(equipe_poss_nom, equipe_fus)
        possessions[num_poss] = Possession(num_poss, equipe_obj)

    possessions[num_poss].ajouter_action(a)

print(f"✓ Actions créées : {len(liste_actions)}")
print(f"✓ Possessions créées : {len(possessions)}")


# ============================================================
# ETAPE 5 : Calculer VAEP pour chaque possession
# ============================================================
for num, poss in possessions.items():
    if poss.nb_actions() >= 2:
        for a in poss.actions:
            a.calculer_vaep(poss.actions)
        # Mettre à jour le VAEP du joueur
        for a in poss.actions:
            joueur_obj = a.joueur
            joueur_obj.set_vaep(joueur_obj.vaep + a.vaep)

print("✓ VAEP calculé pour toutes les possessions")


# ============================================================
# ETAPE 6 : Afficher les résultats
# ============================================================

print("\n" + "=" * 60)
print("   RESULTATS PAR EQUIPE")
print("=" * 60)

equipe_fus.afficher()
equipe_far.afficher()

# Top 5 joueurs par VAEP — FUS Rabat
print("\n" + "=" * 60)
print(f"   TOP 5 JOUEURS PAR VAEP — {equipe_fus.get_nom()}")
print("=" * 60)

joueurs_fus = equipe_fus.get_joueurs()
joueurs_fus_tries = sorted(joueurs_fus, key=lambda j: j.vaep, reverse=True)
for j in joueurs_fus_tries[:5]:
    j.afficher()

# Top 5 joueurs par VAEP — FAR
print("\n" + "=" * 60)
print(f"   TOP 5 JOUEURS PAR VAEP — {equipe_far.get_nom()}")
print("=" * 60)

joueurs_far = equipe_far.get_joueurs()
joueurs_far_tries = sorted(joueurs_far, key=lambda j: j.vaep, reverse=True)
for j in joueurs_far_tries[:5]:
    j.afficher()

# Quelques actions importantes (tirs avec xG > 0)
print("\n" + "=" * 60)
print("   TIRS AVEC XG > 0")
print("=" * 60)

nb_tirs = 0
for a in liste_actions:
    if a.type_action == "Shot" and a.xg > 0:
        a.afficher()
        nb_tirs = nb_tirs + 1

print(f"\nTotal tirs avec xG > 0 : {nb_tirs}")

print("\n" + "=" * 60)
print("   FIN DE L'ANALYSE")
print("=" * 60)