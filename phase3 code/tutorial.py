from PyQt5.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys

class Page1(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("We can have text only tutorial like this")
        self.setSubTitle("Compare these prototypes in group discussions and analyze their "
                         "strengths and weaknesses. Your discussion should reference UI design "
                         "principles such as the ten heuristics of the Nielsen Norman Group. Describe"
                         " how your final UI evolved from each prototype by incorporating the strong "
                         "elements of each prototype, and what new design elements you created after "
                         "the discussion.")


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Or we can write a document and take screenshots")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.logo = QLabel(self)
        self.logo_pixmap = QPixmap('screenshot.png')
        self.logo_pixmap = self.logo_pixmap.scaled(800,600)
        self.logo.setPixmap(self.logo_pixmap)
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)

class Wizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My Wizard")
        self.setGeometry(100, 50, 900, 900)
        self.addPage(Page1())
        self.addPage(Page2())
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