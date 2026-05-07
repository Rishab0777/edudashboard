import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# SAFE IMPORT (AUTO REFRESH OPTIONAL)
# =========================================================

try:
    from streamlit_autorefresh import st_autorefresh
    AUTO_REFRESH = True
except:
    AUTO_REFRESH = False

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Schoolnet Monitoring Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# AUTO REFRESH (SAFE)
# =========================================================

if AUTO_REFRESH:
    st_autorefresh(interval=60000, key="refresh")

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background-color: #F4F6F9;
}

.block-container {
    padding-top: 3rem !important;
    padding-bottom: 1rem;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: white;
}

.sidebar-title {
    font-size: 24px;
    font-weight: 700;
    color: white;
    margin-bottom: 18px;
}

.filter-heading {
    font-size: 13px;
    font-weight: 600;
    color: #D1D5DB;
    margin-top: 14px;
    margin-bottom: 8px;
}

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
}

.kpi-value {
    font-size: 28px;
    font-weight: 600;
}

.section-box {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SAFE DATA LOADING (FIX FOR STREAMLIT CLOUD)
# =========================================================

@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

schools = load_csv("data/schools.csv")
students = load_csv("data/students.csv")
teachers = load_csv("data/teachers.csv")
devices = load_csv("data/devices.csv")
usage = load_csv("data/usage.csv")
tal = load_csv("data/tal_register.csv")

device_health = load_csv("data/device_health.csv")
internet = load_csv("data/internet_uptime.csv")
complaints = load_csv("data/complaints.csv")
project_health = load_csv("data/project_health.csv")
monthly_usage = load_csv("data/monthly_usage.csv")
donor = load_csv("data/donor_monitoring.csv")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("<div class='sidebar-title'>Schoolnet Platform</div>", unsafe_allow_html=True)

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
# STATE FILTER (SAFE)
# =========================================================

if "state" in schools.columns:
    state_options = ["All"] + sorted(schools["state"].dropna().unique().tolist())
else:
    state_options = ["All"]

selected_state = st.sidebar.selectbox("Select State", state_options)

# =========================================================
# FILTER DATA (SAFE GUARDS)
# =========================================================

if selected_state == "All":
    filtered_schools = schools.copy()
    filtered_students = students.copy()
    filtered_devices = devices.copy()
else:
    filtered_schools = schools[schools["state"] == selected_state]
    filtered_students = students[students["school_id"].isin(filtered_schools["school_id"])]
    filtered_devices = devices[devices["school_id"].isin(filtered_schools["school_id"])]

# =========================================================
# HEADER
# =========================================================

st.title("Schoolnet Integrated Monitoring Dashboard")
st.write("Centralized monitoring platform for schools, students, teachers, devices, and outcomes")

# =========================================================
# KPI SAFE CALCULATIONS
# =========================================================

total_schools = filtered_schools["school_id"].nunique() if not filtered_schools.empty else 0

total_students = filtered_students["total_students"].sum() if "total_students" in filtered_students else 0

avg_improvement = round(filtered_students["improvement"].mean(), 2) if "improvement" in filtered_students else 0

active_devices = len(filtered_devices[filtered_devices.get("status", "") == "Active"])
inactive_devices = len(filtered_devices[filtered_devices.get("status", "") == "Inactive"])

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

if page == "Executive Summary":

    st.subheader("Executive Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Schools", total_schools)
    c2.metric("Total Students", total_students)
    c3.metric("Avg Improvement", avg_improvement)
    c4.metric("Active Devices", active_devices)

    if not filtered_students.empty:
        st.plotly_chart(
            px.bar(filtered_students, x="school_id", y="improvement"),
            use_container_width=True
        )

    if not monthly_usage.empty:
        st.plotly_chart(
            px.line(monthly_usage, x="month", y="device_hours"),
            use_container_width=True
        )

# =========================================================
# DONOR MONITORING
# =========================================================

elif page == "Donor Monitoring":

    st.subheader("Donor Monitoring Dashboard")

    if donor.empty:
        st.warning("No donor data found")
    else:
        st.metric("Devices Installed", donor["devices_installed"].sum())
        st.metric("Active Devices", donor["active_devices"].sum())
        st.metric("Avg Improvement", round(donor["student_improvement"].mean(), 2))
        st.metric("Funding Utilization", round(donor["funding_utilization"].mean(), 2))

        st.plotly_chart(
            px.bar(donor, x="state", y="monthly_usage_hours"),
            use_container_width=True
        )

        st.plotly_chart(
            px.scatter(
                donor,
                x="content_usage_hours",
                y="student_improvement",
                size="active_devices"
            ),
            use_container_width=True
        )

        st.dataframe(donor)