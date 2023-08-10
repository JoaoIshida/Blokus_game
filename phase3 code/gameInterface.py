import os
import sys
import pickle
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
import game
import pieces
import players
import board
import button
from players import goldman

def display_achievements(player):
    achievement_text = ""

    if player.score_label.text() == "89":
        if player.is_ai:
            achievement_text += "The Terminator: AI has shown dominance!\n"
            game.MainWindow.achievements["The Terminator"] = True
        else:
            achievement_text += "Artificial Infant: Human outsmarted the AI!\n"
            game.MainWindow.achievements["Artificial Infant"] = True
    if achievement_text:
        msg = QMessageBox()
        msg.setWindowTitle("Achievements Unlocked!")
        msg.setText(achievement_text)
        msg.exec_()
        achievement_text = ""

        # Save achievements to file
        with open(game.MainWindow.achievements_file, "wb") as f:
            pickle.dump(game.MainWindow.achievements, f)

def next_player_clicked(players, turn, board, playerMovedFirst, gameInterface):
    gameInterface.check_end_game()
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
                next_player_index = i + 1
            players[next_player_index].is_turn = True
            # make all pieces of player 1 become movable
            for piece in players[next_player_index].pieces:
                piece.movable = True
                piece.set_color_overlay(Qt.transparent)
            turn.turn.setText(
                f"  Current player({players[next_player_index].pieces[0].colour}): {players[next_player_index].name}  ")
            if players[next_player_index].is_ai:
                if playerMovedFirst == False:
                    return
                ai_move(players, turn, next_player_index, board, gameInterface)
            break

def placeable_pieces(player):
    placeablePieces = []
    for piece in player.pieces:
            if not piece.onboard:
                placeablePieces.append(piece)
    return placeablePieces

def ai_move(players, turn, playerIndex, board, gameInterface):
    validPositions = []
    # Check which pieces are placeable on the board
    
    placeablePieces = []
    placeablePieces = placeable_pieces(players[playerIndex])

    # Check which positions are placeable for each piece
    if len(placeablePieces) != 0:
        validPositions = gameInterface.get_valid_moves(playerIndex, placeablePieces, board)

    # Place the piece with the highest value
    if len(validPositions) != 0:
        maxValue = max(validPositions, key=lambda x: x[3])

        for _ in range(maxValue[5]):
            maxValue[2].flipShape()
        for _ in range(maxValue[4]):
            maxValue[2].rotateShape()
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
                gameInterface.soundPlayer.play_sound()
                if maxValue[2].player.first_move:
                    maxValue[2].player.first_move = False
                if turn:
                    next_player_clicked(players, turn, board, True, gameInterface)
    else:
        next_player_clicked(players, turn, board,True, gameInterface)


def confirm_placement(board, player_list, turn, gameInterface):
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

                        # Remove pice from screen
                        piece.setParent(None)
                        piece.hide()

                        # Update the score count
                        piece.score_label.setText(str(int(piece.score_label.text()) + piece.weight))

                        if piece_placed:
                            gameInterface.soundPlayer.play_sound()
                            if piece.player.first_move:
                                piece.player.first_move = False
                            if turn:
                                next_player_clicked(player_list, turn, board, True, gameInterface)


class gameInterface(QWidget):
    def __init__(self, playerTypes, soundPlayer):
        super().__init__()
        self.pieceList = []
        self.playerList = []
        self.soundPlayer = soundPlayer
        self.playerTypes = playerTypes
        self.last_pressed_piece = None
        self.setWindowTitle("Exit")
        self.setStyleSheet("background-color: rgb(173, 151, 108);")

        layout = QVBoxLayout(self)
        layout.setSpacing(40)

        self.boardLayout = board.Board()
        self.boardLayout.setFixedSize(560, 560)

        # CREATE EXIT
        exit_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Exit", "rgb(244, 195, 209)", "rgb(202, 123, 139)", "25",parent=self)
        exit_button.clicked.connect(self.on_exit_clicked)

        # CREATE PASS
        pass_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Pass", "rgb(244, 195, 209)", "rgb(202, 123, 139)", "25",parent=self)
        pass_button.clicked.connect(lambda: next_player_clicked(self.playerList, self.turn, self.boardLayout, True, self))

        # CREATE CONFIRM
        confirm_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Confirm Placement", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)
        confirm_button.clicked.connect(lambda: confirm_placement(self.boardLayout, self.playerList, self.turn, self))

        # CREATE ROTATE
        rotate_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Rotate", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)
        rotate_button.clicked.connect(self.rotate_piece)

        # CREATE FLIP
        flip_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Flip", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)
        flip_button.clicked.connect(self.flip_piece)

        # CREATE Settings
        settingsButton = button.createButton("rgb(224, 166, 181)", (300, 75), "Settings", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)
        settingsButton.clicked.connect(self.on_settings_button_press)

        # Create End game
        self.endButton = button.createButton("rgb(224, 166, 181)", (300, 75), "End Game", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)
        self.endButton.clicked.connect(self.endGame)

        line_layout = QHBoxLayout()
        line_layout.setSpacing(20)
        layout.addLayout(line_layout)

        # Show whose turn is it
        self.current_player_label = QLabel("  Current player (red): Player 1  ", self)
        self.current_player_label.setStyleSheet(
            "font-size: 30px; font-weight: bold; color: black; background-color: #D9D9D9;")
        self.turn = players.Turn(self.current_player_label)
        self.current_player_label.setFont(goldman(size=12))
        line_layout.addWidget(self.current_player_label)
        line_layout.addWidget(self.endButton)
        self.score_container = QWidget(self)
        layout.addWidget(self.score_container, alignment=Qt.AlignCenter)

        # board frame
        frame = QFrame(self)
        frame.setFixedSize(570, 570)
        frame.setStyleSheet("border: 5px solid black; background-color: transparent;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.move(675, 389)
        layout.addWidget(self.boardLayout, alignment=Qt.AlignCenter)

        # Create a horizontal layout to hold the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(confirm_button)
        buttons_layout.addWidget(rotate_button)
        buttons_layout.addWidget(flip_button)
        buttons_layout.addWidget(pass_button)
        buttons_layout.setContentsMargins(0, 0, 20, 0)
        buttons_layout.setSpacing(20)
        layout.addLayout(buttons_layout)

        self.player_containers = []
        for i in range(4):
            player_container = QWidget(self)
            player_container.setFixedSize(420, 420)
            player_layout = QVBoxLayout(player_container)

            # Add player panel content (replace the following line with your player panel content)
            label = QLabel(f"Player {i + 1} Panel", player_container)
            label.setAlignment(Qt.AlignBottom)
            label.setFixedSize(270, 50)
            label.setContentsMargins(20, 0, 0, 0)
            label.setStyleSheet("font-size: 30px; font-weight: bold; color: black; border-radius: 50px;")
            label.setFont(goldman(size=12))

            player_layout.addWidget(label)
            player_layout.setContentsMargins(0, 0, 0, 0)
            player_layout.setAlignment(Qt.AlignTop)

            self.player_containers.append(player_container)

        # set locations
        self.player_containers[0].move(100, 130)
        self.player_containers[1].move(1400, 130)
        self.player_containers[2].move(100, 570)
        self.player_containers[3].move(1400, 570)
        # set colors
        self.player_containers[0].setStyleSheet("background-color: #CE4A4A; border-radius: 50px;")
        self.player_containers[1].setStyleSheet("background-color: #2EAE52;  border-radius: 50px;")
        self.player_containers[2].setStyleSheet("background-color: #294FB0;  border-radius: 50px;")
        self.player_containers[3].setStyleSheet("background-color: #F4FF72;  border-radius: 50px;")

        playerPanel1 = self.player_containers[0]
        playerPanel2 = self.player_containers[1]
        playerPanel3 = self.player_containers[2]
        playerPanel4 = self.player_containers[3]

        self.score_container.setFixedSize(500, 200)
        self.score_layout = QVBoxLayout(self.score_container)
        self.score_container.setStyleSheet("background-color:#D9D9D9; border-radius: 50px; padding: black;")
        self.score_container.setFont(goldman(size=20))

        self.player_scores = [0, 0, 0, 0]

        # Add QHBoxLayouts for each player's score row
        # First QHBoxLayout for player 1 and player 2 scores
        hbox1 = QHBoxLayout()
        for i in range(2):
            score_panel = players.ScorePanel(f"Player{i + 1}")  # Use the custom ScorePanel widget
            hbox1.addWidget(score_panel)
            self.player_scores[i] = score_panel.score_label  # Save the score_label reference

        # Second QHBoxLayout for player 3 and player 4 scores
        hbox2 = QHBoxLayout()
        for i in range(2, 4):
            score_panel = players.ScorePanel(f"Player{i + 1}")  # Use the custom ScorePanel widget
            hbox2.addWidget(score_panel)
            self.player_scores[i] = score_panel.score_label  # Save the score_label reference

        # Add the two QHBoxLayouts to the QVBoxLayout
        self.score_layout.addLayout(hbox1)
        self.score_layout.addLayout(hbox2)

        colours = ["red", "green", "blue", "yellow"]
        self.humanFirstMove = False
        self.aiMovesBeforeFirstMove = 0
        # create players
        for i in range(1,5):
            if i == 1 and self.playerTypes[i] == "AI":
                player = players.Player(self.player_scores[i-1], is_ai=True, is_turn=False, name=f"Player {i}", color=colours[i-1], num=f"player{i}")
                self.aiMovesBeforeFirstMove += 1
            elif i == 1 and self.playerTypes[i] == "Human":
                self.humanFirstMove = True
                player = players.Player(self.player_scores[i-1], is_ai=False, is_turn=True, name=f"Player {i}", color=colours[i-1], num=f"player{i}")
            elif self.playerTypes[i] == "AI":
                player = players.Player(self.player_scores[i-1],is_ai=True, is_turn=False, name=f"Player {i}", color=colours[i-1], num=f"player{i}")
                self.aiMovesBeforeFirstMove += 1
            elif self.playerTypes[i] == "Human":
                if self.humanFirstMove == False:
                    player = players.Player(self.player_scores[i-1],is_ai=False, is_turn=True, name=f"Player {i}", color=colours[i-1], num=f"player{i}")
                    self.humanFirstMove = True
                else:
                    player = players.Player(self.player_scores[i-1],is_ai=False, is_turn=False, name=f"Player {i}", color=colours[i-1], num=f"player{i}")
            self.playerList.append(player)


        player_panels = [playerPanel1, playerPanel2, playerPanel3, playerPanel4]

        for player_index, player in enumerate(self.playerList):
            player_panel = player_panels[player_index]
            pieces_data = [
                {
                    'player': player.num, 'image': f'assets/{player.color}/1.png', 'weight': 1,
                    'initial_position': QPoint(player_panel.x() + 10, player_panel.y() + 50),
                    'shape': [[1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/2.png', 'weight': 2,
                    'initial_position': QPoint(player_panel.x() + 50, player_panel.y() + 50),
                    'shape': [[1], [1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/3.png', 'weight': 3,
                    'initial_position': QPoint(player_panel.x() + 90, player_panel.y() + 50),
                    'shape': [[1], [1], [1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/4.png', 'weight': 4,
                    'initial_position': QPoint(player_panel.x() + 130, player_panel.y() + 50),
                    'shape': [[1], [1], [1], [1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 170, player_panel.y() + 50),
                    'shape': [[1], [1], [1], [1], [1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/F5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 190, player_panel.y() + 170),
                    'shape': [[0, 1, 1], [1, 1, 0], [0, 1, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/L3.png', 'weight': 3,
                    'initial_position': QPoint(player_panel.x() + 180, player_panel.y() + 350),
                    'shape': [[1, 0], [1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/L4.png', 'weight': 4,
                    'initial_position': QPoint(player_panel.x() + 320, player_panel.y() + 150),
                    'shape': [[1, 1, 1], [0, 0, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/L5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 60, player_panel.y() + 300),
                    'shape': [[1, 1, 1, 1], [0, 0, 0, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/O4.png', 'weight': 4,
                    'initial_position': QPoint(player_panel.x() + 285, player_panel.y() + 50),
                    'shape': [[1, 1], [1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/P5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 210, player_panel.y() + 50),
                    'shape': [[1, 1], [1, 1], [1, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/S5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 100, player_panel.y() + 170),
                    'shape': [[1, 1, 0], [0, 1, 0], [0, 1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/T4.png', 'weight': 4,
                    'initial_position': QPoint(player_panel.x() + 190, player_panel.y() + 270),
                    'shape': [[1, 1, 1], [0, 1, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/T5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 255, player_panel.y() + 110),
                    'shape': [[1, 1, 1], [0, 1, 0], [0, 1, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/U5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 350, player_panel.y() + 50),
                    'shape': [[1, 1], [1, 0], [1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/V5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 10, player_panel.y() + 300),
                    'shape': [[1, 0, 0], [1, 0, 0], [1, 1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/W5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 10, player_panel.y() + 100),
                    'shape': [[1, 0, 0], [1, 1, 0], [0, 1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/X5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 10, player_panel.y() + 200),
                    'shape': [[0, 1, 0], [1, 1, 1], [0, 1, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/Y5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 300, player_panel.y() + 300),
                    'shape': [[1, 1, 1, 1], [0, 1, 0, 0]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/Z4.png', 'weight': 4,
                    'initial_position': QPoint(player_panel.x() + 250, player_panel.y() + 350),
                    'shape': [[1, 1, 0, ], [0, 1, 1]], 'colour': f'{player.color}'
                },
                {
                    'player': player.num, 'image': f'assets/{player.color}/Z5.png', 'weight': 5,
                    'initial_position': QPoint(player_panel.x() + 270, player_panel.y() + 220),
                    'shape': [[1, 1, 1, 0], [0, 0, 1, 1]], 'colour': f'{player.color}'
                },
            ]
            for piece_data in pieces_data:
                image_label = pieces.Piece(
                    self, player.score_label, piece_data['image'], piece_data['initial_position'],
                    piece_data['weight'], self.boardLayout, self.pieceList, piece_data['shape'], piece_data['colour'],
                    player
                )
                self.pieceList.append(image_label)
                player.pieces.append(image_label)

        # Make player 1's pieces movable since that's the first player
        for piece in self.playerList[0].pieces:
            piece.movable = True
            piece.set_color_overlay(Qt.transparent)

        # CREATE SAVE BUTTON
        save_button = button.createButton("rgb(224, 166, 181)", (300, 75), "Save game", "rgb(244, 195, 209)", "rgb(202, 123, 139)","25", parent=self)

        self.saveMenu = saveMenu(boardLayout=self.boardLayout, turn=self.turn,
                                 playerList=self.playerList,
                                 pieceList=self.pieceList, playerTypes=self.playerTypes, soundPlayer=self.soundPlayer)  # popup menu to choose save destination
        save_button.clicked.connect(self.saveMenu.show)

        line_layout.addWidget(exit_button)
        line_layout.addWidget(save_button)
        line_layout.addWidget(settingsButton)
        if self.playerTypes[1] == "Human":
            pass
        else:
            for i in range(self.aiMovesBeforeFirstMove+1):
                next_player_clicked(self.playerList,self.turn,self.boardLayout, False, self)

    def check_end_game(self):
            for player in self.playerList:
                placeablePieces = []
                placeablePieces = placeable_pieces(player)
                if not self.get_valid_moves(player, placeablePieces, self.boardLayout) == []:
                    return
            self.endGame()

    def get_valid_moves(self, player, placeablePieces, board):
        valid_moves = []

        if len(placeablePieces) != 0:
            for piece in placeablePieces:
                    for flip in range(0, 2):
                        for rotation in range(0, 4):
                            for row in range(0, 20):
                                for col in range(0, 20):
                                    if board.canPlacePiece(col, row, piece):
                                        value = board.getValue(col, row, piece)
                                        valid_moves.append((col, row, piece, value, rotation, flip))
                            piece.rotateShape()
                        piece.flipShape()
                

        return valid_moves

    def endGame(self):
        player_scores = {}  # Dictionary to store player scores
        for player in self.playerList:  # Assuming you have a list of player objects
            score = int(player.score_label.text())  # Implement this method in your player class
            player_scores[player.name] = score

        # Find the players with the highest score
        highest_score = max(player_scores.values())
        winners = [player for player, score in player_scores.items() if score == highest_score]
        
        # Show the win screen
        self.showWinScreen(winners, highest_score)

    def showWinScreen(self, winners, score):
        if len(winners) == 1:
            winner_message = f"Player {winners[0]} won with a score of {score}!"
        else:
            winner_message = f"It's a draw between {', '.join(winners)} with a score of {score}!"

        msg_box = QMessageBox()

        msg_box.setWindowTitle("End Game!")
        msg_box.setText(winner_message)
        msg_box.setGeometry(700, 300, 100, 100)
        msg_box.setStyleSheet("QMessageBox { border: 10px solid orange; }")
        msg_box.setFont(goldman(size=20))      

        
        msg_box.setStandardButtons(QMessageBox.NoButton)
        # Add custom buttons
        back_to_menu_button = msg_box.addButton("Back to Main Menu", QMessageBox.ActionRole)
        view_board_button = msg_box.addButton("View Board", QMessageBox.ActionRole)

        msg_box.exec_()
        # Check which button was clicked
        clicked_button = msg_box.clickedButton()
        if clicked_button == back_to_menu_button:
            self.on_exit_clicked()
            pass
        elif clicked_button == view_board_button:
            for player in self.playerList:
                player.is_turn = False
                for piece in player.pieces:
                    piece.movable = False
                    piece.set_color_overlay(Qt.gray)
            pass

    def rotate_piece(self):
        # Find the last pressed piece
        active_piece = None
        if self.last_pressed_piece is not None:
            active_piece = self.last_pressed_piece

        if active_piece == None:
            return
        # rotate shape and recreate pixmap
        rotated_shape = active_piece.rotateShape() #call function in the pieces class instead
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
        self.soundPlayer.play_sound()

    def flip_piece(self):
        # Find the last pressed piece
        active_piece = None
        if self.last_pressed_piece is not None:
            active_piece = self.last_pressed_piece

        if active_piece == None:
            return
        # flip shape and recreate pixmap
        rotated_shape = active_piece.flipShape() #call function in the pieces class instead
        rotated_pixmap = active_piece.pixmap.transformed(QTransform().scale(-1, 1))
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
        self.soundPlayer.play_sound()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:  # "ESC" key for exiting
            self.on_exit_clicked()
        elif key == Qt.Key_R:  # "R" key for rotation
            self.rotate_piece()
        elif key == Qt.Key_F:  # "F" key for rotation
            self.flip_piece()
        elif key == Qt.Key_P:  # "P" key for passing
            next_player_clicked(self.playerList, self.turn, self.boardLayout, True, self)
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            confirm_placement(self.boardLayout, self.playerList, self.turn, self)

    def loadGame(self, filename="File 2"):
        f = f"Save/{filename}/"
        with open(f"{f}saveTurn.pkl", "rb") as file:
            self.turn.turn.setText(pickle.load(file).turnText)
        with open(f"{f}saveBoard.pkl", "rb") as file:
            Board = pickle.load(file)

            # iterate through each square on the board. Is there any better way to do this?
            for i in range(20):
                for j in range(20):
                    self.boardLayout.tileList[i][j].tileColor = Board.tileList[i][j].tileColor
                    self.boardLayout.tileList[i][j].changeColour(Board.tileList[i][j].tileColor)
                    self.boardLayout.tileList[i][j].isTileEmpty = Board.tileList[i][j].isTileEmpty
                    # do we need to set x & y as well or they will be unchanged?

        with open(f"{f}savePieces.pkl", 'rb') as file:
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

        with open(f"{f}savePlayer.pkl", "rb") as file:
            # load the saved player data file
            playerData = pickle.load(file)

            # set the score label for each player
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

    def on_exit_clicked(self):
        #self.soundPlayer.play_sound()
        self.close()
        self.main_menu = game.MainWindow(self.soundPlayer)  # Create an instance of your main menu
        self.main_menu.show()

    def on_settings_button_press(self):
        self.settings_menu = game.settings_menu(self.soundPlayer, False)
        self.settings_menu.show()


class saveMenu(QWidget):
    def __init__(self, playerList, turn, boardLayout, pieceList, playerTypes, soundPlayer):
        super().__init__()

        self.playerList = playerList
        self.turn = turn
        self.boardLayout = boardLayout
        self.pieceList = pieceList
        self.playerTypes = playerTypes
        self.soundPlayer = soundPlayer

        self.setWindowTitle("Choose Saving Destination")
        self.setStyleSheet("background-color: rgb(139, 69, 19);")
        self.setGeometry(500, 200, 500, 500)

        # Button for each file
        self.file1_button = self.makeFileButton("File 1")
        self.file2_button = self.makeFileButton("File 2")
        self.file3_button = self.makeFileButton("File 3")
        self.file4_button = self.makeFileButton("File 4")
        self.file5_button = self.makeFileButton("File 5")

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(200, 50)
        self.cancel_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")
        # theButton.setEnabled(False)
        self.cancel_button.clicked.connect(self.close)

        # Buttons formatting
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file1_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file2_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file3_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file4_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file5_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

    def makeFileButton(self, filename):
        theButton = QPushButton(filename)
        theButton.setFixedSize(400, 100)
        theButton.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")
        # theButton.setEnabled(False)
        theButton.clicked.connect(lambda: self.check_existing_save(filename))
        return theButton

    def check_existing_save(self, filename):
        if len(os.listdir(f"Save/{filename}/")) > 1:  # there is a .DS_Store file so condition is >1
            save_msg = QMessageBox()
            save_msg.setWindowTitle("Older saved file existed!")
            save_msg.setText("Another saved file already existed. Overwrite the old file?")

            saveButton = save_msg.addButton("Save", save_msg.ActionRole)
            saveButton.clicked.connect(lambda: self.saveGame(filename))
            save_msg.addButton("Cancel", save_msg.RejectRole)
            # cancelButton.clicked.connect(self.close)
            save_msg.exec_()
        else:
            self.saveGame(filename)

    def saveGame(self, filename):
        self.close()
        f = f"Save/{filename}/"
        with open(f"{f}savePlayer.pkl", 'wb') as file:
            pickle.dump(self.playerList, file)
        with open(f"{f}saveTurn.pkl", 'wb') as file:
            pickle.dump(self.turn, file)
        with open(f"{f}saveBoard.pkl", 'wb') as file:
            pickle.dump(self.boardLayout, file)
        with open(f"{f}savePieces.pkl", 'wb') as file:
            pickle.dump(self.pieceList, file)
        with open(f"{f}savePlayerTypes.pkl", 'wb') as file:
            pickle.dump(self.playerTypes, file)
        soundSettings = {'volume': self.soundPlayer.volume}
        with open(f"{f}saveSound.pkl", 'wb') as file:
            pickle.dump(soundSettings, file)
        # another messagebox saying the game was saved successfully
        msg = QMessageBox()
        msg.setWindowTitle("Save Success")
        msg.setText(f"Game saved successfully to {filename}")
        msg.exec_()


def startGame():
    app = QApplication(sys.argv)
    window = gameInterface()
    window.show()
    window.showFullScreen()
    # window.showMaximized()
    sys.exit(app.exec_())

