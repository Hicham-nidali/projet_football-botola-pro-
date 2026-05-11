# action.py

class Action:
    type_action = None
    partie_corps = None
    joueur = None
    balle = None
    start_x = None
    start_y = None
    end_x = None
    end_y = None
    minute = None
    resultat = None
    xg = None
    dxg = None
    xt = None
    dxt = None
    vaep = None
    possession_equipe = None
    marquer_but = None
    gagner_possession = None

    # Constructeur
    def __init__(self, type_action, partie_corps, joueur, balle,
                 start_x, start_y, end_x, end_y,
                 minute, resultat, possession_equipe,
                 marquer_but, gagner_possession):
        self.type_action = type_action
        self.partie_corps = partie_corps
        self.joueur = joueur
        self.balle = balle
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.minute = minute
        self.resultat = resultat
        self.possession_equipe = possession_equipe
        self.marquer_but = marquer_but
        self.gagner_possession = gagner_possession
        self.xg = 0.0
        self.dxg = 0.0
        self.xt = 0.0
        self.dxt = 0.0
        self.vaep = 0.0

    # Calculer xG (utilise directement la colonne statsbomb_xg du CSV)
    def calculer_xg(self, xg_csv):
        if xg_csv is not None and 0 <= xg_csv <= 1:
            self.xg = xg_csv
        return self.xg

    # Calculer DXG = xG_après - xG_avant
    def calculer_dxg(self, xg_avant):
        self.dxg = self.xg - xg_avant
        return self.dxg

    # Calculer XT (dangerosité de la zone d'arrivée)
    def calculer_xt(self, grille):
        ligne = int(self.end_y / 8)
        colonne = int(self.end_x / 10.5)
        if 0 <= ligne < 12 and 0 <= colonne < 16:
            self.xt = grille[ligne][colonne]
        return self.xt

    # Calculer DXT = XT_fin - XT_début
    def calculer_dxt(self, grille):
        ligne_debut = int(self.start_y / 8)
        col_debut = int(self.start_x / 10.5)
        xt_debut = 0.0
        if 0 <= ligne_debut < 12 and 0 <= col_debut < 16:
            xt_debut = grille[ligne_debut][col_debut]
        self.dxt = self.xt - xt_debut
        return self.dxt

    # Calculer VAEP = P(marquer) - P(encaisser) sur k actions
    def calculer_vaep(self, actions):
        k = len(actions)
        if k < 2:
            self.vaep = 0.0
            return self.vaep

        somme_xg = 0.0
        nb_buts_adversaire = 0

        for a in actions:
            somme_xg = somme_xg + a.xg
            if not a.gagner_possession and a.xg > 0:
                nb_buts_adversaire = nb_buts_adversaire + 1

        p_marquer = somme_xg / k
        p_encaisser = nb_buts_adversaire / k
        self.vaep = p_marquer - p_encaisser
        return self.vaep

    # Méthode d'affichage
    def afficher(self):
        print(f"\n  Action   : {self.type_action}")
        print(f"  Corps    : {self.partie_corps}")
        print(f"  Joueur   : {self.joueur.get_nom()}")
        print(f"  Minute   : {self.minute}")
        print(f"  Résultat : {self.resultat}")
        print(f"  xG       : {self.xg:.4f}")
        print(f"  DXG      : {self.dxg:.4f}")
        print(f"  XT       : {self.xt:.4f}")
        print(f"  DXT      : {self.dxt:.4f}")
        print(f"  VAEP     : {self.vaep:.4f}")
        print(f"  {'-'*40}")