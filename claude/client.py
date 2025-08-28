import socket
import json
import threading

class GameClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.pseudo = ""
        self.main = []
        self.is_roi = False
        self.score = 0
        self.carte_noire_actuelle = None
        self.en_jeu = False
        
    def rejoindre_serveur(self, host="127.0.0.1", port=5000):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Demander le pseudo
            self.pseudo = input("\nEntrer un Pseudo: ")
            self.socket.send(self.pseudo.encode('utf-8'))
            
            # Démarrer le thread d'écoute
            threading.Thread(target=self.ecouter_serveur, daemon=True).start()
            
            self.connected = True
            print(f"Connecté au serveur en tant que {self.pseudo}")
            
            # Boucle principale du client
            self.boucle_principale()
            
        except Exception as e:
            print(f"Erreur de connexion: {e}")
    
    def ecouter_serveur(self):
        """Thread qui écoute les messages du serveur"""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    self.traiter_message(message)
                except json.JSONDecodeError:
                    print(f"Message du serveur: {data}")
                    
            except Exception as e:
                print(f"Erreur réception: {e}")
                break
        
        self.connected = False
    
    def traiter_message(self, message):
        """Traite les messages structurés du serveur"""
        action = message.get("action")
        
        if action == "connected":
            print(message.get("message", "Connecté!"))
            
        elif action == "start_game":
            print("\n🎮 LA PARTIE COMMENCE!")
            joueurs = message.get("joueurs", [])
            print(f"Joueurs: {', '.join(joueurs)}")
            self.en_jeu = True
            
        elif action == "update_hand":
            self.main = message.get("cartes", [])
            self.is_roi = message.get("is_roi", False)
            self.score = message.get("score", 0)
            self.afficher_main()
            
        elif action == "new_black_card":
            self.carte_noire_actuelle = message.get("carte")
            roi = message.get("roi")
            manche = message.get("manche")
            print(f"\n🃏 MANCHE {manche}")
            print(f"👑 Roi: {roi}")
            print(f"📋 Carte noire: {self.carte_noire_actuelle['lien']}")
            
        elif action == "choose_card":
            if not self.is_roi:
                self.choisir_carte()
                
        elif action == "choose_winner":
            if self.is_roi:
                self.choisir_gagnant(message.get("choix", []))
                
        elif action == "game_over":
            gagnant = message.get("gagnant")
            scores = message.get("scores", [])
            print(f"\n🏆 FIN DE PARTIE!")
            print(f"Gagnant: {gagnant}")
            print("\nScores finaux:")
            for score_info in scores:
                print(f"  {score_info['pseudo']}: {score_info['score']} points")
            self.en_jeu = False
    
    def afficher_main(self):
        """Affiche la main du joueur"""
        print(f"\n{'='*40}")
        print(f"🎯 {self.pseudo} - Score: {self.score}")
        if self.is_roi:
            print("👑 VOUS ÊTES LE ROI")
        print(f"🃏 Vos cartes:")
        for i, carte in enumerate(self.main):
            print(f"  [{i}] {carte['lien']}")
        print("="*40)
    
    def choisir_carte(self):
        """Permet au joueur de choisir une carte à jouer"""
        print(f"\n⏰ Choisissez une carte à jouer contre:")
        print(f"📋 {self.carte_noire_actuelle['lien']}")
        print("Tapez le numéro de la carte (0-7):")
        
        try:
            choix = input("Votre choix: ").strip()
            index = int(choix)
            
            if 0 <= index < len(self.main):
                # Envoyer le choix au serveur
                message = {
                    "action": "play_card",
                    "carte_index": index
                }
                self.socket.send(json.dumps(message).encode('utf-8'))
                print(f"✅ Carte {index} jouée: {self.main[index]['lien']}")
            else:
                print("❌ Index invalide!")
                self.choisir_carte()  # Redemander
                
        except ValueError:
            print("❌ Veuillez entrer un nombre!")
            self.choisir_carte()  # Redemander
    
    def choisir_gagnant(self, choix):
        """Le roi choisit le gagnant parmi les cartes jouées"""
        print(f"\n👑 VOUS ÊTES LE ROI!")
        print(f"📋 Carte noire: {self.carte_noire_actuelle['lien']}")
        print(f"\n🎯 Choisissez la meilleure combinaison:")
        
        for i, choice in enumerate(choix):
            print(f"  [{i+1}] {choice['pseudo']}: {choice['carte']['lien']}")
        
        print("\nTapez le nom du joueur gagnant:")
        try:
            gagnant = input("Votre choix: ").strip()
            
            # Vérifier que le choix est valide
            pseudos_valides = [choice['pseudo'] for choice in choix]
            if gagnant in pseudos_valides:
                message = {
                    "action": "choose_winner", 
                    "winner_pseudo": gagnant
                }
                self.socket.send(json.dumps(message).encode('utf-8'))
                print(f"✅ Vous avez choisi: {gagnant}")
            else:
                print(f"❌ Pseudo invalide! Choisissez parmi: {', '.join(pseudos_valides)}")
                self.choisir_gagnant(choix)  # Redemander
                
        except Exception as e:
            print(f"Erreur: {e}")
            self.choisir_gagnant(choix)
    
    def boucle_principale(self):
        """Boucle principale d'interaction avec l'utilisateur"""
        print("\n📢 En attente du lancement de la partie...")
        print("Commandes disponibles:")
        print("  'main' - Afficher votre main")
        print("  'score' - Afficher votre score")
        print("  'quit' - Quitter")
        
        while self.connected:
            try:
                cmd = input().strip().lower()
                
                if cmd == "quit":
                    break
                elif cmd == "main":
                    self.afficher_main()
                elif cmd == "score":
                    print(f"Score de {self.pseudo}: {self.score}")
                elif cmd == "help":
                    print("Commandes: 'main', 'score', 'quit'")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        self.deconnecter()
    
    def deconnecter(self):
        """Ferme la connexion proprement"""
        self.connected = False
        if self.socket:
            self.socket.close()
        print("Déconnecté du serveur.")

# Fonction principale pour lancer le client
def rejoindre_serveur():
    client = GameClient()
    client.rejoindre_serveur()

if __name__ == "__main__":
    rejoindre_serveur()