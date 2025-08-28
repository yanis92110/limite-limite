#!/usr/bin/env python3
"""
Client console simple pour tester le jeu sans interface graphique
"""

import socket
import json
import threading
import sys

class ClientConsole:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.pseudo = ""
        self.main = []
        self.is_roi = False
        self.score = 0
        self.carte_noire_actuelle = None
        self.en_attente_choix = False
        
    def connecter(self, host="127.0.0.1", port=5000):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Demander le pseudo
            self.pseudo = input("Entrez votre pseudo: ").strip() or f"TestClient_{id(self)%1000}"
            self.socket.send(self.pseudo.encode('utf-8'))
            
            self.connected = True
            print(f"✅ Connecté en tant que {self.pseudo}")
            
            # Démarrer l'écoute
            threading.Thread(target=self.ecouter_serveur, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def ecouter_serveur(self):
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    self.traiter_message(message)
                except json.JSONDecodeError:
                    print(f"📨 Message serveur: {data}")
                    
            except Exception as e:
                print(f"❌ Erreur réception: {e}")
                break
        
        self.connected = False
        print("🔌 Déconnecté du serveur")
    
    def traiter_message(self, message):
        action = message.get("action")
        
        if action == "connected":
            print(f"🎮 {message.get('message', 'Connecté!')}")
            
        elif action == "start_game":
            joueurs = message.get("joueurs", [])
            print(f"\n🚀 PARTIE DÉMARRÉE avec {len(joueurs)} joueurs!")
            print(f"Joueurs: {', '.join(joueurs)}")
            
        elif action == "update_hand":
            self.main = message.get("cartes", [])
            self.is_roi = message.get("is_roi", False)
            self.score = message.get("score", 0)
            self.afficher_main()
            
        elif action == "new_black_card":
            self.carte_noire_actuelle = message.get("carte")
            roi = message.get("roi")
            manche = message.get("manche")
            
            print(f"\n{'='*60}")
            print(f"🎯 MANCHE {manche}")
            print(f"👑 Roi: {roi}")
            print(f"🃏 Carte noire: {self.carte_noire_actuelle['lien']}")
            print('='*60)
            
        elif action == "choose_card":
            if not self.is_roi:
                print(f"\n⏰ À VOUS DE JOUER!")
                self.demander_choix_carte()
                
        elif action == "choose_winner":
            if self.is_roi:
                choix = message.get("choix", [])
                self.demander_choix_gagnant(choix)
                
        elif action == "round_result":
            gagnant = message.get("gagnant")
            roi = message.get("roi")
            print(f"\n🏆 {gagnant} gagne cette manche! (choix de {roi})")
            
        elif action == "game_over":
            gagnant = message.get("gagnant")
            scores = message.get("scores", [])
            print(f"\n🏆 PARTIE TERMINÉE!")
            print(f"Gagnant: {gagnant}")
            print("\n📊 Scores finaux:")
            for score_info in scores:
                emoji = "🏆" if score_info['pseudo'] == gagnant else "🎮"
                print(f"  {emoji} {score_info['pseudo']}: {score_info['score']} points")
            
            self.connected = False
    
    def afficher_main(self):
        print(f"\n{'='*50}")
        print(f"👤 {self.pseudo} - 🏆 Score: {self.score}")
        if self.is_roi:
            print("👑 VOUS ÊTES LE ROI")
        print(f"🎴 Vos cartes:")
        for i, carte in enumerate(self.main):
            print(f"  [{i}] {carte['lien']}")
        print('='*50)
    
    def demander_choix_carte(self):
        print(f"\n📋 Carte noire: {self.carte_noire_actuelle['lien']}")
        print("Choisissez une carte à jouer (0-7):")
        
        try:
            choix = input("Votre choix: ").strip()
            index = int(choix)
            
            if 0 <= index < len(self.main):
                self.envoyer_carte(index)
                print(f"✅ Carte {index} envoyée!")
            else:
                print("❌ Index invalide!")
                self.demander_choix_carte()
                
        except (ValueError, KeyboardInterrupt):
            print("❌ Choix invalide!")
            self.demander_choix_carte()
    
    def demander_choix_gagnant(self, choix):
        print(f"\n👑 VOUS ÊTES LE ROI!")
        print(f"📋 Carte noire: {self.carte_noire_actuelle['lien']}")
        print(f"🎯 Choisissez la meilleure combinaison:")
        
        for i, choice in enumerate(choix):
            print(f"  [{i+1}] {choice['pseudo']}: {choice['carte']['lien']}")
        
        try:
            choix_input = input("\nTapez le nom du joueur gagnant: ").strip()
            pseudos_valides = [choice['pseudo'] for choice in choix]
            
            if choix_input in pseudos_valides:
                self.envoyer_choix_gagnant(choix_input)
                print(f"✅ Vous avez choisi: {choix_input}")
            else:
                print(f"❌ Pseudo invalide! Choisissez parmi: {', '.join(pseudos_valides)}")
                self.demander_choix_gagnant(choix)
                
        except KeyboardInterrupt:
            print("\n👋 Abandon...")
            self.deconnecter()
    
    def envoyer_carte(self, index):
        message = {
            "action": "play_card",
            "carte_index": index
        }
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"❌ Erreur envoi carte: {e}")
    
    def envoyer_choix_gagnant(self, pseudo):
        message = {
            "action": "choose_winner",
            "winner_pseudo": pseudo
        }
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"❌ Erreur envoi choix: {e}")
    
    def deconnecter(self):
        self.connected = False
        if self.socket:
            self.socket.close()
        print("👋 Déconnexion...")

def main():
    client = ClientConsole()
    
    print("🃏 Client de test Cards Against Humanity")
    print("Connexion au serveur...")
    
    # Paramètres de connexion
    host = input("Adresse du serveur (Enter = localhost): ").strip() or "127.0.0.1"
    try:
        port = int(input("Port (Enter = 5000): ").strip() or "5000")
    except ValueError:
        port = 5000
    
    if client.connecter(host, port):
        try:
            # Garder le client en vie
            while client.connected:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Arrêt du client...")
            client.deconnecter()
    
    print("🔚 Fin du client console")

if __name__ == "__main__":
    main()