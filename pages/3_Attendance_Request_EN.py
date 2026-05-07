import streamlit as st

# ==============================
# Page Settings
# ==============================

st.set_page_config(
    page_title="Attendance Request System",
    page_icon="📝",
    layout="centered"
)

# ==============================
# Custom CSS
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
# System Availability Control
# ==============================

SYSTEM_OPEN = False

# To control this by Streamlit secrets later, use:
# SYSTEM_OPEN = st.secrets.get("ATTENDANCE_SYSTEM_OPEN", False)

# ==============================
# Unavailable Page
# ==============================

if not SYSTEM_OPEN:

    st.markdown(
        """
        <div class="maintenance-card">
            <div class="maintenance-icon">🚧</div>

            <div class="maintenance-title">
                Attendance Request System
            </div>

            <div class="maintenance-subtitle">
                The system is not available yet.
            </div>

            <div class="maintenance-text">
                The system is currently under adjustment and testing.
            </div>

            <div class="maintenance-text">
                Please continue using the existing application process temporarily.
            </div>

            <div class="maintenance-footer">
                出勤申請系統尚未開放
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")

    st.stop()

# ==============================
# Original attendance request code goes here after system opens
# ==============================

st.success("The system is now available.")