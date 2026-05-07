import streamlit as st

# ==============================
# 頁面設定
# ==============================

st.set_page_config(
    page_title="出勤申請系統",
    page_icon="📝",
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

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    [data-testid="stDecoration"],
    .stDeployButton,
    .stAppDeployButton,
    #MainMenu,
    footer,
    header {
        display: none !important;
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }

    .maintenance-card {
        background-color: white;
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }

    .maintenance-icon {
        font-size: 76px;
        margin-bottom: 20px;
    }

    .maintenance-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .maintenance-subtitle {
        font-size: 24px;
        font-weight: 600;
        color: #2563eb;
        margin-bottom: 28px;
    }

    .maintenance-text {
        font-size: 18px;
        color: #4b5563;
        line-height: 1.8;
    }

    .maintenance-footer {
        margin-top: 36px;
        font-size: 14px;
        color: #9ca3af;
    }

    .stButton > button {
        height: 48px;
        border-radius: 12px;
        border: none;
        background-color: #2563eb !important;
        color: white !important;
        font-size: 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# 系統開放控制
# ==============================

SYSTEM_OPEN = False

# 若之後想用 Streamlit secrets 控制，改成這行：
# SYSTEM_OPEN = st.secrets.get("ATTENDANCE_SYSTEM_OPEN", False)

# ==============================
# 未開放頁面
# ==============================

if not SYSTEM_OPEN:

    st.markdown(
        """
        <div class="maintenance-card">
            <div class="maintenance-icon">🚧</div>

            <div class="maintenance-title">
                出勤申請系統
            </div>

            <div class="maintenance-subtitle">
                系統尚未開放
            </div>

            <div class="maintenance-text">
                目前系統正在進行功能調整與測試。
            </div>

            <div class="maintenance-text">
                如有出勤申請需求，請暫時使用既有申請流程。
            </div>

            <div class="maintenance-footer">
                Attendance Request System Under Maintenance
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")

    st.stop()

# ==============================
# 系統開放後，原本的出勤申請程式放這裡
# ==============================

st.success("系統已開放")