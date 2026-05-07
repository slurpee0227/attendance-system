import streamlit as st
import requests
import base64
from datetime import datetime, date, timezone


# ==============================
# Basic Settings
# ==============================

POWER_AUTOMATE_URL = st.secrets["SUBMIT_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

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
        max-width: 900px;
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

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stDateInput input {
        background-color: white !important;
        color: #111827 !important;
        border-radius: 10px;
        border: 1px solid #d1d5db !important;
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
# Constants
# ==============================

HOUR_OPTIONS = [f"{i:02d}" for i in range(24)]
MINUTE_OPTIONS = ["00", "30"]

LEAVE_TYPES = [
    "Annual Leave",
    "Personal Leave",
    "Sick Leave",
    "Family Care Leave",
    "Bereavement Leave",
    "Compensatory Leave",
    "Marriage Leave",
    "Maternity Leave",
    "Paternity Leave",
    "Prenatal Checkup Leave",
    "Paternity Prenatal Checkup Leave",
    "Official Leave",
    "Menstrual Leave",
    "Flexible Parental Leave",
    "Other"
]

LEAVE_TYPE_PAYLOAD_MAP = {
    "Annual Leave": "特休(Annual Leave)",
    "Personal Leave": "事假(Personal Leave)",
    "Sick Leave": "病假(Sick Leave)",
    "Family Care Leave": "家庭照顧假(Family Care Leave)",
    "Bereavement Leave": "喪假(Bereavement Leave)",
    "Compensatory Leave": "補休(Compensatory Leave)",
    "Marriage Leave": "婚假(Marriage Leave)",
    "Maternity Leave": "產假(Maternity Leave)",
    "Paternity Leave": "陪產假(Paternity Leave)",
    "Prenatal Checkup Leave": "產檢假(Prenatal Checkup Leave)",
    "Paternity Prenatal Checkup Leave": "陪產檢假(Paternity Prenatal Checkup Leave)",
    "Official Leave": "公假(Official Leave)",
    "Menstrual Leave": "生理假(Menstrual Leave)",
    "Flexible Parental Leave": "彈性育嬰留停(Flexible Parental Leave)",
    "Other": "其他(Other)"
}

LEAVE_ATTACHMENT_REQUIRED_TYPES = [
    "Sick Leave",
    "Bereavement Leave",
    "Family Care Leave",
    "Maternity Leave",
    "Paternity Leave",
    "Prenatal Checkup Leave",
    "Paternity Prenatal Checkup Leave",
    "Official Leave",
    "Flexible Parental Leave"
]

BEREAVEMENT_CATEGORIES = [
    "Parent",
    "Spouse",
    "Child",
    "Grandparent",
    "Sibling",
    "Other"
]

PARENTAL_LEAVE_CATEGORIES = [
    "Reduced Daily Working Hours",
    "Weekly Flexible Leave",
    "Other"
]

OVERTIME_TYPES = [
    "10 Work overtime on weekdays",
    "20 Work overtime on rest day",
    "25 Rest day overtime - foreign employees select 20",
    "30 Work overtime on national holiday"
]

OVERTIME_TYPE_PAYLOAD_MAP = {
    "10 Work overtime on weekdays": "10平日加班 Work overtime on weekdays",
    "20 Work overtime on rest day": "20休息日加班 Work overtime on rest day",
    "25 Rest day overtime - foreign employees select 20": "25休息日加班 Foreign employees select 20",
    "30 Work overtime on national holiday": "30國定假日加班 Work overtime on national holiday"
}

BREAK_HOUR_OPTIONS = ["0", "0.5", "1", "1.5", "2"]

CORRECTION_REASONS = [
    "Forgot to Clock In",
    "Forgot to Clock Out",
    "Forgot to Bring Access Card",
    "Earlier than the card swipe time",
    "Other"
]

CORRECTION_REASON_PAYLOAD_MAP = {
    "Forgot to Clock In": "忘記刷卡上班(Forgot to Clock In)",
    "Forgot to Clock Out": "忘記刷卡下班(Forgot to Clock Out)",
    "Forgot to Bring Access Card": "忘記帶卡(Forgot to Bring Access Card)",
    "Earlier than the card swipe time": "早於刷卡時間(Earlier than the card swipe time)",
    "Other": "其他(Other)"
}


# ==============================
# Utility Functions
# ==============================

def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")


def is_leave_attachment_required(leave_type: str) -> bool:
    return leave_type in LEAVE_ATTACHMENT_REQUIRED_TYPES


def make_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def make_response_key(timestamp, employee_id, email):
    raw = f"{timestamp}|{employee_id}|{email}"
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")


def combine_datetime(date_value, hour_value, minute_value):
    return datetime(
        date_value.year,
        date_value.month,
        date_value.day,
        int(hour_value),
        int(minute_value)
    )


def format_date_raw(d):
    return f"{d.year}/{d.month}/{d.day}"


def build_file_info(uploaded_file):
    if uploaded_file is None:
        return []

    return [{
        "fileName": uploaded_file.name,
        "fileType": uploaded_file.type,
        "fileSize": uploaded_file.size
    }]


def validate_start_end(start_dt, end_dt):
    return start_dt < end_dt


def build_base_payload(
    request_type,
    employee_name,
    employee_id,
    email
):
    timestamp = make_timestamp()

    form_type_map = {
        "Leave": "leave",
        "Overtime": "overtime",
        "Timesheet Correction": "correction"
    }

    form_type_raw_map = {
        "Leave": "請假(Leave)",
        "Overtime": "加班(Overtime)",
        "Timesheet Correction": "補登(Timesheet Correction)"
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
            "formTypeNormalized": form_type_normalized
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
# User Information
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")
level = user_info.get("level", "")
region = user_info.get("region", "")


# ==============================
# Page Header
# ==============================

st.title("📝 Attendance Request System")
st.caption(f"Logged in as: {employee_name} / {employee_id}")
back_to_menu_button()
st.divider()


# ==============================
# Applicant Information
# ==============================

with st.expander("Applicant Information", expanded=True):
    st.text_input("Employee ID", value=employee_id, disabled=True)
    st.text_input("Name", value=employee_name, disabled=True)
    st.text_input("Email", value=email, disabled=True)
    st.text_input("Department", value=department, disabled=True)
    st.text_input("Level", value=level, disabled=True)
    st.text_input("Region", value=region, disabled=True)


# ==============================
# Request Type
# ==============================

st.subheader("Request Type")

request_type = st.radio(
    "Choose Request Type *",
    ["Leave", "Overtime", "Timesheet Correction"],
    horizontal=True
)

st.divider()


# ==============================
# Default Variables
# ==============================

uploaded_file = None

leave_type = ""
leave_reason = ""
bereavement_category = ""
parental_leave_category = ""
leave_start_date = date.today()
leave_end_date = date.today()
leave_start_hour = "08"
leave_start_minute = "00"
leave_end_hour = "17"
leave_end_minute = "00"

pay_type = "PAY"
overtime_type = ""
overtime_reason = ""
break_hours = "0"
no_break_reason = ""
overtime_start_date = date.today()
overtime_end_date = date.today()
overtime_start_hour = "17"
overtime_start_minute = "00"
overtime_end_hour = "19"
overtime_end_minute = "00"

correction_reason = ""
correction_start_date = date.today()
correction_end_date = date.today()
correction_start_hour = "08"
correction_start_minute = "00"
correction_end_hour = "17"
correction_end_minute = "00"


# ==============================
# Leave Form
# ==============================

if request_type == "Leave":

    st.subheader("Leave Information")

    leave_type = st.selectbox(
        "Leave Type *",
        LEAVE_TYPES
    )

    if leave_type == "Bereavement Leave":
        bereavement_category = st.selectbox(
            "Bereavement Category *",
            BEREAVEMENT_CATEGORIES
        )

    if leave_type == "Flexible Parental Leave":
        parental_leave_category = st.selectbox(
            "Flexible Parental Leave Category *",
            PARENTAL_LEAVE_CATEGORIES
        )

    st.markdown("#### Leave Start Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_start_date = st.date_input("Leave Start Date *", value=date.today())
    with col2:
        leave_start_hour = st.selectbox("Start Hour *", HOUR_OPTIONS, index=8)
    with col3:
        leave_start_minute = st.selectbox("Start Minute *", MINUTE_OPTIONS, index=0)

    st.markdown("#### Leave End Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_end_date = st.date_input("Leave End Date *", value=date.today())
    with col2:
        leave_end_hour = st.selectbox("End Hour *", HOUR_OPTIONS, index=17)
    with col3:
        leave_end_minute = st.selectbox("End Minute *", MINUTE_OPTIONS, index=0)

    leave_reason = st.text_area("Leave Reason *")

    if is_leave_attachment_required(leave_type):
        st.warning("Supporting document is required for this leave type.")
        uploaded_file = st.file_uploader(
            "Upload Supporting Document *",
            type=["png", "jpg", "jpeg", "pdf"]
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Supporting Document",
            type=["png", "jpg", "jpeg", "pdf"]
        )


# ==============================
# Overtime Form
# ==============================

elif request_type == "Overtime":

    st.subheader("Overtime Information")

    pay_type = st.selectbox(
        "Payment Type *",
        ["PAY", "COMP"]
    )

    overtime_type = st.selectbox(
        "Overtime Type *",
        OVERTIME_TYPES
    )

    st.markdown("#### Overtime Start Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_start_date = st.date_input("Overtime Start Date *", value=date.today())
    with col2:
        overtime_start_hour = st.selectbox("Overtime Start Hour *", HOUR_OPTIONS, index=17)
    with col3:
        overtime_start_minute = st.selectbox("Overtime Start Minute *", MINUTE_OPTIONS, index=0)

    st.markdown("#### Overtime End Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_end_date = st.date_input("Overtime End Date *", value=date.today())
    with col2:
        overtime_end_hour = st.selectbox("Overtime End Hour *", HOUR_OPTIONS, index=19)
    with col3:
        overtime_end_minute = st.selectbox("Overtime End Minute *", MINUTE_OPTIONS, index=0)

    overtime_reason = st.text_area("Overtime Reason *")

    break_hours = st.selectbox(
        "Break Time - Hours *",
        BREAK_HOUR_OPTIONS
    )

    if break_hours == "0":
        st.warning("If break time is 0, No Break Reason is required.")
        no_break_reason = st.text_area("No Break Reason *")
    else:
        no_break_reason = st.text_area("No Break Reason")

    st.info("Attachment upload is not required for overtime requests.")


# ==============================
# Timesheet Correction Form
# ==============================

elif request_type == "Timesheet Correction":

    st.subheader("Timesheet Correction Information")

    correction_reason = st.selectbox(
        "Timesheet Correction Reason *",
        CORRECTION_REASONS
    )

    st.markdown("#### Correction Start Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        correction_start_date = st.date_input("Correction Start Date *", value=date.today())
    with col2:
        correction_start_hour = st.selectbox("Correction Start Hour *", HOUR_OPTIONS, index=8)
    with col3:
        correction_start_minute = st.selectbox("Correction Start Minute *", MINUTE_OPTIONS, index=0)

    st.markdown("#### Correction End Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        correction_end_date = st.date_input("Correction End Date *", value=date.today())
    with col2:
        correction_end_hour = st.selectbox("Correction End Hour *", HOUR_OPTIONS, index=17)
    with col3:
        correction_end_minute = st.selectbox("Correction End Minute *", MINUTE_OPTIONS, index=0)

    if correction_reason == "Forgot to Bring Access Card":
        st.warning("Attachment upload is required when the reason is Forgot to Bring Access Card.")
        uploaded_file = st.file_uploader(
            "Upload Attachment *",
            type=["png", "jpg", "jpeg", "pdf"]
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Attachment",
            type=["png", "jpg", "jpeg", "pdf"]
        )


# ==============================
# Required Field Validation
# ==============================

def validate_required_fields():
    errors = []

    if not employee_id.strip():
        errors.append("Employee ID")

    if not employee_name.strip():
        errors.append("Name")

    if not email.strip():
        errors.append("Email")

    if request_type == "Leave":

        if not leave_type:
            errors.append("Leave Type")

        if leave_type == "Bereavement Leave" and not bereavement_category:
            errors.append("Bereavement Category")

        if leave_type == "Flexible Parental Leave" and not parental_leave_category:
            errors.append("Flexible Parental Leave Category")

        if not leave_reason.strip():
            errors.append("Leave Reason")

        if is_leave_attachment_required(leave_type) and uploaded_file is None:
            errors.append("Supporting Document")

    elif request_type == "Overtime":

        if not pay_type:
            errors.append("Payment Type")

        if not overtime_type:
            errors.append("Overtime Type")

        if not overtime_reason.strip():
            errors.append("Overtime Reason")

        if not break_hours:
            errors.append("Break Time")

        if break_hours == "0" and not no_break_reason.strip():
            errors.append("No Break Reason")

    elif request_type == "Timesheet Correction":

        if not correction_reason:
            errors.append("Timesheet Correction Reason")

        if correction_reason == "Forgot to Bring Access Card" and uploaded_file is None:
            errors.append("Attachment is required for Forgot to Bring Access Card")

    return errors


# ==============================
# Submit
# ==============================

st.divider()

if st.button("Submit Request", use_container_width=True):

    errors = validate_required_fields()

    if errors:
        st.error("❌ Please check the following required fields:\n\n- " + "\n- ".join(errors))
        st.stop()

    try:
        payload = build_base_payload(
            request_type=request_type,
            employee_name=employee_name,
            employee_id=employee_id,
            email=email
        )

        attachment_links = build_file_info(uploaded_file)

        if request_type == "Leave":

            start_dt = combine_datetime(
                leave_start_date,
                leave_start_hour,
                leave_start_minute
            )

            end_dt = combine_datetime(
                leave_end_date,
                leave_end_hour,
                leave_end_minute
            )

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ End time cannot be earlier than or equal to start time.")
                st.stop()

            leave_type_payload = LEAVE_TYPE_PAYLOAD_MAP[leave_type]

            payload["leave"].update({
                "leaveType": leave_type_payload,
                "flexParentalLeaveCategory": parental_leave_category,
                "bereavementCategory": bereavement_category,
                "leaveStartDateRaw": format_date_raw(leave_start_date),
                "leaveStartHourRaw": leave_start_hour,
                "leaveStartMinuteRaw": leave_start_minute,
                "leaveStartRaw": "",
                "leaveStartIso": start_dt.isoformat(),
                "leaveEndDateRaw": format_date_raw(leave_end_date),
                "leaveEndHourRaw": leave_end_hour,
                "leaveEndMinuteRaw": leave_end_minute,
                "leaveEndRaw": "",
                "leaveEndIso": end_dt.isoformat(),
                "leaveReason": leave_reason.strip(),
                "attachmentLinks": attachment_links
            })

        elif request_type == "Overtime":

            start_dt = combine_datetime(
                overtime_start_date,
                overtime_start_hour,
                overtime_start_minute
            )

            end_dt = combine_datetime(
                overtime_end_date,
                overtime_end_hour,
                overtime_end_minute
            )

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ End time cannot be earlier than or equal to start time.")
                st.stop()

            overtime_type_payload = OVERTIME_TYPE_PAYLOAD_MAP[overtime_type]

            payload["overtime"].update({
                "selectZero": "0",
                "payType": pay_type,
                "overtimeType": overtime_type_payload,
                "overtimeStartDateRaw": format_date_raw(overtime_start_date),
                "overtimeStartHourRaw": overtime_start_hour,
                "overtimeStartMinuteRaw": overtime_start_minute,
                "overtimeStartRaw": "",
                "overtimeStartIso": start_dt.isoformat(),
                "overtimeEndDateRaw": format_date_raw(overtime_end_date),
                "overtimeEndHourRaw": overtime_end_hour,
                "overtimeEndMinuteRaw": overtime_end_minute,
                "overtimeEndRaw": "",
                "overtimeEndIso": end_dt.isoformat(),
                "overtimeReason": overtime_reason.strip(),
                "breakHours": break_hours,
                "noBreakReason": no_break_reason.strip(),
                "attachmentLinks": []
            })

        elif request_type == "Timesheet Correction":

            start_dt = combine_datetime(
                correction_start_date,
                correction_start_hour,
                correction_start_minute
            )

            end_dt = combine_datetime(
                correction_end_date,
                correction_end_hour,
                correction_end_minute
            )

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ End time cannot be earlier than or equal to start time.")
                st.stop()

            correction_reason_payload = CORRECTION_REASON_PAYLOAD_MAP[correction_reason]

            payload["correction"].update({
                "correctionReason": correction_reason_payload,
                "correctionStartDateRaw": format_date_raw(correction_start_date),
                "correctionStartHourRaw": correction_start_hour,
                "correctionStartMinuteRaw": correction_start_minute,
                "correctionStartRaw": "",
                "correctionStartIso": start_dt.isoformat(),
                "correctionEndDateRaw": format_date_raw(correction_end_date),
                "correctionEndHourRaw": correction_end_hour,
                "correctionEndMinuteRaw": correction_end_minute,
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
            st.success("✅ Request submitted successfully.")
        else:
            st.error(f"❌ Flow returned an error: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Unable to connect to Power Automate: {str(e)}")

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")