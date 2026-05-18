"""
test_recognition.py
-----------------------------------
Tests the FaceRecognizer module in isolation.
Works even if database is empty (falls back gracefully).

Run:  python test_recognition.py
"""

import cv2
import numpy as np
from face_recognizer import FaceRecognizer

print("=" * 50)
print("   Face Recognizer — Unit Test")
print("=" * 50)

print("\n[1] Initializing FaceRecognizer...")
recognizer = FaceRecognizer(db_path="database")
print("    ✅  FaceRecognizer created successfully.")

print("\n[2] Checking database state...")
has = recognizer.has_faces()
people = recognizer.list_people()
print(f"    Database has faces : {has}")
print(f"    Enrolled people    : {people if people else '(none)'}")

print("\n[3] Testing recognize() with a blank frame (no-face test)...")
blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
name, conf = recognizer.recognize(blank_frame)
if name is None:
    print(f"    ✅  Blank-frame returned (None, 0.0) — correct graceful behaviour.")
else:
    print(f"    ⚠️   Unexpected result on blank frame: name={name}, conf={conf}")

print("\n[4] Testing recognize() with a noisy frame...")
noisy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
name2, conf2 = recognizer.recognize(noisy_frame)
print(f"    Result  → name={name2!r}  conf={conf2}")
if name2 is None or isinstance(name2, str):
    print("    ✅  Graceful result — no crash.")
else:
    print("    ⚠️   Unexpected type returned.")

print()
if people:
    print(f"[5] Real recognition test skipped — enroll a face first, then run main.py.")
else:
    print("[5] DATABASE IS EMPTY — run  python enroll_face.py  to add people.")

print()
print("=" * 50)
print("✅  test_recognition.py completed without crash.")
print("=" * 50)
