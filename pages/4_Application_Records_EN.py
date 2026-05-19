import streamlit as st
import requests
import pandas as pd
import re

QUERY_FLOW_URL = st.secrets["QUERY_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(page_title="Application Records", page_icon="🔎", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #f4f6f9 !important; color: #111827 !important; }
html, body, [class*="css"] { color: #111827 !important; }
label, p, span, div { color: #111827 !important; }
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"],
[data-testid="stStatusWidget"], [data-testid="stDecoration"], .stDeployButton,
.stAppDeployButton, #MainMenu, footer, header {
    display: none !important;
    visibility: hidden !important;
}
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
.stButton > button {
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
.stButton > button:hover {
    background-color: #0ea5e9 !important;
    color: #ffffff !important;
    border: none !important;
}
.stButton > button:focus, .stButton > button:active {
    background-color: #0284c7 !important;
    color: #ffffff !important;
    border: none !important;
    outline: none !important;
}
.stButton > button p, .stButton > button span, .stButton > button div {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.stRadio label, div[role="radiogroup"] label {
    color: #111827 !important;
}
div[data-baseweb="radio"] span {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

user_info = st.session_state.get("user_info")

if not user_info:
    st.warning("Your login session has expired. Please log in again.")
    if st.button("Back to Login Page", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")
    st.stop()

def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")

def logout_button():
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")

def strip_bilingual_value(value):
    if not isinstance(value, str):
        return value
    text = value.strip()
    match = re.search(r"\(([^()]*)\)", text)
    if match:
        inside = match.group(1).strip()
        if inside:
            return inside
    return text

def translate_status(value):
    status_map = {
        "新建檔": "New",
        "待審核": "Pending Review",
        "待核准": "Pending Approval",
        "已核准": "Approved",
        "退回": "Rejected",
        "已駁回": "Rejected",
        "已歸檔": "Pending HR Upload",
        "已上傳": "Pending HR Upload",
        "已處理": "Uploaded to HR System",
        "待上傳HR系統": "Pending HR Upload",
        "已上傳HR系統": "Uploaded to HR System"
    }
    if not isinstance(value, str):
        return value
    return status_map.get(value.strip(), value)

def translate_column_name(column_name):
    column_map = {
        "狀態": "Status",
        "申請日期": "Application Date",
        "建立時間": "Created Time",
        "送出時間": "Submitted Time",
        "申請類型": "Request Type",
        "工號": "Employee ID",
        "姓名": "Name",
        "部門": "Department",
        "原因": "Reason",
        "假別": "Leave Type",
        "加班類型": "Overtime Type",
        "補登原因": "Correction Reason",
        "開始日期": "Start Date",
        "開始時間": "Start Time",
        "結束日期": "End Date",
        "結束時間": "End Time"
    }
    return column_map.get(str(column_name).strip(), column_name)

def translate_dataframe_to_english(df):
    if df.empty:
        return df
    df = df.rename(columns={col: translate_column_name(col) for col in df.columns})
    if "Status" in df.columns:
        df["Status"] = df["Status"].apply(translate_status)
    return df

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")

query_type_from_menu = st.session_state.get("query_type_en", "Leave")

query_type_map = {
    "Leave": "leave",
    "Overtime": "overtime",
    "Correction": "correction"
}

st.title("🔎 Application Records")
st.caption(f"Logged in as: {employee_name} / {employee_id}")
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
        response = requests.post(QUERY_FLOW_URL, json=payload, timeout=30)

        if response.status_code in [200, 201, 202]:
            result = response.json()

            if result.get("success") is False:
                st.error(result.get("message", "Query failed."))
                st.stop()

            records = result.get("records", [])

            if not records:
                st.info("No application records found.")
            else:
                df = pd.DataFrame(records)
                df = translate_dataframe_to_english(df)
                st.dataframe(df.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.error(f"❌ Query Flow returned an error: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Unable to connect to Query Flow: {str(e)}")
    except Exception as e:
        st.error(f"❌ Query failed: {str(e)}")

st.divider()
logout_button()
