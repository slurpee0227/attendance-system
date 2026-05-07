import streamlit as st
import requests
import base64
from datetime import datetime, date, time, timezone

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
# 隱藏側邊欄
# ==============================

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
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
# 共用函式
# ==============================

def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")


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

st.title("📝 出勤申請系統")
st.caption(f"目前登入：{employee_name} / {employee_id}")
back_to_menu_button()
st.divider()

with st.expander("登入人員資料", expanded=True):
    st.text_input("工號 Employee ID", value=employee_id, disabled=True)
    st.text_input("姓名 Name", value=employee_name, disabled=True)
    st.text_input("Email", value=email, disabled=True)
    st.text_input("部門 Department", value=department, disabled=True)
    st.text_input("Level", value=level, disabled=True)
    st.text_input("Region", value=region, disabled=True)

request_type = st.selectbox(
    "申請類型 / Request Type *",
    ["請假 Leave", "加班 Overtime", "補登 Correction"]
)

leave_type = ""
leave_reason = ""

overtime_type = ""
pay_type = "PAY"
break_hours = "0"
no_break_reason = ""
overtime_reason = ""

correction_reason = ""

# ==============================
# 請假
# ==============================

if request_type == "請假 Leave":

    st.subheader("請假資訊")

    leave_type = st.selectbox(
        "假別 *",
        ["事假", "病假", "特休", "補休", "其他"]
    )

    leave_start_date = st.date_input("開始日期 *", value=date.today())
    leave_start_time = st.time_input("開始時間 *", value=time(8, 0))
    leave_end_date = st.date_input("結束日期 *", value=date.today())
    leave_end_time = st.time_input("結束時間 *", value=time(17, 0))

    leave_reason = st.text_area("請假原因 *")

# ==============================
# 加班
# ==============================

elif request_type == "加班 Overtime":

    st.subheader("加班資訊")

    overtime_type = st.selectbox(
        "加班類型 *",
        [
            "10平日加班 Work overtime on weekdays",
            "20休息日加班 Work overtime on rest day",
            "30國定假日加班 Work overtime on national holiday"
        ]
    )

    pay_type = st.selectbox(
        "給付方式 *",
        ["PAY", "COMP"]
    )

    overtime_start_date = st.date_input("加班開始日期 *", value=date.today())
    overtime_start_time = st.time_input("加班開始時間 *", value=time(17, 0))
    overtime_end_date = st.date_input("加班結束日期 *", value=date.today())
    overtime_end_time = st.time_input("加班結束時間 *", value=time(19, 0))

    break_hours = st.selectbox(
        "休息時數 *",
        ["0", "0.5", "1", "1.5", "2"]
    )

    no_break_reason = st.text_area("未休息原因")
    overtime_reason = st.text_area("加班原因 *")

# ==============================
# 補登
# ==============================

elif request_type == "補登 Correction":

    st.subheader("補登資訊")

    correction_reason = st.selectbox(
        "補登原因 *",
        [
            "忘記刷上班",
            "忘記刷下班",
            "忘記帶卡(Forgot to Bring Access Card)",
            "其他"
        ]
    )

    correction_start_date = st.date_input("補登開始日期 *", value=date.today())
    correction_start_time = st.time_input("補登開始時間 *", value=time(8, 0))
    correction_end_date = st.date_input("補登結束日期 *", value=date.today())
    correction_end_time = st.time_input("補登結束時間 *", value=time(17, 0))

# ==============================
# 附件
# ==============================

st.subheader("附件")

uploaded_file = st.file_uploader(
    "上傳附件",
    type=["png", "jpg", "jpeg", "pdf"]
)


# ==============================
# 必填檢查
# ==============================

def validate_required_fields():
    errors = []

    if request_type == "請假 Leave":
        if not leave_reason.strip():
            errors.append("請假原因")

    elif request_type == "加班 Overtime":
        if not overtime_reason.strip():
            errors.append("加班原因")

    elif request_type == "補登 Correction":
        if not correction_reason.strip():
            errors.append("補登原因")

    return errors


# ==============================
# Payload
# ==============================

def build_base_payload():
    timestamp = make_timestamp()

    form_type_map = {
        "請假 Leave": "leave",
        "加班 Overtime": "overtime",
        "補登 Correction": "correction"
    }

    form_type_raw_map = {
        "請假 Leave": "請假(Leave)",
        "加班 Overtime": "加班(Overtime)",
        "補登 Correction": "補登(Correction)"
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
# 送出
# ==============================

if st.button("送出申請", use_container_width=True):

    errors = validate_required_fields()

    if errors:
        st.error("❌ 以下欄位需確認：\n\n- " + "\n- ".join(errors))
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

        if request_type == "請假 Leave":

            start_dt = datetime.combine(leave_start_date, leave_start_time)
            end_dt = datetime.combine(leave_end_date, leave_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ 結束時間不可早於或等於開始時間")
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

        elif request_type == "加班 Overtime":

            start_dt = datetime.combine(overtime_start_date, overtime_start_time)
            end_dt = datetime.combine(overtime_end_date, overtime_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ 結束時間不可早於或等於開始時間")
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

        elif request_type == "補登 Correction":

            start_dt = datetime.combine(correction_start_date, correction_start_time)
            end_dt = datetime.combine(correction_end_date, correction_end_time)

            if not validate_datetime(start_dt, end_dt):
                st.error("❌ 結束時間不可早於或等於開始時間")
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
            st.success("✅ 申請送出成功")
        else:
            st.error(f"❌ Flow 回傳錯誤：{response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 無法連線到 Power Automate：{str(e)}")

    except Exception as e:
        st.error(f"❌ 發生錯誤：{str(e)}")