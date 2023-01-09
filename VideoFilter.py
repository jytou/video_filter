import sys, os
import cv2
import multiprocessing

from VideoSaver import VideoSaver

# There is a collision between OpneCV's Qt libraries and the ones on my system - may happen on other systems too!
# Use only the headless parst of OpenCV so that OpenCV's Qt libraries are not imported
ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")

from filter_loader import FilterLoader
from SelectedFilter import SelectedFilter
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget, QFrame, QLabel, QDialog, QComboBox, QDialogButtonBox,
                             QScrollArea, QSlider, QSizePolicy, QFileDialog)


class VideoPlayer(QMainWindow):
    # Sliders use ints and the filters for parameters are floats, transform them into large ints using this factor
    SLIDER_FACTOR = 100000

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Filtering Utility")

        # A timer used to play every frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_frame)

        # The path to the source video - is initialized by the Open Video button
        self.source_video_path = None
        # initialize the field for video capture - will be used in play()
        self.cap = None
        self.fps = None
        # The combobox that holds the filters in the dialog - used to retrieve the selected filter
        self.filter_combo = None
        # The current frame being shown in the video - used when pausing
        self.cur_frame = None
        # A thread used to save videos
        self.saving_thread = QThread()
        # Will be used to save videos
        self.saver = None

        # We need to lock things to avoid concurrent modification / reading of filters while playing the video
        self.lock = multiprocessing.Manager().Lock()

        # Load all defined filters
        self.all_filters = FilterLoader.load_filters(["filters"])
        # array of current filters: [SelectedFilter]
        self.selected_filters = []

        # Initialize all components
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # The right part of the screen with the filters
        filters_layout = QVBoxLayout()
        # The left part of the screen with the video and video commands
        video_layout = QVBoxLayout()

        # Initialize the left part with the filter button
        add_filter_button = QPushButton("Add Filter", self)
        add_filter_button.clicked.connect(self.display_add_filter_dialog)
        filters_layout.addWidget(add_filter_button)

        # The scrolling area
        filters_scroll = QScrollArea()
        filters_scroll.setWidgetResizable(True)
        filters_scroll.setMinimumWidth(300)
        filters_list_widget = QWidget()
        self.filters_list_layout = QVBoxLayout(filters_list_widget)
        self.filters_list_layout.addStretch(1)
        filters_scroll.setWidget(filters_list_widget)
        filters_layout.addWidget(filters_scroll)

        # Now the video part
        self.video_frame = QLabel()
        self.video_frame.setFixedSize(800, 600)

        # All buttons under the video
        buttons_layout = QHBoxLayout()

        open_button = QPushButton("Open Video", self)
        open_button.clicked.connect(self.open_video)
        buttons_layout.addWidget(open_button)

        play_button = QPushButton("Play", self)
        play_button.clicked.connect(self.play)
        buttons_layout.addWidget(play_button)

        pause_button = QPushButton("Pause", self)
        pause_button.clicked.connect(self.pause)
        buttons_layout.addWidget(pause_button)

        save_button = QPushButton("Save Video", self)
        save_button.clicked.connect(self.save_video)
        buttons_layout.addWidget(save_button)

        video_layout.addWidget(self.video_frame)
        video_layout.addLayout(buttons_layout)

        # Set both layouts to the main layout
        main_layout.addLayout(video_layout)
        main_layout.addLayout(filters_layout)
        self.setCentralWidget(main_widget)

    def open_video(self):
        """
        Opens an "Open file" dialog to open the source video.
        This method sets the self.source_video_path field
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Videos (*.mp4 *.avi *.m4v *.mkv *.mpg *.mpeg);;All Files (*)",
            options=QFileDialog.Options())
        if filename:
            self.source_video_path = filename

    def save_video(self):
        """
        Opens a "Save file" dialog to determine the target file path.
        Saves the video while applying all the filters
        """
        if self.source_video_path is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Videos (*.avi)")
        if filename:
            # load all the filters and their values
            fs, vals = self.get_current_filter_info()
            self.saver = VideoSaver(self.source_video_path, filename, fs, vals)
            self.saver.moveToThread(self.saving_thread)
            self.saving_thread.started.connect(self.saver.run)
            #saver.finished.connect(self.saving_thread.quit)
            #saver.progress.connect(self.report_progress) TODO report the progress of saving the file
            self.saving_thread.start()

    def get_current_filter_info(self):
        """
        Retrieves the currently selected filters and their parameters
        :return: fs [Filter], vals [{name => value}]
        """
        fs = []
        vals = []
        with self.lock:
            for sf in self.selected_filters:
                fs.append(sf.filter)
                vals.append(sf.vals)
        return fs, vals

    def read_frame(self):
        """
        Reads a single frame of the video if there is a next one and calls show_curframe()
        Sets self.cur_frame accordingly
        """
        if not self.cap or not self.cap.isOpened():
            self.timer.stop()
            return
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            return
        self.cur_frame = frame
        self.show_curframe()

    def show_curframe(self):
        """
        Filters and shows the current frame in the video widget
        Assumes self.cur_frame is correctly set to the current frame
        """
        if self.cur_frame is None:
            return
        fs, vals = self.get_current_filter_info()
        frame = self.cur_frame
        # Apply current filters with their values
        for i in range(len(fs)):
            frame = fs[i].apply_filter(frame, vals[i])
        # Size it to screen size
        frame = cv2.resize(frame, (800, 600))
        # Prepare the image to be rendered in a QObject
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        # Render the image on the widget
        self.video_frame.setPixmap(QPixmap.fromImage(image))

    def play(self):
        """
        User clicked on play button, prepare the video decoding and start the timer to show the frames
        """
        # Set the media player to play the video
        if self.source_video_path is None:
            self.open_video()
        if self.source_video_path is None:
            return
        self.cap = cv2.VideoCapture(self.source_video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer.start(round(1000 / self.fps))

    def pause(self):
        """
        Pauses/restarts the video
        """
        if self.source_video_path is None:
            return
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(round(1000 / self.fps))

    def display_add_filter_dialog(self):
        """
        Shows the "add filter" dialog that enables the user to choose a new filter
        When the selected filter has been selected and the dialog is validated, add the filter to the list of filters
        """
        # Create the "add filter" dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Filter")
        dlg_layout = QVBoxLayout()

        dialog_label = QLabel('Please select a filter')
        dlg_layout.addWidget(dialog_label)

        # Put all filters into a combo box with their names
        filter_combo = QComboBox()
        # Save the actual filters, the list only retains their names
        # TODO make sure that there aren't two filters with the same name
        filter_list = []
        for f in self.all_filters:
            filter_combo.addItem(self.all_filters[f].get_filter_name())
            filter_list.append(self.all_filters[f])
        dlg_layout.addWidget(filter_combo)

        # OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dlg.accept)
        button_box.rejected.connect(dlg.reject)
        dlg_layout.addWidget(button_box)

        dlg.setLayout(dlg_layout)

        if dlg.exec():
            # Add window dialog accepted, add the filter to the currently selected filters
            # Get the actual filter that has been selected
            f = filter_list[filter_combo.currentIndex()]
            # Create a new frame to be added to the filters list
            filter_frame = QFrame()
            filter_frame.setFrameStyle(QFrame.Sunken)
            filter_frame.setFrameShape(QFrame.Box)

            # Create a new entry in the selected_filters array with the selected filter information
            with self.lock:
                vs = {}
                for param in f.get_config():
                    vs[param.name] = param.default_val
                selected_filter = SelectedFilter(f, filter_frame, len(self.selected_filters), vs)
                self.selected_filters.append(selected_filter)

            # The overall layout of the frame itself
            filter_layout = QVBoxLayout()
            # The top part containing the filter name and possibly several buttons - only one for now
            top_layout = QHBoxLayout()
            filter_label = QLabel(f.get_filter_name())
            top_layout.addWidget(filter_label)
            # Delete button for this filter
            delete_button = QPushButton("X")
            # Associate the delete button to the selected filter so that we can retrieve it later
            delete_button.selected_filter = selected_filter
            top_layout.addWidget(delete_button)
            delete_button.clicked.connect(self.delete_filter)
            top_layout.addStretch(1)
            filter_layout.addLayout(top_layout)
            # Now create a slider fer every parameter
            for param in f.get_config():
                # Every parameter actually has a whole layout to get its name and slider displayed horizontally
                filter_param_layout = QHBoxLayout()
                filter_param_label = QLabel(param.name)
                filter_param_layout.addWidget(filter_param_label)
                filter_param_slider = QSlider(Qt.Horizontal)
                # Save the SelectedFilter for future reference - especially the position in the list
                filter_param_slider.selected_filter = selected_filter
                # Save the slider's parameter name
                # TODO make sure that all parameters for every single filter have different names
                filter_param_slider.param_name = param.name
                # Set the slider's range depending on the parameter's min and max values - scaled to SLIDER_FACTOR
                filter_param_slider.setRange(
                    round(param.min_val * self.SLIDER_FACTOR),
                    round(param.max_val * self.SLIDER_FACTOR))
                # Set the slider value to the default
                filter_param_slider.setValue(round(param.default_val * self.SLIDER_FACTOR))
                filter_param_slider.valueChanged[int].connect(self.slider_changed)
                filter_param_layout.addWidget(filter_param_slider)
                filter_layout.addLayout(filter_param_layout)
            filter_frame.setLayout(filter_layout)
            # Insert the widget at the correct position in the list of widgets
            self.filters_list_layout.insertWidget(selected_filter.index, filter_frame)
            # Make sure to refresh the video frame with the current filter if it is not currently running
            if not self.timer.isActive():
                self.show_curframe()

    def slider_changed(self, val):
        """
        Called when a slider's value is changed by the user
        :param val: the new value
        """
        slider = self.sender()
        # Make sure we are not modifying values while they are being read to show the video frames
        with self.lock:
            # Update the value for the corresponding filter + param name
            self.selected_filters[slider.selected_filter.index].vals[slider.param_name] = val / self.SLIDER_FACTOR
        # Refresh the current frame if the video is not running
        if not self.timer.isActive():
            self.show_curframe()

    def delete_filter(self):
        """
        Called when the user clicks the "delete" button of one filter.
        Destroys the corresponding filter both in the UI and in self.selected_filters
        """
        selected_filter = self.sender().selected_filter
        idx = selected_filter.index
        with self.lock:
            self.selected_filters.__delitem__(idx)
            # Delete the widget from the layout so that it will never be shown again
            selected_filter.widget.setParent(None)
            # Decrement the index of all selected filters after this one
            for i in range(idx, len(self.selected_filters)):
                self.selected_filters[i].index -= 1
        # Refresh the current frame if the video is not running
        if not self.timer.isActive():
            self.show_curframe()


# Instantiate the frame and launch the app
app = QApplication(sys.argv)
player = VideoPlayer()
player.show()
sys.exit(app.exec_())
