import streamlit as st
import requests
import base64
from datetime import datetime, date, time, timezone

# ==============================
# Basic Settings
# ==============================

POWER_AUTOMATE_URL = st.secrets["SUBMIT_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="Attendance Request",
    page_icon="📝",
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

# ==============================
# Common Functions
# ==============================

def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("pages/0_English_Login.py")


def format_date_raw(d):
    return f"{d.year}/{d.month}/{d.day}"


def format_hour(t):
    return f"{t.hour:02d}"


def format_minute(t):
    return f"{t.minute:02d}"


def validate_datetime(start_dt, end_dt):
    return start_dt < end_dt


def make_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def make_response_key(timestamp, employee_id, email):
    raw = f"{timestamp}|{employee_id}|{email}"
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")

# ==============================
# User Info
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")
level = user_info.get("level", "")
region = user_info.get("region", "")

# ==============================
# Page
# ==============================

st.title("📝 Attendance Request")
st.caption(f"Current user: {employee_name} / {employee_id}")
back_to_menu_button()
st.divider()

with st.expander("Employee Information", expanded=True):
    st.text_input("Employee ID", value=employee_id, disabled=True)
    st.text_input("Name", value=employee_name, disabled=True)
    st.text_input("Email", value=email, disabled=True)
    st.text_input("Department", value=department, disabled=True)
    st.text_input("Level", value=level, disabled=True)
    st.text_input("Region", value=region, disabled=True)

request_type = st.selectbox(
    "Request Type *",
    ["Leave", "Overtime", "Correction"]
)

leave_type_map = {
    "Personal Leave": "事假",
    "Sick Leave": "病假",
    "Annual Leave": "特休",
    "Compensatory Leave": "補休",
    "Other": "其他"
}

overtime_type_map = {
    "Weekday Overtime": "10平日加班 Work overtime on weekdays",
    "Rest Day Overtime": "20休息日加班 Work overtime on rest day",
    "National Holiday Overtime": "30國定假日加班 Work overtime on national holiday"
}

correction_reason_map = {
    "Missed Clock-in": "忘記刷上班",
    "Missed Clock-out": "忘記刷下班",
    "Forgot to Bring Access Card": "忘記帶卡(Forgot to Bring Access Card)",
    "Other": "其他"
}

leave_type = ""
leave_reason = ""
overtime_type = ""
pay_type = "PAY"
break_hours = "0"
no_break_reason = ""
overtime_reason = ""
correction_reason = ""

# ==============================
# Leave
# ==============================

if request_type == "Leave":
    st.subheader("Leave Information")

    leave_type_label = st.selectbox(
        "Leave Type *",
        list(leave_type_map.keys())
    )
    leave_type = leave_type_map[leave_type_label]

    leave_start_date = st.date_input("Start Date *", value=date.today())
    leave_start_time = st.time_input("Start Time *", value=time(8, 0))
    leave_end_date = st.date_input("End Date *", value=date.today())
    leave_end_time = st.time_input("End Time *", value=time(17, 0))

    leave_reason = st.text_area("Reason *")

# ==============================
# Overtime
# ==============================

elif request_type == "Overtime":
    st.subheader("Overtime Information")

    overtime_type_label = st.selectbox(
        "Overtime Type *",
        list(overtime_type_map.keys())
    )
    overtime_type = overtime_type_map[overtime_type_label]

    pay_type = st.selectbox(
        "Payment Type *",
        ["PAY", "COMP"]
    )

    overtime_start_date = st.date_input("Overtime Start Date *", value=date.today())
    overtime_start_time = st.time_input("Overtime Start Time *", value=time(17, 0))
    overtime_end_date = st.date_input("Overtime End Date *", value=date.today())
    overtime_end_time = st.time_input("Overtime End Time *", value=time(19, 0))

    break_hours = st.selectbox(
        "Break Hours *",
        ["0", "0.5", "1", "1.5", "2"]
    )

    no_break_reason = st.text_area("Reason for No Break")
    overtime_reason = st.text_area("Overtime Reason *")

# ==============================
# Correction
# ==============================

elif request_type == "Correction":
    st.subheader("Correction Information")

    correction_reason_label = st.selectbox(
        "Correction Reason *",
        list(correction_reason_map.keys())
    )
    correction_reason = correction_reason_map[correction_reason_label]

    correction_start_date = st.date_input("Correction Start Date *", value=date.today())
    correction_start_time = st.time_input("Correction Start Time *", value=time(8, 0))
    correction_end_date = st.date_input("Correction End Date *", value=date.today())
    correction_end_time = st.time_input("Correction End Time *", value=time(17, 0))

# ==============================
# Attachment
# ==============================

st.subheader("Attachment")

uploaded_file = st.file_uploader(
    "Upload Attachment",
    type=["png", "jpg", "jpeg", "pdf"]
)

# ==============================
# Required Field Check
# ==============================

def validate_required_fields():
    errors = []

    if request_type == "Leave":
        if not leave_reason.strip():
            errors.append("Reason")

    elif request_type == "Overtime":
        if not overtime_reason.strip():
            errors.append("Overtime Reason")

    elif request_type == "Correction":
        if not correction_reason.strip():
            errors.append("Correction Reason")

    return errors

# ==============================
# Payload
# ==============================

def build_base_payload():
    timestamp = make_timestamp()

    form_type_map = {
        "Leave": "leave",
        "Overtime": "overtime",
        "Correction": "correction"
    }

    form_type_raw_map = {
        "Leave": "請假(Leave)",
        "Overtime": "加班(Overtime)",
        "Correction": "補登(Correction)"
    }

    form_type_normalized = form_type_map[request_type]
    form_type_raw = form_type_raw_map[request_type]
    response_key = make_response_key(timestamp, employee_id, email)

    return {
        "secret": SECRET_KEY,
        "responseKey": response_key,
        "timestamp": timestamp,
        "source": {
            "platform": "Streamlit",
            "triggerType": "streamlit_form_submit",
            "formTypeNormalized": form_type_normalized,
            "language": "en"
        },
        "applicant": {
            "applicantName": employee_name,
            "employeeId": employee_id,
            "email": email
        },
        "request": {
            "formTypeRaw": form_type_raw,
            "formTypeNormalized": form_type_normalized
        },
        "leave": {
            "leaveType": "",
            "flexParentalLeaveCategory": "",
            "bereavementCategory": "",
            "specialDateRaw": "",
            "specialDateIso": "",
            "attachmentLinks": [],
            "leaveStartDateRaw": "",
            "leaveStartHourRaw": "",
            "leaveStartMinuteRaw": "",
            "leaveStartRaw": "",
            "leaveStartIso": "",
            "leaveEndDateRaw": "",
            "leaveEndHourRaw": "",
            "leaveEndMinuteRaw": "",
            "leaveEndRaw": "",
            "leaveEndIso": "",
            "leaveReason": ""
        },
        "overtime": {
            "selectZero": "0",
            "payType": "",
            "overtimeType": "",
            "overtimeStartDateRaw": "",
            "overtimeStartHourRaw": "",
            "overtimeStartMinuteRaw": "",
            "overtimeStartRaw": "",
            "overtimeStartIso": "",
            "overtimeEndDateRaw": "",
            "overtimeEndHourRaw": "",
            "overtimeEndMinuteRaw": "",
            "overtimeEndRaw": "",
            "overtimeEndIso": "",
            "overtimeReason": "",
            "breakHours": "",
            "noBreakReason": "",
            "attachmentLinks": []
        },
        "correction": {
            "correctionReason": "",
            "correctionStartDateRaw": "",
            "correctionStartHourRaw": "",
            "correctionStartMinuteRaw": "",
            "correctionStartRaw": "",
            "correctionStartIso": "",
            "correctionEndDateRaw": "",
            "correctionEndHourRaw": "",
            "correctionEndMinuteRaw": "",
            "correctionEndRaw": "",
            "correctionEndIso": "",
            "attachmentLinks": []
        }
    }

# ==============================
# Submit
# ==============================

if st.button("Submit Request", use_container_width=True):
    errors = validate_required_fields()

    if errors:
        st.error("❌ Please check the following fields:\n\n- " + "\n- ".join(errors))
        st.stop()

    try:
        payload = build_base_payload()
        attachment_links = []

        if uploaded_file is not None:
            attachment_links.append({
                "fileName": uploaded_file.name,
                "fileType": uploaded_file.type,
                "fileSize": uploaded_file.size
            })

        if request_type == "Leave":
            start_dt = datetime.combine(leave_start_date, leave_start_time)
            end_dt = datetime.combine(leave_end_date, leave_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ End time must be later than start time")
                st.stop()

            payload["leave"].update({
                "leaveType": leave_type,
                "leaveStartDateRaw": format_date_raw(leave_start_date),
                "leaveStartHourRaw": format_hour(leave_start_time),
                "leaveStartMinuteRaw": format_minute(leave_start_time),
                "leaveStartRaw": "",
                "leaveStartIso": start_dt.isoformat(),
                "leaveEndDateRaw": format_date_raw(leave_end_date),
                "leaveEndHourRaw": format_hour(leave_end_time),
                "leaveEndMinuteRaw": format_minute(leave_end_time),
                "leaveEndRaw": "",
                "leaveEndIso": end_dt.isoformat(),
                "leaveReason": leave_reason.strip(),
                "attachmentLinks": attachment_links
            })

        elif request_type == "Overtime":
            start_dt = datetime.combine(overtime_start_date, overtime_start_time)
            end_dt = datetime.combine(overtime_end_date, overtime_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ End time must be later than start time")
                st.stop()

            payload["overtime"].update({
                "selectZero": "0",
                "payType": pay_type,
                "overtimeType": overtime_type,
                "overtimeStartDateRaw": format_date_raw(overtime_start_date),
                "overtimeStartHourRaw": format_hour(overtime_start_time),
                "overtimeStartMinuteRaw": format_minute(overtime_start_time),
                "overtimeStartRaw": "",
                "overtimeStartIso": start_dt.isoformat(),
                "overtimeEndDateRaw": format_date_raw(overtime_end_date),
                "overtimeEndHourRaw": format_hour(overtime_end_time),
                "overtimeEndMinuteRaw": format_minute(overtime_end_time),
                "overtimeEndRaw": "",
                "overtimeEndIso": end_dt.isoformat(),
                "overtimeReason": overtime_reason.strip(),
                "breakHours": break_hours,
                "noBreakReason": no_break_reason.strip(),
                "attachmentLinks": attachment_links
            })

        elif request_type == "Correction":
            start_dt = datetime.combine(correction_start_date, correction_start_time)
            end_dt = datetime.combine(correction_end_date, correction_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ End time must be later than start time")
                st.stop()

            payload["correction"].update({
                "correctionReason": correction_reason,
                "correctionStartDateRaw": format_date_raw(correction_start_date),
                "correctionStartHourRaw": format_hour(correction_start_time),
                "correctionStartMinuteRaw": format_minute(correction_start_time),
                "correctionStartRaw": "",
                "correctionStartIso": start_dt.isoformat(),
                "correctionEndDateRaw": format_date_raw(correction_end_date),
                "correctionEndHourRaw": format_hour(correction_end_time),
                "correctionEndMinuteRaw": format_minute(correction_end_time),
                "correctionEndRaw": "",
                "correctionEndIso": end_dt.isoformat(),
                "attachmentLinks": attachment_links
            })

        response = requests.post(
            POWER_AUTOMATE_URL,
            json=payload,
            timeout=30
        )

        if response.status_code in [200, 201, 202]:
            st.success("✅ Request submitted successfully")
        else:
            st.error(f"❌ Flow returned an error: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Unable to connect to Power Automate: {str(e)}")

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
