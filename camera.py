#!/usr/bin/python

import cv2
import os
import threading
import time

import vision.grid


def _acquire_image(camera):
    if camera:
        return camera.read()[1]
    else:
        our_dir = os.path.dirname(os.path.abspath(__file__))
        for entry in os.listdir(our_dir):
            if entry.lower().endswith('.jpg'):
                return cv2.imread(os.path.join(our_dir, entry))


class CameraThread(threading.Thread):
    def __init__(self, image_sink, use_camera):
        super(CameraThread, self).__init__()
        self._image_sink = image_sink
        self._use_camera = use_camera
        self.daemon = True

    def run(self):
        camera = None
        if self._use_camera:
            camera = cv2.VideoCapture(0)

        while True:
            image = _acquire_image(camera)
            image = vision.grid.find_and_rotate_image(image)
            self._image_sink.set(image)
            time.sleep(100)
