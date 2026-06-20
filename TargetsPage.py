import time
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QEvent, QTimer, QByteArray, QBuffer, QIODevice
from uifolder import Ui_TargetsPage
from MediaPlayer import MediaPlayerWindow
from MapWidget import image_to_base64


def qimage_to_base64(qimage, image_format="PNG"):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    image = qimage.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    image.save(buffer, image_format)
    base64_data = byte_array.toBase64().data().decode("utf-8")
    return base64_data


class TargetsPage(QWidget, Ui_TargetsPage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.latest_target_no = None
        # Set Layout
        self.setLayout(QVBoxLayout())

        # Set Widget inside Target Scroll Area
        self.targetsWidget = QWidget()
        self.targetsWidget.setLayout(QGridLayout())
        self.targetsWidget.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.row = 0
        self.column = 0
        self.targets_scrollarea.setWidget(self.targetsWidget)

        # Targets Dictionary
        self.targets = {}
        self.number_of_targets = 0

        # Set Container stylesheet varible
        self.containerStyleSheet = """QWidget:hover{border: 2px solid rgb(64, 71, 88);} QLabel::hover{border: 0px;}"""

        self.oldtarget = QWidget()

        # Set Widget inside Mobile Scroll Area
        self.usersWidget = QWidget()
        self.usersWidget.setLayout(QVBoxLayout())
        self.usersWidget.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.users_scrollarea.setWidget(self.usersWidget)

        # Test
        # QTimer.singleShot(3000, lambda: self.addTarget(QImage("Database/data/deneme/1.jpg"), [1,1], [10, 100], 1))

    def addTarget(self, image, position, time, no):
        print(f"--- addTarget triggered for target {no} at position {position} ---")
        
        # Start deletion timer for the previous latest target
        if hasattr(self, 'latest_target_no') and self.latest_target_no is not None and self.latest_target_no != no:
            old_no = self.latest_target_no
            if old_no in self.targets and "timer" not in self.targets[old_no]:
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda n=old_no: self.removeTarget(n))
                timer.start(2000)
                self.targets[old_no]["timer"] = timer
                
        self.latest_target_no = no

        # Create a new target
        self.number_of_targets += 1
        self.targets[no] = {"image": image, "location": position, "time_interval": time}

        # Create a container widget for the target
        container = self.createContainer(f"target{no}", QPixmap.fromImage(image),
                                         self.number_of_targets)

        # Add the container widget to the grid layout
        self.targetsWidget.layout().addWidget(container, self.row, self.column)

        self.column += 1
        if self.column > 5:  # Adjust this value to change the number of columns
            self.column = 0
            self.row += 1

        # Add target marker
        image_base64 = 'data:image/png;base64,' + qimage_to_base64(image)
        self.parent.homepage.mapwidget.page().runJavaScript(f"""
                    target_marker{no} = L.marker({position}, {{icon: targetIcon}}).addTo(map);
                    target_marker{no}.bindTooltip('<br>' + "<img src='{image_base64}'/>");
                """)

    def setLeavingTime(self, no, time):
        self.targets[no]["time_interval"][1] = time

    def removeTarget(self, no):
        print(f"--- removeTarget triggered for target {no} ---")
        if no in self.targets:
            # Remove from map
            self.parent.homepage.mapwidget.page().runJavaScript(f"""
                if (typeof target_marker{no} !== 'undefined') {{
                    map.removeLayer(target_marker{no});
                }}
            """)
            
            # Remove from UI list
            container = self.findChild(QWidget, f"target{no}")
            if container:
                self.targetsWidget.layout().removeWidget(container)
                container.deleteLater()
                
            # Remove timer if exists
            timer = self.targets[no].pop("timer", None)
            if timer:
                timer.stop()
                timer.deleteLater()
                
            del self.targets[no]
            
            # Allow VideoStreamThread to detect this target ID again
            if hasattr(self.parent, 'homepage') and hasattr(self.parent.homepage, 'cameraWidget'):
                videothread = self.parent.homepage.cameraWidget.videothread
                if no in videothread.known_targets:
                    videothread.known_targets.remove(no)

    def updateTarget(self, no, position, image):
        print(f"--- updateTarget triggered for target {no} at position {position} ---")
        
        # If this target is updated, it becomes the latest target
        if hasattr(self, 'latest_target_no') and self.latest_target_no is not None and self.latest_target_no != no:
            old_no = self.latest_target_no
            if old_no in self.targets and "timer" not in self.targets[old_no]:
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda n=old_no: self.removeTarget(n))
                timer.start(2000)
                self.targets[old_no]["timer"] = timer
                
        self.latest_target_no = no
        
        # Cancel timer for the current target if it had one
        if no in self.targets and "timer" in self.targets[no]:
            self.targets[no]["timer"].stop()
            self.targets[no]["timer"].deleteLater()
            del self.targets[no]["timer"]

        self.parent.homepage.mapwidget.page().runJavaScript(f"target_marker{no}.setLatLng({str(position)});")
        self.setLeavingTime(no, time.time())
        
        if not image.isNull():
            # Update the image in the dictionary
            self.targets[no]["image"] = image
            
            # Update the container label image
            container = self.findChild(QWidget, f"target{no}")
            if container:
                layout = container.layout()
                if layout and layout.count() > 0:
                    image_label = layout.itemAt(0).widget()
                    if isinstance(image_label, QLabel):
                        scaled_pixmap = QPixmap.fromImage(image).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
                        image_label.setPixmap(scaled_pixmap)
            
            # Update the marker tooltip on the map
            image_base64 = 'data:image/png;base64,' + qimage_to_base64(image)
            self.parent.homepage.mapwidget.page().runJavaScript(f"""
                        if (typeof target_marker{no} !== 'undefined') {{
                            target_marker{no}.unbindTooltip();
                            target_marker{no}.bindTooltip('<br>' + "<img src='{image_base64}'/>");
                        }}
                    """)



    def createContainer(self, objectname, pixmap, number):
        # Create a QWidget to hold both labels
        container = QWidget(objectName=objectname)
        layout = QVBoxLayout()
        container.setLayout(layout)
        container.setStyleSheet(self.containerStyleSheet)
        container.setMinimumSize(80, 80)
        container.setMaximumSize(150, 150)

        # Create the image label
        scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(image_label)

        # Create the text label
        text_label = QLabel(str(number))
        text_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        layout.addWidget(text_label)

        # Set click event for container
        container.installEventFilter(self)

        return container



    def eventFilter(self, obj, event):
        if obj.objectName()[:6] == "target":
            # When double clicked open a new window
            if event.type() == QEvent.MouseButtonDblClick:
                no = int(obj.objectName()[6:])
                self.newWindow = MediaPlayerWindow(self,
                                                   no,
                                                   QPixmap.fromImage(self.targets[no]["image"]),
                                                   self.targets[no]["location"],
                                                   self.targets[no]["time_interval"],
                                                   self.parent.homepage.cameraWidget.videothread.starting_time)
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

        return super().eventFilter(obj, event)



