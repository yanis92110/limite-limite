from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import server

class WaitingLobby(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(lambda dt: self.refresh_players(), 1)
        self.layout = BoxLayout(orientation="vertical")
        
        # Titre
        title = Label(text="Salon d'attente", font_size=24)
        self.layout.add_widget(title)
        
        # Bouton pour lancer la partie
        self.btn = Button(text="Lancer la partie", size_hint_y=0.2)
        self.btn.bind(on_press=self.go_partie)
        self.layout.add_widget(self.btn)
        
        # Zone d'affichage des joueurs
        self.players_box = BoxLayout(orientation="vertical")
        self.layout.add_widget(self.players_box)
        
        self.add_widget(self.layout)
        self.refresh_players()

    def refresh_players(self):
        """Met à jour la liste des joueurs connectés"""
        self.players_box.clear_widgets()
        
        # Titre de la section joueurs
        players_title = Label(text="Joueurs connectés:", font_size=18)
        self.players_box.add_widget(players_title)
        
        # Liste des joueurs
        joueurs = server.get_clients_addr()
        if joueurs:
            for i, pseudo in enumerate(joueurs):
                player_label = Label(text=f"{i+1}. {pseudo}")
                self.players_box.add_widget(player_label)
        else:
            no_players = Label(text="Aucun joueur connecté")
            self.players_box.add_widget(no_players)
        
        # Mettre à jour l'état du bouton
        nb_joueurs = len(joueurs)
        if nb_joueurs >= 1:
            self.btn.text = f"Lancer la partie ({nb_joueurs} joueurs)"
            self.btn.disabled = False
        else:
            self.btn.text = f"En attente de joueurs ({nb_joueurs}/2 minimum)"
            self.btn.disabled = True
        
    def go_partie(self, instance):
        """Lance la partie côté serveur et change d'écran"""
        joueurs = server.get_clients_addr()
        if len(joueurs) >= 2:
            print(f"Lancement de la partie avec {len(joueurs)} joueurs")
            
            # Lancer la logique de jeu côté serveur
            server.lancer_partie()
            
            # Changer d'écran pour tous les clients
            self.manager.current = "partie"
        else:
            print("Pas assez de joueurs pour lancer la partie!")