"""
test_pipeline.py
-----------------------------------
Offline test that verifies all modules load and run correctly
WITHOUT needing a webcam or deepface (it falls back gracefully).

Run:  python test_pipeline.py
"""

import cv2
import numpy as np
import time

print("=" * 55)
print("  Smart Attendance — Full Pipeline Test")
print("=" * 55)

errors = []

# ── Test 1: OpenCV ────────────────────────────────────────
try:
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(blank, "OpenCV OK", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    print(f"[1/5] ✅  OpenCV  {cv2.__version__}")
except Exception as e:
    print(f"[1/5] ❌  OpenCV failed: {e}"); errors.append("opencv")

# ── Test 2: MediaPipe Liveness ────────────────────────────
try:
    from liveness_detector import LivenessDetector
    ld = LivenessDetector()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    live, _, status = ld.process(blank)
    print(f"[2/5] ✅  Liveness Detector — status: '{status}'")
except Exception as e:
    print(f"[2/5] ❌  Liveness Detector failed: {e}"); errors.append("liveness")

# ── Test 3: Motion Detector ───────────────────────────────
try:
    from motion_detector import MotionDetector
    md = MotionDetector()
    f1 = np.zeros((480, 640, 3), dtype=np.uint8)
    f2 = np.ones((480, 640, 3), dtype=np.uint8) * 50
    # First call initialises prev frame
    md.detect(f1)
    detected, boxes, _ = md.detect(f2)
    print(f"[3/5] ✅  Motion Detector — detected motion: {detected}")
except Exception as e:
    print(f"[3/5] ❌  Motion Detector failed: {e}"); errors.append("motion")

# ── Test 4: Attendance Logger ─────────────────────────────
try:
    import os, csv
    from attendance_logger import AttendanceLogger
    test_csv = "_test_attendance.csv"
    al = AttendanceLogger(file_path=test_csv)
    res1 = al.log("TestPerson")
    res2 = al.log("TestPerson")  # duplicate should return False
    records = al.get_today_records()
    os.remove(test_csv)
    assert res1 == True,  "First log should succeed"
    assert res2 == False, "Duplicate log should be rejected"
    assert len(records) == 1
    print(f"[4/5] ✅  Attendance Logger — duplicate prevention OK")
except Exception as e:
    print(f"[4/5] ❌  Attendance Logger failed: {e}"); errors.append("logger")

# ── Test 5: Face Recognizer (graceful — no deepface required) ─
try:
    from face_recognizer import FaceRecognizer
    fr = FaceRecognizer()
    has = fr.has_faces()
    people = fr.list_people()
    print(f"[5/5] ✅  Face Recognizer — DB has faces: {has}, people: {people}")
    if not has:
        print("       ⚠️   Run 'python enroll_face.py' to add people to the database.")
except Exception as e:
    print(f"[5/5] ❌  Face Recognizer failed: {e}"); errors.append("recognizer")

# ── Summary ───────────────────────────────────────────────
print()
print("=" * 55)
if errors:
    print(f"❌  {len(errors)} test(s) FAILED: {', '.join(errors)}")
else:
    print("✅  ALL TESTS PASSED — Project is ready to run!")
    print("\nNext steps:")
    print("  1. python enroll_face.py   ← add your face to database")
    print("  2. python main.py          ← start attendance system")
print("=" * 55)
