# -*- coding: utf-8 -*-
"""
test_all.py  -  Complete Automated Test Suite
=============================================
Tests every module without needing a webcam or GPU.

Run:  python test_all.py
Exit code  0  = all pass
Exit code  1  = one or more failures
"""

import sys
import os
import cv2
import csv
import time
import numpy as np
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PASS  = "[PASS]"
FAIL  = "[FAIL]"
SKIP  = "[SKIP]"
SEP   = "-" * 60
errors = []
skips  = []


def section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(f"{SEP}")


def result(num, name, ok, note=""):
    tag = PASS if ok else FAIL
    print(f"  [{num}] {tag}  {name}" + (f"  - {note}" if note else ""))
    if not ok:
        errors.append(name)


# =================================================================
# 1. IMPORTS / ENVIRONMENT
# =================================================================
section("1. Environment and Imports")

# 1.1 Python version
try:
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 9
    result("1.1", f"Python {v.major}.{v.minor}", ok,
           "OK" if ok else "need 3.9+")
except Exception as e:
    result("1.1", "Python version", False, str(e))

# 1.2 OpenCV
try:
    import cv2
    result("1.2", f"OpenCV {cv2.__version__}", True)
except Exception as e:
    result("1.2", "OpenCV import", False, str(e))

# 1.3 NumPy
try:
    import numpy as np
    result("1.3", f"NumPy {np.__version__}", True)
except Exception as e:
    result("1.3", "NumPy import", False, str(e))

# 1.4 Pandas
try:
    import pandas as pd
    result("1.4", f"Pandas {pd.__version__}", True)
except Exception as e:
    result("1.4", "Pandas import", False, str(e))

# 1.5 Pillow
try:
    from PIL import Image
    import PIL
    result("1.5", f"Pillow {PIL.__version__}", True)
except Exception as e:
    result("1.5", "Pillow import", False, str(e))

# 1.6 MediaPipe
try:
    import mediapipe as mp
    result("1.6", f"MediaPipe {mp.__version__}", True)
except Exception as e:
    result("1.6", "MediaPipe import", False, str(e))

# 1.7 DeepFace
try:
    import deepface
    result("1.7", f"DeepFace {deepface.__version__}", True)
except Exception as e:
    result("1.7", "DeepFace import", False, str(e))

# =================================================================
# 2. MODEL FILES
# =================================================================
section("2. Model Files")

for fname in ("face_landmarker.task", "face_detector.tflite"):
    path = os.path.join(ROOT, fname)
    exists = os.path.exists(path)
    size   = os.path.getsize(path) if exists else 0
    ok     = exists and size > 50_000
    result("2.x", fname, ok,
           f"{size // 1024} KB" if ok else "MISSING - run: python setup_models.py")

# =================================================================
# 3. MOTION DETECTOR
# =================================================================
section("3. MotionDetector")

try:
    from motion_detector import MotionDetector
    md = MotionDetector(min_area=100)

    # 3.1 First frame — always no motion
    f1 = np.zeros((480, 640, 3), dtype=np.uint8)
    detected, boxes, _ = md.detect(f1)
    result("3.1", "First frame → no motion", not detected, f"detected={detected}")

    # 3.2 Identical frames → no motion
    detected2, _, _ = md.detect(f1.copy())
    result("3.2", "Identical frames → no motion", not detected2)

    # 3.3 Very different frame → motion
    f2 = np.ones((480, 640, 3), dtype=np.uint8) * 180
    detected3, boxes3, _ = md.detect(f2)
    result("3.3", "Bright frame after dark → motion detected", detected3,
           f"boxes={len(boxes3)}")

    # 3.4 Output frame is BGR ndarray
    _, _, out = md.detect(f2)
    result("3.4", "Returns annotated frame (ndarray)", isinstance(out, np.ndarray))

except Exception as e:
    result("3.x", "MotionDetector", False, str(e))

# =================================================================
# 4. LIVENESS DETECTOR
# =================================================================
section("4. LivenessDetector")

try:
    from liveness_detector import LivenessDetector
    ld = LivenessDetector()

    # 4.1 Blank frame — no face → not live, no crash
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    live, frame_out, status = ld.process(blank)
    result("4.1", "Blank frame → not live", not live, f"status='{status}'")

    # 4.2 Returns BGR frame
    result("4.2", "Returns annotated BGR frame", isinstance(frame_out, np.ndarray))

    # 4.3 Reset clears state
    ld.reset()
    result("4.3", "reset() clears blink state",
           ld.total_blinks == 0 and not ld.is_live)

    # 4.4 EAR property check (internal math)
    pts = np.array([[0,0],[1,2],[2,2],[3,0],[2,-2],[1,-2]], dtype=np.float32)
    # EAR can be numpy.float32 or float — accept both
    ear = ld._ear(pts)
    result("4.4", "EAR calculation returns non-negative number",
           isinstance(ear, (float, np.floating)) and float(ear) >= 0.0, f"EAR={float(ear):.4f}")

    ld.close()
    result("4.5", "close() without error", True)

except FileNotFoundError as e:
    skips.append("LivenessDetector")
    print(f"  [4.x] {SKIP}  LivenessDetector - model file missing: {e}")
except Exception as e:
    result("4.x", "LivenessDetector", False, str(e))

# =================================================================
# 5. ATTENDANCE LOGGER
# =================================================================
section("5. AttendanceLogger")

try:
    from attendance_logger import AttendanceLogger
    # Use a guaranteed-fresh path (not pre-existing)
    csv_path = os.path.join(ROOT, "_test_attendance_tmp.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path)

    al = AttendanceLogger(file_path=csv_path)

    # 5.1 CSV created with header
    with open(csv_path, "r") as f:
        header = f.readline().strip()
    result("5.1", "CSV file created with header", "Name,Date,Time,Status" in header)

    # 5.2 First log succeeds
    ok = al.log("Alice")
    result("5.2", "First log for Alice returns True", ok is True)

    # 5.3 Duplicate log rejected
    ok2 = al.log("Alice")
    result("5.3", "Duplicate log returns False (not logged twice)", ok2 is False)

    # 5.4 Different person logged
    ok3 = al.log("Bob")
    result("5.4", "Different person Bob logged", ok3 is True)

    # 5.5 get_today_records returns both
    recs = al.get_today_records()
    result("5.5", "get_today_records() has 2 entries", len(recs) == 2, f"len={len(recs)}")

    # 5.6 get_all_records
    all_recs = al.get_all_records()
    result("5.6", "get_all_records() returns list", isinstance(all_recs, list))

    # 5.7 is_logged_today
    result("5.7", "is_logged_today(Alice) == True",  al.is_logged_today("Alice"))
    result("5.8", "is_logged_today(Carol) == False", not al.is_logged_today("Carol"))

    os.remove(csv_path)

except Exception as e:
    result("5.x", "AttendanceLogger", False, str(e))
    if os.path.exists(csv_path):
        os.remove(csv_path)

# =================================================================
# 6. FACE RECOGNIZER
# =================================================================
section("6. FaceRecognizer")

try:
    from face_recognizer import FaceRecognizer
    fr = FaceRecognizer(db_path=os.path.join(ROOT, "database"))

    # 6.1 Instantiation
    result("6.1", "FaceRecognizer instantiated", True)

    # 6.2 has_faces
    has = fr.has_faces()
    result("6.2", f"has_faces() returns bool", isinstance(has, bool), f"has={has}")

    # 6.3 list_people
    people = fr.list_people()
    result("6.3", "list_people() returns list", isinstance(people, list),
           f"people={people}")

    # 6.4 Blank frame graceful
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    name, conf = fr.recognize(blank)
    result("6.4", "recognize(blank) → None or str, no crash",
           name is None or isinstance(name, str), f"name={name!r} conf={conf}")

    # 6.5 Noisy frame graceful
    noisy = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    name2, conf2 = fr.recognize(noisy)
    result("6.5", "recognize(noisy) → no crash", True, f"name={name2!r}")

except Exception as e:
    result("6.x", "FaceRecognizer", False, str(e))

# =================================================================
# 7. INTEGRATION - motion -> liveness -> logger chain
# =================================================================
section("7. Integration Chain (no webcam)")

try:
    from motion_detector   import MotionDetector
    from attendance_logger import AttendanceLogger

    # Use a guaranteed-fresh path (not pre-existing)
    int_csv = os.path.join(ROOT, "_test_integration_tmp.csv")
    if os.path.exists(int_csv):
        os.remove(int_csv)

    md2 = MotionDetector(min_area=100)
    al2 = AttendanceLogger(file_path=int_csv)

    # Simulate two frames: no motion, then motion
    dark_frame   = np.zeros((480, 640, 3), dtype=np.uint8)
    bright_frame = np.full((480, 640, 3), 200, dtype=np.uint8)
    md2.detect(dark_frame)
    motion_found, _, _ = md2.detect(bright_frame)

    result("7.1", "Integration: motion detected between frames", motion_found)

    # Simulate logging a detected person
    if motion_found:
        logged = al2.log("IntegrationTest")
        result("7.2", "Integration: attendance logged on motion", logged)
        recs = al2.get_today_records()
        result("7.3", "Integration: record retrievable", len(recs) == 1,
               f"records={recs}")

    os.remove(int_csv)

except Exception as e:
    result("7.x", "Integration chain", False, str(e))

# =================================================================
# 8. DATABASE DIRECTORY
# =================================================================
section("8. Database Structure")

db_path = os.path.join(ROOT, "database")
try:
    result("8.1", "database/ directory exists", os.path.isdir(db_path))
    people = [d for d in os.listdir(db_path)
              if os.path.isdir(os.path.join(db_path, d))]
    result("8.2", f"Found {len(people)} person folder(s)",
           True, f"folders={people}")
    if people:
        for person in people:
            imgs = [f for f in os.listdir(os.path.join(db_path, person))
                    if f.lower().endswith((".jpg",".jpeg",".png"))]
            if imgs:
                result("8.3", f"  {person}: {len(imgs)} image(s)", True)
            else:
                # Empty folder needs webcam enrollment — this is a setup step, not a code bug
                print(f"  [8.3] {SKIP}  {person}: 0 images - run enroll_face.py to add images")
                skips.append(f"{person} has no images (run enroll_face.py)")
    else:
        print(f"  [8.3] {SKIP}  No person folders - run: python enroll_face.py")
        skips.append("database populated")

except Exception as e:
    result("8.x", "Database structure", False, str(e))

# =================================================================
# SUMMARY
# =================================================================
print(f"\n{'='*60}")
print(f"  TEST SUMMARY")
print(f"{'='*60}")
if errors:
    print(f"\n  FAILED: {len(errors)} failure(s):")
    for e in errors:
        print(f"       - {e}")
if skips:
    print(f"\n  SKIPPED: {len(skips)} skip(s):")
    for s in skips:
        print(f"       - {s}")
if not errors:
    print(f"\n  ALL TESTS PASSED!")
    print(f"\n  Next steps:")
    print(f"    python enroll_face.py   - enroll yourself")
    print(f"    python main.py          - run live attendance")
    print(f"    python dashboard.py     - open the GUI dashboard")
print(f"\n{'='*60}")

sys.exit(1 if errors else 0)
