"""
main.py  —  Smart Attendance System with Face + Motion Tracking
================================================================
Pipeline:
  1. Motion Detector  → only process when someone is present (saves CPU)
  2. Liveness Check   → blink detection (prevents fake photos/screens)
  3. Face Recognition → deepface database match
  4. Attendance Log   → CSV, one entry per person per day
  5. On-screen HUD    → real-time status overlay

Controls:
  Q  → Quit
  R  → Reset liveness / retry recognition
  S  → Show today's attendance log in terminal
"""

import cv2
import time
import os

from motion_detector   import MotionDetector
from liveness_detector import LivenessDetector
from face_recognizer   import FaceRecognizer
from attendance_logger import AttendanceLogger

# ─── CONFIG ────────────────────────────────────────────────────────────────────
CAMERA_INDEX         = 0
RECOGNITION_COOLDOWN = 8      # seconds between recognition attempts
FRAME_W, FRAME_H     = 960, 540
# ───────────────────────────────────────────────────────────────────────────────


def draw_hud(frame, state: dict):
    """Overlay semi-transparent info panel on frame."""
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Top bar
    cv2.rectangle(overlay, (0, 0), (w, 70), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Title
    cv2.putText(frame, "SMART ATTENDANCE SYSTEM", (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

    # Bottom info bar
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, h - 60), (w, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay2, 0.65, frame, 0.35, 0, frame)

    people = state.get("people", [])
    logged = state.get("logged_today", [])
    cv2.putText(frame, f"Enrolled: {', '.join(people) if people else 'None'}", (10, h - 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
    cv2.putText(frame, f"Today: {', '.join(logged) if logged else 'No one yet'}", (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 0), 1)

    # Controls hint
    cv2.putText(frame, "[Q] Quit  [R] Reset  [S] Show Log", (w - 290, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)

    # Last recognition result
    last = state.get("last_result", "")
    if last:
        cv2.putText(frame, last, (12, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 180), 2)


def main():
    print("=" * 60)
    print("  Smart Attendance System  |  Face + Motion + Liveness")
    print("=" * 60)

    motion    = MotionDetector(min_area=3500)
    liveness  = LivenessDetector()
    recognizer = FaceRecognizer()
    logger    = AttendanceLogger()

    if not recognizer.has_faces():
        print("\n⚠️  DATABASE IS EMPTY!")
        print("   Please run:  python enroll_face.py")
        print("   to add people before running the attendance system.\n")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam at index", CAMERA_INDEX)
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    time.sleep(1.0)

    last_recognition_time = 0
    last_result_text      = ""
    logged_today          = [r["Name"] for r in logger.get_today_records()]

    state = {
        "people":       recognizer.list_people(),
        "logged_today": logged_today,
        "last_result":  "",
    }

    print("\n[INFO] System running. Press Q to quit, R to reset, S to show today's log.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame read failed.")
            break

        # ── Step 1: Motion Detection ──────────────────────────────────────────
        motion_found, boxes, frame = motion.detect(frame)

        # ── Step 2: Liveness (only when motion) ──────────────────────────────
        if motion_found:
            is_live, frame, status_text = liveness.process(frame)
        else:
            is_live = liveness.is_live  # keep state when briefly no motion

        # ── Step 3: Face Recognition (throttled) ─────────────────────────────
        now = time.time()
        if is_live and (now - last_recognition_time) > RECOGNITION_COOLDOWN:
            print("[INFO] Liveness confirmed. Identifying face …")
            name, conf = recognizer.recognize(frame)

            if name:
                last_result_text = f"✅  {name}  ({conf:.1f}% match)"
                logged = logger.log(name)
                if logged:
                    logged_today.append(name)
                    state["logged_today"] = logged_today
            else:
                last_result_text = "❓ Unknown person"

            state["last_result"]      = last_result_text
            last_recognition_time     = now
            liveness.reset()   # reset for next person

        # ── HUD overlay ───────────────────────────────────────────────────────
        draw_hud(frame, state)

        cv2.imshow("Smart Attendance", frame)

        # ── Key handling ──────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            print("[INFO] Manual reset — liveness and recognition cleared.")
            liveness.reset()
            last_recognition_time = 0
            state["last_result"]  = ""
        elif key == ord('s'):
            records = logger.get_today_records()
            print("\n── Today's Attendance ──────────────────")
            for r in records:
                print(f"  {r['Name']:20s}  {r['Time']}  {r['Status']}")
            if not records:
                print("  (no records yet)")
            print("────────────────────────────────────────\n")

    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] System stopped. Attendance saved to attendance.csv")


if __name__ == "__main__":
    main()
