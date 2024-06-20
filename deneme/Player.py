from PySide6.QtCore import QTimer, Qt, QPoint
from PySide6.QtGui import QAction, QIcon, QImage, QPixmap, QPainter
from PySide6.QtWidgets import (QMainWindow, QPushButton, QFileDialog, QSlider, QHBoxLayout,
                               QWidget, QVBoxLayout, QLabel, QSizePolicy, QMessageBox,
                               QDialog, QGridLayout, QTextEdit)
from moviepy.video.io.VideoFileClip import VideoFileClip


# Main window class responsible for managing the application's main window.
class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.video_clip = None
        self.video_playback_Ui = VideoPlayBackUi()
        self.video_playback = None

        # Initialize the main window view
        self.setWindowTitle("Video Player")
        self.setWindowIcon(QIcon("online-video.png"))
        self.setStyleSheet("background-color: #f0f0f0;")

        # Adding MenuBar with File, Tool, and Help menus
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("&File")
        self.tool_menu = self.menu_bar.addMenu("&Tool")
        self.help_menu = self.menu_bar.addMenu("&Help")

        # Add actions to the File menu
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)
        self.quit_action = QAction("&Quit", self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.triggered.connect(self.quit_application)
        self.file_menu.addAction(self.quit_action)

        # Add action to the Tool menu
        self.play_rev_action = QAction("&Play Reverse", self)
        self.play_rev_action.setShortcut("Ctrl+R")
        self.tool_menu.addAction(self.play_rev_action)

        # Add action to the Help menu
        self.shortcut_help_action = QAction("&Shortcut Help", self)
        self.shortcut_help_action.triggered.connect(self.show_shortcut_help)
        self.help_menu.addAction(self.shortcut_help_action)

        # Set the central widget to the video playback UI
        self.setCentralWidget(self.video_playback_Ui)

        # Connect signals to slots
        self.video_playback_Ui.play_button.clicked.connect(self.play)
        self.video_playback_Ui.pause_button.clicked.connect(self.pause)
        self.play_rev_action.triggered.connect(self.play_reverse)
        self.video_playback_Ui.play_reverse_button.clicked.connect(self.play_reverse)
        self.video_playback_Ui.slider.sliderMoved.connect(self.slider_moved)
        self.video_playback_Ui.video_label.mousePressEvent = self.overlay_mouse_press
        self.video_playback_Ui.video_label.mouseMoveEvent = self.overlay_mouse_move
        self.video_playback_Ui.speed_slider.valueChanged.connect(self.set_playback_speed)
        self.video_playback_Ui.save_frame_button.clicked.connect(self.save_frame)

    # Function to open a video file
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_clip = VideoFileClip(file_path)
            self.video_playback = VideoPlayBack(self.video_playback_Ui, self.video_clip)
            self.video_playback.load_frame()
            self.video_playback_Ui.play_button.setEnabled(True)
            self.video_playback_Ui.pause_button.setEnabled(True)
            self.video_playback_Ui.slider.setRange(0, len(self.video_playback.qimage_frames) - 1)
            self.video_playback_Ui.slider.setEnabled(True)
            self.video_playback_Ui.speed_slider.setRange(50, 200)
            self.video_playback_Ui.speed_slider.setValue(100)
            self.video_playback_Ui.speed_slider.setEnabled(True)
            self.video_playback_Ui.save_frame_button.setEnabled(True)

    # Function to play the video
    def play(self):
        self.video_playback.toggle_play_pause()

    # Function to pause the video
    def pause(self):
        self.video_playback.toggle_play_pause()

    # Function to play the video in reverse
    def play_reverse(self):
        if self.video_clip is None:
            QMessageBox.warning(self, "File not found", "Load the video file first")
            return
        self.video_playback.reverse_play()

    # Function to handle slider movement
    def slider_moved(self, position):
        self.video_playback.current_frame_index = position

    # Function to handle overlay mouse press event
    def overlay_mouse_press(self, event):
        if event.buttons() == Qt.LeftButton:
            self.video_playback.set_overlay_position(event.pos())

    # Function to handle overlay mouse move event
    def overlay_mouse_move(self, event):
        if event.buttons() == Qt.LeftButton:
            self.video_playback.set_overlay_position(event.pos())

    # Function to quit the application
    def quit_application(self):
        self.close()

    # Function to show shortcut help dialog
    def show_shortcut_help(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Shortcut Help")
        layout = QGridLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText("Shortcuts:\n"
                               "Open: Ctrl + O\n"
                               "Quit: Ctrl + Q\n"
                               "Play Reverse: Ctrl + R")
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec_()

    # Function to set the playback speed
    def set_playback_speed(self, value):
        self.video_playback.set_playback_speed(value)

    # Function to save the current frame
    def save_frame(self):
        if (hasattr(self, 'video_playback') and self.video_playback is not None and
                self.video_playback.current_frame_index < len(self.video_playback.qimage_frames)):
            frame_index = self.video_playback.current_frame_index
            frame_image = self.video_playback.qimage_frames[frame_index]
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Frame", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
            if file_path:
                frame_image.save(file_path)
        else:
            QMessageBox.warning(self, "Error", "No frame to save.")


# Video playback UI class responsible for managing the user interface elements related to video playback.
class VideoPlayBackUi(QWidget):
    def __init__(self):
        super().__init__()

        # Create play, pause, slider, speed slider, overlay, and save frame button
        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.pause_button = QPushButton("Pause")
        self.play_reverse_button = QPushButton("Play Reverse")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider_label = QLabel("Frame Slider:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        self.speed_slider_label = QLabel("Playback Speed:")
        self.overlay_widget = OverlayWidget()
        self.save_frame_button = QPushButton("Save Frame")
        self.save_frame_button.setEnabled(False)

        # Create layout and add widgets
        video_button_layout = QHBoxLayout()
        video_button_layout.addWidget(self.play_button, 1)
        video_button_layout.addWidget(self.pause_button, 1)
        video_button_layout.addWidget(self.play_reverse_button, 1)
        video_button_layout.addWidget(self.slider_label)
        video_button_layout.addWidget(self.slider, 5)
        video_button_layout.addWidget(self.speed_slider_label)
        video_button_layout.addWidget(self.speed_slider, 3)
        video_button_layout.addWidget(self.save_frame_button)
        video_button_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Create video label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addWidget(self.overlay_widget)
        main_layout.addLayout(video_button_layout)
        self.setLayout(main_layout)

        # Set size policy
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )


# Video playback class responsible for managing the actual playback of the video.
class VideoPlayBack:
    def __init__(self, video_playback_ui, video_clip):
        self.video_playback_ui = video_playback_ui
        self.video_clip = video_clip
        self.qimage_frames = None
        self.current_frame_index = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.timer = QTimer()

    # Function to load frames from the video clip
    def load_frame(self):
        self.qimage_frames = []
        if self.video_clip is None:
            print("class: VideoPlayBack, fun: load_frame: video_clip is Null")
        for frame in self.video_clip.iter_frames():
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.qimage_frames.append(q_image)
        return self.qimage_frames

    # Function to update the frame
    def update_frame(self):
        if self.current_frame_index < len(self.qimage_frames):
            qimage_frame = self.qimage_frames[self.current_frame_index]
            pixmap = QPixmap.fromImage(qimage_frame)
            self.video_playback_ui.video_label.setPixmap(pixmap)
            self.video_playback_ui.slider.setValue(self.current_frame_index)
            self.current_frame_index += 1
        else:
            self.timer.stop()

    # Function to reverse the frame
    def reverse_frame(self):
        self.current_frame_index -= 1
        self.update_frame()
        self.current_frame_index -= 1

    # Function to toggle play/pause
    def toggle_play_pause(self):
        if self.is_playing:
            self.timer.stop()
        else:
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(1000 / (self.video_clip.fps * self.playback_speed))
        self.is_playing = not self.is_playing

    # Function to play video in reverse
    def reverse_play(self):
        if self.video_clip is None:
            QMessageBox.warning(self.video_playback_ui, "File not found", "Load the video file first")
            return
        self.timer.timeout.connect(self.reverse_frame)
        self.timer.start(1000 / (self.video_clip.fps * self.playback_speed))

    # Function to set playback speed
    def set_playback_speed(self, value):
        self.playback_speed = value / 100.0

    # Function to set overlay position
    def set_overlay_position(self, position):
        self.video_playback_ui.overlay_widget.position = position
        self.video_playback_ui.overlay_widget.update()


# Overlay widget class responsible for managing the overlay image.
class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.position = QPoint(10, 10)
        self.overlay_image = QImage("Overlay.PNG")
        self.overlay_image = self.overlay_image.scaledToWidth(100)
        self.setFixedSize(self.overlay_image.size())

    # Function to paint the overlay image
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.overlay_image)

    # Function to handle mouse press event
    def mousePressEvent(self, event):
        self.position = event.pos()
        self.update()

    # Function to handle mouse move event
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.position = event.pos()
            self.update()
