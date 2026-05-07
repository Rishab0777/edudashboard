import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Schoolnet Monitoring Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SAFE AUTO REFRESH (OPTIONAL)
# =========================================================
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, key="refresh")
except:
    pass

# =========================================================
# BASE PATH (IMPORTANT FOR STREAMLIT CLOUD)
# =========================================================
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_csv(file_name):
    return pd.read_csv(os.path.join(DATA_DIR, file_name))

# =========================================================
# LOAD DATA (CASE-SAFE FILE NAMES)
# IMPORTANT: Match EXACT GitHub filenames
# =========================================================
schools = load_csv("Schools.csv")
students = load_csv("Students.csv")
teachers = load_csv("Teachers.csv")
devices = load_csv("Devices.csv")
usage = load_csv("Usage.csv")
tal = load_csv("Tal_Register.csv")

device_health = load_csv("device_health.csv")
internet = load_csv("internet_uptime.csv")
complaints = load_csv("complaints.csv")
project_health = load_csv("project_health.csv")
monthly_usage = load_csv("monthly_usage.csv")
donor = load_csv("donor_monitoring.csv")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Schoolnet Platform")

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
state_options = ["All"] + sorted(schools["state"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", state_options)

# =========================================================
# FILTER DATA
# =========================================================
if selected_state != "All":
    schools_f = schools[schools["state"] == selected_state]
    students_f = students[students["school_id"].isin(schools_f["school_id"])]
    teachers_f = teachers[teachers["school_id"].isin(schools_f["school_id"])]
    devices_f = devices[devices["school_id"].isin(schools_f["school_id"])]
else:
    schools_f = schools
    students_f = students
    teachers_f = teachers
    devices_f = devices

# =========================================================
# HEADER
# =========================================================
st.title("Schoolnet Integrated Monitoring Dashboard")
st.markdown("Centralized monitoring platform for schools, students, devices, and learning outcomes")
st.markdown("---")

# =========================================================
# KPI CALCULATIONS (SAFE)
# =========================================================
total_schools = schools_f["school_id"].nunique()

total_students = students_f["total_students"].sum() if "total_students" in students_f.columns else 0

avg_improvement = round(students_f["improvement"].mean(), 2) if "improvement" in students_f.columns else 0

active_devices = len(devices_f[devices_f["status"] == "Active"]) if "status" in devices_f.columns else 0
inactive_devices = len(devices_f[devices_f["status"] == "Inactive"]) if "status" in devices_f.columns else 0

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================
if page == "Executive Summary":

    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Schools", total_schools)
    col2.metric("Total Students", total_students)
    col3.metric("Avg Improvement", f"{avg_improvement}%")
    col4.metric("Active Devices", active_devices)

    st.markdown("### Student Improvement")

    if "improvement" in students_f.columns:
        fig1 = px.bar(students_f, x="school_id", y="improvement")
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Device Usage Trend")

    if "device_hours" in monthly_usage.columns:
        fig2 = px.line(monthly_usage, x="month", y="device_hours", color="state")
        st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# DONOR MONITORING
# =========================================================
elif page == "Donor Monitoring":

    st.subheader("Donor Monitoring Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Devices Installed", donor["devices_installed"].sum())
    col2.metric("Active Devices", donor["active_devices"].sum())
    col3.metric("Improvement", f"{donor['student_improvement'].mean():.1f}%")
    col4.metric("Funding Utilization", f"{donor['funding_utilization'].mean():.1f}%")

    st.markdown("### State-wise Usage")

    fig1 = px.bar(donor, x="state", y="monthly_usage_hours", color="project_health")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Learning Impact")

    fig2 = px.scatter(
        donor,
        x="content_usage_hours",
        y="student_improvement",
        size="active_devices",
        color="project_health",
        hover_name="school_name"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(donor, use_container_width=True)