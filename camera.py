#!/usr/bin/python

try:
    import cv2
except ImportError:
    print 'Skipping OpenCV...'
import os
import threading
import time

import vision.grid


class CameraThread(threading.Thread):
    def __init__(self, image_sink, use_camera):
        super(CameraThread, self).__init__()
        self._image_sink = image_sink
        self._use_camera = use_camera
        self.daemon = True

    def run(self):
        camera = None
        if self._use_camera:
            camera = cv2.VideoCapture(1)

        while True:
            if self._use_camera:
                image = camera.read()[1]
            else:
                image = self._load_jpg_img()

            if image is not None:
                image = vision.grid.find_and_rotate_image(image)
                self._image_sink.set(image)
            time.sleep(0.1)

    @staticmethod
    def _load_jpg_img():
        our_dir = os.path.dirname(os.path.abspath(__file__))
        for entry in os.listdir(our_dir):
            if entry.lower().endswith('.jpg'):
                return cv2.imread(os.path.join(our_dir, entry))
