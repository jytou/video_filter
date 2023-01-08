from abstract_filter import Filter, FilterParameter
import cv2


class FaceDetect(Filter):
    """
    A simple face detector using haar cascades - find the data in subfolder data
    """
    # !! WARNING !! By doing this, we are not thread-safe
    haar_cascade_face = cv2.CascadeClassifier('filters/data/haarcascade_frontalface_default.xml')
    param_scale_factor = FilterParameter("Scale factor", 2, 100, 5)
    config = [param_scale_factor]

    @staticmethod
    def get_filter_name():
        return "Face Detection"

    @staticmethod
    def apply_filter(frame, params):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Applying the haar classifier to detect faces on the grayscale image
        faces_rect = FaceDetect.haar_cascade_face.detectMultiScale(
            gray_image,
            scaleFactor=params[FaceDetect.param_scale_factor.name],
            minNeighbors=5)

        # Draw a rectangle for each detected face
        for (x, y, w, h) in faces_rect:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 15)

        return frame

    @staticmethod
    def get_config():
        return FaceDetect.config

