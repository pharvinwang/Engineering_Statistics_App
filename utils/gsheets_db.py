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
#
# v3.1 修正：選擇性快取失效 + 驗證碼即時生效
#
#   問題 1：原 v3 的 _invalidate_ws_cache 呼叫 .clear()，會清除所有 worksheet
#     的快取，導致 A 同學寫入 Week 03 時，B 同學正在讀取 Week 07 的快取也一起
#     失效，產生不必要的 API 呼叫。
#   修正方式：
#   - 為 _get_ws_data_cached 加入 cache_bust 參數（非底線前綴，納入 cache key）
#   - _invalidate_ws_cache(sheet_title) 只對指定分頁在本 session 遞增版本號
#   - 所有讀取呼叫改用 _get_ws_data(sheet_title) wrapper，自動帶入版本號
#   - 不同 session 之間的快取互不干擾，跨 session 的舊快取靠 ttl=30 自然過期
#
#   問題 2：_get_students_data 原本 ttl=3600（1 小時），在 Google Sheets 更新
#     同學驗證碼後，需等 1 小時或 Reboot 才能生效，會把在線同學踢出。
#   修正方式：ttl 改為 300（5 分鐘），更新驗證碼後最多等 5 分鐘自動生效。

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
    ★ 改用 @st.cache_resource（不嘗試 pickle 序列化）。
    gspread Spreadsheet 物件無法被 @st.cache_data 序列化，
    序列化失敗會讓函式靜默回傳 None，造成後續所有 worksheet() 呼叫失敗。
    @st.cache_resource 直接快取物件參照，適合 gspread / DB connection 等不可序列化物件。
    """
    return _get_shared_client().open_by_key(SPREADSHEET_ID)


# ══════════════════════════════════════════════════════════════════════
# 密碼讀取（雙層快取）
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


def get_weekly_password_safe(week_name: str):
    """
    雙層快取版本，解決 55 人同時載入頁面觸發 API 的問題：
    1. session_state：同一 session 內完全免 API
    2. cache_data：跨 session 共用，1小時內 server 只打一次 API
    在各週 .py 改用此函式取代 get_weekly_password()
    """
    ss_key = f"_pwd_{week_name}"
    if not st.session_state.get(ss_key):
        pwd = get_weekly_password(week_name)
        if pwd:
            st.session_state[ss_key] = pwd
    return st.session_state.get(ss_key)


# ══════════════════════════════════════════════════════════════════════
# 學生名單快取（ttl=300，5分鐘，55人共用）
# ══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)   # 5 分鐘：驗證碼更新後最多等 5 分鐘生效，不需 Reboot
def _get_students_data():
    """
    讀取 Students 表並快取 5 分鐘（ttl=300）。
    55人同時送出時只打 1 次 API。
    更新驗證碼後最多等 5 分鐘生效，不需 Reboot。
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
# ★ v3.1 選擇性快取失效核心設計
#
# 問題：@st.cache_data 只提供 .clear()（清除所有 entry），無法指定單一 key。
# 解法：在 cache key 中加入 cache_bust 整數，透過 session_state 版本號控制
#       哪個 session 看到哪個版本的快取。
#
# 運作方式：
#   - _get_ws_data_cached(sheet_title, cache_bust) — cache_bust 納入 cache key
#   - _get_ws_version(sheet_title) — 從 session_state 取得目前版本號（預設 0）
#   - _get_ws_data(sheet_title) — wrapper，自動帶入版本號
#   - _invalidate_ws_cache(sheet_title) — 只對指定分頁在本 session 遞增版本號
#
# 效果：
#   - Session A 寫入 Week 03 → A 的 _wsv_Week 03 = 1 → A 下次讀 Week 03 = cache miss
#   - Session B 讀 Week 07 → B 的 _wsv_Week 07 = 0 → ("Week 07", 0) 快取命中 ✓
#   - Session A 的失效操作對 Session B 的 Week 07 完全無影響 ✓
# ══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)
def _get_ws_data_cached(sheet_title: str, cache_bust: int = 0):   # ★ cache_bust 納入 key
    """
    快取單張 worksheet 的所有資料（ttl=30秒）。
    cache_bust 用於選擇性失效，不影響函式邏輯。

    回傳：(all_rows, id_to_rownum)
      - all_rows: [[col0, col1, ...], ...]，含 header
      - id_to_rownum: {student_id: row_number(1-indexed)}
    """
    try:
        ws = _get_spreadsheet().worksheet(sheet_title)
        all_rows = ws.get_all_values()
        id_to_rownum = {}
        for i, row in enumerate(all_rows[1:], start=2):
            if len(row) >= 2 and row[1].strip():
                id_to_rownum[row[1].strip()] = i
        return all_rows, id_to_rownum
    except gspread.exceptions.WorksheetNotFound:
        return None, {}
    except Exception:
        return None, {}


def _get_ws_version(sheet_title: str) -> int:
    """取得本 session 中指定分頁的快取版本號（預設 0）。"""
    return st.session_state.get(f"_wsv_{sheet_title}", 0)


def _get_ws_data(sheet_title: str):
    """
    ★ v3.1 公開 wrapper：自動帶入版本號，確保讀到的是失效後的新資料。
    所有內部函式應呼叫此 wrapper，而非直接呼叫 _get_ws_data_cached。
    """
    return _get_ws_data_cached(sheet_title, _get_ws_version(sheet_title))


def _invalidate_ws_cache(sheet_title: str):
    """
    ★ v3.1 選擇性失效：只對指定分頁在本 session 遞增版本號。
    其他分頁、其他 session 的快取完全不受影響。
    """
    key = f"_wsv_{sheet_title}"
    st.session_state[key] = st.session_state.get(key, 0) + 1


# ══════════════════════════════════════════════════════════════════════
# 自動建表
# ══════════════════════════════════════════════════════════════════════
def ensure_quiz_sheet_exists(sheet_title: str):
    """
    確保 worksheet 存在。若不存在則建立並從 Students 複製名單。
    使用快取判斷是否存在，避免不必要的 API 呼叫。
    """
    spreadsheet = _get_spreadsheet()
    cached_rows, _ = _get_ws_data(sheet_title)   # ★ 使用 wrapper
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
    all_rows, id_to_rownum = _get_ws_data(week)   # ★ 使用 wrapper
    if not id_to_rownum:
        return False
    student_id_str = str(student_id).strip()
    if student_id_str not in id_to_rownum:
        return False
    if all_rows is None:
        return False
    # 從快取資料取得該列
    row_idx = id_to_rownum[student_id_str] - 1   # 轉為 0-indexed
    if row_idx < len(all_rows):
        row = all_rows[row_idx]
        return len(row) >= 6 and str(row[5]).strip() != ""
    return False


# ══════════════════════════════════════════════════════════════════════
# 【核心優化】save_score v3.1
# 最大改善：不再每次都讀 col_values，改用快取的 id_to_rownum
# ══════════════════════════════════════════════════════════════════════
def save_score(student_idx, student_id, name, week, answer, score):
    """
    【無敵寫入 v3.1】55 人並發優化版。

    v2 的瓶頸：
      每次 save_score = open_by_key + col_values(讀整欄) + update
      55人同時 = 165 次 API → 超過 quota → 429 → 系統崩潰

    v3 的改善：
      - spreadsheet 物件從 cache_resource 取得（不重複 open_by_key）
      - row 位置從 _get_ws_data_cached 取得（不重複讀 col_values）
      - 55人同時送出：只有第一人讀表，其餘從快取取得 row 位置
      - 理論 API 次數：1次讀 + 55次寫 = 56次（vs 舊版 165次）

    v3.1 改善：
      - 改用 _get_ws_data() wrapper 取得 row 位置（選擇性快取失效）
      - _invalidate_ws_cache(week) 只失效本張表，不影響其他分頁快取
    """
    MAX_RETRIES = 6
    tw_tz = pytz.timezone('Asia/Taipei')

    # ── 【雪崩防護 v2】已移除前置 sleep，改由 retry backoff 處理，不凍結畫面 ──
    for attempt in range(MAX_RETRIES):
        try:
            # ── 確保 worksheet 存在 ──────────────────────────────────
            sheet = ensure_quiz_sheet_exists(week)
            current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            student_id_str = str(student_id).strip()

            # ── 【關鍵】從快取取得 row 位置，不讀整欄 ───────────────
            _, id_to_rownum = _get_ws_data(week)   # ★ 使用 wrapper

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
            _invalidate_ws_cache(week)   # ★ 選擇性失效，只影響 week 這張表
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
    不額外打 API（使用 _get_ws_data wrapper）。
    回傳 {"pct": int, "detail": str} 或 None。
    """
    student_id_str = str(student_id).strip()
    all_rows, id_to_rownum = _get_ws_data(week)   # ★ 使用 wrapper
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
def _get_sheet_titles():
    """
    取得工作表清單。
    ★ 不使用 @st.cache_data：失敗時的空列表 [] 會被快取 5 分鐘，
      導致期間內所有查詢都拿到空結果。
    改用 session_state 手動快取，只有成功結果才寫入。
    """
    import time as _t
    _KEY    = "_sheet_titles_v2"
    _TS_KEY = "_sheet_titles_v2_ts"
    _TTL    = 60   # 成功結果快取 60 秒

    cached  = st.session_state.get(_KEY)
    last_ts = st.session_state.get(_TS_KEY, 0)

    if cached and (_t.monotonic() - last_ts) < _TTL:
        return cached

    try:
        titles = [ws.title for ws in _get_spreadsheet().worksheets()]
        if titles:
            st.session_state[_KEY]    = titles
            st.session_state[_TS_KEY] = _t.monotonic()
        return titles
    except Exception:
        return cached if cached else []


def get_all_scores(student_id):
    """
    查詢該同學所有週次成績。
    完全使用快取，55人同時查詢只需 API 1 次。
    回傳 (results, error_msg)：
      - results: list，成功時為成績列表（可能為空）
      - error_msg: str or None，有錯誤時說明原因
    """
    student_id_str = str(student_id).strip()
    results = []

    titles = _get_sheet_titles()
    if not titles:
        return [], "無法取得工作表清單，請稍後再試（Google Sheets API 連線異常）"

    for title in titles:
        if title in ("Students", "測驗密碼", "總成績彙整", "互動成績彙整"):
            continue
        try:
            all_rows, id_to_rownum = _get_ws_data(title)   # ★ 使用 wrapper
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
    return results, None


# ══════════════════════════════════════════════════════════════════════
# 注意：can_submit / mark_submitted / seconds_until_retry
# 已於 v2.1 廢棄，冷卻邏輯統一由 utils/week_submit.py 的
# render_ia_section() 內部處理，請勿在週課頁面直接呼叫。
# ══════════════════════════════════════════════════════════════════════