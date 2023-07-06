import sys
from board import Board
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QPainter, QBitmap, QImage, QColor
from PyQt5.QtCore import Qt, QPoint

# PLAYER CLASS
class Player:
    def __init__(self, score_label, is_ai=False, is_turn = False, name = "Player"):
        self.score_label = score_label #SCORE FOR TOTAL
        self.pieces = [] #SAVES PLAYER PIECES
        self.is_ai = is_ai
        self.is_turn = is_turn
        self.name = name
        
class Turn:
    def __init__(self, turn):
        self.turn = turn
        # self.turn = parent.name


class DraggableLabel(QLabel):
    def __init__(self, parent, score_label, pixmap_path, initial_position, weight, Layout, pieces):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path) #PIXMAP IS SO THAT THE PYQT CAN IDENTIFY THE COLORED PART OF THE PIECES
        self.setPixmap(self.pixmap)        # LIKE THE L OR T SHAPED
        self.setAlignment(Qt.AlignCenter)
        self.Layout = Layout
        self.pieces = pieces
        self.dragging = False
        self.offset = QPoint()
        self.score_label = score_label
        self.initial_position = initial_position
        self.onboard = False
        self.weight = weight

        self.last_confirmed_position = self.initial_position
        self.new_position = None

        self.move(self.initial_position)

        # Create a mask from the alpha channel of the image
        mask = QBitmap(self.pixmap.createMaskFromColor(Qt.transparent))
        self.setMask(mask)

    def set_size_by_percentage(self, percentage):
        original_size = self.pixmap.size()
        new_width = int(original_size.width() * percentage)
        new_height = int(original_size.height() * percentage)
        self.setFixedSize(new_width, new_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.onboard:  # Only allow dragging if the piece is not on the board
                self.dragging = True #IF PIECE IS ON THE BOARD, THE PIECE IS NOT DRAGGED ANYMORE
                self.offset = event.pos()
            else:
                self.dragging = False
                self.move(self.last_confirmed_position)  # Move the piece back to the last confirmed position

    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = event.windowPos().toPoint()
            new_pos = current_pos - self.offset

            new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))

            self.move(new_pos)

            # Check if the move is possible and update the color overlay accordingly
            if self.geometry().intersects(self.Layout.geometry()) and not self.check_collision(self.pieces):
                self.set_color_overlay(Qt.green) #MEANS THAT THE PIECE CAN BE PLACED AND COUNTS THE POINTS
            else:
                self.set_color_overlay(Qt.red) #PIECE CANNOT BE PLACED

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            if not self.onboard and self.geometry().intersects(self.Layout.geometry()) and not self.check_collision(self.pieces):
                # Store the new position but don't confirm it yet
                self.new_position = self.pos()
            # After dropping the piece, reset the color overlay to transparent
            self.set_color_overlay(Qt.transparent)
    #OVERLAY FOR THE GREEN AND RED
    def set_color_overlay(self, color):
        overlay_pixmap = QPixmap(self.pixmap.size())
        overlay_pixmap.fill(Qt.transparent)
        painter = QPainter(overlay_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.fillRect(overlay_pixmap.rect(), color)
        painter.end()

        self.setPixmap(overlay_pixmap)

    #SELF EXPLANATORY
    def check_collision(self, pieces):
        for piece in pieces:
            if piece != self and piece.onboard and self.pixel_collision(piece):
                return True
        return False

    def pixel_collision(self, other_piece):
        # Convert the pieces' pixmaps to QImages for pixel-level collision check
        image1 = self.pixmap.toImage()
        image2 = other_piece.pixmap.toImage()

        # Calculate the intersection area between the pieces' geometries
        intersection = self.geometry().intersected(other_piece.geometry())

        # Iterate over the pixels within the intersection area
        for x in range(intersection.x(), intersection.x() + intersection.width()):
            for y in range(intersection.y(), intersection.y() + intersection.height()):
                # Calculate the corresponding positions within the images
                img1_x = x - self.geometry().x()
                img1_y = y - self.geometry().y()
                img2_x = x - other_piece.geometry().x()
                img2_y = y - other_piece.geometry().y()

                # Check if the corresponding pixels are both opaque
                if image1.pixelColor(img1_x, img1_y).alpha() > 0 and image2.pixelColor(img2_x, img2_y).alpha() > 0:
                    return True

        return False

#EXIT BUTTON (OPTIONAL)
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
    pieces = []
    players = []
    window = QWidget()
    window.setWindowTitle("Game")
    window.setGeometry(100, 50, 900, 900)
    window.setStyleSheet("background-color: rgb(139, 69, 19);")

    layout = QVBoxLayout(window)

    exit_button = QPushButton('Exit', window)
    exit_button.clicked.connect(on_exit_clicked)

    pass_button = QPushButton('Pass', window)
    pass_button.clicked.connect(lambda: next_player_clicked(players, turn))

    confirm_button = QPushButton('Confirm', window)
    confirm_button.clicked.connect(lambda: confirm_placement(pieces))
    confirm_button.clicked.connect(lambda: next_player_clicked(players, turn))
    layout.addWidget(confirm_button)

    boardLayout = Board()
    boardLayout.setFixedSize(560, 560)
    boardLayout.setStyleSheet("background-color: rgb(255, 255, 255);")
    # Show whose turn is it
    player_text = QLabel("Player 1", window)
    turn = Turn(player_text)

    layout.addWidget(exit_button)
    layout.addWidget(pass_button)
    layout.addWidget(boardLayout)

    # Player 1 - RED
    score_label1 = QLabel("0")
    score_label1.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label1.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(255, 0, 0);")
    layout.addWidget(score_label1)

    player1 = Player(score_label1, is_turn = True, name = "Player 1")

    # Player 2 - GREEN
    score_label2 = QLabel("0")
    score_label2.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label2.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(0, 255, 0);")
    layout.addWidget(score_label2)

    player2 = Player(score_label2, is_ai=True, name = "AI")

    # Player 3 - BLUE
    score_label3 = QLabel("0")
    score_label3.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label3.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(0, 0, 255);")
    layout.addWidget(score_label3)

    player3 = Player(score_label3, name = "Player 3")

    # Player 4 - YELLOW
    score_label4 = QLabel("0")
    score_label4.setAlignment(Qt.AlignRight | Qt.AlignTop)
    score_label4.setStyleSheet(
        "font-size: 24px; padding: 10px; color: black; background-color: rgb(255, 255, 0);")
    layout.addWidget(score_label4)

    player4 = Player(score_label4, name = "Player 4")

    players.append(player1)
    players.append(player2)
    players.append(player3)
    players.append(player4)

    layout.addWidget(player_text)


    # Player 1's Pieces - RED
    initial_position1 = QPoint(200, score_label1.height() + 250)
    image_label1 = DraggableLabel(window, player1.score_label, 'assets/X5.png', initial_position1, 5, boardLayout, pieces)
    image_label1.setScaledContents(True)
    image_label1.set_size_by_percentage(1)
    pieces.append(image_label1)

    # Player 2's Pieces - GREEN
    initial_position2 = QPoint(200, score_label2.height() + 150)
    image_label2 = DraggableLabel(window, player2.score_label, 'assets/L5.png', initial_position2, 5, boardLayout, pieces)
    image_label2.setScaledContents(True)
    image_label2.set_size_by_percentage(1)
    pieces.append(image_label2)

    # Player 3's Pieces - BLUE
    initial_position3 = QPoint(50, score_label3.height() + 150)
    image_label3 = DraggableLabel(window, player3.score_label, 'assets/Z5.png', initial_position3, 2, boardLayout, pieces)
    image_label3.setScaledContents(True)
    image_label3.set_size_by_percentage(1)
    pieces.append(image_label3)

    # Player 4's Pieces -YELLOW
    initial_position4 = QPoint(50, score_label4.height() + 250)
    image_label4 = DraggableLabel(window, player4.score_label, '../assets/Y5.png', initial_position4, 4, boardLayout, pieces)
    image_label4.setScaledContents(True)
    image_label4.set_size_by_percentage(1)
    pieces.append(image_label4)

    initial_position4 = QPoint(350, score_label4.height() + 250)
    image_label4 = DraggableLabel(window, player4.score_label, 'assets/Y5.png', initial_position4, 4, boardLayout, pieces)
    image_label4.setScaledContents(True)
    image_label4.set_size_by_percentage(1)
    pieces.append(image_label4)

    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    startGame()
