# possession.py

class Possession:
    num_possession = None
    equipe = None
    actions = None
    gagnee = None
    perdue = None

    # Constructeur
    def __init__(self, num_possession, equipe):
        self.num_possession = num_possession
        self.equipe = equipe
        self.actions = []
        self.gagnee = False
        self.perdue = False

    # Ajouter une action (max 5)
    def ajouter_action(self, action):
        if len(self.actions) < 5:
            self.actions.append(action)

    # Nombre d'actions dans la possession
    def nb_actions(self):
        return len(self.actions)

    # Calculer VAEP total de la possession
    def calculer_vaep_possession(self):
        if len(self.actions) < 2:
            return 0.0
        total = 0.0
        for action in self.actions:
            total = total + action.calculer_vaep(self.actions)
        return total

    # Méthode d'affichage
    def afficher(self):
        print(f"Possession #{self.num_possession} | Equipe : {self.equipe.get_nom()} | "
              f"Actions : {self.nb_actions()} | "
              f"Gagnée : {self.gagnee} | Perdue : {self.perdue} | "
              f"VAEP : {self.calculer_vaep_possession():.4f}")