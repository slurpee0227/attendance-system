import streamlit as st
import requests
import pandas as pd

# ==============================
# Basic Settings
# ==============================

QUERY_FLOW_URL = st.secrets["QUERY_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="Application Records",
    page_icon="🔎",
    layout="centered"
)

# ==============================
# Style
# ==============================

st.markdown(
    """
    <style>
    .stApp { background-color: #f4f6f9 !important; color: #111827 !important; }
    html, body, [class*="css"] { color: #111827 !important; }
    label, p, span, div { color: #111827 !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; visibility: hidden !important; }
    [data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stDecoration"],
    .stDeployButton, .stAppDeployButton, #MainMenu, footer, header {
        display: none !important; visibility: hidden !important; height: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# Login Check
# ==============================

user_info = st.session_state.get("user_info")

if not user_info:
    st.warning("Your login session has expired. Please log in again.")

    if st.button("Back to Login", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/0_English_Login.py")

    st.stop()


def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("pages/0_English_Login.py")

# ==============================
# User Info
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")

# ==============================
# Query Type
# ==============================

query_type_from_menu = st.session_state.get("query_type_en", "Leave")

query_type_map = {
    "Leave": "leave",
    "Overtime": "overtime",
    "Correction": "correction"
}

# ==============================
# Page
# ==============================

st.title("🔎 Application Records")
st.caption(f"Current user: {employee_name} / {employee_id}")
st.caption(f"Department: {department}")
back_to_menu_button()
st.divider()

st.subheader("Query Criteria")

default_index = ["Leave", "Overtime", "Correction"].index(query_type_from_menu)

query_type = st.radio(
    "Request Type",
    ["Leave", "Overtime", "Correction"],
    index=default_index,
    horizontal=True
)

st.session_state.query_type_en = query_type
query_type_normalized = query_type_map[query_type]

if st.button("Query Records", use_container_width=True):
    payload = {
        "secret": SECRET_KEY,
        "employeeId": employee_id,
        "email": email,
        "queryType": query_type_normalized
    }

    try:
        response = requests.post(
            QUERY_FLOW_URL,
            json=payload,
            timeout=30
        )

        if response.status_code in [200, 201, 202]:
            result = response.json()

            if result.get("success") is False:
                st.error(result.get("message", "Query failed"))
                st.stop()

            records = result.get("records", [])

            if not records:
                st.info("No application records found")
            else:
                df = pd.DataFrame(records)

                status_map = {
                    "已歸檔": "Pending HR upload",
                    "已上傳": "Pending HR upload",
                    "已處理": "Uploaded to HR system"
                }

                if "狀態" in df.columns:
                    df["狀態"] = df["狀態"].replace(status_map)

                column_map = {
                    "狀態": "Status",
                    "申請日期": "Application Date",
                    "申請類型": "Request Type",
                    "假別": "Leave Type",
                    "加班類型": "Overtime Type",
                    "給付方式": "Payment Type",
                    "補登原因": "Correction Reason",
                    "開始時間": "Start Time",
                    "結束時間": "End Time",
                    "原因": "Reason",
                    "部門": "Department",
                    "工號": "Employee ID",
                    "姓名": "Name"
                }

                df = df.rename(columns=column_map)

                st.dataframe(
                    df.reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )

        else:
            st.error(f"❌ Query Flow returned an error: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Unable to connect to Query Flow: {str(e)}")

    except Exception as e:
        st.error(f"❌ Query failed: {str(e)}")

st.divider()

if st.button("Logout", use_container_width=True):
    st.session_state.clear()
    st.switch_page("pages/0_English_Login.py")
