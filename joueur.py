# joueur.py

class Joueur:
    nom = None
    equipe = None
    position_x = None
    position_y = None
    xg = None
    vaep = None

    # Constructeur
    def __init__(self, nom, equipe, position_x, position_y):
        self.nom = nom
        self.equipe = equipe
        self.position_x = position_x
        self.position_y = position_y
        self.xg = 0.0
        self.vaep = 0.0

    # Getter nom
    def get_nom(self):
        return self.nom

    # Getter position
    def get_position(self):
        return (self.position_x, self.position_y)

    # Getter xg
    def get_xg(self):
        return self.xg

    # Setter xG — additionne au lieu de remplacer
    # Un joueur accumule ses xG sur toutes ses actions
    def set_xg(self, valeur):
        if 0 <= valeur <= 1:
            self.xg = self.xg + valeur   # ← on additionne !

    # Setter vaep
    def set_vaep(self, valeur):
        self.vaep = valeur

    # Méthode d'affichage
    def afficher(self):
        print(f"Joueur : {self.nom} | Equipe : {self.equipe} | "
              f"xG : {self.xg:.3f} | VAEP : {self.vaep:.3f}")