import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# ─── Configuration ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Vision | Smart Attendance",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Extreme Premium CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Advanced Animated Background */
    .stApp {
        background: linear-gradient(-45deg, #0b0c10, #1f2833, #0b0c10, #000000);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #c5c6c7;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(31, 40, 51, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(102, 252, 241, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102, 252, 241, 0.8);
        box-shadow: 0 12px 40px 0 rgba(102, 252, 241, 0.2);
    }

    /* Metric Styling inside Glass Cards */
    .metric-icon {
        font-size: 32px;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(#66fcf1, #45a29e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-value {
        font-size: 42px;
        font-weight: 800;
        color: #f8f9fa;
        letter-spacing: -1px;
    }
    .metric-title {
        font-size: 14px;
        font-weight: 600;
        color: #45a29e;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 5px;
    }

    /* Title Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #66fcf1, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #45a29e;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 40px;
        border-bottom: 1px solid rgba(102, 252, 241, 0.2);
        padding-bottom: 20px;
    }

    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: rgba(31, 40, 51, 0.3);
        padding: 10px 10px 0 10px;
        border-radius: 12px 12px 0 0;
        border-bottom: 1px solid rgba(102, 252, 241, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8b9bb4;
        font-weight: 600;
        font-size: 16px;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #66fcf1 !important;
        background-color: rgba(102, 252, 241, 0.1);
        border-bottom: 3px solid #66fcf1 !important;
    }

    /* Dataframe and inputs */
    .stTextInput>div>div>input {
        background-color: rgba(31, 40, 51, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(102, 252, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    .stSelectbox>div>div>div {
        background-color: rgba(31, 40, 51, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(102, 252, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Button Override */
    .stButton>button {
        background: linear-gradient(90deg, #45a29e 0%, #66fcf1 100%);
        color: #0b0c10 !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        box-shadow: 0 4px 15px rgba(102, 252, 241, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 252, 241, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ─── Data Loading ──────────────────────────────────────────────────────────────
CSV_FILE = "attendance.csv"
DB_DIR = "database"

@st.cache_data(ttl=2) # Near real-time refresh
def load_attendance():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Name", "Date", "Time", "Status"])
    return pd.read_csv(CSV_FILE)

def get_enrolled_users():
    if not os.path.exists(DB_DIR):
        return []
    return [d for d in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, d))]

# ─── UI Layout ─────────────────────────────────────────────────────────────────

st.markdown("<h1 class='main-title'>AI VISION COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Enterprise-Grade Face Recognition Attendance Dashboard</p>", unsafe_allow_html=True)

df = load_attendance()
enrolled_users = get_enrolled_users()
total_enrolled = len(enrolled_users)
today_str = datetime.now().strftime("%Y-%m-%d")

if not df.empty:
    today_df = df[df["Date"] == today_str]
    present_today = len(today_df)
else:
    present_today = 0
    
absent_today = max(0, total_enrolled - present_today)
attendance_rate = int((present_today / total_enrolled) * 100) if total_enrolled > 0 else 0

# ─── Top Glass Metrics ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{total_enrolled}</div>
        <div class="metric-title">Registered Personnel</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-icon">✅</div>
        <div class="metric-value" style="color: #66fcf1;">{present_today}</div>
        <div class="metric-title">Present Today</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-icon">❌</div>
        <div class="metric-value" style="color: #ff6b6b;">{absent_today}</div>
        <div class="metric-title">Absent Today</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value" style="color: #feca57;">{attendance_rate}%</div>
        <div class="metric-title">Daily Attendance Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 SYSTEM ANALYTICS", "📋 INTELLIGENCE LOGS", "⚙️ ENTITY MANAGEMENT"])

# ─── TAB 1: ANALYTICS ────────────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if not df.empty:
        col_c1, col_c2 = st.columns([7, 3])
        
        with col_c1:
            # Bar Chart
            trend_df = df.groupby('Date').size().reset_index(name='Counts')
            last_7_days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            trend_df = pd.DataFrame({'Date': last_7_days}).merge(trend_df, on='Date', how='left').fillna(0)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=trend_df['Date'], 
                    y=trend_df['Counts'],
                    marker=dict(
                        color='#66fcf1',
                        line=dict(color='rgba(102, 252, 241, 0.8)', width=2)
                    ),
                    text=trend_df['Counts'],
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title=dict(text="ATTENDANCE VOLUME (7 DAYS)", font=dict(color='#c5c6c7', size=18)),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#8b9bb4',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(102, 252, 241, 0.1)'),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_c2:
            # Donut Chart
            if total_enrolled > 0:
                fig2 = go.Figure(data=[go.Pie(
                    labels=['Present', 'Absent'],
                    values=[present_today, absent_today],
                    hole=.7,
                    marker_colors=['#66fcf1', '#1f2833'],
                    textinfo='percent'
                )])
                fig2.update_layout(
                    title=dict(text="TODAY'S DISTRIBUTION", font=dict(color='#c5c6c7', size=18)),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#8b9bb4',
                    showlegend=False,
                    annotations=[dict(text=f'{attendance_rate}%', x=0.5, y=0.5, font_size=28, font_color='#66fcf1', showarrow=False)]
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No users enrolled.")
    else:
        st.info("Awaiting intelligence data. No logs available yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 2: LOGS ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if df.empty:
        st.warning("No records found.")
    else:
        c1, c2, c3 = st.columns([3, 3, 2])
        with c1:
            dates = ["ALL"] + sorted(df["Date"].unique().tolist(), reverse=True)
            selected_date = st.selectbox("FILTER BY DATE", dates)
        with c2:
            names = ["ALL"] + sorted(df["Name"].unique().tolist())
            selected_name = st.selectbox("FILTER BY IDENTITY", names)
            
        filtered_df = df.copy()
        if selected_date != "ALL":
            filtered_df = filtered_df[filtered_df["Date"] == selected_date]
        if selected_name != "ALL":
            filtered_df = filtered_df[filtered_df["Name"] == selected_name]
            
        # Using Plotly Table for Premium Look instead of st.dataframe
        fig_table = go.Figure(data=[go.Table(
            header=dict(
                values=["<b>IDENTITY</b>", "<b>DATE</b>", "<b>TIME</b>", "<b>STATUS</b>"],
                fill_color='#1f2833',
                align='left',
                font=dict(color='white', size=14),
                height=40
            ),
            cells=dict(
                values=[filtered_df['Name'], filtered_df['Date'], filtered_df['Time'], filtered_df['Status']],
                fill_color='#0b0c10',
                align='left',
                font=dict(color='#c5c6c7', size=13),
                height=35,
                line_color='rgba(102, 252, 241, 0.2)'
            ))
        ])
        fig_table.update_layout(margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_table, use_container_width=True)
        
        # Download
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 SECURE EXPORT (CSV)", data=csv_data, file_name=f"intel_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 3: MANAGEMENT ───────────────────────────────────────────────────────
with tab3:
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#66fcf1;'>Active Entities</h3>", unsafe_allow_html=True)
        if not enrolled_users:
            st.warning("Database Empty.")
        else:
            for person in enrolled_users:
                st.markdown(f"""
                <div style="background: rgba(102, 252, 241, 0.05); border-left: 4px solid #66fcf1; padding: 12px; margin-bottom: 8px; border-radius: 4px;">
                    <strong style="color: white; font-size: 16px;">{person}</strong>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_m2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#66fcf1;'>Register New Entity</h3>", unsafe_allow_html=True)
        new_name = st.text_input("Entity Identity (Name)")
        
        image_source = st.radio("Data Source", ["Upload Image", "Use Camera"], horizontal=True)
        
        uploaded_file = None
        if image_source == "Upload Image":
            uploaded_file = st.file_uploader("Upload Facial Data (JPG/PNG)", type=["jpg", "jpeg", "png"])
        else:
            uploaded_file = st.camera_input("Capture Facial Data")
        
        if st.button("INITIALIZE REGISTRATION"):
            if new_name and uploaded_file:
                clean_name = new_name.strip().replace(" ", "_")
                person_dir = os.path.join(DB_DIR, clean_name)
                
                if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
                if not os.path.exists(person_dir): os.makedirs(person_dir)
                    
                # Save as timestamped file to avoid overwrites
                img_name = f"1_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                img_path = os.path.join(person_dir, img_name)
                
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                st.success(f"Registration Confirmed: {clean_name}")
                st.rerun()
            else:
                st.error("Identity and Data required.")
        st.markdown("</div>", unsafe_allow_html=True)
