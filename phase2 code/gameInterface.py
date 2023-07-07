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
                if players[0].is_ai:
                    ai_move(players, turn, 0)
            else:
                players[i+1].is_turn = True
                turn.turn.setText(players[i+1].name)
                if players[i+1].is_ai:
                    ai_move(players, turn, i+1)
            break

#right now the AI can only place the piece at top left corner
def ai_move(players, turn, player_index):
    # Find the first piece that is not already on the board
    piece_to_place = None
    for piece in players[player_index].pieces:
        if not piece.onboard:
            piece_to_place = piece
            break

    if piece_to_place:
        # Find a valid position to place the piece
        for i in range(15, 250, 25):
            for j in range(90, 250):
                piece_to_place.last_confirmed_position = QPoint(i, j)
                piece_to_place.move(piece_to_place.last_confirmed_position)
                if not piece_to_place.check_collision(piece_to_place.pieces):
                    piece_to_place.onboard = True
                    break

        # Update the score count only if the piece is successfully placed
        if piece_to_place.onboard:
            # Update the score count
            piece_to_place.score_label.setText(str(piece_to_place.weight))

    next_player_clicked(players, turn)

def confirm_placement(pieces):
    for piece in pieces:
        if piece.new_position is not None and not piece.onboard:  # Add condition to check if the piece is not already on the board
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
        self.pieceList = []
        self.playerList = []
        self.setWindowTitle("Game")
        #self.setGeometry(200, 0, 1200, 900)
        self.setStyleSheet("background-color: rgb(139, 69, 19);")

        layout = QVBoxLayout(self)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(on_exit_clicked)

        pass_button = QPushButton('Pass', self)
        pass_button.clicked.connect(lambda: next_player_clicked(self.playerList, turn))

        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(lambda: confirm_placement(self.pieceList))
        confirm_button.clicked.connect(lambda: next_player_clicked(self.playerList, turn))
        layout.addWidget(confirm_button)

        boardLayout = board.Board()
        boardLayout.setFixedSize(560, 560)
        boardLayout.setStyleSheet("background-color: rgb(255, 255, 255);")        
    
        layout.addWidget(exit_button)
        layout.addWidget(pass_button)
        layout.addWidget(boardLayout)

        board_text_layout = QHBoxLayout()
        board_text_layout.addWidget(boardLayout)
        paragraph_text = QLabel("Drag the piece to the board when is your turn. \nCorfirm piece location by pressing confirm or \"enter\" on your keyboard")
        board_text_layout.addWidget(paragraph_text)
        layout.addLayout(board_text_layout)
        paragraph_text.setStyleSheet("font-size: 20px; color: white;")

        # Show whose turn is it
        player_text = QLabel("Player 1", self)
        turn = players.Turn(player_text)
        layout.addWidget(QLabel("Current player's turn:", self))
        layout.addWidget(player_text)

        playerPanel1 = players.PlayerPanel("red")
        playerPanel2 = players.PlayerPanel("green")
        playerPanel3 = players.PlayerPanel("blue")
        playerPanel4 = players.PlayerPanel("yellow")

        # Player 1 - RED
        layout.addWidget(playerPanel1)
        player1 = players.Player(playerPanel1, is_turn = True, name = "Player 1")

        # Player 2 - GREEN
        layout.addWidget(playerPanel2)
        player2 = players.Player(playerPanel2, is_ai=True, name = "Player 2: AI1")

        # Player 3 - BLUE
        layout.addWidget(playerPanel3)
        player3 = players.Player(playerPanel3, is_ai = False, name = "Player 3")

        # Player 4 - YELLOW
        layout.addWidget(playerPanel4)
        player4 = players.Player(playerPanel4, is_ai=True, name = "Player 4: AI2")

        self.playerList.append(player1)
        self.playerList.append(player2)
        self.playerList.append(player3)
        self.playerList.append(player4)
        
        player_pieces = [
            #SO FAR, EVERY SCORE IS AFTER 70, AND DISTANCE IS AROUND 50
            #RED
        { 
            'player': player1,'image': 'assets/red/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 300), 
        },
        { 
            'player': player1,'image': 'assets/red/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 300), 
        },
        { 
            'player': player1,'image': 'assets/red/L3.png','weight': 3,
            'initial_position': QPoint(150, playerPanel1.height() + 300), 
        },
        { 
            'player': player1,'image': 'assets/red/Z5.png','weight': 5,
            'initial_position': QPoint(220, playerPanel1.height() + 300), 
        },
        { 
            'player': player1,'image': 'assets/red/X5.png','weight': 5,
            'initial_position': QPoint(350, playerPanel1.height() + 300), 
        },
            #GREEN
         { 
            'player': player2,'image': 'assets/green/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 370), 
        },
        { 
            'player': player2,'image': 'assets/green/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 370), 
        },
        { 
            'player': player2,'image': 'assets/green/L3.png','weight': 3,
            'initial_position': QPoint(150, playerPanel1.height() + 370), 
        },
        { 
            'player': player2,'image': 'assets/green/Z5.png','weight': 5,
            'initial_position': QPoint(220, playerPanel1.height() + 370), 
        },
        { 
            'player': player2,'image': 'assets/green/X5.png','weight': 5,
            'initial_position': QPoint(350, playerPanel1.height() + 370), 
        },
            #BLUE
         { 
            'player': player3,'image': 'assets/blue/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 440), 
        },
        { 
            'player': player3,'image': 'assets/blue/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 440), 
        },
        { 
            'player': player3,'image': 'assets/blue/L3.png','weight': 3,
            'initial_position': QPoint(150, playerPanel1.height() + 440), 
        },
        { 
            'player': player3,'image': 'assets/blue/Z5.png','weight': 5,
            'initial_position': QPoint(220, playerPanel1.height() + 440), 
        },
        { 
            'player': player3,'image': 'assets/blue/X5.png','weight': 5,
            'initial_position': QPoint(350, playerPanel1.height() + 440), 
        },
            #YELLOW
         { 
            'player': player4,'image': 'assets/yellow/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 510), 
        },
        { 
            'player': player4,'image': 'assets/yellow/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 510), 
        },
        { 
            'player': player4,'image': 'assets/yellow/L3.png','weight': 3,
            'initial_position': QPoint(150, playerPanel1.height() + 510), 
        },
        { 
            'player': player4,'image': 'assets/yellow/Z5.png','weight': 5,
            'initial_position': QPoint(220, playerPanel1.height() + 510), 
        },
        { 
            'player': player4,'image': 'assets/yellow/X5.png','weight': 5,
            'initial_position': QPoint(350, playerPanel1.height() + 510), 
        },
        ]
        for piece_data in player_pieces:
            player = piece_data['player']
            image_label = pieces.Piece(
                self, player.score_label, piece_data['image'], piece_data['initial_position'],
                piece_data['weight'], boardLayout, self.pieceList
            )
            self.pieceList.append(image_label)
            player.pieces.append(image_label)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            confirm_placement(self.pieceList)

def startGame():
    app = QApplication(sys.argv)
    window = gameInterface()
    window.show()
    window.showFullScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    startGame()