"""
dashboard.py  —  Smart Attendance System — Live Dashboard
==========================================================
A Tkinter-based GUI dashboard that shows:
  - Real-time attendance records (today and history)
  - Live statistics (total people, present today, absent)
  - Auto-refresh every 5 seconds
  - Export button for CSV
  - Clear / filter controls

Run:   python dashboard.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import shutil
import threading
from datetime import datetime
from attendance_logger import AttendanceLogger

# ── Colour Palette ─────────────────────────────────────────────────────────────
BG_DARK    = "#0f1117"
BG_CARD    = "#1c1f2e"
BG_TABLE   = "#151825"
ACCENT     = "#00d4ff"
ACCENT2    = "#7c3aed"
GREEN      = "#22c55e"
RED        = "#ef4444"
YELLOW     = "#facc15"
TEXT_PRI   = "#f1f5f9"
TEXT_SEC   = "#94a3b8"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEAD  = ("Segoe UI", 12, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)

REFRESH_MS = 5000   # auto-refresh interval


class StatCard(tk.Frame):
    """A single coloured statistics card."""
    def __init__(self, parent, title, value="0", color=ACCENT, **kwargs):
        super().__init__(parent, bg=BG_CARD, highlightbackground=color,
                         highlightthickness=2, **kwargs)
        self._color = color
        self._lbl_val = tk.Label(self, text=value, font=("Segoe UI", 28, "bold"),
                                 fg=color, bg=BG_CARD)
        self._lbl_val.pack(pady=(14, 0))
        tk.Label(self, text=title, font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(pady=(2, 12))

    def set(self, value):
        self._lbl_val.config(text=str(value))


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance System — Dashboard")
        self.configure(bg=BG_DARK)
        self.minsize(900, 620)
        self.geometry("1050x680")

        self._logger = AttendanceLogger()
        self._filter_date = tk.StringVar(value="")
        self._filter_name = tk.StringVar(value="")

        self._build_ui()
        self._refresh()

    # ── UI Construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG_CARD)
        hdr.pack(fill="x", padx=0, pady=0)

        tk.Label(hdr, text="🎓  Smart Attendance Dashboard",
                 font=FONT_TITLE, fg=ACCENT, bg=BG_CARD,
                 pady=14).pack(side="left", padx=20)

        self._lbl_time = tk.Label(hdr, text="", font=FONT_BODY, fg=TEXT_SEC, bg=BG_CARD)
        self._lbl_time.pack(side="right", padx=20)
        self._tick_clock()

        # ── Stat Cards ───────────────────────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG_DARK)
        cards_frame.pack(fill="x", padx=20, pady=(16, 0))

        self._card_total   = StatCard(cards_frame, "Total Enrolled", color=ACCENT)
        self._card_present = StatCard(cards_frame, "Present Today",  color=GREEN)
        self._card_absent  = StatCard(cards_frame, "Absent Today",   color=RED)
        self._card_records = StatCard(cards_frame, "All-Time Records", color=ACCENT2)

        for card in (self._card_total, self._card_present, self._card_absent, self._card_records):
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)

        # ── Filter Bar ───────────────────────────────────────────────────────
        fb = tk.Frame(self, bg=BG_DARK)
        fb.pack(fill="x", padx=20, pady=(10, 0))

        tk.Label(fb, text="Filter by date:", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_DARK).pack(side="left")
        date_entry = tk.Entry(fb, textvariable=self._filter_date, font=FONT_BODY,
                              bg=BG_CARD, fg=TEXT_PRI, insertbackground=ACCENT,
                              relief="flat", width=13)
        date_entry.pack(side="left", padx=(6, 20))
        tk.Label(fb, text="(YYYY-MM-DD)", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_DARK).pack(side="left")

        tk.Label(fb, text="Name:", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_DARK).pack(side="left", padx=(20, 4))
        name_entry = tk.Entry(fb, textvariable=self._filter_name, font=FONT_BODY,
                              bg=BG_CARD, fg=TEXT_PRI, insertbackground=ACCENT,
                              relief="flat", width=16)
        name_entry.pack(side="left", padx=4)

        self._make_btn(fb, "🔍 Filter", self._refresh, ACCENT).pack(side="left", padx=12)
        self._make_btn(fb, "🔄 Refresh", self._refresh, ACCENT2).pack(side="left", padx=4)
        self._make_btn(fb, "📤 Export CSV", self._export_csv, GREEN).pack(side="right", padx=4)
        self._make_btn(fb, "📋 Copy Today", self._copy_today, YELLOW).pack(side="right", padx=4)

        # ── Table ────────────────────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=BG_TABLE)
        table_frame.pack(fill="both", expand=True, padx=20, pady=12)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=BG_TABLE,
                         foreground=TEXT_PRI,
                         rowheight=32,
                         fieldbackground=BG_TABLE,
                         bordercolor=BG_CARD,
                         borderwidth=0,
                         font=FONT_BODY)
        style.configure("Custom.Treeview.Heading",
                         background=BG_CARD,
                         foreground=ACCENT,
                         font=FONT_HEAD,
                         relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT_PRI)])

        cols = ("Name", "Date", "Time", "Status")
        self._tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Custom.Treeview")
        col_widths = {"Name": 200, "Date": 130, "Time": 110, "Status": 120}
        for c in cols:
            self._tree.heading(c, text=c, anchor="center")
            self._tree.column(c, width=col_widths[c], anchor="center", minwidth=80)

        # tag colours
        self._tree.tag_configure("present", foreground=GREEN)
        self._tree.tag_configure("absent",  foreground=RED)
        self._tree.tag_configure("alt",     background="#1a1f30")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ── Status bar ───────────────────────────────────────────────────────
        self._status_lbl = tk.Label(self, text="", font=FONT_SMALL,
                                    fg=TEXT_SEC, bg=BG_DARK, anchor="w", pady=4)
        self._status_lbl.pack(fill="x", padx=22)

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _make_btn(self, parent, text, cmd, color):
        b = tk.Button(parent, text=text, command=cmd, font=FONT_SMALL,
                      bg=color, fg=BG_DARK, activebackground=BG_CARD,
                      activeforeground=color, relief="flat", padx=10, pady=5,
                      cursor="hand2", bd=0)
        return b

    def _tick_clock(self):
        self._lbl_time.config(text=datetime.now().strftime("%A, %d %b %Y   %H:%M:%S"))
        self.after(1000, self._tick_clock)

    # ── Data Refresh ───────────────────────────────────────────────────────────
    def _refresh(self):
        records = self._logger.get_all_records()
        today   = datetime.now().strftime("%Y-%m-%d")

        # ── Filters ──────────────────────────────────────────────────────────
        fdate = self._filter_date.get().strip()
        fname = self._filter_name.get().strip().lower()
        if fdate:
            records = [r for r in records if r["Date"] == fdate]
        if fname:
            records = [r for r in records if fname in r["Name"].lower()]

        # ── Stats ────────────────────────────────────────────────────────────
        all_records  = self._logger.get_all_records()
        enrolled     = len(set(r["Name"] for r in all_records))
        today_names  = set(r["Name"] for r in all_records if r["Date"] == today)
        present      = len(today_names)
        absent       = max(0, enrolled - present)

        self._card_total.set(enrolled)
        self._card_present.set(present)
        self._card_absent.set(absent)
        self._card_records.set(len(all_records))

        # ── Table fill ───────────────────────────────────────────────────────
        for item in self._tree.get_children():
            self._tree.delete(item)

        for i, row in enumerate(reversed(records)):   # newest first
            status = row.get("Status", "Present")
            tag    = "present" if status == "Present" else "absent"
            if i % 2 == 0:
                tag = (tag, "alt")
            self._tree.insert("", "end",
                              values=(row["Name"], row["Date"], row["Time"], status),
                              tags=tag)

        count = len(records)
        label = fdate or "all dates"
        self._status_lbl.config(
            text=f"Showing {count} record(s) for {label}  |  Last refreshed: "
                 f"{datetime.now().strftime('%H:%M:%S')}"
        )

        # schedule next auto-refresh
        self.after(REFRESH_MS, self._refresh)

    # ── Actions ────────────────────────────────────────────────────────────────
    def _export_csv(self):
        src = self._logger.file_path
        if not os.path.exists(src):
            messagebox.showwarning("No Data", "attendance.csv does not exist yet.")
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        if dest:
            shutil.copy2(src, dest)
            messagebox.showinfo("Exported", f"Saved to:\n{dest}")

    def _copy_today(self):
        records = self._logger.get_today_records()
        if not records:
            messagebox.showinfo("Nothing", "No records for today.")
            return
        lines = ["Name\tDate\tTime\tStatus"]
        for r in records:
            lines.append(f"{r['Name']}\t{r['Date']}\t{r['Time']}\t{r['Status']}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self._status_lbl.config(text=f"Copied {len(records)} record(s) to clipboard!")


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
