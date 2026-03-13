# utils/sidebar.py
# =====================================================================
# 統一側邊欄模組
# - 連線狀態：檢查 GSheets API 是否正常（60 秒快取）
# - 線上人數：直接讀 Streamlit 自己的 session 數，零 API 消耗
# - 週次導覽、登入資訊、系統時間
#
# 使用方式（在任意頁面最頂部加入）：
#   from utils.sidebar import render_sidebar
#   render_sidebar(current_page="Week 02")
# =====================================================================

import streamlit as st
import time
from datetime import datetime, timezone, timedelta

# ── Taiwan timezone ───────────────────────────────────────────────────
TZ_TW = timezone(timedelta(hours=8))

# ── 連線狀態快取 TTL（秒）────────────────────────────────────────────
_CONN_TTL = 60    # 每 60 秒重新檢查一次 GSheets 連線


# ─────────────────────────────────────────────────────────────────────
# 內部工具函數
# ─────────────────────────────────────────────────────────────────────

def _cache_get(key: str, ttl: int):
    c = st.session_state.get(f"__sb_{key}")
    if c and (time.monotonic() - c["t"]) < ttl:
        return c["v"]
    return None

def _cache_set(key: str, val):
    st.session_state[f"__sb_{key}"] = {"v": val, "t": time.monotonic()}

def _cache_clear(*keys):
    for k in keys:
        st.session_state.pop(f"__sb_{k}", None)


def get_online_count() -> int:
    """
    直接讀取 Streamlit Runtime 的 active session 數。
    每個開著網頁的分頁 = 1 個 session。
    分頁關閉後 Streamlit 自動移除，完全不需要心跳或 GSheets。
    """
    try:
        from streamlit.runtime import get_instance
        runtime = get_instance()
        return runtime._session_mgr.num_active_sessions()
    except Exception:
        return 0


def _check_connection() -> tuple:
    """回傳 (is_ok: bool, message: str)，結果快取 60 秒"""
    cached = _cache_get("conn", _CONN_TTL)
    if cached is not None:
        return cached

    try:
        import utils.gsheets_db as _db
        # ★ v3：改用 _get_shared_client()（cache_resource），不再依賴 _gc alias
        sid = getattr(_db, "_SPREADSHEET_ID", None) or getattr(_db, "SPREADSHEET_ID", None)
        if sid is None:
            result = (False, "找不到 SPREADSHEET_ID")
        else:
            try:
                client = _db._get_shared_client()
                sh = client.open_by_key(sid)
                _ = sh.title
                result = (True, "雲端連線正常")
            except Exception:
                # 本地開發時 secrets 可能不存在，嘗試 _get_spreadsheet() 快取版本
                try:
                    sh = _db._get_spreadsheet()
                    _ = sh.title
                    result = (True, "雲端連線正常")
                except Exception as e2:
                    result = (False, f"連線異常：{str(e2)[:30]}")
    except Exception as e:
        result = (False, f"連線異常：{str(e)[:25]}")

    _cache_set("conn", result)
    return result


# ─────────────────────────────────────────────────────────────────────
# 週次清單（新增週次時只需在這裡加）
# ─────────────────────────────────────────────────────────────────────
WEEK_MENU = [
    ("Week 01", "📐 第 1 章：統計基礎"),
    ("Week 02", "📊 第 2 章：資料描述"),
    ("Week 03", "🎲 第 3 章：機率"),
    ("Week 04", "🔢 第 4 章：隨機變數"),
    ("Week 05", "📈 第 5 章：機率分配"),
    ("Week 06", "📉 第 6 章：常態分配"),
    ("Week 07", "🧪 第 7 章：抽樣分配"),
    ("Week 08", "🔬 第 8 章：區間估計"),
    ("Week 09", "✅ 第 9 章：假設檢定（一）"),
    ("Week 10", "✅ 第10章：假設檢定（二）"),
    ("Week 11", "📏 第11章：迴歸分析"),
    ("Week 12", "📐 第12章：相關分析"),
    ("Week 13", "🏭 第13章：變異數分析"),
    ("Week 14", "📋 第14章：無母數統計"),
    ("Week 15", "🏆 第15章：品質管制"),
]


# ─────────────────────────────────────────────────────────────────────
# 主函數
# ─────────────────────────────────────────────────────────────────────

def render_sidebar(current_page: str = ""):
    """
    渲染統一側邊欄。

    Parameters
    ----------
    current_page : str
        目前週次，例如 "Week 02"。用於週次導覽高亮顯示。

    在每個頁面頂部呼叫：
        from utils.sidebar import render_sidebar
        render_sidebar(current_page="Week 02")
    """
    # ── 讀取資料 ────────────────────────────────────────────────────
    conn_ok, conn_msg = _check_connection()
    total        = get_online_count()
    student_id   = st.session_state.get("student_id", "")
    student_name = st.session_state.get("student_name", "")
    is_logged    = st.session_state.get("password_correct", False)
    now_tw       = datetime.now(TZ_TW).strftime("%m/%d %H:%M")

    # ════════════════════════════════════════════════════════════════
    with st.sidebar:

        st.divider()

        # ② 連線狀態
        if conn_ok:
            st.markdown(f'''
            <div style="background:#dcfce7;border:1px solid #86efac;
                        border-radius:10px;padding:8px 12px;margin:0 0 6px 0;
                        text-align:center;">
                <div style="color:#166534;font-weight:700;font-size:0.82rem;">
                    ☁️ {conn_msg}
                </div>
                <div style="color:#15803d;font-size:0.72rem;margin-top:2px;">
                    Google Sheets API 正常
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div style="background:#fee2e2;border:1px solid #fca5a5;
                        border-radius:10px;padding:8px 12px;margin:0 0 6px 0;
                        text-align:center;">
                <div style="color:#991b1b;font-weight:700;font-size:0.82rem;">
                    ⚠️ {conn_msg}
                </div>
                <div style="color:#b91c1c;font-size:0.72rem;margin-top:2px;">
                    成績暫時無法儲存
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # ③ 線上人數
        st.markdown(f'''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;
                    border-radius:10px;padding:9px 12px;margin:0 0 6px 0;
                    text-align:center;">
            <div style="color:#1e40af;font-weight:700;font-size:0.82rem;margin-bottom:4px;">
                🟢 目前在線人數
            </div>
            <div>
                <span style="color:#1e40af;font-size:1.4rem;font-weight:800;
                             line-height:1.2;">{total if total > 0 else "—"}</span>
                <span style="color:#1e40af;font-size:0.80rem;font-weight:600;">
                    {" 人" if total > 0 else ""}
                </span>
            </div>
            <div style="color:#3b82f6;font-size:0.72rem;margin-top:2px;opacity:0.85;">
                （開啟網頁的分頁數）
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # ④ 重新整理按鈕
        st.markdown('''
        <style>
        div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            height: 34px !important;
            padding: 0 8px !important;
        }
        </style>
        ''', unsafe_allow_html=True)
        if st.button("🔄 重新整理狀態", key="_sb_refresh", use_container_width=True):
            _cache_clear("conn")
            st.rerun()

        st.divider()

        # ⑤ 目前週次
        if current_page:
            # Find label for current page
            cur_label = next((lbl for key, lbl in WEEK_MENU if key == current_page), current_page)
            st.markdown(f'''
            <div style="background:#1e3a5f;border-radius:10px;
                        padding:10px 14px;margin:0 0 6px 0;text-align:center;">
                <div style="color:#93c5fd;font-size:0.72rem;font-weight:700;
                            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;">
                    目前頁面
                </div>
                <div style="color:#ffffff;font-size:0.9rem;font-weight:700;line-height:1.4;">
                    {cur_label}
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.divider()

        # ⑥ 系統時間
        st.markdown(f'''
        <div style="text-align:center;color:#94a3b8;font-size:0.76rem;padding:2px 0 4px 0;">
            🕐 {now_tw}（台灣時間）
        </div>
        ''', unsafe_allow_html=True)