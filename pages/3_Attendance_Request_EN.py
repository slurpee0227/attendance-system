import streamlit as st
import requests
import base64
from datetime import datetime, date, timedelta, timezone


# ==============================
# Basic Settings
# ==============================

POWER_AUTOMATE_URL = st.secrets["SUBMIT_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="Attendance Application Form",
    page_icon="📝",
    layout="centered"
)


# ==============================
# UI Style
# ==============================


def apply_page_style():
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
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 980px;
        }
        .section-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 18px 20px;
            margin: 12px 0 18px 0;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }
        .hint-box {
            background: #eff6ff;
            border-left: 5px solid #2563eb;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 8px 0 16px 0;
            font-size: 14px;
            line-height: 1.6;
        }
        .warning-box {
            background: #fff7ed;
            border-left: 5px solid #f97316;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 8px 0 16px 0;
            font-size: 14px;
            line-height: 1.6;
        }
        .stButton > button {
            height: 50px;
            border-radius: 12px;
            border: none;
            background-color: #2563eb !important;
            color: white !important;
            font-size: 16px;
            font-weight: 700;
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



apply_page_style()


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
# Form Options - aligned with Google Form
# ==============================

HOUR_OPTIONS = [f"{i:02d}" for i in range(24)]
MINUTE_OPTIONS = ["00", "30"]

REQUEST_TYPES = [
    "Leave",
    "Overtime",
    "Timesheet Correction"
]

LEAVE_TYPES = [
    "Annual Leave",
    "Sick Leave",
    "Personal Leave",
    "Official Business Leave",
    "Menstrual Leave",
    "Family Care Leave",
    "Vitality Leave",
    "Bereavement Leave",
    "Official Leave",
    "Marriage Leave",
    "Occupational Injury Leave",
    "Paternity Leave / Accompanying Prenatal Check-up Leave",
    "Maternity Leave",
    "Prenatal Check-up Leave",
    "Volunteer Leave",
    "Flexible Parental Leave (Day)"
]

LEAVE_TYPE_PAYLOAD_MAP = {
    "Annual Leave": "特休(Annual Leave)",
    "Sick Leave": "病假(Sick Leave)",
    "Personal Leave": "事假(Personal Leave)",
    "Official Business Leave": "公出(Official Business Leave)",
    "Menstrual Leave": "生理假(Menstrual Leave)",
    "Family Care Leave": "家庭照顧假(Family Care Leave)",
    "Vitality Leave": "活力假(Vitality Leave)",
    "Bereavement Leave": "喪假(Bereavement Leave)",
    "Official Leave": "公假(Official Leave)",
    "Marriage Leave": "婚假(Marriage Leave)",
    "Occupational Injury Leave": "公傷假(Occupational Injury Leave)",
    "Paternity Leave / Accompanying Prenatal Check-up Leave": "陪產檢假/陪產假(Paternity Leave / Accompanying Prenatal Check-up Leave)",
    "Maternity Leave": "產假(Maternity Leave)",
    "Prenatal Check-up Leave": "產檢假(Prenatal Check-up Leave)",
    "Volunteer Leave": "志工假(Volunteer Leave)",
    "Flexible Parental Leave (Day)": "彈性育嬰留停(日)"
}

FLEX_PARENTAL_CATEGORIES = [
    "Apply 5 days in advance",
    "Primary caregiver illness / urgent matter",
    "Childcare service suspension",
    "School suspension",
    "Child illness"
]

FLEX_PARENTAL_CATEGORY_PAYLOAD_MAP = {
    "Apply 5 days in advance": "5日前提出申請",
    "Primary caregiver illness / urgent matter": "主要照顧者急病/急事",
    "Childcare service suspension": "小孩停托",
    "School suspension": "小孩停課",
    "Child illness": "小孩生病"
}

BEREAVEMENT_CATEGORIES = [
    "3 days - great-grandparents, siblings, spouse's grandparents",
    "6 days - grandparents, children, spouse's parents, adoptive or step parents",
    "8 days - parents, spouse, adoptive parents, step parents"
]

BEREAVEMENT_CATEGORY_PAYLOAD_MAP = {
    "3 days - great-grandparents, siblings, spouse's grandparents": "喪假3日(外曾/曾祖父母、兄弟姐妹、配偶之祖父母或外祖父母)",
    "6 days - grandparents, children, spouse's parents, adoptive or step parents": "喪假6日(祖/外父母、子女、配偶之父母、養父母或繼父母)",
    "8 days - parents, spouse, adoptive parents, step parents": "喪假8日(父母、配偶、養父母、繼父母)"
}

SPECIAL_DATE_REQUIRED_TYPES = [
    "Marriage Leave",
    "Paternity Leave / Accompanying Prenatal Check-up Leave",
    "Maternity Leave",
    "Prenatal Check-up Leave",
    "Bereavement Leave",
    "Flexible Parental Leave (Day)"
]

LEAVE_ATTACHMENT_REQUIRED_TYPES = [
    "Sick Leave",
    "Bereavement Leave",
    "Family Care Leave",
    "Maternity Leave",
    "Paternity Leave / Accompanying Prenatal Check-up Leave",
    "Prenatal Check-up Leave",
    "Official Leave",
    "Flexible Parental Leave (Day)"
]

OVERTIME_PAY_TYPE = "PAY"

OVERTIME_TYPES = [
    "10 Work overtime on weekdays",
    "20 Work overtime on holidays - no transportation expenses",
    "25 Work overtime on holidays - foreign employees select 20",
    "60 Work overtime on national holidays - foreign employees select 63",
    "63 Work overtime on national holidays - no transportation expenses",
    "100 Overtime on rescheduled workday - foreign employees select 101",
    "101 Overtime on rescheduled workday - no transportation expenses"
]

OVERTIME_TYPE_PAYLOAD_MAP = {
    "10 Work overtime on weekdays": "10平日加班 Work overtime on weekdays",
    "20 Work overtime on holidays - no transportation expenses": "20休息日加班(無交通費) Work overtime on holidays (no transportation expenses)",
    "25 Work overtime on holidays - foreign employees select 20": "25休息日加班 Foreign employees select 20",
    "60 Work overtime on national holidays - foreign employees select 63": "60國定假日加班 Foreign employees select 63",
    "63 Work overtime on national holidays - no transportation expenses": "63國定假日加班(無交通費) Work overtime on national holidays (no transportation expenses)",
    "100 Overtime on rescheduled workday - foreign employees select 101": "100調班日加班 Foreign employees select 101",
    "101 Overtime on rescheduled workday - no transportation expenses": "101調班日加班(無交通費) Overtime on Rescheduled Workday (no transportation expenses)"
}

BREAK_HOUR_OPTIONS = ["0", "0.5", "1", "1.5", "2"]

CORRECTION_REASONS = [
    "Forgot to Bring Access Card",
    "Forgot to Clock In",
    "Forgot to Clock Out",
    "Earlier than the card swipe time"
]

CORRECTION_REASON_PAYLOAD_MAP = {
    "Forgot to Bring Access Card": "忘記帶卡(Forgot to Bring Access Card)",
    "Forgot to Clock In": "忘記刷卡上班(Forgot to Clock In)",
    "Forgot to Clock Out": "忘記刷卡下班(Forgot to Clock Out)",
    "Earlier than the card swipe time": "早於刷卡時間(Earlier than the card swipe time)"
}

MAX_UPLOAD_SIZE_MB = 10
UPLOAD_TYPES = ["png", "jpg", "jpeg", "pdf"]


# ==============================
# Utility Functions
# ==============================

def back_to_menu_button():
    if st.button("Back to Main Menu", use_container_width=True):
        st.switch_page("登入頁.py")


def info_box(text):
    st.markdown(f'<div class="hint-box">{text}</div>', unsafe_allow_html=True)


def warning_box(text):
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)


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


def is_annual_leave(leave_type):
    return leave_type == "Annual Leave"


def is_special_date_required(leave_type):
    return leave_type in SPECIAL_DATE_REQUIRED_TYPES


def is_leave_attachment_required(leave_type):
    return leave_type in LEAVE_ATTACHMENT_REQUIRED_TYPES


def special_date_label(leave_type):
    if leave_type == "Marriage Leave":
        return "Date * | Marriage registration date"
    if leave_type == "Maternity Leave":
        return "Date * | Expected delivery date / birth date"
    if leave_type == "Prenatal Check-up Leave":
        return "Date * | Expected delivery date"
    if leave_type == "Paternity Leave / Accompanying Prenatal Check-up Leave":
        return "Date * | Expected delivery date / birth date"
    if leave_type == "Bereavement Leave":
        return "Date * | Date of relative's passing"
    if leave_type == "Flexible Parental Leave (Day)":
        return "Date * | Child's birthday"
    return "Date *"


def validate_upload(uploaded_file):
    if uploaded_file is None:
        return None

    size_mb = uploaded_file.size / 1024 / 1024
    if size_mb > MAX_UPLOAD_SIZE_MB:
        return f"The attachment must not exceed {MAX_UPLOAD_SIZE_MB}MB. Current size is about {size_mb:.2f}MB."

    return None


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


def build_base_payload(request_type_normalized, form_type_raw, employee_name, employee_id, email):
    timestamp = make_timestamp()
    response_key = make_response_key(timestamp, employee_id, email)

    return {
        "secret": SECRET_KEY,
        "responseKey": response_key,
        "timestamp": timestamp,
        "source": {
            "platform": "Streamlit",
            "triggerType": "streamlit_form_submit",
            "formTypeNormalized": request_type_normalized
        },
        "applicant": {
            "applicantName": employee_name,
            "employeeId": employee_id,
            "email": email
        },
        "request": {
            "formTypeRaw": form_type_raw,
            "formTypeNormalized": request_type_normalized
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


def request_type_to_payload(request_type):
    if request_type == "Leave":
        return "leave", "請假(Leave)"
    if request_type == "Overtime":
        return "overtime", "加班(Overtime)"
    return "correction", "補登(Timesheet Correction)"


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

st.title("MA1100&1P00 Employee Attendance Application Form")
st.caption("MA1100&1P00 人員出勤申報表單")
back_to_menu_button()
st.divider()

st.subheader("Applicant Information")
info_box("Employee ID and name are filled from your login information. Please confirm the information is correct.")

col1, col2 = st.columns(2)
with col1:
    st.text_input("Email *", value=email, disabled=True)
    st.text_input("Employee ID *", value=employee_id, disabled=True)
    st.text_input("Name *", value=employee_name, disabled=True)
with col2:
    st.text_input("Department", value=department, disabled=True)
    st.text_input("Level", value=level, disabled=True)
    st.text_input("Region", value=region, disabled=True)

st.divider()

request_type = st.radio(
    "Choose Form Type *",
    REQUEST_TYPES,
    horizontal=True
)

st.divider()


# ==============================
# Defaults
# ==============================

uploaded_file = None

leave_type = None
flex_parental_category = ""
bereavement_category = ""
special_date = None
leave_start_date = date.today()
leave_end_date = date.today()
leave_start_hour = "08"
leave_start_minute = "00"
leave_end_hour = "17"
leave_end_minute = "00"
leave_reason = ""

select_zero = "0"
pay_type = OVERTIME_PAY_TYPE
overtime_type = None
overtime_start_date = date.today()
overtime_end_date = date.today()
overtime_start_hour = "17"
overtime_start_minute = "00"
overtime_end_hour = "19"
overtime_end_minute = "00"
overtime_reason = ""
break_hours = "0"
no_break_reason = ""

correction_reason = None
correction_start_date = date.today()
correction_start_hour = "08"
correction_start_minute = "00"
correction_end_date = date.today()
correction_end_hour = "17"
correction_end_minute = "00"


# ==============================
# Leave
# ==============================

if request_type == "Leave":
    st.subheader("Leave Application Form")

    warning_box(
        "Annual leave must be applied at least two days in advance and approved by your direct supervisor. "
        "Supporting documents are required for sick leave, bereavement leave, family care leave, maternity leave, "
        "paternity leave, prenatal check-up leave, accompanying prenatal check-up leave, official leave, and flexible parental leave."
    )

    leave_type = st.selectbox("Leave Type *", LEAVE_TYPES)

    if leave_type == "Flexible Parental Leave (Day)":
        flex_parental_category = st.radio(
            "Flexible Parental Leave Category *",
            FLEX_PARENTAL_CATEGORIES
        )

    if leave_type == "Bereavement Leave":
        bereavement_category = st.radio(
            "Bereavement Category *",
            BEREAVEMENT_CATEGORIES
        )

    if is_special_date_required(leave_type):
        special_date = st.date_input(
            special_date_label(leave_type),
            value=date.today()
        )

    if is_leave_attachment_required(leave_type):
        warning_box(
            "Supporting documents are required for this leave type. The leave application is not valid without completed document upload. "
            "Only one file is allowed. If you have multiple files, please combine them into a single PDF or image file. Maximum file size is 10MB."
        )
        uploaded_file = st.file_uploader(
            "Upload Supporting Documents for Leave *",
            type=UPLOAD_TYPES,
            accept_multiple_files=False
        )
    else:
        uploaded_file = None

    if uploaded_file is not None:
        upload_error = validate_upload(uploaded_file)
        if upload_error:
            st.error(upload_error)

    st.markdown("#### Leave Start Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_start_date = st.date_input("Start Date *", value=date.today())
    with col2:
        leave_start_hour = st.selectbox("Start Time(Hour) *", HOUR_OPTIONS, index=8)
    with col3:
        leave_start_minute = st.selectbox("Start Time(Minute) *", MINUTE_OPTIONS, index=0)

    st.markdown("#### Leave End Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_end_date = st.date_input("End Date *", value=date.today())
    with col2:
        leave_end_hour = st.selectbox("End Time(Hour) *", HOUR_OPTIONS, index=17)
    with col3:
        leave_end_minute = st.selectbox("End Time(Minute) *", MINUTE_OPTIONS, index=0)

    leave_reason = st.text_area("Leave Reason *")

    if is_annual_leave(leave_type):
        two_days_later = date.today() + timedelta(days=2)
        if leave_start_date < two_days_later:
            st.warning("Reminder: Annual leave must be applied at least two days in advance and approved by your direct supervisor.")


# ==============================
# Overtime
# ==============================

elif request_type == "Overtime":
    st.subheader("Overtime Application Form")

    warning_box(
        "Please fill in this form at the end of daily overtime, after swiping your card after getting off work."
    )

    select_zero = st.radio("Please select 0 *", ["0"], horizontal=True)
    pay_type = st.radio("Overtime Pay Type *", ["PAY"], horizontal=True)

    overtime_type = st.radio(
        "Overtime Type *",
        OVERTIME_TYPES
    )

    info_box(
        "Foreign employees: Select Code 10 for weekday overtime. For holiday overtime, select no transportation expenses "
        "(Code 20 or 63), and do not select options with transportation expenses (Code 25 or 60)."
    )

    st.markdown("#### Overtime Start Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_start_date = st.date_input("Start Date *", value=date.today())
    with col2:
        overtime_start_hour = st.selectbox("Start Time(Hour) *", HOUR_OPTIONS, index=17)
    with col3:
        overtime_start_minute = st.selectbox("Start Time(Minute) *", MINUTE_OPTIONS, index=0)

    st.markdown("#### Overtime End Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_end_date = st.date_input("End Date *", value=date.today())
    with col2:
        overtime_end_hour = st.selectbox("End Time(Hour) *", HOUR_OPTIONS, index=19)
    with col3:
        overtime_end_minute = st.selectbox("End Time(Minute) *", MINUTE_OPTIONS, index=0)

    overtime_reason = st.text_area("Overtime Reason *")

    break_hours = st.radio(
        "Break Time - Hours *",
        BREAK_HOUR_OPTIONS,
        horizontal=True
    )

    if break_hours == "0":
        warning_box("If you selected no rest, please fill in the reason below.")
        no_break_reason = st.text_area("No Break Reason *")
    else:
        no_break_reason = ""

    st.info("Attachment upload is not required for overtime requests.")


# ==============================
# Timesheet Correction
# ==============================

else:
    st.subheader("Timesheet Correction Application Form")

    warning_box(
        "If you forget to clock in/out, do not have your card, or encounter attendance irregularities, "
        "you must complete a manual attendance correction. In case of forgotten card, submission of the borrowing registration form is required."
    )

    correction_reason = st.radio(
        "Timesheet Correction Reason *",
        CORRECTION_REASONS
    )

    if correction_reason == "Forgot to Clock In":
        st.markdown("#### Start Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("Start Date *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("Start Time(Hour) *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("Start Time(Minute) *", MINUTE_OPTIONS, index=0)

        correction_end_date = correction_start_date
        correction_end_hour = correction_start_hour
        correction_end_minute = correction_start_minute

    elif correction_reason in [
        "Forgot to Clock Out",
        "Earlier than the card swipe time"
    ]:
        st.markdown("#### End Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("End Date *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("End Time(Hour) *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("End Time(Minute) *", MINUTE_OPTIONS, index=0)

        correction_start_date = correction_end_date
        correction_start_hour = correction_end_hour
        correction_start_minute = correction_end_minute

    elif correction_reason == "Forgot to Bring Access Card":
        warning_box(
            "In case of forgotten card, submission of the borrowing registration form is required. "
            "The correction is not valid without completed document upload. Only one file is allowed. Maximum file size is 10MB."
        )

        st.markdown("#### Start Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("Start Date *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("Start Time(Hour) *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("Start Time(Minute) *", MINUTE_OPTIONS, index=0)

        st.markdown("#### End Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("End Date *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("End Time(Hour) *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("End Time(Minute) *", MINUTE_OPTIONS, index=0)

        uploaded_file = st.file_uploader(
            "Upload Supporting Documents for Timesheet Correction *",
            type=UPLOAD_TYPES,
            accept_multiple_files=False
        )

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                st.error(upload_error)


# ==============================
# Required Validation
# ==============================

def validate_required_fields():
    errors = []

    if not email.strip():
        errors.append("Email")

    if not employee_id.strip():
        errors.append("Employee ID")

    if " " in employee_id:
        errors.append("Employee ID cannot contain spaces")

    if not employee_name.strip():
        errors.append("Name")

    if " " in employee_name:
        errors.append("Name cannot contain spaces")

    if request_type == "Leave":
        if not leave_type:
            errors.append("Leave Type")

        if leave_type == "Flexible Parental Leave (Day)" and not flex_parental_category:
            errors.append("Flexible Parental Leave Category")

        if leave_type == "Bereavement Leave" and not bereavement_category:
            errors.append("Bereavement Category")

        if is_special_date_required(leave_type) and special_date is None:
            errors.append("Date")

        if is_leave_attachment_required(leave_type) and uploaded_file is None:
            errors.append("Upload Supporting Documents for Leave")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

        if not leave_reason.strip():
            errors.append("Leave Reason")

    elif request_type == "Overtime":
        if select_zero != "0":
            errors.append("Please select 0")

        if pay_type != "PAY":
            errors.append("Overtime Pay Type")

        if not overtime_type:
            errors.append("Overtime Type")

        if not overtime_reason.strip():
            errors.append("Overtime Reason")

        if not break_hours:
            errors.append("Break Time")

        if break_hours == "0" and not no_break_reason.strip():
            errors.append("No Break Reason")

    else:
        if not correction_reason:
            errors.append("Timesheet Correction Reason")

        if correction_reason == "Forgot to Bring Access Card" and uploaded_file is None:
            errors.append("Upload Supporting Documents for Timesheet Correction")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

    return errors


# ==============================
# Submit
# ==============================

st.divider()

if st.button("Submit", use_container_width=True):

    errors = validate_required_fields()

    if errors:
        st.error("❌ Please check the following fields:\n\n- " + "\n- ".join(errors))
        st.stop()

    form_type_normalized, form_type_raw = request_type_to_payload(request_type)

    payload = build_base_payload(
        request_type_normalized=form_type_normalized,
        form_type_raw=form_type_raw,
        employee_name=employee_name,
        employee_id=employee_id,
        email=email
    )

    try:
        attachment_links = build_file_info(uploaded_file)

        if request_type == "Leave":
            start_dt = combine_datetime(leave_start_date, leave_start_hour, leave_start_minute)
            end_dt = combine_datetime(leave_end_date, leave_end_hour, leave_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ Leave end time cannot be earlier than or equal to start time.")
                st.stop()

            leave_type_payload = LEAVE_TYPE_PAYLOAD_MAP[leave_type]
            flex_parental_payload = FLEX_PARENTAL_CATEGORY_PAYLOAD_MAP.get(flex_parental_category, "")
            bereavement_payload = BEREAVEMENT_CATEGORY_PAYLOAD_MAP.get(bereavement_category, "")

            payload["leave"].update({
                "leaveType": leave_type_payload,
                "flexParentalLeaveCategory": flex_parental_payload,
                "bereavementCategory": bereavement_payload,
                "specialDateRaw": format_date_raw(special_date) if special_date else "",
                "specialDateIso": special_date.isoformat() if special_date else "",
                "attachmentLinks": attachment_links,
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
                "leaveReason": leave_reason.strip()
            })

        elif request_type == "Overtime":
            start_dt = combine_datetime(overtime_start_date, overtime_start_hour, overtime_start_minute)
            end_dt = combine_datetime(overtime_end_date, overtime_end_hour, overtime_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ Overtime end time cannot be earlier than or equal to start time.")
                st.stop()

            overtime_type_payload = OVERTIME_TYPE_PAYLOAD_MAP[overtime_type]

            payload["overtime"].update({
                "selectZero": select_zero,
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

        else:
            start_dt = combine_datetime(correction_start_date, correction_start_hour, correction_start_minute)
            end_dt = combine_datetime(correction_end_date, correction_end_hour, correction_end_minute)

            if correction_reason == "Forgot to Bring Access Card" and not validate_start_end(start_dt, end_dt):
                st.error("❌ Correction end time cannot be earlier than or equal to start time.")
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
