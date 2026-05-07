import streamlit as st
import requests

# ==============================
# Basic Settings
# ==============================

LOGIN_FLOW_URL = st.secrets["LOGIN_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="Attendance System Login",
    page_icon="🔐",
    layout="centered"
)

# ==============================
# Custom Style
# ==============================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f6f9 !important;
        color: #111827 !important;
    }
    html, body, [class*="css"] {
        color: #111827 !important;
    }
    label, p, span, div {
        color: #111827;
    }
    [data-testid="stToolbar"],
    .stDeployButton,
    .stAppDeployButton,
    #MainMenu,
    footer,
    header {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 850px;
    }
    .stButton > button {
        height: 52px;
        border-radius: 12px;
        border: none;
        background-color: #2563eb !important;
        color: white !important;
        font-size: 16px;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stDateInput input,
    .stTimeInput input {
        background-color: white !important;
        color: #111827 !important;
        border-radius: 10px;
        border: 1px solid #d1d5db !important;
    }
    .stTextInput input::placeholder {
        color: #6b7280 !important;
    }
    .stRadio label,
    div[role="radiogroup"] label {
        color: #111827 !important;
    }
    .stSuccess {
        border-radius: 10px;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    [data-testid="stStatusWidget"] * {
        visibility: hidden !important;
        opacity: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# Session Initialization
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==============================
# Login Check
# ==============================

def login_check(employee_id, email):
    payload = {
        "secret": SECRET_KEY,
        "employeeId": employee_id.strip(),
        "email": email.strip()
    }

    response = requests.post(
        LOGIN_FLOW_URL,
        json=payload,
        timeout=30
    )

    if response.status_code not in [200, 201, 202]:
        return False, None, f"Flow error: {response.status_code}"

    result = response.json()

    if result.get("loginSuccess") is True and result.get("user"):
        return True, result.get("user"), ""

    return False, None, result.get("message", "Login failed")

# ==============================
# Login Page
# ==============================

if not st.session_state.logged_in or not st.session_state.user_info:
    st.title("🔐 Attendance System Login")
    st.caption("English Version")

    if st.button("中文版", use_container_width=True):
        st.switch_page("登入頁.py")

    st.divider()

    employee_id = st.text_input(
        "Employee ID *",
        placeholder="Enter your employee ID"
    )

    email = st.text_input(
        "Email *",
        placeholder="Enter your email address"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Login", use_container_width=True):
        errors = []

        if not employee_id.strip():
            errors.append("Employee ID")

        if not email.strip():
            errors.append("Email")

        if email.strip() and "@" not in email:
            errors.append("Invalid email format")

        if errors:
            st.error(
                "❌ Please check the following fields:\n\n- "
                + "\n- ".join(errors)
            )
            st.stop()

        try:
            success, user_info, message = login_check(
                employee_id,
                email
            )

            if success:
                st.session_state.logged_in = True
                st.session_state.user_info = user_info
                st.rerun()
            else:
                st.error(f"❌ {message}")

        except Exception as e:
            st.error(f"❌ Login failed: {str(e)}")

    st.stop()

# ==============================
# Main Menu
# ==============================

user_info = st.session_state.user_info

employee_name = user_info.get("name", "")
employee_id = user_info.get("employeeId", "")
department = user_info.get("department", "")

st.title("🕒 Attendance System")

st.success(f"Login successful: {employee_name} / {employee_id}")
st.caption(f"Department: {department}")

st.divider()
st.subheader("Please select a function")

if st.button("中文版", use_container_width=True):
    st.switch_page("登入頁.py")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📝 Attendance Request",
        use_container_width=True
    ):
        st.switch_page("pages/3_Attendance_Request_EN.py")

with col2:
    if st.button(
        "🔎 Application Records",
        use_container_width=True
    ):
        st.switch_page("pages/4_Application_Records_EN.py")

st.divider()

if st.button("Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()
