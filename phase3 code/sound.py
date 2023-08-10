from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class soundPlayer:
    def __init__(self):
        self.media_player = QMediaPlayer()
        self.volume = 60
        self.media_player.setVolume(self.volume)

    def play_sound(self):
        content = QMediaContent(QUrl.fromLocalFile("assets/sfx/legolulw.wav"))
        self.media_player.setMedia(content)
        self.media_player.play()

    def setVolume(self, volume):
        self.volume = volume
        self.media_player.setVolume(self.volume)

