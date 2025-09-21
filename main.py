#Importing the components we need
from PySide6.QtWidgets import QApplication, QWidget

#sys processing command-line args
import sys


#Responsible for running the app
app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()