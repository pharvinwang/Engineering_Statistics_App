# 檔案位置： D:\Engineering_Statistics_App\pages\00_成績查詢.py
from utils.auth import require_login
require_login()

import streamlit as st

try:
    from utils.sidebar import render_sidebar
    _sidebar_ok = True
except Exception:
    _sidebar_ok = False

try:
    from utils.style import apply_theme
    apply_theme()
except Exception:
    pass

try:
    from utils.gsheets_db import verify_student, get_all_scores, mark_submitted, seconds_until_retry
except ImportError:
    def verify_student(*a, **k): return False, None
    def get_all_scores(*a, **k): return []
    def mark_submitted(*a, **k): pass
    def seconds_until_retry(*a, **k): return 0

if _sidebar_ok:
    render_sidebar(current_page="成績查詢")

# ── 登入防護 ──────────────────────────────────────────────────────────
if "password_correct" not in st.session_state or not st.session_state.password_correct:
    st.markdown(
        '<div style="max-width:380px;margin:60px auto 0 auto;' +
        'background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);' +
        'border-radius:14px;padding:28px 32px;text-align:center;' +
        'box-shadow:0 6px 24px rgba(0,0,0,0.18);">' +
        '<div style="font-size:2.2rem;margin-bottom:10px;">🔐</div>' +
        '<h2 style="color:#f1f5f9;font-size:1.2rem;font-weight:800;margin:0 0 8px 0;">尚未登入</h2>' +
        '<p style="color:#94a3b8;font-size:0.9rem;line-height:1.6;margin:0 0 16px 0;">' +
        '此頁面需要登入才能存取。<br>請先回到首頁輸入課程密碼。</p>' +
        '<div style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);' +
        'border-radius:8px;padding:9px 14px;color:#93c5fd;font-size:0.88rem;">' +
        '👈 請點選左側導覽列的 <strong>Home</strong> 進行登入</div></div>',
        unsafe_allow_html=True)
    st.stop()

_CSS = """
<style>
/* 查詢按鈕 */
.st-key-gq_btn button, .stkey_gq_btn button {
    background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    height: 52px !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 3px 12px rgba(29,78,216,0.30) !important;
    letter-spacing: 0.04em !important;
}
.st-key-gq_btn button:hover, .stkey_gq_btn button:hover {
    background: linear-gradient(90deg, #1e40af 0%, #1d4ed8 100%) !important;
    box-shadow: 0 5px 18px rgba(29,78,216,0.40) !important;
    transform: translateY(-1px) !important;
}
</style>
"""

try:
    st.html(_CSS)
except AttributeError:
    st.markdown(_CSS, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);' +
    'border-radius:16px;padding:28px 40px 24px 40px;' +
    'margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">' +
    '<div style="color:#f1f5f9;font-size:2.0rem;font-weight:900;margin:0;">' +
    '📋 個人成績查詢</div></div>',
    unsafe_allow_html=True)

# ── 查詢表單 ─────────────────────────────────────────────────────────
st.markdown(
    '<style>'
    '.st-key-gq_container > div:first-child {'
    '  border-radius:0 0 12px 12px !important;'
    '  border-top:none !important;'
    '  margin-top:-1px !important;'
    '}'
    '</style>'
    '<div style="'
    'background:linear-gradient(90deg,#0f766e 0%,#0d9488 100%);'
    'border-radius:12px 12px 0 0;'
    'padding:12px 20px 10px 20px;">'
    '<span style="color:white;font-weight:700;font-size:1.0rem;">'
    '🔍 請輸入您的資料</span>'
    '<div style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin-top:5px;">'
    '請輸入學號、姓名與驗證碼後送出，系統將顯示您所有週次的互動參與與小考成績。'
    '</div></div>',
    unsafe_allow_html=True)

with st.container(border=True, key="gq_container"):
    col_id, col_name, col_code = st.columns(3)
    with col_id:
        q_id   = st.text_input("📝 學號",   key="gq_id",   placeholder="請輸入學號")
    with col_name:
        q_name = st.text_input("📝 姓名",   key="gq_name", placeholder="請輸入姓名")
    with col_code:
        q_code = st.text_input("🔑 驗證碼", key="gq_code", placeholder="個人驗證碼",
                                type="password")






_gq_wait = seconds_until_retry("gq_search", cooldown_sec=10)
if _gq_wait > 0:
    st.info(f"⏳ 請等待 **{_gq_wait} 秒**後再查詢")

if st.button("🔍 查詢我的成績", key="gq_btn", use_container_width=True,
             disabled=(_gq_wait > 0)):
    mark_submitted("gq_search")
    if not (q_id and q_name and q_code):
        st.markdown(
            '<div style="border-radius:10px;border:1px solid #fde68a;margin:8px 0;">' +
            '<div style="background:#d97706;border-radius:10px 10px 0 0;padding:9px 16px;">' +
            '<span style="color:white;font-weight:700;">⚠️ 資料不完整</span></div>' +
            '<div style="background:#fffbeb;border-radius:0 0 10px 10px;' +
            'padding:12px 16px;color:#92400e;">' +
            '請完整填寫學號、姓名與驗證碼再查詢。</div></div>',
            unsafe_allow_html=True)
    else:
        with st.spinner("🔄 驗證身分中，請稍候…"):
            is_valid, student_idx = verify_student(q_id, q_name, q_code)
        if not is_valid:
            st.markdown(
                '<div style="border-radius:10px;border:1px solid #fecaca;margin:8px 0;">' +
                '<div style="background:#ef4444;border-radius:10px 10px 0 0;padding:9px 16px;">' +
                '<span style="color:white;font-weight:700;">⛔ 身分驗證失敗</span></div>' +
                '<div style="background:#fef2f2;border-radius:0 0 10px 10px;' +
                'padding:12px 16px;color:#991b1b;">' +
                '學號、姓名或驗證碼有誤，請重新確認後再試。</div></div>',
                unsafe_allow_html=True)
        else:
            with st.spinner("📊 讀取成績中，請稍候…"):
                records = get_all_scores(q_id)
                st.session_state["_gq_records"] = records
                st.session_state["_gq_name"]    = q_name
                st.session_state["_gq_id"]      = q_id

            st.markdown(
                '<div style="border-radius:10px;border:1px solid #bbf7d0;margin:12px 0 6px 0;">' +
                '<div style="background:#15803d;border-radius:10px 10px 0 0;padding:9px 16px;">' +
                '<span style="color:white;font-weight:700;">✅ 驗證成功</span></div>' +
                '<div style="background:#f0fdf4;border-radius:0 0 10px 10px;' +
                'padding:10px 16px;color:#166534;font-size:0.95rem;">' +
                "已找到 <b>" + q_name + "</b>（" + q_id +
                "）的成績記錄，共 <b>" + str(len(records)) + "</b> 筆。" +
                '</div></div>', unsafe_allow_html=True)

            if not records:
                st.markdown(
                    '<div style="border-radius:10px;border:1px solid #e2e8f0;margin:8px 0;">' +
                    '<div style="background:#475569;border-radius:10px 10px 0 0;padding:9px 16px;">' +
                    '<span style="color:white;font-weight:700;">📭 尚無成績記錄</span></div>' +
                    '<div style="background:#f8fafc;border-radius:0 0 10px 10px;' +
                    'padding:12px 16px;color:#334155;">' +
                    '目前系統中找不到您的送出記錄。<br>' +
                    '請確認是否已在各週課程頁面送出互動記錄與測驗。</div></div>',
                    unsafe_allow_html=True)
            else:
                import re as _re

                def _to_week(title):
                    m = _re.match(r'(Week \d+)', title.strip())
                    return m.group(1) if m else None

                try:
                    from utils.gsheets_db import _get_sheet_titles
                    _all_titles = _get_sheet_titles()
                except Exception:
                    _all_titles = [r["week"] for r in records]

                _week_set = set()
                for _t in _all_titles:
                    _wk = _to_week(_t)
                    if _wk: _week_set.add(_wk)
                all_weeks = sorted(_week_set)

                ia_map, quiz_map = {}, {}
                for r in records:
                    wk = _to_week(r["week"])
                    if wk not in _week_set: continue
                    if r["type"] == "互動參與": ia_map[wk] = r
                    elif r["type"] == "小考":   quiz_map[wk] = r

                table = (
                    '<table style="width:100%;border-collapse:collapse;margin:12px 0;' +
                    'font-size:0.95rem;border:2px solid #c8d8e8;' +
                    'box-shadow:0 2px 10px rgba(30,58,95,0.10);background:#e8f0f7;">' +
                    '<thead><tr>' +
                    '<th style="background:#1e3a5f;color:white;padding:11px 18px;' +
                    'text-align:left;font-weight:700;width:110px;">週次</th>' +
                    '<th style="background:#1e3a5f;color:white;padding:11px 18px;' +
                    'text-align:center;font-weight:700;">互動參與</th>' +
                    '<th style="background:#1e3a5f;color:white;padding:11px 18px;' +
                    'text-align:center;font-weight:700;width:160px;">小考成績</th>' +
                    '</tr></thead><tbody>'
                )
                rows = ""
                for i, week in enumerate(all_weeks):
                    bg = "#e8f0f7" if i % 2 == 0 else "#f0f5fa"
                    if week in ia_map:
                        r   = ia_map[week]
                        pct = r["score"]
                        rec = r.get("record", "")
                        dn, tn = 0, 0
                        m2 = _re.search(r'\((\d+)/(\d+)\)', rec.split("|")[0])
                        if m2: dn, tn = int(m2.group(1)), int(m2.group(2))
                        bc  = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"
                        cnt = f'{dn}/{tn}' if tn else "—"
                        ia  = (
                            f'<div style="display:flex;flex-direction:column;align-items:center;gap:5px;">' +
                            f'<div style="display:flex;align-items:center;gap:10px;width:100%;">' +
                            f'<div style="flex:1;background:#dde6f0;border-radius:999px;height:11px;">' +
                            f'<div style="width:{pct}%;background:{bc};height:100%;border-radius:999px;"></div></div>' +
                            f'<span style="font-weight:800;color:{bc};min-width:42px;text-align:right;">{pct}%</span></div>' +
                            f'<span style="font-size:0.82rem;color:#64748b;">已完成 {cnt} 項互動</span></div>'
                        )
                    else:
                        ia = '<span style="color:#b0bec5;font-size:0.88rem;">尚未送出</span>'
                    if week in quiz_map:
                        r      = quiz_map[week]
                        sc     = r["score"]
                        sc_col = "#22c55e" if sc >= 75 else "#f59e0b" if sc >= 50 else "#ef4444"
                        lbl    = "🌟" if sc == 100 else "👍" if sc >= 75 else "📖"
                        qz     = (
                            f'<span style="font-size:1.5rem;font-weight:900;color:{sc_col};">{sc}</span>' +
                            f'<span style="color:#94a3b8;font-size:0.85rem;"> / 100 {lbl}</span>'
                        )
                    else:
                        qz = '<span style="color:#b0bec5;font-size:0.88rem;">尚未作答</span>'
                    rows += (
                        f'<tr style="background:{bg};">' +
                        f'<td style="padding:13px 18px;font-weight:700;color:#1e3a5f;border-bottom:1px solid #d4e0ec;">{week}</td>' +
                        f'<td style="padding:13px 18px;border-bottom:1px solid #d4e0ec;text-align:center;">{ia}</td>' +
                        f'<td style="padding:13px 18px;border-bottom:1px solid #d4e0ec;text-align:center;">{qz}</td>' +
                        f'</tr>'
                    )
                st.markdown(table + rows + '</tbody></table>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)