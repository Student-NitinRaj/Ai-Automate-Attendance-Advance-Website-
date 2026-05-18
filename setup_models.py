"""
setup_models.py
------------------------------------------------------
Downloads required MediaPipe model files if they are
not already present in the project directory.

Run ONCE before using the system:
    python setup_models.py
"""

import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS = {
    "face_landmarker.task": (
        "https://storage.googleapis.com/mediapipe-models/"
        "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
    ),
    "face_detector.tflite": (
        "https://storage.googleapis.com/mediapipe-models/"
        "face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
    ),
}


def _progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"\r    [{bar}] {pct:3d}%  {downloaded // 1024:>6} KB", end="", flush=True)


def download_if_missing():
    print("=" * 60)
    print("  Smart Attendance — Model Setup")
    print("=" * 60)
    all_ok = True

    for filename, url in MODELS.items():
        dest = os.path.join(BASE_DIR, filename)
        size = os.path.getsize(dest) if os.path.exists(dest) else 0

        if os.path.exists(dest) and size > 100_000:
            print(f"\n[OK] {filename} already present ({size // 1024} KB)")
            continue

        print(f"\n[DOWNLOAD] {filename} ...")
        print(f"     URL: {url}")
        try:
            urllib.request.urlretrieve(url, dest, reporthook=_progress)
            print()
            new_size = os.path.getsize(dest)
            print(f"     Saved to: {dest}  ({new_size // 1024} KB)")
        except Exception as e:
            print(f"\n[FAIL] Failed to download {filename}: {e}")
            all_ok = False

    print()
    print("=" * 60)
    if all_ok:
        print("[OK] All models ready!")
        print("\nNext steps:")
        print("  1. python enroll_face.py   - add your face")
        print("  2. python main.py          - run attendance system")
    else:
        print("[FAIL] Some downloads failed. Check internet connection.")
    print("=" * 60)
    return all_ok


if __name__ == "__main__":
    ok = download_if_missing()
    sys.exit(0 if ok else 1)
