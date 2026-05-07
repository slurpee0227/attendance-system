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
        .stDateInput input {
            background-color: white !important;
            color: #111827 !important;
            border-radius: 10px;
            border: 1px solid #d1d5db !important;
        }

        div[data-baseweb="select"] > div {
            background-color: white !important;
            color: #111827 !important;
            border-radius: 10px !important;
            border: 1px solid #d1d5db !important;
        }

        div[data-baseweb="select"] span {
            color: #111827 !important;
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
# 表單選項
# ==============================

HOUR_OPTIONS = [f"{i:02d}" for i in range(24)]
MINUTE_OPTIONS = ["00", "30"]

REQUEST_TYPES = ["請假", "加班", "補登"]

REQUEST_TYPE_PAYLOAD_MAP = {
    "請假": {
        "raw": "請假(Leave)",
        "normalized": "leave"
    },
    "加班": {
        "raw": "加班(Overtime)",
        "normalized": "overtime"
    },
    "補登": {
        "raw": "補登(Timesheet Correction)",
        "normalized": "correction"
    }
}

LEAVE_TYPES = [
    "特休",
    "病假",
    "事假",
    "公出",
    "生理假",
    "家庭照顧假",
    "活力假",
    "喪假",
    "公假",
    "婚假",
    "公傷假",
    "陪產檢假/陪產假",
    "產假",
    "產檢假",
    "志工假",
    "彈性育嬰留停(日)"
]

LEAVE_TYPE_PAYLOAD_MAP = {
    "特休": "特休(Annual Leave)",
    "病假": "病假(Sick Leave)",
    "事假": "事假(Personal Leave)",
    "公出": "公出(Official Business Leave)",
    "生理假": "生理假(Menstrual Leave)",
    "家庭照顧假": "家庭照顧假(Family Care Leave)",
    "活力假": "活力假(Vitality Leave)",
    "喪假": "喪假(Bereavement Leave)",
    "公假": "公假(Official Leave)",
    "婚假": "婚假(Marriage Leave)",
    "公傷假": "公傷假(Occupational Injury Leave)",
    "陪產檢假/陪產假": "陪產檢假/陪產假(Paternity Leave / Accompanying Prenatal Check-up Leave)",
    "產假": "產假(Maternity Leave)",
    "產檢假": "產檢假(Prenatal Check-up Leave)",
    "志工假": "志工假(Volunteer Leave)",
    "彈性育嬰留停(日)": "彈性育嬰留停(日)"
}

FLEX_PARENTAL_CATEGORIES = [
    "5日前提出申請",
    "主要照顧者急病/急事",
    "小孩停托",
    "小孩停課",
    "小孩生病"
]

BEREAVEMENT_CATEGORIES = [
    "喪假3日：外曾祖父母、曾祖父母、兄弟姊妹、配偶之祖父母或外祖父母",
    "喪假6日：祖父母、外祖父母、子女、配偶之父母、養父母或繼父母",
    "喪假8日：父母、配偶、養父母、繼父母"
]

BEREAVEMENT_CATEGORY_PAYLOAD_MAP = {
    "喪假3日：外曾祖父母、曾祖父母、兄弟姊妹、配偶之祖父母或外祖父母": "喪假3日(外曾/曾祖父母、兄弟姐妹、配偶之祖父母或外祖父母)",
    "喪假6日：祖父母、外祖父母、子女、配偶之父母、養父母或繼父母": "喪假6日(祖/外父母、子女、配偶之父母、養父母或繼父母)",
    "喪假8日：父母、配偶、養父母、繼父母": "喪假8日(父母、配偶、養父母、繼父母)"
}

SPECIAL_DATE_LEAVE_KEYWORDS = [
    "婚假",
    "陪產檢假",
    "陪產假",
    "產假",
    "產檢假",
    "喪假",
    "彈性育嬰留停"
]

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

OVERTIME_TYPES = [
    "10平日加班",
    "20休息日加班（無交通費）",
    "25休息日加班",
    "60國定假日加班",
    "63國定假日加班（無交通費）",
    "100調班日加班",
    "101調班日加班（無交通費）"
]

OVERTIME_TYPE_PAYLOAD_MAP = {
    "10平日加班": "10平日加班 Work overtime on weekdays",
    "20休息日加班（無交通費）": "20休息日加班(無交通費) Work overtime on holidays (no transportation expenses)",
    "25休息日加班": "25休息日加班 Foreign employees select 20",
    "60國定假日加班": "60國定假日加班 Foreign employees select 63",
    "63國定假日加班（無交通費）": "63國定假日加班(無交通費) Work overtime on national holidays (no transportation expenses)",
    "100調班日加班": "100調班日加班 Foreign employees select 101",
    "101調班日加班（無交通費）": "101調班日加班(無交通費) Overtime on Rescheduled Workday (no transportation expenses)"
}

BREAK_HOUR_OPTIONS = ["0", "0.5", "1", "1.5", "2"]

CORRECTION_REASONS = [
    "忘記帶卡",
    "忘記刷卡上班",
    "忘記刷卡下班",
    "早於刷卡時間"
]

CORRECTION_REASON_PAYLOAD_MAP = {
    "忘記帶卡": "忘記帶卡(Forgot to Bring Access Card)",
    "忘記刷卡上班": "忘記刷卡上班(Forgot to Clock In)",
    "忘記刷卡下班": "忘記刷卡下班(Forgot to Clock Out)",
    "早於刷卡時間": "早於刷卡時間(Earlier than the card swipe time)"
}

MAX_UPLOAD_SIZE_MB = 10
UPLOAD_TYPES = ["png", "jpg", "jpeg", "pdf"]


# ==============================
# 共用函式
# ==============================

def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")


def hint_box(text):
    st.markdown(
        f"""
        <div class="hint-box">{text}</div>
        """,
        unsafe_allow_html=True
    )


def warning_box(text):
    st.markdown(
        f"""
        <div class="warning-box">{text}</div>
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
    return leave_type == "特休"


def is_special_date_required(leave_type):
    return any(keyword in leave_type for keyword in SPECIAL_DATE_LEAVE_KEYWORDS)


def is_leave_attachment_required(leave_type):
    return any(keyword in leave_type for keyword in LEAVE_ATTACHMENT_REQUIRED_KEYWORDS)


def special_date_label(leave_type):
    if "婚假" in leave_type:
        return "日期 *（登記結婚日期）"
    if "陪產檢假" in leave_type or "陪產假" in leave_type:
        return "日期 *（預產期或出生日期）"
    if "產假" in leave_type:
        return "日期 *（預產期或出生日期）"
    if "產檢假" in leave_type:
        return "日期 *（預產期日期）"
    if "喪假" in leave_type:
        return "日期 *（親人辭世日期）"
    if "彈性育嬰留停" in leave_type:
        return "日期 *（小孩生日日期）"
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
back_to_menu_button()
st.divider()

with st.container():
    st.subheader("申請人資料")
    hint_box("工號與姓名由登入資料自動帶入，請確認資料正確。工號與姓名不可包含空白。外籍同仁請於姓名欄使用中文姓名。")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("電子郵件 *", value=email, disabled=True)
        st.text_input("工號 *", value=employee_id, disabled=True)
        st.text_input("姓名 *", value=employee_name, disabled=True)
    with col2:
        st.text_input("部門", value=department, disabled=True)
        st.text_input("層級", value=level, disabled=True)
        st.text_input("國籍", value=region, disabled=True)

st.divider()

request_type = st.radio(
    "請選擇申請需求項目 *",
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
pay_type = "PAY"
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

if request_type == "請假":
    st.subheader("請假申請單")

    warning_box("特休需於兩天前申請，並由主管同意才能送出表單。病假、喪假、家庭照顧假、產假、陪產假、產檢假、陪產檢假、公假、彈性育嬰留停皆需附上證明，才能申請。")

    leave_type = st.selectbox("選擇假別 *", LEAVE_TYPES)

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
        warning_box("此假別需上傳請假證明。若無上傳完成，視同無請假。附件僅允許上傳 1 個檔案，若有多個檔案，請先合併為 1 個 PDF 或圖片檔。檔案大小上限為 10MB。")
        uploaded_file = st.file_uploader(
            "請假附件上傳 *",
            type=UPLOAD_TYPES,
            accept_multiple_files=False
        )
    else:
        uploaded_file = None

    if uploaded_file is not None:
        upload_error = validate_upload(uploaded_file)
        if upload_error:
            st.error(upload_error)

    st.markdown("#### 請假開始日期與時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_start_date = st.date_input("請假開始日期 *", value=date.today())
    with col2:
        leave_start_hour = st.selectbox("請假開始時間（小時） *", HOUR_OPTIONS, index=8)
    with col3:
        leave_start_minute = st.selectbox("請假開始時間（分鐘） *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 請假結束日期與時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_end_date = st.date_input("請假結束日期 *", value=date.today())
    with col2:
        leave_end_hour = st.selectbox("請假結束時間（小時） *", HOUR_OPTIONS, index=17)
    with col3:
        leave_end_minute = st.selectbox("請假結束時間（分鐘） *", MINUTE_OPTIONS, index=0)

    leave_reason = st.text_area("請假原因 *")

    if is_annual_leave(leave_type):
        two_days_later = date.today() + timedelta(days=2)
        if leave_start_date < two_days_later:
            st.warning("提醒：特休需於兩天前申請，並由主管同意才能送出表單。")


# ==============================
# 加班
# ==============================

elif request_type == "加班":
    st.subheader("加班申請單")

    warning_box("請於每日加班結束，刷卡下班後再填寫此表單。")

    select_zero = st.radio("請選 0 *", ["0"], horizontal=True)
    pay_type = st.radio("給付方式 *", ["PAY"], horizontal=True)

    overtime_type = st.radio(
        "加班類型 *",
        OVERTIME_TYPES
    )

    hint_box("外籍同仁：平日加班請選 Code 10；假日加班請選無交通費 Code 20 或 63，請勿選擇含交通費選項 Code 25 或 60。")

    st.markdown("#### 加班開始日期與時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_start_date = st.date_input("加班開始日期 *", value=date.today())
    with col2:
        overtime_start_hour = st.selectbox("加班開始時間（小時） *", HOUR_OPTIONS, index=17)
    with col3:
        overtime_start_minute = st.selectbox("加班開始時間（分鐘） *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 加班結束日期與時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_end_date = st.date_input("加班結束日期 *", value=date.today())
    with col2:
        overtime_end_hour = st.selectbox("加班結束時間（小時） *", HOUR_OPTIONS, index=19)
    with col3:
        overtime_end_minute = st.selectbox("加班結束時間（分鐘） *", MINUTE_OPTIONS, index=0)

    overtime_reason = st.text_area("加班原因 *")

    break_hours = st.radio(
        "加班休息時間（小時） *",
        BREAK_HOUR_OPTIONS,
        horizontal=True
    )

    if break_hours == "0":
        warning_box("如勾選未休息，請於下方填寫原因。")
        no_break_reason = st.text_area("未休息原因 *")
    else:
        no_break_reason = ""

    st.info("加班申請不需上傳附件。")


# ==============================
# 補登
# ==============================

else:
    st.subheader("工時補登申請單")

    warning_box("如有忘記刷卡、未帶卡，或是出勤異常，皆需完成補登。忘記帶卡需上傳借用登記表。")

    correction_reason = st.radio(
        "補登原因 *",
        CORRECTION_REASONS
    )

    if correction_reason == "忘記刷卡上班":
        st.markdown("#### 補登上班日期與時間")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("補登上班日期 *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("補登上班時間（小時） *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("補登上班時間（分鐘） *", MINUTE_OPTIONS, index=0)

        correction_end_date = correction_start_date
        correction_end_hour = correction_start_hour
        correction_end_minute = correction_start_minute

    elif correction_reason in ["忘記刷卡下班", "早於刷卡時間"]:
        st.markdown("#### 補登下班日期與時間")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("補登下班日期 *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("補登下班時間（小時） *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("補登下班時間（分鐘） *", MINUTE_OPTIONS, index=0)

        correction_start_date = correction_end_date
        correction_start_hour = correction_end_hour
        correction_start_minute = correction_end_minute

    elif correction_reason == "忘記帶卡":
        warning_box("忘記帶卡需上傳借用登記表。若無上傳完成，視同無補登。附件僅允許上傳 1 個檔案，若有多個檔案，請先合併為 1 個 PDF 或圖片檔。檔案大小上限為 10MB。")

        st.markdown("#### 補登上班日期與時間")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_start_date = st.date_input("補登上班日期 *", value=date.today())
        with col2:
            correction_start_hour = st.selectbox("補登上班時間（小時） *", HOUR_OPTIONS, index=8)
        with col3:
            correction_start_minute = st.selectbox("補登上班時間（分鐘） *", MINUTE_OPTIONS, index=0)

        st.markdown("#### 補登下班日期與時間")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            correction_end_date = st.date_input("補登下班日期 *", value=date.today())
        with col2:
            correction_end_hour = st.selectbox("補登下班時間（小時） *", HOUR_OPTIONS, index=17)
        with col3:
            correction_end_minute = st.selectbox("補登下班時間（分鐘） *", MINUTE_OPTIONS, index=0)

        uploaded_file = st.file_uploader(
            "補登附件上傳 *",
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
        errors.append("電子郵件")

    if not employee_id.strip():
        errors.append("工號")

    if " " in employee_id:
        errors.append("工號不可含空白")

    if not employee_name.strip():
        errors.append("姓名")

    if " " in employee_name:
        errors.append("姓名不可含空白")

    if request_type == "請假":
        if not leave_type:
            errors.append("選擇假別")

        if "彈性育嬰留停" in leave_type and not flex_parental_category:
            errors.append("彈性育嬰留停假別分類")

        if "喪假" in leave_type and not bereavement_category:
            errors.append("喪假假別分類")

        if is_special_date_required(leave_type) and special_date is None:
            errors.append("日期")

        if is_leave_attachment_required(leave_type) and uploaded_file is None:
            errors.append("請假附件上傳")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

        if not leave_reason.strip():
            errors.append("請假原因")

    elif request_type == "加班":
        if select_zero != "0":
            errors.append("請選 0")

        if pay_type != "PAY":
            errors.append("給付方式")

        if not overtime_type:
            errors.append("加班類型")

        if not overtime_reason.strip():
            errors.append("加班原因")

        if not break_hours:
            errors.append("加班休息時間")

        if break_hours == "0" and not no_break_reason.strip():
            errors.append("未休息原因")

    else:
        if not correction_reason:
            errors.append("補登原因")

        if correction_reason == "忘記帶卡" and uploaded_file is None:
            errors.append("補登附件上傳")

        if uploaded_file is not None:
            upload_error = validate_upload(uploaded_file)
            if upload_error:
                errors.append(upload_error)

    return errors


# ==============================
# 送出
# ==============================

st.divider()

if st.button("送出申請", use_container_width=True):

    errors = validate_required_fields()

    if errors:
        st.error("❌ 以下欄位需確認：\n\n- " + "\n- ".join(errors))
        st.stop()

    form_type_normalized = REQUEST_TYPE_PAYLOAD_MAP[request_type]["normalized"]
    form_type_raw = REQUEST_TYPE_PAYLOAD_MAP[request_type]["raw"]

    payload = build_base_payload(
        request_type_normalized=form_type_normalized,
        form_type_raw=form_type_raw,
        employee_name=employee_name,
        employee_id=employee_id,
        email=email
    )

    try:
        attachment_links = build_file_info(uploaded_file)

        if request_type == "請假":
            start_dt = combine_datetime(leave_start_date, leave_start_hour, leave_start_minute)
            end_dt = combine_datetime(leave_end_date, leave_end_hour, leave_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ 請假結束時間不可早於或等於開始時間。")
                st.stop()

            leave_type_payload = LEAVE_TYPE_PAYLOAD_MAP[leave_type]
            bereavement_payload = BEREAVEMENT_CATEGORY_PAYLOAD_MAP.get(bereavement_category, bereavement_category)

            payload["leave"].update({
                "leaveType": leave_type_payload,
                "flexParentalLeaveCategory": flex_parental_category,
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

        elif request_type == "加班":
            start_dt = combine_datetime(overtime_start_date, overtime_start_hour, overtime_start_minute)
            end_dt = combine_datetime(overtime_end_date, overtime_end_hour, overtime_end_minute)

            if not validate_start_end(start_dt, end_dt):
                st.error("❌ 加班結束時間不可早於或等於開始時間。")
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

            if correction_reason == "忘記帶卡" and not validate_start_end(start_dt, end_dt):
                st.error("❌ 補登結束時間不可早於或等於開始時間。")
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
            st.success("✅ 申請送出成功")
        else:
            st.error(f"❌ Flow 回傳錯誤：{response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 無法連線到 Power Automate：{str(e)}")

    except Exception as e:
        st.error(f"❌ 發生錯誤：{str(e)}")
