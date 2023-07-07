import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from gameInterface import gameInterface
from pieces import *

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blokus")
        self.setFixedSize(900, 900)

        self.widget = QWidget()

        self.logo = QLabel(self)
        self.logo_pixmap = QPixmap('assets/Blokus.png')
        self.logo.setPixmap(self.logo_pixmap)
        self.logo.setAlignment(Qt.AlignCenter)

        self.newGame_button = QPushButton("NEW GAME")
        self.newGame_button.setFixedSize(400, 100)
        self.newGame_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: black; background-color: rgb(224, 166, 181);")

        self.load_button = QPushButton("LOAD GAME (WIP)")
        self.load_button.setFixedSize(400, 100)
        self.load_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
        self.load_button.setEnabled(False)

        self.tutorial_button = QPushButton("TUTORIAL (WIP)")
        self.tutorial_button.setFixedSize(400, 100)
        self.tutorial_button.setStyleSheet(
            "font-size: 24px; padding: 10px; color: white; background-color: rgb(102, 73, 81);")
        self.tutorial_button.setEnabled(False)

        self.layout_container = QHBoxLayout()
        self.widget.setLayout(self.layout_container)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.newGame_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.load_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.tutorial_button, alignment=Qt.AlignCenter)

        self.newGame_button.clicked.connect(self.on_newGame_button_press)

        self.layout_container.addLayout(self.layout)
        self.setCentralWidget(self.widget)

    def on_newGame_button_press(self):
        self.newGame_button.setText("You already clicked me.")
        self.newGame_button.setEnabled(False)
        self.newGame_button.setVisible(False)
        self.clearLayout(layout=self.layout_container)
        self.startGame()
        self.setStyleSheet("background-color: rgb(139, 69, 19);")

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
        self.game = gameInterface()
        self.setCentralWidget(self.game)


def draw_menu():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet("background-color: rgb(196, 59, 93);")
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    draw_menu()
