from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

def createButton(colour, size, text, hoverColour, pressColour, borderRadius, parent=None):
    button = QPushButton(parent)
    button.setText(text)
    button.setFixedSize(size[0],size[1])
    button.setStyleSheet(
        f"QPushButton {{"
        f"   font-size: 24px; padding: 10px;"
        f"   color: black; background-color: {colour};"
        f"   border: 3px solid black; border-radius: {borderRadius}px;"
        f"}}"
        f"QPushButton:hover {{"
        f"   background-color: {hoverColour};"
        f"}}"
        f"QPushButton:pressed {{"
        f"   background-color: {pressColour};"
        f"}}")
    
    return button
    