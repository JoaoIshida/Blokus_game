import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import gameInterface
import game

class playerCountButton(QPushButton):
    def __init__(self, playerCount, buttonGrid, selected):
        super().__init__(playerCount)  
        self.buttonGrid = buttonGrid
        self.playerCount = playerCount
        self.setText = playerCount
        self.selected = selected
        self.setFixedSize(80, 80)
        self.clicked.connect(self.toggleSelection)
        self.updateColor()

    def toggleSelection(self):
        self.buttonGrid.deselectAllButtons()
        self.selected = True
        self.updateColor()
        self.buttonGrid.updatePlayerMenus(self.playerCount)

    def updateColor(self):
        color = "green" if self.selected else "rgb(220,220,220)"
        self.setStyleSheet(f"border-radius: 25px; background-color: {color};")

class playerCount(QFrame):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)
        self.setFixedSize(300,300)
        self.setStyleSheet("background-color: rgb(112,128,144); border: 3px solid black;")
        textLabel = QLabel("Choose the number of players")
        textLabel.setFixedSize(275, 70)
        textLabel.setFont(QFont('Arial', 14))
        textLabel.setStyleSheet("background-color: rgb(220,220,220); border: 3px solid black; border-radius: 5px;")
        gridLayout.addWidget(textLabel, 0, 0, 1, 3)
        self.buttons = []
        for i in range(2,5):
            if i == 4:
                self.buttons.append(playerCountButton(str(i), self, True))
            else:
                self.buttons.append(playerCountButton(str(i), self, False))
        
        for i in range(3):
                button = self.buttons[i]
                gridLayout.addWidget(button, 1, i, Qt.AlignCenter)

    def deselectAllButtons(self):
        for button in self.buttons:
            button.selected = False
            button.updateColor()

    def updatePlayerMenus(self, count):
        self.mainWindow.updatePlayerMenus(count)

class playerMenu(QFrame):
    playerTypeChanged = pyqtSignal(str)
    def __init__(self, colour, playerCount, playerNumber):
        super().__init__()
        self.setStyleSheet(f"background-color: {colour}; border: 3px solid black;")
        self.setFixedSize(300, 300)

        self.playerCount = playerCount
        self.playerNumber = playerNumber  # Store player number
        layout = QGridLayout(self)
        self.setLayout(layout)

        # Add a label to the layout
        label = QLabel(f"Player {playerNumber}")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont('Arial', 18, QFont.Bold))
        label.setFixedSize(200, 50)
        layout.addWidget(label, 0, 0)

        # Add a dropdown (QComboBox) for choosing AI or Player
        self.dropdown = QComboBox()
        self.dropdown.setFixedSize(200, 50)
        self.dropdown.setFont(QFont('Arial', 14))
        self.dropdown.addItem("Player")
        self.dropdown.addItem("AI")
        self.dropdown.currentTextChanged.connect(self.updatePlayerType)
        layout.addWidget(self.dropdown, 1, 0,alignment=Qt.AlignCenter)

    def updatePlayerType(self, value):
        self.playerTypeChanged.emit(value)

class rules(QWidget):
    def __init__(self):
        super().__init__()
        self.playerTypes = {}
        self.playerCount = 4
        self.setWindowTitle("Choose Saving Destination")
        self.setStyleSheet("background-color: rgb(196, 59, 93);")
        self.setGeometry(100, 50, 700, 600)

        self.layout = QGridLayout(self)

        colours = ["rgb(240,128,128)", "green", "yellow", "rgb(70,130,180)"]
        positons = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        self.playerMenus = []

        for i in range(4):
            self.playerTypes[i+1] = "Player"
            menu = playerMenu(colours[i], i+1, i+1)
            menu.playerTypeChanged.connect(self.storePlayerType)
            self.playerMenus.append(menu)
            self.layout.addWidget(menu, positons[i][0], positons[i][1])

        backButton = QPushButton("Back to Main Menu")
        backButton.setFixedSize(300, 100)
        backButton.setStyleSheet(
            "QPushButton {"
            "   font-size: 24px; padding: 10px;"
            "   color: black; background-color: rgb(224, 166, 181);"
            "   border: 3px solid black; border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: rgb(244, 195, 209);"
            "}"
            "QPushButton:pressed {"
            "   background-color: rgb(202, 123, 139);"
            "}")

        startButton = QPushButton("Start Game")
        startButton.setFixedSize(300, 100)
        startButton.setStyleSheet(
            "QPushButton {"
            "   font-size: 24px; padding: 10px;"
            "   color: black; background-color: rgb(224, 166, 181);"
            "   border: 3px solid black; border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: rgb(244, 195, 209);"
            "}"
            "QPushButton:pressed {"
            "   background-color: rgb(202, 123, 139);"
            "}")

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(backButton)

        self.layout.addLayout(buttonLayout, 1, 2, alignment=Qt.AlignCenter)
        startButton.clicked.connect(self.startGame)
        backButton.clicked.connect(self.backtoMenu)

        playerCountMenu = playerCount(self)
        self.layout.addWidget(playerCountMenu, 0, 2, 1, 2, alignment=Qt.AlignCenter)
        

    def updatePlayerMenus(self, playerCount):
        self.playerCount = playerCount
        for i, playerMenu in enumerate(self.playerMenus):
            playerMenu.setHidden(i >= int(playerCount))

    def storePlayerType(self, playerType):
        playerNumber = self.sender().playerNumber
        self.playerTypes[playerNumber] = playerType

    def gameSettings(self):
        return self.playerCount, self.playerTypes

    def startGame(self):
        self.close()
        self.game = gameInterface.gameInterface()
        self.game.showFullScreen()
        self.game.setFocus(Qt.OtherFocusReason)

    def backtoMenu(self):
        self.close()
        self.mainMenu = game.MainWindow()
        self.mainMenu.show()
        self.mainMenu.setFocus(Qt.OtherFocusReason)