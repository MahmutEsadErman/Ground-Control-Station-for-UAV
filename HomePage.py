import sys

from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PySide6.QtCore import QFile, Qt

from CameraWidget import CameraWidget
from MapWidget import MapWidget


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # Load the ui file
        ui_file_name = "uifolder/HomePage.ui"
        ui_file = QFile(ui_file_name)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        # Set Map Widget
        istanbulhavalimani = [41.27442, 28.727317]
        self.mapwidget = MapWidget(istanbulhavalimani)
        self.ui.mapFrame.layout().addWidget(self.mapwidget)

        # Set Camera Widget
        self.cameraWidget = CameraWidget()
        self.ui.cameraFrame.layout().addWidget(self.cameraWidget)

        # Show in another window buttons
        self.mapwidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.ui.mapFrame, self.mapwidget))
        self.cameraWidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.ui.cameraFrame, self.cameraWidget))

        # Buttons
        self.ui.btn_waypoints.clicked.connect(self.buttonFunctions)
        self.ui.btn_movemarker.clicked.connect(self.buttonFunctions)
        self.ui.btn_undo.clicked.connect(self.buttonFunctions)
        self.ui.btn_setMission.clicked.connect(self.buttonFunctions)

    def buttonFunctions(self):
        button = self.sender()

        if button.objectName() == "btn_waypoints":
            self.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
            self.mapwidget.page().runJavaScript(f"map.on('click', putWaypoint);")
        if button.objectName() == "btn_movemarker":
            self.mapwidget.page().runJavaScript(f"map.off('click', putWaypoint);")
            self.mapwidget.page().runJavaScript(f"map.on('click', moveMarkerByClick);")
        if button.objectName() == "btn_undo":
            self.mapwidget.page().runJavaScript("undoWaypoint();")
        if button.objectName() == "btn_setMission":
            self.mapwidget.page().runJavaScript("setMission();")
            print("mission: "+str(self.mapwidget.mission))


    def AllocateWidget(self, parent, child):
        if child.isAttached:
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow()
            self.new_window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            child.btn_AllocateWidget.setIcon(QIcon("assets/icons/16x16/cil-arrow-bottom.png"))
            self.new_window.setCentralWidget(child)
            self.new_window.show()
            child.isAttached = False
        else:
            parent.layout().addWidget(child)
            self.new_window.setCentralWidget(None)
            self.new_window.close()
            child.btn_AllocateWidget.setIcon(QIcon("assets/icons/16x16/cil-arrow-top.png"))
            child.isAttached = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec())
