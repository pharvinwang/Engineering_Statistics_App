# 檔案位置： D:\Engineering_Statistics_App\utils\gsheets_db.py
# v3 重大優化：解決 55 人同時使用時的系統崩潰問題
#
# 根本原因分析：
#   1. save_score() 每次都 open_by_key() → 同一個 spreadsheet 物件重複取得
#   2. col_values(2) 讀整欄找 row → 55人並發 = 55次讀取同一欄
#   3. _create_client() 在 @cache_data 中每次都重新 OAuth，跨 session 無法共用
#   4. 55人同時送出 ≈ 110次 API/分鐘，超過 Google 60次/分鐘限制
#
# v3 修正重點：
#   A. spreadsheet 物件也加入 session 快取（減少 open_by_key 次數）
#   B. save_score 改用「先讀整張表快取，再從快取找 row」不重複讀 col_values
#   C. 寫入後主動讓快取失效，確保下次讀到新資料
#   D. _create_client() 改為 @st.cache_resource（跨 session 共用同一個 OAuth 連線）
#   E. 所有 worksheet 物件也快取在 session，避免重複 .worksheet() 呼叫

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import time
import random
import os

# ══════════════════════════════════════════════════════════════════════
# 速率限制判斷
# ══════════════════════════════════════════════════════════════════════
_RATE_LIMIT_CODES = {429, 500, 503}

def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    if hasattr(exc, 'response') and exc.response is not None:
        try:
            if exc.response.status_code in _RATE_LIMIT_CODES:
                return True
        except Exception:
            pass
    return any(k in msg for k in ('429', 'quota', 'rate limit', 'too many requests',
                                   'resource exhausted', '500', '503'))


# ══════════════════════════════════════════════════════════════════════
# 【關鍵優化 A】OAuth client 改用 @st.cache_resource
# cache_data 會序列化/反序列化，不適合 client 物件
# cache_resource 跨所有 session 共用同一個連線物件，55人只需 authorize 一次
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def _get_shared_client():
    """
    全伺服器共用的 gspread client（@cache_resource）。
    55個 session 共用 → 只需 OAuth 一次，大幅減少 API 消耗。
    """
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


def _create_client():
    """向下相容：等同於 _get_shared_client()"""
    return _get_shared_client()


def _get_client():
    """
    取得 gspread client。
    優先用共用 client（cache_resource），session cache 作為備援。
    """
    try:
        return _get_shared_client()
    except Exception:
        # 備援：session 層快取
        if "_gsheets_client" not in st.session_state:
            st.session_state["_gsheets_client"] = _create_client()
        return st.session_state["_gsheets_client"]


# ══════════════════════════════════════════════════════════════════════
# 向下相容
# ══════════════════════════════════════════════════════════════════════
def init_connection():
    return _get_client()


SPREADSHEET_ID = "1HPUEl3cAzfxwTvkcVU1PU9bBxqvWdX4NWjRbuZ9Qlcg"
_gc = None
_SPREADSHEET_ID = SPREADSHEET_ID


# ══════════════════════════════════════════════════════════════════════
# 【關鍵優化 B】Spreadsheet 物件快取
# open_by_key() 本身就是一次 API 呼叫，應避免重複呼叫
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def _get_spreadsheet():
    """
    全伺服器共用的 spreadsheet 物件。
    避免每次 save_score 都呼叫 open_by_key()。
    """
    return _get_shared_client().open_by_key(SPREADSHEET_ID)


# ══════════════════════════════════════════════════════════════════════
# 密碼讀取（維持 cache_data）
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def get_weekly_password(week_name):
    """從 Google 試算表的「測驗密碼」分頁中抓取該週的解鎖密碼"""
    try:
        sheet = _get_spreadsheet().worksheet("測驗密碼")
        records = sheet.get_all_records()
        for row in records:
            if str(row.get("週次", "")).strip() == week_name:
                return str(row.get("密碼", "")).strip()
        return None
    except Exception as e:
        print(f"讀取密碼發生錯誤: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════
# 學生名單快取（ttl=3600，55人共用）
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def _get_students_data():
    """
    讀取 Students 表並快取 1 小時。
    55人同時送出時只打 1 次 API。
    """
    try:
        return _get_spreadsheet().worksheet("Students").get_all_values()
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════
# 學生驗證
# ══════════════════════════════════════════════════════════════════════
def verify_student(student_id, name, v_code):
    """驗證身分，回傳 (True, idx) 或 (False, None)"""
    MAX_RETRIES = 4
    for attempt in range(MAX_RETRIES):
        try:
            data = _get_students_data()
            if not data:
                data = _get_spreadsheet().worksheet("Students").get_all_values()
            for row in data[1:]:
                if len(row) >= 4:
                    if (str(row[1]).strip() == str(student_id).strip() and
                            str(row[2]).strip() == str(name).strip() and
                            str(row[3]).strip() == str(v_code).strip()):
                        return True, str(row[0]).strip()
            return False, None
        except gspread.exceptions.APIError as api_err:
            if _is_rate_limit(api_err) and attempt < MAX_RETRIES - 1:
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue
            else:
                st.error("⚠️ 伺服器暫時忙碌，驗證失敗。請等待 **10～20 秒**後再按一次送出！")
                return False, None
        except Exception as e:
            st.error(f"資料庫連線異常：{e}")
            return False, None
    return False, None


# ══════════════════════════════════════════════════════════════════════
# 【關鍵優化 C】worksheet 資料快取（每張表）
# 這是最重要的優化：55人同時送出時，col_values 只需讀 1 次
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def _get_ws_data_cached(sheet_title: str):
    """
    快取單張 worksheet 的所有資料（ttl=30秒）。

    為什麼 ttl=30 而不是更長？
    - 太長（如 120 秒）：同學 A 送出後，同學 B 在 30 秒內查詢
      可能看到舊快取而找不到自己的 row，導致 append_row 重複寫入
    - 30 秒是合理的折衷：55 人送出通常在幾秒內完成，
      30 秒後快取自動更新，不會累積錯誤

    回傳：(headers, all_rows, id_to_rownum)
      - all_rows: [[col0, col1, ...], ...]，含 header
      - id_to_rownum: {student_id: row_number(1-indexed)}
    """
    try:
        ws = _get_spreadsheet().worksheet(sheet_title)
        all_rows = ws.get_all_values()
        id_to_rownum = {}
        for i, row in enumerate(all_rows[1:], start=2):   # row 1 = header
            if len(row) >= 2 and row[1].strip():
                id_to_rownum[row[1].strip()] = i
        return all_rows, id_to_rownum
    except gspread.exceptions.WorksheetNotFound:
        return None, {}
    except Exception:
        return None, {}


def _invalidate_ws_cache(sheet_title: str):
    """寫入完成後讓該表的快取失效，下次讀取會拿到最新資料"""
    try:
        _get_ws_data_cached.clear()   # clear all cached data for this function
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════
# 自動建表
# ══════════════════════════════════════════════════════════════════════
def ensure_quiz_sheet_exists(sheet_title: str):
    """
    確保 worksheet 存在。若不存在則建立並從 Students 複製名單。
    使用快取判斷是否存在，避免不必要的 API 呼叫。
    """
    spreadsheet = _get_spreadsheet()
    # 先用快取確認，若快取回傳 None 才真的去建立
    cached_rows, _ = _get_ws_data_cached(sheet_title)
    if cached_rows is not None:
        return spreadsheet.worksheet(sheet_title)

    try:
        return spreadsheet.worksheet(sheet_title)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=sheet_title, rows=100, cols=10)
        students_data = spreadsheet.worksheet("Students").get_all_values()
        bulk_data = [["編號", "學號", "姓名", "測驗時間", "答案紀錄", "測驗分數"]]
        for row in students_data[1:]:
            if len(row) >= 3 and str(row[1]).strip() != "":
                bulk_data.append([
                    str(row[0]).strip(), str(row[1]).strip(),
                    str(row[2]).strip(), "", "", ""
                ])
        sheet.update(values=bulk_data, range_name="A1")
        _invalidate_ws_cache(sheet_title)
        return sheet


# ══════════════════════════════════════════════════════════════════════
# 檢查是否已作答
# ══════════════════════════════════════════════════════════════════════
def check_has_submitted(student_id, week):
    """使用快取資料檢查是否已送出，不額外打 API"""
    _, id_to_rownum = _get_ws_data_cached(week)
    if not id_to_rownum:
        return False
    student_id_str = str(student_id).strip()
    if student_id_str not in id_to_rownum:
        return False
    # 從快取資料取得該列
    all_rows, _ = _get_ws_data_cached(week)
    if all_rows is None:
        return False
    row_idx = id_to_rownum[student_id_str] - 1   # 轉為 0-indexed
    if row_idx < len(all_rows):
        row = all_rows[row_idx]
        return len(row) >= 6 and str(row[5]).strip() != ""
    return False


# ══════════════════════════════════════════════════════════════════════
# 【核心優化】save_score v3
# 最大改善：不再每次都讀 col_values，改用快取的 id_to_rownum
# ══════════════════════════════════════════════════════════════════════
def save_score(student_idx, student_id, name, week, answer, score):
    """
    【無敵寫入 v3】55 人並發優化版。

    v2 的瓶頸：
      每次 save_score = open_by_key + col_values(讀整欄) + update
      55人同時 = 165 次 API → 超過 quota → 429 → 系統崩潰

    v3 的改善：
      - spreadsheet 物件從 cache_resource 取得（不重複 open_by_key）
      - row 位置從 _get_ws_data_cached 取得（不重複讀 col_values）
      - 55人同時送出：只有第一人讀表，其餘從快取取得 row 位置
      - 理論 API 次數：1次讀 + 55次寫 = 56次（vs 舊版 165次）
    """
    MAX_RETRIES = 6
    tw_tz = pytz.timezone('Asia/Taipei')

    # ── 【雪崩防護】送出前隨機延遲 0~3 秒 ──────────────────────────
    # 55人同時按送出時，讓每人在不同時間點到達 API，避免同時撞牆
    time.sleep(random.uniform(0, 3))

    for attempt in range(MAX_RETRIES):
        try:
            # ── 確保 worksheet 存在 ──────────────────────────────────
            sheet = ensure_quiz_sheet_exists(week)

            current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            student_id_str = str(student_id).strip()

            # ── 【關鍵】從快取取得 row 位置，不讀整欄 ───────────────
            _, id_to_rownum = _get_ws_data_cached(week)
            
            if student_id_str in id_to_rownum:
                # 已有此學生 → 更新現有列
                row_idx = id_to_rownum[student_id_str]
                sheet.update(
                    values=[[current_time, str(answer), score]],
                    range_name=f"D{row_idx}:F{row_idx}"
                )
            else:
                # 加選生或快取未命中 → 新增列
                sheet.append_row([student_idx, student_id_str, name,
                                   current_time, str(answer), score])

            # ── 寫入成功，讓快取失效（下次讀取會是最新資料）─────────
            _invalidate_ws_cache(week)
            return True

        except gspread.exceptions.APIError as api_err:
            if _is_rate_limit(api_err) and attempt < MAX_RETRIES - 1:
                # Full Jitter：完全隨機分散在 [0, 2^attempt * 3] 秒之間
                # 55人同時重試時，每人等待時間完全不同，有效避免雪崩
                cap = min(2 ** attempt * 3, 30)   # 上限 30 秒
                wait = random.uniform(0, cap)
                time.sleep(wait)
                _invalidate_ws_cache(week)
                continue
            else:
                st.error(
                    f"⚠️ 伺服器暫時忙碌（第 {attempt+1} 次嘗試失敗）。\n"
                    f"請等待約 **15～30 秒**後再按一次「送出」！\n"
                    f"您的互動進度**完全保留**，不需要重做。"
                )
                return False

        except Exception as e:
            st.error(f"寫入失敗，錯誤代碼：{e}")
            return False

    return False


# ══════════════════════════════════════════════════════════════════════
# 讀取已儲存的互動進度（防止 session 重連後送出低分蓋高分）
# ══════════════════════════════════════════════════════════════════════
def get_saved_progress(student_id, week):
    """
    從快取讀取該同學已儲存的互動進度。
    不額外打 API（使用 _get_ws_data_cached）。
    回傳 {"pct": int, "detail": str} 或 None。
    """
    student_id_str = str(student_id).strip()
    all_rows, id_to_rownum = _get_ws_data_cached(week)
    if all_rows is None or student_id_str not in id_to_rownum:
        return None
    row_idx = id_to_rownum[student_id_str] - 1   # 0-indexed
    if row_idx >= len(all_rows):
        return None
    row_data = all_rows[row_idx]
    if len(row_data) >= 6 and str(row_data[5]).strip() != "":
        try:
            pct = int(str(row_data[5]).strip())
        except ValueError:
            pct = 0
        return {"pct": pct, "detail": str(row_data[4]).strip()}
    return None


# ══════════════════════════════════════════════════════════════════════
# 成績查詢（快取版，55人同時查詢只打 1 次 API）
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def _get_sheet_titles():
    """快取工作表清單（5 分鐘更新一次）"""
    try:
        return [ws.title for ws in _get_spreadsheet().worksheets()]
    except Exception:
        return []


def get_all_scores(student_id):
    """
    查詢該同學所有週次成績。
    完全使用快取，55人同時查詢只需 API 1 次。
    """
    student_id_str = str(student_id).strip()
    results = []

    titles = _get_sheet_titles()
    for title in titles:
        if title in ("Students", "測驗密碼", "總成績彙整", "互動成績彙整"):
            continue
        try:
            all_rows, id_to_rownum = _get_ws_data_cached(title)
            if all_rows is None or student_id_str not in id_to_rownum:
                continue
            row_idx = id_to_rownum[student_id_str] - 1
            if row_idx >= len(all_rows):
                continue
            row = all_rows[row_idx]
            if len(row) >= 6 and str(row[5]).strip() != "":
                is_ia = "互動" in title
                try:
                    score_val = int(str(row[5]).strip())
                except ValueError:
                    score_val = 0
                results.append({
                    "week":   title,
                    "type":   "互動參與" if is_ia else "小考",
                    "time":   str(row[3]).strip(),
                    "record": str(row[4]).strip(),
                    "score":  score_val,
                })
        except Exception:
            continue

    results.sort(key=lambda x: x["week"])
    return results


# ══════════════════════════════════════════════════════════════════════
# 【送出冷卻防護】防止同學連續重複按送出加劇 429 問題
# 在各週頁面的送出按鈕前呼叫 can_submit()，成功後呼叫 mark_submitted()
# ══════════════════════════════════════════════════════════════════════
def can_submit(key: str, cooldown_sec: int = 15) -> bool:
    """
    判斷是否可以送出（冷卻時間內不允許重複按）。
    key: 唯一識別字串，例如 "w2_ia" 或 "w2_quiz"
    cooldown_sec: 冷卻秒數，預設 15 秒

    用法：
        if can_submit("w2_ia"):
            # 執行送出邏輯
            ...
        else:
            st.warning("⏳ 請稍候 15 秒再重新送出，系統正在處理中...")
    """
    ts_key = f"__submit_ts_{key}"
    last_ts = st.session_state.get(ts_key, 0)
    return (time.monotonic() - last_ts) >= cooldown_sec


def mark_submitted(key: str):
    """送出後記錄時間戳，啟動冷卻計時"""
    st.session_state[f"__submit_ts_{key}"] = time.monotonic()


def seconds_until_retry(key: str, cooldown_sec: int = 15) -> int:
    """回傳還需等幾秒才能重試（0 = 可以送出）"""
    ts_key = f"__submit_ts_{key}"
    last_ts = st.session_state.get(ts_key, 0)
    elapsed = time.monotonic() - last_ts
    remaining = cooldown_sec - elapsed
    return max(0, int(remaining))