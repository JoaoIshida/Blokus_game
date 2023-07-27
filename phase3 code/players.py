from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Player:
    def __init__(self, score_label, is_ai=False, is_turn=False, name="Player"):
        self.score_label = score_label
        self.pieces = []
        self.is_ai = is_ai
        self.is_turn = is_turn
        self.name = name
        self.first_move = True

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

class PlayerPanel(QLabel):
    def __init__(self, colour):
        super().__init__()
        self.setText("0")
        self.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.setStyleSheet(
            f"font-size: 24px; padding: 10px; color: black; background-color: {colour};")
