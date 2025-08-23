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
        Clock.schedule_interval(lambda dt:self.refresh_players(),1)
        self.layout = BoxLayout(orientation="vertical")
        self.btn = Button(text="Lancer la partie")
        self.btn.bind(on_press=self.go_partie)
        self.layout.add_widget(self.btn)

        self.players_box = BoxLayout(orientation="vertical")
        self.layout.add_widget(self.players_box)
        self.add_widget(self.layout)
        self.refresh_players()

    def refresh_players(self):
        self.players_box.clear_widgets()
        for addr in server.get_clients_addr():
            self.players_box.add_widget(Label(text=str(addr)))
        # Tu peux appeler cette méthode régulièrement avec Clock si tu veux du live
    def go_partie(self, instance):
        for addr in server.get_clients_addr():
            self.manager.current = "partie"