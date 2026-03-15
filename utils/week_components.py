# 檔案位置： D:\Engineering_Statistics_App\utils\week_components.py
import streamlit as st

_WEEK_CSS = """
<style>
/* 只隱藏 checkmark icon，其餘全部交給 config.toml 處理 */
[data-baseweb="input"] > div > svg,
[data-baseweb="input"] [role="presentation"] { display: none !important; }
</style>
"""

def apply_week_css():
    st.markdown(_WEEK_CSS, unsafe_allow_html=True)


def card(color, bg, tc, title, msg):
    st.markdown(
        '<div style="border-radius:12px;overflow:hidden;'
        'box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">'
        '<div style="background:' + color + ';padding:10px 18px;">'
        '<span style="color:white;font-weight:700;font-size:1.0rem;">' + title + '</span></div>'
        '<div style="background:' + bg + ';padding:14px 18px;color:' + tc + ';'
        'font-size:1.05rem;line-height:1.7;">' + msg + '</div></div>',
        unsafe_allow_html=True)


def section_header(label):
    st.markdown(
        '<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);'
        'border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">'
        '<span style="color:#ffffff;font-size:1.3rem;font-weight:800;">' + label + '</span></div>',
        unsafe_allow_html=True)


def render_completion_rate(done, total):
    pct = int(done / total * 100) if total else 0
    card("#0369a1", "#e0f2fe", "#0c4a6e", "📊 本週互動完成率",
         f"已完成 <b>{done}/{total}</b> 項互動（{pct}%）")


def render_progress_card(track_prefix, groups, labels):
    """橫向 N 欄並排，每節一欄，標題去 TabN 前綴。"""
    ncols = len(groups)
    cols = st.columns(ncols)
    for ci, (gname, gkeys) in enumerate(groups.items()):
        clean = " ".join(gname.split(" ")[1:]) if gname.split(" ")[0].startswith("Tab") else gname
        done_g = sum(1 for k in gkeys if st.session_state.get(track_prefix + k, False))
        items = "".join(
            '<div style="font-size:0.83rem;padding:3px 0;">'
            + ('<span style="color:#166534;">✅ ' if st.session_state.get(track_prefix+k, False)
               else '<span style="color:#94a3b8;">⬜ ')
            + labels.get(k, k) + '</span></div>'
            for k in gkeys)
        with cols[ci]:
            st.markdown(
                '<div style="border-radius:10px;overflow:hidden;border:1px solid #e2e8f0;'
                'height:100%;box-shadow:0 2px 8px rgba(0,0,0,0.06);">'
                '<div style="background:#1e3a5f;padding:8px 12px;">'
                '<span style="color:white;font-size:0.85rem;font-weight:700;">' + clean + '</span>'
                ' <span style="color:#93c5fd;font-size:0.78rem;">'
                + str(done_g)+'/'+str(len(gkeys)) + '</span>'
                '</div>'
                '<div style="background:#f8fafc;padding:10px 12px;">'
                + items +
                '</div></div>',
                unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)


def render_progress_summary(done, total):
    """送出前進度摘要，實色背景。"""
    pct = int(done/total*100) if total else 0
    if pct >= 80:   bg, bd, tc, ic = "#dcfce7", "#86efac", "#166534", "✅"
    elif pct >= 50: bg, bd, tc, ic = "#fef9c3", "#fde047", "#854d0e", "⚠️"
    else:           bg, bd, tc, ic = "#fee2e2", "#fca5a5", "#991b1b", "❌"
    st.markdown(
        f'<div style="background:{bg};border:1px solid {bd};border-radius:8px;'
        f'padding:10px 16px;margin:6px 0 10px 0;">'
        f'<span style="font-weight:700;color:{tc};">{ic} 目前進度：{pct}%（{done}/{total} 項）</span>'
        f'<span style="font-size:0.82rem;color:#64748b;margin-left:10px;">'
        f'若進度與預期不符，請先返回完成各項互動再送出</span></div>',
        unsafe_allow_html=True)


def render_teal_header(title, subtitle):
    """青綠漸層 header，下方直接接裸 columns。"""
    st.markdown(
        '<div style="background:linear-gradient(90deg,#0f766e 0%,#0d9488 100%);'
        'border-radius:12px;padding:12px 20px 14px 20px;margin-bottom:10px;">'
        '<span style="color:white;font-weight:700;font-size:1.0rem;">' + title + '</span>'
        '<div style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin-top:5px;">'
        + subtitle + '</div></div>',
        unsafe_allow_html=True)


def render_student_inputs(prefix, id_ph="請輸入學號", name_ph="請輸入姓名", code_ph="個人驗證碼"):
    """
    公版學生身分輸入欄位（裸 columns，無任何 container）。
    prefix 決定所有 key，確保 60 人同時使用不衝突。
    回傳 (student_id, name, v_code)
    """
    c1, c2, c3 = st.columns(3)
    with c1: sid   = st.text_input("📝 學號",   key=f"{prefix}_id",   placeholder=id_ph)
    with c2: sname = st.text_input("📝 姓名",   key=f"{prefix}_name", placeholder=name_ph)
    with c3: scode = st.text_input("🔑 驗證碼", key=f"{prefix}_code",
                                    placeholder=code_ph, type="password")
    return sid, sname, scode



def render_teal_input_block(container_key: str, title: str, subtitle: str,
                             id_key: str, name_key: str, code_key: str):
    """
    公版青綠輸入區塊，結構完全照 00_成績查詢.py。
    回傳 (student_id, name, v_code)
    """
    st.markdown(
        '<style>'
        '.st-key-' + container_key + ' > div:first-child {'
        '  border-radius:0 0 12px 12px !important;'
        '  border-top:none !important;'
        '  margin-top:-1px !important;'
        '}'
        '</style>'
        '<div style="'
        'background:linear-gradient(90deg,#0f766e 0%,#0d9488 100%);'
        'border-radius:12px 12px 0 0;'
        'padding:12px 20px 10px 20px;">'
        '<span style="color:white;font-weight:700;font-size:1.0rem;">' + title + '</span>'
        '<div style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin-top:5px;">'
        + subtitle +
        '</div></div>',
        unsafe_allow_html=True)
    with st.container(border=True, key=container_key):
        col_id, col_name, col_code = st.columns(3)
        with col_id:
            sid   = st.text_input("📝 學號",   key=id_key,   placeholder="請輸入學號")
        with col_name:
            sname = st.text_input("📝 姓名",   key=name_key, placeholder="請輸入姓名")
        with col_code:
            scode = st.text_input("🔑 驗證碼", key=code_key,
                                   placeholder="個人驗證碼", type="password")
    return sid, sname, scode

def render_copyright():
    st.markdown(
        '<div style="margin:20px 0 8px 0;padding-top:16px;'
        'border-top:1px solid #e2e8f0;text-align:center;">'
        '<span style="display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;'
        'border-radius:20px;padding:5px 18px;color:#64748b;font-size:0.78rem;line-height:1.6;">'
        '📚 教學輔助用途 · 課本例題引用自《工程統計》Lawrence L. Lapin 著；潘南飛、溫志中 編譯'
        ' · Cengage Learning Asia · ISBN 978-957-9282-94-9</span></div>',
        unsafe_allow_html=True)