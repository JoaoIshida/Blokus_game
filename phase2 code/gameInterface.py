import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
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

def startGame():
    app = QApplication(sys.argv)
    pieceList = []
    playerList = []
    window = QWidget()
    window.setWindowTitle("Game")
    window.setGeometry(100, 50, 900, 900)
    window.setStyleSheet("background-color: rgb(139, 69, 19);")

    layout = QVBoxLayout(window)

    exit_button = QPushButton('Exit', window)
    exit_button.clicked.connect(on_exit_clicked)

    pass_button = QPushButton('Pass', window)
    pass_button.clicked.connect(lambda: next_player_clicked(playerList, turn))

    confirm_button = QPushButton('Confirm', window)
    confirm_button.clicked.connect(lambda: confirm_placement(pieceList))
    confirm_button.clicked.connect(lambda: next_player_clicked(playerList, turn))
    layout.addWidget(confirm_button)

    boardLayout = board.Board()
    boardLayout.setFixedSize(560, 560)
    boardLayout.setStyleSheet("background-color: rgb(255, 255, 255);")


    layout.addWidget(exit_button)
    layout.addWidget(pass_button)
    layout.addWidget(boardLayout)

    # Player 1 - RED
    score_label1 = QLabel("0")
    score_label1.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label1.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(255, 0, 0);")
    layout.addWidget(score_label1)

    player1 = players.Player(score_label1, is_turn = True, name = "Player 1")

    # Player 2 - GREEN
    score_label2 = QLabel("0")
    score_label2.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label2.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(0, 255, 0);")
    layout.addWidget(score_label2)

    player2 = players.Player(score_label2, is_ai=True, name = "AI")

    # Player 3 - BLUE
    score_label3 = QLabel("0")
    score_label3.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label3.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(0, 0, 255);")
    layout.addWidget(score_label3)

    player3 = players.Player(score_label3, name = "Player 3")

    # Player 4 - YELLOW
    score_label4 = QLabel("0")
    score_label4.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label4.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(255, 255, 0);")
    layout.addWidget(score_label4)

    player4 = players.Player(score_label4, name = "Player 4")

    playerList.append(player1)
    playerList.append(player2)
    playerList.append(player3)
    playerList.append(player4)
    
    # Show whose turn is it
    player_text = QLabel("Player 1", window)
    turn = players.Turn(player_text)
    layout.addWidget(player_text)


    # Player 1's Pieces - RED
    initial_position1 = QPoint(200, score_label1.height() + 250)
    image_label1 = pieces.Piece(window, player1.score_label, 'assets/X5.png', initial_position1, 5, boardLayout, pieceList)
    pieceList.append(image_label1)

    # Player 2's Pieces - GREEN
    initial_position2 = QPoint(200, score_label2.height() + 150)
    image_label2 = pieces.Piece(window, player2.score_label, 'assets/L5.png', initial_position2, 5, boardLayout, pieceList)
    pieceList.append(image_label2)

    # Player 3's Pieces - BLUE
    initial_position3 = QPoint(50, score_label3.height() + 150)
    image_label3 = pieces.Piece(window, player3.score_label, 'assets/Z5.png', initial_position3, 2, boardLayout, pieceList)
    pieceList.append(image_label3)

    # Player 4's Pieces -YELLOW
    initial_position4 = QPoint(350, score_label4.height() + 250)
    image_label4 = pieces.Piece(window, player4.score_label, 'assets/Y5.png', initial_position4, 4, boardLayout, pieceList)
    pieceList.append(image_label4)

    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    startGame()