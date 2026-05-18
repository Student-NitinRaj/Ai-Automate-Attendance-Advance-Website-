# Smart Attendance System — Advanced Face + Motion + Liveness

> **Fully offline, AI-powered attendance system** that automatically logs attendance using face recognition, blink-based liveness detection, and motion-triggered processing.

---

## Features

| Feature | Description |
|---------|-------------|
| **Face Recognition** | DeepFace / VGG-Face deep learning model |
| **Liveness Detection** | MediaPipe eye-blink analysis (EAR) — rejects photos and screens |
| **Motion Detection** | Frame-difference algorithm — only processes when someone is present (saves CPU) |
| **Duplicate Prevention** | One entry per person per day — no double-counting |
| **GUI Dashboard** | Dark-mode Tkinter dashboard with live stats, filters, export |
| **CLI Viewer** | Terminal-based attendance viewer with date/name filters |

---

## Project Structure

```
Advance attendance Motion Sensor/
│
├── main.py               ← Main live attendance system (webcam)
├── enroll_face.py        ← Enroll new people via webcam (5 photos)
├── dashboard.py          ← GUI dashboard (dark mode, live stats)
├── view_attendance.py    ← CLI attendance viewer
│
├── motion_detector.py    ← Frame-difference motion detection
├── liveness_detector.py  ← MediaPipe blink detection (EAR)
├── face_recognizer.py    ← DeepFace identity matching
├── attendance_logger.py  ← CSV attendance record manager
│
├── test_all.py           ← Complete automated test suite (27 tests)
├── test_pipeline.py      ← Quick module smoke test
├── test_recognition.py   ← Face recognizer unit test
├── setup_models.py       ← Download MediaPipe model files
│
├── face_landmarker.task  ← MediaPipe face landmarks model
├── face_detector.tflite  ← MediaPipe face detection model
├── attendance.csv        ← Auto-generated attendance log
├── requirements.txt
│
└── database/             ← Face database
    └── <PersonName>/
        ├── 1.jpg
        └── 2.jpg
```

---

## Quick Start

### Step 1 — Install dependencies
```
python -m pip install -r requirements.txt
```

### Step 2 — Download MediaPipe models (first time only)
```
python setup_models.py
```

### Step 3 — Run automated tests to verify everything works
```
python -X utf8 test_all.py
```
Expected: **ALL TESTS PASSED** (27 tests, Python exit code 0)

### Step 4 — Enroll people into the face database
```
python enroll_face.py
```
Enter a name, look at your webcam — it captures 5 photos automatically.

### Step 5 — Start the attendance system
```
python main.py
```

### Step 6 (Optional) — Open the GUI Dashboard
```
python dashboard.py
```

### Step 7 (Optional) — View attendance from terminal
```
python view_attendance.py               # today's records
python view_attendance.py --all         # all records
python view_attendance.py --date 2026-05-15
python view_attendance.py --name Nitin
```

### Step 8 (Optional) — Open the Streamlit Web Dashboard
```
streamlit run streamlit_app.py
```

---

## How It Works

```
Webcam Frame
    │
    ▼
Motion Detector   ← Skips processing if no one present (saves CPU)
    │ Motion found
    ▼
Liveness Detector ← Requires 2 real blinks to confirm live person
    │ Blinks confirmed
    ▼
Face Recognizer   ← Matches face against database (VGG-Face model)
    │ Match found
    ▼
Attendance Logger ← Logs Name, Date, Time to CSV (once per day)
```

---

## Anti-Spoofing (Fake Attendance Prevention)

| Attack | Defence |
|--------|---------|
| Photo attack (holding a photo) | No blinks detected → Rejected |
| Screen attack (phone/laptop) | No real blinks → Rejected |
| Duplicate scan (same person twice) | Second entry blocked by CSV check |

---

## Keyboard Controls (while `main.py` is running)

| Key | Action |
|-----|--------|
| `Q` | Quit the system |
| `R` | Reset liveness — allow re-scan |
| `S` | Print today's attendance log to terminal |

---

## Test Suite

Run `python -X utf8 test_all.py` to run all 27 automated tests:

| Section | Tests |
|---------|-------|
| 1. Environment & Imports | Python 3.9+, OpenCV, NumPy, Pandas, Pillow, MediaPipe, DeepFace |
| 2. Model Files | face_landmarker.task, face_detector.tflite |
| 3. MotionDetector | 4 tests (first frame, identical, motion, output type) |
| 4. LivenessDetector | 5 tests (blank frame, return type, reset, EAR, close) |
| 5. AttendanceLogger | 8 tests (header, log, duplicate, multi-person, queries) |
| 6. FaceRecognizer | 5 tests (init, has_faces, list_people, graceful fallback) |
| 7. Integration Chain | 3 tests (motion→log→retrieve, no webcam needed) |
| 8. Database Structure | 2 tests (directory exists, person folders) |

---

## attendance.csv Format

```
Name,Date,Time,Status
Nitin,2026-05-15,09:15:32,Present
```

---

## Requirements

- Python 3.9+
- Webcam (for `main.py` and `enroll_face.py`)
- No GPU required — runs on CPU

```
opencv-python>=4.8.0
mediapipe>=0.10.0
deepface>=0.0.90
tf-keras>=2.14.0
tensorflow>=2.14.0
pandas>=2.0.0
numpy>=1.24.0
pillow>=10.0.0
```
