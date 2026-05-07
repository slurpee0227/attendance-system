import streamlit as st
import requests
import pandas as pd

# ==============================
# 基本設定
# ==============================
QUERY_FLOW_URL = st.secrets["QUERY_FLOW_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(
    page_title="申請紀錄查詢",
    page_icon="🔎",
    layout="centered"
)

# ==============================
# 隱藏側邊欄
# ==============================

st.markdown(
    """
    <style>

    /* =========================
       強制亮色系
    ========================= */

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

    /* =========================
       隱藏側邊欄
    ========================= */

    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* =========================
       隱藏 Streamlit Cloud UI
    ========================= */

    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }

    .stDeployButton,
    .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    footer {
        display: none !important;
        visibility: hidden !important;
    }

    header {
        display: none !important;
        visibility: hidden !important;
    }

    /* 嘗試隱藏右下角 Hosted with Streamlit */

    iframe {
        display: none !important;
        visibility: hidden !important;
    }

    body > div:last-child {
        display: none !important;
        visibility: hidden !important;
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


def back_to_menu_button():
    if st.button("返回主選單", use_container_width=True):
        st.switch_page("登入頁.py")


# ==============================
# 登入人員資料
# ==============================

employee_id = user_info.get("employeeId", "")
employee_name = user_info.get("name", "")
email = user_info.get("email", "")
department = user_info.get("department", "")

# ==============================
# 查詢類型
# ==============================

query_type_from_menu = st.session_state.get("query_type", "請假")

query_type_map = {
    "請假": "leave",
    "加班": "overtime",
    "補登": "correction"
}

reverse_query_type_map = {
    "leave": "請假",
    "overtime": "加班",
    "correction": "補登"
}

# ==============================
# 頁面
# ==============================

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
        response = requests.post(
            QUERY_FLOW_URL,
            json=payload,
            timeout=30
        )

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

                # =========================
                # 狀態文字轉換
                # =========================

                status_map = {
                    "已歸檔": "待上傳HR系統",
                    "已上傳": "待上傳HR系統",
                    "已處理": "已上傳HR系統"
                }

                if "狀態" in df.columns:
                    df["狀態"] = df["狀態"].replace(status_map)

                # =========================
                # 顯示表格
                # =========================

                st.dataframe(
                    df.reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )

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