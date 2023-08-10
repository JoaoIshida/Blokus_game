from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import os

class soundPlayer:
    def __init__(self):
        self.media_player = QMediaPlayer()
        self.volume = 60
        self.media_player.setVolume(self.volume)

    def play_sound(self):
        # Get the directory of the script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(script_dir, "assets", "sfx", "legolulw.wav")
        
        url = QUrl.fromLocalFile(absolute_path)
        self.media_player.setMedia(QMediaContent(url))
        self.media_player.play()

    def setVolume(self, volume):
        self.volume = volume
        self.media_player.setVolume(self.volume)