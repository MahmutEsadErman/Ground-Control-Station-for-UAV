from PySide6.QtWidgets import QApplication, QMainWindow, QMenu
import sys
from Player import MainWindow

app = QApplication(sys.argv)

mainWindow = MainWindow(app)
mainWindow.show()

app.exec()