import streamlit as st
import requests
import base64
from datetime import datetime, date, timedelta, timezone


# ==============================
# 基本設定
# ==============================

POWER_AUTOMATE_URL = st.secrets["SUBMIT_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="出勤申請系統",
    page_icon="📝",
    layout="centered"
)


# ==============================
# UI 樣式
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
# 登入檢查
# ==============================

user_info = st.session_state.get("user_info")

if not user_info:
    st.warning("登入已失效，請重新登入。")
    if st.button("返回登入頁", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")
    st.stop()


# ==============================
# 表單選項 - 依 Google Form 題目設計
# ==============================

HOUR_OPTIONS = [f"{i:02d}" for i in range(24)]
MINUTE_OPTIONS = ["00", "30"]

REQUEST_TYPES = [
    "請假(Leave)",
    "加班(Overtime)",
    "補登(Timesheet Correction)"
]

LEAVE_TYPES = [
    "特休(Annual Leave)",
    "病假(Sick Leave)",
    "事假(Personal Leave)",
    "公出(Official Business Leave)",
    "生理假(Menstrual Leave)",
    "家庭照顧假(Family Care Leave)",
    "活力假(Vitality Leave)",
    "喪假(Bereavement Leave)",
    "公假(Official Leave)",
    "婚假(Marriage Leave)",
    "公傷假(Occupational Injury Leave)",
    "陪產檢假/陪產假(Paternity Leave / Accompanying Prenatal Check-up Leave)",
    "產假(Maternity Leave)",
    "產檢假(Prenatal Check-up Leave)",
    "志工假(Volunteer Leave)",
    "彈性育嬰留停(日)"
]

FLEX_PARENTAL_CATEGORIES = [
    "5日前提出申請",
    "主要照顧者急病/急事",
    "小孩停托",
    "小孩停課",
    "小孩生病"
]

BEREAVEMENT_CATEGORIES = [
    "喪假3日(外曾/曾祖父母、兄弟姐妹、配偶之祖父母或外祖父母)",
    "喪假6日(祖/外父母、子女、配偶之父母、養父母或繼父母)",
    "喪假8日(父母、配偶、養父母、繼父母)"
]

SPECIAL_DATE_LEAVE_KEYWORDS = [
    "婚假",
    "陪產檢假",
    "陪產假",
    "產假",
    "產檢假",
    "喪假",
    "彈性育嬰留停"
]

# 使用者確認：以下假別需附證明才能申請
LEAVE_ATTACHMENT_REQUIRED_KEYWORDS = [
    "病假",
    "喪假",
    "家庭照顧假",
    "產假",
    "陪產假",
    "產檢假",
    "陪產檢假",
    "公假",
    "彈性育嬰留停"
]

OVERTIME_PAY_TYPE = "PAY"

OVERTIME_TYPES = [
    "10平日加班 Work overtime on weekdays",
    "20休息日加班(無交通費) Work overtime on holidays (no transportation expenses)",
    "25休息日加班 Foreign employees select 20",
    "60國定假日加班 Foreign employees select 63",
    "63國定假日加班(無交通費) Work overtime on national holidays (no transportation expenses)",
    "100調班日加班 Foreign employees select 101",
    "101調班日加班(無交通費) Overtime on Rescheduled Workday (no transportation expenses)"
]

BREAK_HOUR_OPTIONS = ["0", "0.5", "1", "1.5", "2"]

CORRECTION_REASONS = [
    "忘記帶卡(Forgot to Bring Access Card)",
    "忘記刷卡上班(Forgot to Clock In)",
    "忘記刷卡下班(Forgot to Clock Out)",
    "早於刷卡時間(Earlier than the card swipe time)"
]

MAX_UPLOAD_SIZE_MB = 10
UPLOAD_TYPES = ["png", "jpg", "jpeg", "pdf"]


# ==============================
# 共用函式
# ==============================

def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")


def bilingual_hint(zh_text, en_text):
    st.markdown(
        f"""
        <div class="hint-box">
        {zh_text}<br>
        <span style="color:#374151;">{en_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def warning_hint(zh_text, en_text):
    st.markdown(
        f"""
        <div class="warning-box">
        {zh_text}<br>
        <span style="color:#374151;">{en_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


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
    return "特休" in leave_type


def is_special_date_required(leave_type):
    return any(keyword in leave_type for keyword in SPECIAL_DATE_LEAVE_KEYWORDS)


def is_leave_attachment_required(leave_type):
    return any(keyword in leave_type for keyword in LEAVE_ATTACHMENT_REQUIRED_KEYWORDS)


def special_date_label(leave_type):
    if "婚假" in leave_type:
        return "日期 *｜婚假：登記結婚日期"
    if "產假" in leave_type:
        return "日期 *｜產假/流產假：預產期/出生日期"
    if "產檢假" in leave_type:
        return "日期 *｜產檢假：預產期日期"
    if "陪產檢假" in leave_type or "陪產假" in leave_type:
        return "日期 *｜陪產假：預產期/出生日期"
    if "喪假" in leave_type:
        return "日期 *｜喪假：親人辭世日期"
    if "彈性育嬰留停" in leave_type:
        return "日期 *｜彈性育嬰留停(日)：小孩生日日期"
    return "日期 *"


def validate_upload(uploaded_file):
    if uploaded_file is None:
        return None

    size_mb = uploaded_file.size / 1024 / 1024
    if size_mb > MAX_UPLOAD_SIZE_MB:
        return f"附件大小不可超過 {MAX_UPLOAD_SIZE_MB}MB，目前約 {size_mb:.2f}MB。"

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


def request_type_to_normalized(request_type):
    if request_type == "請假(Leave)":
        return "leave"
    if request_type == "加班(Overtime)":
        return "overtime"
    return "correction"


# ==============================
# 登入人員資料
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")
level = user_info.get("level", "")
region = user_info.get("region", "")


# ==============================
# 頁面
# ==============================

st.title("MA1100&1P00 人員出勤申報表單")
st.caption("MA1100&1P00 Employee Attendance Application Form")
back_to_menu_button()
st.divider()

with st.container():
    st.subheader("申請人資料")
    bilingual_hint(
        "工號與姓名由登入資料自動帶入，請確認資料正確。",
        "Employee ID and name are filled from your login information. Please confirm the information is correct."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("電子郵件 Email *", value=email, disabled=True)
        st.text_input("工號 Employee ID *", value=employee_id, disabled=True)
        st.text_input("姓名 Name *", value=employee_name, disabled=True)
    with col2:
        st.text_input("部門 Department", value=department, disabled=True)
        st.text_input("Level", value=level, disabled=True)
        st.text_input("Region", value=region, disabled=True)

st.divider()

request_type = st.radio(
    "請選擇申請需求項目 Choose Form Type *",
    REQUEST_TYPES,
    horizontal=True
)

st.divider()


# ==============================
# 預設變數
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
# 請假
# ==============================

if request_type == "請假(Leave)":
    st.subheader("請假申請單 Leave Application Form")

    warning_hint(
        "特休需於兩天前申請，並由主管同意才能送出表單。病假、喪假、家庭照顧假、產假、陪產假、產檢假、陪產檢假、公假、彈性育嬰留停皆需附上證明。",
        "Annual leave must be applied at least two days in advance and approved by your direct supervisor. Supporting documents are required for specified leave types."
    )

    leave_type = st.selectbox("選擇假別 Leave Type *", LEAVE_TYPES)

    if "彈性育嬰留停" in leave_type:
        flex_parental_category = st.radio(
            "選擇彈性育嬰留停假別分類 *",
            FLEX_PARENTAL_CATEGORIES
        )

    if "喪假" in leave_type:
        bereavement_category = st.radio(
            "選擇喪假假別分類 *",
            BEREAVEMENT_CATEGORIES
        )

    if is_special_date_required(leave_type):
        special_date = st.date_input(
            special_date_label(leave_type),
            value=date.today()
        )

    if is_leave_attachment_required(leave_type):
        warning_hint(
            "此假別需上傳請假證明。若無上傳完成，視同無請假。",
            "Supporting document is required for this leave type. The leave application is not valid without completed document upload."
        )
        uploaded_file = st.file_uploader(
            "請假附件上傳 Upload File *",
            type=UPLOAD_TYPES,
            accept_multiple_files=False
        )
    else:
        uploaded_file = None

    if uploaded_file is not None:
        upload_error = validate_upload(uploaded_file)
        if upload_error:
            st.error(upload_error)

    st.markdown("#### 請假開始日期與時間 Start Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_start_date = st.date_input("請假開始日期 Start Date *", value=date.today())
    with col2:
        leave_start_hour = st.selectbox("請假開始時間(小時) *", HOUR_OPTIONS, index=8)
    with col3:
        leave_start_minute = st.selectbox("請假開始時間(分鐘) *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 請假結束日期與時間 End Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_end_date = st.date_input("請假結束日期 End Date *", value=date.today())
    with col2:
        leave_end_hour = st.selectbox("請假結束時間(小時) *", HOUR_OPTIONS, index=17)
    with col3:
        leave_end_minute = st.selectbox("請假結束時間(分鐘) *", MINUTE_OPTIONS, index=0)

    leave_reason = st.text_area("請假原因 Leave Reason *")

    if is_annual_leave(leave_type):
        two_days_later = date.today() + timedelta(days=2)
        if leave_start_date < two_days_later:
            st.warning("提醒：特休需於兩天前申請，並由主管同意才能送出表單。")


# ==============================
# 加班
# ==============================

elif request_type == "加班(Overtime)":
    st.subheader("加班申請單 Overtime Application Form")

    warning_hint(
        "請於每日加班結束，刷卡下班後再填寫此表單。",
        "Please fill in this form at the end of daily overtime, after swiping your card after getting off work."
    )

    select_zero = st.radio("請選0 *", ["0"], horizontal=True)
    pay_type = st.radio("加班類型 *", ["PAY"], horizontal=True)

    overtime_type = st.radio(
        "加班類型 Overtime Type *",
        OVERTIME_TYPES
    )

    bilingual_hint(
        "外籍同仁：平日加班請選 Code 10；假日加班請選無交通費 Code 20 或 63，請勿選擇含交通費選項 Code 25 或 60。",
        "Foreign employees: Select Code 10 for weekday overtime. For holiday overtime, select no transportation expenses (Code 20 or 63), and do not select options with transportation expenses (Code 25 or 60)."
    )

    st.markdown("#### 加班開始日期與時間 Start Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_start_date = st.date_input("加班開始日期 Start Date *", value=date.today())
    with col2:
        overtime_start_hour = st.selectbox("加班開始時間(小時) *", HOUR_OPTIONS, index=17)
    with col3:
        overtime_start_minute = st.selectbox("加班開始時間(分鐘) *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 加班結束日期與時間 End Date & Time")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_end_date = st.date_input("加班結束日期 End Date *", value=date.today())
    with col2:
        overtime_end_hour = st.selectbox("加班結束時間(小時) *", HOUR_OPTIONS, index=19)
    with col3:
        overtime_end_minute = st.selectbox("加班結束時間(分鐘) *", MINUTE_OPTIONS, index=0)

    overtime_reason = st.text_area("加班原因 Overtime Reason *")

    break_hours = st.radio(
        "加班休息時間(Break Time)_小時/Hours *",
        BREAK_HOUR_OPTIONS,
        horizontal=True
    )

    if break_hours == "0":
        warning_hint(
            "如勾選未休息，請於下方填寫原因。",
            "If you selected no rest, please fill in the reason below."
        )
        no_break_reason = st.text_area("未休息原因 No Break Reason *")
    else:
        no_break_reason = ""

    st.info("加班申請不需上傳附件。")


# ==============================
# 補登
# ==============================

else:
    st.subheader("工時補登申請單 Timesheet Correction Application Form")

    warning_hint(
        "如有忘記刷卡、未帶卡，或是出勤異常，皆需完成補登。忘記帶卡需上傳借用登記表。",
        "If you forget to clock in/out, do not have your card, or encounter attendance irregularities, you must complete a correction. In case of forgotten card, the borrowing registration form is required."
    )

    correction_reason = st.radio(
        "補登原因 Timesheet Correction Reason *",
        CORRECTION_REASONS
    )

    if correction_reason == "忘記刷卡上班(Forgot to Clock In)":
        st.markdown("#### 補登上班日期與時間 Start Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("補登上班日期 Start Date *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("補登上班時間(小時) *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("補登上班時間(分鐘) *", MINUTE_OPTIONS, index=0)

        correction_end_date = correction_start_date
        correction_end_hour = correction_start_hour
        correction_end_minute = correction_start_minute

    elif correction_reason in [
        "忘記刷卡下班(Forgot to Clock Out)",
        "早於刷卡時間(Earlier than the card swipe time)"
    ]:
        st.markdown("#### 補登下班日期與時間 End Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("補登下班日期 End Date *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("補登下班時間(小時) *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("補登下班時間(分鐘) *", MINUTE_OPTIONS, index=0)

        correction_start_date = correction_end_date
        correction_start_hour = correction_end_hour
        correction_start_minute = correction_end_minute

    elif correction_reason == "忘記帶卡(Forgot to Bring Access Card)":
        warning_hint(
            "忘記帶卡需上傳借用登記表。若無上傳完成，視同無補登。",
            "In case of forgotten card, submission of the borrowing registration form is required. The correction is not valid without completed document upload."
        )

        st.markdown("#### 補登上班日期與時間 Start Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("補登上班日期 Start Date *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("補登上班時間(小時) *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("補登上班時間(分鐘) *", MINUTE_OPTIONS, index=0)

        st.markdown("#### 補登下班日期與時間 End Date & Time")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("補登下班日期 End Date *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("補登下班時間(小時) *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("補登下班時間(分鐘) *", MINUTE_OPTIONS, index=0)

        uploaded_file = st.file_uploader(
            "補登附件上傳 Upload File *",
            type=UPLOAD_TYPES,
            accept_multiple_files=False
        )

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                st.error(upload_error)


# ==============================
# 必填檢查
# ==============================

def validate_required_fields():
    errors = []

    if not email.strip():
        errors.append("電子郵件 Email")

    if not employee_id.strip():
        errors.append("工號 Employee ID")

    if " " in employee_id:
        errors.append("工號不可含空白 Employee ID cannot contain spaces")

    if not employee_name.strip():
        errors.append("姓名 Name")

    if " " in employee_name:
        errors.append("姓名不可含空白 Name cannot contain spaces")

    if request_type == "請假(Leave)":
        if not leave_type:
            errors.append("選擇假別 Leave Type")

        if "彈性育嬰留停" in leave_type and not flex_parental_category:
            errors.append("彈性育嬰留停假別分類")

        if "喪假" in leave_type and not bereavement_category:
            errors.append("喪假假別分類")

        if is_special_date_required(leave_type) and special_date is None:
            errors.append("特殊日期 Date")

        if is_leave_attachment_required(leave_type) and uploaded_file is None:
            errors.append("請假附件上傳 Upload File")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

        if not leave_reason.strip():
            errors.append("請假原因 Leave Reason")

    elif request_type == "加班(Overtime)":
        if select_zero != "0":
            errors.append("請選0")

        if pay_type != "PAY":
            errors.append("加班類型 PAY")

        if not overtime_type:
            errors.append("加班類型 Overtime Type")

        if not overtime_reason.strip():
            errors.append("加班原因 Overtime Reason")

        if not break_hours:
            errors.append("加班休息時間 Break Time")

        if break_hours == "0" and not no_break_reason.strip():
            errors.append("未休息原因 No Break Reason")

    else:
        if not correction_reason:
            errors.append("補登原因 Timesheet Correction Reason")

        if correction_reason == "忘記帶卡(Forgot to Bring Access Card)" and uploaded_file is None:
            errors.append("補登附件上傳 Upload File")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

    return errors


# ==============================
# 送出
# ==============================

st.divider()

if st.button("送出申請 Submit", use_container_width=True):

    errors = validate_required_fields()

    if errors:
        st.error("❌ 以下欄位需確認：\n\n- " + "\n- ".join(errors))
        st.stop()

    form_type_normalized = request_type_to_normalized(request_type)

    payload = build_base_payload(
        request_type_normalized=form_type_normalized,
        form_type_raw=request_type,
        employee_name=employee_name,
        employee_id=employee_id,
        email=email
    )

    try:
        attachment_links = build_file_info(uploaded_file)

        if request_type == "請假(Leave)":
            start_dt = combine_datetime(leave_start_date, leave_start_hour, leave_start_minute)
            end_dt = combine_datetime(leave_end_date, leave_end_hour, leave_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ 請假結束時間不可早於或等於開始時間。")
                st.stop()

            payload["leave"].update({
                "leaveType": leave_type,
                "flexParentalLeaveCategory": flex_parental_category,
                "bereavementCategory": bereavement_category,
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

        elif request_type == "加班(Overtime)":
            start_dt = combine_datetime(overtime_start_date, overtime_start_hour, overtime_start_minute)
            end_dt = combine_datetime(overtime_end_date, overtime_end_hour, overtime_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ 加班結束時間不可早於或等於開始時間。")
                st.stop()

            payload["overtime"].update({
                "selectZero": select_zero,
                "payType": pay_type,
                "overtimeType": overtime_type,
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

            # 忘記帶卡是完整起訖；其他補單點時間不需檢查 start < end
            if correction_reason == "忘記帶卡(Forgot to Bring Access Card)" and not validate_start_end(start_dt, end_dt):
                st.error("❌ 補登結束時間不可早於或等於開始時間。")
                st.stop()

            payload["correction"].update({
                "correctionReason": correction_reason,
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
            st.success("✅ 申請送出成功")
        else:
            st.error(f"❌ Flow 回傳錯誤：{response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 無法連線到 Power Automate：{str(e)}")

    except Exception as e:
        st.error(f"❌ 發生錯誤：{str(e)}")
