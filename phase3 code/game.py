import sys
import os
from PyQt5.QtGui import QPixmap
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QMessageBox
import gameInterface
from pieces import *

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

class MainWindow(QMainWindow):
    achievements_file = "achievements.pkl"

    # Load achievements from file or set default values
    if os.path.exists(achievements_file):
        with open(achievements_file, "rb") as f:
            achievements = pickle.load(f)
    else:
        achievements = {
            "FirstBlood": False,
            "Peace Agreement": False,
            "Philo-Blokus": False
        }

    def show_achievement_message(self, achievement_name):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Achievement Unlocked!")
        msg.setText(f"You've unlocked the {achievement_name} achievement!")
        msg.exec_()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blokus")
        self.setGeometry(100, 50, 900, 900)
        self.setStyleSheet("background-color: rgb(196, 59, 93);")

        self.widget = QWidget()

        self.logo = QLabel(self)
        self.logo_pixmap = QPixmap('assets/Blokus.png')
        self.logo.setPixmap(self.logo_pixmap)
        self.logo.setAlignment(Qt.AlignCenter)

        self.newGame_button = QPushButton("NEW GAME")
        self.newGame_button.setFixedSize(400, 100)
        self.newGame_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")

        self.load_button = QPushButton("LOAD GAME")
        self.load_button.setFixedSize(400, 100)
        self.load_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")
        # self.load_button.setStyleSheet(
        #     "font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
        # self.load_button.setEnabled(False)

        self.tutorial_button = QPushButton("TUTORIAL (WIP)")
        self.tutorial_button.setFixedSize(400, 100)
        self.tutorial_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
        self.tutorial_button.setEnabled(False)

        self.achievement_button = QPushButton("ACHIEVEMENT")
        self.achievement_button.setFixedSize(400, 100)
        self.achievement_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")

        self.layout_container = QHBoxLayout()
        self.widget.setLayout(self.layout_container)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.newGame_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.load_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.tutorial_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.achievement_button, alignment=Qt.AlignCenter)

        self.newGame_button.clicked.connect(self.on_newGame_button_press)
        self.load_button.clicked.connect(self.on_loadGame_button_press)
        self.achievement_button.clicked.connect(self.on_achievement_button_press)

        self.layout_container.addLayout(self.layout)
        self.setCentralWidget(self.widget)

    def on_newGame_button_press(self):
        self.newGame_button.setText("You already clicked me.")
        self.newGame_button.setEnabled(False)
        self.newGame_button.setVisible(False)
        self.clearLayout(layout=self.layout_container)
        self.startGame()
        # self.setStyleSheet("background-color: rgb(139, 69, 19);")
        # self.showFullScreen()
        if not MainWindow.achievements["FirstBlood"]:
            MainWindow.achievements["FirstBlood"] = True
            self.save_achievements()
            self.show_achievement_message("FirstBlood")
    def on_loadGame_button_press(self):
        #open a new window to choose the file
        self.loadMenu = loadMenu()
        self.close()
        self.loadMenu.show()
        if not MainWindow.achievements["Peace Agreement"]:
            MainWindow.achievements["Peace Agreement"] = True
            self.save_achievements()
            self.show_achievement_message("Peace Agreement")

    def on_achievement_button_press(self):
        self.achievementMenu = achievementMenu(MainWindow.achievements)
        self.close()
        self.achievementMenu.show()

    def save_achievements(self):
        with open(MainWindow.achievements_file, "wb") as f:
            pickle.dump(MainWindow.achievements, f)

    # It just starts a new game and overwrite with the data from the saved files
    def load_chosen_file(self, filename):
        self.on_newGame_button_press()
        self.game.loadGame(filename)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def startGame(self):
        self.close()
        self.game = gameInterface.gameInterface()
        self.game.showFullScreen()
        self.game.setFocus(Qt.OtherFocusReason)

class achievementMenu(QWidget):
    def __init__(self, achievements):
        super().__init__()
        self.achievements = achievements


        self.setWindowTitle("Achievements")
        self.setStyleSheet("background-color: rgb(196, 59, 93);")
        self.setGeometry(100, 50, 900, 900)

        # Button for each achievement
        self.achievement1_button = self.makeAchievementButton("FirstBlood")
        self.achievement2_button = self.makeAchievementButton("Peace Agreement")
        self.achievement3_button = self.makeAchievementButton("Philo-Blokus")
        self.achievement4_button = self.makeAchievementButton("Artificial Infant")
        self.achievement5_button = self.makeAchievementButton("The Terminator")

        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(200, 50)
        self.back_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")

        self.back_button.clicked.connect(self.go_back_main_menu)

        # Buttons formatting
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.achievement1_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.achievement2_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.achievement3_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.achievement4_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.achievement5_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

    def makeAchievementButton(self, achievement):
        theButton = QPushButton(achievement)
        theButton.setFixedSize(400, 100)
        # Check if the achievement is unlocked and change the button style accordingly
        if self.achievements.get(achievement, False):
            theButton.setStyleSheet(
                "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")
        else:
            theButton.setStyleSheet("font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
        return theButton

    def go_back_main_menu(self):
        self.close()
        self.mainMenu = MainWindow()
        self.mainMenu.show()
class loadMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Choose Saving Destination")
        self.setStyleSheet("background-color: rgb(196, 59, 93);")
        # self.setGeometry(500, 200, 500, 500)
        self.setGeometry(100, 50, 900, 900)

        #Button for each file
        self.file1_button = self.makeFileButton("File 1")
        self.file2_button = self.makeFileButton("File 2")
        self.file3_button = self.makeFileButton("File 3")
        self.file4_button = self.makeFileButton("File 4")
        self.file5_button = self.makeFileButton("File 5")

        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(200, 50)
        self.back_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")

        self.back_button.clicked.connect(self.go_back_main_menu)
        #Buttons formatting
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file1_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file2_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file3_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file4_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.file5_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

    def makeFileButton(self, filename):
        theButton = QPushButton(filename)
        theButton.setFixedSize(400, 100)
        if len(os.listdir(f"Save/{filename}/")) < 2:
            theButton.setStyleSheet(
                "font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
            theButton.setEnabled(False)
        else:
            theButton.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")
            theButton.clicked.connect(lambda: self.load_the_file(filename))
        return theButton


    def load_the_file(self, filename):
        # Start new game
        self.close()
        # self.destroy()
        self.startGame()
        self.game.loadGame(filename)

    def go_back_main_menu(self):
        self.close()
        self.mainMenu = MainWindow()
        self.mainMenu.show()

    def startGame(self):
        self.game = gameInterface.gameInterface()
        self.game.showFullScreen()
        self.game.setFocus(Qt.OtherFocusReason)

def draw_menu():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    draw_menu()
