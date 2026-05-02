# balle.py

class Balle:
    x = None
    y = None

    # Constructeur
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Getter position
    def get_position(self):
        return (self.x, self.y)

    # Déplacer la balle vers une nouvelle position
    def deplacer(self, x, y):
        self.x = x
        self.y = y

    # Méthode d'affichage
    def afficher(self):
        print(f"Balle en position : ({self.x}, {self.y})")