from Carte import Carte
from random import shuffle
import os

class Paquet:
    """Classe représentant un paquet"""
    def __init__(self, rempli: bool, type_cartes="blanches"):
        """Initialisation d'un paquet"""
        self.cartes = []
        self.type_cartes = type_cartes
        if rempli:
            self.remplir()
            self.battre()

    def __str__(self):
        """Affichage du paquet"""
        return '\n'.join(str(carte) for carte in self.cartes)

    def remplir(self):
        """Méthode qui initialise un paquet de cartes mélangé"""
        dossier = "img_blanches" if self.type_cartes == "blanches" else "img_noires"
        
        # Si les dossiers spécifiques n'existent pas, utiliser le dossier img général
        if not os.path.exists(dossier):
            print(f"LE DOSSIER {dossier} NEXISTE PAS")
            dossier = "img"
        
        if os.path.exists(dossier):
            for nom_fichier in os.listdir(dossier):
                chemin = os.path.join(dossier, nom_fichier)
                if os.path.isfile(chemin):
                    couleur = 0 if self.type_cartes == "blanches" else 1
                    self.cartes.append(Carte(couleur, chemin))
        else:
            # Créer des cartes par défaut pour les tests
            if self.type_cartes == "blanches":
                for i in range(50):
                    self.cartes.append(Carte(0, f"carte_blanche_{i}.jpg"))
            else:
                for i in range(20):
                    self.cartes.append(Carte(1, f"carte_noire_{i}.jpg"))

    def pop_carte(self):
        if self.cartes:
            return self.cartes.pop()
        return None
        
    def ajouter_carte(self, carte: Carte):
        self.cartes.append(carte)
        
    def getCarte(self, index: int):
        if 0 <= index < len(self.cartes):
            return self.cartes[index]
        return None
        
    def printDerniereCarte(self):
        if not self.est_vide():
            print(self.cartes[-1])

    def battre(self):
        shuffle(self.cartes)
        
    def est_vide(self):
        return len(self.cartes) == 0