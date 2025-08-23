from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
import client
import server
import threading

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        button = Button(text="Créer partie")
        button2 = Button(text="Rejoindre partie")
        button.bind(on_press=self.creer_partie)
        button2.bind(on_press=self.rejoindre_partie)
        layout.add_widget(button)
        layout.add_widget(button2)
        self.add_widget(layout)


    def creer_partie(self,instance):
    # création du socket
        self.manager.current = "lobby"
        threading.Thread(target=server.creer_serveur, daemon=True).start()
        threading.Thread(target=client.rejoindre_serveur, daemon=True).start()
    

    def rejoindre_partie(self,instance):
        threading.Thread(target=client.rejoindre_serveur, daemon=True).start()

