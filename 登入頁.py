import streamlit as st
import requests

# ==============================
# 基本設定
# ==============================

LOGIN_FLOW_URL = st.secrets["LOGIN_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]
ATTENDANCE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeQlonRowaqwFUks_HoaSt0QonFOnfklRtmez8oIl3dWDzwVg/viewform?usp=header"

st.set_page_config(
    page_title="登入頁",
    page_icon="🔐",
    layout="centered"
)

# ==============================
# 自訂樣式
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

    .stButton > button,
    .stButton > button[kind="secondary"],
    .stButton > button[kind="primary"] {
        height: 52px;
        border-radius: 12px;
        border: none !important;
        background-color: #38bdf8 !important;
        color: #ffffff !important;
        font-size: 16px;
        font-weight: 700;
        transition: 0.2s;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
    }

    .stButton > button:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
        border: none !important;
    }

    .stButton > button:focus,
    .stButton > button:active {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25) !important;
    }

    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .stLinkButton > a,
    .stLinkButton > a[kind="secondary"],
    .stLinkButton > a[kind="primary"] {
        height: 52px;
        border-radius: 12px;
        border: none !important;
        background-color: #38bdf8 !important;
        color: #ffffff !important;
        font-size: 16px;
        font-weight: 700;
        transition: 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
    }

    .stLinkButton > a:hover,
    .stLinkButton > a[kind="secondary"]:hover,
    .stLinkButton > a[kind="primary"]:hover {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
        text-decoration: none !important;
        border: none !important;
    }

    .stLinkButton > a:focus,
    .stLinkButton > a:active {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        text-decoration: none !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25) !important;
    }

    .stLinkButton > a p,
    .stLinkButton > a span,
    .stLinkButton > a div {
        color: #ffffff !important;
        font-weight: 700 !important;
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
# 初始化 Session
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==============================
# 登入驗證
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
        return False, None, f"Flow 錯誤：{response.status_code}"

    result = response.json()

    if result.get("loginSuccess") is True and result.get("user"):
        return True, result.get("user"), ""

    return False, None, result.get("message", "登入失敗")

# ==============================
# 尚未登入：登入頁
# ==============================

if not st.session_state.logged_in or not st.session_state.user_info:

    st.title("🔐 出勤系統登入")
    st.caption("Attendance System Login")

    if st.button("English Version", use_container_width=True):
        st.switch_page("pages/0_English_Login.py")

    st.divider()

    employee_id = st.text_input(
        "工號 Employee ID *",
        placeholder="請輸入工號"
    )

    email = st.text_input(
        "Mail *",
        placeholder="請輸入信箱"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("登入", use_container_width=True):

        errors = []

        if not employee_id.strip():
            errors.append("工號 Employee ID")

        if not email.strip():
            errors.append("Mail")

        if email.strip() and "@" not in email:
            errors.append("Mail 格式不正確")

        if errors:

            st.error(
                "❌ 以下欄位需確認：\n\n- "
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

            st.error(f"❌ 登入失敗：{str(e)}")

    st.stop()

# ==============================
# 登入成功：主選單
# ==============================

user_info = st.session_state.user_info

employee_name = user_info.get("name", "")
employee_id = user_info.get("employeeId", "")
department = user_info.get("department", "")

st.title("🕒 出勤系統")

st.success(f"登入成功：{employee_name} / {employee_id}")

st.caption(f"部門：{department}")

st.divider()

st.subheader("請選擇功能")

if st.button("English Version", use_container_width=True):
    st.switch_page("pages/0_English_Login.py")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ==============================
# 出勤申請
# ==============================

with col1:

    st.link_button(
        "📝 進入出勤申請",
        ATTENDANCE_FORM_URL,
        use_container_width=True
    )

# ==============================
# 申請紀錄查詢
# ==============================

with col2:

    if st.button(
        "🔎 申請紀錄查詢",
        use_container_width=True
    ):
        st.switch_page("pages/2_申請紀錄查詢.py")

# ==============================
# 登出
# ==============================

st.divider()

if st.button(
    "登出",
    use_container_width=True
):

    st.session_state.clear()

    st.rerun()