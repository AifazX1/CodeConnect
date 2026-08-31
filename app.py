```python
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
from datetime import date, datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CodeConnect",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #f7f8fc;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Main title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0;
    }

    /* Cards */
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-title {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 750;
    }

    /* Login */
    .login-box {
        max-width: 450px;
        margin: 60px auto;
        background: white;
        padding: 40px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
    }

    /* Section headings */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    /* Hide Streamlit decoration */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def init_supabase() -> Client:

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


try:
    supabase = init_supabase()

except Exception as e:

    st.error("Unable to connect to Supabase.")

    st.code(str(e))

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ============================================================
# LOGIN
# ============================================================

def login_screen():

    st.markdown(
        "<div style='text-align:center; margin-top:50px;'>"
        "<div style='font-size:55px;'>💻</div>"
        "<h1>CodeConnect</h1>"
        "<p style='color:#6b7280;'>Coding Awareness Program Management System</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("### 🔐 Administrator Login")

    email = st.text_input(
        "Email",
        placeholder="admin@example.com"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_button = st.button(
        "Login",
        type="primary",
        use_container_width=True
    )

    if login_button:

        if not email or not password:

            st.warning("Please enter your email and password.")

        else:

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                if response.user:

                    st.session_state.logged_in = True
                    st.session_state.user_email = response.user.email

                    st.success("Login successful!")

                    st.rerun()

            except Exception as e:

                st.error("Invalid email or password.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;color:#9ca3af;margin-top:30px;'>"
        "CodeConnect • Community Engagement Project"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.logged_in = False
    st.session_state.user_email = None

    st.rerun()


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_students():

    response = (
        supabase
        .table("students")
        .select(
            "id, registration_id, name, age, gender, "
            "school_id, class_name, parent_name, contact, "
            "coding_level, session_attended, registration_date, "
            "schools(school_name)"
        )
        .order("id", desc=True)
        .execute()
    )

    return response.data or []


def get_schools():

    response = (
        supabase
        .table("schools")
        .select("*")
        .order("school_name")
        .execute()
    )

    return response.data or []


def get_sessions():

    response = (
        supabase
        .table("sessions")
        .select("*")
        .order("session_date", desc=True)
        .execute()
    )

    return response.data or []


def get_attendance():

    response = (
        supabase
        .table("session_attendance")
        .select(
            "id, student_id, session_id, attended, "
            "students(name, registration_id), "
            "sessions(session_name, session_date)"
        )
        .order("id", desc=True)
        .execute()
    )

    return response.data or []


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.markdown(
        "<div class='main-title'>Dashboard</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Overview of the Coding Awareness Program</div>",
        unsafe_allow_html=True
    )

    st.write("")

    students = get_students()
    schools = get_schools()
    sessions = get_sessions()

    total_students = len(students)
    total_schools = len(schools)
    total_sessions = len(sessions)

    attended_count = sum(
        1 for student in students
        if student.get("session_attended") is True
    )

    attendance_percentage = (
        round((attended_count / total_students) * 100)
        if total_students
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "👨‍🎓 Students",
            total_students
        )

    with c2:
        st.metric(
            "🏫 Schools",
            total_schools
        )

    with c3:
        st.metric(
            "💻 Sessions",
            total_sessions
        )

    with c4:
        st.metric(
            "📅 Attendance",
            f"{attendance_percentage}%"
        )

    st.divider()

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # CLASS DISTRIBUTION
    # --------------------------------------------------------

    with col1:

        st.subheader("Students by Class")

        if students:

            class_data = {}

            for student in students:

                class_name = student.get("class_name") or "Unknown"

                class_data[class_name] = (
                    class_data.get(class_name, 0) + 1
                )

            chart_df = pd.DataFrame(
                {
                    "Class": list(class_data.keys()),
                    "Students": list(class_data.values())
                }
            )

            fig = px.bar(
                chart_df,
                x="Class",
                y="Students",
                title="Class-wise Registration"
            )

            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No student data available.")

    # --------------------------------------------------------
    # CODING LEVEL
    # --------------------------------------------------------

    with col2:

        st.subheader("Coding Levels")

        if students:

            levels = {}

            for student in students:

                level = student.get("coding_level") or "Unknown"

                levels[level] = levels.get(level, 0) + 1

            level_df = pd.DataFrame(
                {
                    "Level": list(levels.keys()),
                    "Students": list(levels.values())
                }
            )

            fig = px.pie(
                level_df,
                names="Level",
                values="Students",
                hole=0.45
            )

            fig.update_layout(
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No student data available.")

    st.divider()

    # --------------------------------------------------------
    # RECENT STUDENTS
    # --------------------------------------------------------

    st.subheader("🆕 Recent Registrations")

    if students:

        recent = []

        for student in students[:8]:

            school_data = student.get("schools")

            school_name = (
                school_data.get("school_name")
                if isinstance(school_data, dict)
                else "Unknown"
            )

            recent.append(
                {
                    "Registration ID": student.get("registration_id"),
                    "Name": student.get("name"),
                    "School": school_name,
                    "Class": student.get("class_name"),
                    "Coding Level": student.get("coding_level")
                }
            )

        st.dataframe(
            pd.DataFrame(recent),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No registrations yet.")


# ============================================================
# STUDENT REGISTRATION
# ============================================================

def register_student():

    st.markdown(
        "<div class='main-title'>Register Student</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Add a child to the Coding Awareness Program</div>",
        unsafe_allow_html=True
    )

    st.write("")

    schools = get_schools()

    if not schools:

        st.warning(
            "No schools have been added yet. "
            "Please add a school from the Schools section."
        )

        return

    school_options = {
        school["school_name"]: school["id"]
        for school in schools
    }

    with st.form("student_registration"):

        st.subheader("👤 Child Information")

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Full Name *",
                placeholder="Enter child's name"
            )

            age = st.number_input(
                "Age",
                min_value=5,
                max_value=18,
                value=12
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

            class_name = st.selectbox(
                "Class",
                [
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12"
                ]
            )

        with col2:

            school_name = st.selectbox(
                "School *",
                list(school_options.keys())
            )

            parent_name = st.text_input(
                "Parent / Guardian Name",
                placeholder="Enter parent or guardian name"
            )

            contact = st.text_input(
                "Contact Number",
                placeholder="Enter contact number"
            )

            coding_level = st.selectbox(
                "Coding Level",
                [
                    "Beginner",
                    "Intermediate",
                    "Advanced"
                ]
            )

        st.subheader("💻 Program Information")

        session_attended = st.checkbox(
            "Student has attended a coding awareness session"
        )

        submitted = st.form_submit_button(
            "Register Student",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not name.strip():

                st.error("Please enter the student's name.")

            else:

                try:

                    # Generate registration ID
                    existing_students = get_students()

                    registration_id = (
                        f"CC{len(existing_students) + 1:03d}"
                    )

                    supabase.table("students").insert(
                        {
                            "registration_id": registration_id,
                            "name": name.strip(),
                            "age": age,
                            "gender": gender,
                            "school_id": school_options[school_name],
                            "class_name": class_name,
                            "parent_name": parent_name.strip(),
                            "contact": contact.strip(),
                            "coding_level": coding_level,
                            "session_attended": session_attended
                        }
                    ).execute()

                    st.success(
                        f"Student registered successfully! "
                        f"Registration ID: {registration_id}"
                    )

                    st.balloons()

                except Exception as e:

                    st.error("Unable to register student.")

                    st.code(str(e))


# ============================================================
# STUDENT DATABASE
# ============================================================

def student_database():

    st.markdown(
        "<div class='main-title'>Student Records</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>View and manage registered students</div>",
        unsafe_allow_html=True
    )

    st.write("")

    students = get_students()

    if not students:

        st.info(
            "No students registered yet."
        )

        return

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = st.text_input(
        "🔎 Search students",
        placeholder="Search by name, registration ID, school..."
    )

    filtered_students = students

    if search:

        search_lower = search.lower()

        filtered_students = [

            student for student in students

            if (
                search_lower in str(
                    student.get("name", "")
                ).lower()
                or
                search_lower in str(
                    student.get("registration_id", "")
                ).lower()
                or
                search_lower in str(
                    student.get("class_name", "")
                ).lower()
            )
        ]

    st.write(
        f"Showing **{len(filtered_students)}** student(s)"
    )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    table_data = []

    for student in filtered_students:

        school_data = student.get("schools")

        school_name = (
            school_data.get("school_name")
            if isinstance(school_data, dict)
            else "Unknown"
        )

        table_data.append(
            {
                "ID": student.get("registration_id"),
                "Name": student.get("name"),
                "Age": student.get("age"),
                "Gender": student.get("gender"),
                "School": school_name,
                "Class": student.get("class_name"),
                "Coding Level": student.get("coding_level"),
                "Attended": (
                    "Yes"
                    if student.get("session_attended")
                    else "No"
                )
            }
        )

    st.dataframe(
        pd.DataFrame(table_data),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------------
    # EDIT / DELETE
    # --------------------------------------------------------

    st.subheader("✏️ Manage Student")

    student_ids = [
        student["registration_id"]
        for student in students
    ]

    selected_id = st.selectbox(
        "Select student",
        student_ids
    )

    selected_student = next(
        (
            s for s in students
            if s["registration_id"] == selected_id
        ),
        None
    )

    if selected_student:

        edit_col, delete_col = st.columns(2)

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        with edit_col:

            with st.expander("✏️ Edit Student", expanded=False):

                schools = get_schools()

                school_options = {
                    school["school_name"]: school["id"]
                    for school in schools
                }

                current_school = "Unknown"

                school_data = selected_student.get("schools")

                if isinstance(school_data, dict):

                    current_school = school_data.get(
                        "school_name",
                        "Unknown"
                    )

                school_names = list(school_options.keys())

                if current_school not in school_names and school_names:

                    current_school = school_names[0]

                with st.form("edit_student"):

                    new_name = st.text_input(
                        "Name",
                        value=selected_student.get("name", "")
                    )

                    new_age = st.number_input(
                        "Age",
                        min_value=5,
                        max_value=18,
                        value=int(
                            selected_student.get("age") or 12
                        )
                    )

                    new_gender = st.selectbox(
                        "Gender",
                        ["Male", "Female", "Other"],
                        index=max(
                            0,
                            ["Male", "Female", "Other"].index(
                                selected_student.get(
                                    "gender",
                                    "Male"
                                )
                            )
                        )
                    )

                    new_class = st.selectbox(
                        "Class",
                        [
                            "5",
                            "6",
                            "7",
                            "8",
                            "9",
                            "10",
                            "11",
                            "12"
                        ],
                        index=(
                            [
                                "5",
                                "6",
                                "7",
                                "8",
                                "9",
                                "10",
                                "11",
                                "12"
                            ].index(
                                str(
                                    selected_student.get(
                                        "class_name",
                                        "8"
                                    )
                                )
                            )
                            if str(
                                selected_student.get(
                                    "class_name",
                                    "8"
                                )
                            ) in [
                                "5",
                                "6",
                                "7",
                                "8",
                                "9",
                                "10",
                                "11",
                                "12"
                            ]
                            else 0
                        )
                    )

                    new_school = st.selectbox(
                        "School",
                        school_names,
                        index=(
                            school_names.index(current_school)
                            if current_school in school_names
                            else 0
                        )
                    )

                    new_parent = st.text_input(
                        "Parent / Guardian",
                        value=selected_student.get(
                            "parent_name",
                            ""
                        ) or ""
                    )

                    new_contact = st.text_input(
                        "Contact",
                        value=selected_student.get(
                            "contact",
                            ""
                        ) or ""
                    )

                    new_level = st.selectbox(
                        "Coding Level",
                        [
                            "Beginner",
                            "Intermediate",
                            "Advanced"
                        ],
                        index=(
                            [
                                "Beginner",
                                "Intermediate",
                                "Advanced"
                            ].index(
                                selected_student.get(
                                    "coding_level",
                                    "Beginner"
                                )
                            )
                        )
                    )

                    new_attended = st.checkbox(
                        "Session attended",
                        value=bool(
                            selected_student.get(
                                "session_attended"
                            )
                        )
                    )

                    update_button = st.form_submit_button(
                        "Save Changes",
                        type="primary"
                    )

                    if update_button:

                        try:

                            supabase.table(
                                "students"
                            ).update(
                                {
                                    "name": new_name.strip(),
                                    "age": new_age,
                                    "gender": new_gender,
                                    "school_id": school_options[
                                        new_school
                                    ],
                                    "class_name": new_class,
                                    "parent_name": new_parent.strip(),
                                    "contact": new_contact.strip(),
                                    "coding_level": new_level,
                                    "session_attended": new_attended
                                }
                            ).eq(
                                "id",
                                selected_student["id"]
                            ).execute()

                            st.success(
                                "Student updated successfully."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "Unable to update student."
                            )

                            st.code(str(e))

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        with delete_col:

            with st.expander("🗑️ Delete Student"):

                st.warning(
                    f"You are about to delete "
                    f"**{selected_student['name']}**."
                )

                confirm_delete = st.checkbox(
                    "I understand that this cannot be undone."
                )

                if st.button(
                    "Delete Student",
                    type="secondary"
                ):

                    if not confirm_delete:

                        st.error(
                            "Please confirm deletion first."
                        )

                    else:

                        try:

                            supabase.table(
                                "students"
                            ).delete().eq(
                                "id",
                                selected_student["id"]
                            ).execute()

                            st.success(
                                "Student deleted successfully."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "Unable to delete student."
                            )

                            st.code(str(e))


# ============================================================
# SCHOOLS
# ============================================================

def schools_page():

    st.markdown(
        "<div class='main-title'>Schools</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Manage participating schools</div>",
        unsafe_allow_html=True
    )

    st.write("")

    schools = get_schools()

    col1, col2 = st.columns([1, 1])

    # --------------------------------------------------------
    # ADD SCHOOL
    # --------------------------------------------------------

    with col1:

        st.subheader("🏫 Add School")

        with st.form("add_school"):

            school_name = st.text_input(
                "School Name"
            )

            city = st.text_input(
                "City"
            )

            add_button = st.form_submit_button(
                "Add School",
                type="primary"
            )

            if add_button:

                if not school_name.strip():

                    st.error(
                        "Please enter a school name."
                    )

                else:

                    try:

                        supabase.table(
                            "schools"
                        ).insert(
                            {
                                "school_name":
                                    school_name.strip(),
                                "city":
                                    city.strip()
                            }
                        ).execute()

                        st.success(
                            "School added successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Unable to add school."
                        )

                        st.code(str(e))

    # --------------------------------------------------------
    # SCHOOL LIST
    # --------------------------------------------------------

    with col2:

        st.subheader("📋 Participating Schools")

        if schools:

            school_data = []

            for school in schools:

                school_data.append(
                    {
                        "School": school.get(
                            "school_name"
                        ),
                        "City": school.get(
                            "city"
                        ) or "-"
                    }
                )

            st.dataframe(
                pd.DataFrame(school_data),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No schools added yet."
            )


# ============================================================
# CODING SESSIONS
# ============================================================

def sessions_page():

    st.markdown(
        "<div class='main-title'>Coding Sessions</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Manage coding awareness sessions</div>",
        unsafe_allow_html=True
    )

    st.write("")

    sessions = get_sessions()

    col1, col2 = st.columns([1, 1])

    # --------------------------------------------------------
    # ADD SESSION
    # --------------------------------------------------------

    with col1:

        st.subheader("💻 Create Session")

        with st.form("create_session"):

            session_name = st.text_input(
                "Session Name",
                placeholder="Python for Beginners"
            )

            topic = st.text_input(
                "Topic",
                placeholder="Introduction to Python"
            )

            session_date = st.date_input(
                "Session Date",
                value=date.today()
            )

            description = st.text_area(
                "Description"
            )

            create_button = st.form_submit_button(
                "Create Session",
                type="primary"
            )

            if create_button:

                if not session_name.strip():

                    st.error(
                        "Please enter a session name."
                    )

                else:

                    try:

                        supabase.table(
                            "sessions"
                        ).insert(
                            {
                                "session_name":
                                    session_name.strip(),
                                "topic":
                                    topic.strip(),
                                "session_date":
                                    str(session_date),
                                "description":
                                    description.strip()
                            }
                        ).execute()

                        st.success(
                            "Session created successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Unable to create session."
                        )

                        st.code(str(e))

    # --------------------------------------------------------
    # SESSION LIST
    # --------------------------------------------------------

    with col2:

        st.subheader("📚 Sessions")

        if sessions:

            session_data = []

            for session in sessions:

                session_data.append(
                    {
                        "Session":
                            session.get("session_name"),
                        "Topic":
                            session.get("topic"),
                        "Date":
                            session.get("session_date")
                    }
                )

            st.dataframe(
                pd.DataFrame(session_data),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No sessions created yet."
            )


# ============================================================
# ATTENDANCE
# ============================================================

def attendance_page():

    st.markdown(
        "<div class='main-title'>Attendance</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Record coding session attendance</div>",
        unsafe_allow_html=True
    )

    st.write("")

    students = get_students()
    sessions = get_sessions()

    if not students:

        st.info(
            "Register students before recording attendance."
        )

        return

    if not sessions:

        st.info(
            "Create a coding session before recording attendance."
        )

        return

    student_options = {
        f"{s['registration_id']} — {s['name']}":
            s["id"]
        for s in students
    }

    session_options = {
        f"{s['session_name']} — {s['session_date']}":
            s["id"]
        for s in sessions
    }

    with st.form("attendance_form"):

        student = st.selectbox(
            "Student",
            list(student_options.keys())
        )

        session = st.selectbox(
            "Coding Session",
            list(session_options.keys())
        )

        attended = st.checkbox(
            "Present",
            value=True
        )

        submit_attendance = st.form_submit_button(
            "Save Attendance",
            type="primary"
        )

        if submit_attendance:

            try:

                supabase.table(
                    "session_attendance"
                ).upsert(
                    {
                        "student_id":
                            student_options[student],
                        "session_id":
                            session_options[session],
                        "attended":
                            attended
                    },
                    on_conflict="student_id,session_id"
                ).execute()

                st.success(
                    "Attendance saved successfully."
                )

            except Exception as e:

                st.error(
                    "Unable to save attendance."
                )

                st.code(str(e))

    st.divider()

    st.subheader("📋 Attendance Records")

    attendance = get_attendance()

    if attendance:

        rows = []

        for record in attendance:

            student_data = record.get("students") or {}
            session_data = record.get("sessions") or {}

            rows.append(
                {
                    "Student":
                        student_data.get("name", "Unknown"),
                    "Registration ID":
                        student_data.get(
                            "registration_id",
                            "-"
                        ),
                    "Session":
                        session_data.get(
                            "session_name",
                            "Unknown"
                        ),
                    "Date":
                        session_data.get(
                            "session_date",
                            "-"
                        ),
                    "Status":
                        "Present"
                        if record.get("attended")
                        else "Absent"
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No attendance records yet."
        )


# ============================================================
# REPORTS
# ============================================================

def reports_page():

    st.markdown(
        "<div class='main-title'>Reports & Analytics</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Program statistics and downloadable data</div>",
        unsafe_allow_html=True
    )

    st.write("")

    students = get_students()

    if not students:

        st.info(
            "No student data available for reports."
        )

        return

    # --------------------------------------------------------
    # GENDER
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        gender_data = {}

        for student in students:

            gender = student.get(
                "gender",
                "Unknown"
            )

            gender_data[gender] = (
                gender_data.get(gender, 0) + 1
            )

        gender_df = pd.DataFrame(
            {
                "Gender": list(gender_data.keys()),
                "Students": list(gender_data.values())
            }
        )

        fig = px.pie(
            gender_df,
            names="Gender",
            values="Students",
            title="Students by Gender"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # SCHOOL
    # --------------------------------------------------------

    with col2:

        school_data = {}

        for student in students:

            school = student.get("schools")

            school_name = (
                school.get("school_name")
                if isinstance(school, dict)
                else "Unknown"
            )

            school_data[school_name] = (
                school_data.get(school_name, 0) + 1
            )

        school_df = pd.DataFrame(
            {
                "School": list(school_data.keys()),
                "Students": list(school_data.values())
            }
        )

        fig = px.bar(
            school_df,
            x="School",
            y="Students",
            title="Students by School"
        )

        fig.update_layout(
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # --------------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------------

    st.subheader("📥 Export Student Data")

    export_rows = []

    for student in students:

        school = student.get("schools")

        school_name = (
            school.get("school_name")
            if isinstance(school, dict)
            else "Unknown"
        )

        export_rows.append(
            {
                "Registration ID":
                    student.get("registration_id"),
                "Name":
                    student.get("name"),
                "Age":
                    student.get("age"),
                "Gender":
                    student.get("gender"),
                "School":
                    school_name,
                "Class":
                    student.get("class_name"),
                "Parent / Guardian":
                    student.get("parent_name"),
                "Contact":
                    student.get("contact"),
                "Coding Level":
                    student.get("coding_level"),
                "Session Attended":
                    student.get(
                        "session_attended"
                    )
            }
        )

    export_df = pd.DataFrame(export_rows)

    csv = export_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Student CSV",
        data=csv,
        file_name="codeconnect_students.csv",
        mime="text/csv",
        type="primary"
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

if not st.session_state.logged_in:

    login_screen()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style='text-align:center;padding:15px 0 25px 0;'>
            <div style='font-size:42px;'>💻</div>
            <h2 style='margin:0;'>CodeConnect</h2>
            <p style='font-size:12px;color:#9ca3af !important;'>
                Coding Awareness Program
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        f"""
        <div style='padding:8px 0;'>
            <span style='font-size:12px;color:#9ca3af !important;'>
                SIGNED IN AS
            </span><br>
            <b>{st.session_state.user_email}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👨‍🎓 Register Student",
            "📋 Student Records",
            "🏫 Schools",
            "💻 Coding Sessions",
            "📅 Attendance",
            "📊 Reports"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "🏠 Dashboard":

    dashboard()

elif page == "👨‍🎓 Register Student":

    register_student()

elif page == "📋 Student Records":

    student_database()

elif page == "🏫 Schools":

    schools_page()

elif page == "💻 Coding Sessions":

    sessions_page()

elif page == "📅 Attendance":

    attendance_page()

elif page == "📊 Reports":

    reports_page()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br><br>
    <div style='text-align:center;color:#9ca3af;font-size:12px;'>
        CodeConnect • Coding Awareness Program • Community Engagement Project
    </div>
    """,
    unsafe_allow_html=True
)
```
