# 檔案位置： D:\Engineering_Statistics_App\pages\01_Week_01.py
from utils.auth import require_login
require_login()
import streamlit as st
import random

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    import subprocess as _sp, sys
    _sp.check_call([sys.executable, "-m", "pip", "install", "plotly", "--quiet"])
    import plotly.express as px
    import plotly.graph_objects as go

try:
    from utils.style import apply_theme, set_chart_layout, F_ANNOTATION, F_TITLE
    apply_theme()
except Exception as e:
    st.error(f"樣式載入失敗：{e}")
    F_ANNOTATION = 20; F_TITLE = 24
    def set_chart_layout(fig, *a, **k): return fig


# ── 輸入欄位樣式優化（精準 selector）★ v2.1 ──────────────────────────
st.markdown('''
<style>
/* ── label 標題 ────────────────────────────────────────── */
div[data-testid="stTextInput"] p,
div[data-testid="stTextInput"] label {
    font-weight: 700 !important;
    color: #1e3a5f !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.03em !important;
    margin-bottom: 4px !important;
}

/* ── 輸入框容器（Streamlit 的真實 DOM 層）──────────────── */
div[data-testid="stTextInput"] input {
    border: 2px solid #334155 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #0f172a !important;
    font-size: 1.0rem !important;
    padding: 10px 14px !important;
    height: 44px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.10), inset 0 1px 2px rgba(0,0,0,0.04) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

/* ── focus ─────────────────────────────────────────────── */
div[data-testid="stTextInput"] input:focus {
    border: 2px solid #1d4ed8 !important;
    box-shadow: 0 0 0 3px rgba(29,78,216,0.20), 0 1px 4px rgba(0,0,0,0.10) !important;
    outline: none !important;
}

/* ── placeholder ────────────────────────────────────────── */
div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
    font-size: 0.92rem !important;
}

/* ── 密碼眼睛 icon ──────────────────────────────────────── */
div[data-testid="stTextInput"] button {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── hover 效果 ─────────────────────────────────────────── */
div[data-testid="stTextInput"] input:hover:not(:focus) {
    border-color: #475569 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12), inset 0 1px 2px rgba(0,0,0,0.04) !important;
}
</style>
''', unsafe_allow_html=True)


try:
    from utils.sidebar import render_sidebar
    _sidebar_ok = True
except Exception:
    _sidebar_ok = False

try:
    from utils.gsheets_db import save_score, check_has_submitted, verify_student, get_weekly_password, get_saved_progress, can_submit, mark_submitted, seconds_until_retry
except ImportError:
    def save_score(*a, **k): return False
    def check_has_submitted(*a, **k): return False
    def verify_student(*a, **k): return False, None
    def get_weekly_password(*a, **k): return "888888"

# ── 常數 ──────────────────────────────────────────────────────────────
F_GLOBAL = 18; F_AXIS = 20; F_TICK = 18

# ── 登入防護 ──────────────────────────────────────────────────────────
if "password_correct" not in st.session_state or not st.session_state.password_correct:
    st.markdown('''
    <div style="
        max-width: 380px;
        margin: 60px auto 0 auto;
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2440 100%);
        border-radius: 14px;
        padding: 28px 32px;
        text-align: center;
        box-shadow: 0 6px 24px rgba(0,0,0,0.18);
    ">
        <div style="font-size:2.2rem; margin-bottom:10px;">🔐</div>
        <h2 style="color:#f1f5f9; font-size:1.2rem; font-weight:800; margin:0 0 8px 0;">
            尚未登入
        </h2>
        <p style="color:#94a3b8; font-size:0.9rem; line-height:1.6; margin:0 0 16px 0;">
            此頁面需要登入才能存取。<br>
            請先回到首頁輸入課程密碼。
        </p>
        <div style="
            background:rgba(59,130,246,0.15);
            border: 1px solid rgba(59,130,246,0.4);
            border-radius:8px;
            padding:9px 14px;
            color:#93c5fd;
            font-size:0.88rem;
        ">
            👈 請點選左側導覽列的 <strong>Home</strong> 進行登入
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.stop()

# ── 共用 _card() ──────────────────────────────────────────────────────
def _card(color, bg, tc, title, msg):
    html = (
        '<div style="border-radius:12px;overflow:hidden;'
        'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
        'border:1px solid #e2e8f0;margin:8px 0;">'
        '<div style="background:' + color + ';padding:10px 18px;">'
        '<span style="color:white;font-weight:700;font-size:1.0rem;">' + title + '</span></div>'
        '<div style="background:' + bg + ';padding:14px 18px;'
        'color:' + tc + ';font-size:1.05rem;line-height:1.7;">' + msg + '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ── Session State 初始化 ──────────────────────────────────────────────
if "w1_locked" not in st.session_state:
    st.session_state.w1_locked = False

if _sidebar_ok:
    render_sidebar(current_page="Week 01")

# ── 互動追蹤 key 清單（Section 2a 用）────────────────────────────────
TRACK_KEYS = {
    "t1_quiz":   False,   # Tab1 資料型態測驗
    "t2_quiz":   False,   # Tab2 母體樣本測驗
    "t3_sim":    False,   # Tab3 鑽心試驗模擬器
    "t4_sample": False,   # Tab4 隨機抽樣互動
    "t5_model":  False,   # Tab5 物理模型預測
}
for k in TRACK_KEYS:
    if "w1_track_" + k not in st.session_state:
        st.session_state["w1_track_" + k] = False

# ── 滑桿初始值（偵測是否真正移動過）────────────────────────────────
_SLIDER_INIT = {
    "w1_concrete_total": 500,
    "w1_strain_e": 0.0005,
}

# ── 輔助函數 ─────────────────────────────────────────────────────────
def mark_done(key: str):
    st.session_state["w1_track_" + key] = True

def count_done() -> int:
    return sum(1 for k in TRACK_KEYS if st.session_state.get("w1_track_" + k, False))

def check_slider(slider_key: str, track_key: str):
    init_val = _SLIDER_INIT.get(slider_key)
    cur_val  = st.session_state.get(slider_key, init_val)
    if init_val is not None and cur_val != init_val:
        mark_done(track_key)


# ==========================================
# 頁面標題與內容
# ==========================================
st.markdown('''
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
    border-radius:16px;padding:28px 40px 24px 40px;
    margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);
    text-align:center;">
    <div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;
                margin:0 0 8px 0;line-height:1.25;">
        Week 01｜統計在工程決策中的角色 🎯
    </div>
    <div style="color:#94a3b8;font-size:1.05rem;margin:0 0 10px 0;">
        The Role of Statistics in Engineering Decision-Making · Chapter 1
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.22);
        border-radius:20px;padding:5px 16px;">
        <span style="color:#93c5fd;font-size:0.82rem;">📖</span>
        <span style="color:#e2e8f0;font-size:0.82rem;font-weight:600;">課本第 1 章 · §1.1–1.6</span>
        <span style="color:#64748b;font-size:0.78rem;">｜《工程統計》Lapin 著</span>
    </div>
</div>
''', unsafe_allow_html=True)

# 翻譯提示
st.markdown('''
<div style="margin:0 0 10px 0;text-align:center;">
    <span style="display:inline-block;background:#eff6ff;border:1px solid #bfdbfe;
        border-radius:20px;padding:4px 16px;color:#3b82f6;font-size:0.75rem;line-height:1.6;">
        🌐 <b>For English:</b> Right-click anywhere on the page → "Translate to English" (Chrome / Edge built-in translation)
    </span>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
            border:1px solid #99f6e4;margin:0 0 18px 0;">
    <div style="background:#0f766e;padding:9px 18px;">
        <span style="color:white;font-weight:700;font-size:0.95rem;">📌 本週學習路線</span>
    </div>
    <div style="background:#f0fdfa;padding:13px 18px;color:#134e4a;font-size:1.0rem;line-height:1.7;">
        請依序點選下方各小節的標籤，完成理論閱讀與互動實驗。
        完成所有標籤後，再挑戰最後的<strong>整合性總測驗</strong>！<br>
        <span style="font-size:0.92rem;color:#0f766e;">
            §1.1-1.2 資料型態 → §1.3 母體與樣本 → §1.4 需要抽樣的理由 → §1.5 樣本的選取 → §1.6 統計工程應用
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">
        📚 1. 本週核心理論與互動
    </span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標籤，完成理論閱讀與互動實驗</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1.1-1.2 統計與資料型態", 
    "1.3 母體、樣本與推論", 
    "1.4 需要樣本的理由", 
    "1.5 樣本的選取", 
    "1.6 統計工程應用"
])

# ------------------------------------------
# Tab 1: 1.1 - 1.2 統計資料型態
# ------------------------------------------
with tab1:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">📌 核心概念：統計學的意義與資料型態</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.0rem;line-height:1.8;">
            <b>統計學 (Statistics)</b>：透過數值資料的分析，提供人們在不確定情況下作成適當決策或傳達有用資訊的科學方法。<br><br>
            資料依衡量方式（尺度）分為四大類型：<br>
            ▸ <b>名目資料 (Nominal)</b>：僅代表分類，無大小順序（如系所代號）<br>
            ▸ <b>順序資料 (Ordinal)</b>：可排序，但差距無意義（如蒲福風級）<br>
            ▸ <b>區間資料 (Interval)</b>：差距有意義，但無真正零點（如攝氏溫度）<br>
            ▸ <b>比率資料 (Ratio)</b>：有真正零點，可乘除運算（如重量、長度）
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">💡 隨堂小測驗：資料型態鑑定儀</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    data_example = st.radio("📍 **題目：『橋樑基座承受的載重 (噸)』是屬於哪一種資料型態？你覺得是以下哪一個呢？請勾選你覺得的答案：**", 
                            ["請選擇您的答案...", "A. 名目資料 (Nominal)", "B. 順序資料 (Ordinal)", "C. 區間資料 (Interval)", "D. 比率資料 (Ratio)"])
    if st.button("送出鑑定", key="btn_tab1"):
        if data_example == "請選擇您的答案...":
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 請先選擇答案</span></div>
            <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">嘿！您還沒選擇答案喔，請先勾選一個再送出。</div>
        </div>
        ''', unsafe_allow_html=True)
        elif data_example == "D. 比率資料 (Ratio)":
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🎉 恭喜答對！</span></div>
            <div style="background:#f0fdf4;padding:13px 18px;color:#166534;font-size:1.0rem;line-height:1.6;">重量有絕對的零點（0噸=無重量），20噸是10噸的兩倍，可乘除運算 → 比率資料 (Ratio)！</div>
        </div>
        ''', unsafe_allow_html=True)
            mark_done("t1_quiz")
        else:
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">❌ 答錯了</span></div>
            <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">提示：載重有沒有「真正的零點」？能不能說 20 噸是 10 噸的兩倍？</div>
        </div>
        ''', unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 1.3 母體與樣本 (演繹與歸納)
# ------------------------------------------
with tab2:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 6px 0;">
        <div style="background:#0f766e;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">📌 核心概念：母體、樣本與統計推論</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.0rem;line-height:1.8;">
            🎯 <b>母體 (Population)</b>：所感興趣之對象特徵的所有可能觀察結果的集合。<br>
            🧩 <b>樣本 (Sample)</b>：由母體選出的部分觀測值的集合。
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="display:flex;gap:14px;margin:10px 0 14px 0;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #99f6e4;">
            <div style="background:#0f766e;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">⬇️ 演繹統計 (Deductive)</span>
            </div>
            <div style="flex:1;background:#f0fdfa;padding:14px 16px;color:#134e4a;font-size:1.0rem;line-height:1.7;">
                由充分已知的<b>母體特性</b>來探討<b>樣本</b>的相關特性。<br>
                <span style="color:#0f766e;font-size:0.88rem;">方向：母體 → 樣本</span>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #99f6e4;">
            <div style="background:#0f766e;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">⬆️ 推論統計 (Inductive)</span>
            </div>
            <div style="flex:1;background:#f0fdfa;padding:14px 16px;color:#134e4a;font-size:1.0rem;line-height:1.7;">
                由已知的<b>樣本特性</b>來推論未知的<b>母體特性</b>。<br>
                <span style="color:#0f766e;font-size:0.88rem;">方向：樣本 → 母體（工程上最常用）</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">💡 隨堂小測驗：你是哪一種統計學家？</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    reasoning_type = st.radio("📍 **題目：『我隨機抽了 3 支鋼材發現有 1 支瑕疵，我想以此推估整批鋼材的總不良率。』請問這屬於哪一種統計推論？**", 
                              ["請選擇您的答案...", "A. 演繹統計 (Deductive)", "B. 歸納/推論統計 (Inductive)"])
    if st.button("送出解答", key="btn_tab2"):
        if reasoning_type == "請選擇您的答案...":
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 請先選擇答案</span></div>
            <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">請先勾選一個答案再送出喔！</div>
        </div>
        ''', unsafe_allow_html=True)
        elif reasoning_type == "B. 歸納/推論統計 (Inductive)":
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🎉 恭喜答對！</span></div>
            <div style="background:#f0fdf4;padding:13px 18px;color:#166534;font-size:1.0rem;line-height:1.6;">從「已知的樣本結果」反向推估「未知的母體特徵」，這正是歸納/推論統計的核心精神！</div>
        </div>
        ''', unsafe_allow_html=True)
            mark_done("t2_quiz")
        else:
            st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">❌ 答錯了</span></div>
            <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">提示：我們是從「樣本推回母體」還是「母體推向樣本」？仔細看題目方向！</div>
        </div>
        ''', unsafe_allow_html=True)

# ------------------------------------------
# Tab 3: 1.4 需要樣本的理由
# ------------------------------------------
with tab3:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">📌 核心概念：為何工程上依賴「抽樣」而非「普查」？</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.0rem;line-height:1.85;">
            以抽樣取代普查最主要的原因是其<b>經濟上的優點</b>，樣本可節省的成本通常非常顯著。此外還有：<br><br>
            ① <b>時間限制 (Timeliness)</b>：普查耗時過長，完成時資訊可能已過時。<br>
            ② <b>大母體 (Large Populations)</b>：母體龐大（或無限），無法全部觀測。<br>
            ③ <b>破壞性觀測 (Destructive Nature)</b>：如混凝土鑽心試驗，觀測即破壞，不能普查。
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">💡 互動實驗：鑽心試驗模擬器（感受破壞性觀測的成本）</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    total_concrete = st.slider(
        "設定預拌混凝土總圓柱試體數量（普查需全部壓碎）— 拖動滑桿感受普查 vs 抽樣的成本差距",
        100, 1000, 500, key="w1_concrete_total"
    )
    check_slider("w1_concrete_total", "t3_sim")
    sample_to_crush = st.number_input("決定抽樣壓碎的數量", 1, total_concrete, 10)
    if st.button("執行抗壓試驗", key="btn_tab3"):
        mark_done("t3_sim")
        cost_saved = (total_concrete - sample_to_crush) * 500
        st.markdown(
            '<div style="display:flex;gap:14px;margin-top:10px;flex-wrap:wrap;">'
            '<div style="flex:1;min-width:200px;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;">'
            '<div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;">💥 試驗完成</span></div>'
            '<div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;">破壞了 <b>' + str(sample_to_crush) + '</b> 顆試體，取得抗壓強度數據</div>'
            '</div>'
            '<div style="flex:1;min-width:200px;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;">'
            '<div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;">✅ 抽樣節省</span></div>'
            '<div style="background:#f0fdf4;padding:13px 18px;color:#166534;font-size:1.0rem;">保全 <b>' + str(total_concrete - sample_to_crush) + '</b> 顆，省下約 <b>' + f'{cost_saved:,}' + ' 元</b></div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ------------------------------------------
# Tab 4: 1.5 樣本的選取
# ------------------------------------------
with tab4:
    if "secret_a_country" not in st.session_state:
        st.session_state.secret_a_country = random.sample(range(1, 101), 10)
        st.session_state.secret_a_country.sort()
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">📌 核心概念：確保樣本的代表性——隨機抽樣</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.0rem;line-height:1.7;">
            <b>簡單隨機抽樣法</b>：母體中的任一樣本被抽出的機率均相同。<br>
            實務上可利用「<b>隨機數字表（附錄表 F）</b>」或電腦產生的「<b>擬隨機數 (Pseudorandom number)</b>」來抽樣。
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">💡 互動盲測：隨機抽樣大比拼（電腦 vs 亂數表 vs 人腦）</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("假設有 100 名諾貝爾物理得主 (編號 01-100)，我們要抽出 10 位進行訪談。")
    st.markdown("🤫 **【秘密任務】系統已經在背後偷偷隨機指定了 10 位作為「A 國得主」！**")
    st.markdown("但在揭曉之前，沒有人知道是哪 10 個號碼。理論上，隨機抽出 10 人時，中獎期望值是 1 人。請選擇一種方法進行抽樣，看看哪一種方法能最客觀地逮住他們！")
    
    if st.button("🔄 重新洗牌 (更換隱藏的 A 國得主名單)"):
        st.session_state.secret_a_country = random.sample(range(1, 101), 10)
        st.session_state.secret_a_country.sort()
        st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#0369a1;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🔀 洗牌完成</span></div>
            <div style="background:#e0f2fe;padding:13px 18px;color:#0c4a6e;font-size:1.0rem;line-height:1.6;">A 國得主已經換人囉！名單依然是個秘密，準備開始新的抽樣挑戰！</div>
        </div>
        ''', unsafe_allow_html=True)

    sample_method = st.radio("請選擇您想測試的抽樣方法：", ["A. 電腦擬隨機抽樣", "B. 查閱隨機數字表 (附錄表 F)", "C. 人腦直覺隨機挑選 (手動輸入)"])
    
    def reveal_and_check(sampled_list):
        secret_list = st.session_state.secret_a_country
        caught = [x for x in sampled_list if x in secret_list]
        hit_color = "#22c55e" if len(caught) > 0 else "#3b82f6"
        hit_bg = "#f0fdf4" if len(caught) > 0 else "#eff6ff"
        hit_tc = "#166534" if len(caught) > 0 else "#1e40af"
        hit_msg = f"🎯 發現 {len(caught)} 位 A 國得主！中獎編號：{caught}" if len(caught) > 0 else "🎯 這次沒有抽中任何 A 國得主"
        st.markdown(
            '<div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap;">'
            '<div style="flex:1;min-width:220px;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;">'
            '<div style="background:#3b82f6;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">✅ 您的抽樣名單</span></div>'
            '<div style="background:#eff6ff;padding:13px 18px;font-size:1.0rem;color:#1e40af;font-weight:600;">' + str(sampled_list) + '</div>'
            '</div>'
            '<div style="flex:1;min-width:220px;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;">'
            '<div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🔓 系統揭曉：A 國得主</span></div>'
            '<div style="background:#fffbeb;padding:13px 18px;font-size:1.0rem;color:#92400e;font-weight:600;">' + str(secret_list) + '</div>'
            '</div>'
            '<div style="flex:1;min-width:220px;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;">'
            '<div style="background:' + hit_color + ';padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🏆 對獎結果</span></div>'
            '<div style="background:' + hit_bg + ';padding:13px 18px;font-size:1.0rem;color:' + hit_tc + ';font-weight:600;">' + hit_msg + '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    if sample_method == "A. 電腦擬隨機抽樣":
        st.write("由電腦程式內部重複地進行隨機選取，產生 10 個不重複的擬隨機數。")
        if st.button("🤖 執行電腦抽樣並對獎", key="btn_tab4_a"):
            sampled = random.sample(range(1, 101), 10)
            sampled.sort()
            reveal_and_check(sampled)
            mark_done("t4_sample")
            
    elif sample_method == "B. 查閱隨機數字表 (附錄表 F)":
        st.write("請從亂數表抄寫 10 組 5 位數。系統將自動擷取每組的 **前 2 碼** 作為得主編號（若為 00 則視為 100）。")
        table_input = st.text_input("輸入 10 組數字 (請以「逗號」分隔)：", value="", placeholder="例如: 12651, 61646, 81169, 74436...")
        if st.button("📖 解析亂數表並對獎", key="btn_tab4_b"):
            if not table_input.strip():
                st.markdown('''
                <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                    <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 尚未輸入</span></div>
                    <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">請先查閱附錄表 F 並輸入數字再進行對獎！</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                parts = table_input.split(",")
                sampled = []
                for p in parts:
                    p = p.strip()
                    if len(p) >= 2 and p[:2].isdigit():
                        num = int(p[:2])
                        if num == 0: num = 100
                        sampled.append(num)
                if len(sampled) > 0:
                    sampled.sort()
                    reveal_and_check(sampled)
                    mark_done("t4_sample")
                else:
                    st.markdown('''
                    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                        <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">❌ 格式錯誤</span></div>
                        <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">無法解析數字，請確保輸入格式正確（例如：12651, 61646）</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
    elif sample_method == "C. 人腦直覺隨機挑選 (手動輸入)":
        st.write("請憑直覺，隨機輸入 10 個 1~100 的數字。看看人類大腦是否真的能做到「公平且無預期的隨機」？")
        human_input = st.text_input("輸入 10 個數字 (請以「逗號」分隔)：", value="", placeholder="例如: 7, 14, 25, 33, 42...")
        if st.button("🧠 提交人腦名單並對獎", key="btn_tab4_c"):
            if not human_input.strip():
                st.markdown('''
                <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                    <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 尚未輸入</span></div>
                    <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">請先憑直覺輸入 10 個數字再進行對獎！</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                parts = human_input.split(",")
                sampled = []
                for p in parts:
                    try:
                        num = int(p.strip())
                        if 1 <= num <= 100:
                            sampled.append(num)
                    except:
                        pass
                if len(sampled) > 0:
                    sampled.sort()
                    reveal_and_check(sampled)
                    mark_done("t4_sample")
                else:
                    st.markdown('''
                    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                        <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">❌ 格式錯誤</span></div>
                        <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">無法解析數字，請確保輸入為 1~100 之間的整數並以逗號分隔</div>
                    </div>
                    ''', unsafe_allow_html=True)

# ------------------------------------------
# Tab 5: 1.6 統計之工程應用
# ------------------------------------------
with tab5:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">📌 核心概念：模式建立與預測（Model Building）</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.0rem;line-height:1.7;">
            由一個或多個自變數預測因變數，是工程統計的重要應用。<br>
            由試驗資料中求出變數間最適配的關係式，稱為<b>迴歸分析 (Regression Analysis)</b>。
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:9px 18px;">
            <span style="color:white;font-weight:700;font-size:0.95rem;">💡 互動實驗：物理模型預測</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.write("Lapin 課本中的物理模型範例：圓形金屬棒的應力 $S$ 與應變 $E$ 之間的線性關係方程式為：$$ S = -5,000 + 10^7 E $$")
    e_input = st.slider(
        "請調整預期應變量 E — 拖動滑桿觀察應力如何隨應變線性增加",
        min_value=0.0001, max_value=0.0010, value=0.0005, step=0.0001,
        format="%.4f", key="w1_strain_e"
    )
    check_slider("w1_strain_e", "t5_model")
    if st.button("計算預測應力", key="btn_tab5"):
        mark_done("t5_model")
        s_predict = -5000 + (10**7 * e_input)
        st.markdown(
            '<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);border:1px solid #e2e8f0;margin-top:12px;">'
            '<div style="background:#3b82f6;padding:10px 20px;">'
            '<span style="color:white;font-size:1.0rem;font-weight:700;">📐 預測之應力承受值 S（載重/單位面積）</span>'
            '</div>'
            '<div style="background:#eff6ff;padding:16px 20px;">'
            '<span style="font-size:2.4rem;font-weight:900;color:#1e40af;">' + f'{s_predict:,.0f}' + '</span>'
            '<span style="font-size:1.1rem;color:#475569;margin-left:8px;">磅 (lb)</span><br>'
            '<span style="font-size:0.9rem;color:#94a3b8;">依據迴歸線性模型預測 · E = ' + f'{e_input:.4f}' + '</span>'
            '</div></div>',
            unsafe_allow_html=True
        )

st.divider()

# ==========================================
# 模組二：實務工程案例 (折疊收納)
# ==========================================
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:8px 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📂 2. 實務工程案例探討</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">點擊展開案例，看看統計如何在真實工程中發揮關鍵作用</p>', unsafe_allow_html=True)
with st.expander("☎️ 案例 A：電話聲音傳輸 (普查的迷思與抽樣的奇蹟) - 點擊展開", expanded=False):
    st.markdown("**案例背景 (例題 1.1)**")
    st.write("舊有電話主要缺點為聲波太慢且每一次談話需佔一個線路。若將原有連續傳遞（如同普查）改以每 100 微秒為一間隔的電磁波進行傳遞區間（如同抽樣）。")
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
        <div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">✅ 工程結論</span></div>
        <div style="background:#f0fdf4;padding:13px 18px;color:#166534;font-size:1.0rem;line-height:1.6;">以部分間斷傳輸電磁波的方式，較連續性傳遞可省下可觀的時間與成本，將電磁波速及容量增快至 100 倍！</div>
    </div>
    ''', unsafe_allow_html=True)

with st.expander("👨‍👩‍👧‍👦 案例 B：美國 1950 年人口普查 (普查一定比抽樣準確嗎？) - 點擊展開", expanded=False):
    st.markdown("**案例背景 (例題 1.2)**")
    st.write("美國 1950 年人口普查報告指出，30歲以下的鰥夫（喪妻）人數比1940年增加了 10倍 (100%)。這是一個極度不合理的數值。")
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
        <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 工程結論</span></div>
        <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">普查資料雖龐大，但電腦化處理時讀卡位置誤打造成巨大錯誤。謹慎的抽樣往往比草率的普查更正確！</div>
    </div>
    ''', unsafe_allow_html=True)

st.divider()

# =====================================================================
# ██  SECTION 2a：互動參與進度記錄  ██
# =====================================================================
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📝 2a. 本週互動參與記錄</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">完成上方各節互動後，在此送出本週參與記錄（不計分，僅記錄完成狀況）</p>', unsafe_allow_html=True)

done_count = count_done()
total_count = len(TRACK_KEYS)
done_pct = int(done_count / total_count * 100)

# 追蹤清單標籤
track_labels = {
    "t1_quiz":   "1.1–1.2 資料型態測驗",
    "t2_quiz":   "1.3 母體樣本測驗",
    "t3_sim":    "1.4 鑽心試驗模擬",
    "t4_sample": "1.5 隨機抽樣互動",
    "t5_model":  "1.6 物理模型預測",
}

# 進度卡片（5項分2列）
_p_row1 = st.columns(3)
_p_row2 = st.columns(2)
_p_all = list(_p_row1) + list(_p_row2)
for _i, (k, label) in enumerate(track_labels.items()):
    done_flag = st.session_state.get("w1_track_" + k, False)
    icon = "✅" if done_flag else "⬜"
    with _p_all[_i]:
        st.markdown(
            '<div style="border-radius:10px;overflow:hidden;border:1px solid #e2e8f0;margin-bottom:8px;">' +
            '<div style="background:#1e3a5f;padding:8px 12px;">' +
            '<span style="color:white;font-size:0.88rem;font-weight:700;">' + icon + " " + label + '</span>' +
            '</div></div>',
            unsafe_allow_html=True
        )

_card("#0369a1", "#e0f2fe", "#0c4a6e", "📊 本週互動完成率",
      "已完成 <b>" + str(done_count) + "/" + str(total_count) + "</b> 項互動（" + str(done_pct) + "%）")

# 送出表單
_card("#475569", "#f8fafc", "#334155", "📤 送出互動參與記錄",
      "請填寫學號、姓名與驗證碼後送出，系統將記錄本週互動完成狀況。")

col_2a_id, col_2a_name, col_2a_code = st.columns(3)
with col_2a_id:   ia_id   = st.text_input("📝 學號", key="w1_ia_id")
with col_2a_name: ia_name = st.text_input("📝 姓名", key="w1_ia_name")
with col_2a_code: ia_code = st.text_input("🔑 驗證碼", type="password", key="w1_ia_code")

# ── 即時顯示即將送出的進度明細（讓同學確認是否正確）──────────────
_track_label_map_w1 = {
    "t1_quiz":   "資料型態測驗",
    "t2_quiz":   "母體樣本測驗",
    "t3_sim":    "鑽心試驗模擬",
    "t4_sample": "隨機抽樣互動",
    "t5_model":  "物理模型預測",
}
_preview_done_w1 = sum(1 for k in TRACK_KEYS if st.session_state.get("w1_track_" + k, False))
_preview_pct_w1  = int(_preview_done_w1 / len(TRACK_KEYS) * 100)
_preview_color_w1 = "#22c55e" if _preview_pct_w1 >= 80 else "#f59e0b" if _preview_pct_w1 >= 50 else "#ef4444"
_items_html_w1 = " ".join(
    f'<span style="font-size:0.82rem;padding:2px 8px;margin:2px;border-radius:6px;display:inline-block;'
    f'background:{"#dcfce7" if st.session_state.get("w1_track_"+k, False) else "#f1f5f9"};'
    f'color:{"#166534" if st.session_state.get("w1_track_"+k, False) else "#94a3b8"};">'
    f'{"✅" if st.session_state.get("w1_track_"+k, False) else "⬜"} {_track_label_map_w1.get(k,k)}</span>'
    for k in TRACK_KEYS
)
st.markdown(
    f'<div style="border-radius:10px;overflow:hidden;border:1px solid {_preview_color_w1}44;margin:8px 0;">' +
    f'<div style="background:{_preview_color_w1}18;padding:9px 16px;border-bottom:1px solid {_preview_color_w1}33;">' +
    f'<span style="font-weight:700;color:{_preview_color_w1};">📋 送出前確認：目前進度 {_preview_pct_w1}%（{_preview_done_w1}/{len(TRACK_KEYS)} 項）</span>' +
    f'<span style="font-size:0.82rem;color:#94a3b8;margin-left:8px;">若進度與預期不符，請先返回完成各項互動再送出</span>' +
    f'</div><div style="padding:10px 16px;line-height:2.0;">{_items_html_w1}</div></div>',
    unsafe_allow_html=True
)

_w1_wait = seconds_until_retry("w1_ia")
if _w1_wait > 0:
    st.info(f"⏳ 系統處理中，請等待 **{_w1_wait} 秒**後再送出（防止重複送出影響系統穩定性）")
if st.button("📤 送出本週互動記錄", key="w1_ia_submit", use_container_width=True,
             disabled=(_w1_wait > 0)):
    mark_submitted("w1_ia")
    if ia_id and ia_name and ia_code:
        is_valid_ia, student_idx_ia = verify_student(ia_id, ia_name, ia_code)
        if not is_valid_ia:
            _card("#ef4444", "#fef2f2", "#991b1b", "⛔ 身分驗證失敗",
                  "學號、姓名或驗證碼有誤，請重新確認！")
        else:
            detail_parts = []
            for k in TRACK_KEYS:
                done_flag = st.session_state.get("w1_track_" + k, False)
                symbol = "V" if done_flag else "-"
                detail_parts.append(k + ":" + symbol)
            detail_str = " | ".join(detail_parts)
            ia_record = str(done_pct) + "% (" + str(done_count) + "/" + str(total_count) + ") | " + detail_str

            # ── 防止 session 重連後進度歸零寫入 ──────────────────
            try:
                from utils.gsheets_db import get_saved_progress as _gsp
                _saved = _gsp(ia_id, "Week 01 互動")
                if _saved and _saved["pct"] > done_pct:
                    _saved_detail = _saved.get("detail", "")
                    for _part in _saved_detail.split("|"):
                        _part = _part.strip()
                        if ":" in _part:
                            _k, _v = _part.split(":", 1)
                            _k = _k.strip()
                            if _k in TRACK_KEYS and _v.strip() == "V":
                                st.session_state["w1_track_" + _k] = True
                    done_count = count_done()
                    done_pct   = int(done_count / total_count * 100)
                    detail_parts = []
                    for k in TRACK_KEYS:
                        done_flag = st.session_state.get("w1_track_" + k, False)
                        symbol = "V" if done_flag else "-"
                        detail_parts.append(k + ":" + symbol)
                    detail_str = " | ".join(detail_parts)
                    ia_record = str(done_pct) + "% (" + str(done_count) + "/" + str(total_count) + ") | " + detail_str
            except Exception:
                pass

            success_ia = save_score(student_idx_ia, ia_id, ia_name, "Week 01 互動", ia_record, done_pct)
            if success_ia:
                # ✅ 成功：只存結果，不清除 w1_track_* 進度
                st.session_state["w1_ia_submitted"] = {
                    "name": ia_name, "id": ia_id,
                    "pct": done_pct, "done": done_count, "total": total_count
                }
                st.rerun()
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 送出失敗，請稍後重試",
                      "伺服器暫時忙碌（可能是很多同學同時送出）。<br>"
                      "您的互動進度 <b>完全保留</b>，請等待 <b>10～20 秒</b>後再按一次「送出」即可。")
    else:
        _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 資料不完整",
              "請完整填寫學號、姓名與驗證碼再送出。")

st.divider()

# ==========================================
# 模組三：整合性總測驗
# ==========================================
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:8px 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">
        📝 3. 本週整合性總測驗
    </span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:1.0rem;margin:0 0 16px 4px;">完成所有理論閱讀後，輸入老師公布的解鎖密碼開始作答</p>', unsafe_allow_html=True)

real_password = get_weekly_password("Week 01")
if not real_password:
    real_password = "ADMIN"

st.markdown('''
<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
    <div style="background:#475569;padding:9px 18px;"><span style="color:white;font-weight:700;">🔒 測驗鎖定中</span></div>
    <div style="background:#f8fafc;padding:13px 18px;color:#334155;font-size:1.0rem;">
        請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。
    </div>
</div>
''', unsafe_allow_html=True)

_col_pw, _col_btn = st.columns([5, 1])
with _col_pw:
    user_code = st.text_input("密碼", type="password", key="w1_unlock_code",
                               label_visibility="collapsed", placeholder="🔑 請輸入 6 位數解鎖密碼…")
with _col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w1_unlock_btn")

if user_code != real_password:
    if user_code != "":
        st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">❌ 密碼錯誤</span></div>
            <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">請確認您輸入的字母與數字是否正確！</div>
        </div>
        ''', unsafe_allow_html=True)
else:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
        <div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🔓 密碼正確！</span></div>
        <div style="background:#f0fdf4;padding:13px 18px;color:#166534;font-size:1.0rem;line-height:1.6;">測驗已解鎖，請完成以下題目後送出。</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
        <div style="background:#3b82f6;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">📋 測驗說明</span></div>
        <div style="background:#eff6ff;padding:13px 18px;color:#1e40af;font-size:1.0rem;line-height:1.6;">4 題，每題 25 分，共 100 分。作答送出後即鎖定成績，請確實核對學號與驗證碼！</div>
    </div>
    ''', unsafe_allow_html=True)

    with st.form("week1_unified_quiz"):
        col_id, col_name, col_code = st.columns(3)
        with col_id: st_id = st.text_input("📝 學號")
        with col_name: st_name = st.text_input("📝 姓名")
        with col_code: st_vcode = st.text_input("🔑 驗證碼", type="password")
        
        st.markdown("---")
        
        st.markdown("**Q1 (1.2節)：請問「橋樑的承載重量 (噸)」屬於哪一種統計資料型態？**")
        q1 = st.radio("Q1 選項：", ["名目資料 (Nominal)", "順序資料 (Ordinal)", "區間資料 (Interval)", "比率資料 (Ratio)"], key="q1")
        
        st.markdown("**Q2 (1.4節)：進行建築物之混凝土鑽心試驗來決定強度，是基於下列哪一種必須採用「抽樣」而非「普查」的原因？**")
        q2 = st.radio("Q2 選項：", ["時間限制 (Timeliness)", "具有破壞性特質的觀測 (Destructive Nature)", "大母體 (Large Populations)", "無法取得的母體 (Inaccessible Populations)"], key="q2")
        
        st.markdown("**Q3 (1.6節)：利用數學方程式 (如 $S = -5000 + 10^7 E$)，由已知應變預測未知應力的統計程序，屬於哪一種工程應用？**")
        q3 = st.radio("Q3 選項：", ["統計製程管制 (SPC)", "模式建立與預測 (迴歸分析)", "評量設計的可靠度", "實驗設計 (DOE)"], key="q3")
        
        st.markdown("**Q4 (1.3節)：某品管工程師已知這批鋼材的「母體平均強度」，他據此計算出隨機抽取 5 支鋼材其平均強度大於某個數值的機率。這種「由充分已知的母體特性來探討樣本相關特性」的推理過程稱之為？**")
        q4 = st.radio("Q4 選項：", ["敘述統計 (Descriptive Statistics)", "歸納統計 (Inductive Statistics)", "演繹統計 (Deductive Statistics)", "探究性統計 (Exploratory Data Analysis)"], key="q4")
        
        st.markdown("---")
        
        if st.form_submit_button("✅ 簽署並送出本週測驗", disabled=st.session_state.w1_locked):
            if st_id and st_name and st_vcode:
                with st.spinner("系統安全驗證與自動評分中..."):
                    is_valid_user, student_idx = verify_student(st_id, st_name, st_vcode)
                    
                    if not is_valid_user:
                        st.markdown('''
                        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                            <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⛔ 身分驗證失敗</span></div>
                            <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">您輸入的學號、姓名或驗證碼有誤，請重新確認！（為保護成績安全，不予顯示作答結果）</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        if check_has_submitted(st_id, "Week 01"):
                            st.markdown('''
                            <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                                <div style="background:#ef4444;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⛔ 拒絕送出</span></div>
                                <div style="background:#fef2f2;padding:13px 18px;color:#991b1b;font-size:1.0rem;line-height:1.6;">系統查詢到您已繳交過 Week 01 的測驗！請勿重複作答。</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            score = 0
                            if q1 == "比率資料 (Ratio)": score += 25
                            if q2 == "具有破壞性特質的觀測 (Destructive Nature)": score += 25
                            if q3 == "模式建立與預測 (迴歸分析)": score += 25
                            if q4 == "演繹統計 (Deductive Statistics)": score += 25
                            
                            ans_str = f"Q1:{q1[:2]}, Q2:{q2[:4]}, Q3:{q3[:4]}, Q4:{q4[:2]}"
                            success = save_score(student_idx, st_id, st_name, "Week 01", ans_str, score)
                            
                            if success:
                                st.session_state.w1_locked = True
                                success_html = (
                                    '<div style="border-radius:12px;overflow:hidden;'
                                    'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
                                    'border:1px solid #e2e8f0;margin:8px 0;">'
                                    '<div style="background:#22c55e;padding:9px 18px;">'
                                    '<span style="color:white;font-weight:700;">🎊 上傳成功！</span></div>'
                                    '<div style="background:#f0fdf4;padding:13px 18px;'
                                    'color:#166634;font-size:1.0rem;line-height:1.65;">'
                                    '<b>' + st_name + '</b>（' + st_id + '）驗證通過<br>'
                                    '<span style="font-size:2rem;font-weight:900;color:#15803d;">'
                                    + str(score) +
                                    '</span> 分　成績已鎖定寫入資料庫！</div></div>'
                                )
                                st.markdown(success_html, unsafe_allow_html=True)
                                if score == 100:
                                    st.balloons()
                                    st.markdown('''
                                    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                                        <div style="background:#7c3aed;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🏆 滿分 100！</span></div>
                                        <div style="background:#f5f3ff;padding:13px 18px;color:#4c1d95;font-size:1.0rem;line-height:1.6;">統計學第一章你已完全掌握，繼續保持這個狀態！</div>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                elif score >= 75:
                                    st.markdown('''
                                    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                                        <div style="background:#3b82f6;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">👍 表現不錯！</span></div>
                                        <div style="background:#eff6ff;padding:13px 18px;color:#1e40af;font-size:1.0rem;line-height:1.6;">建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析，再複習一次更紮實！</div>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                else:
                                    st.markdown('''
                                    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                                        <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">📖 繼續加油！</span></div>
                                        <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">請回顧本週各節的概念說明與互動實驗，特別是不確定的題目——理解比死背更重要！</div>
                                    </div>
                                    ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
                    <div style="background:#f59e0b;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">⚠️ 資料不完整</span></div>
                    <div style="background:#fffbeb;padding:13px 18px;color:#92400e;font-size:1.0rem;line-height:1.6;">請完整填寫學號、姓名與驗證碼再送出表單。</div>
                </div>
                ''', unsafe_allow_html=True)

    if st.session_state.w1_locked:
        st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">
            <div style="background:#475569;padding:9px 18px;"><span style="color:white;font-weight:700;font-size:0.95rem;">🔒 測驗已鎖定</span></div>
            <div style="background:#f8fafc;padding:13px 18px;color:#334155;font-size:1.0rem;line-height:1.6;">系統已安全登錄您的成績，如有疑問請聯繫授課教師。</div>
        </div>
        ''', unsafe_allow_html=True)

# =====================================================================
# 頁面底部：本週學習摘要速查卡
# =====================================================================
st.divider()
with st.expander("📚 本週核心概念速查卡（考前複習用）", expanded=False):
    _cards = [
        ("#3b82f6","#eff6ff","#1e40af","📊 1.1–1.2 統計學與資料型態",
         ["統計學：在不確定情況下作成決策的科學方法",
          "名目 (Nominal)：僅分類，無大小順序",
          "順序 (Ordinal)：可排序，但差距無意義",
          "區間 (Interval)：差距有意義，但無真正零點",
          "比率 (Ratio)：有真正零點，可乘除（最完整）"]),
        ("#0f766e","#f0fdfa","#134e4a","🔍 1.3 母體與樣本",
         ["母體 (Population)：全體觀察結果的集合",
          "樣本 (Sample)：母體的部分觀測值",
          "演繹統計：母體 → 樣本（已知推未知）",
          "推論/歸納統計：樣本 → 母體（工程上最常用）"]),
        ("#f59e0b","#fffbeb","#92400e","💡 1.4 需要抽樣的四大理由",
         ["時間限制 (Timeliness)",
          "大母體 (Large Populations)",
          "破壞性觀測 (Destructive Nature)",
          "無法取得的母體 (Inaccessible Populations)"]),
        ("#22c55e","#f0fdf4","#166534","🎲 1.5 樣本的選取",
         ["簡單隨機抽樣：每個個體被抽到的機率相等",
          "工具：隨機數字表（附錄表 F）或電腦擬隨機數",
          "人腦直覺往往有偏誤，不適合用來抽樣"]),
        ("#0369a1","#e0f2fe","#0c4a6e","📈 1.6 統計工程應用",
         ["模式建立與預測（迴歸分析）",
          "線性模型範例：S = −5,000 + 10⁷E",
          "品質衡量、可靠度評估、實驗設計（DOE）"]),
    ]
    # 5 張卡片：3+2 兩列排版
    _ref_row1 = st.columns(3)
    _ref_row2_pad = st.columns([1, 2, 2, 1])  # 置中對齊兩張卡
    _ref_row2 = [_ref_row2_pad[1], _ref_row2_pad[2]]
    _ref_all = list(_ref_row1) + list(_ref_row2)
    for _i, (_hc, _bc, _tc, _title, _items) in enumerate(_cards):
        with _ref_all[_i]:
            _items_html = "".join(
                '<li style="margin:4px 0;color:' + _tc + ';font-size:0.92rem;">' + it + '</li>'
                for it in _items
            )
            st.markdown(
                '<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);' +
                'border:1px solid #e2e8f0;margin-bottom:14px;">' +
                '<div style="background:' + _hc + ';padding:9px 16px;">' +
                '<span style="color:white;font-weight:800;font-size:0.92rem;">' + _title + '</span></div>' +
                '<div style="background:' + _bc + ';padding:11px 16px;">' +
                '<ul style="margin:0;padding-left:16px;">' + _items_html + '</ul></div></div>',
                unsafe_allow_html=True
            )

# =====================================================================
# 頁面底部版權聲明 badge
# =====================================================================
st.markdown('''
<div style="margin:20px 0 8px 0;padding-top:16px;border-top:1px solid #e2e8f0;text-align:center;">
    <span style="display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;
        border-radius:20px;padding:5px 18px;color:#64748b;font-size:0.78rem;line-height:1.6;">
        📚 教學輔助用途 · 課本例題引用自《工程統計》Lawrence L. Lapin 著；潘南飛、溫志中 編譯
        · Cengage Learning Asia · ISBN 978-957-9282-94-9
    </span>
</div>
''', unsafe_allow_html=True)