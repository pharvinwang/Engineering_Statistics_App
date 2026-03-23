# 檔案位置： D:\Engineering_Statistics_App\pages\04_Week_04.py
import streamlit as st
import pandas as pd
import numpy as np
import math
from math import comb, factorial, exp

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    import subprocess as _sp, sys
    _sp.check_call([sys.executable, "-m", "pip", "install", "plotly", "--quiet"])
    import plotly.express as px
    import plotly.graph_objects as go

# 1. 套用樣式
try:
    from utils.style import apply_theme, set_chart_layout, F_ANNOTATION, F_TITLE
    apply_theme()
except Exception as e:
    st.error(f"樣式載入失敗：{e}")
    F_ANNOTATION = 20; F_TITLE = 24
    def set_chart_layout(fig, *a, **k): return fig

# ── 共用 UI 元件（與 Week 03 完全相同的 import 方式）──────────────────
from utils.week_components import (
    apply_week_css, card as _card, section_header,
    render_copyright, render_teal_input_block
)
from utils.week_submit import render_ia_section
apply_week_css()

# 2. 登入防護
from utils.auth import require_login
require_login()

# 3. 後端資料庫
try:
    from utils.gsheets_db import save_score, check_has_submitted, verify_student, get_weekly_password, get_weekly_password_safe, get_saved_progress
except ImportError:
    def save_score(*a, **k): return False
    def check_has_submitted(*a, **k): return False
    def verify_student(*a, **k): return False, None
    def get_weekly_password(*a, **k): return "888888"
    def get_weekly_password_safe(*a, **k): return "888888"   # ★ v2.5
    def get_saved_progress(*a, **k): return None

# 4. Sidebar
try:
    from utils.sidebar import render_sidebar
    _sidebar_ok = True
except Exception:
    _sidebar_ok = False

# ── 常數 ──────────────────────────────────────────────────────────────
F_GLOBAL = 18; F_AXIS = 20; F_TICK = 18

# ── Session State ──────────────────────────────────────────────────────
if "w4_locked" not in st.session_state:
    st.session_state.w4_locked = False
if _sidebar_ok:
    render_sidebar(current_page="Week 04")

# ── 互動追蹤（9 項，對應課本 3 節核心計算）──────────────────────────
TRACK_KEYS = {
    "t1_pmf":   False,   # §4.1 PMF 形狀探索滑桿
    "t1_add":   False,   # §4.1 加法法則逐步計算（課本表4.1）
    "t1_quiz":  False,   # §4.1 隨堂測驗
    "t2_ev":    False,   # §4.2 期望值滑桿（感受極端值拉偏）
    "t2_calc":  False,   # §4.2 逐步計算 E(X)/Var(X)/SD(X)（課本習題4.12）
    "t2_quiz":  False,   # §4.2 隨堂測驗
    "t3_binom": False,   # §4.3 二項分配滑桿探索
    "t3_aql":   False,   # §4.3 AQL 逐步計算（課本例題4.4）
    "t3_quiz":  False,   # §4.3 隨堂測驗
}
GROUPS_IA = {
    "Tab1 §4.1 隨機變數與機率分配": ["t1_pmf", "t1_add", "t1_quiz"],
    "Tab2 §4.2 期望值與變異數":     ["t2_ev",  "t2_calc","t2_quiz"],
    "Tab3 §4.3 二項分配":           ["t3_binom","t3_aql","t3_quiz"],
}
LABELS_IA = {
    "t1_pmf":  "PMF 形狀探索",   "t1_add": "加法法則計算", "t1_quiz": "隨堂測驗",
    "t2_ev":   "期望值滑桿",     "t2_calc":"逐步計算",      "t2_quiz": "隨堂測驗",
    "t3_binom":"二項分配探索",   "t3_aql": "AQL 品管計算",  "t3_quiz": "隨堂測驗",
}
for k in TRACK_KEYS:
    if "w4_track_" + k not in st.session_state:
        st.session_state["w4_track_" + k] = False

# 滑桿初始值（判斷是否真正互動）
_SLIDER_INIT = {"w4_lam": 2.0, "w4_p4": 0.02, "w4_n_bin": 10, "w4_pi_bin": 0.10}
for _sk in _SLIDER_INIT:
    if "w4_sld_moved_" + _sk not in st.session_state:
        st.session_state["w4_sld_moved_" + _sk] = False

# 逐步計算步驟旗標
for _sf in ["w4_ev_s1","w4_ev_s2","w4_ev_s3","w4_ev_s4",
            "w4_aql_s1","w4_aql_s2","w4_aql_s3"]:
    if _sf not in st.session_state:
        st.session_state[_sf] = False

def mark_done(key):
    st.session_state["w4_track_" + key] = True

def check_slider(slider_key, track_key):
    cur = st.session_state.get(slider_key, None)
    ini = _SLIDER_INIT.get(slider_key, None)
    if cur is not None and cur != ini:
        if not st.session_state.get("w4_sld_moved_" + slider_key, False):
            st.session_state["w4_sld_moved_" + slider_key] = True
        mark_done(track_key)

def count_done():
    return sum(1 for k in TRACK_KEYS if st.session_state.get("w4_track_" + k, False))

# ══════════════════════════════════════════════════════════════════════
#  HERO（與 Week 03 完全相同的 HTML 結構）
# ══════════════════════════════════════════════════════════════════════
st.markdown('''
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
    border-radius:16px;padding:28px 40px 24px 40px;
    margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">
    <div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;margin:0 0 8px 0;line-height:1.25;">
        Week 04｜離散機率分配 🎲
    </div>
    <div style="color:#94a3b8;font-size:1.05rem;margin:0 0 10px 0;">
        Discrete Probability Distributions &middot; Chapter 4
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.22);
        border-radius:20px;padding:5px 16px;">
        <span style="color:#93c5fd;font-size:0.82rem;">📖</span>
        <span style="color:#e2e8f0;font-size:0.82rem;font-weight:600;">課本第 4 章 · §4.1–4.3</span>
        <span style="color:#64748b;font-size:0.78rem;">｜《工程統計》Lapin 著</span>
    </div>
</div>
''', unsafe_allow_html=True)

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
        <span style="color:white;font-weight:700;font-size:1.0rem;">📌 本週學習路線</span>
    </div>
    <div style="background:#f0fdfa;padding:13px 18px;color:#134e4a;font-size:1.05rem;line-height:1.7;">
        請依序點選下方各小節的標籤，完成理論閱讀與互動實驗。
        完成所有標籤後，再挑戰最後的<strong>整合性總測驗</strong>！<br>
        <span style="font-size:0.92rem;color:#0f766e;">
            §4.1 隨機變數與機率分配 → §4.2 期望值與變異數 → §4.3 二項分配與AQL品管
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">🎲 1. 本週核心理論與互動實驗室</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標籤，完成理論閱讀與互動實驗</p>',
            unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🎯 4.1 隨機變數與機率分配",
    "⚖️ 4.2 期望值與變異數",
    "🎲 4.3 二項分配",
])

# ══════════════════════════════════════════════════════════════════════
#  Tab 1：§4.1 隨機變數與機率分配
# ══════════════════════════════════════════════════════════════════════
with tab1:
    # ── 名詞卡 1：隨機變數 ────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 10px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 隨機變數 Random Variable</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            將隨機試驗的<b>樣本空間</b>映射到<b>實數軸</b>上的函數。大寫 <b>X</b> 表示隨機變數，小寫 <b>x</b> 為其特定取值。<br>
            ▸ 例：抽驗 5 個電子組件，令 X = 瑕疵品個數，X 可取 0,1,2,3,4,5（課本圖4.1）
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # 隨機變數映射 SVG
    st.markdown(
        '<svg viewBox="0 0 640 88" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;max-width:640px;display:block;margin:4px auto 8px auto;">'
        '<rect width="640" height="88" fill="#f8fafc" rx="10"/>'
        '<rect x="10" y="8" width="162" height="72" rx="8" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.5"/>'
        '<text x="91" y="25" text-anchor="middle" font-size="11" font-weight="700" fill="#0369a1">樣本空間 S（32種）</text>'
        '<text x="91" y="43" text-anchor="middle" font-size="10" fill="#0c4a6e">GGGGG → 0個瑕疵</text>'
        '<text x="91" y="57" text-anchor="middle" font-size="10" fill="#0c4a6e">GGGGD → 1個瑕疵</text>'
        '<text x="91" y="71" text-anchor="middle" font-size="10" fill="#0c4a6e">……（共32種）</text>'
        '<line x1="174" y1="44" x2="238" y2="44" stroke="#475569" stroke-width="2"/>'
        '<polygon points="235,39 245,44 235,49" fill="#475569"/>'
        '<text x="210" y="36" text-anchor="middle" font-size="11" font-weight="700" fill="#7c3aed">X = f(s)</text>'
        '<rect x="248" y="8" width="382" height="72" rx="8" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>'
        '<text x="439" y="25" text-anchor="middle" font-size="11" font-weight="700" fill="#7c3aed">實數取值 x（瑕疵品個數）</text>'
        '<line x1="268" y1="62" x2="618" y2="62" stroke="#7c3aed" stroke-width="2"/>'
        '<text x="274" y="76" font-size="11" fill="#4c1d95">0</text>'
        '<text x="334" y="76" font-size="11" fill="#4c1d95">1</text>'
        '<text x="394" y="76" font-size="11" fill="#4c1d95">2</text>'
        '<text x="454" y="76" font-size="11" fill="#4c1d95">3</text>'
        '<text x="514" y="76" font-size="11" fill="#4c1d95">4</text>'
        '<text x="574" y="76" font-size="11" fill="#4c1d95">5</text>'
        '<circle cx="276" cy="62" r="4" fill="#22c55e"/><circle cx="336" cy="62" r="4" fill="#22c55e"/>'
        '<circle cx="396" cy="62" r="4" fill="#22c55e"/><circle cx="456" cy="62" r="4" fill="#22c55e"/>'
        '<circle cx="516" cy="62" r="4" fill="#22c55e"/><circle cx="576" cy="62" r="4" fill="#22c55e"/>'
        '</svg>',
        unsafe_allow_html=True
    )
    st.caption("圖：X 將32種樣本點映射到 {0,1,2,3,4,5}（對應課本圖4.1）")

    # ── 名詞卡 2：間斷型 PMF ─────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:10px 0 6px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 間斷型 Discrete + 機率集結函數 PMF</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            可能取值<b>有限或可數</b>（0,1,2,…）。機率函數稱為 PMF：<b>p(y) = P[Y = y]</b><br>
            ▸ 性質①：<b>0 ≤ p(y) ≤ 1</b>（機率不可為負）<br>
            ▸ 性質②：<b>Σ p(y) = 1</b>（全機率公理，Y 必定取某個值）<br>
            ▸ 例：設備月故障數 Y = 0,1,2,… 的機率如課本表4.1所示
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # PMF 圖解 SVG
    st.markdown(
        '<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;max-width:640px;display:block;margin:0 auto 6px auto;">'
        '<rect width="640" height="200" fill="#f0fdfa" rx="10" stroke="#99f6e4" stroke-width="1.2"/>'
        # 標題
        '<text x="320" y="20" text-anchor="middle" font-size="12" font-weight="700" fill="#0f766e">'
        'PMF 圖解：每條長條的高度 = 該取值的機率 p(y)</text>'
        # 橫軸
        '<line x1="60" y1="160" x2="590" y2="160" stroke="#475569" stroke-width="2"/>'
        '<polygon points="588,155 598,160 588,165" fill="#475569"/>'
        '<text x="602" y="164" font-size="11" fill="#475569">y</text>'
        # 縱軸
        '<line x1="60" y1="30" x2="60" y2="160" stroke="#475569" stroke-width="2"/>'
        '<polygon points="55,32 60,22 65,32" fill="#475569"/>'
        '<text x="28" y="26" font-size="11" fill="#475569">p(y)</text>'
        # 縱軸刻度
        '<line x1="56" y1="120" x2="64" y2="120" stroke="#475569" stroke-width="1"/>'
        '<text x="44" y="124" font-size="10" fill="#475569">0.2</text>'
        '<line x1="56" y1="80" x2="64" y2="80" stroke="#475569" stroke-width="1"/>'
        '<text x="44" y="84" font-size="10" fill="#475569">0.4</text>'
        # 長條（設備故障數 λ=2 的 PMF 示意，高度按比例縮放）
        # p(0)=0.135→54px, p(1)=0.271→108px, p(2)=0.271→108px, p(3)=0.180→72px, p(4)=0.090→36px, p(5)=0.036→14px
        '<rect x="90"  y="106" width="44" height="54"  rx="3" fill="#3b82f6" opacity="0.85"/>'
        '<rect x="175" y="52"  width="44" height="108" rx="3" fill="#22c55e" opacity="0.90"/>'
        '<rect x="260" y="52"  width="44" height="108" rx="3" fill="#22c55e" opacity="0.90"/>'
        '<rect x="345" y="88"  width="44" height="72"  rx="3" fill="#3b82f6" opacity="0.85"/>'
        '<rect x="430" y="124" width="44" height="36"  rx="3" fill="#3b82f6" opacity="0.85"/>'
        '<rect x="515" y="146" width="44" height="14"  rx="3" fill="#3b82f6" opacity="0.85"/>'
        # 橫軸標籤
        '<text x="112"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">0</text>'
        '<text x="197"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">1</text>'
        '<text x="282"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">2</text>'
        '<text x="367"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">3</text>'
        '<text x="452"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">4</text>'
        '<text x="537"  y="176" text-anchor="middle" font-size="12" fill="#134e4a" font-weight="600">5</text>'
        # 長條頂部機率標示
        '<text x="112"  y="100" text-anchor="middle" font-size="10" fill="#0369a1">0.135</text>'
        '<text x="197"  y="46"  text-anchor="middle" font-size="10" fill="#166534" font-weight="700">0.271</text>'
        '<text x="282"  y="46"  text-anchor="middle" font-size="10" fill="#166534" font-weight="700">0.271</text>'
        '<text x="367"  y="82"  text-anchor="middle" font-size="10" fill="#0369a1">0.180</text>'
        '<text x="452"  y="118" text-anchor="middle" font-size="10" fill="#0369a1">0.090</text>'
        '<text x="537"  y="140" text-anchor="middle" font-size="10" fill="#0369a1">…</text>'
        # 說明箭頭：長條高度 = p(y)
        '<line x1="197" y1="52" x2="197" y2="160" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,3"/>'
        '<text x="210" y="108" font-size="11" font-weight="700" fill="#d97706">← 高度</text>'
        '<text x="210" y="122" font-size="11" fill="#d97706">= p(1)</text>'
        '<text x="210" y="136" font-size="11" fill="#d97706">= 0.271</text>'
        # 全機率=1 說明
        '<rect x="390" y="25" width="238" height="30" rx="6" fill="rgba(15,118,110,0.1)" stroke="#0f766e" stroke-width="1"/>'
        '<text x="509" y="35" text-anchor="middle" font-size="11" font-weight="700" fill="#0f766e">'
        'Σ p(y) = 0.135+0.271+0.271+… = 1.000</text>'
        '<text x="509" y="49" text-anchor="middle" font-size="10" fill="#0f766e">所有長條面積加總恆等於 1</text>'
        # 橫軸說明
        '<text x="320" y="194" text-anchor="middle" font-size="11" fill="#475569">'
        '故障數 y（只能取整數：0, 1, 2, 3, …）</text>'
        '</svg>',
        unsafe_allow_html=True
    )
    st.caption("PMF 圖：每個整數取值對應一條長條，長條高度即為該取值的機率值 p(y)；所有長條加總 = 1")

    # ── 名詞卡 3：連續型 PDF ─────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:14px 0 6px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 連續型 Continuous + 機率密度函數 PDF</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            可能取值<b>無限且不可數</b>（如強度、尺寸）。用 PDF：<b>P[a≤X≤b] = ∫ₐᵇ f(x)dx</b>（曲線下面積）<br>
            ▸ <b>f(x) ≥ 0</b>，總面積 <b>∫f(x)dx = 1</b><br>
            ▸ 關鍵差異：單一點的機率為 0；只有「區間」才有意義的機率（課本例題4.1 磁帶裂紋）
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # PDF 圖解：用 Plotly 畫曲線 + 區間陰影，確保陰影完全在曲線下方
    _x_all  = np.linspace(0, 300, 500)
    _f_all  = 0.01 * np.exp(-0.01 * _x_all)   # 課本例題4.1 f(x)=0.01e^{-0.01x}
    _a, _b  = 50, 150                           # 示意區間 [a, b]
    _mask   = (_x_all >= _a) & (_x_all <= _b)
    _x_sh   = _x_all[_mask]
    _f_sh   = _f_all[_mask]

    fig_pdf_demo = go.Figure()
    # ① 陰影區間（fill='tozeroy' 自動填到 x 軸，完全在曲線下）
    fig_pdf_demo.add_trace(go.Scatter(
        x=_x_sh, y=_f_sh,
        fill='tozeroy', fillcolor='rgba(59,130,246,0.25)',
        line=dict(color='rgba(0,0,0,0)', width=0),
        showlegend=False, hoverinfo='skip'
    ))
    # ② 完整曲線（畫在陰影上方）
    fig_pdf_demo.add_trace(go.Scatter(
        x=_x_all, y=_f_all,
        mode='lines', line=dict(color='#0f766e', width=3),
        name='f(x) = 0.01e⁻⁰·⁰¹ˣ',
        hovertemplate='x=%{x:.1f} 吋<br>f(x)=%{y:.5f}<extra></extra>'
    ))
    # ③ a、b 垂直虛線
    fig_pdf_demo.add_vline(
        x=_a, line_dash='dash', line_color='#ef4444', line_width=1.5,
        annotation_text='a=50吋', annotation_position='top left',
        annotation_font_color='#ef4444', annotation_font_size=13
    )
    fig_pdf_demo.add_vline(
        x=_b, line_dash='dash', line_color='#ef4444', line_width=1.5,
        annotation_text='b=150吋', annotation_position='top right',
        annotation_font_color='#ef4444', annotation_font_size=13
    )
    # ④ 面積標示
    _p_ab = round(float(np.trapezoid(_f_sh, _x_sh)), 4)
    fig_pdf_demo.add_annotation(
        x=100, y=0.004,
        text=f'<b>面積 = P[50≤X≤150]<br>= {_p_ab}</b>',
        showarrow=False,
        font=dict(size=13, color='#1e40af'),
        bgcolor='rgba(239,246,255,0.85)',
        bordercolor='#3b82f6', borderwidth=1
    )
    # ⑤ 單點機率=0 說明
    fig_pdf_demo.add_annotation(
        x=20, y=0.007,
        text='P[X=某點] = 0<br>（線段無面積）',
        showarrow=True, ax=0, ay=-30,
        arrowhead=2, arrowcolor='#94a3b8',
        font=dict(size=11, color='#64748b'),
        bgcolor='rgba(248,250,252,0.9)'
    )
    fig_pdf_demo.update_layout(
        height=340,
        showlegend=False,
        title=dict(
            text='PDF 圖解：f(x)=0.01e⁻⁰·⁰¹ˣ（課本例題4.1 磁帶裂紋間距）',
            font=dict(size=14, color='#0f766e')
        ),
        xaxis=dict(title='裂紋間距 x（吋）', range=[0, 300],
                   tickfont=dict(size=12)),
        yaxis=dict(title='f(x)', tickfont=dict(size=12)),
        margin=dict(t=50, b=40, l=60, r=20),
        plot_bgcolor='#f0fdfa', paper_bgcolor='#f0fdfa'
    )
    st.plotly_chart(fig_pdf_demo, use_container_width=True)
    st.caption(
        f"藍色陰影面積 = P[50≤X≤150] = {_p_ab}，"
        "陰影完全在曲線下方。"
        "曲線本身不是機率（f(x) 可以 > 1）；單一點無面積，所以單點機率恆為 0。"
    )

    st.markdown('''
    <div class="why-box">
    <b>🔧 為什麼工程師需要隨機變數？</b><br>
    製程的瑕疵數、設備的故障次數、磁帶裂紋的間距……工程測量結果永遠帶有不確定性。
    隨機變數提供數學語言，讓工程師把「可能的結果」轉換成「機率數字」，
    進而計算風險、設定品管標準、決定備料數量。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 PMF 兩大性質</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                0 ≤ p(y) ≤ 1（每個機率非負）<br>
                Σ p(y) = 1（全機率公理）<br>
                <small style="color:#7c3aed;font-size:0.85rem;">長條高度=機率，加總恆=1</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 PDF 兩大性質</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                f(x) ≥ 0（密度函數恆非負）<br>
                P[a≤X≤b] = ∫ₐᵇ f(x)dx<br>
                <small style="color:#7c3aed;font-size:0.85rem;">面積=機率，總面積=1</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：PMF 形狀探索（課本表4.1 卜瓦松分配）──────────
    with st.expander("🛠️ 展開實驗室 A：PMF 形狀探索——感受 λ 如何改變分配（課本表4.1）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>透過調整月平均故障數 λ，直觀感受 PMF 峰值如何移動，以及高風險機率如何急速上升。<br>
                <b>你會發現：</b>λ=2 就是課本表4.1的設備故障分配；λ 越大，「0次故障」的機率越低。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：設備月故障數監控（課本表4.1）</b><br>
        某工廠設備的月故障次數 Y 服從卜瓦松分配，月平均故障數為 λ。
        課本表4.1 使用 λ=2。請拖動滑桿，觀察 PMF 的形狀如何隨 λ 改變。
        </div>
        ''', unsafe_allow_html=True)

        col_reset1a, _ = st.columns([1, 5])
        with col_reset1a:
            if st.button("🔄 復原課本預設值（λ=2）", key="w4_reset_lam"):
                if "w4_lam" in st.session_state:
                    del st.session_state["w4_lam"]
                st.rerun()

        lam = st.slider(
            "月平均故障數 λ — 拖動滑桿感受 PMF 峰值如何移動",
            0.5, 8.0, 2.0, 0.5, key="w4_lam"
        )
        check_slider("w4_lam", "t1_pmf")

        y_r  = list(range(16))
        pmf_v = [exp(-lam) * (lam**y) / factorial(y) for y in y_r]
        p_zero = pmf_v[0]
        p_risk = sum(pmf_v[5:])  # P[Y>=5]

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("月平均故障 λ", f"{lam:.1f} 次")
        with col2: st.metric("E(Y) = λ", f"{lam:.1f}")
        with col3: st.metric("P[Y=0]（零故障）", f"{p_zero:.4f}")
        with col4: st.metric("P[Y≥5]（高風險）", f"{p_risk:.4f}")

        bar_colors = ['#ef4444' if y >= 5 else '#22c55e' if y == round(lam) else '#3b82f6' for y in y_r]
        fig1a = go.Figure()
        fig1a.add_trace(go.Bar(
            x=y_r, y=pmf_v, marker_color=bar_colors,
            hovertemplate="故障數: %{x}<br>機率: %{y:.4f}<extra></extra>"
        ))
        fig1a.add_trace(go.Scatter(
            x=[lam], y=[pmf_v[min(round(lam), 15)]], mode="markers",
            marker=dict(color="#1e3a5f", size=14, symbol="triangle-down"),
            name="E(Y)=λ",
            hovertemplate="E(Y)=λ=%{x:.1f}<extra></extra>"
        ))
        fig1a.add_vline(x=lam, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"E(Y)=λ={lam:.1f}",
                        annotation_font_size=F_ANNOTATION, annotation_font_color="#f59e0b")
        fig1a.add_vline(x=4.5, line_dash="dot", line_color="#ef4444",
                        annotation_text="高風險界限(Y≥5)",
                        annotation_position="top left",
                        annotation_font_size=F_ANNOTATION, annotation_font_color="#ef4444")
        set_chart_layout(fig1a, f"設備月故障數 PMF（λ={lam:.1f}）", "故障數 y", "機率 p(y)")
        fig1a.update_layout(height=420, showlegend=False)
        fig1a.update_xaxes(range=[-0.5, 15.5])
        st.plotly_chart(fig1a, use_container_width=True)

        if lam == 2.0:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本表4.1 對照（λ=2）",
                  "p(0)=0.1353, p(1)=0.2707, p(2)=0.2707, p(3)=0.1804, p(4)=0.0902……與圖表完全吻合！"
                  "E(Y) = λ = 2 次/月。")
        elif p_risk > 0.10:
            _card("#ef4444","#fef2f2","#991b1b","⚠️ 高風險警示",
                  "P[Y≥5]=" + str(round(p_risk,3)) + " > 10%，頻繁故障將影響生產。建議強化預防性維護，目標將 λ 降至 2.0 以下。")
        else:
            _card("#22c55e","#f0fdf4","#166534","✅ 故障風險可控",
                  "P[Y≥5]=" + str(round(p_risk,4)) + " ≤ 10%。目前故障頻率在可接受範圍，維持現有保養週期即可。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. PMF 峰值位置 = 期望值 E(Y) = λ，λ 越大峰值越往右移。<br>
        2. Σ p(y) = 1 不論 λ 為何值均成立——這是 PMF 的不變性質。<br>
        3. 工程含義：降低 λ（改善維護品質）等同直接降低高故障月份的比例。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：PMF 加法法則逐步計算（課本表4.1）────────────────
    with st.expander("🛠️ 展開實驗室 B：PMF 加法法則逐步計算（課本表4.1）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>在 PMF 表上練習「至多」與「至少」的機率計算，熟練加法法則與餘事件法則。<br>
                <b>你會發現：</b>「至少 1 次故障」用餘事件法則（1−P(0)）比逐項加總快得多，這是工程師的計算捷徑。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本表4.1：設備月故障數的機率分配（λ=2）**
        請根據下表，分兩步計算「至多 2 次故障」與「至少 1 次故障」的機率。
        """)

        fail_data = [
            {"故障數 y": 0, "機率 p(y)": 0.1353},
            {"故障數 y": 1, "機率 p(y)": 0.2707},
            {"故障數 y": 2, "機率 p(y)": 0.2707},
            {"故障數 y": 3, "機率 p(y)": 0.1804},
            {"故障數 y": 4, "機率 p(y)": 0.0902},
            {"故障數 y": 5, "機率 p(y)": 0.0361},
            {"故障數 y": 6, "機率 p(y)": 0.0121},
            {"故障數 y": "7+","機率 p(y)": 0.0045},
        ]
        _card("#0369a1","#e0f2fe","#0c4a6e","📋 步驟一：確認各事件互斥",
              "故障 0 次、1 次、2 次……這些事件兩兩互斥（不可能同時故障1次又故障2次），故可直接使用加法法則相加。")
        st.dataframe(pd.DataFrame(fail_data), use_container_width=True, hide_index=True)

        true_at_most2  = 0.1353 + 0.2707 + 0.2707
        true_at_least1 = round(1 - 0.1353, 4)

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：用加法法則計算 P(Y≤2) = P(0)+P(1)+P(2)",
              "請填入計算結果（保留 4 位小數）：")
        atmost2_input = st.number_input(
            "P(Y≤2) = P(0)+P(1)+P(2) = ?",
            value=0.0, step=0.001, format="%.4f", key="w4_step2_atmost2"
        )
        step2_done = False
        if atmost2_input != 0.0:
            if abs(atmost2_input - true_at_most2) < 0.002:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                      "P(Y≤2) = 0.1353+0.2707+0.2707 = <b>0.6767</b>。設備在 67.7% 的月份故障次數不超過 2 次。")
                step2_done = True
                mark_done("t1_add")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算一次",
                      "P(0)=0.1353, P(1)=0.2707, P(2)=0.2707，三個值相加（你填了 " + str(round(atmost2_input,4)) + "）。")

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：用餘事件法則計算 P(Y≥1) = 1−P(Y=0)",
              "提示：「至少 1 次故障」的對立事件是「0 次故障」，請填入計算結果（保留 4 位小數）：")
        atleast1_input = st.number_input(
            "P(Y≥1) = 1 − P(0) = 1 − 0.1353 = ?",
            value=0.0, step=0.001, format="%.4f", key="w4_step3_atleast1"
        )
        step3_done = False
        if atleast1_input != 0.0:
            if abs(atleast1_input - true_at_least1) < 0.002:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟三正確！",
                      "P(Y≥1) = 1 − 0.1353 = <b>0.8647</b>。有 86.5% 的月份至少發生 1 次故障——設備確實需要定期維護！")
                step3_done = True
                mark_done("t1_add")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再確認","1 − 0.1353 = ?（你填了 " + str(round(atleast1_input,4)) + "）")

        if step2_done and step3_done:
            st.markdown("---")
            _card("#7c3aed","#f5f3ff","#4c1d95","🎉 兩個步驟都完成了！",
                  "加法法則（互斥事件直接加總）+ 餘事件法則（1 減去餘事件），是計算 PMF 機率的兩大工具。"
                  "「至少1次」用餘事件法則比加 p(1)+p(2)+…+p(7+) 少算許多項。")
            ks = [str(d["故障數 y"]) for d in fail_data]
            ps = [d["機率 p(y)"] for d in fail_data]
            fig1b = go.Figure(go.Bar(
                x=ks, y=ps,
                marker_color=["#22c55e" if i<=2 else "#ef4444" for i in range(len(ks))],
                text=[f"{p:.4f}" for p in ps], textposition="outside", textfont=dict(size=13),
                hovertemplate="故障數: %{x}<br>機率: %{y:.4f}<extra></extra>",
            ))
            set_chart_layout(fig1b, "設備月故障數 PMF（綠=P(Y≤2)，紅=高故障區）", "故障數 y", "機率 p(y)")
            fig1b.update_layout(height=420, yaxis=dict(range=[0, 0.35]))
            st.plotly_chart(fig1b, use_container_width=True)
            col_s1, col_s2 = st.columns(2)
            with col_s1: st.metric("P(Y≤2)", f"{true_at_most2:.4f}", "加法法則")
            with col_s2: st.metric("P(Y≥1)", f"{true_at_least1:.4f}", "餘事件法則")

        if st.button("🔄 重新開始實驗室 B", key="w4_reset_add"):
            for k in ["w4_step2_atmost2","w4_step3_atleast1"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §4.1 ─────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§4.1 隨機變數與機率分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q1 = st.radio(
        "📍 **題目：某製程每批次出現瑕疵品數 Y 的機率分配如下：p(0)=0.50, p(1)=0.30, p(2)=0.15, p(3)=0.05。"
        "P(Y≥2) = ？**",
        ["請選擇...", "A. 0.20", "B. 0.50", "C. 0.80", "D. 0.15"],
        key="w4_q1_radio"
    )
    if st.button("送出答案", key="w4_q1_btn"):
        if q1 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q1:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "P(Y≥2) = P(2)+P(3) = 0.15+0.05 = 0.20（加法法則，互斥事件直接加總）。"
                  "或用餘事件法則：1 − P(0) − P(1) = 1 − 0.50 − 0.30 = 0.20。")
            mark_done("t1_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "P(Y≥2) = P(2)+P(3)，將符合條件的各互斥事件機率加總。或用餘事件：1−P(Y<2)=1−P(0)−P(1)。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 2：§4.2 期望值與變異數
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 10px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 期望值 E(X)——機率分配的重心</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>E(X) = Σ x · p(x)</b>　所有可能值的機率加權平均，代表機率分配的「重心」（集中趨勢）<br>
            ▸ 線性特性：<b>E(a+bX) = a+b·E(X)</b>，E(c) = c<br>
            ▸ 注意：期望值是長期大量重複試驗的均值，並非單次試驗必定出現的值
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:10px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 變異數 Var(X) 與標準差 SD(X)——離散程度</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>Var(X) = E(X²) − [E(X)]²</b>　衡量機率分配的「離散程度」（風險波動大小）<br>
            <b>SD(X) = √Var(X)</b>　單位與 X 相同，比變異數更直覺<br>
            ▸ <b>Var(a+bX) = b²·Var(X)</b>，Var(c) = 0<br>
            ▸ 工程含義：Var 越大 → 波動越劇烈 → 設計時需要更高的安全係數或備援容量
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 為什麼工程師需要期望值與變異數？</b><br>
    E(X) 告訴你「平均要準備多少資源」（如：每月備用 2 組零件）；
    Var(X) 告訴你「這個平均值有多可信」（高 Var = 高波動 = 保守備料）。
    兩個數字加在一起，才能做出合理的工程決策。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 期望值</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                E(X) = Σ x · p(x)<br>
                E(a+bX) = a + b·E(X)<br>
                <small style="color:#7c3aed;font-size:0.85rem;">加權平均 = 機率分配重心</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 變異數與標準差</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                Var(X) = E(X²) − [E(X)]²<br>
                SD(X) = √Var(X)<br>
                <small style="color:#7c3aed;font-size:0.85rem;">Var 越大 = 波動越難預測</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：感受期望值被極端值拉偏（課本習題4.12）────────
    with st.expander("🛠️ 展開實驗室 A：感受期望值被尖峰車流「拉偏」的現象（課本習題4.12）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>親眼看到「少數極端高值雖然機率低，卻能顯著拉高期望值」的現象。<br>
                <b>你會發現：</b>調高 P[X=4] 後，E(X) 上升、SD(X) 也跟著變大，代表車流更難預測——這就是為何工程師要同時看 E 和 Var。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境（課本習題4.12）：收費站每分鐘到達車輛數 X</b><br>
        原始分配：p(0)=0.37, p(1)=0.37, p(2)=0.18, p(3)=0.06, p(4)=0.02。課本計算 E(X)=0.99。<br>
        請調整「X=4 輛（尖峰時刻）」的機率，觀察 E(X) 如何被拉偏、SD(X) 如何上升。
        </div>
        ''', unsafe_allow_html=True)

        col_reset2a, _ = st.columns([1, 5])
        with col_reset2a:
            if st.button("🔄 復原課本預設值（P[X=4]=0.02）", key="w4_reset_p4"):
                if "w4_p4" in st.session_state:
                    del st.session_state["w4_p4"]
                st.rerun()

        p4 = st.slider(
            "P[X=4]（尖峰機率）— 拖動觀察 E(X) 如何上升",
            0.00, 0.20, 0.02, 0.01, key="w4_p4"
        )
        check_slider("w4_p4", "t2_ev")

        base = [0.37, 0.37, 0.18, 0.06]
        px = [b/sum(base)*(1.0-p4) for b in base] + [p4]
        ex_a  = sum(i*px[i] for i in range(5))
        ex2_a = sum(i**2*px[i] for i in range(5))
        var_a = ex2_a - ex_a**2
        sd_a  = var_a**0.5

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("P[X=4]（尖峰機率）", f"{p4:.2f}")
        with col2: st.metric("E(X)", f"{ex_a:.4f} 輛/分",
                              delta=f"{(ex_a-0.99):+.4f} vs 課本0.99")
        with col3: st.metric("Var(X)", f"{var_a:.4f}")
        with col4: st.metric("SD(X)", f"{sd_a:.4f} 輛")

        fig2a = go.Figure()
        fig2a.add_trace(go.Bar(
            x=[0,1,2,3,4], y=px,
            marker_color=['#ef4444' if i==4 else '#3b82f6' for i in range(5)],
            hovertemplate="車輛數: %{x}<br>機率: %{y:.4f}<extra></extra>"
        ))
        fig2a.add_trace(go.Scatter(
            x=[ex_a], y=[max(px)*0.6], mode="markers",
            marker=dict(color="#1e3a5f", size=14, symbol="triangle-down"),
            name="E(X)", hovertemplate="E(X)=%{x:.4f}<extra></extra>"
        ))
        fig2a.add_vline(x=ex_a, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"E(X)={ex_a:.3f}",
                        annotation_font_size=F_ANNOTATION, annotation_font_color="#f59e0b")
        fig2a.add_vline(x=0.99, line_dash="dot", line_color="#94a3b8",
                        annotation_text="課本E(X)=0.99",
                        annotation_position="top left",
                        annotation_font_size=F_ANNOTATION, annotation_font_color="#94a3b8")
        set_chart_layout(fig2a, "收費站到達車輛數機率分配（紅色=調整的尖峰）", "每分鐘到達車輛數 x", "機率 p(x)")
        fig2a.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig2a, use_container_width=True)

        if p4 == 0.02:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本習題4.12 對照",
                  "E(X) = 0×0.37+1×0.37+2×0.18+3×0.06+4×0.02 = 0.99 輛/分（與圖表對照一致）。")
        elif p4 >= 0.10:
            _card("#ef4444","#fef2f2","#991b1b","⚠️ 尖峰壓力升高",
                  "E(X)=" + str(round(ex_a,4)) + " 輛/分，SD=" + str(round(sd_a,4)) +
                  "。尖峰車流顯著拉高均值與標準差，需要增設備援車道或彈性排班。")
        else:
            _card("#22c55e","#f0fdf4","#166534","✅ 車流相對穩定",
                  "E(X)=" + str(round(ex_a,4)) + " 輛/分，SD=" + str(round(sd_a,4)) +
                  "。當前服務窗口可應付，但仍需注意 SD 的波動。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. 即使 P[X=4] 只從 0.02 上升到 0.10，E(X) 的增幅可能超過 10%——極端值的影響遠超過機率本身。<br>
        2. Var(X) 與 SD(X) 同步上升，代表車流預測難度增加——光看平均值不夠，還要看波動。<br>
        3. 工程設計原則：容量設計至少要達到 E(X) + 2·SD(X) 的水準，才能應付大多數情況。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：逐步計算 E(X)、Var(X)、SD(X)（課本習題4.12）──
    with st.expander("🛠️ 展開實驗室 B：逐步計算 E(X)、Var(X)、SD(X)——課本習題4.12 完整手算", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>一步步手算 E(X) → E(X²) → Var(X) → SD(X)，理解每個公式的數學結構。<br>
                <b>你會發現：</b>Var(X) = E(X²) − [E(X)]² 比逐項計算 Σ(x−E)²p(x) 更有效率，是工程師常用的計算捷徑。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本習題4.12：收費站每分鐘到達車輛數 X 的機率分配**
        """)
        st.dataframe(pd.DataFrame({
            "x（車輛數）": [0, 1, 2, 3, 4],
            "p(x)（機率）": [0.37, 0.37, 0.18, 0.06, 0.02]
        }), use_container_width=True, hide_index=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：計算 E(X) = Σ x·p(x)（保留 2 位小數）","")
        s1 = st.number_input("E(X) = ?", 0.0, 5.0, 0.0, 0.01, key="w4_s1_val")
        if st.button("✔ 確認步驟一", key="w4_s1_btn"):
            if abs(s1-0.99) < 0.02:
                st.session_state["w4_ev_s1"] = True
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟一正確！E(X) = 0.99",
                      "計算：0×0.37 + 1×0.37 + 2×0.18 + 3×0.06 + 4×0.02 = 0+0.37+0.36+0.18+0.08 = 0.99 輛/分")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                      "E(X) = Σx·p(x)，逐項相乘後加總。提示：結果約 1.0 輛/分。")

        if st.session_state["w4_ev_s1"]:
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算 E(X²) = Σ x²·p(x)（保留 2 位小數）","")
            s2 = st.number_input("E(X²) = ?", 0.0, 10.0, 0.0, 0.01, key="w4_s2_val")
            if st.button("✔ 確認步驟二", key="w4_s2_btn"):
                if abs(s2-1.95) < 0.02:
                    st.session_state["w4_ev_s2"] = True
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！E(X²) = 1.95",
                          "計算：0²×0.37 + 1²×0.37 + 2²×0.18 + 3²×0.06 + 4²×0.02 = 0+0.37+0.72+0.54+0.32 = 1.95")
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                          "E(X²) = Σx²·p(x)，注意是 x 的平方再乘機率。提示：結果約 1.95。")

        if st.session_state["w4_ev_s2"]:
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：Var(X) = E(X²) − [E(X)]²（保留 4 位小數）","")
            s3 = st.number_input("Var(X) = ?", 0.0, 5.0, 0.0, 0.0001, format="%.4f", key="w4_s3_val")
            if st.button("✔ 確認步驟三", key="w4_s3_btn"):
                if abs(s3-0.9699) < 0.005:
                    st.session_state["w4_ev_s3"] = True
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟三正確！Var(X) = 0.9699",
                          "計算：Var(X) = 1.95 − (0.99)² = 1.95 − 0.9801 = 0.9699 輛²")
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                          "Var(X) = E(X²) − [E(X)]² = 1.95 − 0.99²，先算 0.99² = 0.9801，再相減。")

        if st.session_state["w4_ev_s3"]:
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟四：SD(X) = √Var(X)（保留 4 位小數）","")
            s4 = st.number_input("SD(X) = ?", 0.0, 5.0, 0.0, 0.0001, format="%.4f", key="w4_s4_val")
            if st.button("✔ 確認步驟四", key="w4_s4_btn"):
                if abs(s4-0.9848) < 0.005:
                    st.session_state["w4_ev_s4"] = True
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟四正確！SD(X) = 0.9848",
                          "計算：SD(X) = √0.9699 ≈ 0.9848 輛/分")
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                          "SD(X) = √Var(X) = √0.9699 ≈ 0.9848，保留四位小數。")

        if st.session_state["w4_ev_s4"]:
            mark_done("t2_calc")
            st.markdown("---")
            _card("#7c3aed","#f5f3ff","#4c1d95","🎉 四個步驟全部完成！完整結果",
                  "E(X)=0.99 輛/分，SD(X)=0.9848 ≈ E(X)。"
                  "波動幅度與均值相當，設計服務窗口時建議容量至少 E(X)+2·SD(X) ≈ 2.97 輛/分，才能應付大多數時段。")
            st.dataframe(pd.DataFrame({
                "統計量":   ["E(X)","E(X²)","Var(X)","SD(X)"],
                "公式":     ["Σx·p(x)","Σx²·p(x)","E(X²)−[E(X)]²","√Var(X)"],
                "數值":     ["0.99 輛/分","1.95","0.9699","0.9848 輛/分"],
                "工程意義": ["平均每分鐘約1輛到達","計算Var的中間量","車流波動量（越大越難預測）","設計備援容量的依據"]
            }), use_container_width=True, hide_index=True)

        if st.button("🔄 重新開始實驗室 B（期望值計算）", key="w4_reset_ev"):
            for sk in ["w4_ev_s1","w4_ev_s2","w4_ev_s3","w4_ev_s4"]:
                st.session_state[sk] = False
            for k in ["w4_s1_val","w4_s2_val","w4_s3_val","w4_s4_val"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §4.2 ─────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§4.2 期望值與變異數</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q2 = st.radio(
        "📍 **題目（習題4.12）：收費站分配 p(0)=0.37, p(1)=0.37, p(2)=0.18, p(3)=0.06, p(4)=0.02，E(X) = ？**",
        ["請選擇...", "A. E(X) = 0.87", "B. E(X) = 1.20",
         "C. E(X) = 0.99 輛/分", "D. E(X) = 1.95"],
        key="w4_q2_radio"
    )
    if st.button("送出答案", key="w4_q2_btn"):
        if q2 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "C." in q2:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "E(X) = 0×0.37+1×0.37+2×0.18+3×0.06+4×0.02 = 0.99 輛/分。"
                  "注意 D 選項 1.95 是 E(X²)，不是 E(X)——這是常見的混淆！")
            mark_done("t2_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "E(X) = Σx·p(x)，每個 x 乘以其機率後加總。D 選項 1.95 是 E(X²)（x 的平方加權），不是 E(X)。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 3：§4.3 二項分配
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 10px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 柏努利過程 Bernoulli Process</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            連續重複試驗，滿足以下<b>三個條件</b>，就構成柏努利過程：<br>
            ▸ 條件①　<b>二元結果</b>：每次試驗只有「成功（π）」或「失敗（1−π）」兩種結果<br>
            ▸ 條件②　<b>固定機率</b>：每次試驗的成功機率 π 保持不變<br>
            ▸ 條件③　<b>統計獨立</b>：各次試驗結果互不影響<br>
            ▸ 工程例：電路板抽驗（良品/瑕疵），焊接測試（通過/失敗），AQL 允收抽樣
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:10px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 二項分配公式 b(r; n, π)</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            在 n 次柏努利試驗中，恰好出現 r 次成功的機率：<br>
            <b>b(r; n, π) = C(n,r) · πʳ · (1−π)ⁿ⁻ʳ</b>　　r = 0,1,…,n<br>
            其中 <b>C(n,r) = n! / [r!·(n−r)!]</b>（組合數 = 從 n 次選 r 次成功的方法數）<br>
            ▸ <b>E(R) = nπ</b>（期望成功次數）；<b>Var(R) = nπ(1−π)</b><br>
            ▸ 累積機率 <b>B(r;n,π) = P[R≤r]</b>，可由課本附錄表A查得
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # 柏努利三假設 SVG
    st.markdown(
        '<svg viewBox="0 0 680 172" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;max-width:680px;display:block;margin:4px auto 10px auto;">'
        '<rect width="680" height="172" fill="#f8fafc" rx="12"/>'
        '<text x="340" y="19" text-anchor="middle" font-size="13" font-weight="800" fill="#1e3a5f">'
        '柏努利過程三大假設 → 才能使用二項分配公式</text>'
        '<rect x="16" y="30" width="196" height="76" rx="10" fill="#e0f2fe" stroke="#0369a1" stroke-width="2"/>'
        '<text x="114" y="52" text-anchor="middle" font-size="12" font-weight="700" fill="#0369a1">假設①　二元結果</text>'
        '<text x="114" y="70" text-anchor="middle" font-size="11" fill="#0c4a6e">每次試驗只有兩種結果：</text>'
        '<text x="114" y="87" text-anchor="middle" font-size="11" fill="#0c4a6e">成功（π）或失敗（1−π）</text>'
        '<rect x="242" y="30" width="196" height="76" rx="10" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>'
        '<text x="340" y="52" text-anchor="middle" font-size="12" font-weight="700" fill="#166534">假設②　固定機率</text>'
        '<text x="340" y="70" text-anchor="middle" font-size="11" fill="#166534">每次試驗成功機率</text>'
        '<text x="340" y="87" text-anchor="middle" font-size="11" fill="#166534">π 保持不變</text>'
        '<rect x="468" y="30" width="196" height="76" rx="10" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2"/>'
        '<text x="566" y="52" text-anchor="middle" font-size="12" font-weight="700" fill="#4c1d95">假設③　統計獨立</text>'
        '<text x="566" y="70" text-anchor="middle" font-size="11" fill="#4c1d95">各次試驗結果</text>'
        '<text x="566" y="87" text-anchor="middle" font-size="11" fill="#4c1d95">互不影響</text>'
        '<line x1="114" y1="106" x2="310" y2="145" stroke="#94a3b8" stroke-width="1.8"/>'
        '<line x1="340" y1="106" x2="340" y2="145" stroke="#94a3b8" stroke-width="1.8"/>'
        '<line x1="566" y1="106" x2="370" y2="145" stroke="#94a3b8" stroke-width="1.8"/>'
        '<polygon points="308,140 312,152 318,140" fill="#94a3b8"/>'
        '<polygon points="338,140 342,152 346,140" fill="#94a3b8"/>'
        '<polygon points="368,140 372,152 376,140" fill="#94a3b8"/>'
        '<rect x="178" y="150" width="324" height="18" rx="7" fill="#1e3a5f"/>'
        '<text x="340" y="163" text-anchor="middle" font-size="12" font-weight="800" fill="white">'
        'b(r;n,π) = C(n,r) · πʳ · (1−π)ⁿ⁻ʳ</text>'
        '</svg>',
        unsafe_allow_html=True
    )
    st.caption("三假設缺任何一條，就不能直接套用二項分配公式（例如：不放回抽樣時 π 不固定，應改用超幾何分配）")

    st.markdown('''
    <div class="why-box">
    <b>🔧 工程場景：AQL 允收抽樣（課本例題4.4）</b><br>
    品管工程師每批抽取 n 件產品，製程瑕疵率為 π。
    利用二項分配計算「抽到 r 件瑕疵品的機率」，決定是否允收整批產品。
    這正是課本例題4.4「美軍餐飲設備 AQL=6.5%」的核心數學——品管工程師的日常計算。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 二項分配公式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                b(r;n,π) = C(n,r)·πʳ·(1−π)ⁿ⁻ʳ<br>
                C(n,r) = n! / [r!·(n−r)!]<br>
                <small style="color:#7c3aed;font-size:0.85rem;">組合數 = 從n次選r次的方法數</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 E(R)、Var(R) 與 B(r)</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:14px 16px;color:#4c1d95;font-size:0.97rem;line-height:1.85;">
                <b>R</b>：成功次數（隨機變數）<br>
                <b>E(R) = n·π</b>　← 期望成功次數<br>
                <b>Var(R) = n·π·(1−π)</b>　← 成功次數的波動量<br>
                <b>B(r) = P[R ≤ r]</b>　← 累積機率（成功次數不超過 r 的機率）<br>
                <small style="color:#7c3aed;font-size:0.84rem;">B(r) 可直接查課本附錄表A，不必逐項加總</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：二項分配滑桿探索──────────────────────────────
    with st.expander("🛠️ 展開實驗室 A：調整 n 與 π，觀察二項分配如何變化", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受 n 與 π 如何決定二項分配的「峰值位置」與「分佈寬度」。<br>
                <b>你會發現：</b>E(R)=nπ 就是峰值所在；n=5, π=0.10 正是課本表4.4 的汽車零件例子。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：電路板抽樣品管</b><br>
        品管工程師每批抽取 n 片電路板，製程瑕疵率為 π。
        調整 n 與 π，觀察各種瑕疵數出現的機率，以及 E(R)=nπ 如何代表「平均幾片瑕疵」。
        </div>
        ''', unsafe_allow_html=True)

        col_reset3a, _ = st.columns([1, 5])
        with col_reset3a:
            if st.button("🔄 復原課本預設值（n=5, π=0.10）", key="w4_reset_binom"):
                for k in ["w4_n_bin","w4_pi_bin"]:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()

        col_sl1, col_sl2 = st.columns(2)
        with col_sl1:
            n_b = st.slider("樣本數 n（每批抽取片數）", 5, 30, 10, 1, key="w4_n_bin")
            check_slider("w4_n_bin","t3_binom")
        with col_sl2:
            pi_b = st.slider("瑕疵率 π（每片不良機率）", 0.01, 0.50, 0.10, 0.01, key="w4_pi_bin")
            check_slider("w4_pi_bin","t3_binom")

        r_all = list(range(n_b+1))
        b_all = [comb(n_b,r)*(pi_b**r)*((1-pi_b)**(n_b-r)) for r in r_all]
        er_b  = n_b*pi_b
        vr_b  = n_b*pi_b*(1-pi_b)

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("E(R) = nπ", f"{er_b:.2f} 片")
        with col2: st.metric("Var(R) = nπ(1−π)", f"{vr_b:.3f}")
        with col3: st.metric("SD(R)", f"{vr_b**0.5:.3f} 片")
        peak_r = min(int(er_b), n_b)
        with col4: st.metric("b(最高峰 r)", f"{b_all[peak_r]:.4f}")

        bar_col3 = ['#22c55e' if r==peak_r else '#ef4444' if r > er_b+vr_b**0.5 else '#3b82f6' for r in r_all]
        fig3a = go.Figure()
        fig3a.add_trace(go.Bar(
            x=r_all, y=b_all, marker_color=bar_col3,
            hovertemplate="瑕疵數: %{x}<br>機率: %{y:.4f}<extra></extra>"
        ))
        fig3a.add_trace(go.Scatter(
            x=[er_b], y=[max(b_all)*0.6], mode="markers",
            marker=dict(color="#1e3a5f", size=14, symbol="triangle-down"),
            name="E(R)", hovertemplate="E(R)=%{x:.2f}<extra></extra>"
        ))
        fig3a.add_vline(x=er_b, line_dash="dash", line_color="#f59e0b",
                        annotation_text=f"E(R)={er_b:.1f}",
                        annotation_font_size=F_ANNOTATION, annotation_font_color="#f59e0b")
        set_chart_layout(fig3a, f"二項分配 b(r; n={n_b}, π={pi_b:.2f})", "瑕疵數 r", "機率 b(r;n,π)")
        fig3a.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig3a, use_container_width=True)
        st.caption("🟢 綠色=峰值（r最接近E(R)）；🔴 高風險區（超過E(R)+SD(R)）；▼ 三角形標記=E(R)")

        if abs(n_b-5)<=1 and abs(pi_b-0.10)<=0.01:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本表4.4 對照（n=5, π=0.10）",
                  "b(0)=0.59049, b(1)=0.32805, b(2)=0.07290, b(3)=0.00810——E(R)=0.5，峰值在 r=0，與圖表完全吻合！")
        else:
            _card("#f59e0b","#fffbeb","#92400e","📐 當前計算結果",
                  "E(R) = " + str(n_b) + "×" + str(round(pi_b,2)) + " = " + str(round(er_b,2)) + " 片；"
                  "Var(R) = " + str(n_b) + "×" + str(round(pi_b,2)) + "×" + str(round(1-pi_b,2)) + " = " + str(round(vr_b,3)) + "。"
                  "調回 n=5, π=0.10 可對照課本表4.4。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. E(R) = nπ 直接給出峰值位置——知道 n 和 π，不用計算就能知道最可能出現幾個瑕疵。<br>
        2. n 越大，分佈越趨近鐘形（對稱）；π=0.5 時 Var(R) 最大，分佈最寬。<br>
        3. 品管工程師用 E(R) 估算每批次預期瑕疵數，用 Var(R) 決定允收標準的寬鬆程度。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：AQL 允收機率逐步計算（課本例題4.4）────────────
    with st.expander("🛠️ 展開實驗室 B：AQL 品管——允收機率逐步計算（課本例題4.4）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>逐步計算 b(0)、b(1)、b(2)，加總得到 AQL 允收機率 P[R≤2]。<br>
                <b>你會發現：</b>即使品質差（π=0.20），允收機率仍超過 50%——說明此 AQL 規定存在明顯漏洞，工程師需在兩型誤差間取得平衡。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本例題4.4：美軍餐飲設備 AQL 品管規定**
        從 n=13 件餐飲設備中抽驗，不潔件數 ≤ 2 則允收（AQL=6.5%，π=0.065）。
        **請逐步計算允收機率 P[R≤2] = b(0) + b(1) + b(2)。**
        """)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：b(0; 13, 0.065) = C(13,0)·(0.065)⁰·(0.935)¹³ = (0.935)¹³",
              "C(13,0)=1，(0.065)⁰=1，只需計算 (0.935)¹³。請填入結果（保留 4 位小數）：")
        b0_in = st.number_input("b(0) = ?", 0.0, 1.0, 0.0, 0.0001, format="%.4f", key="w4_aql_s1_val")
        if st.button("✔ 確認步驟一", key="w4_aql_s1_btn"):
            b0_true = (0.935)**13
            if abs(b0_in - b0_true) < 0.002:
                st.session_state["w4_aql_s1"] = True
                _card("#22c55e","#f0fdf4","#166534",
                      "✅ 步驟一正確！b(0) = " + str(round(b0_true,4)),
                      "(0.935)¹³ ≈ 0.4174，代表13件全部合格的機率。")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                      "(0.935)¹³，使用計算機逐步相乘。提示：結果約 0.417。")

        if st.session_state["w4_aql_s1"]:
            b0_true = (0.935)**13
            _card("#0369a1","#e0f2fe","#0c4a6e",
                  "✏️ 步驟二：b(1; 13, 0.065) = C(13,1)·(0.065)¹·(0.935)¹² = 13·0.065·(0.935)¹²",
                  "C(13,1)=13。請填入結果（保留 4 位小數）：")
            b1_in = st.number_input("b(1) = ?", 0.0, 1.0, 0.0, 0.0001, format="%.4f", key="w4_aql_s2_val")
            if st.button("✔ 確認步驟二", key="w4_aql_s2_btn"):
                b1_true = 13 * 0.065 * (0.935)**12
                if abs(b1_in - b1_true) < 0.003:
                    st.session_state["w4_aql_s2"] = True
                    _card("#22c55e","#f0fdf4","#166534",
                          "✅ 步驟二正確！b(1) = " + str(round(b1_true,4)),
                          "13×0.065×(0.935)¹² ≈ 0.3772，代表恰好 1 件不潔的機率。")
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                          "13×0.065×(0.935)¹²，結果約 " + str(round(13*0.065*(0.935)**12,4)) + "。")

        if st.session_state["w4_aql_s2"]:
            b0_true = (0.935)**13
            b1_true = 13 * 0.065 * (0.935)**12
            _card("#0369a1","#e0f2fe","#0c4a6e",
                  "✏️ 步驟三：b(2; 13, 0.065) = C(13,2)·(0.065)²·(0.935)¹¹",
                  "C(13,2) = 13×12/(2×1) = 78。請填入結果（保留 4 位小數）：")
            b2_in = st.number_input("b(2) = ?", 0.0, 1.0, 0.0, 0.0001, format="%.4f", key="w4_aql_s3_val")
            if st.button("✔ 確認步驟三（並計算 P[R≤2]）", key="w4_aql_s3_btn"):
                b2_true = comb(13,2) * (0.065**2) * (0.935**11)
                if abs(b2_in - b2_true) < 0.003:
                    st.session_state["w4_aql_s3"] = True
                    _card("#22c55e","#f0fdf4","#166534",
                          "✅ 步驟三正確！b(2) = " + str(round(b2_true,4)),
                          "78×(0.065)²×(0.935)¹¹ ≈ 0.1573，代表恰好 2 件不潔的機率。")
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                          "78×(0.065)²×(0.935)¹¹，結果約 " + str(round(b2_true,4)) + "。")

        if st.session_state["w4_aql_s3"]:
            b0_true = (0.935)**13
            b1_true = 13 * 0.065 * (0.935)**12
            b2_true = comb(13,2) * (0.065**2) * (0.935**11)
            total   = b0_true + b1_true + b2_true
            mark_done("t3_aql")
            st.markdown("---")
            _card("#7c3aed","#f5f3ff","#4c1d95","🎉 三步驟全部完成！課本例題4.4 答案確認",
                  "P[R≤2] = " + str(round(b0_true,4)) + " + " + str(round(b1_true,4)) + " + " +
                  str(round(b2_true,4)) + " = " + str(round(total,4)) +
                  "（課本答案：0.9519）")
            st.dataframe(pd.DataFrame({
                "項目": ["b(0)","b(1)","b(2)","P[R≤2] 允收機率"],
                "計算式": ["(0.935)¹³","13×0.065×(0.935)¹²","78×(0.065)²×(0.935)¹¹","b(0)+b(1)+b(2)"],
                "數值": [str(round(b0_true,4)), str(round(b1_true,4)), str(round(b2_true,4)), str(round(total,4))],
                "品管意義": ["13件全部合格","恰好1件不合格","恰好2件不合格","符合AQL規定的允收機率"]
            }), use_container_width=True, hide_index=True)

            # 不同π值下允收機率比較圖
            pi_vals = [0.04, 0.065, 0.10, 0.15, 0.20]
            acc_vals = [sum(comb(13,r)*(pi_v**r)*((1-pi_v)**(13-r)) for r in range(3)) for pi_v in pi_vals]
            acc_col  = ['#22c55e' if p>0.90 else '#f59e0b' if p>0.50 else '#ef4444' for p in acc_vals]
            fig3b = go.Figure(go.Bar(
                x=[f"π={p}" for p in pi_vals], y=acc_vals,
                marker_color=acc_col,
                text=[f"{p:.4f}" for p in acc_vals],
                textposition="outside", textfont=dict(size=13),
                hovertemplate="瑕疵率: %{x}<br>允收機率: %{y:.4f}<extra></extra>"
            ))
            fig3b.add_hline(y=0.95, line_dash="dash", line_color="#22c55e",
                            annotation_text="95% 安全線",
                            annotation_font_size=F_ANNOTATION, annotation_font_color="#22c55e")
            fig3b.add_hline(y=0.50, line_dash="dot", line_color="#ef4444",
                            annotation_text="50% 警戒線",
                            annotation_font_size=F_ANNOTATION, annotation_font_color="#ef4444")
            set_chart_layout(fig3b, "不同瑕疵率下的允收機率（n=13，允收≤2件）", "瑕疵率 π", "允收機率 P[R≤2]")
            fig3b.update_layout(height=420, yaxis=dict(range=[0, 1.1]))
            st.plotly_chart(fig3b, use_container_width=True)

            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本例題4.4 討論",
                  "π=0.20（20%不潔）時，允收機率仍高達 ~50%——此 AQL 規定太寬鬆，劣質品有一半機率被放行。"
                  "工程師需在「型I誤差（好品被拒）」與「型II誤差（劣品放行）」之間取得平衡，這是第 8 章統計檢定的核心議題。")

            st.markdown('''
            <div class="discover-box">
            💡 <b>實驗結論</b>：<br>
            1. 品質好（π=0.065 符合AQL）時，允收機率高達 95.2%——此標準對供應商算合理。<br>
            2. 品質差（π=0.20）時，允收機率仍有 50%——代表此抽驗方案放行劣品的風險很高。<br>
            3. 工程決策：若要讓 π=0.20 的允收機率降到 5% 以下，需要擴大抽樣數 n 或降低允收門檻。
            </div>
            ''', unsafe_allow_html=True)

        if st.button("🔄 重新開始實驗室 B（AQL計算）", key="w4_reset_aql"):
            for sk in ["w4_aql_s1","w4_aql_s2","w4_aql_s3"]:
                st.session_state[sk] = False
            for k in ["w4_aql_s1_val","w4_aql_s2_val","w4_aql_s3_val"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §4.3 ─────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§4.3 二項分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q3 = st.radio(
        "📍 **題目（課本表4.4）：汽車零件生產線（n=5，π=0.10），恰好出現 2 件不良品的機率 b(2;5,0.10) = ？**",
        ["請選擇...",
         "A. b(2;5,0.10) = 0.0729",
         "B. b(2;5,0.10) = 0.3281",
         "C. b(2;5,0.10) = 0.0081",
         "D. b(2;5,0.10) = 0.5905"],
        key="w4_q3_radio"
    )
    if st.button("送出答案", key="w4_q3_btn"):
        if q3 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q3:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "b(2;5,0.10) = C(5,2)×(0.10)²×(0.90)³ = 10×0.01×0.729 = 0.0729。"
                  "C(5,2)=10 是5次中選2次不良品位置的組合數。D選項0.5905是b(0)（全良品的機率）。（課本表4.4）")
            mark_done("t3_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "b(r;n,π)=C(n,r)·πʳ·(1−π)ⁿ⁻ʳ。代入：C(5,2)=10，(0.10)²=0.01，(0.90)³=0.729，三者相乘=0.0729。"
                  "D選項0.5905是b(0)，代表5件全部良品的機率。")


# ══════════════════════════════════════════════════════════════════════
#  ██  SECTION 2a：互動參與進度記錄  ██
# ══════════════════════════════════════════════════════════════════════
st.divider()
section_header("📝 2a. 本週互動參與記錄")
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">完成互動實驗後，輸入學號與驗證碼，將參與記錄送出給老師。</p>', unsafe_allow_html=True)

done_count  = count_done()
total_count = len(TRACK_KEYS)
pct_done    = int(done_count / total_count * 100)

render_ia_section({
    "wp":         "w4",
    "sheet_name": "Week 04 互動",
    "track_keys": TRACK_KEYS,
    "groups":     GROUPS_IA,
    "labels":     LABELS_IA,
    "done_count": done_count,
    "total_count":total_count,
    "pct":        pct_done,
})

# ══════════════════════════════════════════════════════════════════════
#  ██  SECTION 2b：整合性總測驗  ██
# ══════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📋 2b. 本週整合性總測驗</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">完成所有互動實驗後，輸入老師公布的解鎖密碼，開始作答並上傳成績。</p>',
            unsafe_allow_html=True)

real_password = get_weekly_password_safe("Week 04")
if not real_password:
    real_password = "888888"

_card("#475569","#f8fafc","#334155","🔒 測驗鎖定中",
      "請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。")
_col_pw, _col_btn = st.columns([5, 1])
with _col_pw:
    user_code = st.text_input("密碼", type="password", key="w4_unlock_code",
                               label_visibility="collapsed",
                               placeholder="🔑 請輸入 6 位數解鎖密碼…")
with _col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w4_unlock_btn")

if user_code != real_password:
    if user_code != "":
        _card("#ef4444","#fef2f2","#991b1b","❌ 密碼錯誤","請確認字母與數字是否正確！")
else:
    if "w4_locked" not in st.session_state:
        st.session_state.w4_locked = False
    _card("#22c55e","#f0fdf4","#166534","🔓 密碼正確！","測驗已解鎖，請完成以下題目後送出。")
    _card("#3b82f6","#eff6ff","#1e40af","📋 測驗說明",
          "4 題，每題 25 分，共 100 分。作答送出後即鎖定成績，請確實核對學號與驗證碼！")

    st.markdown(
        '<style>'
        '.st-key-w4_quiz_container > div:first-child {'
        '  border-radius:0 0 12px 12px !important;'
        '  border-top:none !important;'
        '  margin-top:-1px !important;'
        '}'
        '</style>'
        '<div style="'
        'background:linear-gradient(90deg,#0f766e 0%,#0d9488 100%);'
        'border-radius:12px 12px 0 0;'
        'padding:12px 20px 10px 20px;">'
        '<span style="color:white;font-weight:700;font-size:1.0rem;">📝 填寫身分資料</span>'
        '<div style="color:rgba(255,255,255,0.88);font-size:0.95rem;margin-top:5px;">'
        '請填寫學號、姓名與驗證碼，系統將驗證後鎖定成績。'
        '</div></div>',
        unsafe_allow_html=True)
    with st.container(border=True, key="w4_quiz_container"):
        c_id, c_name, c_code = st.columns(3)
        with c_id:   st_id    = st.text_input("📝 學號",   key="w4_quiz_id",   placeholder="請輸入學號")
        with c_name: st_name  = st.text_input("📝 姓名",   key="w4_quiz_name", placeholder="請輸入姓名")
        with c_code: st_vcode = st.text_input("🔑 驗證碼", key="w4_quiz_code", placeholder="個人驗證碼", type="password")

    with st.form("week4_unified_quiz"):
        st.markdown("---")
        q1f = st.radio(
            "**Q1（§4.1）：某生產線品管紀錄顯示，每批次不良品數 Y 的分配為 p(0)=0.60, p(1)=0.25, p(2)=0.10, p(3)=0.05。P(Y≤1) = ？**",
            ["請選擇...", "A. 0.25", "B. 0.60", "C. 0.85", "D. 0.15"],
            key="w4_qf1"
        )
        q2f = st.radio(
            "**Q2（§4.2）：某路口等候車輛數 X，p(0)=0.20, p(1)=0.50, p(2)=0.30，已知 E(X)=1.10、E(X²)=1.70。Var(X) = ？**",
            ["請選擇...", "A. Var(X) = 0.49", "B. Var(X) = 0.60",
             "C. Var(X) = 1.10", "D. Var(X) = 1.70"],
            key="w4_qf2"
        )
        q3f = st.radio(
            "**Q3（§4.3）：某電腦組裝線（n=4，π=0.20），恰好出現 1 件不良品的機率 b(1;4,0.20) = ？**",
            ["請選擇...", "A. 0.1638", "B. 0.4096", "C. 0.1536", "D. 0.0016"],
            key="w4_qf3"
        )
        q4f = st.radio(
            "**Q4（§4.3）：某製程 n=20，π=0.10，E(R) 與 Var(R) 各為何？**",
            ["請選擇...",
             "A. E(R)=2, Var(R)=2.0",
             "B. E(R)=1.8, Var(R)=2.0",
             "C. E(R)=2, Var(R)=0.9",
             "D. E(R)=2, Var(R)=1.8"],
            key="w4_qf4"
        )
        st.markdown("---")

        if st.form_submit_button("✅ 簽署並送出本週測驗",
                                  disabled=st.session_state.w4_locked):
            if st_id and st_name and st_vcode:
                is_valid, student_idx = verify_student(st_id, st_name, st_vcode)
                if not is_valid:
                    _card("#ef4444","#fef2f2","#991b1b","⛔ 身分驗證失敗",
                          "您輸入的學號、姓名或驗證碼有誤，請重新確認！")
                elif check_has_submitted(st_id, "Week 04"):
                    _card("#ef4444","#fef2f2","#991b1b","⛔ 拒絕送出",
                          "系統查詢到您已繳交過 Week 04 的測驗！請勿重複作答。")
                else:
                    score = 0
                    if q1f.startswith("C."): score += 25
                    if q2f.startswith("A."): score += 25
                    if q3f.startswith("B."): score += 25
                    if q4f.startswith("D."): score += 25
                    detail_str = ("Q1:"+q1f[:2]+",Q2:"+q2f[:2]+
                                  ",Q3:"+q3f[:2]+",Q4:"+q4f[:2])
                    success = save_score(student_idx, st_id, st_name,
                                         "Week 04", detail_str, score)
                    if success:
                        st.session_state.w4_locked = True
                        st.markdown(
                            '<div style="border-radius:12px;overflow:hidden;'
                            'box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">'
                            '<div style="background:#22c55e;padding:10px 18px;">'
                            '<span style="color:white;font-weight:700;font-size:1.0rem;">🎊 上傳成功！</span>'
                            '</div>'
                            '<div style="background:#f0fdf4;padding:14px 18px;color:#166534;">'
                            '<b>' + st_name + '</b>（' + st_id + '）驗證通過<br>'
                            '<span style="font-size:2.0rem;font-weight:900;color:#15803d;">'
                            + str(score) + '</span>'
                            '<span style="font-size:1.0rem;"> 分　成績已鎖定！</span>'
                            '</div></div>',
                            unsafe_allow_html=True
                        )
                        if score == 100:
                            st.balloons()
                            _card("#7c3aed","#f5f3ff","#4c1d95","🏆 滿分 100！",
                                  "PMF 加法法則、期望值計算、二項公式、AQL 品管——離散機率分配核心全數掌握！")
                        elif score >= 75:
                            _card("#3b82f6","#eff6ff","#1e40af","👍 表現不錯！",
                                  "建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。")
                        else:
                            _card("#f59e0b","#fffbeb","#92400e","📖 繼續加油！",
                                  "請回顧本週各節的概念說明與互動實驗，機率公式需要多練習！")

                        # ── 逐題對錯與解析（與 Week 03 完全相同結構）────────
                        _ANSWERS_W4 = {
                            "Q1": ("C. 0.85",
                                   "§4.1：P(Y≤1) = P(0)+P(1) = 0.60+0.25 = 0.85。互斥事件直接用加法法則相加；"
                                   "或用餘事件：1−P(2)−P(3) = 1−0.10−0.05 = 0.85。"
                                   "注意此題問的是「至多1件」，與練習題的「至少2件」方向相反，要特別留意。"),
                            "Q2": ("A. Var(X) = 0.49",
                                   "§4.2：Var(X) = E(X²)−[E(X)]² = 1.70−(1.10)² = 1.70−1.21 = 0.49。"
                                   "D選項1.70是E(X²)而非Var(X)——[E(X)]²必須從E(X²)中扣除，這是最常見的計算失誤。"),
                            "Q3": ("B. 0.4096",
                                   "§4.3：b(1;4,0.20)=C(4,1)×(0.20)¹×(0.80)³=4×0.20×0.512=0.4096。"
                                   "C(4,1)=4是4次中選1次不良品位置的組合數。"
                                   "A選項0.1638是b(2;4,0.20)，C選項0.1536是b(2;4,0.10)，D選項0.0016是(0.20)⁴。"),
                            "Q4": ("D. E(R)=2, Var(R)=1.8",
                                   "§4.3：E(R)=nπ=20×0.10=2；Var(R)=nπ(1-π)=20×0.10×0.90=1.8。"
                                   "Var必須乘以(1-π)，不等於E(R)本身——這是最常見的計算錯誤。"),
                        }
                        _student_ans_w4 = {"Q1": q1f, "Q2": q2f, "Q3": q3f, "Q4": q4f}
                        _rows_w4 = ""
                        for _qn, (_correct, _expl) in _ANSWERS_W4.items():
                            _stu    = _student_ans_w4[_qn]
                            _ok     = (_stu == _correct)
                            _icon   = "✅" if _ok else "❌"
                            _hbg    = "#15803d" if _ok else "#dc2626"
                            _bbg    = "#f0fdf4" if _ok else "#fef2f2"
                            _tc2    = "#166534" if _ok else "#991b1b"
                            _status = "答對" if _ok else "答錯"
                            _rows_w4 += (
                                f'<div style="border-radius:10px;overflow:hidden;'
                                f'border:1px solid #e2e8f0;margin:8px 0;">'
                                f'<div style="background:{_hbg};padding:8px 16px;">'
                                f'<span style="color:white;font-weight:700;">'
                                f'{_icon} {_qn}　{_status}</span></div>'
                                f'<div style="background:{_bbg};padding:12px 16px;'
                                f'color:{_tc2};font-size:0.97rem;line-height:1.7;">'
                                f'<b>您的答案：</b>{_stu}<br>'
                                + ('' if _ok else f'<b>正確答案：</b>{_correct}<br>')
                                + f'<b>解析：</b>{_expl}'
                                f'</div></div>'
                            )
                        st.markdown(
                            '<div style="background:#1e3a5f;border-radius:12px;'
                            'padding:10px 18px;margin:14px 0 6px 0;">'
                            '<span style="color:white;font-weight:800;font-size:1.05rem;">'
                            '📋 本次作答詳細解析</span></div>'
                            + _rows_w4,
                            unsafe_allow_html=True
                        )
                        # ─────────────────────────────────────────────────────
            else:
                _card("#f59e0b","#fffbeb","#92400e","⚠️ 資料不完整",
                      "請完整填寫學號、姓名與驗證碼再送出表單。")

    if st.session_state.w4_locked:
        _card("#475569","#f8fafc","#334155","🔒 測驗已鎖定",
              "系統已安全登錄您的成績，如有疑問請聯繫授課教師。")


# ══════════════════════════════════════════════════════════════════════
#  底部速查卡（與 Week 03 完全相同的 HTML 結構）
# ══════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("📚 本週核心概念速查卡（考前複習用）", expanded=False):
    _cards = [
        ("#0f766e","#f0fdfa","#134e4a","📌 §4.1 隨機變數與機率分配",
         ["隨機變數：樣本空間→實數的映射函數",
          "間斷型：可數，用 PMF p(y)=P[Y=y]",
          "連續型：不可數，用 PDF f(x)≥0",
          "PMF：0≤p(y)≤1 且 Σp(y)=1",
          "PDF：P[a≤X≤b]=∫f(x)dx，面積=機率"]),
        ("#7c3aed","#f5f3ff","#4c1d95","📐 §4.2 期望值與變異數",
         ["E(X)=Σx·p(x)（機率加權均值）",
          "Var(X)=E(X²)−[E(X)]²（離散程度）",
          "SD(X)=√Var(X)（與X同單位）",
          "E(a+bX)=a+bE(X)",
          "Var(a+bX)=b²Var(X)"]),
        ("#0369a1","#e0f2fe","#0c4a6e","🎲 §4.3 二項分配",
         ["柏努利：二元結果＋固定π＋獨立",
          "b(r;n,π)=C(n,r)·πʳ·(1-π)ⁿ⁻ʳ",
          "C(n,r)=n!/[r!(n-r)!]（組合數）",
          "E(R)=nπ；Var(R)=nπ(1-π)",
          "B(r)=P[R≤r]，查課本附錄表A"]),
    ]
    _cols = st.columns(3)
    for _i, (_hc, _bc, _tc, _title, _items) in enumerate(_cards):
        with _cols[_i % 3]:
            _ihtml = "".join(
                '<li style="margin:4px 0;color:' + _tc + ';font-size:0.92rem;">' + it + '</li>'
                for it in _items
            )
            st.markdown(
                '<div style="border-radius:12px;overflow:hidden;'
                'box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin-bottom:14px;">'
                '<div style="background:' + _hc + ';padding:9px 16px;">'
                '<span style="color:white;font-weight:800;font-size:0.95rem;">' + _title + '</span></div>'
                '<div style="background:' + _bc + ';padding:11px 16px;">'
                '<ul style="margin:0;padding-left:16px;">' + _ihtml + '</ul></div></div>',
                unsafe_allow_html=True
            )

# ── 版權 badge ───────────────────────────────────────────────────────
render_copyright()
