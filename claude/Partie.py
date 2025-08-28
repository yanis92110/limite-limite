from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import json
import threading
import socket
import server
import random
import os

class Partie(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # État du jeu local
        self.main_joueur = []
        self.is_roi = False
        self.score = 0
        self.pseudo = ""
        self.carte_noire_actuelle = None
        self.choix_disponibles = []
        self.en_attente_choix = False
        self.en_attente_roi = False
        self.partie_terminee = False
        
        # Référence vers le client socket
        self.client_socket = None
        self.game_client = None
        
        self.setup_ui()
        
        # Planifier la mise à jour de l'interface
        Clock.schedule_interval(self.update_ui, 0.5)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header avec informations du joueur
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        self.label_joueur = Label(text="Connexion...", font_size=18, bold=True)
        self.label_score = Label(text="Score: 0", font_size=18, bold=True)
        self.label_statut = Label(text="", font_size=16, bold=True)
        
        header_layout.add_widget(self.label_joueur)
        header_layout.add_widget(self.label_score)
        header_layout.add_widget(self.label_statut)
        main_layout.add_widget(header_layout)
        
        # Zone carte noire actuelle
        carte_noire_layout = BoxLayout(orientation='vertical', size_hint_y=0.2)
        titre_carte_noire = Label(text="🃏 CARTE NOIRE (QUESTION)", font_size=16, bold=True)
        self.img_carte_noire = Image(source="img_noires/1.jpg")  # Image par défaut
        carte_noire_layout.add_widget(titre_carte_noire)
        carte_noire_layout.add_widget(self.img_carte_noire)
        main_layout.add_widget(carte_noire_layout)
        
        # Messages et instructions
        self.label_instructions = Label(
            text="🎮 Partie en cours de démarrage...",
            font_size=14,
            size_hint_y=0.1,
            color=(0, 0.7, 1, 1)
        )
        main_layout.add_widget(self.label_instructions)
        
        # Zone principale - cartes de la main
        zone_main_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        titre_main = Label(text="🎴 VOTRE MAIN", font_size=16, bold=True, size_hint_y=0.1)
        zone_main_layout.add_widget(titre_main)
        
        # ScrollView pour les cartes
        scroll_main = ScrollView()
        self.grid_cartes = GridLayout(cols=2, size_hint_y=None, spacing=5, padding=5)
        self.grid_cartes.bind(minimum_height=self.grid_cartes.setter('height'))
        scroll_main.add_widget(self.grid_cartes)
        zone_main_layout.add_widget(scroll_main)
        
        main_layout.add_widget(zone_main_layout)
        
        # Zone pour les choix du roi
        self.zone_choix_roi = BoxLayout(orientation='vertical', size_hint_y=0.15)
        self.zone_choix_roi.add_widget(Label(text=""))  # Espace vide par défaut
        main_layout.add_widget(self.zone_choix_roi)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Appelé quand on entre sur cet écran"""
        print("Entrée dans l'écran Partie")
        if not self.game_client:
            self.connecter_client_existant()
    
    def set_connection_params(self, host, port):
        """Définit les paramètres de connexion pour un serveur distant"""
        self.connection_host = host
        self.connection_port = port
        print(f"Paramètres de connexion définis: {host}:{port}")
    
    def connecter_client_existant(self):
        """Se connecte en tant que client au serveur"""
        try:
            # Créer un nouveau client pour cette interface
            self.game_client = GameClientGUI(self)
            
            # Utiliser les paramètres de connexion personnalisés s'ils existent
            host = getattr(self, 'connection_host', '127.0.0.1')
            port = getattr(self, 'connection_port', 5000)
            
            # Demander le pseudo à l'utilisateur via popup
            self.demander_pseudo(host, port)
            
        except Exception as e:
            print(f"Erreur connexion client: {e}")
            self.label_instructions.text = f"❌ Erreur de connexion: {e}"
    
    def demander_pseudo(self, host='127.0.0.1', port=5000):
        """Popup pour demander le pseudo du joueur"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(
            text=f"🌐 Connexion à {host}:{port}\nEntrez votre pseudo:", 
            size_hint_y=0.4
        ))
        
        self.input_pseudo = TextInput(
            text=f"Joueur_{id(self) % 1000}", 
            size_hint_y=0.3,
            multiline=False
        )
        content.add_widget(self.input_pseudo)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        btn_annuler = Button(text="Retour")
        btn_annuler.bind(on_press=self.annuler_connexion)
        
        btn_ok = Button(text="Rejoindre")
        btn_ok.bind(on_press=lambda x: self.valider_pseudo(host, port))
        
        btn_layout.add_widget(btn_annuler)
        btn_layout.add_widget(btn_ok)
        content.add_widget(btn_layout)
        
        self.popup_pseudo = Popup(
            title="Connexion à la partie",
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        self.popup_pseudo.open()
    
    def valider_pseudo(self, host='127.0.0.1', port=5000):
        """Valide le pseudo et lance la connexion"""
        pseudo = self.input_pseudo.text.strip()
        if pseudo:
            self.popup_pseudo.dismiss()
            self.pseudo = pseudo
            self.label_joueur.text = f"👤 {pseudo}"
            
            # Lancer la connexion avec les paramètres fournis
            threading.Thread(
                target=self.game_client.rejoindre_serveur, 
                args=(pseudo, host, port), 
                daemon=True
            ).start()
        else:
            # Erreur : pseudo vide
            self.input_pseudo.hint_text = "Le pseudo ne peut pas être vide!"
    
    def annuler_connexion(self, instance):
        """Annule la connexion et retourne au menu"""
        self.popup_pseudo.dismiss()
        self.manager.current = "menu"
    
    def update_ui(self, dt):
        """Met à jour l'interface utilisateur"""
        if self.game_client:
            self.label_score.text = f"🏆 Score: {self.game_client.score}"
            
            if self.game_client.is_roi:
                self.label_statut.text = "👑 VOUS ÊTES LE ROI"
                self.label_statut.color = (1, 0.8, 0, 1)  # Doré
            else:
                self.label_statut.text = "🎮 Joueur"
                self.label_statut.color = (1, 1, 1, 1)  # Blanc
            
            # Mettre à jour la carte noire
            if self.game_client.carte_noire_actuelle:
                carte_id = self.game_client.carte_noire_actuelle
                self.img_carte_noire.source = f"img_noires/{carte_id}.jpg"
    
    def afficher_main(self, cartes_ids):
        """Affiche les cartes de la main du joueur sous forme d'images"""
        self.grid_cartes.clear_widgets()
        self.main_joueur = cartes_ids

        if not cartes_ids:
            self.grid_cartes.add_widget(Label(text="Aucune carte", size_hint_y=None, height=40))
            return

        for i, carte_id in enumerate(cartes_ids):
            btn_carte = Button(
                size_hint_y=None,
                height=120,
                background_normal=f"img_blanches/{carte_id}.jpg",
                background_down=f"img_blanches/{carte_id}.jpg",
                text=f"{i}",
                color=(1, 1, 1, 0),  # texte invisible
            )
            btn_carte.bind(on_press=lambda x, idx=i: self.choisir_carte(idx))
            self.grid_cartes.add_widget(btn_carte)
    
    def activer_choix_cartes(self, message="Choisissez une carte à jouer"):
        """Active les boutons de cartes et affiche les instructions"""
        self.label_instructions.text = f"⏳ {message}"
        self.label_instructions.color = (1, 0.5, 0, 1)  # Orange
        
        # Réactiver tous les boutons de cartes
        for widget in self.grid_cartes.children:
            if isinstance(widget, Button):
                widget.disabled = False
                widget.background_color = (0.2, 0.8, 0.2, 1)  # Vert actif
    
    def desactiver_choix_cartes(self, message="Carte jouée! En attente des autres joueurs..."):
        """Désactive les boutons de cartes"""
        self.label_instructions.text = f"✅ {message}"
        self.label_instructions.color = (0, 1, 0, 1)  # Vert
        
        # Désactiver tous les boutons de cartes
        for widget in self.grid_cartes.children:
            if isinstance(widget, Button):
                widget.disabled = True
                widget.background_color = (0.5, 0.5, 0.5, 1)  # Gris
    
    def afficher_choix_roi(self, choix):
        """Affiche les choix disponibles pour le roi (affichage des images de cartes)"""
        self.zone_choix_roi.clear_widgets()

        titre = Label(
            text="👑 EN TANT QUE ROI, CHOISISSEZ LA MEILLEURE CARTE :",
            size_hint_y=0.2,
            font_size=14,
            bold=True,
            color=(1, 0.8, 0, 1)  # Doré
        )
        self.zone_choix_roi.add_widget(titre)

        # ScrollView pour les choix
        scroll_choix = ScrollView(size_hint_y=0.8)
        grid_choix = GridLayout(cols=2, size_hint_y=None, spacing=10, padding=10)
        grid_choix.bind(minimum_height=grid_choix.setter('height'))

        for choice in choix:
            pseudo = choice['pseudo']
            carte_id = choice['carte_id']

            box = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=5)
            img = Image(source=f"img_blanches/{carte_id}.jpg", size_hint_y=0.7)
            btn_choix = Button(
                text=f"🎭 {pseudo}",
                size_hint_y=0.3,
                background_color=(1, 0.8, 0, 1),  # Doré
                color=(0, 0, 0, 1)  # Texte noir
            )
            btn_choix.bind(on_press=lambda x, pseudo=pseudo: self.choisir_gagnant(pseudo))
            box.add_widget(img)
            box.add_widget(btn_choix)
            grid_choix.add_widget(box)

        scroll_choix.add_widget(grid_choix)
        self.zone_choix_roi.add_widget(scroll_choix)

        # Message d'instruction
        self.label_instructions.text = "👑 Vous êtes le roi ! Choisissez la meilleure carte."
        self.label_instructions.color = (1, 0.8, 0, 1)  # Doré
    
    def nettoyer_choix_roi(self):
        """Nettoie la zone des choix du roi"""
        self.zone_choix_roi.clear_widgets()
        self.zone_choix_roi.add_widget(Label(text=""))
    
    def choisir_carte(self, index):
        """Le joueur choisit une carte à jouer"""
        if self.game_client and not self.game_client.is_roi and index < len(self.main_joueur):
            self.game_client.jouer_carte(index)
            self.desactiver_choix_cartes(f"Carte {index} jouée!")
    
    def choisir_gagnant(self, pseudo):
        """Le roi choisit le gagnant"""
        if self.game_client and self.game_client.is_roi:
            self.game_client.choisir_gagnant_gui(pseudo)
            self.nettoyer_choix_roi()
            self.label_instructions.text = f"✅ Vous avez choisi {pseudo} comme gagnant!"
            self.label_instructions.color = (0, 1, 0, 1)  # Vert
    
    def afficher_resultat_manche(self, gagnant, roi):
        """Affiche le résultat d'une manche"""
        self.nettoyer_choix_roi()
        
        if gagnant == self.pseudo:
            self.label_instructions.text = f"🏆 VOUS GAGNEZ CETTE MANCHE! (+1 point)"
            self.label_instructions.color = (0, 1, 0, 1)  # Vert
        else:
            self.label_instructions.text = f"🎭 {gagnant} gagne cette manche (choisi par {roi})"
            self.label_instructions.color = (1, 1, 0, 1)  # Jaune
        
        # Programmer l'affichage pour quelques secondes
        from kivy.clock import Clock

        Clock.schedule_once(
            lambda dt: setattr(self.label_instructions, 'text', "⏳ Préparation de la prochaine manche..."), 
            3.0
        )
    
    def afficher_fin_de_partie(self, gagnant, scores):
        """Affiche les résultats de fin de partie"""
        self.partie_terminee = True
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Titre
        content.add_widget(Label(
            text=f"🏆 PARTIE TERMINÉE!\nGagnant: {gagnant}", 
            font_size=20, 
            bold=True,
            size_hint_y=0.3
        ))
        
        # Scores
        scores_layout = BoxLayout(orientation='vertical', size_hint_y=0.5)
        scores_layout.add_widget(Label(text="📊 Scores finaux:", font_size=16, bold=True))
        
        for score_info in scores:
            pseudo = score_info['pseudo']
            score = score_info['score']
            emoji = "🏆" if pseudo == gagnant else "🎮"
            scores_layout.add_widget(Label(text=f"{emoji} {pseudo}: {score} points"))
        
        content.add_widget(scores_layout)
        
        # Bouton retour au menu
        btn_menu = Button(text="Retour au menu", size_hint_y=0.2)
        btn_menu.bind(on_press=self.retour_menu)
        content.add_widget(btn_menu)
        
        self.popup_fin = Popup(
            title="Fin de partie",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        self.popup_fin.open()
    
    def retour_menu(self, instance):
        """Retour au menu principal"""
        if hasattr(self, 'popup_fin'):
            self.popup_fin.dismiss()
        
        # Nettoyer la connexion
        if self.game_client:
            self.game_client.deconnecter()
            self.game_client = None
        
        # Retour au menu
        self.manager.current = "menu"


class GameClientGUI:
    """Client de jeu intégré à l'interface graphique"""
    def __init__(self, partie_screen):
        self.partie_screen = partie_screen
        self.socket = None
        self.connected = False
        self.pseudo = ""
        self.main = []  # Main sous forme de liste d'IDs de cartes
        self.is_roi = False
        self.score = 0
        self.carte_noire_actuelle = None  # ID de la carte noire actuelle
        self.en_jeu = False
    
    def rejoindre_serveur(self, pseudo, host="127.0.0.1", port=5000):
        """Connexion au serveur avec le pseudo donné"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            self.pseudo = pseudo
            self.socket.send(pseudo.encode('utf-8'))
            
            self.connected = True
            print(f"Client GUI connecté: {pseudo}")
            
            # Mettre à jour l'interface
            Clock.schedule_once(lambda dt: setattr(
                self.partie_screen.label_instructions, 'text', 
                f"✅ Connecté en tant que {pseudo}!"
            ), 0)
            
            # Démarrer l'écoute
            self.ecouter_serveur()
            
        except Exception as e:
            print(f"Erreur connexion GUI: {e}")
            Clock.schedule_once(lambda dt: setattr(
                self.partie_screen.label_instructions, 'text', 
                f"❌ Erreur de connexion: {e}"
            ), 0)
    
    def ecouter_serveur(self):
        """Écoute les messages du serveur"""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    Clock.schedule_once(lambda dt: self.traiter_message(message), 0)
                except json.JSONDecodeError:
                    Clock.schedule_once(lambda dt: print(f"Message serveur: {data}"), 0)
                    
            except Exception as e:
                print(f"Erreur réception GUI: {e}")
                break
        
        self.connected = False
    
    def traiter_message(self, message):
        """Traite les messages du serveur (sur le thread principal Kivy)"""
        action = message.get("action")
        
        if action == "connected":
            self.partie_screen.label_instructions.text = message.get("message", "Connecté!")
            self.partie_screen.label_instructions.color = (0, 1, 0, 1)
            
        elif action == "start_game":
            joueurs = message.get("joueurs", [])
            self.en_jeu = True
            self.partie_screen.label_instructions.text = f"🎮 Partie démarrée avec {len(joueurs)} joueurs!"
            
        elif action == "update_hand":
            self.main = message.get("cartes", [])  # Liste d'IDs de cartes
            self.is_roi = message.get("is_roi", False)
            self.score = message.get("score", 0)
            
            # Mettre à jour l'affichage des cartes
            self.partie_screen.afficher_main(self.main)
            
        elif action == "new_black_card":
            self.carte_noire_actuelle = message.get("carte")  # ID de la carte noire
            roi = message.get("roi")
            manche = message.get("manche")
            
            self.partie_screen.label_instructions.text = f"🎯 Manche {manche} - Roi: {roi}"
            self.partie_screen.label_instructions.color = (0, 0.7, 1, 1)
            
        elif action == "choose_card":
            if not self.is_roi:
                self.partie_screen.activer_choix_cartes("⏳ À vous de jouer! Choisissez une carte.")
                    
        elif action == "choose_winner":
            if self.is_roi:
                choix = message.get("choix", [])
                self.partie_screen.afficher_choix_roi(choix)
                
        elif action == "round_result":
            gagnant = message.get("gagnant")
            roi = message.get("roi")
            self.partie_screen.afficher_resultat_manche(gagnant, roi)
            
        elif action == "game_over":
            gagnant = message.get("gagnant")
            scores = message.get("scores", [])
            self.en_jeu = False
            self.partie_screen.afficher_fin_de_partie(gagnant, scores)
    
    def jouer_carte(self, index):
        """Envoie le choix de carte au serveur"""
        if 0 <= index < len(self.main) and self.connected:
            message = {
                "action": "play_card",
                "carte_index": index
            }
            try:
                self.socket.send(json.dumps(message).encode('utf-8'))
                print(f"Carte {index} jouée: {self.main[index]}")
            except Exception as e:
                print(f"Erreur envoi carte: {e}")
    
    def choisir_gagnant_gui(self, pseudo):
        """Envoie le choix du gagnant au serveur"""
        if self.connected:
            message = {
                "action": "choose_winner",
                "winner_pseudo": pseudo
            }
            try:
                self.socket.send(json.dumps(message).encode('utf-8'))
                print(f"Gagnant choisi: {pseudo}")
            except Exception as e:
                print(f"Erreur choix gagnant: {e}")
    
    def deconnecter(self):
        """Ferme la connexion proprement"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Client GUI déconnecté")