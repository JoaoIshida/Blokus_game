import sys
import time
import pickle
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
    #if player.first_move == True:
    #    achievement_text += "player first move\n"
    if player.score_label.text() == "35":
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
            # make all pieces of player i not movable
            for piece in players[i].pieces:
                piece.movable = False
                piece.set_color_overlay(Qt.gray)
            if i + 1 >= len(players):
                next_player_index = 0
            else:
                next_player_index = i+1
            players[next_player_index].is_turn = True
            # make all pieces of player 1 become movable
            for piece in players[next_player_index].pieces:
                piece.movable = True
                piece.set_color_overlay(Qt.transparent)
            turn.turn.setText(f"Current player({players[next_player_index].pieces[0].colour}): {players[next_player_index].name}")
            if players[next_player_index].is_ai:
                ai_move(players, turn, next_player_index, board)
            break

def ai_move(players, turn, playerIndex, board):
    placeablePieces = []
    validPositions = []
    for piece in players[playerIndex].pieces:
        if not piece.onboard:
            placeablePieces.append(piece)

    if len(placeablePieces) != 0:
        for piece in placeablePieces:
            for row in range(0, 20):
                for col in range(0, 20):
                    if board.canPlacePiece(col, row, piece) and not board.aiCollision(col, row, piece):
                        value = board.getValue(col, row, piece)
                        validPositions.append((col, row, piece, value))

    if len(validPositions) != 0:
        maxValue = max(validPositions, key=lambda x: x[3])
        if board.canPlacePiece(maxValue[0], maxValue[1], maxValue[2]):
            for row in range(len(maxValue[2].shape)):
                for col in range(len(maxValue[2].shape[row])):
                    if maxValue[2].shape[row][col] == 1:
                        board.tileList[maxValue[1] + row][maxValue[0] + col].changeColour(maxValue[2].colour)
                        board.tileList[maxValue[1] + row][maxValue[0] + col].changeState()
                        # Mark the piece as on the board
            maxValue[2].last_confirmed_position = maxValue[2].new_position
            maxValue[2].new_position = None
            maxValue[2].onboard = True
            piece_placed = True

            # Remove piece from screen
            maxValue[2].setParent(None)
            maxValue[2].hide()

            # Update the score count
            maxValue[2].score_label.setText(str(int(maxValue[2].score_label.text()) + maxValue[2].weight))

            if piece_placed:
                if maxValue[2].player.first_move:
                    maxValue[2].player.first_move = False
                if turn:
                    next_player_clicked(players, turn, board)
    else:
        next_player_clicked(players, turn, board)

def confirm_placement(board, player_list, turn):
    piece_placed = False    
    for player in player_list:
        if player.is_turn:
            for piece in player.pieces:
                if piece.new_position is not None and not piece.onboard:

                    # Calculate the starting position for the piece's shape within the tile
                    startX = int((piece.new_position.x() - board.x() + board.tileSize // 2) / board.tileSize)
                    startY = int((piece.new_position.y() - board.y() + board.tileSize // 2) / board.tileSize)

                    # Check if the piece can be placed according to Blokus rules
                    if board.canPlacePiece(startX, startY, piece):
                        # Loop through the piece shape and update the tile colors accordingly
                        for row in range(len(piece.shape)):
                            for col in range(len(piece.shape[row])):
                                if piece.shape[row][col] == 1:
                                    board.tileList[startY + row][startX + col].changeColour(piece.colour)
                                    board.tileList[startY + row][startX + col].changeState()

                        # Mark the piece as on the board
                        piece.last_confirmed_position = piece.new_position
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
        confirm_button.clicked.connect(lambda: confirm_placement(self.boardLayout, self.playerList, self.turn))
        confirm_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        #CREATE ROTATE
        rotate_button = QPushButton('Rotate', self)
        rotate_button.clicked.connect(self.rotate_piece)
        rotate_button.setStyleSheet("QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        # CREATE SAVE
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.saveGame)  # under development
        save_button.setStyleSheet(
            "QPushButton { border-radius: 25px; padding: 20px; font-size: 20px; border: 2px solid black; background-color: rgb(224, 166, 181);}")

        # Create a horizontal layout to hold the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(exit_button)
        buttons_layout.addWidget(confirm_button)
        buttons_layout.addWidget(rotate_button)
        buttons_layout.addWidget(pass_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.setContentsMargins(20, 0, 20, 0)
        buttons_layout.setSpacing(20)
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.boardLayout)

        board_text_layout = QHBoxLayout()
        board_text_layout.addWidget(self.boardLayout)
        paragraph_text = QLabel("Drag the piece to the board when is your turn. \nCorfirm piece location by pressing Confirm or \"enter\" on your keyboard\nRotate piece location by pressing Rotate or \"R\" on your keyboard\nPass turn by pressing Pass or \"P\" on your keyboard\nExit game by pressing Exit or \"Esc\" on your keyboard\nSave the game state by pressing Save")
        board_text_layout.addWidget(paragraph_text)
        layout.addLayout(board_text_layout)
        paragraph_text.setStyleSheet("font-size: 20px; color: white;")

        playerPanel1 = players.PlayerPanel("red")
        playerPanel2 = players.PlayerPanel("green")
        playerPanel3 = players.PlayerPanel("blue")
        playerPanel4 = players.PlayerPanel("yellow")

        # Show whose turn is it
        self.current_player_label = QLabel("Current player (red): Player 1", self)
        self.current_player_label.setStyleSheet("font-size: 30px; font-weight: bold; color: black; background-color: rgb(255, 150, 100);")
        self.turn = players.Turn(self.current_player_label)
        layout.addWidget(self.current_player_label)

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
            'initial_position': QPoint(50, playerPanel1.height() + 270), 
            'shape': [[1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 270),
            'shape': [[1],[1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 270),
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 270), 
            'shape': [[1,0],[1,1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 270),
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 270),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/T4.png','weight': 4,
            'initial_position': QPoint(540, playerPanel1.height() + 270), 
            'shape': [[1,1,1],[0,1,0]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/P5.png','weight': 5,
            'initial_position': QPoint(625, playerPanel1.height() + 270), 
            'shape': [[1,1],[1,1],[1,0]], 'colour': 'red'
        },
        { 
            'player': player1,'image': 'assets/red/W5.png','weight': 5,
            'initial_position': QPoint(700, playerPanel1.height() + 270), 
            'shape': [[1,0,0],[1,1,0],[0,1,1]], 'colour': 'red'
        },
            #GREEN
         { 
            'player': player2,'image': 'assets/green/1.png','weight': 1,
            'initial_position': QPoint(50, playerPanel1.height() + 350),
            'shape': [[1]], 'colour': 'green' 
        },
        { 
            'player': player2,'image': 'assets/green/2.png','weight': 2,
            'initial_position': QPoint(100, playerPanel1.height() + 350), 
            'shape': [[1],[1]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/F5.png','weight': 5,
            'initial_position': QPoint(150, playerPanel1.height() + 350), 
            'shape': [[0,1,1],[1,1,0],[0,1,0]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/L3.png','weight': 3,
            'initial_position': QPoint(250, playerPanel1.height() + 350), 
            'shape': [[1,0],[1,1]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/Z5.png','weight': 5,
            'initial_position': QPoint(325, playerPanel1.height() + 350),
            'shape': [[1,1,1,0],[0,0,1,1]], 'colour': 'green' 
        },
        { 
            'player': player2,'image': 'assets/green/X5.png','weight': 5,
            'initial_position': QPoint(450, playerPanel1.height() + 350),
            'shape': [[0,1,0],[1,1,1],[0,1,0]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/T4.png','weight': 4,
            'initial_position': QPoint(540, playerPanel1.height() + 350), 
            'shape': [[1,1,1],[0,1,0]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/P5.png','weight': 5,
            'initial_position': QPoint(625, playerPanel1.height() + 350), 
            'shape': [[1,1],[1,1],[1,0]], 'colour': 'green'
        },
        { 
            'player': player2,'image': 'assets/green/W5.png','weight': 5,
            'initial_position': QPoint(700, playerPanel1.height() + 350), 
            'shape': [[1,0,0],[1,1,0],[0,1,1]], 'colour': 'green'
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
        { 
            'player': player3,'image': 'assets/blue/T4.png','weight': 4,
            'initial_position': QPoint(540, playerPanel1.height() + 440), 
            'shape': [[1,1,1],[0,1,0]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/P5.png','weight': 5,
            'initial_position': QPoint(625, playerPanel1.height() + 440), 
            'shape': [[1,1],[1,1],[1,0]], 'colour': 'blue'
        },
        { 
            'player': player3,'image': 'assets/blue/W5.png','weight': 5,
            'initial_position': QPoint(700, playerPanel1.height() + 440), 
            'shape': [[1,0,0],[1,1,0],[0,1,1]], 'colour': 'blue'
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
        { 
            'player': player4,'image': 'assets/yellow/T4.png','weight': 4,
            'initial_position': QPoint(540, playerPanel1.height() + 510), 
            'shape': [[1,1,1],[0,1,0]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/P5.png','weight': 5,
            'initial_position': QPoint(625, playerPanel1.height() + 510), 
            'shape': [[1,1],[1,1],[1,0]], 'colour': 'yellow'
        },
        { 
            'player': player4,'image': 'assets/yellow/W5.png','weight': 5,
            'initial_position': QPoint(700, playerPanel1.height() + 510), 
            'shape': [[1,0,0],[1,1,0],[0,1,1]], 'colour': 'yellow'
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

        # Make player 1's pieces movable since that's the first player
        for piece in player1.pieces:
            piece.movable = True
            piece.set_color_overlay(Qt.transparent)

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
        key = event.key()
        if key == Qt.Key_Escape:  # "ESC" key for exiting
            on_exit_clicked()
        elif key == Qt.Key_R:  # "R" key for rotation
            self.rotate_piece()
        elif key == Qt.Key_P:  # "P" key for passing
            next_player_clicked(self.playerList, self.turn, self.boardLayout)
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            confirm_placement(self.boardLayout, self.playerList, self.turn)

    def saveGame(self):
        # print(json.dumps(self.playerList[0].pieces))
        with open("savePlayer.pkl", 'wb') as file:
            pickle.dump(self.playerList, file)
        with open("saveTurn.pkl", 'wb') as file:
            pickle.dump(self.turn, file)
        with open("saveBoard.pkl", 'wb') as file:
            pickle.dump(self.boardLayout, file)
        with open("savePieces.pkl", 'wb') as file:
            pickle.dump(self.pieceList, file)

    def loadGame(self):
        with open("saveTurn.pkl", "rb") as file:
            self.turn.turn.setText(pickle.load(file).turnText)
        with open("saveBoard.pkl", "rb") as file:
            Board = pickle.load(file)

            #iterate through each square on the board. Is there any better way to do this?
            for i in range(20):
                for j in range(20):
                    self.boardLayout.tileList[i][j].tileColor = Board.tileList[i][j].tileColor
                    self.boardLayout.tileList[i][j].changeColour(Board.tileList[i][j].tileColor)
                    self.boardLayout.tileList[i][j].isTileEmpty = Board.tileList[i][j].isTileEmpty
                    # do we need to set x & y as well or they will be unchanged?

        with open("savePieces.pkl", 'rb') as file:
            Pieces = pickle.load(file)
            for i in range(len(self.pieceList)):
                self.pieceList[i].dragging = Pieces[i].dragging
                self.pieceList[i].offset = Pieces[i].offset
                self.pieceList[i].onboard = Pieces[i].onboard
                self.pieceList[i].movable = Pieces[i].movable
                self.pieceList[i].last_confirmed_position = Pieces[i].last_confirmed_position
                self.pieceList[i].new_position = Pieces[i].new_position

                # Update QLabels accordingly
                if self.pieceList[i].onboard:
                    self.pieceList[i].hide()

                # Set overlay to gray as default, we will update it in the next step
                self.pieceList[i].set_color_overlay(Qt.gray)

        with open("savePlayer.pkl", "rb") as file:
            # load the saved player data file
            playerData = pickle.load(file)

            #set the score label for each player
            for i in range(len(self.playerList)):
                text = playerData[i].score
                self.playerList[i].score_label.setText(text)
                self.playerList[i].is_ai = playerData[i].is_ai
                self.playerList[i].is_turn = playerData[i].is_turn
                self.playerList[i].name = playerData[i].name
                self.playerList[i].first_move = playerData[i].first_move

            # Now the players are updates, update QLabel overlay accordingly
                if self.playerList[i].is_turn:
                    for piece in self.playerList[i].pieces:
                        piece.set_color_overlay(Qt.transparent)
def startGame():
    app = QApplication(sys.argv)
    window = gameInterface()
    window.show()
    window.showFullScreen()
    # window.showMaximized()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    startGame()
