import streamlit as st

st.set_page_config(
    page_title="Attendance Request System",
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

    st.title("Attendance Request System")
    st.subheader("System Not Available Yet")

    st.warning("The system is currently under adjustment and testing.")
    st.info("Please continue using the existing application process temporarily.")

    st.caption("Under Maintenance")

    st.divider()

    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")

    st.stop()

st.success("System is now available.")