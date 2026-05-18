"""
motion_detector.py
Detects motion in a video stream using frame-difference technique.
Returns bounding boxes and a flag indicating significant motion.
"""

import cv2
import numpy as np


class MotionDetector:
    def __init__(self, min_area=4000, blur_ksize=21, threshold=25, dilate_iter=2):
        self.min_area    = min_area
        self.blur_ksize  = blur_ksize
        self.threshold   = threshold
        self.dilate_iter = dilate_iter
        self._prev_gray  = None

    def detect(self, frame):
        """
        Detect motion in `frame` (BGR numpy array).
        Returns (motion_detected: bool, boxes: list of (x,y,w,h), annotated_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.blur_ksize, self.blur_ksize), 0)

        if self._prev_gray is None:
            self._prev_gray = gray
            return False, [], frame

        diff   = cv2.absdiff(self._prev_gray, gray)
        _, thr = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        thr    = cv2.dilate(thr, None, iterations=self.dilate_iter)

        contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self._prev_gray = gray

        boxes   = []
        for c in contours:
            if cv2.contourArea(c) >= self.min_area:
                x, y, w, h = cv2.boundingRect(c)
                boxes.append((x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if boxes:
            cv2.putText(frame, "MOTION DETECTED", (10, frame.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

        return bool(boxes), boxes, frame
