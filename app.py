import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Schoolnet Monitoring Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=60000, key="refresh")

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =========================
GLOBAL
========================= */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background-color: #F4F6F9;
}

/* =========================
TOP SPACING
========================= */

.block-container {
    padding-top: 3rem !important;
    padding-bottom: 1rem;
}

/* Prevent title hiding */

[data-testid="stHeader"] {
    background: transparent;
}

header {
    height: 0rem;
}

/* =========================
SIDEBAR
========================= */

[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Sidebar labels */

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: white;
}

/* Sidebar title */

.sidebar-title {
    font-size: 24px;
    font-weight: 700;
    color: white;
    margin-bottom: 18px;
    cursor: pointer;
    text-decoration: none;
}

/* Filter heading */

.filter-heading {
    font-size: 13px;
    font-weight: 600;
    color: #D1D5DB;
    margin-top: 14px;
    margin-bottom: 8px;
}

/* =========================
DROPDOWN
========================= */

div[data-baseweb="select"] > div {
    background-color: white !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    cursor: pointer !important;
}

div[data-baseweb="select"] span {
    color: black !important;
    font-weight: 500 !important;
}

/* =========================
HEADER
========================= */

.main-title {
    font-size: 30px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 2px;
    cursor: pointer;
}

.sub-title {
    font-size: 14px;
    color: #6B7280;
    margin-top: 0px;
    margin-bottom: 10px;
}

/* =========================
KPI CARDS
========================= */

.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border-left: 5px solid #1F4E79;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

.kpi-title {
    font-size: 13px;
    color: #6B7280;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 600;
    color: #111827;
}

/* =========================
SECTION BOX
========================= */

.section-box {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

schools = pd.read_csv("Schools.csv")
students = pd.read_csv("Students.csv")
teachers = pd.read_csv("Teachers.csv")
devices = pd.read_csv("Devices.csv")
usage = pd.read_csv("Usage.csv")
tal = pd.read_csv("Tal_Register.csv")

device_health = pd.read_csv("device_health.csv")
internet = pd.read_csv("internet_uptime.csv")
complaints = pd.read_csv("complaints.csv")
project_health = pd.read_csv("project_health.csv")
monthly_usage = pd.read_csv("monthly_usage.csv")
donor = pd.read_csv("donor_monitoring.csv")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    """
    <a href="/" target="_self" style="text-decoration:none;">
        <div class="sidebar-title">
            Schoolnet Platform
        </div>
    </a>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Summary",
        "Donor Monitoring",
        "Device Health Monitoring",
        "Internet Monitoring",
        "Complaint Tracking",
        "Project Health Center"
    ]
)

# =========================================================
# STATE FILTER
# =========================================================

st.sidebar.markdown(
    '<div class="filter-heading">Select State</div>',
    unsafe_allow_html=True
)

state_options = ["All"] + sorted(schools["state"].unique())

selected_state = st.sidebar.selectbox(
    label="",
    options=state_options,
    index=0,
    label_visibility="collapsed"
)

# =========================================================
# LIVE CSV UPLOAD
# =========================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Upload Latest Data")

uploaded_device = st.sidebar.file_uploader(
    "Upload Device Health CSV",
    type=["csv"]
)

uploaded_internet = st.sidebar.file_uploader(
    "Upload Internet CSV",
    type=["csv"]
)

uploaded_complaints = st.sidebar.file_uploader(
    "Upload Complaints CSV",
    type=["csv"]
)

# =========================================================
# LIVE CSV REPLACEMENT
# =========================================================

if uploaded_device is not None:
    device_health = pd.read_csv(uploaded_device)

if uploaded_internet is not None:
    internet = pd.read_csv(uploaded_internet)

if uploaded_complaints is not None:
    complaints = pd.read_csv(uploaded_complaints)

# =========================================================
# FILTER DATA
# =========================================================

if selected_state == "All":

    filtered_schools = schools.copy()
    filtered_students = students.copy()
    filtered_teachers = teachers.copy()
    filtered_devices = devices.copy()

else:

    filtered_schools = schools[
        schools["state"] == selected_state
    ]

    filtered_students = students[
        students["school_id"].isin(
            filtered_schools["school_id"]
        )
    ]

    filtered_teachers = teachers[
        teachers["school_id"].isin(
            filtered_schools["school_id"]
        )
    ]

    filtered_devices = devices[
        devices["school_id"].isin(
            filtered_schools["school_id"]
        )
    ]

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <a href="/" target="_self" style="text-decoration:none;">
        <div class="main-title">
            Schoolnet Integrated Monitoring Dashboard
        </div>
    </a>

    <div class="sub-title">
        Centralized monitoring platform for schools, students, teachers, devices, and learning outcomes
    </div>

    <hr>
    """,
    unsafe_allow_html=True
)

# =========================================================
# KPI VALUES
# =========================================================

total_schools = filtered_schools["school_id"].nunique()

total_students = filtered_students["total_students"].sum()

avg_improvement = round(
    filtered_students["improvement"].mean(),
    2
)

active_devices = filtered_devices[
    filtered_devices["status"] == "Active"
]["device_id"].count()

inactive_devices = filtered_devices[
    filtered_devices["status"] == "Inactive"
]["device_id"].count()

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

if page == "Executive Summary":

    st.markdown("### Executive Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Schools</div>
            <div class="kpi-value">{total_schools}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Students</div>
            <div class="kpi-value">{total_students}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Improvement</div>
            <div class="kpi-value">{avg_improvement}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Devices</div>
            <div class="kpi-value">{active_devices}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Inactive Devices</div>
            <div class="kpi-value">{inactive_devices}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)

        st.markdown("#### Student Improvement")

        fig1 = px.bar(
            filtered_students,
            x="school_id",
            y="improvement",
            color="grade",
            template="plotly_white"
        )

        fig1.update_layout(height=400)

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="section-box">', unsafe_allow_html=True)

        st.markdown("#### Device Usage Trend")

        fig2 = px.line(
            monthly_usage,
            x="month",
            y="device_hours",
            color="state",
            template="plotly_white"
        )

        fig2.update_layout(height=400)

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# DONOR MONITORING
# =========================================================

elif page == "Donor Monitoring":

    st.markdown("## Donor Monitoring Dashboard")

    total_devices = donor["devices_installed"].sum()

    active_devices = donor["active_devices"].sum()

    avg_improvement = round(
        donor["student_improvement"].mean(),
        1
    )

    avg_utilization = round(
        donor["funding_utilization"].mean(),
        1
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Devices Installed</div>
            <div class="kpi-value">{total_devices}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Devices</div>
            <div class="kpi-value">{active_devices}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Learning Improvement</div>
            <div class="kpi-value">{avg_improvement}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Funding Utilization</div>
            <div class="kpi-value">{avg_utilization}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### State-wise Usage Hours")

        fig1 = px.bar(
            donor,
            x="state",
            y="monthly_usage_hours",
            color="project_health",
            template="plotly_white"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Learning Improvement")

        fig2 = px.scatter(
            donor,
            x="content_usage_hours",
            y="student_improvement",
            size="active_devices",
            color="project_health",
            hover_name="school_name",
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Donor Monitoring Details")

    st.dataframe(
        donor,
        use_container_width=True
    )