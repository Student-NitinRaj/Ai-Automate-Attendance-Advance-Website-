import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configure page
st.set_page_config(page_title="Smart Attendance Dashboard", page_icon="🎓", layout="wide")

# Custom CSS for premium look
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00D4FF;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00D4FF;
    }
    .metric-title {
        font-size: 14px;
        color: #94A3B8;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Smart Attendance Dashboard")
st.markdown("Real-time view of attendance records from the Edge Device.")

CSV_FILE = "attendance.csv"

def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Name", "Date", "Time", "Status"])
    return pd.read_csv(CSV_FILE)

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
today = datetime.now().strftime("%Y-%m-%d")

if not df.empty:
    dates = ["All"] + list(df['Date'].unique())
    selected_date = st.sidebar.selectbox("Filter by Date", dates, index=1 if today in dates else 0)
    
    names = ["All"] + list(df['Name'].unique())
    selected_name = st.sidebar.selectbox("Filter by Name", names)

    # Apply filters
    if selected_date != "All":
        df = df[df['Date'] == selected_date]
    if selected_name != "All":
        df = df[df['Name'] == selected_name]

# Metrics Row
col1, col2, col3 = st.columns(3)
total_records = len(df)
present_count = len(df[df['Status'] == 'Present']) if not df.empty else 0
unique_people = df['Name'].nunique() if not df.empty else 0

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_records}</div><div class="metric-title">Total Records</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card" style="border-color: #22C55E;"><div class="metric-value" style="color: #22C55E;">{present_count}</div><div class="metric-title">Present Today</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card" style="border-color: #A855F7;"><div class="metric-value" style="color: #A855F7;">{unique_people}</div><div class="metric-title">Unique People</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Data Table
st.subheader("📋 Attendance Log")
if df.empty:
    st.info("No attendance records found.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Export button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export as CSV",
        data=csv_data,
        file_name=f"attendance_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
