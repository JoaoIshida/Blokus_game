from PyQt5.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys

class TutorialWizard(QWizardPage):
    def __init__(self, pageNum, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tut = QLabel(self)
        self.tut_pixmap = QPixmap(f"Tutorial/{pageNum}.png")
        self.tut_pixmap = self.tut_pixmap.scaledToWidth(850)
        self.tut.setPixmap(self.tut_pixmap)
        self.tut.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.tut)

class Wizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutorial")
        self.setGeometry(100, 50, 1000, 800)
        self.pageOne = TutorialWizard("One")
        self.pageTwo = TutorialWizard("Two")
        self.pageThree = TutorialWizard("Three")
        self.pageFour = TutorialWizard("Four")
        self.pageFive = TutorialWizard("Five")

        self.addPage(self.pageOne)
        self.addPage(self.pageTwo)
        self.addPage(self.pageThree)
        self.addPage(self.pageFour)
        self.addPage(self.pageFive)

        # self.addPage(Page1())
        # self.addPage(Page2())
        # self.addPage(Page3())
        # self.addPage(Page4())

        self.setWizardStyle(QWizard.ClassicStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage)
        self.setOption(QWizard.NoCancelButton, False)
        self.setOption(QWizard.CancelButtonOnLeft)

        self.setButtonText(QWizard.CancelButton, "Skip")
        self.setButtonText(QWizard.NextButton, "Next >")
        self.setButtonText(QWizard.BackButton, "< Back")
        self.setButtonText(QWizard.FinishButton, "Finish")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wizard = Wizard()
    wizard.show()
    sys.exit(app.exec_())