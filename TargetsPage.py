import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QScrollArea, QLabel, QGridLayout, \
    QPushButton
from PySide6.QtCore import Qt, QEvent

from MediaPlayer import MediaPlayerWindow

class TargetsPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set Layout
        self.setLayout(QVBoxLayout())

        # Set Scroll Area
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.layout().setContentsMargins(100, 10, 100, 10)
        self.layout().addWidget(self.scrollArea)

        # Set Widget inside Scroll Area
        self.targetsWidget = QWidget()
        self.targetsWidget.setLayout(QGridLayout())
        self.targetsWidget.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.row = 0
        self.column = 0
        self.scrollArea.setWidget(self.targetsWidget)

        # Targets Dictionary
        self.targets = {}
        self.number_of_targets = 0

        # Set Container stylesheet varible
        self.containerStyleSheet = """QWidget:hover{border: 2px solid rgb(64, 71, 88);} QLabel::hover{border: 0px;}"""

        # Add Button
        button = QPushButton()
        button.clicked.connect(self.addTarget)
        self.layout().addWidget(button)

        self.oldtarget = QWidget()

    def addTarget(self, pixmap, location, time_interval):
        # Create a new target
        self.number_of_targets += 1
        self.targets[self.number_of_targets] = {"pixmap": pixmap, "location": location, "time_interval": time_interval}

        # Create a QWidget to hold both labels
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        container.setStyleSheet(self.containerStyleSheet)
        container.setMinimumSize(80, 80)
        container.setMaximumSize(150, 150)

        # Create the image label
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(image_label)

        # Create the text label
        text_label = QLabel(str(self.number_of_targets))
        text_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(text_label)

        # Add the container widget to the grid layout
        self.targetsWidget.layout().addWidget(container, self.row, self.column)

        self.column += 1
        if self.column > 4:  # Adjust this value to change the number of columns
            self.column = 0
            self.row += 1

        # Set click event for container
        container.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj.objectName() == "target":
            # When double clicked open a new window
            if event.type() == QEvent.MouseButtonDblClick:
                self.newWindow = MediaPlayerWindow()
                self.newWindow.show()
            # When clicked change the border color
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    self.oldtarget.setStyleSheet(self.containerStyleSheet)
                    obj.setStyleSheet("""
                        QWidget{border: 2px solid rgb(64, 71, 88);}
                        QLabel{border: 0px;}
                                """)
                    self.oldtarget = obj
                    return True
            if event.type() == QEvent.MouseButtonRelease:
                self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TargetsPage()
    window.show()
    sys.exit(app.exec())
