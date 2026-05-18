"""
attendance_logger.py
Handles logging of attendance records to a CSV file.
Prevents duplicate logging for the same person on the same day.
"""

import csv
import os
from datetime import datetime


class AttendanceLogger:
    def __init__(self, file_path="attendance.csv"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time", "Status"])

    def is_logged_today(self, name):
        date_str = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(self.file_path):
            return False
        with open(self.file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Name"] == name and row["Date"] == date_str:
                    return True
        return False

    def log(self, name, status="Present"):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        if not self.is_logged_today(name):
            with open(self.file_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, date_str, time_str, status])
            print(f"[ATTENDANCE] ✅ Logged: {name} at {time_str} ({status})")
            return True
        else:
            print(f"[ATTENDANCE] ℹ️  {name} already logged today.")
            return False

    def get_today_records(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        records = []
        if not os.path.exists(self.file_path):
            return records
        with open(self.file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Date"] == date_str:
                    records.append(row)
        return records

    def get_all_records(self):
        records = []
        if not os.path.exists(self.file_path):
            return records
        with open(self.file_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records
