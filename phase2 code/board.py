from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Tile Class
class tile(QFrame):
    # Sets the initial state of the tile
    def __init__(self, x ,y):
        super().__init__()
        self.x = x
        self.y = y
        self.isTileEmpty = True
        self.setStyleSheet(f"background-color: white; border: 1px solid black;")

    # Checks if the tile is empty
    def isEmpty(self):
        return self.isTileEmpty

# Game Window
class Board(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blokus")
        self.centralWidget = QWidget()

        # Configure the Layout of Board
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.centralWidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralWidget)

        # Create the board
        self.initBoard()

    # Create a 20x20 board with each tile being a QFrame
    def initBoard(self):
        for row in range(20):
            for col in range(20):
                # Creates a tile with the given row and column then adds the tile to the board
                self.gridLayout.addWidget(tile(row, col), row+1, col+1)


