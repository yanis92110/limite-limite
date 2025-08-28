from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
import client
import server
import threading
import Jeu
from Jeu import Jeu


class Partie(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cartes = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        self.add_widget(cartes)
