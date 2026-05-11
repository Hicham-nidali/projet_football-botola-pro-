# vaep.py
# Fonctions utilitaires pour le calcul VAEP
# VAEP = P(marquer d'ici k actions) - P(encaisser d'ici k actions)

# Calculer le VAEP total d'une liste d'actions
def calculer_vaep_liste(actions):
    total = 0.0
    for a in actions:
        total = total + a.vaep
    return total

# Calculer le VAEP moyen d'une liste d'actions
def calculer_vaep_moyen(actions):
    if len(actions) == 0:
        return 0.0
    return calculer_vaep_liste(actions) / len(actions)

# Trouver l'action avec le meilleur VAEP dans une liste
def meilleure_action(actions):
    if len(actions) == 0:
        return None
    meilleure = actions[0]
    for a in actions:
        if a.vaep > meilleure.vaep:
            meilleure = a
    return meilleure