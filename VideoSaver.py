import traceback
import cv2
from PyQt5 import QtCore


class VideoSaver(QtCore.QObject):
    """
    A class to save a video in a separate thread in order not to block the UI
    """
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, source_filename, target_filename, fs, vals):
        super().__init__()
        self.source_filename = source_filename
        self.target_filename = target_filename
        self.fs = fs
        self.vals = vals

    @QtCore.pyqtSlot()
    def run(self):
        print("Saving video...")
        try:
            # Prepare the reader for the source file
            cap = cv2.VideoCapture(self.source_filename)
            fps = cap.get(cv2.CAP_PROP_FPS)
            # Prepare the writer for the target file
            out = cv2.VideoWriter(
                self.target_filename,
                cv2.VideoWriter_fourcc(*"MJPG"), # cv2.VideoWriter_fourcc(*"H264"), # cv2.VideoWriter_fourcc(*"avc1"),
                fps,
                (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            # Write every frame while applying the filters
            i = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    for i in range(len(self.fs)):
                        frame = self.fs[i].apply_filter(frame, self.vals[i])
                    out.write(frame)
                else:
                    break
                self.progress.emit(i)
                i += 1
                if i % int(fps * 10) == 0:
                    print(str(round(i // fps)) + " seconds saved")

            # Finish the reading / writing
            cap.release()
            out.release()
            print("Saving ended successfully")
        except:
            # Let's make sure we get some trace if anything goes wrong in this thread
            traceback.print_exc()
        self.finished.emit()

