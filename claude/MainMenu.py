from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import server
import threading

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=50, spacing=30)

        # Titre du jeu
        titre = Label(
            text="🃏 CARDS AGAINST HUMANITY 🃏", 
            font_size=28, 
            bold=True, 
            size_hint_y=0.3,
            color=(1, 0.8, 0, 1)  # Couleur dorée
        )
        main_layout.add_widget(titre)

        # Boutons du menu
        buttons_layout = BoxLayout(orientation='vertical', spacing=20, size_hint_y=0.7)

        # Bouton créer partie
        btn_creer = Button(
            text="🏠 Créer une partie", 
            font_size=20, 
            size_hint_y=0.5,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        btn_creer.bind(on_press=self.creer_partie)

        # Bouton rejoindre partie
        btn_rejoindre = Button(
            text="🔗 Rejoindre une partie", 
            font_size=20, 
            size_hint_y=0.5,
            background_color=(0.2, 0.6, 1, 1)
        )
        btn_rejoindre.bind(on_press=self.rejoindre_partie)

        buttons_layout.add_widget(btn_creer)
        buttons_layout.add_widget(btn_rejoindre)
        main_layout.add_widget(buttons_layout)

        # Instructions
        instructions = Label(
            text="Créez une partie pour être l'hôte\nou rejoignez une partie existante",
            font_size=14,
            size_hint_y=0.2,
            color=(0.8, 0.8, 0.8, 1)
        )
        main_layout.add_widget(instructions)

        self.add_widget(main_layout)

    def creer_partie(self, instance):
        """Crée une partie et lance le serveur"""
        try:
            print("🏠 Création d'une partie...")
            
            # Lancer le serveur dans un thread séparé
            threading.Thread(target=server.creer_serveur, daemon=True).start()
            
            # Attendre un peu que le serveur se lance
            from kivy.clock import Clock
            Clock.schedule_once(self.aller_au_lobby, 1.0)
            
            # Feedback visuel
            instance.text = "⏳ Création en cours..."
            instance.disabled = True
            
        except Exception as e:
            print(f"Erreur création partie: {e}")
            self.afficher_erreur(f"Erreur lors de la création: {e}")

    def aller_au_lobby(self, dt):
        """Va au lobby après création du serveur"""
        print("📋 Passage au lobby...")
        self.manager.current = "lobby"

    def rejoindre_partie(self, instance):
        """Affiche une popup pour rejoindre une partie"""
        self.demander_adresse_serveur()

    def demander_adresse_serveur(self):
        """Popup pour demander l'adresse du serveur"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        content.add_widget(Label(text="🌐 Adresse du serveur:", size_hint_y=0.2))
        
        self.input_host = TextInput(
            text="127.0.0.1",
            size_hint_y=0.3,
            multiline=False,
            hint_text="Adresse IP du serveur"
        )
        content.add_widget(self.input_host)
        
        content.add_widget(Label(text="🔌 Port:", size_hint_y=0.2))
        
        self.input_port = TextInput(
            text="5000",
            size_hint_y=0.3,
            multiline=False,
            input_filter='int',
            hint_text="Port du serveur"
        )
        content.add_widget(self.input_port)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        btn_annuler = Button(text="Annuler")
        btn_annuler.bind(on_press=self.fermer_popup_serveur)
        
        btn_connecter = Button(text="Se connecter")
        btn_connecter.bind(on_press=self.connecter_serveur_distant)
        
        btn_layout.add_widget(btn_annuler)
        btn_layout.add_widget(btn_connecter)
        content.add_widget(btn_layout)
        
        self.popup_serveur = Popup(
            title="Connexion à un serveur",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        self.popup_serveur.open()

    def fermer_popup_serveur(self, instance):
        """Ferme la popup de serveur"""
        self.popup_serveur.dismiss()

    def connecter_serveur_distant(self, instance):
        """Se connecte à un serveur distant"""
        try:
            host = self.input_host.text.strip() or "127.0.0.1"
            port = int(self.input_port.text.strip() or "5000")
            
            self.popup_serveur.dismiss()
            
            print(f"🔗 Connexion à {host}:{port}...")
            
            # Aller directement à la partie avec ces paramètres
            self.manager.current = "partie"
            
            # Passer les paramètres de connexion à l'écran Partie
            partie_screen = self.manager.get_screen("partie")
            if hasattr(partie_screen, 'set_connection_params'):
                partie_screen.set_connection_params(host, port)
            
        except ValueError:
            self.afficher_erreur("Port invalide! Utilisez un nombre.")
        except Exception as e:
            self.afficher_erreur(f"Erreur de connexion: {e}")

    def afficher_erreur(self, message):
        """Affiche une popup d'erreur"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        content.add_widget(Label(text="❌ Erreur", font_size=18, size_hint_y=0.3))
        content.add_widget(Label(text=message, size_hint_y=0.4))
        
        btn_ok = Button(text="OK", size_hint_y=0.3)
        content.add_widget(btn_ok)
        
        popup_erreur = Popup(
            title="Erreur",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False
        )
        
        btn_ok.bind(on_press=popup_erreur.dismiss)
        popup_erreur.open()