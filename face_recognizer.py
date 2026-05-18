"""
face_recognizer.py
Identifies a person's face from a captured frame using DeepFace.
Matches against the images stored in the database/ folder structure:
    database/
        PersonName/
            photo1.jpg
            photo2.jpg
"""

import os
import cv2
import numpy as np


class FaceRecognizer:
    def __init__(self, db_path="database", model_name="VGG-Face", distance_metric="cosine", threshold=0.4):
        self.db_path         = db_path
        self.model_name      = model_name
        self.distance_metric = distance_metric
        self.threshold       = threshold
        os.makedirs(self.db_path, exist_ok=True)

    def has_faces(self):
        for root, _, files in os.walk(self.db_path):
            if any(f.lower().endswith((".jpg", ".jpeg", ".png")) for f in files):
                return True
        return False

    def list_people(self):
        people = []
        for entry in os.scandir(self.db_path):
            if entry.is_dir():
                has_img = any(
                    f.lower().endswith((".jpg", ".jpeg", ".png"))
                    for f in os.listdir(entry.path)
                )
                if has_img:
                    people.append(entry.name)
        return people

    def recognize(self, frame_bgr):
        """
        Recognize a face from a BGR numpy array.
        Returns (name: str | None, confidence: float)
        """
        if not self.has_faces():
            print("[RECOGNIZER] ⚠️  Database is empty. Add images to database/<Name>/")
            return None, 0.0

        try:
            from deepface import DeepFace
        except ImportError:
            print("[RECOGNIZER] ❌ deepface not installed. Run: python -m pip install deepface tf-keras")
            return None, 0.0

        # Save temp frame
        tmp = "_tmp_frame.jpg"
        cv2.imwrite(tmp, frame_bgr)

        try:
            dfs = DeepFace.find(
                img_path=tmp,
                db_path=self.db_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=False,
                silent=True,
            )
            if dfs and len(dfs[0]) > 0:
                best = dfs[0].iloc[0]
                identity_path = best["identity"]
                dist_col = [c for c in best.index if "distance" in c.lower()]
                distance  = best[dist_col[0]] if dist_col else 1.0

                if distance <= self.threshold:
                    # Extract person name from path
                    parent = os.path.basename(os.path.dirname(identity_path))
                    name = parent if parent and parent.lower() != "database" else \
                           os.path.splitext(os.path.basename(identity_path))[0]
                    confidence = round((1.0 - distance) * 100, 1)
                    return name, confidence
        except Exception as e:
            print(f"[RECOGNIZER] Error: {e}")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

        return None, 0.0
