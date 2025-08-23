from Carte import Carte
from Paquet import Paquet
from Joueur import Joueur
import server
from time import *
from random import choice

class Partie():
    """Instance de jeu"""
    def __init__(self,nbjoueurs: int):
        """Constructeur qui prend en parametre un nombre de joueur.
        Il initialise un paquet rempli et mélangé.
        Puis il créer autant de mains que de nombre de joueurs"""
        self.cartesNoires: Paquet = Paquet(True)
        self.cartesBlanches: Paquet = Paquet(True)
        self.defausse: Paquet = Paquet(False)
        self.continuer: bool = True
        self.joueurs: list = [Joueur(self.paquet, _) for _ in range(len(server.clients))]
        self.roi: Joueur = choice(self.joueurs)
        self.choix: list = []
        #Un joueur a toujours 8 cartes
        #Il y a un roi qui attend que tlm ait choisi sa carte, choisi aléatoirement pour le premier tour
    
    def pioche(self,joueur: Joueur):
        if self.paquet.est_vide():
            self.paquet ,self.defausse = self.defausse, self.paquet
            self.paquet.battre()
        joueur.ajouterCarte(self.paquet.pop_carte())

    def demander_carte(self):
        self.choix.clear()
        for j in self.joueurs:
            if not j.estRoi:
                j.socket.sendall("Choisissez une carte".encode("utf-8"))
        # attendre toutes les réponses
        while len(self.choix) < len(self.joueurs) - 1:
            for j in self.joueurs:
                if not j.estRoi:
                    try:
                        data = j.socket.recv(1024).decode("utf-8").strip()
                        if j.pseudo not in self.choix:
                            self.choix[j.pseudo] = data
                    except:
                        pass
    def jouer(self):
        print(f"Le roi est {self.roi}")
        carteNoireActuelle: Carte = self.cartesNoires.pop_carte()
        print(f"La carte noire actuelle est {carteNoireActuelle}")
        

