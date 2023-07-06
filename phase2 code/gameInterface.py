import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import pieces
import players
import board

def on_exit_clicked():
    QApplication.quit()

def next_player_clicked(players, turn):
    for i in range(len(players)):
        if players[i].is_turn:
            players[i].is_turn = False
            if i+1 >= len(players):
                players[0].is_turn = True
                turn.turn.setText(players[0].name)
            else:
                players[i+1].is_turn = True
                turn.turn.setText(players[i+1].name)
            break

def confirm_placement(pieces):
    for piece in pieces:
        if piece.new_position is not None:
            # Update the score count
            piece.score_label.setText(str(int(piece.score_label.text()) + piece.weight))
            # Mark the piece as on the board
            piece.onboard = True
            # Confirm the new position
            piece.last_confirmed_position = piece.new_position
            piece.new_position = None

class gameInterface(QWidget):
    def __init__(self):
        super().__init__()
        pieceList = []
        playerList = []
        self.setWindowTitle("Game")
        self.setGeometry(100, 50, 900, 900)
        self.setStyleSheet("background-color: rgb(139, 69, 19);")

        layout = QVBoxLayout(self)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(on_exit_clicked)

        pass_button = QPushButton('Pass', self)
        pass_button.clicked.connect(lambda: next_player_clicked(playerList, turn))

        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(lambda: confirm_placement(pieceList))
        confirm_button.clicked.connect(lambda: next_player_clicked(playerList, turn))
        layout.addWidget(confirm_button)

        boardLayout = board.Board()
        boardLayout.setFixedSize(560, 560)
        boardLayout.setStyleSheet("background-color: rgb(255, 255, 255);")


        layout.addWidget(exit_button)
        layout.addWidget(pass_button)
        layout.addWidget(boardLayout)
        playerPanel1 = players.PlayerPanel("red")
        playerPanel2 = players.PlayerPanel("green")
        playerPanel3 = players.PlayerPanel("blue")
        playerPanel4 = players.PlayerPanel("yellow")
        # Player 1 - RED
        layout.addWidget(playerPanel1)
        player1 = players.Player(playerPanel1, is_turn = True, name = "Player 1")

        # Player 2 - GREEN
        layout.addWidget(playerPanel2)
        player2 = players.Player(playerPanel2, is_ai=True, name = "AI")

        # Player 3 - BLUE
        layout.addWidget(playerPanel3)
        player3 = players.Player(playerPanel3, name = "Player 3")

        # Player 4 - YELLOW
        layout.addWidget(playerPanel4)
        player4 = players.Player(playerPanel4, name = "Player 4")

        playerList.append(player1)
        playerList.append(player2)
        playerList.append(player3)
        playerList.append(player4)
        
        # Show whose turn is it
        player_text = QLabel("Player 1", self)
        turn = players.Turn(player_text)
        layout.addWidget(player_text)


        # Player 1's Pieces - RED
        initial_position1 = QPoint(200, playerPanel1.height() + 250)
        image_label1 = pieces.Piece(self, player1.score_label, 'assets/X5.png', initial_position1, 5, boardLayout, pieceList)
        pieceList.append(image_label1)

        # Player 2's Pieces - GREEN
        initial_position2 = QPoint(200, playerPanel2.height() + 150)
        image_label2 = pieces.Piece(self, player2.score_label, 'assets/L5.png', initial_position2, 5, boardLayout, pieceList)
        pieceList.append(image_label2)

        # Player 3's Pieces - BLUE
        initial_position3 = QPoint(50, playerPanel3.height() + 150)
        image_label3 = pieces.Piece(self, player3.score_label, 'assets/Z5.png', initial_position3, 2, boardLayout, pieceList)
        pieceList.append(image_label3)

        # Player 4's Pieces -YELLOW
        initial_position4 = QPoint(350, playerPanel4.height() + 250)
        image_label4 = pieces.Piece(self, player4.score_label, 'assets/Y5.png', initial_position4, 4, boardLayout, pieceList)
        pieceList.append(image_label4)

def startGame():
    app = QApplication(sys.argv)
    window = gameInterface()
    window.show()
    sys.exit(app.exec_())
