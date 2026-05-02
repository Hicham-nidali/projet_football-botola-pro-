# equipe.py

class Equipe:
    nom = None
    joueurs = None

    # Constructeur
    def __init__(self, nom):
        self.nom = nom
        self.joueurs = []

    # Ajouter un joueur à l'équipe
    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)

    # Getter liste joueurs
    def get_joueurs(self):
        return self.joueurs

    # Getter nom équipe
    def get_nom(self):
        return self.nom

    # Calculer le VAEP total de l'équipe
    def get_vaep_total(self):
        total = 0.0
        for joueur in self.joueurs:
            total = total + joueur.vaep
        return total

    # Méthode d'affichage
    def afficher(self):
        print(f"Equipe : {self.nom} | Joueurs : {len(self.joueurs)} | VAEP total : {self.get_vaep_total():.3f}")