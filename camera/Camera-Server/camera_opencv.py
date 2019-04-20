import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            try:
                yield cv2.imencode('.jpg', img)[1].tobytes()
            except GeneratorExit:
                print("image encode error")
                
