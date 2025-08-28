from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from MainMenu import MainMenu
from WaitingLobby import WaitingLobby
from Partie import Partie

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Créer les écrans
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(WaitingLobby(name="lobby"))
        sm.add_widget(Partie(name="partie"))
        
        return sm

if __name__ == "__main__":
    MyApp().run()