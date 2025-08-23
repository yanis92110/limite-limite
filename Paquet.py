from Carte import Carte
from random import shuffle
import os
class Paquet:
    """Classe représentant un paquet"""
    def __init__(self, rempli: bool):
        """Initialisation d'un paquet"""
        self.cartes = []
        if rempli:
            self.remplir()
            self.battre()

    def __str__(self):
        """Affichage du paquet"""
        return '\n'.join(str(carte) for carte in self.cartes)


    def remplir(self):
        """Méthode qui initialise un paquet de cartes mélangé"""
        for nom_fichier in os.listdir("img"):
            chemin = os.path.join("img", nom_fichier)
            if os.path.isfile(chemin):
                self.cartes.append(Carte(0,chemin))

    def pop_carte(self):
        return self.cartes.pop()
        
    def ajouter_carte(self, carte: Carte):
        self.cartes.append(carte)
    def getCarte(self, index: int):
        return self.cartes[index]
    def printDerniereCarte(self):
        if not self.est_vide():
            print(self.cartes[-1])



    def battre(self):
        shuffle(self.cartes)
    def est_vide(self):
        return self.cartes == []
    
