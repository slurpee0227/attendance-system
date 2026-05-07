import streamlit as st
import requests
import pandas as pd
import re

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

    label, p, span, div {
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
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    .stButton > button {
        height: 50px;
        border-radius: 12px;
        border: none;
        background-color: #2563eb !important;
        color: white !important;
        font-size: 16px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }

    .stRadio label,
    div[role="radiogroup"] label {
        color: #111827 !important;
    }

    div[data-baseweb="radio"] span {
        color: #111827 !important;
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

    if st.button("Back to Login Page", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")

    st.stop()


# ==============================
# Utility Functions
# ==============================

def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")


def logout_button():
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")


def strip_bilingual_value(value):
    """
    Convert values like:
    忘記帶卡(Forgot to Bring Access Card) -> Forgot to Bring Access Card
    特休(Annual Leave) -> Annual Leave
    """
    if not isinstance(value, str):
        return value

    text = value.strip()

    # Use English text inside parentheses when present.
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


def translate_request_type(value):
    request_type_map = {
        "請假": "Leave",
        "請假(Leave)": "Leave",
        "leave": "Leave",
        "加班": "Overtime",
        "加班(Overtime)": "Overtime",
        "overtime": "Overtime",
        "補登": "Correction",
        "補登(Timesheet Correction)": "Correction",
        "correction": "Correction"
    }

    if not isinstance(value, str):
        return value

    return request_type_map.get(value.strip(), strip_bilingual_value(value))


def translate_overtime_type(value):
    if not isinstance(value, str):
        return value

    text = value.strip()

    overtime_map = {
        "10平日加班 Work overtime on weekdays": "10 Work overtime on weekdays",
        "20休息日加班(無交通費) Work overtime on holidays (no transportation expenses)": "20 Work overtime on holidays (no transportation expenses)",
        "25休息日加班 Foreign employees select 20": "25 Rest day overtime - foreign employees select 20",
        "60國定假日加班 Foreign employees select 63": "60 National holiday overtime - foreign employees select 63",
        "63國定假日加班(無交通費) Work overtime on national holidays (no transportation expenses)": "63 Work overtime on national holidays (no transportation expenses)",
        "100調班日加班 Foreign employees select 101": "100 Rescheduled workday overtime - foreign employees select 101",
        "101調班日加班(無交通費) Overtime on Rescheduled Workday (no transportation expenses)": "101 Overtime on rescheduled workday (no transportation expenses)"
    }

    return overtime_map.get(text, strip_bilingual_value(text))


def translate_correction_reason(value):
    if not isinstance(value, str):
        return value

    reason_map = {
        "忘記帶卡": "Forgot to Bring Access Card",
        "忘記帶卡(Forgot to Bring Access Card)": "Forgot to Bring Access Card",
        "忘記刷卡上班": "Forgot to Clock In",
        "忘記刷卡上班(Forgot to Clock In)": "Forgot to Clock In",
        "忘記刷卡下班": "Forgot to Clock Out",
        "忘記刷卡下班(Forgot to Clock Out)": "Forgot to Clock Out",
        "早於刷卡時間": "Earlier than the card swipe time",
        "早於刷卡時間(Earlier than the card swipe time)": "Earlier than the card swipe time",
        "其他": "Other",
        "其他(Other)": "Other"
    }

    text = value.strip()
    return reason_map.get(text, strip_bilingual_value(text))


def translate_leave_type(value):
    if not isinstance(value, str):
        return value

    leave_map = {
        "特休(Annual Leave)": "Annual Leave",
        "病假(Sick Leave)": "Sick Leave",
        "事假(Personal Leave)": "Personal Leave",
        "公出(Official Business Leave)": "Official Business Leave",
        "生理假(Menstrual Leave)": "Menstrual Leave",
        "家庭照顧假(Family Care Leave)": "Family Care Leave",
        "活力假(Vitality Leave)": "Vitality Leave",
        "喪假(Bereavement Leave)": "Bereavement Leave",
        "公假(Official Leave)": "Official Leave",
        "婚假(Marriage Leave)": "Marriage Leave",
        "公傷假(Occupational Injury Leave)": "Occupational Injury Leave",
        "陪產檢假/陪產假(Paternity Leave / Accompanying Prenatal Check-up Leave)": "Paternity Leave / Accompanying Prenatal Check-up Leave",
        "產假(Maternity Leave)": "Maternity Leave",
        "產檢假(Prenatal Check-up Leave)": "Prenatal Check-up Leave",
        "志工假(Volunteer Leave)": "Volunteer Leave",
        "彈性育嬰留停(日)": "Flexible Parental Leave - Day"
    }

    text = value.strip()
    return leave_map.get(text, strip_bilingual_value(text))


def translate_column_name(column_name):
    column_map = {
        # Common
        "狀態": "Status",
        "申請日期": "Application Date",
        "建立時間": "Created Time",
        "送出時間": "Submitted Time",
        "申請類型": "Request Type",
        "類型": "Request Type",
        "工號": "Employee ID",
        "員工工號": "Employee ID",
        "姓名": "Name",
        "部門": "Department",
        "原因": "Reason",
        "備註": "Remark",
        "附件": "Attachment",

        # Leave
        "假別": "Leave Type",
        "請假假別": "Leave Type",
        "請假原因": "Leave Reason",
        "請假開始日期": "Start Date",
        "請假開始時間": "Start Time",
        "請假結束日期": "End Date",
        "請假結束時間": "End Time",
        "請假附件": "Leave Attachment",
        "喪假分類": "Bereavement Category",
        "彈性育嬰留停分類": "Flexible Parental Leave Category",
        "特殊日期": "Special Date",

        # Overtime
        "加班類型": "Overtime Type",
        "給付方式": "Payment Type",
        "加班開始日期": "Start Date",
        "加班開始時間": "Start Time",
        "加班結束日期": "End Date",
        "加班結束時間": "End Time",
        "加班原因": "Overtime Reason",
        "休息時數": "Break Hours",
        "加班休息時間": "Break Hours",
        "未休息原因": "No Break Reason",

        # Correction
        "補登原因": "Correction Reason",
        "補登開始日期": "Start Date",
        "補登開始時間": "Start Time",
        "補登結束日期": "End Date",
        "補登結束時間": "End Time",
        "補登上班日期": "Clock-in Date",
        "補登上班時間": "Clock-in Time",
        "補登下班日期": "Clock-out Date",
        "補登下班時間": "Clock-out Time",
        "補登附件": "Correction Attachment",

        # The exact issue shown in the screenshot
        "開始日期": "Start Date",
        "開始時間": "Start Time",
        "結束日期": "End Date",
        "結束時間": "End Time"
    }

    return column_map.get(str(column_name).strip(), column_name)


def translate_dataframe_to_english(df):
    if df.empty:
        return df

    # Rename columns first.
    df = df.rename(columns={col: translate_column_name(col) for col in df.columns})

    # Translate known value columns after renaming.
    if "Status" in df.columns:
        df["Status"] = df["Status"].apply(translate_status)

    if "Request Type" in df.columns:
        df["Request Type"] = df["Request Type"].apply(translate_request_type)

    if "Leave Type" in df.columns:
        df["Leave Type"] = df["Leave Type"].apply(translate_leave_type)

    if "Overtime Type" in df.columns:
        df["Overtime Type"] = df["Overtime Type"].apply(translate_overtime_type)

    if "Correction Reason" in df.columns:
        df["Correction Reason"] = df["Correction Reason"].apply(translate_correction_reason)

    if "Reason" in df.columns:
        # The Flow may return correction reason under the generic "原因" field.
        df["Reason"] = df["Reason"].apply(translate_correction_reason)
        df["Reason"] = df["Reason"].apply(translate_leave_type)
        df["Reason"] = df["Reason"].apply(translate_overtime_type)

    return df


# ==============================
# User Information
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
        response = requests.post(
            QUERY_FLOW_URL,
            json=payload,
            timeout=30
        )

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
logout_button()
