import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import button
import gameInterface
import game

class playerMenu(QFrame):
    playerTypeChanged = pyqtSignal(str)
    def __init__(self, colour, playerNumber):
        super().__init__()
        self.setStyleSheet(f"background-color: {colour}; border: 3px solid black;")
        self.setFixedSize(300, 300)

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
        self.dropdown.addItem("Human")
        self.dropdown.addItem("AI")
        self.dropdown.currentTextChanged.connect(self.updatePlayerType)
        layout.addWidget(self.dropdown, 1, 0,alignment=Qt.AlignCenter)

    def updatePlayerType(self, value):
        self.playerTypeChanged.emit(value)

class rules(QWidget):
    def __init__(self, soundPlayer):
        super().__init__()
        self.playerTypes = {}
        self.soundPlayer = soundPlayer
        self.setWindowTitle("Choose Saving Destination")
        self.setStyleSheet("background-color: rgb(196, 59, 93);")
        self.setGeometry(100, 50, 700, 600)

        self.layout = QGridLayout(self)

        colours = ["rgb(240,128,128)", "green", "rgb(70,130,180)", "yellow"]
        positons = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        self.playerMenus = []

        for i in range(4):
            self.playerTypes[i+1] = "Human"
            menu = playerMenu(colours[i], i+1)
            menu.playerTypeChanged.connect(self.storePlayerType)
            self.playerMenus.append(menu)
            self.layout.addWidget(menu, positons[i][0], positons[i][1])

        backButton = button.createButton(("rgb(224, 166, 181)","rgb(244, 195, 209)", "rgb(202, 123, 139)"), (300, 100), "Back","25")

        startButton = button.createButton(("rgb(224, 166, 181)","rgb(244, 195, 209)", "rgb(202, 123, 139)"), (300, 100), "Start","25")

        textHint = QLabel("Choose the type of player,\n one colour must be human")
        textHint.setFixedSize(300, 100)
        textHint.setAlignment(Qt.AlignCenter)
        textHint.setStyleSheet("border: 3px solid black;")
        textHint.setFont(QFont('Arial', 16, QFont.Bold))
        
        self.layout.addWidget(textHint, 0,2)
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(backButton)

        self.layout.addLayout(buttonLayout, 1, 2)
        startButton.clicked.connect(self.startGame)
        backButton.clicked.connect(self.backtoMenu)

    def storePlayerType(self, playerType):
        playerNumber = self.sender().playerNumber
        self.playerTypes[playerNumber] = playerType

    def gameSettings(self):
        return self.playerTypes

    def startGame(self):
        humanPlayers = 0
        for playerNumber, playerType in self.playerTypes.items():
            if playerType == "Human":
                humanPlayers += 1

        if humanPlayers == 0:
            return
    
        self.close()
        self.game = gameInterface.gameInterface(self.playerTypes, self.soundPlayer)
        self.game.showFullScreen()
        self.game.setFocus(Qt.OtherFocusReason)

        if not game.MainWindow.achievements["FirstBlood"]:
            game.MainWindow.achievements["FirstBlood"] = True
            game.MainWindow.save_achievements(game.MainWindow)
            game.MainWindow.show_achievement_message(game.MainWindow, "FirstBlood")

    def backtoMenu(self):
        self.close()
        self.mainMenu = game.MainWindow(self.soundPlayer)
        self.mainMenu.show()
        self.mainMenu.setFocus(Qt.OtherFocusReason)