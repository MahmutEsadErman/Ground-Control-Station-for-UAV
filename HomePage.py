import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QFile

from MapWidget import MapWidget


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless Window
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        # Load the ui file
        ui_file_name = "uifolder/HomePage.ui"
        ui_file = QFile(ui_file_name)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        istanbulhavalimani = [41.27442, 28.727317]
        self.mapwidget = MapWidget(istanbulhavalimani)
        self.ui.mapWidget.layout().addWidget(self.mapwidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
