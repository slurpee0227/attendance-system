import streamlit as st
import requests
import pandas as pd

QUERY_FLOW_URL = st.secrets["QUERY_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(page_title="申請紀錄查詢", page_icon="🔎", layout="centered")

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
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 850px; }
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
.stTextInput input, .stTextArea textarea, .stSelectbox div, .stDateInput input, .stTimeInput input {
    background-color: white !important;
    color: #111827 !important;
    border-radius: 10px;
    border: 1px solid #d1d5db !important;
}
.stTextInput input::placeholder { color: #6b7280 !important; }
.stRadio label, div[role="radiogroup"] label { color: #111827 !important; }
.stSuccess { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

user_info = st.session_state.get("user_info")

if not user_info:
    st.warning("登入已失效，請重新登入")
    if st.button("返回登入頁", use_container_width=True):
        st.session_state.clear()
        st.switch_page("登入頁.py")
    st.stop()

def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")

query_type_from_menu = st.session_state.get("query_type", "請假")

query_type_map = {
    "請假": "leave",
    "加班": "overtime",
    "補登": "correction"
}

st.title("🔎 申請紀錄查詢")
st.caption(f"目前登入：{employee_name} / {employee_id}")
st.caption(f"部門：{department}")
back_to_menu_button()
st.divider()

st.subheader("查詢條件")
default_index = ["請假", "加班", "補登"].index(query_type_from_menu)

query_type = st.radio(
    "申請類型",
    ["請假", "加班", "補登"],
    index=default_index,
    horizontal=True
)

st.session_state.query_type = query_type
query_type_normalized = query_type_map[query_type]

if st.button("查詢紀錄", use_container_width=True):
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
                st.error(result.get("message", "查詢失敗"))
                st.stop()

            records = result.get("records", [])

            if not records:
                st.info("目前查無申請紀錄")
            else:
                df = pd.DataFrame(records)
                status_map = {
                    "已歸檔": "待上傳HR系統",
                    "已上傳": "待上傳HR系統",
                    "已處理": "已上傳HR系統"
                }
                if "狀態" in df.columns:
                    df["狀態"] = df["狀態"].replace(status_map)
                st.dataframe(df.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.error(f"❌ 查詢 Flow 回傳錯誤：{response.status_code}")
            st.text(response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 無法連線到查詢 Flow：{str(e)}")
    except Exception as e:
        st.error(f"❌ 查詢失敗：{str(e)}")

st.divider()

if st.button("登出", use_container_width=True):
    st.session_state.clear()
    st.switch_page("登入頁.py")
