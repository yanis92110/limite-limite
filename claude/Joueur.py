from Paquet import Paquet
from Carte import Carte

class Joueur():
    def __init__(self, paquet, pseudo, socket):
        self.socket = socket
        self.cartes = []
        self.pseudo = pseudo
        self.score = 0
        self.estRoi = False
        
        # Distribuer 8 cartes au départ
        for i in range(8):
            if not paquet.est_vide():
                carte = paquet.pop_carte()
                self.cartes.append(carte)

    def __str__(self):
        return f"Main de {self.pseudo} ({self.nombreCartes()} cartes, Score: {self.score})"

    def getCarte(self, index):
        if 0 <= index < len(self.cartes):
            return self.cartes[index]
        return None

    def setCarte(self, index, carte):
        if 0 <= index < len(self.cartes):
            self.cartes[index] = carte
    
    def setRoi(self, boolean):
        self.estRoi = boolean

    def ajouterCarte(self, carte):
        self.cartes.append(carte)

    def retirerCarte(self, index):
        if 0 <= index < len(self.cartes):
            return self.cartes.pop(index)
        return None

    def nombreCartes(self):
        return len(self.cartes)

    def montrerCarte(self, index):
        carte = self.getCarte(index)
        if carte:
            print(f"Carte {index}: {carte.getLien()}")

    def addScore(self, valeur):
        self.score += valeur
    
    def afficherMain(self):
        """Affiche toute la main du joueur"""
        print(f"\n=== Main de {self.pseudo} ===")
        for i, carte in enumerate(self.cartes):
            print(f"{i}: {carte.getLien()}")
        print(f"Score: {self.score}")
        if self.estRoi:
            print("👑 VOUS ÊTES LE ROI")
        print("=" * 30)