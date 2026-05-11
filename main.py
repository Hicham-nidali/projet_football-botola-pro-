# main.py

import pandas as pd
from balle import Balle
from joueur import Joueur
from equipe import Equipe
from action import Action
from possession import Possession

# ============================================================
# GRILLE XT (12 lignes x 16 colonnes)
# Source : Karun Singh — Expected Threat (xT)
# Représente la dangerosité de chaque zone du terrain
# Terrain StatsBomb : 120m x 80m
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

# Vérifier les vrais noms d'équipes dans le CSV
noms_equipes = df["team_name"].dropna().unique()
print(f"✓ Equipes dans le CSV : {list(noms_equipes)}")


# ============================================================
# ETAPE 2 : Créer les deux équipes (noms exacts du CSV)
# ============================================================
nom_fus = noms_equipes[0]
nom_far = noms_equipes[1]

equipe_fus = Equipe(nom_fus)
equipe_far = Equipe(nom_far)

equipes = {
    nom_fus: equipe_fus,
    nom_far: equipe_far
}

print(f"✓ Equipes créées : {equipe_fus.get_nom()} | {equipe_far.get_nom()}")


# ============================================================
# ETAPE 3 : Créer les joueurs depuis le CSV (sans doublons)
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

    pos_x = float(pos_x) if not pd.isna(pos_x) else 0.0
    pos_y = float(pos_y) if not pd.isna(pos_y) else 0.0

    j = Joueur(nom, equipe_nom, pos_x, pos_y)
    joueurs[nom] = j

    if equipe_nom in equipes:
        equipes[equipe_nom].ajouter_joueur(j)

print(f"✓ Joueurs créés : {len(joueurs)}")
print(f"   {equipe_fus.get_nom()} : {len(equipe_fus.get_joueurs())} joueurs")
print(f"   {equipe_far.get_nom()} : {len(equipe_far.get_joueurs())} joueurs")


# ============================================================
# ETAPE 4 : Créer les possessions et les actions (sans doublons)
# ============================================================

# Types d'actions valides selon SPADL
types_valides = ["Pass", "Shot", "Dribble"]

possessions = {}

# id unique de chaque événement pour éviter les doublons
ids_vus = set()

for i, ligne in df.iterrows():

    # Ignorer les doublons via l'id unique StatsBomb
    event_id = ligne["id"]
    if event_id in ids_vus:
        continue
    ids_vus.add(event_id)

    type_action = ligne["event_type_name"]
    if type_action not in types_valides:
        continue

    nom_joueur = ligne["player_name"]
    if pd.isna(nom_joueur) or nom_joueur not in joueurs:
        continue

    # Coordonnées depuis le CSV
    start_x = float(ligne["location_x"])     if not pd.isna(ligne["location_x"])     else 0.0
    start_y = float(ligne["location_y"])     if not pd.isna(ligne["location_y"])     else 0.0
    end_x   = float(ligne["end_location_x"]) if not pd.isna(ligne["end_location_x"]) else 0.0
    end_y   = float(ligne["end_location_y"]) if not pd.isna(ligne["end_location_y"]) else 0.0
    minute  = int(ligne["minute"]) if not pd.isna(ligne["minute"]) else 0

    # Partie du corps
    partie_corps = ligne["body_part_name"] if not pd.isna(ligne["body_part_name"]) else "inconnu"

    # Résultat de l'action
    resultat = ligne["outcome_name"] if not pd.isna(ligne["outcome_name"]) else "inconnu"

    # Equipe en possession du ballon
    possession_equipe = ligne["possession_team_name"] if not pd.isna(ligne["possession_team_name"]) else ""

    # Marquer un but ?
    marquer_but = (type_action == "Shot" and resultat == "Goal")

    # Gagner la possession ?
    equipe_action = ligne["team_name"] if not pd.isna(ligne["team_name"]) else ""
    gagner_possession = (equipe_action == possession_equipe)

    # xG depuis StatsBomb
    xg_csv = float(ligne["statsbomb_xg"]) if not pd.isna(ligne["statsbomb_xg"]) else 0.0

    # Créer la Balle à la position de départ
    balle = Balle(start_x, start_y)

    # Créer l'objet Action
    a = Action(
        type_action,
        partie_corps,
        joueurs[nom_joueur],
        balle,
        start_x, start_y,
        end_x, end_y,
        minute,
        resultat,
        possession_equipe,
        marquer_but,
        gagner_possession
    )

    # Calculer XG directement depuis StatsBomb
    a.calculer_xg(xg_csv)

    # Calculer XT (dangerosité de la zone d'arrivée)
    a.calculer_xt(grille_xt)

    # Mettre à jour le xG du joueur
    if xg_csv > 0:
        joueurs[nom_joueur].set_xg(xg_csv)

    # Récupérer ou créer la possession
    num_poss = int(ligne["possession"]) if not pd.isna(ligne["possession"]) else 0
    equipe_obj = equipes.get(possession_equipe, equipe_fus)

    if num_poss not in possessions:
        possessions[num_poss] = Possession(num_poss, equipe_obj)

    possessions[num_poss].ajouter_action(a)

print(f"✓ Possessions créées : {len(possessions)}")


# ============================================================
# ETAPE 5 : Calculer DXG, DXT et VAEP par possession
# ============================================================
for num, poss in possessions.items():
    actions = poss.actions
    k = len(actions)

    if k < 2:
        poss.gagnee = False
        for a in actions:
            if a.gagner_possession:
                poss.gagnee = True
        if poss.gagnee:
            poss.perdue = False
        else:
            poss.perdue = True
        continue

    # Calculer DXG (différence xG entre actions consécutives)
    for idx in range(k):
        xg_avant = actions[idx - 1].xg if idx > 0 else 0.0
        actions[idx].calculer_dxg(xg_avant)

    # Calculer DXT (différence XT entre actions consécutives)
    for idx in range(k):
        actions[idx].calculer_dxt(grille_xt)

    # Calculer VAEP pour chaque action de la possession
    for a in actions:
        a.calculer_vaep(actions)

    # Mettre à jour le VAEP de chaque joueur
    for a in actions:
        joueurs[a.joueur.get_nom()].set_vaep(
            joueurs[a.joueur.get_nom()].vaep + a.vaep
        )

    # Marquer la possession gagnée ou perdue
    if len(actions) >= 1:
        poss.gagnee = False
        for a in actions:
            if a.gagner_possession:
                poss.gagnee = True
        if poss.gagnee:
            poss.perdue = False
        else:
            poss.perdue = True

print("✓ DXG, DXT et VAEP calculés pour toutes les possessions")


# ============================================================
# ETAPE 6 : Affichage automatique des résultats
# ============================================================

print("\n" + "=" * 60)
print("   RESULTATS PAR EQUIPE")
print("=" * 60)
equipe_fus.afficher()
equipe_far.afficher()

print("\n" + "=" * 60)
print(f"   TOP 5 JOUEURS PAR VAEP — {equipe_fus.get_nom()}")
print("=" * 60)
tries_fus = sorted(equipe_fus.get_joueurs(), key=lambda j: j.vaep, reverse=True)
for j in tries_fus[:5]:
    j.afficher()

print("\n" + "=" * 60)
print(f"   TOP 5 JOUEURS PAR VAEP — {equipe_far.get_nom()}")
print("=" * 60)
tries_far = sorted(equipe_far.get_joueurs(), key=lambda j: j.vaep, reverse=True)
for j in tries_far[:5]:
    j.afficher()

print("\n" + "=" * 60)
print("   TIRS DU MATCH (1 ligne par tir unique)")
print("=" * 60)
vus = set()
for num, poss in possessions.items():
    for a in poss.actions:
        if a.type_action == "Shot" and a.xg > 0:
            cle = (a.joueur.get_nom(), a.minute, a.resultat)
            if cle not in vus:
                vus.add(cle)
                a.afficher()


# ============================================================
# ETAPE 7 : Menu interactif — input utilisateur
# ============================================================

continuer = True

while continuer:
    print("\n" + "=" * 60)
    print("   MENU INTERACTIF")
    print("=" * 60)
    print("1 - Stats d'un joueur spécifique")
    print("2 - Liste de tous les joueurs")
    print("3 - Détail d'une possession")
    print("4 - Meilleures possessions par VAEP")
    print("5 - Buts du match")
    print("6 - Comparer deux joueurs")
    print("7 - Quitter")
    print("-" * 60)

    choix = input("Votre choix (1/2/3/4/5/6/7) : ").strip()

    # ----------------------------------------------------------
    if choix == "1":
        print("\nJoueurs disponibles :")
        for nom in sorted(joueurs.keys()):
            print(f"   - {nom}")
        nom = input("\nEntrez le nom exact du joueur : ").strip()
        if nom in joueurs:
            print("\n" + "-" * 60)
            joueurs[nom].afficher()
            print("\n   Actions de ce joueur :")
            nb = 0
            for num, poss in possessions.items():
                for a in poss.actions:
                    if a.joueur.get_nom() == nom:
                        a.afficher()
                        nb = nb + 1
            print(f"\n   Total actions : {nb}")
        else:
            print(f"❌ Joueur '{nom}' non trouvé.")

    # ----------------------------------------------------------
    elif choix == "2":
        equipe_choisie = input(
            f"Quelle équipe ? ({equipe_fus.get_nom()} / {equipe_far.get_nom()}) : "
        ).strip()

        if equipe_choisie in equipes:
            print(f"\n--- Joueurs de {equipe_choisie} ---")
            liste = sorted(
                equipes[equipe_choisie].get_joueurs(),
                key=lambda j: j.vaep,
                reverse=True
            )
            for j in liste:
                j.afficher()
        else:
            print("❌ Equipe non trouvée.")

    # ----------------------------------------------------------
    elif choix == "3":
        print(f"\nNuméro de possession disponible : 1 à {max(possessions.keys())}")
        num_str = input("Entrez le numéro de possession : ").strip()
        if num_str.isdigit() and int(num_str) in possessions:
            num = int(num_str)
            poss = possessions[num]
            print("\n" + "-" * 60)
            poss.afficher()
            print(f"\n   Actions de cette possession ({poss.nb_actions()}) :")
            for a in poss.actions:
                a.afficher()
        else:
            print("❌ Possession non trouvée.")

    # ----------------------------------------------------------
    elif choix == "4":
        print("\n--- Top 10 possessions par VAEP (k >= 2 actions) ---")
        possessions_valides = []
        for p in possessions.values():
            if p.nb_actions() >= 2:
                possessions_valides.append(p)

        possessions_triees = sorted(
            possessions_valides,
            key=lambda p: p.calculer_vaep_possession(),
            reverse=True
        )
        for p in possessions_triees[:10]:
            p.afficher()

    # ----------------------------------------------------------
    elif choix == "5":
        print("\n--- Buts du match ---")
        nb_buts = 0
        for num, poss in possessions.items():
            for a in poss.actions:
                if a.marquer_but:
                    print(f"\n⚽ BUT !")
                    a.afficher()
                    nb_buts = nb_buts + 1
        if nb_buts == 0:
            print("Aucun but trouvé.")
        else:
            print(f"\nTotal buts : {nb_buts}")

    # ----------------------------------------------------------
    elif choix == "6":
        print("\nJoueurs disponibles :")
        for nom in sorted(joueurs.keys()):
            print(f"   - {nom}")
        nom1 = input("\nJoueur 1 : ").strip()
        nom2 = input("Joueur 2 : ").strip()
        if nom1 in joueurs and nom2 in joueurs:
            j1 = joueurs[nom1]
            j2 = joueurs[nom2]
            print("\n" + "-" * 60)
            print("COMPARAISON :")
            print(f"   {'Métrique':<15} {'':>5} {nom1:<30} {nom2:<30}")
            print("-" * 60)
            print(f"   {'xG':<15} {'':>5} {j1.get_xg():<30.4f} {j2.get_xg():<30.4f}")
            print(f"   {'VAEP':<15} {'':>5} {j1.vaep:<30.4f} {j2.vaep:<30.4f}")
            print(f"   {'Equipe':<15} {'':>5} {j1.equipe:<30} {j2.equipe:<30}")
            # Compter les actions de chaque joueur
            nb1 = 0
            nb2 = 0
            for num, poss in possessions.items():
                for a in poss.actions:
                    if a.joueur.get_nom() == nom1:
                        nb1 = nb1 + 1
                    if a.joueur.get_nom() == nom2:
                        nb2 = nb2 + 1
            print(f"   {'Nb actions':<15} {'':>5} {nb1:<30} {nb2:<30}")
            print("-" * 60)
            if j1.vaep > j2.vaep:
                print(f"   ✓ {nom1} a un meilleur VAEP")
            elif j2.vaep > j1.vaep:
                print(f"   ✓ {nom2} a un meilleur VAEP")
            else:
                print("   = VAEP identique")
        else:
            print("❌ Un ou deux joueurs non trouvés.")

    # ----------------------------------------------------------
    elif choix == "7":
        print("\nFin de l'analyse. Au revoir !")
        continuer = False

    # ----------------------------------------------------------
    else:
        print("❌ Choix invalide. Entrez un chiffre entre 1 et 7.")


print("\n" + "=" * 60)
print("   FIN DE L'ANALYSE")
print("=" * 60)