import logging
import queue
import threading
import numpy
import cv2
import time

logger = logging.getLogger('jeepers')

class MotionDetector(object):
    def __init__(self, resolution, motion_threshold=5):
        width, height = resolution
        self.cols = width
        self.rows = height
        self.MOTION_THRESHOLD = motion_threshold
        self.motion_counter = 0
        self.motion = False
        self.avg_frame = None

    def write(self, s):
        logger.debug(str(len(s)))
        logger.debug(str(self.rows * self.cols * 3))
        frame = numpy.fromstring(s, dtype=numpy.uint8)
        frame = frame.reshape((self.rows, self.cols, 3))
        gray = self.prep_frame(frame)

        if self.avg_frame is None:
            self.avg_frame = gray.copy().astype("float")
        else:
            self.check_motion(gray)

        return len(s)

    def check_motion(self, gray):
        start = time.time()
        cv2.accumulateWeighted(gray, self.avg_frame, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg_frame))
        thresh = cv2.threshold(frameDelta, 5, 255,
                               cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (im2, contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contains_motion = False
        for contour in contours:
            if cv2.contourArea(contour) > 200:
                contains_motion = True
                break
        if contains_motion:
            self.motion_found()
        else:
            self.motion_counter = 0
            self.motion = False
        logger.debug("Processed in " + str(time.time() - start))

    def prep_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def motion_found(self):
        self.motion_counter += 1
        self.motion = self.motion_counter >= self.MOTION_THRESHOLD
