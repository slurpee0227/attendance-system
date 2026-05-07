import streamlit as st
import requests

# ==============================
# 基本設定
# ==============================

LOGIN_FLOW_URL = st.secrets["LOGIN_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

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

    /* =========================
       強制亮色背景與文字
    ========================= */

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

    /* =========================
       隱藏 Streamlit Cloud UI
    ========================= */

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

    /* =========================
       隱藏側邊欄
    ========================= */

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* =========================
       主區塊
    ========================= */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 850px;
    }

    /* =========================
       Button
    ========================= */

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

    /* =========================
       Input / Select / TextArea
    ========================= */

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

    /* =========================
       Radio
    ========================= */

    .stRadio label,
    div[role="radiogroup"] label {
        color: #111827 !important;
    }

    /* =========================
       成功訊息
    ========================= */

    .stSuccess {
        border-radius: 10px;
    }

    /* 嘗試隱藏右下角 Streamlit Badge */

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

col1, col2 = st.columns(2)

# ==============================
# 出勤申請
# ==============================

with col1:

    if st.button(
        "📝 進入出勤申請",
        use_container_width=True
    ):
        st.switch_page("pages/1_出勤申請系統.py")

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