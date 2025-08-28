from Carte import Carte
from Paquet import Paquet
from Joueur import Joueur
from time import sleep
from random import choice
import json
import threading

class Jeu():
    """Instance de jeu"""
    def __init__(self, clients_sockets, pseudos_dict):
        """Constructeur qui prend les sockets clients et leurs pseudos"""
        self.cartesNoires = Paquet(True, "noires")  # Cartes noires (questions)
        self.cartesBlanches = Paquet(True, "blanches")  # Cartes blanches (réponses)
        self.defausse = Paquet(False)
        self.continuer = True
        
        # Créer les joueurs avec leurs sockets
        self.joueurs = []
        for socket_client in clients_sockets:
            pseudo = pseudos_dict.get(socket_client, f"Joueur{len(self.joueurs)+1}")
            joueur = Joueur(self.cartesBlanches, pseudo, socket_client)
            self.joueurs.append(joueur)
        
        self.roi = choice(self.joueurs)
        self.roi.setRoi(True)
        self.choix = {}  # Dictionnaire pseudo -> carte choisie
        self.manche = 1
        
        print(f"Jeu initialisé avec {len(self.joueurs)} joueurs")
        self.envoyer_mains_initiales()
    
    def envoyer_mains_initiales(self):
        """Envoie à chaque joueur sa main de départ"""
        for joueur in self.joueurs:
            cartes_data = []
            for i, carte in enumerate(joueur.cartes):
                cartes_data.append({
                    "index": i,
                    "couleur": carte.getCouleur(),
                    "lien": carte.getLien()
                })
            
            message = {
                "action": "update_hand",
                "cartes": cartes_data,
                "is_roi": joueur.estRoi,
                "score": joueur.score
            }
            
            try:
                joueur.socket.send(json.dumps(message).encode('utf-8'))
            except:
                print(f"Erreur envoi main à {joueur.pseudo}")

    def pioche_blanche(self, joueur):
        if self.cartesBlanches.est_vide():
            self.cartesBlanches, self.defausse = self.defausse, self.cartesBlanches
            self.cartesBlanches.battre()
        if not self.cartesBlanches.est_vide():
            joueur.ajouterCarte(self.cartesBlanches.pop_carte())

    def jouer(self):
        """Boucle principale du jeu"""
        print(f"=== Début de la partie ===")
        print(f"Le roi initial est {self.roi.pseudo}")
        
        while self.continuer and len(self.joueurs) > 1:
            self.jouer_manche()
            self.manche += 1
            
            # Vérifier condition de fin (par exemple, premier à 5 points)
            for joueur in self.joueurs:
                if joueur.score >= 5:
                    self.fin_de_partie(joueur)
                    return
    
    def jouer_manche(self):
        """Joue une manche complète"""
        print(f"\n=== Manche {self.manche} ===")
        
        # 1. Piocher une carte noire
        if self.cartesNoires.est_vide():
            print("Plus de cartes noires ! Fin de partie.")
            self.continuer = False
            return
            
        carte_noire = self.cartesNoires.pop_carte()
        print(f"Carte noire: {carte_noire.getLien()}")
        
        # 2. Diffuser la carte noire à tous les joueurs
        self.diffuser_carte_noire(carte_noire)
        
        # 3. Demander aux joueurs (sauf roi) de choisir une carte
        self.demander_cartes_joueurs()
        
        # 4. Le roi choisit la meilleure combinaison
        gagnant = self.roi_choisit_gagnant()
        
        # 5. Attribuer le point et changer de roi
        if gagnant:
            gagnant.addScore(1)
            print(f"{gagnant.pseudo} gagne cette manche! Score: {gagnant.score}")
            
            # Le gagnant devient le nouveau roi
            self.roi.setRoi(False)
            gagnant.setRoi(True)
            self.roi = gagnant
        
        # 6. Tous les joueurs piochent une carte pour revenir à 8
        for joueur in self.joueurs:
            while joueur.nombreCartes() < 8:
                self.pioche_blanche(joueur)
        
        # 7. Mettre à jour les mains de tous les joueurs
        self.envoyer_mains_initiales()
        
        sleep(2)  # Petite pause entre les manches

    def diffuser_carte_noire(self, carte_noire):
        """Diffuse la carte noire à tous les joueurs"""
        message = {
            "action": "new_black_card",
            "carte": {
                "lien": carte_noire.getLien(),
                "couleur": carte_noire.getCouleur()
            },
            "roi": self.roi.pseudo,
            "manche": self.manche
        }
        
        for joueur in self.joueurs:
            try:
                joueur.socket.send(json.dumps(message).encode('utf-8'))
            except:
                print(f"Erreur envoi carte noire à {joueur.pseudo}")

    def demander_cartes_joueurs(self):
        """Demande à chaque joueur (sauf roi) de choisir une carte"""
        self.choix.clear()
        
        # Envoyer la demande à tous les non-rois
        for joueur in self.joueurs:
            if not joueur.estRoi:
                message = {
                    "action": "choose_card",
                    "message": "Choisissez une carte à jouer (index 0-7)"
                }
                try:
                    joueur.socket.send(json.dumps(message).encode('utf-8'))
                except:
                    print(f"Erreur demande carte à {joueur.pseudo}")
        
        # Attendre toutes les réponses
        print("En attente des choix des joueurs...")
        timeout = 30  # 30 secondes max
        elapsed = 0
        
        while len(self.choix) < len([j for j in self.joueurs if not j.estRoi]) and elapsed < timeout:
            sleep(1)
            elapsed += 1
        
        print(f"Choix reçus: {len(self.choix)} / {len([j for j in self.joueurs if not j.estRoi])}")

    def recevoir_carte_jouee(self, socket_joueur, carte_index):
        """Traite la carte jouée par un joueur"""
        joueur = next((j for j in self.joueurs if j.socket == socket_joueur), None)
        
        if joueur and not joueur.estRoi and joueur.pseudo not in self.choix:
            try:
                carte_index = int(carte_index)
                if 0 <= carte_index < joueur.nombreCartes():
                    carte_jouee = joueur.retirerCarte(carte_index)
                    self.choix[joueur.pseudo] = carte_jouee
                    print(f"{joueur.pseudo} a joué la carte {carte_index}")
            except (ValueError, IndexError):
                print(f"Index de carte invalide de {joueur.pseudo}: {carte_index}")

    def roi_choisit_gagnant(self):
        """Le roi choisit la meilleure combinaison"""
        if not self.choix:
            print("Aucune carte jouée!")
            return None
        
        # Envoyer les choix au roi
        choix_data = []
        for pseudo, carte in self.choix.items():
            choix_data.append({
                "pseudo": pseudo,
                "carte": {
                    "lien": carte.getLien(),
                    "couleur": carte.getCouleur()
                }
            })
        
        message = {
            "action": "choose_winner",
            "choix": choix_data,
            "message": "Choisissez le gagnant"
        }
        
        try:
            self.roi.socket.send(json.dumps(message).encode('utf-8'))
        except:
            print(f"Erreur envoi choix au roi {self.roi.pseudo}")
            return None
        
        # Attendre la réponse du roi
        print(f"En attente du choix du roi {self.roi.pseudo}...")
        timeout = 60  # 60 secondes pour le roi
        elapsed = 0
        
        self.gagnant_choisi = None
        
        while not self.gagnant_choisi and elapsed < timeout:
            sleep(1)
            elapsed += 1
        
        # Si pas de réponse, choisir aléatoirement
        if not self.gagnant_choisi:
            gagnant_pseudo = choice(list(self.choix.keys()))
            print(f"Timeout! Choix aléatoire: {gagnant_pseudo}")
        else:
            gagnant_pseudo = self.gagnant_choisi
        
        return next((j for j in self.joueurs if j.pseudo == gagnant_pseudo), None)

    def recevoir_choix_roi(self, socket_roi, pseudo_gagnant):
        """Traite le choix du roi"""
        if socket_roi == self.roi.socket and pseudo_gagnant in self.choix:
            self.gagnant_choisi = pseudo_gagnant
            print(f"Le roi a choisi: {pseudo_gagnant}")
            
            # Diffuser le résultat à tous les joueurs
            message = {
                "action": "round_result",
                "gagnant": pseudo_gagnant,
                "roi": self.roi.pseudo
            }
            for joueur in self.joueurs:
                try:
                    joueur.socket.send(json.dumps(message).encode('utf-8'))
                except:
                    pass

    def fin_de_partie(self, gagnant):
        """Termine la partie"""
        print(f"\n=== FIN DE PARTIE ===")
        print(f"🏆 {gagnant.pseudo} remporte la partie avec {gagnant.score} points!")
        
        # Diffuser les résultats finaux
        scores = []
        for joueur in self.joueurs:
            scores.append({
                "pseudo": joueur.pseudo,
                "score": joueur.score
            })
        
        message = {
            "action": "game_over",
            "gagnant": gagnant.pseudo,
            "scores": scores
        }
        
        for joueur in self.joueurs:
            try:
                joueur.socket.send(json.dumps(message).encode('utf-8'))
            except:
                pass
        
        self.continuer = False