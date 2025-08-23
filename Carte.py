class Carte:
    """#0: Blanche, #1 Noire"""
    def __init__(self, couleur, lien):
        self.couleur = couleur
        self.lien = lien
    # et en gros une carte c juste une image
    # Méthode __str__ définie en dehors de __init__
    def getCouleur(self):
        if self.couleur == 0:
            return "Blanche"
        else:
            return "Noire"
    def setCouleur(self,couleur):
        self.couleur=couleur
    def getLien(self):
        return self.lien
    def setLien(self,lien):
        self.lien = lien