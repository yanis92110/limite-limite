from Paquet import Paquet
from Carte import Carte
class Joueur():
    def __init__(self, paquet, pseudo, socket):
        super().__init__()
        self.socket = socket
        self.cartes: list = []
        self.pseudo: str = pseudo
        self.score: int = 0
        self.estRoi: bool = False
        for i in range(0, 8):
            carte = paquet.pop_carte()
            self.cartes.append(carte)

    def __str__(self):
        return f"Main de {self.pseudo}"

    def getCarte(self, index: int):
        return self.cartes[index]

    def setCarte(self, index: int, carte: Carte):
        self.cartes[index] = carte
    
    def setRoi(self, boolean:bool):
        self.estRoi = boolean

    def ajouterCarte(self, carte: Carte):
        self.cartes.append(carte)

    def retirerCarte(self, index: int):
        return self.cartes.pop(index)

    def nombreCartes(self):
        return len(self.cartes)

    def montrerCarte(self, index: int):
        print(self.cartes[index])
    def addScore(self,valeur: int):
        self.score+=valeur
    def jouer(socket):
        while True:
            msg = socket.recv(1024).decode("utf-8")
            print(msg)

            if "Choisis une carte" in msg:
                carte = input("Ta carte : ")
                socket.sendall(carte.encode("utf-8"))
            
            if "Choisis la meilleure" in msg:
                choix = input("Qui gagne ? ")
                socket.sendall(choix.encode("utf-8"))

