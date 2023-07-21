import sys
from PyQt5 import QtGui
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

    def changeState(self):
        self.isTileEmpty = False

    def tilePosition(self):
        return self.x, self.y
    
    def changeColour(self):
        self.setStyleSheet(f"background-color: red; border: 1px solid black;")
    

# Game Window
class Board(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tileSize = 28
        self.setWindowTitle("Blokus")
        self.centralWidget = QWidget()
        self.firstMove = True
        self.tileList = [[]]
        # Configure the Layout of Board
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.centralWidget.setLayout(self.gridLayout)
        self.setCentralWidget(self.centralWidget)

        # # Create the board
        self.initBoard()

    # Create a 20x20 board with each tile being a QFrame
    def initBoard(self):
        for _ in range(20):
            self.tileList.append([])
            
        for row in range(20):
            for col in range(20):
                # Creates a tile with the given row and column then adds the tile to the board
                tileObject = tile(row,col)
                self.tileList[row].append(tileObject)
                self.gridLayout.addWidget(tileObject, row+1, col+1)

    def inBounds(self, x, y):
        return 0 <= x < 20 and 0 <= y < 20

    def canPlacePiece(self, pieceShape, tileX, tileY):
        pieceHeight = len(pieceShape)
        pieceWidth = len(pieceShape[0])

        # Check if the piece is within the bounds of the board
        if not (0 <= tileX < 20 and 0 <= tileY < 20):
            return False

        if self.firstMove:
            return True
        else:
            cornerTouching = False  # Initialize a variable to track if there is any corner touching

            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if pieceShape[row][col] == 1:
                        x, y = tileX + col, tileY + row

                        # Check if the piece is within the bounds of the board
                        if not (0 <= x < 20 and 0 <= y < 20):
                            return False

                        if not self.tileList[y][x].isEmpty():
                            return False

                        # Check if any corner tiles are filled
                        cornerTiles = [(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)]
                        for cornerX, cornerY in cornerTiles:
                            if self.inBounds(cornerX, cornerY) and not self.tileList[cornerY][cornerX].isEmpty():
                                cornerTouching = True
                                break
                        if cornerTouching:
                            break
                if cornerTouching:
                    break
            if not cornerTouching:
                return False

            # Check if any side tiles are filled
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if pieceShape[row][col] == 1:
                        x, y = tileX + col, tileY + row

                        # Check if the piece is within the bounds of the board
                        if not (0 <= x < 20 and 0 <= y < 20):
                            return False
                        
                        sideTiles = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                        for sideX, sideY in sideTiles:
                            if self.inBounds(sideX, sideY) and not self.tileList[sideY][sideX].isEmpty():
                                return False
            return True

