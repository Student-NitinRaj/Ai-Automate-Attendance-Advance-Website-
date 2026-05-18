"""
enroll_face.py
Interactive face enrollment tool.
Captures 5 photos per person from the webcam using MediaPipe FaceDetector (Tasks API).

Usage:  python enroll_face.py
"""

import cv2
import os
import time
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

DB_PATH         = "database"
PHOTOS_NEEDED   = 5
CAPTURE_DELAY   = 0.8
MODEL_PATH      = os.path.join(os.path.dirname(__file__), "face_detector.tflite")


def capture_face_photos(name: str, camera_index: int = 0):
    person_dir = os.path.join(DB_PATH, name)
    os.makedirs(person_dir, exist_ok=True)

    existing  = [f for f in os.listdir(person_dir) if f.lower().endswith(".jpg")]
    start_idx = len(existing) + 1

    # Build FaceDetector with Tasks API
    base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    fd_opts   = mp_vision.FaceDetectorOptions(
        base_options=base_opts,
        running_mode=mp_vision.RunningMode.IMAGE,
        min_detection_confidence=0.6,
    )
    detector = mp_vision.FaceDetector.create_from_options(fd_opts)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    count     = 0
    last_time = 0
    print(f"\n[INFO] Enrolling '{name}'. Need {PHOTOS_NEEDED} photos.")
    print("[INFO] Look at the camera — photos are taken automatically.\n")

    while count < PHOTOS_NEEDED:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        ih, iw  = frame.shape[:2]

        # Detect faces
        rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img   = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result   = detector.detect(mp_img)
        detected = bool(result.detections)

        # Top HUD bar
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (iw, 55), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.65, display, 0.35, 0, display)
        cv2.putText(display, f"ENROLLING: {name}   |   {count}/{PHOTOS_NEEDED} photos",
                    (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if detected:
            det = result.detections[0].bounding_box
            x1  = det.origin_x
            y1  = det.origin_y
            x2  = x1 + det.width
            y2  = y1 + det.height
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 220, 0), 2)

            now = time.time()
            if now - last_time >= CAPTURE_DELAY:
                path = os.path.join(person_dir, f"{start_idx + count}.jpg")
                cv2.imwrite(path, frame)
                count    += 1
                last_time = now
                print(f"  Captured photo {count}/{PHOTOS_NEEDED} -> {path}")

            cv2.putText(display, f"Face detected! ({count}/{PHOTOS_NEEDED})",
                        (10, ih - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 0), 2)
        else:
            cv2.putText(display, "Position your face in the frame...",
                        (10, ih - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Face Enrollment — Press Q to quit", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()

    if count >= PHOTOS_NEEDED:
        print(f"\nEnrollment complete for '{name}'! ({count} photos saved)")
        print("Now run:  python main.py")
    else:
        print(f"\nEnrollment incomplete ({count}/{PHOTOS_NEEDED} photos).")


def main():
    print("=" * 50)
    print("   Smart Attendance -- Face Enrollment")
    print("=" * 50)
    name = input("Enter person's full name (e.g. Nitin): ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    capture_face_photos(name)


if __name__ == "__main__":
    main()
