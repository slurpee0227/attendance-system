import streamlit as st

st.set_page_config(
    page_title="出勤申請系統",
    page_icon="📝",
    layout="centered"
)

st.markdown(
    """
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
        max-width: 850px;
        padding-top: 4rem;
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

SYSTEM_OPEN = False

if not SYSTEM_OPEN:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/595/595067.png",
        width=90
    )

    st.title("出勤申請系統")
    st.subheader("系統尚未開放")

    st.warning("目前系統正在進行功能調整與測試。")
    st.info("如有出勤申請需求，請暫時使用既有申請流程。")

    st.caption("系統維護中")

    st.divider()

    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")

    st.stop()

st.success("系統已開放")