import sys
import time
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import pieces
import players
import board

def display_achievements(player):
    achievement_text = ""
    if player.first_move == True:
        achievement_text += "player first move\n"
    if player.score_label.text() == "21":
        if player.is_ai:
            achievement_text += "The Terminator: AI has shown dominance!\n"
        else:
            achievement_text += "Artificial Infant: Human outsmarted the AI!\n"
    if achievement_text:
        msg = QMessageBox()
        msg.setWindowTitle("Achievements Unlocked!")
        msg.setText(achievement_text)
        msg.exec_()
        achievement_text = ""

def on_exit_clicked():
    QApplication.quit()

def next_player_clicked(players, turn, board):
    for i in range(len(players)):
        if players[i].is_turn:
            display_achievements(players[i])
            players[i].is_turn = False
            if i+1 >= len(players):
                players[0].is_turn = True
                turn.turn.setText(players[0].name)
                if players[0].is_ai:
                    ai_move(players, turn, 0, board)
            else:
                players[i+1].is_turn = True
                turn.turn.setText(players[i+1].name)
                if players[i+1].is_ai:
                    ai_move(players, turn, i+1, board)
            break

#right now the AI can only place the piece at top left corner
def ai_move(players, turn, player_index, board):
    # Find the first piece that is not already on the board
    piece_to_place = None
    for piece in players[player_index].pieces:
        if not piece.onboard:
            piece_to_place = piece
            break

    if piece_to_place:
        # Find a valid position to place the piece
        for i in range(15, 250, 25):
            for j in range(145, 680):
                piece_to_place.last_confirmed_position = QPoint(i, j)
                if not piece_to_place.check_collision(piece_to_place.pieces):
                    piece_to_place.onboard = True
                    break

        # Update the score count only if the piece is successfully placed
        if piece_to_place.onboard:
            # Update the score count
            piece_to_place.score_label.setText(str(piece_to_place.weight + int(players[player_index].score_label.text())))

            # Slowly move the piece to the destination
            start_pos = piece_to_place.pos()
            end_pos = piece_to_place.last_confirmed_position
            num_steps = 100  # Adjust the number of steps for slower or faster movement
            step_x = (end_pos.x() - start_pos.x()) / num_steps
            step_y = (end_pos.y() - start_pos.y()) / num_steps

            def move_piece():
                nonlocal start_pos, num_steps

                start_pos.setX(round(start_pos.x() + step_x))  # Round the x position to an integer
                start_pos.setY(round(start_pos.y() + step_y))  # Round the y position to an integer
                piece_to_place.move(start_pos)

                num_steps -= 1
                if num_steps == 0:
                    next_player_clicked(players, turn, board)
                else:
                    QTimer.singleShot(10, move_piece)  # Adjust the delay for smoother movement

            move_piece()

def confirm_placement(pieces, board, player_list, turn):
    piece_placed = False    

    for piece in pieces:
        if piece.new_position is not None and not piece.onboard:
            
            # Calculate the starting position for the piece's shape within the tile
            startX = int((piece.new_position.x() - board.x() + board.tileSize // 2) / board.tileSize)
            startY = int((piece.new_position.y() - board.y() + board.tileSize // 2) / board.tileSize)

            # Check if the piece can be placed according to Blokus rules
            if board.canPlacePiece(piece.shape, startX, startY, piece):
                # Loop through the piece shape and update the tile colors accordingly
                for row in range(len(piece.shape)):
                    for col in range(len(piece.shape[row])):
                        if piece.shape[row][col] == 1:
                            board.tileList[startY + row][startX + col].changeColour(piece.colour)
                            board.tileList[startY + row][startX + col].changeState()

                # Mark the piece as on the board
                piece.last_confirmed_position = piece.new_position
                board.firstMove = False
                piece.new_position = None
                piece.onboard = True
                piece_placed = True

                #Remove pice from screen
                piece.setParent(None)
                piece.hide()

                # Update the score count
                piece.score_label.setText(str(int(piece.score_label.text()) + piece.weight))
                
                if piece_placed:
                    if piece.player.first_move:
                            piece.player.first_move = False
                    if turn:
                        next_player_clicked(player_list, turn, board)

class gameInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.pieceList = []
        self.playerList = []
        self.setWindowTitle("Game")
        self.setStyleSheet("background-color: rgb(139, 69, 19);")
        self.last_pressed_piece = None  # Initialize the last pressed piece as None
        
        layout = QVBoxLayout(self)
        self.boardLayout = board.Board()
        self.boardLayout.setFixedSize(560, 560)
        self.boardLayout.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        #CREATE EXIT
        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(on_exit_clicked)
        exit_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        #CREATE PASS
        pass_button = QPushButton('Pass', self)
        pass_button.clicked.connect(lambda: next_player_clicked(self.playerList, self.turn, self.boardLayout))
        pass_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        #CREATE CONFIRM
        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(lambda: confirm_placement(self.pieceList, self.boardLayout, self.playerList, self.turn))
        #confirm_button.clicked.connect(lambda: next_player_clicked(self.playerList, self.turn))
        confirm_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        #CREATE ROTATE
        rotate_button = QPushButton('Rotate', self)
        rotate_button.clicked.connect(self.rotate_piece)
        rotate_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        # Create a horizontal layout to hold the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(exit_button)
        buttons_layout.addWidget(confirm_button)
        buttons_layout.addWidget(rotate_button)
        buttons_layout.addWidget(pass_button)
        buttons_layout.setContentsMargins(20, 0, 20, 0)
        buttons_layout.setSpacing(20)
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.boardLayout)

        board_text_layout = QHBoxLayout()
        board_text_layout.addWidget(self.boardLayout)
        paragraph_text = QLabel("Drag the piece to the board when is your turn. \nCorfirm piece location by pressing confirm or \"enter\" on your keyboard")
        board_text_layout.addWidget(paragraph_text)
        layout.addLayout(board_text_layout)
        paragraph_text.setStyleSheet("font-size: 20px; color: white;")

        # Show whose turn is it
        player_text = QLabel("Player 1", self)
        self.turn = players.Turn(player_text)
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
            'shape': [[1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 300),
            'shape': [[1],[1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 300),
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 300), 
            'shape': [[1,0],[1,1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 300),
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 300),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'red'
        },
            #GREEN
         { 
            'player': player2,'image': 'assets/green/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 370),
            'shape': [[1]], 'colour': 'green' 
        },
        { 
            'player': player2,'image': 'assets/green/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 370), 
            'shape': [[1],[1]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 370), 
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 370), 
            'shape': [[1,0],[1,1]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 370),
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'green' 
        },
        { 
            'player': player3,'image': 'assets/green/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 370),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'green'
        },
            #BLUE
         {  
            'player': player3,'image': 'assets/blue/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 440), 
            'shape': [[1]], 'colour': 'blue' 
        },
        { 
            'player': player3,'image': 'assets/blue/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 440), 
            'shape': [[1],[1]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 440), 
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 440), 
            'shape': [[1,0],[1,1]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 440), 
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 440),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'blue'
        },
            #YELLOW
        {             
             
            'player': player4,'image': 'assets/yellow/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 510), 
            'shape': [[1]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 510), 
            'shape': [[1],[1]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 510), 
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 510), 
            'shape': [[1,0],[1,1]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 510), 
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 510),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'yellow'
        },
        ]
        for piece_data in player_pieces:
            player = piece_data['player']
            image_label = pieces.Piece(
                self, player.score_label, piece_data['image'], piece_data['initial_position'],
                piece_data['weight'], self.boardLayout, self.pieceList, piece_data['shape'], piece_data['colour'], player
            )
            self.pieceList.append(image_label)
            player.pieces.append(image_label)

    def rotate_piece(self):
        # Find the last pressed piece
        active_piece = self.last_pressed_piece

        if not active_piece:
            return

        #rotate shape and recreate pixmap
        rotated_shape = list(zip(*reversed(active_piece.shape)))
        rotated_pixmap = active_piece.pixmap.transformed(QTransform().rotate(90))

        new_pixmap = QPixmap(rotated_pixmap.size())
        new_pixmap.fill(Qt.transparent)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, rotated_pixmap)
        painter.end()

        active_piece.shape = rotated_shape
        active_piece.pixmap = new_pixmap

        active_piece.setPixmap(active_piece.pixmap)

        active_piece.setFixedSize(rotated_pixmap.size())

        mask = QBitmap(active_piece.pixmap.createMaskFromColor(Qt.transparent))
        active_piece.setMask(mask)

        active_piece.move(active_piece.pos())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            confirm_placement(self.pieceList, self.boardLayout,self.playerList, self.turn)
            next_player_clicked(self.playerList, self.turn, self.boardLayout)

def startGame():
    app = QApplication(sys.argv)
    window = gameInterface()
    window.show()
    window.showFullScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    startGame()
