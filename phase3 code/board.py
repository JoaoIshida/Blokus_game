import sys
import math
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Tile Class
class tile(QFrame):
    # Sets the initial state of the tile
    def __init__(self, x ,y, value):
        super().__init__()
        self.x = x
        self.y = y
        self.value = value
        self.isTileEmpty = True
        self.tileColor = 'white'
        self.setStyleSheet(f"background-color: white; border: 1px solid black;")
    
    # Checks if the tile is empty
    def isEmpty(self):
        return self.isTileEmpty

    def changeState(self):
        self.isTileEmpty = False

    def tilePosition(self):
        return self.x, self.y
    
    def changeColour(self, color):
        self.tileColor = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.isTileEmpty = False

    def __getstate__(self):
        d = self.__dict__
        self_dict = {'x': d['x'], 'y': d['y'],'isTileEmpty': d['isTileEmpty'], 'tileColor': d['tileColor']}
        return self_dict

    def __setstate__(self, state):
        self.__dict__ = state

# Game Window
class Board(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tileSize = 28
        self.setWindowTitle("Blokus")
        self.centralWidget = QWidget()
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
                # Calculate the value of the tiles. Increased in value as the tile is closer to the center
                center = 10
                distance_to_center = math.sqrt((row - center)**2 + (col - center)**2)
                max_distance = math.sqrt((0 - center)**2 + (0 - center)**2)
                value = int(100 * (1 - (distance_to_center / max_distance)**2))

                # Creates a tile with the given row and column then adds the tile to the board
                tileObject = tile(row,col,value)
                # Creates a tile with the given row and column then adds the tile to the board
                self.tileList[row].append(tileObject)
                self.gridLayout.addWidget(tileObject, row+1, col+1)

    def inBounds(self, x, y):
        return 0 <= x < 20 and 0 <= y < 20

    def checkInCorner(self , x , y):
        if x == 0 and y == 0:
            return True
        elif x == 0 and y == 19:
            return True
        elif x == 19 and y == 0:
            return True
        elif x == 19 and y == 19:
            return True
        else:
            return False

    def canPlacePiece(self, tileX, tileY, piece):
        pieceHeight = len(piece.shape)
        pieceWidth = len(piece.shape[0])
        piece_colour = piece.colour
        inCorner = False
        # Check if the piece is within the bounds of the board
        if not (0 <= tileX < 20 and 0 <= tileY < 20):
            return False
        
        if piece.player.first_move:
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if self.checkInCorner(tileX + col, tileY + row) == True and piece.shape[row][col] == 1:
                        inCorner = True
                    if self.inBounds(tileX + col, tileY + row) == False or self.tileList[tileY + row][tileX + col].isEmpty() == False:
                        return False
            if inCorner == True:
                return True
            else:
                return False
        else:
            sameColourCorner = False
            
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if piece.shape[row][col] == 1:
                        if self.inBounds(tileX + col, tileY + row) == False or self.tileList[tileY + row][tileX + col].isEmpty() == False:
                            return False
                    
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if piece.shape[row][col] == 1:
                        x, y = tileX + col, tileY + row

                        # Check if the piece is within the bounds of the board
                        if not (0 <= x < 20 and 0 <= y < 20):
                            return False

                        if not self.tileList[y][x].isEmpty():
                            return False

                        # Check if any corner tiles are filled
                        cornerTiles = [(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)]
                        for cornerX, cornerY in cornerTiles:
                            if self.inBounds(cornerX, cornerY) and not self.tileList[cornerY][cornerX].isEmpty() and self.tileList[cornerY][cornerX].tileColor == piece_colour:
                                sameColourCorner = True
                                break

                        if sameColourCorner:
                            break
                if sameColourCorner:
                    break
            if not sameColourCorner:
                return False

            # Check if any side tiles are filled
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if piece.shape[row][col] == 1:
                        x, y = tileX + col, tileY + row

                        # Check if the piece is within the bounds of the board
                        if not self.inBounds(x, y):
                            return False
                        
                        sideTiles = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                        for sideX, sideY in sideTiles:
                            if self.inBounds(sideX, sideY) and not self.tileList[sideY][sideX].isEmpty() and self.tileList[sideY][sideX].tileColor == piece_colour:
                                return False
            return True
        
    def check_collision(self, piece):
        startX = int((piece.new_position.x() - self.x() + self.tileSize // 2) / self.tileSize)
        startY = int((piece.new_position.y() - self.y() + self.tileSize // 2) / self.tileSize)

        numTilesX = self.width() // self.tileSize
        numTilesY = self.height() // self.tileSize

        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                    tile_x = startX + col
                    tile_y = startY + row

                    if not (0 <= tile_x < numTilesX and 0 <= tile_y < numTilesY):
                        # Piece is out of bounds of the board
                        return True

                    if not self.tileList[tile_y][tile_x].isEmpty():
                        # There's already a colored tile on the board at the same position
                        return True

        return False

    def getValue(self, x , y, piece):
        pieceHeight = len(piece.shape)
        pieceWidth = len(piece.shape[0])
        value = 0
        if self.canPlacePiece(x, y, piece) == True:
            for row in range(pieceHeight):
                for col in range(pieceWidth):
                    if piece.shape[row][col] == 1:
                        value += self.tileList[y + row][x + col].value
        return value

    def __getstate__(self):
        d = self.__dict__
        self_dict = {'tileList': d['tileList']}
        return self_dict

    def __setstate__(self, state):
        self.__dict__ = state