from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

def goldman(size=12):
    # Load the font from the font file
    font_id = QFontDatabase.addApplicationFont("assets/Goldman-Regular.ttf") 

    # Get the font family name if the font was loaded successfully
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        goldman_font_family = font_families[0]
    else:
        goldman_font_family = "Arial"

    goldman_font = QFont(goldman_font_family, size)

    return goldman_font
    
class Player:
    def __init__(self, score_label, is_ai=False, is_turn=False, name="Player", color='red', num="player0"):
        self.score_label = score_label
        self.pieces = []
        self.is_ai = is_ai
        self.is_turn = is_turn
        self.name = name
        self.first_move = True
        self.color = color
        self.num=num

    # I have to do this since I cannot pickle PyQt objects
    def __getstate__(self):
        d = self.__dict__
        self_dict = {'score': d['score_label'].text(), 'is_ai':d['is_ai'], 'is_turn':d['is_turn'], 'name':d['name'], 'first_move':d['first_move']}
        return self_dict

    def __setstate__(self, state):
        self.__dict__ = state

class Turn:
    def __init__(self, turn):
        self.turn = turn

    def __getstate__(self):
        d = self.__dict__
        self_dict = {'turnText': d['turn'].text()}
        return self_dict

    def __setstate__(self, state):
        self.__dict__ = state

class ScorePanel(QWidget):
    def __init__(self, player_name):
        super().__init__()
        self.player_name = player_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)  # Use QHBoxLayout to arrange label and score_label side by side
        self.label = QLabel(f"{self.player_name} Score =", self)
        self.score_label = QLabel("0", self)
        self.score_label.setStyleSheet("font-weight:bold; font-size: 20px;")
        self.label.setFixedWidth(170)

        self.score_label.setContentsMargins(0,0,0,0)
        self.label.setContentsMargins(0,0,0,0)

        layout.addWidget(self.label)
        layout.addWidget(self.score_label)
        self.label.setStyleSheet("font-weight:bold; font-size: 20px")
        self.label.setFont(goldman(12))
