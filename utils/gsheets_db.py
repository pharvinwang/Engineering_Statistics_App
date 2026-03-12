# 檔案位置： D:\Engineering_Statistics_App\utils\gsheets_db.py
# v2 修正：解決 50 人同時送出時的 API Rate Limit (429) 錯誤
#
# 修正重點：
#   1. init_connection() 改為 session 快取，不再每次重新 authorize
#   2. save_score() 採用 Exponential Backoff + 隨機抖動，避免同時重試互相衝突
#   3. 加入 _RATE_LIMIT_CODES 精準判斷是否為 quota 錯誤
#   4. 減少多餘的 API 呼叫（connect once, write once）
#   5. 提供更清楚的錯誤訊息，讓學生知道要「稍候幾秒再試」

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import time
import random
import os

# ── 判斷是否為速率限制錯誤 ─────────────────────────────────────────────────────
_RATE_LIMIT_CODES = {429, 500, 503}  # 429 = Too Many Requests, 5xx = 伺服器暫時過載

def _is_rate_limit(exc: Exception) -> bool:
    """判斷是否為 API 速率限制或暫時性錯誤"""
    msg = str(exc).lower()
    if hasattr(exc, 'response') and exc.response is not None:
        try:
            if exc.response.status_code in _RATE_LIMIT_CODES:
                return True
        except Exception:
            pass
    return any(k in msg for k in ('429', 'quota', 'rate limit', 'too many requests',
                                   'resource exhausted', '500', '503'))


# ── 連線快取（同一個 Streamlit session 只 authorize 一次）──────────────────────
def _get_client():
    """
    取得 gspread client。
    同一 session 內快取，避免每次寫入都重新 OAuth（耗費 quota 且慢）。
    """
    if "_gsheets_client" not in st.session_state:
        st.session_state["_gsheets_client"] = _create_client()
    return st.session_state["_gsheets_client"]


def _create_client():
    """建立新的 gspread client（只在 session 開始時呼叫一次）"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    if os.path.exists('google_key.json'):
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_key.json', scope)
    elif "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        raise FileNotFoundError(
            "找不到 Google 金鑰檔案！請確認 google_key.json 存在或已設定 Secrets。"
        )
    return gspread.authorize(creds)


# ── 保留原本的 init_connection（向下相容）──────────────────────────────────────
def init_connection():
    """初始化 Google Sheets 連線（向下相容舊介面）"""
    return _get_client()


SPREADSHEET_ID = "1HPUEl3cAzfxwTvkcVU1PU9bBxqvWdX4NWjRbuZ9Qlcg"

# sidebar.py 也需要這兩個，加上 alias
_gc = None          # 在第一次呼叫後由 _get_client() 取代
_SPREADSHEET_ID = SPREADSHEET_ID


# ── 密碼讀取（保留原本的 cache）──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_weekly_password(week_name):
    """從 Google 試算表的「測驗密碼」分頁中抓取該週的解鎖密碼"""
    try:
        client = _create_client()           # 此處不用 session cache，因為 cache_data 跨 session
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("測驗密碼")
        records = sheet.get_all_records()
        for row in records:
            if str(row.get("週次", "")).strip() == week_name:
                return str(row.get("密碼", "")).strip()
        return None
    except Exception as e:
        print(f"讀取密碼發生錯誤: {e}")
        return None


# ── 學生驗證 ──────────────────────────────────────────────────────────────────
def verify_student(student_id, name, v_code):
    """【防偷窺機制】驗證身分，若成功則順便回傳該生的「編號」"""
    try:
        client = _get_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Students")
        data = sheet.get_all_values()
        for row in data[1:]:
            if len(row) >= 4:
                if (str(row[1]).strip() == str(student_id).strip() and
                        str(row[2]).strip() == str(name).strip() and
                        str(row[3]).strip() == str(v_code).strip()):
                    return True, str(row[0]).strip()
        return False, None
    except Exception as e:
        st.error(f"資料庫連線異常：{e}")
        return False, None


# ── 自動建表 ───────────────────────────────────────────────────────────────────
def ensure_quiz_sheet_exists(client, spreadsheet, week_name):
    """【自動生成】建立新表單並複製：編號、學號、姓名"""
    try:
        return spreadsheet.worksheet(week_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=week_name, rows=100, cols=10)
        students_data = spreadsheet.worksheet("Students").get_all_values()
        bulk_data = [["編號", "學號", "姓名", "測驗時間", "答案紀錄", "測驗分數"]]
        for row in students_data[1:]:
            if len(row) >= 3 and str(row[1]).strip() != "":
                bulk_data.append([
                    str(row[0]).strip(), str(row[1]).strip(),
                    str(row[2]).strip(), "", "", ""
                ])
        sheet.update(values=bulk_data, range_name="A1")
        return sheet


# ── 檢查是否已作答 ────────────────────────────────────────────────────────────
def check_has_submitted(student_id, week):
    """檢查是否已經作答過"""
    try:
        client = _get_client()
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        try:
            sheet = spreadsheet.worksheet(week)
        except gspread.exceptions.WorksheetNotFound:
            return False
        ids = sheet.col_values(2)
        student_id_str = str(student_id).strip()
        if student_id_str in ids:
            row_idx = ids.index(student_id_str) + 1
            row_data = sheet.row_values(row_idx)
            if len(row_data) >= 6 and str(row_data[5]).strip() != "":
                return True
        return False
    except Exception:
        return False


# ── 核心寫入：Exponential Backoff + Jitter ────────────────────────────────────
def save_score(student_idx, student_id, name, week, answer, score):
    """
    【無敵寫入 v2】按學號對號入座，若為加選生則自動新增列。

    Rate Limit 防護：
    - 最多重試 6 次
    - 等待時間：2^attempt 秒（1, 2, 4, 8, 16, 32）
    - 加上 0~1 秒的隨機抖動（jitter），避免 50 人同時在相同時刻重試互相衝突
    - 精準識別 429 / quota 錯誤才重試，其他錯誤直接回報
    """
    MAX_RETRIES = 6
    tw_tz = pytz.timezone('Asia/Taipei')

    for attempt in range(MAX_RETRIES):
        try:
            client = _get_client()
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            sheet = ensure_quiz_sheet_exists(client, spreadsheet, week)

            current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            student_id_str = str(student_id).strip()

            ids = sheet.col_values(2)
            if student_id_str in ids:
                row_idx = ids.index(student_id_str) + 1
                sheet.update(
                    values=[[current_time, answer, score]],
                    range_name=f"D{row_idx}:F{row_idx}"
                )
            else:
                sheet.append_row([student_idx, student_id_str, name,
                                   current_time, answer, score])
            return True  # ✅ 成功

        except gspread.exceptions.APIError as api_err:
            if _is_rate_limit(api_err) and attempt < MAX_RETRIES - 1:
                wait = (2 ** attempt) + random.uniform(0, 1)   # 1~2, 2~3, 4~5, 8~9, 16~17 秒
                time.sleep(wait)
                # 連線可能已失效，清掉 session cache 讓下次重新 authorize
                st.session_state.pop("_gsheets_client", None)
                continue
            else:
                # 最後一次仍失敗，或非 rate limit 錯誤
                st.error(
                    f"⚠️ 伺服器暫時忙碌（嘗試 {attempt+1} 次後仍失敗）。"
                    f"請等待約 **10～20 秒**後再按一次「送出」！"
                )
                return False

        except Exception as e:
            # 非 API 錯誤（網路斷線、試算表不存在等），直接回報
            st.error(f"寫入失敗，錯誤代碼：{e}")
            return False

    return False