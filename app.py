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
   
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

.kpi-blue {
    border-left: 5px solid #2563EB;
}

.kpi-green {
    border-left: 5px solid #16A34A;
}

.kpi-orange {
    border-left: 5px solid #EA580C;
}

.kpi-red {
    border-left: 5px solid #DC2626;
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

schools = pd.read_csv("data/Schools.csv")
students = pd.read_csv("data/Students.csv")
teachers = pd.read_csv("data/Teachers.csv")
devices = pd.read_csv("data/Devices.csv")
usage = pd.read_csv("data/Usage.csv")
tal = pd.read_csv("data/Tal_Register.csv")
# =========================================================
# TAL CALCULATED COLUMNS
# =========================================================

tal["attendance_percent"] = round(
    (tal["students_present"] / tal["class_strength"]) * 100,
    1
)

tal["learning_improvement"] = (
    tal["avg_score_post"]
    -
    tal["avg_score_pre"]
)

device_health = pd.read_csv("data/device_health.csv")
internet = pd.read_csv("data/internet_uptime.csv")
complaints = pd.read_csv("data/complaints.csv")
project_health = pd.read_csv("data/project_health.csv")
monthly_usage = pd.read_csv("data/monthly_usage.csv")
donor = pd.read_csv("data/donor_monitoring.csv")

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
        "TAL Register Entry",
        "TAL Analytics",
        "Teacher Efficiency Dashboard",
        "Attendance & Intervention Impact",
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

selected_date = st.sidebar.date_input(
    "Select Date"
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

tal["date"] = pd.to_datetime(
    tal["date"],
    format='mixed',
    errors='coerce'
)

invalid_dates = tal[tal["date"].isna()]

if not invalid_dates.empty:
    st.warning("Some rows contain invalid dates.")
    st.dataframe(invalid_dates)

if selected_state == "All":

    filtered_schools = schools.copy()
    filtered_students = students.copy()
    filtered_teachers = teachers.copy()
    filtered_devices = devices.copy()

    filtered_tal = tal.copy()

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

    filtered_tal = tal[
    tal["school_id"].isin(filtered_schools["school_id"])
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
        <div class="kpi-card kpi-blue">
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
# TAL REGISTER ENTRY
# =========================================================

elif page == "TAL Register Entry":

    st.markdown("## TAL Register Entry Form")

    st.markdown(
        "Fill classroom activity details below"
    )

    col1, col2 = st.columns(2)

    with col1:

        school_id = st.selectbox(
            "Select School",
            tal["school_id"].unique()
        )

        teacher_id = st.selectbox(
            "Select Teacher",
            tal["teacher_id"].unique()
        )

        grade = st.selectbox(
            "Select Grade",
            sorted(tal["grade"].unique())
        )

        subject = st.selectbox(
            "Select Subject",
            tal["subject"].unique()
        )

        topic = st.text_input(
            "Topic Being Taught"
        )

        learning_mode = st.selectbox(
            "Learning Mode",
            ["Digital", "Blended", "Traditional"]
        )

    with col2:

        class_strength = st.number_input(
            "Class Strength",
            min_value=1,
            value=40
        )

        students_present = st.number_input(
            "Students Present",
            min_value=0,
            value=35
        )

        device_used = st.selectbox(
            "Device Used",
            ["Yes", "No"]
        )

        device_id = st.text_input(
            "Device ID"
        )

        time_saved = st.number_input(
            "Time Saved (Minutes)",
            min_value=0,
            value=15
        )

    st.markdown("### Assessment Scores")

    c1, c2 = st.columns(2)

    with c1:

        avg_score_pre = st.number_input(
            "Pre Test Score",
            min_value=0,
            max_value=100,
            value=50
        )

    with c2:

        avg_score_post = st.number_input(
            "Post Test Score",
            min_value=0,
            max_value=100,
            value=65
        )

    if st.button("Submit TAL Entry"):

                # VALIDATION

        if students_present > class_strength:
            st.error(
                "Students present cannot exceed class strength"
            )
            st.stop()

        if avg_score_post < avg_score_pre:
            st.warning(
                "Post score is lower than pre score"
            )

        attendance_percent = round(
            (students_present / class_strength) * 100,
            1
        )

        learning_improvement = (
            avg_score_post - avg_score_pre
        )

        new_entry = pd.DataFrame({

            "tal_id":[tal["tal_id"].max() + 1],

            "date":[pd.Timestamp.today().strftime("%Y-%m-%d")],

            "school_id":[school_id],

            "teacher_id":[teacher_id],

            "grade":[grade],

            "subject":[subject],

            "topic":[topic],

            "class_strength":[class_strength],

            "students_present":[students_present],

            "attendance_percent":[attendance_percent],

            "device_used":[device_used],

            "device_id":[device_id],

            "time_saved":[time_saved],

            "learning_mode":[learning_mode],

            "avg_score_pre":[avg_score_pre],

            "avg_score_post":[avg_score_post],

            "learning_improvement":[learning_improvement]

        })


        # ADD ENTRY TO EXISTING CSV

        tal_updated = pd.concat(
            [tal, new_entry],
            ignore_index=True
        )

        tal_updated.to_csv(
            "data/Tal_Register.csv",
            index=False
        )

        st.success(
            "TAL Entry Submitted & Saved Successfully"
        )

        st.dataframe(
            new_entry,
            use_container_width=True
        )

# =========================================================
# TAL ANALYTICS
# =========================================================

elif page == "TAL Analytics":

    st.markdown("## TAL Analytics Dashboard")

    filtered_tal = filtered_tal.copy()

    if filtered_tal.empty:
        st.warning("No TAL records found for selected filters/date.")
        st.stop()
    # =====================================================
    # CALCULATIONS USING FILTERED DATA
    # =====================================================

    tal["attendance_percent"] = round(
    (
            tal["students_present"]
            /
            tal["class_strength"].replace(0, 1)
        ) * 100,
        1
    )


    filtered_tal["learning_improvement"] = (
        filtered_tal["avg_score_post"]
        -
        filtered_tal["avg_score_pre"]
    )

    avg_attendance = round(
        filtered_tal["attendance_percent"].mean(),
        1
    )

    avg_improvement = round(
        filtered_tal["learning_improvement"].mean(),
        1
    )

    digital_classes = filtered_tal[
        filtered_tal["device_used"] == "Yes"
    ].shape[0]

    traditional_classes = filtered_tal[
        filtered_tal["device_used"] == "No"
    ].shape[0]

    # =====================================================
    # KPI CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Attendance</div>
            <div class="kpi-value">{avg_attendance}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Learning Improvement</div>
            <div class="kpi-value">{avg_improvement}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Digital Classes</div>
            <div class="kpi-value">{digital_classes}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Traditional Classes</div>
            <div class="kpi-value">{traditional_classes}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # CHARTS
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Subject-wise Learning Improvement")

        fig1 = px.bar(
            filtered_tal,
            x="subject",
            y="learning_improvement",
            color="learning_mode",
            template="plotly_white"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Attendance by Grade")

        fig2 = px.line(
            filtered_tal,
            x="grade",
            y="attendance_percent",
            markers=True,
            color="learning_mode",
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # SEARCH + TABLE
    # =====================================================

    st.markdown("### TAL Register Analytics")

    search_teacher = st.text_input(
        "Search Teacher ID"
    )

    searched_tal = filtered_tal[
        filtered_tal["teacher_id"]
        .astype(str)
        .str.contains(
            search_teacher,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        searched_tal,
        use_container_width=True
    )

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    csv = searched_tal.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download TAL Report",
        data=csv,
        file_name="tal_report.csv",
        mime="text/csv"
    )

# =========================================================
# TEACHER EFFICIENCY DASHBOARD
# =========================================================

elif page == "Teacher Efficiency Dashboard":

    st.markdown("## Teacher Efficiency Dashboard")

    teacher_efficiency = tal.groupby(
        "teacher_id"
    ).agg({

        "time_saved":"mean",
        "attendance_percent":"mean",
        "avg_score_post":"mean"

    }).reset_index()

    teacher_efficiency["efficiency_score"] = round(

        (
            teacher_efficiency["time_saved"] * 0.3
            +
            teacher_efficiency["attendance_percent"] * 0.4
            +
            teacher_efficiency["avg_score_post"] * 0.3
        ),

        1

    )

    avg_score = round(
        teacher_efficiency[
            "efficiency_score"
        ].mean(),
        1
    )

    if not teacher_efficiency.empty:
        best_teacher = teacher_efficiency.sort_values(
            by="efficiency_score",
            ascending=False
        ).iloc[0]["teacher_id"]
    else:
        best_teacher = "N/A"

    total_teachers = teacher_efficiency.shape[0]

    avg_time_saved = round(
        teacher_efficiency["time_saved"].mean(),
        1
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Efficiency</div>
            <div class="kpi-value">{avg_score}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Top Teacher</div>
            <div class="kpi-value">{best_teacher}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Teachers Evaluated</div>
            <div class="kpi-value">{total_teachers}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Time Saved</div>
            <div class="kpi-value">{avg_time_saved}m</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

        # LOW PERFORMANCE ALERT

    low_perf = tal[
        tal["learning_improvement"] < 5
    ]

    if low_perf.shape[0] > 0:

        st.error(
            f"{low_perf.shape[0]} low performing classes need intervention"
        )

        st.dataframe(
            low_perf[
                [
                    "school_id",
                    "teacher_id",
                    "subject",
                    "learning_improvement"
                ]
            ],
            use_container_width=True
        )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Teacher Efficiency Scores")

        fig1 = px.bar(
            teacher_efficiency,
            x="teacher_id",
            y="efficiency_score",
            template="plotly_white"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Time Saved by Teachers")

        fig2 = px.scatter(
            teacher_efficiency,
            x="attendance_percent",
            y="avg_score_post",
            size="time_saved",
            hover_name="teacher_id",
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("### Teacher Performance Table")

    st.dataframe(
        teacher_efficiency,
        use_container_width=True
    )

# =========================================================
# ATTENDANCE & INTERVENTION IMPACT
# =========================================================

elif page == "Attendance & Intervention Impact":

    st.markdown(
        "## Attendance & Intervention Impact"
    )

    tal["improvement"] = (
        tal["avg_score_post"]
        -
        tal["avg_score_pre"]
    )

    avg_pre = round(
        tal["avg_score_pre"].mean(),
        1
    )

    avg_post = round(
        tal["avg_score_post"].mean(),
        1
    )

    avg_growth = round(
        tal["improvement"].mean(),
        1
    )

    avg_attendance = round(
        tal["attendance_percent"].mean(),
        1
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Pre Score</div>
            <div class="kpi-value">{avg_pre}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Post Score</div>
            <div class="kpi-value">{avg_post}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Learning Growth</div>
            <div class="kpi-value">{avg_growth}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Attendance Rate</div>
            <div class="kpi-value">{avg_attendance}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Pre vs Post Scores")

        fig1 = px.bar(
            tal,
            x="subject",
            y=["avg_score_pre","avg_score_post"],
            barmode="group",
            template="plotly_white"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            '<div class="section-box">',
            unsafe_allow_html=True
        )

        st.markdown("### Attendance vs Improvement")

        fig2 = px.scatter(
            tal,
            x="attendance_percent",
            y="improvement",
            color="learning_mode",
            size="time_saved",
            hover_name="subject",
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("### Intervention Impact Data")

    st.dataframe(
        tal,
        use_container_width=True
    )



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


# =========================================================
# DEVICE HEALTH MONITORING
# =========================================================

elif page == "Device Health Monitoring":

    st.markdown("## Device Health Monitoring")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.pie(
            device_health,
            names="status",
            title="Device Status Distribution",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig2 = px.bar(
            device_health,
            x="device_id",
            y="battery_health",
            color="status",
            title="Battery Health by Device",
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Device Details")

    st.dataframe(device_health)

# =========================================================
# INTERNET MONITORING
# =========================================================

elif page == "Internet Monitoring":

    st.markdown("## Internet Monitoring Dashboard")

    stable_count = internet[internet["status"] == "Stable"].shape[0]

    unstable_count = internet[
        internet["status"] == "Unstable"
    ].shape[0]

    critical_count = internet[
        internet["status"] == "Critical"
    ].shape[0]

    avg_uptime = round(
        internet["internet_uptime"].mean(),
        2
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Uptime</div>
            <div class="kpi-value">{avg_uptime}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Stable Schools</div>
            <div class="kpi-value">{stable_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Unstable Schools</div>
            <div class="kpi-value">{unstable_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Critical Schools</div>
            <div class="kpi-value">{critical_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Internet Uptime by School")

        fig1 = px.bar(
            internet,
            x="school_name",
            y="internet_uptime",
            color="status",
            template="plotly_white"
        )

        fig1.update_layout(height=420)

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Average Internet Speed")

        fig2 = px.line(
            internet,
            x="school_name",
            y="avg_speed_mbps",
            markers=True,
            template="plotly_white"
        )

        fig2.update_layout(height=420)

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Internet Monitoring Details")

    st.dataframe(
        internet,
        use_container_width=True
    )

# =========================================================
# COMPLAINT TRACKING
# =========================================================

elif page == "Complaint Tracking":

    st.markdown("## Complaint Tracking Dashboard")

    open_tickets = complaints[
        complaints["status"] == "Open"
    ].shape[0]

    resolved_tickets = complaints[
        complaints["status"] == "Resolved"
    ].shape[0]

    avg_days = round(
        complaints["days_open"].mean(),
        1
    )

    high_priority = complaints[
        complaints["priority"] == "High"
    ].shape[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Open Tickets</div>
            <div class="kpi-value">{open_tickets}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Resolved Tickets</div>
            <div class="kpi-value">{resolved_tickets}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Days Open</div>
            <div class="kpi-value">{avg_days}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">High Priority Issues</div>
            <div class="kpi-value">{high_priority}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Complaint Status")

        fig1 = px.pie(
            complaints,
            names="status",
            template="plotly_white"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Ticket Aging Analysis")

        fig2 = px.bar(
            complaints,
            x="ticket_id",
            y="days_open",
            color="priority",
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Complaint Details")

    st.dataframe(
        complaints,
        use_container_width=True
    )

# =========================================================
# PROJECT HEALTH CENTER
# =========================================================

elif page == "Project Health Center":

    st.markdown("## Project Health Center")

    excellent = project_health[
        project_health["overall_health"] == "Excellent"
    ].shape[0]

    good = project_health[
        project_health["overall_health"] == "Good"
    ].shape[0]

    critical = project_health[
        project_health["overall_health"] == "Critical"
    ].shape[0]

    avg_engagement = round(
        project_health["student_engagement"].mean(),
        1
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Excellent Projects</div>
            <div class="kpi-value">{excellent}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Good Projects</div>
            <div class="kpi-value">{good}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Critical Projects</div>
            <div class="kpi-value">{critical}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Student Engagement</div>
            <div class="kpi-value">{avg_engagement}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Overall Health Distribution")

        fig1 = px.pie(
            project_health,
            names="overall_health",
            template="plotly_white"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:

        st.markdown('<div class="section-box">',
        unsafe_allow_html=True)

        st.markdown("### Device Usage vs Student Engagement")

        fig2 = px.scatter(
            project_health,
            x="device_usage_score",
            y="student_engagement",
            color="overall_health",
            size="teacher_engagement",
            hover_name="school_id",
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Project Health Details")

    st.dataframe(
        project_health,
        use_container_width=True
    )