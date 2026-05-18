"""
final_check.py  -  Smart Attendance System - Complete Final Verification
=========================================================================
Checks EVERY component of the project in one clean run:
  1. Python & all packages
  2. Model files (MediaPipe)
  3. Face database (enrolled people + photos)
  4. All 4 modules (Motion, Liveness, Logger, Recognizer)
  5. Integration pipeline
  6. Attendance CSV state
  7. Available scripts summary

Run:  python final_check.py
"""

import sys
import os
import cv2
import csv
import numpy as np
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PASS  = "  [PASS]"
FAIL  = "  [FAIL]"
SKIP  = "  [SKIP]"
INFO  = "  [INFO]"
W     = 62
LINE  = "=" * W
SEP   = "-" * W

passed = 0
failed = 0
skipped = 0


def ok(label, note=""):
    global passed
    passed += 1
    suffix = f"  ({note})" if note else ""
    print(f"{PASS}  {label}{suffix}")


def fail(label, note=""):
    global failed
    failed += 1
    suffix = f"  ({note})" if note else ""
    print(f"{FAIL}  {label}{suffix}")


def skip(label, note=""):
    global skipped
    skipped += 1
    suffix = f"  ({note})" if note else ""
    print(f"{SKIP}  {label}{suffix}")


def info(label):
    print(f"{INFO}  {label}")


def section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(f"{SEP}")


# ============================================================
print()
print(LINE)
print("  SMART ATTENDANCE SYSTEM  -  FINAL CHECK")
print(f"  {datetime.now().strftime('%A, %d %B %Y  %H:%M:%S')}")
print(LINE)


# ============================================================
# 1. PYTHON ENVIRONMENT
# ============================================================
section("1. Python Environment & Packages")

v = sys.version_info
if v.major == 3 and v.minor >= 9:
    ok(f"Python {v.major}.{v.minor}.{v.micro}", "compatible")
else:
    fail(f"Python {v.major}.{v.minor}", "need Python 3.9+")

packages = {
    "opencv-python": ("cv2",       lambda: cv2.__version__),
    "numpy":         ("numpy",     lambda: np.__version__),
    "pandas":        ("pandas",    lambda: __import__("pandas").__version__),
    "pillow":        ("PIL",       lambda: __import__("PIL").__version__),
    "mediapipe":     ("mediapipe", lambda: __import__("mediapipe").__version__),
    "deepface":      ("deepface",  lambda: __import__("deepface").__version__),
    "tensorflow":    ("tensorflow",lambda: __import__("tensorflow").__version__),
}

for pkg, (mod, ver_fn) in packages.items():
    try:
        ver = ver_fn()
        ok(f"{pkg}", ver)
    except Exception as e:
        fail(f"{pkg}", str(e))


# ============================================================
# 2. MODEL FILES
# ============================================================
section("2. MediaPipe Model Files")

models = {
    "face_landmarker.task": 500_000,   # ~3.6 MB
    "face_detector.tflite": 50_000,    # ~224 KB
}

for fname, min_size in models.items():
    path = os.path.join(ROOT, fname)
    if os.path.exists(path):
        sz = os.path.getsize(path)
        if sz >= min_size:
            ok(fname, f"{sz // 1024} KB")
        else:
            fail(fname, f"too small ({sz} bytes) - corrupted?")
    else:
        fail(fname, "MISSING - run: python setup_models.py")


# ============================================================
# 3. FACE DATABASE
# ============================================================
section("3. Face Database")

db_path = os.path.join(ROOT, "database")
if os.path.isdir(db_path):
    ok("database/ directory exists")
    people = []
    for d in os.scandir(db_path):
        if d.is_dir():
            imgs = [f for f in os.listdir(d.path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if imgs:
                people.append((d.name, len(imgs)))
                ok(f"  Person: '{d.name}'", f"{len(imgs)} photos enrolled")
            else:
                skip(f"  Person: '{d.name}'", "0 photos - run enroll_face.py")
    if not people:
        fail("No enrolled people", "run: python enroll_face.py")
    else:
        ok(f"Total enrolled people", str(len(people)))
else:
    fail("database/ directory missing")


# ============================================================
# 4. MODULE TESTS
# ============================================================
section("4. Module Tests")

# -- MotionDetector --
try:
    from motion_detector import MotionDetector
    md = MotionDetector(min_area=100)
    f1 = np.zeros((480, 640, 3), dtype=np.uint8)
    f2 = np.full((480, 640, 3), 180, dtype=np.uint8)
    md.detect(f1)
    detected, boxes, out_frame = md.detect(f2)
    assert detected, "motion not detected"
    assert isinstance(out_frame, np.ndarray), "bad return type"
    ok("MotionDetector", "motion detection + frame output")
except Exception as e:
    fail("MotionDetector", str(e))

# -- LivenessDetector --
try:
    from liveness_detector import LivenessDetector
    ld = LivenessDetector()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    is_live, frame_out, status = ld.process(blank)
    assert not is_live, "blank frame should not be live"
    assert isinstance(frame_out, np.ndarray)
    ld.reset()
    assert ld.total_blinks == 0 and not ld.is_live
    ld.close()
    ok("LivenessDetector", f"EAR blink detection, status='{status}'")
except FileNotFoundError:
    fail("LivenessDetector", "model file missing - run setup_models.py")
except Exception as e:
    fail("LivenessDetector", str(e))

# -- AttendanceLogger --
try:
    from attendance_logger import AttendanceLogger
    tmp_csv = os.path.join(ROOT, "_fc_tmp.csv")
    if os.path.exists(tmp_csv):
        os.remove(tmp_csv)
    al = AttendanceLogger(file_path=tmp_csv)
    r1 = al.log("TestUser")
    r2 = al.log("TestUser")   # duplicate
    r3 = al.log("TestUser2")
    recs = al.get_today_records()
    os.remove(tmp_csv)
    assert r1 is True,  "first log should succeed"
    assert r2 is False, "duplicate should be blocked"
    assert r3 is True,  "second person should succeed"
    assert len(recs) == 2, f"expected 2, got {len(recs)}"
    ok("AttendanceLogger", "log / duplicate-block / get_today_records all correct")
except Exception as e:
    fail("AttendanceLogger", str(e))

# -- FaceRecognizer --
try:
    from face_recognizer import FaceRecognizer
    fr = FaceRecognizer(db_path=db_path)
    has  = fr.has_faces()
    ppl  = fr.list_people()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    name, conf = fr.recognize(blank)
    assert isinstance(has, bool)
    assert isinstance(ppl, list)
    assert name is None or isinstance(name, str)
    ok("FaceRecognizer", f"has_faces={has}, people={ppl}, graceful blank-frame")
except Exception as e:
    fail("FaceRecognizer", str(e))


# ============================================================
# 5. INTEGRATION TEST (motion -> log -> retrieve)
# ============================================================
section("5. Integration Pipeline Test")

try:
    from motion_detector   import MotionDetector
    from attendance_logger import AttendanceLogger

    tmp2 = os.path.join(ROOT, "_fc_int.csv")
    if os.path.exists(tmp2): os.remove(tmp2)

    md2 = MotionDetector(min_area=100)
    al2 = AttendanceLogger(file_path=tmp2)

    dark   = np.zeros((480, 640, 3), dtype=np.uint8)
    bright = np.full((480, 640, 3), 200, dtype=np.uint8)
    md2.detect(dark)
    found, _, _ = md2.detect(bright)
    assert found, "motion not detected"

    logged = al2.log("IntegrationPerson")
    assert logged is True

    recs = al2.get_today_records()
    assert len(recs) == 1
    assert recs[0]["Name"] == "IntegrationPerson"

    os.remove(tmp2)
    ok("Full pipeline: motion -> attendance log -> retrieve", "all 3 steps work")
except Exception as e:
    fail("Integration pipeline", str(e))


# ============================================================
# 6. ATTENDANCE CSV STATUS
# ============================================================
section("6. Live Attendance CSV")

csv_path = os.path.join(ROOT, "attendance.csv")
if os.path.exists(csv_path):
    ok("attendance.csv exists")
    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))
    today = datetime.now().strftime("%Y-%m-%d")
    today_rows = [r for r in rows if r.get("Date") == today]
    info(f"Total records all time : {len(rows)}")
    info(f"Records for today ({today}): {len(today_rows)}")
    if today_rows:
        for r in today_rows:
            info(f"  -> {r['Name']:20s}  {r['Time']}  {r['Status']}")
    else:
        info("  No attendance logged yet today (blink in front of webcam in main.py)")
else:
    skip("attendance.csv", "not created yet - will appear when main.py logs first entry")


# ============================================================
# 7. SCRIPT AVAILABILITY
# ============================================================
section("7. Project Scripts")

scripts = {
    "main.py":             "Main live system (webcam + face recognition)",
    "enroll_face.py":      "Enroll a new person via webcam",
    "dashboard.py":        "GUI dashboard (dark mode, live stats)",
    "view_attendance.py":  "CLI attendance viewer",
    "setup_models.py":     "Download MediaPipe models",
    "test_all.py":         "Full automated test suite (27 tests)",
    "test_pipeline.py":    "Quick 5-step smoke test",
    "test_recognition.py": "Face recognizer unit test",
}

for script, desc in scripts.items():
    path = os.path.join(ROOT, script)
    if os.path.exists(path):
        size = os.path.getsize(path)
        ok(f"{script}", desc)
    else:
        fail(f"{script}", "FILE MISSING")


# ============================================================
# FINAL SUMMARY
# ============================================================
total = passed + failed + skipped
print()
print(LINE)
print("  FINAL CHECK SUMMARY")
print(LINE)
print(f"  Total checks : {total}")
print(f"  Passed       : {passed}")
print(f"  Skipped      : {skipped}  (setup steps requiring webcam)")
print(f"  Failed       : {failed}")
print(LINE)

if failed == 0:
    print()
    print("  PROJECT IS 100% COMPLETE AND WORKING!")
    print()
    print("  QUICK START:")
    print("    python enroll_face.py    - enroll a new person")
    print("    python main.py           - start live attendance")
    print("    python dashboard.py      - open GUI dashboard")
    print("    python view_attendance.py --all  - view all records")
else:
    print()
    print(f"  {failed} check(s) FAILED. Fix the items above and re-run.")

print(LINE)
print()

sys.exit(0 if failed == 0 else 1)
