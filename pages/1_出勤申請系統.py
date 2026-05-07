import streamlit as st
import requests
import base64
from datetime import datetime, date, timezone


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
# 自訂樣式
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
# 登入檢查
# ==============================

user_info = st.session_state.get("user_info")

if not user_info:
    st.warning("登入已失效，請重新登入")

    if st.button("返回登入頁", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")

    st.stop()


# ==============================
# 常數設定
# ==============================

HOUR_OPTIONS = [f"{i:02d}" for i in range(24)]
MINUTE_OPTIONS = ["00", "30"]

LEAVE_TYPES = [
    "特休(Annual Leave)",
    "事假(Personal Leave)",
    "病假(Sick Leave)",
    "家庭照顧假(Family Care Leave)",
    "喪假(Bereavement Leave)",
    "補休(Compensatory Leave)",
    "婚假(Marriage Leave)",
    "產假(Maternity Leave)",
    "陪產假(Paternity Leave)",
    "產檢假(Prenatal Checkup Leave)",
    "陪產檢假(Paternity Prenatal Checkup Leave)",
    "公假(Official Leave)",
    "生理假(Menstrual Leave)",
    "彈性育嬰留停(Flexible Parental Leave)",
    "其他(Other)"
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

BEREAVEMENT_CATEGORIES = [
    "父母",
    "配偶",
    "子女",
    "祖父母",
    "兄弟姊妹",
    "其他"
]

PARENTAL_LEAVE_CATEGORIES = [
    "每日減少工時",
    "每週彈性請假",
    "其他"
]

OVERTIME_TYPES = [
    "10平日加班 Work overtime on weekdays",
    "20休息日加班 Work overtime on rest day",
    "25休息日加班 Foreign employees select 20",
    "30國定假日加班 Work overtime on national holiday"
]

BREAK_HOUR_OPTIONS = ["0", "0.5", "1", "1.5", "2"]

CORRECTION_REASONS = [
    "忘記刷卡上班(Forgot to Clock In)",
    "忘記刷卡下班(Forgot to Clock Out)",
    "忘記帶卡(Forgot to Bring Access Card)",
    "早於刷卡時間(Earlier than the card swipe time)",
    "其他(Other)"
]


# ==============================
# 共用函式
# ==============================

def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")


def is_leave_attachment_required(leave_type: str) -> bool:
    return any(keyword in leave_type for keyword in LEAVE_ATTACHMENT_REQUIRED_KEYWORDS)


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
        "請假 Leave": "leave",
        "加班 Overtime": "overtime",
        "補登 Correction": "correction"
    }

    form_type_raw_map = {
        "請假 Leave": "請假(Leave)",
        "加班 Overtime": "加班(Overtime)",
        "補登 Correction": "補登(Timesheet Correction)"
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
# 登入人員資料
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")
level = user_info.get("level", "")
region = user_info.get("region", "")


# ==============================
# 頁面標題
# ==============================

st.title("📝 出勤申請系統")
st.caption(f"目前登入：{employee_name} / {employee_id}")
back_to_menu_button()
st.divider()


# ==============================
# 申請人資訊
# ==============================

with st.expander("申請人資料", expanded=True):
    st.text_input("工號 Employee ID", value=employee_id, disabled=True)
    st.text_input("姓名 Name", value=employee_name, disabled=True)
    st.text_input("Email", value=email, disabled=True)
    st.text_input("部門 Department", value=department, disabled=True)
    st.text_input("Level", value=level, disabled=True)
    st.text_input("Region", value=region, disabled=True)


# ==============================
# 申請類型
# ==============================

st.subheader("申請需求項目")

request_type = st.radio(
    "請選擇申請需求項目 *",
    ["請假 Leave", "加班 Overtime", "補登 Correction"],
    horizontal=True
)

st.divider()


# ==============================
# 預設變數
# ==============================

uploaded_file = None

leave_type = ""
bereavement_category = ""
parental_leave_category = ""
leave_reason = ""
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
# 請假表單
# ==============================

if request_type == "請假 Leave":

    st.subheader("請假資訊")

    leave_type = st.selectbox(
        "選擇假別 Leave Type *",
        LEAVE_TYPES
    )

    if "喪假" in leave_type:
        bereavement_category = st.selectbox(
            "選擇喪假假別分類 *",
            BEREAVEMENT_CATEGORIES
        )

    if "彈性育嬰留停" in leave_type:
        parental_leave_category = st.selectbox(
            "選擇彈性育嬰留停假別分類 *",
            PARENTAL_LEAVE_CATEGORIES
        )

    st.markdown("#### 請假開始時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_start_date = st.date_input("請假開始日期 *", value=date.today())
    with col2:
        leave_start_hour = st.selectbox("開始小時 *", HOUR_OPTIONS, index=8)
    with col3:
        leave_start_minute = st.selectbox("開始分鐘 *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 請假結束時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        leave_end_date = st.date_input("請假結束日期 *", value=date.today())
    with col2:
        leave_end_hour = st.selectbox("結束小時 *", HOUR_OPTIONS, index=17)
    with col3:
        leave_end_minute = st.selectbox("結束分鐘 *", MINUTE_OPTIONS, index=0)

    leave_reason = st.text_area("請假原因 *")

    if is_leave_attachment_required(leave_type):
        st.warning("此假別需附上證明，才能申請。")
        uploaded_file = st.file_uploader(
            "請假附件上傳 Upload Supporting Document *",
            type=["png", "jpg", "jpeg", "pdf"]
        )
    else:
        uploaded_file = st.file_uploader(
            "請假附件上傳 Upload Supporting Document",
            type=["png", "jpg", "jpeg", "pdf"]
        )


# ==============================
# 加班表單
# ==============================

elif request_type == "加班 Overtime":

    st.subheader("加班資訊")

    pay_type = st.selectbox(
        "給付方式 *",
        ["PAY", "COMP"]
    )

    overtime_type = st.selectbox(
        "加班類型 Overtime Type *",
        OVERTIME_TYPES
    )

    st.markdown("#### 加班開始時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_start_date = st.date_input("加班開始日期 *", value=date.today())
    with col2:
        overtime_start_hour = st.selectbox("加班開始小時 *", HOUR_OPTIONS, index=17)
    with col3:
        overtime_start_minute = st.selectbox("加班開始分鐘 *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 加班結束時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        overtime_end_date = st.date_input("加班結束日期 *", value=date.today())
    with col2:
        overtime_end_hour = st.selectbox("加班結束小時 *", HOUR_OPTIONS, index=19)
    with col3:
        overtime_end_minute = st.selectbox("加班結束分鐘 *", MINUTE_OPTIONS, index=0)

    overtime_reason = st.text_area("加班原因 *")

    break_hours = st.selectbox(
        "加班休息時間(Break Time)_小時/Hours *",
        BREAK_HOUR_OPTIONS
    )

    if break_hours == "0":
        st.warning("休息時間為 0 時，需填寫未休息原因。")
        no_break_reason = st.text_area("未休息原因 No Break Reason *")
    else:
        no_break_reason = st.text_area("未休息原因 No Break Reason")

    st.info("加班申請不需要上傳附件。")


# ==============================
# 補登表單
# ==============================

elif request_type == "補登 Correction":

    st.subheader("補登資訊")

    correction_reason = st.selectbox(
        "補登原因 Timesheet Correction Reason *",
        CORRECTION_REASONS
    )

    st.markdown("#### 補登開始時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        correction_start_date = st.date_input("補登開始日期 Start Date *", value=date.today())
    with col2:
        correction_start_hour = st.selectbox("補登開始小時 *", HOUR_OPTIONS, index=8)
    with col3:
        correction_start_minute = st.selectbox("補登開始分鐘 *", MINUTE_OPTIONS, index=0)

    st.markdown("#### 補登結束時間")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        correction_end_date = st.date_input("補登結束日期 End Date *", value=date.today())
    with col2:
        correction_end_hour = st.selectbox("補登結束小時 *", HOUR_OPTIONS, index=17)
    with col3:
        correction_end_minute = st.selectbox("補登結束分鐘 *", MINUTE_OPTIONS, index=0)

    if correction_reason == "忘記帶卡(Forgot to Bring Access Card)":
        st.warning("忘記帶卡需上傳附件。")
        uploaded_file = st.file_uploader(
            "補登附件上傳 Upload File *",
            type=["png", "jpg", "jpeg", "pdf"]
        )
    else:
        uploaded_file = st.file_uploader(
            "補登附件上傳 Upload File",
            type=["png", "jpg", "jpeg", "pdf"]
        )


# ==============================
# 必填檢查
# ==============================

def validate_required_fields():
    errors = []

    if not employee_id.strip():
        errors.append("工號 Employee ID")

    if not employee_name.strip():
        errors.append("姓名 Name")

    if not email.strip():
        errors.append("Email")

    if request_type == "請假 Leave":

        if not leave_type:
            errors.append("假別 Leave Type")

        if "喪假" in leave_type and not bereavement_category:
            errors.append("喪假假別分類")

        if "彈性育嬰留停" in leave_type and not parental_leave_category:
            errors.append("彈性育嬰留停假別分類")

        if not leave_reason.strip():
            errors.append("請假原因 Leave Reason")

        if is_leave_attachment_required(leave_type) and uploaded_file is None:
            errors.append("此假別需上傳證明附件 Upload Supporting Document")

    elif request_type == "加班 Overtime":

        if not pay_type:
            errors.append("給付方式 Pay Type")

        if not overtime_type:
            errors.append("加班類型 Overtime Type")

        if not overtime_reason.strip():
            errors.append("加班原因 Overtime Reason")

        if not break_hours:
            errors.append("加班休息時間 Break Time")

        if break_hours == "0" and not no_break_reason.strip():
            errors.append("未休息原因 No Break Reason")

    elif request_type == "補登 Correction":

        if not correction_reason:
            errors.append("補登原因 Timesheet Correction Reason")

        if correction_reason == "忘記帶卡(Forgot to Bring Access Card)" and uploaded_file is None:
            errors.append("忘記帶卡需上傳補登附件 Upload File")

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

    try:
        payload = build_base_payload(
            request_type=request_type,
            employee_name=employee_name,
            employee_id=employee_id,
            email=email
        )

        attachment_links = build_file_info(uploaded_file)

        if request_type == "請假 Leave":

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
                st.error("❌ 結束時間不可早於或等於開始時間")
                st.stop()

            payload["leave"].update({
                "leaveType": leave_type,
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

        elif request_type == "加班 Overtime":

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
                st.error("❌ 結束時間不可早於或等於開始時間")
                st.stop()

            payload["overtime"].update({
                "selectZero": "0",
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

        elif request_type == "補登 Correction":

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
                st.error("❌ 結束時間不可早於或等於開始時間")
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