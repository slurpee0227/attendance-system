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
# CSS
# ==============================

st.markdown("""
<style>

.stApp {
    background-color: #f4f6f9;
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
header,
footer,
#MainMenu {
    display: none !important;
}

.block-container {
    max-width: 900px;
    padding-top: 3rem;
}

.maintenance-card {
    background: white;
    border-radius: 20px;
    padding: 60px 40px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.maintenance-icon {
    font-size: 80px;
    margin-bottom: 20px;
}

.maintenance-title {
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 20px;
    color: #111827;
}

.maintenance-subtitle {
    font-size: 24px;
    font-weight: 600;
    color: #2563eb;
    margin-bottom: 30px;
}

.maintenance-text {
    font-size: 18px;
    color: #4b5563;
    line-height: 1.8;
}

.maintenance-footer {
    margin-top: 40px;
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
""", unsafe_allow_html=True)

# ==============================
# 系統開放控制
# ==============================

SYSTEM_OPEN = False

# ==============================
# 未開放頁面
# ==============================

if not SYSTEM_OPEN:

    st.markdown("""
    <div class="maintenance-card">

        <div class="maintenance-icon">
            🚧
        </div>

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
            系統維護中
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")

    st.stop()

# ==============================
# 系統正式開放後
# ==============================

st.success("系統已開放")