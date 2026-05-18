"""
liveness_detector.py
Detects whether a face is a live person using Eye Aspect Ratio (EAR)
and blink detection via MediaPipe FaceLandmarker (Tasks API).
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ── Eye landmark indices in FaceLandmarker 468-point mesh ────────────────────
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")


class LivenessDetector:
    EAR_THRESHOLD       = 0.21
    BLINK_CONSEC_FRAMES = 2
    REQUIRED_BLINKS     = 2

    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"face_landmarker.task not found at {MODEL_PATH}.\n"
                "Run the setup once:\n"
                "  python setup_models.py"
            )
        base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        opts = mp_vision.FaceLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker  = mp_vision.FaceLandmarker.create_from_options(opts)
        self._blink_ctr   = 0
        self.total_blinks = 0
        self.is_live      = False

    def _ear(self, pts):
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        h  = np.linalg.norm(pts[0] - pts[3])
        return (v1 + v2) / (2.0 * h + 1e-6)

    def _get_pts(self, landmarks, indices, w, h):
        return np.array(
            [[landmarks[i].x * w, landmarks[i].y * h] for i in indices],
            dtype=np.float32,
        )

    def process(self, bgr_frame):
        """
        Args:
            bgr_frame: numpy BGR image
        Returns:
            (is_live: bool, annotated_frame: ndarray, status: str)
        """
        ih, iw = bgr_frame.shape[:2]
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result  = self._landmarker.detect(mp_image)
        status  = "No face detected"
        color   = (0, 165, 255)

        if result.face_landmarks:
            lm = result.face_landmarks[0]  # first face

            left_pts  = self._get_pts(lm, LEFT_EYE,  iw, ih)
            right_pts = self._get_pts(lm, RIGHT_EYE, iw, ih)
            ear = (self._ear(left_pts) + self._ear(right_pts)) / 2.0

            if ear < self.EAR_THRESHOLD:
                self._blink_ctr += 1
            else:
                if self._blink_ctr >= self.BLINK_CONSEC_FRAMES:
                    self.total_blinks += 1
                    if self.total_blinks >= self.REQUIRED_BLINKS:
                        self.is_live = True
                self._blink_ctr = 0

            if self.is_live:
                status = f"LIVE - Liveness Confirmed!"
                color  = (0, 220, 0)
            else:
                remaining = max(0, self.REQUIRED_BLINKS - self.total_blinks)
                status = f"Please blink {remaining} more time(s)..."
                color  = (0, 165, 255)

            cv2.putText(bgr_frame, f"EAR: {ear:.3f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(bgr_frame, f"Blinks: {self.total_blinks}/{self.REQUIRED_BLINKS}",
                        (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.putText(bgr_frame, status, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)

        return self.is_live, bgr_frame, status

    def reset(self):
        self._blink_ctr   = 0
        self.total_blinks = 0
        self.is_live      = False

    def close(self):
        self._landmarker.close()
