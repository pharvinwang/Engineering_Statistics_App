# 檔案位置： D:\Engineering_Statistics_App\pages\03_Week_03.py
import streamlit as st
import pandas as pd
import numpy as np
import math

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

# ── 共用 UI 元件（week_components + week_submit）──────────────────
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
    from utils.gsheets_db import save_score, check_has_submitted, verify_student, get_weekly_password, get_saved_progress
except ImportError:
    def save_score(*a, **k): return False
    def check_has_submitted(*a, **k): return False
    def verify_student(*a, **k): return False, None
    def get_weekly_password(*a, **k): return "888888"
    def get_saved_progress(*a, **k): return None

# 4. Sidebar
try:
    from utils.sidebar import render_sidebar
    _sidebar_ok = True
except Exception:
    _sidebar_ok = False

# ── 常數 ──────────────────────────────────────────────────────────────
F_GLOBAL = 18; F_AXIS = 20; F_TICK = 18

# ── Session State 初始化 ──────────────────────────────────────────────
if "w3_locked" not in st.session_state:
    st.session_state.w3_locked = False

if _sidebar_ok:
    render_sidebar(current_page="Week 03")

# ── 互動追蹤 key 清單（Section 2a 用）────────────────────────────────
TRACK_KEYS = {
    "t1_prob":   False,   # Tab1 基本機率滑桿（需移動才算）
    "t1_add":    False,   # Tab1 加法法則逐步計算（完成才算）
    "t1_quiz":   False,   # Tab1 隨堂測驗（答對才算）
    "t2_mult":   False,   # Tab2 乘法法則滑桿（需移動才算）
    "t2_tree":   False,   # Tab2 機率樹互動（完成才算）
    "t2_quiz":   False,   # Tab2 隨堂測驗（答對才算）
    "t3_cond":   False,   # Tab3 條件機率逐步計算（完成才算）
    "t3_quiz":   False,   # Tab3 隨堂測驗（答對才算）
    "t4_tree":   False,   # Tab4 機率樹狀圖互動（完成才算）
    "t4_quiz":   False,   # Tab4 隨堂測驗（答對才算）
    "t5_series": False,   # Tab5 串聯可靠度滑桿（需移動才算）
    "t5_parallel":False,  # Tab5 並聯可靠度滑桿（需移動才算）
    "t5_design": False,   # Tab5 升級vs並聯設計挑戰滑桿（需移動才算）
    "t5_quiz":   False,   # Tab5 隨堂測驗（答對才算）
}
# ── 互動參與送出：分組與標籤（傳給 render_ia_section）────────────
GROUPS_IA = {
    "Tab1 §3.1 基本概念":  ["t1_prob", "t1_add", "t1_quiz"],
    "Tab2 §3.2 複合事件":  ["t2_mult", "t2_tree", "t2_quiz"],
    "Tab3 §3.3 條件機率":  ["t3_cond", "t3_quiz"],
    "Tab4 §3.4 機率樹":    ["t4_tree", "t4_quiz"],
    "Tab5 §3.5 系統可靠度": ["t5_series", "t5_parallel", "t5_design", "t5_quiz"],
}
LABELS_IA = {
    "t1_prob": "基本機率滑桿", "t1_add": "加法法則計算", "t1_quiz": "隨堂測驗",
    "t2_mult": "乘法法則滑桿", "t2_tree": "例題驗算",    "t2_quiz": "隨堂測驗",
    "t3_cond": "條件機率計算", "t3_quiz": "隨堂測驗",
    "t4_tree": "機率樹互動",   "t4_quiz": "隨堂測驗",
    "t5_series": "串聯設計器", "t5_parallel": "並聯設計器",
    "t5_design": "升級vs並聯挑戰", "t5_quiz": "隨堂測驗",
}

for k in TRACK_KEYS:
    if "w3_track_" + k not in st.session_state:
        st.session_state["w3_track_" + k] = False

# 滑桿初始值記錄（偵測是否真正移動過）
_SLIDER_INIT = {
    "w3_defect_rate": 5,
    "w3_mission_n": 5,
    "w3_r1": 90, "w3_r2": 80, "w3_r3": 95,
    "w3_p1": 40, "w3_p2": 50, "w3_p3": 60,
    "w3_r2_upgrade": 0.95, "w3_n_redundant": 2,
}
for _sk in _SLIDER_INIT:
    if "w3_sld_moved_" + _sk not in st.session_state:
        st.session_state["w3_sld_moved_" + _sk] = False

def mark_done(key):
    st.session_state["w3_track_" + key] = True

def check_slider(slider_key, track_key):
    current_val = st.session_state.get(slider_key, None)
    init_val    = _SLIDER_INIT.get(slider_key, None)
    if current_val is not None and current_val != init_val:
        if not st.session_state.get("w3_sld_moved_" + slider_key, False):
            st.session_state["w3_sld_moved_" + slider_key] = True
        mark_done(track_key)

def count_done():
    return sum(1 for k in TRACK_KEYS if st.session_state.get("w3_track_" + k, False))

# ══════════════════════════════════════════════════════════════════════
#  HERO 卡片
# ══════════════════════════════════════════════════════════════════════
st.markdown('''
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
    border-radius:16px;padding:28px 40px 24px 40px;
    margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">
    <div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;margin:0 0 8px 0;line-height:1.25;">
        Week 03｜機率與系統可靠度 🎲
    </div>
    <div style="color:#94a3b8;font-size:1.05rem;margin:0 0 10px 0;">
        Probability &amp; System Reliability · Chapter 3
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.22);
        border-radius:20px;padding:5px 16px;">
        <span style="color:#93c5fd;font-size:0.82rem;">📖</span>
        <span style="color:#e2e8f0;font-size:0.82rem;font-weight:600;">課本第 3 章 · §3.1–3.5</span>
        <span style="color:#64748b;font-size:0.78rem;">｜《工程統計》Lapin 著</span>
    </div>
</div>
''', unsafe_allow_html=True)

# ── 學習路線提示框 ────────────────────────────────────────────────────
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
        <span style="color:white;font-weight:700;font-size:1.0rem;">📌 本週學習路線</span>
    </div>
    <div style="background:#f0fdfa;padding:13px 18px;color:#134e4a;font-size:1.05rem;line-height:1.7;">
        請依序點選下方各小節的標籤，完成理論閱讀與互動實驗。
        完成所有標籤後，再挑戰最後的<strong>整合性總測驗</strong>！<br>
        <span style="font-size:0.92rem;color:#0f766e;">
            §3.1 基本概念 → §3.2 複合事件 → §3.3 條件機率 → §3.4 乘法法則與機率樹 → §3.5 系統可靠度
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

# ── Section 1 Header ──────────────────────────────────────────────────
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">🎲 1. 本週核心理論與互動實驗室</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標籤，完成理論閱讀與互動實驗</p>',
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 3.1 統計基本概念",
    "🔗 3.2 複合事件之機率",
    "🔍 3.3 條件機率",
    "🌳 3.4 乘法法則與機率樹",
    "⚙️ 3.5 系統可靠度",
])

# ══════════════════════════════════════════════════════════════════════
#  Tab 1：§3.1 統計基本概念
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§3.1 統計基本概念</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>隨機實驗 (Random Experiment)</b>：無法預先確定結果的觀測活動，例如檢驗一批螺栓是否合格。<br>
            <b>事件 (Event)</b>：隨機實驗的可能結果，例如「抽到合格品」。<br>
            <b>樣本空間 (Sample Space)</b>：所有可能結果的完整集合，例如 {合格, 不合格}。<br>
            <b>簡單事件 (Elementary Event)</b>：不可再細分、僅含一個樣本點的事件。<br><br>
            ▸ 機率定義：事件長期發生次數的比率，介於 0（不可能）到 1（必然）之間<br>
            ▸ 等機率條件下：P(事件) = 事件集大小 ÷ 樣本空間大小<br>
            ▸ <b>互斥事件</b>：兩事件不可能同時發生，P(A 且 B) = 0
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 為什麼工程師需要機率？</b><br>
    工程中充滿不確定性：焊接機器人的失誤率、混凝土強度是否達標、橋梁在設計壽命內不發生疲勞破壞的機率……
    機率提供了一套量化不確定性的語言，讓工程師能夠用數字表達「這個設計有多安全」，而不只是說「應該沒問題」。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 基本機率公式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(事件) = 事件集大小 / 樣本空間大小<br>
                <small style="color:#7c3aed;font-size:0.88rem;">適用於各簡單事件等機率發生的情況</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 餘事件公式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(A) = 1 − P(非 A)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">若餘事件機率已知，直接相減即可</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：品質檢驗機率模擬器 ────────────────────────────
    with st.expander("🛠️ 展開實驗室 A：品質檢驗機率模擬器（感受樣本空間與機率定義）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解機率是「事件集大小 ÷ 樣本空間大小」，並感受不同不良率下抽到合格品的機率變化。<br>
                <b>你會發現：</b>當母體不良率從 0% 升到 50% 時，P(合格) 從 1.0 線性下降——機率就是長期比率，不是感覺。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：螺栓生產線品質檢驗</b><br>
        某橋梁工程採用的高強度螺栓，生產批量為 1000 顆，品管員隨機抽取 1 顆進行拉力測試。
        若螺栓的不良率（強度不足的比例）可由你控制，請問：抽到合格品的機率是多少？
        </div>
        ''', unsafe_allow_html=True)

        defect_rate = st.slider(
            "設定螺栓不良率（%）— 拖動滑桿感受 P(合格) 如何隨不良率改變",
            0, 50, 5, 1, key="w3_defect_rate"
        )
        check_slider("w3_defect_rate", "t1_prob")

        n_total = 1000
        n_defect = int(n_total * defect_rate / 100)
        n_good   = n_total - n_defect
        p_good   = n_good / n_total
        p_defect = n_defect / n_total

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("樣本空間大小（N）", f"{n_total} 顆")
        with col2: st.metric("合格品數（事件集）", f"{n_good} 顆")
        with col3: st.metric("P(合格)", f"{p_good:.3f}")
        with col4: st.metric("P(不合格)", f"{p_defect:.3f}")

        # 視覺化：P(合格) 隨不良率變化的折線 + 當前點
        rates = list(range(0, 51, 1))
        p_goods = [(1000 - 1000*r/100)/1000 for r in rates]
        fig1a = go.Figure()
        fig1a.add_trace(go.Scatter(
            x=rates, y=p_goods, mode="lines",
            line=dict(color="#0f766e", width=3),
            name="P(合格)", hovertemplate="不良率: %{x}%<br>P(合格): %{y:.3f}<extra></extra>"
        ))
        fig1a.add_trace(go.Scatter(
            x=[defect_rate], y=[p_good], mode="markers",
            marker=dict(color="#ef4444", size=14, symbol="circle"),
            name="當前設定", hovertemplate="當前不良率: %{x}%<br>P(合格): %{y:.3f}<extra></extra>"
        ))
        fig1a.add_hline(y=0.5, line_dash="dash", line_color="#94a3b8",
                        annotation_text="P = 0.5", annotation_position="right",
                        annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig1a, "P(合格) 隨不良率的變化", "不良率（%）", "P(合格品)")
        fig1a.update_layout(height=420, yaxis=dict(range=[-0.05, 1.1]))
        st.plotly_chart(fig1a, use_container_width=True)

        if defect_rate == 0:
            _card("#22c55e","#f0fdf4","#166534","✅ 不良率 = 0%",
                  "P(合格) = 1.0，這是必然事件——樣本空間中所有螺栓都是合格品。")
        elif defect_rate == 50:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 不良率 = 50%",
                  "P(合格) = 0.5，如同公正硬幣——合格與不合格機率相等。")
        else:
            _card("#0369a1","#e0f2fe","#0c4a6e","📊 動態摘要",
                  "P(合格) = " + str(n_good) + " / " + str(n_total) + " = " + str(round(p_good, 3)) +
                  "；P(不合格) = " + str(n_defect) + " / " + str(n_total) + " = " + str(round(p_defect, 3)) +
                  "。兩者互為餘事件，相加恰好等於 1。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. 機率 = 事件集大小 ÷ 樣本空間大小，這是等機率條件下的定義。<br>
        2. P(合格) + P(不合格) = 1，因為兩者互為餘事件，且涵蓋了全部樣本空間。<br>
        3. 工程品管的核心目標：讓不良率趨近於 0，使 P(合格) 趨近於 1。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：逐步計算——加法法則（太空梭故障例題）─────────────
    with st.expander("🛠️ 展開實驗室 B：加法法則逐步計算（課本例題 3.1 重現）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>熟練互斥事件的加法法則與餘事件法則的計算流程。<br>
                <b>你會發現：</b>「至少 1 次」這類問題用餘事件法則反而最簡單——1 減去「零次」即可。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本場景（表 3.1）：動力室故障個數與機率**
        某太空站動力室依據歷史資料，故障個數 0～7+ 的機率已知如下表。
        **你能用加法法則計算「最多 3 個故障」與「至少 1 個故障」的機率嗎？**
        """)

        # 課本表 3.1 資料
        failure_data = [
            {"k": "0", "prob": 0.3679},
            {"k": "1", "prob": 0.3679},
            {"k": "2", "prob": 0.1839},
            {"k": "3", "prob": 0.0613},
            {"k": "4", "prob": 0.0153},
            {"k": "5", "prob": 0.0031},
            {"k": "6", "prob": 0.0005},
            {"k": "7+","prob": 0.0001},
        ]
        df_fail = pd.DataFrame(failure_data)
        df_fail.columns = ["故障數量 k", "機率 P(k)"]
        _card("#0369a1","#e0f2fe","#0c4a6e","📋 步驟一：觀察已知機率表",
              "以下各事件互斥（故障次數不可能同時是 0 也是 1），故可直接使用加法法則。")
        st.dataframe(df_fail, use_container_width=True, hide_index=True)

        true_at_most3 = 0.3679 + 0.3679 + 0.1839 + 0.0613
        true_zero     = 0.3679
        true_at_least1 = round(1 - true_zero, 4)

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算「最多 3 個故障」的機率",
              "提示：P(最多 3 個) = P(0) + P(1) + P(2) + P(3)，請填入計算結果（保留 4 位小數）：")

        atmost3_input = st.number_input(
            "P(最多 3 個故障) = P(0)+P(1)+P(2)+P(3) = ?",
            value=0.0, step=0.001, format="%.4f", key="w3_step2_atmost3"
        )
        step2_done = False
        if atmost3_input != 0.0:
            if abs(atmost3_input - true_at_most3) < 0.0015:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                      "P(最多 3 個) = 0.3679 + 0.3679 + 0.1839 + 0.0613 = <b>0.9810</b>。"
                      "這代表動力室幾乎有 98% 的機率，故障次數不超過 3 個。")
                step2_done = True
                mark_done("t1_add")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算一次",
                      "請將 P(0)=0.3679, P(1)=0.3679, P(2)=0.1839, P(3)=0.0613 四個值相加（你填了 " + str(round(atmost3_input, 4)) + "）。")

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：用餘事件法則計算「至少 1 個故障」",
              "提示：P(至少 1 個) = 1 − P(0 個故障)，請填入計算結果（保留 4 位小數）：")

        atleast1_input = st.number_input(
            "P(至少 1 個故障) = 1 − P(0) = 1 − 0.3679 = ?",
            value=0.0, step=0.001, format="%.4f", key="w3_step3_atleast1"
        )
        step3_done = False
        if atleast1_input != 0.0:
            if abs(atleast1_input - true_at_least1) < 0.0015:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟三正確！",
                      "P(至少 1 個) = 1 − 0.3679 = <b>0.6321</b>。"
                      "餘事件法則的精髓：若「直接算」很繁雜，先算「什麼都沒有」再用 1 來減。")
                step3_done = True
                mark_done("t1_add")
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再確認一次",
                      "1 − 0.3679 = ?（你填了 " + str(round(atleast1_input, 4)) + "）")

        if step2_done and step3_done:
            st.markdown("---")
            _card("#7c3aed","#f5f3ff","#4c1d95","🎉 兩個步驟都完成了！",
                  "加法法則（互斥事件相加）與餘事件法則（1 減去餘事件機率）是計算工程風險的兩大基本工具。")

            # 長條圖視覺化
            ks      = [d["k"] for d in failure_data]
            probs   = [d["prob"] for d in failure_data]
            colors  = ["#22c55e" if int(k.replace("+","")) <= 3 else "#ef4444"
                       for k in ks]
            fig1b = go.Figure(go.Bar(
                x=ks, y=probs,
                marker_color=colors,
                text=[f"{p:.4f}" for p in probs],
                textposition="outside",
                textfont=dict(size=13),
                hovertemplate="故障數: %{x}<br>機率: %{y:.4f}<extra></extra>",
            ))
            fig1b.add_hline(y=0.0, line_color="#94a3b8", line_width=1)
            set_chart_layout(fig1b, "動力室故障個數機率分佈（綠色 = 最多 3 個故障）",
                             "故障個數 k", "機率 P(k)")
            fig1b.update_layout(
                height=420,
                yaxis=dict(range=[0, 0.45]),
                margin=dict(t=60, b=40, l=50, r=20)
            )
            st.plotly_chart(fig1b, use_container_width=True)

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("P(最多 3 個故障)", f"{true_at_most3:.4f}", "加法法則")
            with col_s2:
                st.metric("P(至少 1 個故障)", f"{true_at_least1:.4f}", "餘事件法則")

        # 重置按鈕
        if st.button("🔄 重新開始實驗室 B", key="w3_reset_add"):
            for k in ["w3_step2_atmost3", "w3_step3_atleast1"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 ───────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§3.1 基本機率</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q1 = st.radio(
        "📍 **題目：某生產線一批 50 片磁片中，有 5 片磁軌損壞（F）、3 片磁片折損（B），其餘皆可使用。"
        "若隨機抽取 1 片，P(無法使用) = ？**",
        ["請選擇...", "A. 8/50 = 0.16", "B. 5/50 = 0.10", "C. 3/50 = 0.06", "D. 42/50 = 0.84"],
        key="w3_q1_radio"
    )
    if st.button("送出答案", key="w3_q1_btn"):
        if q1 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q1:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "無法使用 = F + B = 5 + 3 = 8 片；P(無法使用) = 8/50 = 0.16。"
                  "這就是加法法則應用在互斥事件的基本例子——損壞類型互斥，可直接相加。")
            mark_done("t1_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "無法使用的磁片包含兩種：磁軌損壞（F）與磁片折損（B），兩種皆無法使用，應合計計算事件集大小。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 2：§3.2 複合事件之機率
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§3.2 複合事件之機率</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>複合事件 (Compound Event)</b>：兩個或以上簡單事件的組合。<br>
            <b>聯集（或）A ∪ B</b>：A 或 B 至少有一個發生（含兩者皆發生）。<br>
            <b>交集（且）A ∩ B</b>：A 與 B 同時發生。<br>
            <b>統計獨立</b>：兩事件中，任一事件的發生不影響另一事件的機率。<br><br>
            ▸ <b>加法法則通式</b>：P(A 或 B) = P(A) + P(B) − P(A 且 B)<br>
            ▸ <b>互斥事件加法</b>：P(A 且 B) = 0，故 P(A 或 B) = P(A) + P(B)<br>
            ▸ <b>獨立事件乘法</b>：P(A 且 B) = P(A) × P(B)
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 工程中的複合事件</b><br>
    橋梁承受颱風（A）同時發生地震（B）——這是 A ∩ B 的情境。
    工程師需要評估「颱風或地震至少發生一個」的機率，這正是加法法則通式的用武之地。
    若颱風與地震統計獨立，P(A ∩ B) = P(A) × P(B)，可大幅簡化計算。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 加法法則通式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(A ∪ B) = P(A) + P(B) − P(A ∩ B)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">減去交集是為避免重複計算</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 獨立事件乘法法則</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(A ∩ B) = P(A) × P(B)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">僅適用於統計獨立事件</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：乘法法則——太空梭爆毀模擬器 ────────────────────
    with st.expander("🛠️ 展開實驗室 A：獨立事件乘法法則——太空梭爆毀機率模擬器", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>應用餘事件法則 + 獨立事件乘法法則，計算「至少發生 1 次爆毀」的機率。<br>
                <b>你會發現：</b>即使單次成功率 99.3%，累積多次後「至少失敗 1 次」的機率會快速累積——這就是為什麼工程師重視每一次任務的可靠度。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：課本例題 3.5（NASA 太空梭）</b><br>
        NASA 統計顯示太空梭每 145 次飛行中發生 1 次爆毀，即單次爆毀機率 = 1/145 ≈ 0.00690。
        若每次飛行成功與否互為獨立事件，請問在 n 次飛行中，至少發生 1 次爆毀的機率為何？<br>
        <b>公式</b>：P(至少 1 次爆毀) = 1 − P(全部成功) = 1 − (144/145)ⁿ
        </div>
        ''', unsafe_allow_html=True)

        mission_n = st.slider(
            "設定飛行任務次數 n — 拖動滑桿觀察累積風險如何隨次數上升",
            1, 200, 5, 1, key="w3_mission_n"
        )
        check_slider("w3_mission_n", "t2_mult")

        p_success_single = 144/145
        p_all_success    = p_success_single ** mission_n
        p_at_least_1     = 1 - p_all_success

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("飛行次數 n", f"{mission_n} 次")
        with col2: st.metric("P(全部成功)", f"{p_all_success:.4f}")
        with col3: st.metric("P(至少 1 次爆毀)", f"{p_at_least_1:.4f}")

        ns   = list(range(1, 201))
        vals = [round(1 - (144/145)**n, 4) for n in ns]
        fig2a = go.Figure()
        fig2a.add_trace(go.Scatter(
            x=ns, y=vals, mode="lines",
            line=dict(color="#ef4444", width=2.5),
            name="P(至少1次爆毀)", hovertemplate="n=%{x}<br>P=%{y:.4f}<extra></extra>"
        ))
        fig2a.add_trace(go.Scatter(
            x=[mission_n], y=[p_at_least_1], mode="markers",
            marker=dict(color="#1e3a5f", size=14),
            name="當前 n", hovertemplate="n=%{x}<br>P=%{y:.4f}<extra></extra>"
        ))
        # 標示課本四個例子
        for nb, label_text in [(2,"n=2"), (5,"n=5"), (10,"n=10"), (50,"n=50")]:
            fig2a.add_vline(x=nb, line_dash="dot", line_color="#94a3b8", line_width=1)
        set_chart_layout(fig2a, "P(至少 1 次爆毀) 隨飛行次數累積", "飛行次數 n", "P(至少 1 次爆毀)")
        fig2a.update_layout(height=420, yaxis=dict(range=[0, 1.05]))
        st.plotly_chart(fig2a, use_container_width=True)

        # 對照課本四個值
        _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本例題 3.5 對照（n = 2, 5, 10, 50 次）",
              "n=2：P≈0.014 ｜ n=5：P≈0.034 ｜ n=10：P≈0.067 ｜ n=50：P≈0.293<br>"
              "至 1995 年 NASA 共進行 49 次飛行，1 次爆毀，與 1/49 ≈ 0.020 的歷史記錄相符。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. 獨立事件的乘法法則：P(全部成功) = (P 單次成功)ⁿ，每多一次任務，「全部成功」的機率就縮小一點。<br>
        2. 餘事件法則的威力：「至少 1 次失敗」= 1 − 「完全沒有失敗」，用於複雜情境時特別簡潔。<br>
        3. 工程含義：即使每次任務的失敗率極低（0.7%），累積到 50 次後整體風險已接近 30%。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：加法法則通式——金屬製造缺失（例題 3.2）────────────
    with st.expander("📖 課本例題 3.2 重現：加法法則通式（金屬製造缺失）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解為什麼加法法則通式需要減去交集——避免「重複計算」。<br>
                <b>你會發現：</b>P(A 或 B) ≠ P(A) + P(B)，除非兩事件互斥（交集為 0）。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本例題 3.2：金屬製造缺失**
        某批金屬零件的製造過程中：
        - P(錯誤接著 FB) = 0.10
        - P(過氧化 EO) = 0.25
        - P(FB 且 EO) = 0.05（兩種缺失同時存在）

        **請計算：P(FB 或 EO) — 至少有一種缺失的機率**
        """)

        col_reset2b, _ = st.columns([1, 5])
        with col_reset2b:
            if st.button("🔄 復原預設值", key="w3_reset_ex32"):
                for k in ["w3_pFB", "w3_pEO", "w3_pFBEO", "w3_ex32_touched"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        pFB   = st.number_input("P(錯誤接著 FB) =", value=0.10, step=0.01, format="%.2f", key="w3_pFB")
        pEO   = st.number_input("P(過氧化 EO) =",   value=0.25, step=0.01, format="%.2f", key="w3_pEO")
        pFBEO = st.number_input("P(FB 且 EO) =",    value=0.05, step=0.01, format="%.2f", key="w3_pFBEO")

        # 使用者是否曾互動（改過任何數值才算）
        _ex32_default = (abs(pFB-0.10)<0.001 and abs(pEO-0.25)<0.001 and abs(pFBEO-0.05)<0.001)
        if not _ex32_default:
            st.session_state["w3_ex32_touched"] = True
        _ex32_touched = st.session_state.get("w3_ex32_touched", False)

        result = pFB + pEO - pFBEO
        st.markdown("---")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1: st.metric("P(FB)", f"{pFB:.2f}")
        with col_m2: st.metric("P(EO)", f"{pEO:.2f}")
        with col_m3: st.metric("P(FB ∩ EO)", f"{pFBEO:.2f}")
        with col_m4: st.metric("P(FB ∪ EO)", f"{result:.2f}")

        if abs(result - 0.30) < 0.001 and _ex32_touched:
            _card("#22c55e","#f0fdf4","#166534","✅ 課本答案 0.30 驗證通過！",
                  "P(FB ∪ EO) = 0.10 + 0.25 − 0.05 = 0.30，代表有 30% 的產品至少有一種生產缺失。"
                  "扣掉 0.05 是因為同時有兩種缺失的零件，若不扣除會被計算兩次。")
            mark_done("t2_tree")
        elif abs(result - 0.30) >= 0.001 and _ex32_touched:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 答案還不對",
                  f"目前計算結果 P(FB ∪ EO) = {result:.2f}，請重新調整數值再試試。")

        # 維恩圖視覺化（用圓形近似）
        fig2b = go.Figure()
        theta = np.linspace(0, 2*np.pi, 200)
        # FB 圓（左）
        x_fb = 0.35 * np.cos(theta) - 0.2
        y_fb = 0.35 * np.sin(theta)
        fig2b.add_trace(go.Scatter(x=x_fb, y=y_fb, mode="lines", fill="toself",
                                   fillcolor="rgba(239,68,68,0.3)",
                                   line=dict(color="#ef4444", width=2), name="FB 錯誤接著"))
        # EO 圓（右）
        x_eo = 0.35 * np.cos(theta) + 0.2
        y_eo = 0.35 * np.sin(theta)
        fig2b.add_trace(go.Scatter(x=x_eo, y=y_eo, mode="lines", fill="toself",
                                   fillcolor="rgba(59,130,246,0.3)",
                                   line=dict(color="#3b82f6", width=2), name="EO 過氧化"))
        fig2b.add_annotation(x=-0.42, y=0, text="P(FB)=" + str(round(pFB,2)),
                              font=dict(size=14, color="#ef4444"), showarrow=False)
        fig2b.add_annotation(x=0.42, y=0, text="P(EO)=" + str(round(pEO,2)),
                              font=dict(size=14, color="#3b82f6"), showarrow=False)
        fig2b.add_annotation(x=0, y=0, text="∩=" + str(round(pFBEO,2)),
                              font=dict(size=14, color="#1e293b"), showarrow=False)
        fig2b.update_layout(
            height=420,
            xaxis=dict(range=[-0.85,0.85], showticklabels=False, showgrid=False,
                       scaleanchor="y", scaleratio=1),
            yaxis=dict(range=[-0.85,0.85], showticklabels=False, showgrid=False),
            title=dict(text="維恩圖：P(FB ∪ EO) = 交集需從總和中扣除", font=dict(size=F_TITLE)),
            showlegend=True, plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig2b, use_container_width=True)

    # ── 隨堂小測驗 ───────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§3.2 複合事件</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q2 = st.radio(
        "📍 **題目：若 A 與 B 為統計獨立事件，P(A)=0.4，P(B)=0.3，則 P(A ∩ B) = ？**",
        ["請選擇...", "A. 0.12", "B. 0.58", "C. 0.70", "D. 無法確定"],
        key="w3_q2_radio"
    )
    if st.button("送出答案", key="w3_q2_btn"):
        if q2 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q2:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "A 與 B 統計獨立，故 P(A ∩ B) = P(A) × P(B) = 0.4 × 0.3 = 0.12。"
                  "這是獨立事件乘法法則的直接應用。")
            mark_done("t2_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "當兩事件統計獨立時，P(A ∩ B) = P(A) × P(B)——A 的發生不影響 B 的機率，反之亦然。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 3：§3.3 條件機率
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§3.3 條件機率</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>條件機率 (Conditional Probability)</b>：在事件 B 已知發生的條件下，事件 A 發生的機率。<br>
            記作 P(A | B)，讀作「給定 B 發生時，A 的機率」。<br><br>
            ▸ <b>公式</b>：P(A | B) = P(A ∩ B) ÷ P(B)<br>
            ▸ <b>統計獨立的判斷</b>：若 P(A | B) = P(A)，則 A 與 B 統計獨立（B 的發生不影響 A）<br>
            ▸ <b>非條件機率</b>：不考慮任何給定條件下事件 A 發生的機率，即 P(A)
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 工程中的條件機率</b><br>
    品管員看到某零件外觀有裂縫（已知事件 B），想知道它內部是否也有缺陷（事件 A）的機率。
    這正是 P(A | B) 的工程含義：不是從母體全部抽取，而是在「已觀察到某特徵」的條件下評估另一特徵的機率。
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #ddd6fe;margin:8px 0;">
        <div style="background:#7c3aed;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📐 條件機率公式</span>
        </div>
        <div style="background:#f5f3ff;padding:16px 18px;color:#4c1d95;
                    font-size:1.1rem;line-height:1.9;text-align:center;">
            P(A | B) = P(A ∩ B) ÷ P(B)<br>
            <small style="color:#7c3aed;font-size:0.88rem;">
                P(B) > 0；分子為聯合機率，分母為已知（條件）事件的機率
            </small>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：條件機率逐步計算——學會會員範例 ──────────────────
    with st.expander("🛠️ 展開實驗室 A：條件機率逐步計算（課本學會會員範例）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>從聯合機率表計算條件機率，並驗證兩事件是否統計獨立。<br>
                <b>你會發現：</b>P(UG | EE) ≠ P(UG)，說明「大學部」與「電機系」為相依事件——系所與年級並非獨立。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("""
        **📋 課本場景（圖 3.3）：學會會員樣本空間**
        總計 38 位會員，其中：大學部(UG)=19 人，研究所(G)=19 人；
        電機系(EE)=12 人（其中 UG 有 5 人）。
        """)

        # 聯合機率表
        joint_data = {
            "": ["大學部(UG)", "研究所(G)", "合計"],
            "電機系(EE)": ["5/38 = 0.132", "7/38 = 0.184", "12/38 = 0.316"],
            "機械系(ME)": ["8/38 = 0.211", "5/38 = 0.132", "13/38 = 0.342"],
            "土木系(CE)": ["6/38 = 0.158", "7/38 = 0.184", "13/38 = 0.342"],
            "合計":       ["19/38 = 0.500", "19/38 = 0.500", "38/38 = 1.000"],
        }
        df_joint = pd.DataFrame(joint_data)
        _card("#0369a1","#e0f2fe","#0c4a6e","📋 步驟一：觀察聯合機率表",
              "分子為人數，分母均為 38（總人數）。")
        st.dataframe(df_joint, use_container_width=True, hide_index=True)

        true_UG_given_EE = round(5/12, 4)   # P(UG|EE) = (5/38)/(12/38) = 5/12
        true_EE_given_UG = round(5/19, 4)   # P(EE|UG) = (5/38)/(19/38) = 5/19
        true_pUG         = round(19/38, 4)  # P(UG) = 0.5

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算 P(UG | EE)",
              "= P(UG ∩ EE) ÷ P(EE) = (5/38) ÷ (12/38) = 5 ÷ 12。請填入結果（保留 4 位小數）：")

        ug_ee_input = st.number_input(
            "P(大學部 | 電機系) = 5/12 = ?",
            value=0.0, step=0.001, format="%.4f", key="w3_step2_ugee"
        )
        step2_cond_done = False
        if ug_ee_input != 0.0:
            if abs(ug_ee_input - true_UG_given_EE) < 0.0015:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                      "P(UG | EE) = 5/12 ≈ <b>0.4167</b>。"
                      "在 12 名電機系學生中，有 5 名是大學部，所以條件機率為 5/12。")
                step2_cond_done = True
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算一次",
                      "P(UG|EE) = P(UG ∩ EE) ÷ P(EE) = (5/38) ÷ (12/38) = 5/12（你填了 " + str(round(ug_ee_input,4)) + "）")

        st.markdown("---")
        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：判斷 UG 與 EE 是否統計獨立",
              "P(UG) = 19/38 = 0.5000。若 P(UG | EE) = P(UG)，則獨立。"
              "你在步驟二算出的 P(UG | EE) ≈ 0.4167。請問兩者相等嗎？")

        indep_ans = st.radio(
            "P(UG | EE) ≈ 0.4167 vs P(UG) = 0.5000，UG 與 EE 的關係為：",
            ["請選擇...", "A. 統計獨立（兩機率相等）", "B. 統計相依（兩機率不等）"],
            key="w3_step3_indep"
        )
        if st.button("確認步驟三", key="w3_btn_step3_cond"):
            if "B." in indep_ans:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟三正確！",
                      "P(UG | EE) = 0.4167 ≠ P(UG) = 0.5000，故 UG 與 EE 為<b>相依事件</b>。"
                      "這代表系所的選擇與大學部/研究所身分有關聯，並非獨立。")
                mark_done("t3_cond")
            elif "A." in indep_ans:
                _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                      "0.4167 ≠ 0.5000，所以 P(UG | EE) ≠ P(UG)，統計獨立的判斷條件不成立。")

        # 重置按鈕
        if st.button("🔄 重新開始實驗室 A（條件機率）", key="w3_reset_cond"):
            for k in ["w3_step2_ugee", "w3_step3_indep"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 ───────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§3.3 條件機率</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q3 = st.radio(
        "📍 **題目：已知 P(A ∩ B) = 0.06，P(B) = 0.30，則 P(A | B) = ？**",
        ["請選擇...", "A. 0.20", "B. 0.36", "C. 0.50", "D. 0.06"],
        key="w3_q3_radio"
    )
    if st.button("送出答案", key="w3_q3_btn"):
        if q3 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q3:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "P(A | B) = P(A ∩ B) ÷ P(B) = 0.06 ÷ 0.30 = 0.20。"
                  "條件機率就是在「已知 B 發生」的縮小樣本空間中，A 所占的比例。")
            mark_done("t3_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "條件機率公式：P(A | B) = P(A ∩ B) ÷ P(B)，分子是交集機率，分母是條件事件的機率。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 4：§3.4 乘法法則、機率樹及抽樣
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§3.4 乘法法則通式與機率樹</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>乘法法則通式</b>（獨立與相依事件皆適用）：<br>
            P(A ∩ B) = P(A) × P(B | A) = P(B) × P(A | B)<br><br>
            <b>機率樹 (Probability Tree)</b>：以樹狀圖清楚表達多階段隨機試驗的結構。<br>
            ▸ 每個分枝上標注<b>條件機率</b>，同一分叉點所有分枝之和為 1<br>
            ▸ 每條路徑的機率 = 路徑上各分枝機率之<b>乘積</b><br>
            ▸ 所有路徑互斥且無遺漏，機率總和為 1<br><br>
            <b>不還原抽樣</b>：每次抽取後不放回，母體縮小，條件機率的分母逐次遞減。
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 機率樹的工程應用</b><br>
    石油探測的決策：地質師先判斷是否有石油（第一階段），再解讀震測結果（第二階段）。
    機率樹把「藏油/未藏油 × 震測正確/錯誤」的四條路徑清晰呈現，
    幫助工程師計算每條決策路徑的機率，找出最有價值的探勘策略。
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 乘法法則通式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(A ∩ B) = P(A) × P(B | A)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">獨立時 P(B|A)=P(B)，退化為 P(A)×P(B)</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 不還原抽樣（第 2 次）</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                P(良品₂ | 良品₁) = (G−1) / (N−1)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">N：母體大小；G：良品數；分母每次遞減</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室 A：石油探測機率樹模擬器（課本例題 3.7）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用乘法法則通式計算機率樹每條路徑的聯合機率，並驗證路徑機率之和為 1。<br>
                <b>你會發現：</b>調整「藏油機率」後，四條路徑同步變化，但總和恆為 1——機率樹的完備性。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：課本例題 3.7（石油探測）</b><br>
        某地區埋有石油（O）的機率為 P(O)。若確實藏油，震測可正確測出的機率 P(F|O)=0.8；
        若未藏油，震測正確測出無油（U）的機率 P(U|非O)=0.9。<br>
        請調整 P(O) 的值，觀察四條機率樹路徑如何動態變化。
        </div>
        ''', unsafe_allow_html=True)

        col_reset4a, _ = st.columns([1, 5])
        with col_reset4a:
            if st.button("🔄 復原課本預設值（P(O)=40%）", key="w3_reset_oil"):
                if "w3_p_oil" in st.session_state:
                    del st.session_state["w3_p_oil"]
                st.rerun()

        p_oil = st.slider(
            "設定藏油機率 P(O)（%）— 課本預設值 = 40%",
            5, 95, 40, 5, key="w3_p_oil"
        )
        if p_oil != 40:
            mark_done("t4_tree")

        pO = p_oil / 100;  pNO = 1 - pO
        pFO = 0.8;  pUO = 0.2;  pFNO = 0.1;  pUNO = 0.9

        path_OF  = round(pO  * pFO,  4)
        path_OU  = round(pO  * pUO,  4)
        path_NOF = round(pNO * pFNO, 4)
        path_NOU = round(pNO * pUNO, 4)
        total_paths = round(path_OF + path_OU + path_NOF + path_NOU, 4)

        tree_df = pd.DataFrame({
            "路徑": ["O ∩ F（藏油，震測出有）", "O ∩ U（藏油，震測未測出）",
                     "非O ∩ F（無油，誤測出有）", "非O ∩ U（無油，正確測無）"],
            "計算式": [
                "P(O)×P(F|O) = " + str(round(pO,2)) + "×0.8",
                "P(O)×P(U|O) = " + str(round(pO,2)) + "×0.2",
                "P(非O)×P(F|非O) = " + str(round(pNO,2)) + "×0.1",
                "P(非O)×P(U|非O) = " + str(round(pNO,2)) + "×0.9",
            ],
            "聯合機率": [path_OF, path_OU, path_NOF, path_NOU],
        })
        st.dataframe(tree_df, use_container_width=True, hide_index=True)

        col_t1,col_t2,col_t3,col_t4,col_t5 = st.columns(5)
        with col_t1: st.metric("O ∩ F",    str(path_OF))
        with col_t2: st.metric("O ∩ U",    str(path_OU))
        with col_t3: st.metric("非O ∩ F",  str(path_NOF))
        with col_t4: st.metric("非O ∩ U",  str(path_NOU))
        with col_t5: st.metric("四路徑總和", str(total_paths))

        labels_t   = ["O∩F（藏油可測）","O∩U（藏油未測）","非O∩F（誤測）","非O∩U（正確無油）"]
        values_t   = [path_OF, path_OU, path_NOF, path_NOU]
        bar_cols_t = ["#22c55e","#f59e0b","#ef4444","#3b82f6"]
        fig4a = go.Figure(go.Bar(
            x=values_t, y=labels_t, orientation="h",
            marker_color=bar_cols_t,
            text=[str(v) for v in values_t],
            textposition="outside", textfont=dict(size=13),
            hovertemplate="%{y}<br>機率: %{x:.4f}<extra></extra>"
        ))
        title_t4 = "機率樹四條路徑聯合機率（P(O)=" + str(round(pO,2)) + "）"
        set_chart_layout(fig4a, title_t4, "聯合機率", "路徑")
        fig4a.update_layout(height=420, xaxis=dict(range=[0, 0.75]),
                            margin=dict(t=60, b=40, l=200, r=60))
        st.plotly_chart(fig4a, use_container_width=True)

        if abs(total_paths - 1.0) < 0.001:
            _card("#22c55e","#f0fdf4","#166534","✅ 機率樹完備性驗證通過",
                  "四條路徑機率之和 = " + str(total_paths) + " = 1.000。機率樹每個分叉點展開的分枝互斥且無遺漏，總和必為 1。")
        if p_oil == 40:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本例題 3.7 對照（P(O)=0.4）",
                  "P(O∩F)=0.32；P(O∩U)=0.08；P(非O∩F)=0.06；P(非O∩U)=0.54 → 總和=1.00 ✓")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. 乘法法則通式：每條路徑的機率 = 路徑上各分枝條件機率的乘積。<br>
        2. 機率樹完備性：所有路徑機率之和恆為 1，可用以自我檢驗計算。<br>
        3. 工程決策：「非O∩F」是偽陽性（誤測有油），工程師需評估此錯誤的代價。
        </div>
        ''', unsafe_allow_html=True)

    with st.expander("📖 課本例題 3.9 重現：不還原抽樣機率樹（晶片抽樣）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解不還原抽樣中，條件機率如何隨每次抽取而改變（分母逐次遞減）。<br>
                <b>你會發現：</b>調整不良品數量後，各路徑機率相應改變，驗證乘法法則通式。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown(
            "**課本例題 3.9**：100 個晶片中 G 個良品、10 個不良品，不還原抽取 3 個。課本預設：G=90，D=10。"
        )

        col_reset4b, _ = st.columns([1, 5])
        with col_reset4b:
            if st.button("🔄 復原課本預設（G=90）", key="w3_reset_chip"):
                if "w3_chip_G" in st.session_state:
                    del st.session_state["w3_chip_G"]
                st.rerun()

        chip_G = st.slider("設定良品數 G（D = 100 − G）— 課本預設 G=90", 70, 99, 90, 1, key="w3_chip_G")
        chip_D = 100 - chip_G

        paths_chip = []
        for s1 in ["G","D"]:
            p1 = chip_G/100 if s1=="G" else chip_D/100
            rg1 = chip_G-1 if s1=="G" else chip_G
            rd1 = chip_D   if s1=="G" else chip_D-1
            for s2 in ["G","D"]:
                p2 = rg1/99 if s2=="G" else rd1/99
                rg2 = rg1-1 if s2=="G" else rg1
                rd2 = rd1   if s2=="G" else rd1-1
                for s3 in ["G","D"]:
                    p3 = rg2/98 if s3=="G" else rd2/98
                    paths_chip.append({"路徑": s1+"\u2081"+s2+"\u2082"+s3+"\u2083",
                                       "機率": round(p1*p2*p3, 6)})

        # ── 計算 8 條路徑 ─────────────────────────────────────────────
        pGGG = round((chip_G/100)*((chip_G-1)/99)*((chip_G-2)/98), 5)
        pGGD = round((chip_G/100)*((chip_G-1)/99)*(chip_D/98), 5)
        pGDG = round((chip_G/100)*(chip_D/99)*((chip_G-1)/98), 5)
        pGDD = round((chip_G/100)*(chip_D/99)*((chip_D-1)/98), 5)
        pDGG = round((chip_D/100)*((chip_G)/99)*((chip_G-1)/98), 5)
        pDGD = round((chip_D/100)*((chip_G)/99)*(chip_D-1+1-1)/98, 5)  # D1→G2→D3
        # 精確計算所有8條
        def _p3(s1,s2,s3,G,D):
            g,d = G,D
            p1 = g/100 if s1=="G" else d/100
            if s1=="G": g-=1
            else: d-=1
            p2 = g/99 if s2=="G" else d/99
            if s2=="G": g-=1
            else: d-=1
            p3 = g/98 if s3=="G" else d/98
            return round(p1*p2*p3, 5)
        paths8 = {
            "GGG": _p3("G","G","G",chip_G,chip_D),
            "GGD": _p3("G","G","D",chip_G,chip_D),
            "GDG": _p3("G","D","G",chip_G,chip_D),
            "GDD": _p3("G","D","D",chip_G,chip_D),
            "DGG": _p3("D","G","G",chip_G,chip_D),
            "DGD": _p3("D","G","D",chip_G,chip_D),
            "DDG": _p3("D","D","G",chip_G,chip_D),
            "DDD": _p3("D","D","D",chip_G,chip_D),
        }
        total_chip = round(sum(paths8.values()), 4)
        pGGG = paths8["GGG"]

        # ── 機率樹 SVG（仿課本圖 3.5）─────────────────────────────────
        # 版面：左→右 4 欄：第1次/第2次/第3次/聯合機率+樣本空間
        # 顏色：G=藍色系, D=紅色系
        CG = "#2563eb"   # 良品色
        CD = "#dc2626"   # 不良品色
        BG_G = "#eff6ff" # 良品背景
        BG_D = "#fef2f2" # 不良品背景

        # 各層 x 座標（節點中心）
        # 層0(根) → 層1(第1次) → 層2(第2次) → 層3(第3次葉) → 標籤
        x0   = 30    # 根節點
        x1   = 120   # 第1次分枝節點
        x2   = 270   # 第2次分枝節點
        x3   = 420   # 第3次分枝（葉）
        x_jp = 505   # 聯合機率文字
        x_sp = 620   # 樣本空間文字
        W    = 760
        # 8個葉節點 y 座標（等距）
        leaf_h = 68
        leaf_ys = [44 + i * leaf_h for i in range(8)]   # 44,112,180,...,532
        # 第2次節點：2個葉一組取中心
        l2_ys = [(leaf_ys[0]+leaf_ys[1])//2,   # GG→ y中
                 (leaf_ys[2]+leaf_ys[3])//2,   # GD→ y中
                 (leaf_ys[4]+leaf_ys[5])//2,   # DG→ y中
                 (leaf_ys[6]+leaf_ys[7])//2]   # DD→ y中
        # 第1次節點：4個葉一組取中心
        l1_G = (leaf_ys[0]+leaf_ys[3])//2  # G1 節點
        l1_D = (leaf_ys[4]+leaf_ys[7])//2  # D1 節點
        # 根節點
        root_y = (leaf_ys[0]+leaf_ys[7])//2

        H = leaf_ys[-1] + 50

        def node_rect(x, y, label, color, bg, w=38, h=22):
            """圓角矩形節點"""
            return (
                f'<rect x="{x-w//2}" y="{y-h//2}" width="{w}" height="{h}" rx="5" ' +
                f'fill="{bg}" stroke="{color}" stroke-width="1.8"/>' +
                f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="12" ' +
                f'font-weight="700" fill="{color}">{label}</text>'
            )

        def branch_line(x1c, y1c, x2c, y2c, color):
            return f'<line x1="{x1c}" y1="{y1c}" x2="{x2c}" y2="{y2c}" stroke="{color}" stroke-width="1.4" stroke-opacity="0.7"/>'

        def frac_label(x, y, num, den, color):
            """在線段中點顯示分數標籤"""
            return (
                f'<text x="{x}" y="{y-3}" text-anchor="middle" font-size="10" fill="{color}">{num}</text>' +
                f'<line x1="{x-10}" y1="{y+1}" x2="{x+10}" y2="{y+1}" stroke="{color}" stroke-width="0.8"/>' +
                f'<text x="{x}" y="{y+12}" text-anchor="middle" font-size="10" fill="{color}">{den}</text>'
            )

        parts = [
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" ',
            f'style="width:100%;max-height:500px;border-radius:12px;border:1px solid #e2e8f0;background:#fafafa;font-family:sans-serif;">',
            # 欄標題
            f'<text x="{x1}" y="18" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">第 1 次抽樣</text>',
            f'<text x="{x2}" y="18" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">第 2 次抽樣</text>',
            f'<text x="{x3}" y="18" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">第 3 次抽樣</text>',
            f'<text x="{x_jp+15}" y="18" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">聯合機率</text>',
            f'<text x="{x_sp+20}" y="18" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">樣本空間</text>',
        ]

        # 定義樹結構：每條路徑 (s1,s2,s3)
        tree = [
            ("G","G","G"),("G","G","D"),("G","D","G"),("G","D","D"),
            ("D","G","G"),("D","G","D"),("D","D","G"),("D","D","D"),
        ]
        key_order = ["GGG","GGD","GDG","GDD","DGG","DGD","DDG","DDD"]

        # 分數分子（依 G, chip_G, chip_D）
        def branch_nums(s1,s2,s3,G,D):
            """回傳各枝分子分母"""
            g,d = G,D
            n1 = g if s1=="G" else d; den1 = 100
            if s1=="G": g-=1
            else: d-=1
            n2 = g if s2=="G" else d; den2 = 99
            if s2=="G": g-=1
            else: d-=1
            n3 = g if s3=="G" else d; den3 = 98
            return (n1,den1,n2,den2,n3,den3)

        # 根節點
        parts.append(node_rect(x0, root_y, "start", "#475569", "#f1f5f9", 44, 22))

        # 第1次枝：G1, D1
        for s1, l1y in [("G",l1_G),("D",l1_D)]:
            c1 = CG if s1=="G" else CD
            bg1 = BG_G if s1=="G" else BG_D
            lbl1 = f"{s1}₁"
            parts.append(branch_line(x0+22, root_y, x1-19, l1y, c1))
            # 分數在線段中點
            mx = (x0+22+x1-19)//2
            my = (root_y+l1y)//2
            n1 = chip_G if s1=="G" else chip_D
            parts.append(frac_label(mx, my, n1, 100, c1))
            parts.append(node_rect(x1, l1y, lbl1, c1, bg1))

            # 第2次枝
            children2 = [(s1,"G"),(s1,"D")]
            for s2 in ["G","D"]:
                idx2 = 0 if s2=="G" else 1
                l2y_idx = (0 if s1=="G" else 2) + idx2
                l2y = l2_ys[l2y_idx]
                c2 = CG if s2=="G" else CD
                bg2 = BG_G if s2=="G" else BG_D
                lbl2 = f"{s2}₂"
                parts.append(branch_line(x1+19, l1y, x2-19, l2y, c2))
                mx2 = (x1+19+x2-19)//2
                my2 = (l1y+l2y)//2
                n1_,_1,n2,_2,_,_ = branch_nums(s1,s2,"G",chip_G,chip_D)
                parts.append(frac_label(mx2, my2, n2, 99, c2))
                parts.append(node_rect(x2, l2y, lbl2, c2, bg2))

                # 第3次枝（葉節點）
                for s3 in ["G","D"]:
                    leaf_idx = (0 if s1=="G" else 4) + (0 if s2=="G" else 2) + (0 if s3=="G" else 1)
                    ly = leaf_ys[leaf_idx]
                    c3 = CG if s3=="G" else CD
                    bg3 = BG_G if s3=="G" else BG_D
                    lbl3 = f"{s3}₃"
                    parts.append(branch_line(x2+19, l2y, x3-19, ly, c3))
                    mx3 = (x2+19+x3-19)//2
                    my3 = (l2y+ly)//2
                    n1_,_1,n2_,_2,n3,_3 = branch_nums(s1,s2,s3,chip_G,chip_D)
                    parts.append(frac_label(mx3, my3, n3, 98, c3))
                    parts.append(node_rect(x3, ly, lbl3, c3, bg3))

                    # 聯合機率
                    path_key = s1+s2+s3
                    jp = paths8[path_key]
                    is_best = (path_key == "GGG")
                    jp_color = "#166534" if is_best else ("#374151" if s3=="G" else "#991b1b")
                    jp_weight = "800" if is_best else "400"
                    parts.append(
                        f'<text x="{x_jp}" y="{ly+5}" font-size="11" font-weight="{jp_weight}" fill="{jp_color}">{jp}</text>'
                    )

                    # 樣本空間標籤
                    def sub_map(c): return {"G":"G","D":"D"}[c]
                    sp_lbl = f"{s1}₁{s2}₂{s3}₃"
                    sp_color = CG if s3=="G" else CD
                    parts.append(
                        f'<text x="{x_sp}" y="{ly+5}" font-size="11" fill="{sp_color}">{sp_lbl}</text>'
                    )

        # 底部總和驗證列
        total_y = H - 20
        tc = "#166534" if abs(total_chip-1.0)<0.002 else "#991b1b"
        parts.append(
            f'<rect x="4" y="{total_y-16}" width="{W-8}" height="24" rx="5" fill="#f0fdf4"/>' +
            f'<text x="{W//2}" y="{total_y}" text-anchor="middle" font-size="11" font-weight="700" fill="{tc}">' +
            f'8 條路徑機率總和 = {total_chip}　（完備性驗證）</text>'
        )
        parts.append("</svg>")
        st.markdown("".join(parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # metrics 列
        col_m1,col_m2,col_m3,col_m4 = st.columns(4)
        with col_m1: st.metric("P(G₁G₂G₃) 全良品",   str(paths8["GGG"]))
        with col_m2: st.metric("P(G₁G₂D₃) 最後不良", str(paths8["GGD"]))
        with col_m3: st.metric("P(至少 1 個不良)",     str(round(1-paths8["GGG"],5)))
        with col_m4: st.metric("8 路徑總和",            str(total_chip))

        if abs(total_chip - 1.0) < 0.002:
            _card("#22c55e","#f0fdf4","#166534","✅ 完備性通過","8 條路徑機率總和 = 1.000")

        if chip_G == 90:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本例題 3.9 對照（G=90, D=10）",
                  "P(G₁G₂G₃) = 90/100 × 89/99 × 88/98 ≈ 0.72653；"
                  "P(G₁G₂D₃) ≈ 0.08256（課本第 2 個簡單事件）")

    # ── 隨堂小測驗 tab4 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§3.4 乘法法則與機率樹</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q4 = st.radio(
        "📍 **題目：某橋梁工地在雨季，土壤液化機率 P(L)=0.3；若液化，基樁沉陷機率 P(S|L)=0.8。"
        "P(液化 且 沉陷) = ？**",
        ["請選擇...", "A. 0.24", "B. 0.50", "C. 0.11", "D. 0.80"],
        key="w3_q4_radio"
    )
    if st.button("送出答案", key="w3_q4_btn"):
        if q4 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q4:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "P(L ∩ S) = P(L) × P(S | L) = 0.3 × 0.8 = 0.24（乘法法則通式）。"
                  "這是機率樹路徑 L→S 的聯合機率，雨季同時液化且沉陷的機率為 24%。")
            mark_done("t4_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "乘法法則通式：P(A ∩ B) = P(A) × P(B | A)，將兩個已知機率相乘即可。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 5：§3.5 系統可靠度的預測
# ══════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§3.5 系統可靠度的預測</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>可靠度 Rᵢ(t)</b>：單元 i 在時間 t 內仍可正常運作的機率（0 到 1 之間）。<br><br>
            <b>串聯系統</b>（所有單元都要正常，整體才能運作）：<br>
            Rₛ = R₁ × R₂ × … × Rₙ　← 任一單元故障即全系統故障<br><br>
            <b>並聯系統</b>（任一單元正常，整體即可運作）：<br>
            Rₛ = 1 − (1−R₁)(1−R₂)…(1−Rₙ)　← 所有單元同時故障才停機<br><br>
            ▸ 串聯可靠度 ≤ 最小單元可靠度（最弱環節決定上限）<br>
            ▸ 並聯可靠度 ≥ 最大單元可靠度（冗餘備援大幅提升整體可靠度）
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="why-box">
    <b>🔧 為什麼工程師重視系統可靠度？</b><br>
    橋梁主纜、高鐵煞車系統、核電廠冷卻迴路——這些都是串聯或並聯系統的工程實例。
    串聯系統最脆弱的單元一旦失效，整個系統就崩潰；
    並聯設計（冗餘備援）能讓可靠度大幅超越各別單元，是工程安全設計的核心策略。
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 串聯系統可靠度</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                Rₛ(t) = R₁(t) × R₂(t) × … × Rₙ(t)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">獨立事件乘法法則；Rₛ ≤ min(Rᵢ)</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 並聯系統可靠度</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                Rₛ(t) = 1 − (1−R₁)(1−R₂)…(1−Rₙ)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">餘事件法則；Rₛ ≥ max(Rᵢ)</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：串聯系統可靠度設計器（課本圖 3.7）──────────────
    with st.expander("🛠️ 展開實驗室 A：串聯系統可靠度設計器（課本圖 3.7）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受「最弱單元決定整體串聯可靠度」，以及提升不同單元對整體效益的差異。<br>
                <b>你會發現：</b>即使三個單元個別可靠度都在 90% 以上，串聯後整體仍可能低於 75%。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：橋梁結構監測串聯系統（課本圖 3.7 衍生）</b><br>
        橋梁監測系統由三個子系統串聯：單元 1（應變感測器）、單元 2（無線傳輸模組）、單元 3（警報主機）。
        三者皆正常，監測才有效。請拖動滑桿調整各單元可靠度！
        </div>
        ''', unsafe_allow_html=True)

        col_reset5a, _ = st.columns([2, 3])
        with col_reset5a:
            if st.button("🔄 復原預設（0.90, 0.80, 0.95）", key="w3_reset_series"):
                for k in ["w3_r1","w3_r2","w3_r3"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: r1 = st.slider("R₁（%）感測器",    50, 99, 90, 1, key="w3_r1")
        with col_s2: r2 = st.slider("R₂（%）無線傳輸",  50, 99, 80, 1, key="w3_r2")
        with col_s3: r3 = st.slider("R₃（%）警報主機",  50, 99, 95, 1, key="w3_r3")

        check_slider("w3_r1", "t5_series")
        check_slider("w3_r2", "t5_series")
        check_slider("w3_r3", "t5_series")

        R1, R2, R3 = r1/100, r2/100, r3/100
        Rs_series  = round(R1*R2*R3, 4)
        min_r      = min(R1, R2, R3)

        col_m1,col_m2,col_m3,col_m4 = st.columns(4)
        with col_m1: st.metric("R₁ 感測器", str(R1))
        with col_m2: st.metric("R₂ 傳輸",   str(R2))
        with col_m3: st.metric("R₃ 警報",   str(R3))
        with col_m4: st.metric("🔗 串聯 Rₛ", str(Rs_series))

        # ── 串聯架構 SVG 圖示 ────────────────────────────────────────────
        def _sc(r):
            if r >= 0.95: return "#16a34a"
            if r >= 0.85: return "#2563eb"
            if r >= 0.75: return "#d97706"
            return "#dc2626"

        def _bg(r):
            if r >= 0.95: return "#f0fdf4"
            if r >= 0.85: return "#eff6ff"
            if r >= 0.75: return "#fffbeb"
            return "#fef2f2"

        rs_vals_a   = [R1, R2, R3]
        names_a     = ["感測器", "無線傳輸", "警報主機"]
        nums_a      = ["1", "2", "3"]
        weakest_a   = min(rs_vals_a)
        # 方塊尺寸：加高以容納三行文字
        bw_a, bh_a  = 100, 68
        gap_a       = 52          # 方塊間水平間距
        pad_left    = 30          # 左側輸入線長
        x_starts    = [pad_left, pad_left + bw_a + gap_a, pad_left + 2*(bw_a + gap_a)]
        rs_box_w    = 148
        SVG_W_A     = x_starts[-1] + bw_a + 16 + rs_box_w + 12
        # 高度：標題區(42) + 方塊區(bh_a) + 計算式區(36) + 底部留白(8)
        title_h     = 42
        calc_h      = 36
        bot_pad     = 8
        SVG_H_A     = title_h + bh_a + calc_h + bot_pad
        mid_y_a     = title_h + bh_a // 2   # 方塊中心線

        parts_a = [
            f'<svg viewBox="0 0 {SVG_W_A} {SVG_H_A}" xmlns="http://www.w3.org/2000/svg" ',
            f'style="width:100%;border-radius:12px;border:1px solid #e2e8f0;background:#f8fafc;">',
            f'<text x="12" y="18" font-size="13" font-weight="700" fill="#1e3a5f">串聯系統架構圖</text>',
            f'<text x="12" y="34" font-size="10" fill="#94a3b8">所有單元皆需正常運作，系統才能運作</text>',
            # 左側輸入線
            f'<line x1="4" y1="{mid_y_a}" x2="{x_starts[0]}" y2="{mid_y_a}" stroke="#64748b" stroke-width="2"/>',
        ]

        for i, (xb, rv, num, name) in enumerate(zip(x_starts, rs_vals_a, nums_a, names_a)):
            bc       = _sc(rv)
            bg       = _bg(rv)
            is_w     = (rv == weakest_a)
            sw       = 3 if is_w else 1.5
            sc       = "#f59e0b" if is_w else bc
            top_y    = title_h
            # 方塊
            parts_a.append(f'<rect x="{xb}" y="{top_y}" width="{bw_a}" height="{bh_a}" rx="9" fill="{bg}" stroke="{sc}" stroke-width="{sw}"/>')
            # clipPath for fill bar
            parts_a.append(f'<clipPath id="clipA{i}"><rect x="{xb}" y="{top_y}" width="{bw_a}" height="{bh_a}" rx="9"/></clipPath>')
            # 底部填充條（可靠度視覺化）
            bar_h2 = int(bh_a * rv)
            bar_y2 = top_y + bh_a - bar_h2
            parts_a.append(f'<rect x="{xb}" y="{bar_y2}" width="{bw_a}" height="{bar_h2}" fill="{bc}" opacity="0.15" clip-path="url(#clipA{i})"/>')
            # 編號（大）
            parts_a.append(f'<text x="{xb+bw_a//2}" y="{top_y+20}" text-anchor="middle" font-size="15" font-weight="900" fill="{bc}">{num}</text>')
            # 名稱
            parts_a.append(f'<text x="{xb+bw_a//2}" y="{top_y+36}" text-anchor="middle" font-size="11" fill="#374151">{name}</text>')
            # 可靠度（大字）
            parts_a.append(f'<text x="{xb+bw_a//2}" y="{top_y+56}" text-anchor="middle" font-size="14" font-weight="800" fill="{bc}">{rv:.0%}</text>')
            # 最弱標記（框內右上角小標）
            if is_w:
                parts_a.append(f'<rect x="{xb+bw_a-36}" y="{top_y+4}" width="32" height="14" rx="4" fill="#fef3c7"/>')
                parts_a.append(f'<text x="{xb+bw_a-20}" y="{top_y+14}" text-anchor="middle" font-size="9" fill="#d97706" font-weight="700">⚠ 最弱</text>')
            # 連接線＋× 符號
            if i < 2:
                lx1 = xb + bw_a
                lx2 = lx1 + gap_a
                mx  = lx1 + gap_a // 2
                parts_a.append(f'<line x1="{lx1}" y1="{mid_y_a}" x2="{lx2}" y2="{mid_y_a}" stroke="#64748b" stroke-width="2"/>')
                parts_a.append(f'<text x="{mx}" y="{mid_y_a+5}" text-anchor="middle" font-size="17" fill="#94a3b8">×</text>')

        # 右側輸出線 → Rₛ 色塊
        x_rs      = x_starts[-1] + bw_a + 16
        rs_color_a = _sc(Rs_series)
        rs_bg_a    = _bg(Rs_series)
        rs_box_h   = bh_a
        parts_a += [
            f'<line x1="{x_starts[-1]+bw_a}" y1="{mid_y_a}" x2="{x_rs}" y2="{mid_y_a}" stroke="#64748b" stroke-width="2"/>',
            f'<rect x="{x_rs}" y="{title_h}" width="{rs_box_w}" height="{rs_box_h}" rx="9" fill="{rs_bg_a}" stroke="{rs_color_a}" stroke-width="2"/>',
            f'<text x="{x_rs+rs_box_w//2}" y="{title_h+20}" text-anchor="middle" font-size="11" fill="#64748b">系統可靠度</text>',
            f'<text x="{x_rs+rs_box_w//2}" y="{title_h+42}" text-anchor="middle" font-size="18" font-weight="900" fill="{rs_color_a}">Rₛ = {Rs_series:.4f}</text>',
            f'<text x="{x_rs+rs_box_w//2}" y="{title_h+58}" text-anchor="middle" font-size="10" fill="#94a3b8">≤ 最弱單元 {weakest_a:.2f}</text>',
        ]

        # 計算式（圖示下方）
        calc_y = title_h + bh_a + 22
        eq_str = f"{R1:.2f} × {R2:.2f} × {R3:.2f} = {Rs_series:.4f}"
        parts_a += [
            f'<rect x="4" y="{title_h+bh_a+6}" width="{SVG_W_A-8}" height="28" rx="6" fill="#f1f5f9"/>',
            f'<text x="{SVG_W_A//2}" y="{calc_y}" text-anchor="middle" font-size="12" fill="#475569">',
            f'Rₛ = R₁ × R₂ × R₃ = {eq_str}',
            f'</text>',
        ]
        parts_a.append("</svg>")
        st.markdown("".join(parts_a), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        fig5a = go.Figure(go.Bar(
            x=["R₁ 感測器","R₂ 傳輸","R₃ 警報","Rₛ 串聯系統"],
            y=[R1, R2, R3, Rs_series],
            marker_color=[_sc(R1), _sc(R2), _sc(R3), _sc(Rs_series)],
            text=[f"{v:.1%}" for v in [R1, R2, R3, Rs_series]],
            textposition="outside", textfont=dict(size=13),
            hovertemplate="%{x}<br>可靠度: %{y:.4f}<extra></extra>"
        ))
        fig5a.add_hline(y=min_r, line_dash="dash", line_color="#f59e0b", line_width=2,
                        annotation_text="最弱單元=" + str(round(min_r,2)),
                        annotation_position="top right", annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig5a, "串聯系統：各單元可靠度 vs 系統可靠度", "單元", "可靠度")
        fig5a.update_layout(height=360, yaxis=dict(range=[0, 1.15]),
                            margin=dict(t=60, b=40, l=50, r=20))
        st.plotly_chart(fig5a, use_container_width=True)

        if r1==90 and r2==80 and r3==95:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本圖 3.7 對照（R₁=0.90, R₂=0.80, R₃=0.95）",
                  "Rₛ = 0.90 × 0.80 × 0.95 = <b>0.684</b>（課本計算結果）。"
                  "串聯可靠度明顯低於最弱單元（0.80），應優先提升 R₂。")
        else:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 串聯定律",
                  "串聯 Rₛ = " + str(Rs_series) + " ≤ 最弱單元 " + str(round(min_r,2)) +
                  "。串聯系統的可靠度永遠不超過最弱的那個單元——木桶效應在可靠度工程中完整體現。")

        st.markdown('''
        <div class="discover-box">
        💡 <b>實驗結論</b>：<br>
        1. 串聯可靠度 = 各單元可靠度之積，單元愈多整體可靠度愈低。<br>
        2. 最弱環節決定系統上限：Rₛ ≤ min(R₁, R₂, R₃)。<br>
        3. 工程策略：提升串聯系統時，應優先改善可靠度最低的單元，邊際效益最大。
        </div>
        ''', unsafe_allow_html=True)

    # ── 互動實驗室 B：並聯系統可靠度設計器（課本圖 3.8）──────────────
    with st.expander("🛠️ 展開實驗室 B：並聯系統可靠度設計器（冗餘備援）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解並聯（冗餘備援）系統如何大幅提升整體可靠度，以及與串聯的對比。<br>
                <b>你會發現：</b>即使三個單元個別可靠度只有 60%，並聯後整體可靠度可超過 93%！
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="discover-box">
        <b>📋 情境：橋梁施工液壓制動器並聯備援（課本圖 3.8 衍生）</b><br>
        三個液壓缸（P₁, P₂, P₃）並聯：任一液壓缸正常，制動即有效。
        請調整各液壓缸的可靠度，感受並聯備援的強大效益！
        </div>
        ''', unsafe_allow_html=True)

        col_reset5b, _ = st.columns([2, 3])
        with col_reset5b:
            if st.button("🔄 復原預設（0.40, 0.50, 0.60）", key="w3_reset_parallel"):
                for k in ["w3_p1","w3_p2","w3_p3"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: p1 = st.slider("P₁（%）液壓缸 1", 10, 99, 40, 1, key="w3_p1")
        with col_p2: p2 = st.slider("P₂（%）液壓缸 2", 10, 99, 50, 1, key="w3_p2")
        with col_p3: p3 = st.slider("P₃（%）液壓缸 3", 10, 99, 60, 1, key="w3_p3")

        check_slider("w3_p1", "t5_parallel")
        check_slider("w3_p2", "t5_parallel")
        check_slider("w3_p3", "t5_parallel")

        P1, P2, P3 = p1/100, p2/100, p3/100
        Rs_par  = round(1-(1-P1)*(1-P2)*(1-P3), 4)
        Rs_ser2 = round(P1*P2*P3, 4)
        max_p   = max(P1, P2, P3)

        col_mp1,col_mp2,col_mp3,col_mp4,col_mp5 = st.columns(5)
        with col_mp1: st.metric("P₁", str(P1))
        with col_mp2: st.metric("P₂", str(P2))
        with col_mp3: st.metric("P₃", str(P3))
        with col_mp4: st.metric("⚡ 並聯 Rₛ",    str(Rs_par))
        with col_mp5: st.metric("🔗 串聯（對比）", str(Rs_ser2))

        # ── 並聯架構 SVG 圖示 ────────────────────────────────────────────
        # 版面設計（從左到右）：
        #   [輸入線+OR] → [左節點] → [三個並聯方塊] → [右節點] → [輸出線] → [Rₛ框]
        #   名稱標籤放在方塊「內部」上半行，可靠度放下半行，完全不外溢
        def _pc(r):
            if r >= 0.95: return "#16a34a"
            if r >= 0.85: return "#2563eb"
            if r >= 0.75: return "#d97706"
            return "#dc2626"

        def _pbg(r):
            if r >= 0.95: return "#f0fdf4"
            if r >= 0.85: return "#eff6ff"
            if r >= 0.75: return "#fffbeb"
            return "#fef2f2"

        par_vals   = [P1, P2, P3]
        par_nums   = ["P₁", "P₂", "P₃"]
        par_names  = ["液壓缸 1", "液壓缸 2", "液壓缸 3"]
        fail_rate  = round((1-P1)*(1-P2)*(1-P3), 4)

        # ── 尺寸常數（全部在這裡調，不會互相干擾）──
        title_h  = 36    # 標題列高
        pbw      = 120   # 方塊寬
        pbh      = 44    # 方塊高（放得下兩行字）
        p_gap    = 8     # 方塊間距
        in_len   = 36    # 左輸入線長度（OR標籤在這段上）
        out_len  = 16    # 右輸出到Rₛ框的連線長
        rs_w     = 140   # Rₛ框寬
        rs_h     = 58    # Rₛ框高（固定）
        calc_h   = 30    # 底部計算式列高
        bot_pad  = 6

        n        = 3
        grp_h    = n*pbh + (n-1)*p_gap        # 並聯組總高
        node_x   = in_len                      # 左節點 x
        box_x    = node_x                      # 方塊左邊 x（與左節點對齊）
        rnode_x  = node_x + pbw               # 右節點 x
        top_y    = title_h                     # 方塊組起始 y
        ys       = [top_y + i*(pbh+p_gap) for i in range(n)]
        mys      = [y + pbh//2 for y in ys]   # 各方塊中心 y
        sys_cy   = top_y + grp_h//2           # 並聯組垂直中心

        SVG_W = rnode_x + out_len + rs_w + 8
        SVG_H = title_h + grp_h + calc_h + bot_pad

        parts_b = [
            f'<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg" ',
            f'style="width:100%;max-height:360px;border-radius:12px;border:1px solid #e2e8f0;background:#f8fafc;">',
            # 標題
            f'<text x="10" y="15" font-size="12" font-weight="700" fill="#1e3a5f">並聯系統架構圖</text>',
            f'<text x="10" y="28" font-size="10" fill="#94a3b8">任一單元正常即可，系統即可運作</text>',
            # 左輸入線（從 x=4 到 node_x）
            f'<line x1="4" y1="{sys_cy}" x2="{node_x}" y2="{sys_cy}" stroke="#64748b" stroke-width="2"/>',
            # OR 標籤（浮在輸入線正中央，帶白底避免與線重疊）
            f'<rect x="{in_len//2 - 14}" y="{sys_cy-9}" width="28" height="16" rx="4" fill="white" stroke="#ddd6fe" stroke-width="1"/>',
            f'<text x="{in_len//2}" y="{sys_cy+3}" text-anchor="middle" font-size="10" font-weight="700" fill="#7c3aed">OR</text>',
            # 左節點垂直線
            f'<line x1="{node_x}" y1="{mys[0]}" x2="{node_x}" y2="{mys[-1]}" stroke="#64748b" stroke-width="2"/>',
            # 右節點垂直線
            f'<line x1="{rnode_x}" y1="{mys[0]}" x2="{rnode_x}" y2="{mys[-1]}" stroke="#64748b" stroke-width="2"/>',
        ]

        for i, (yb, rv, num, name) in enumerate(zip(ys, par_vals, par_nums, par_names)):
            bc    = _pc(rv)
            bg    = _pbg(rv)
            my    = mys[i]
            bar_w = int(pbw * rv)
            # 左分支水平線
            parts_b.append(f'<line x1="{node_x}" y1="{my}" x2="{box_x}" y2="{my}" stroke="#64748b" stroke-width="1.5"/>')
            # 右分支水平線
            parts_b.append(f'<line x1="{rnode_x}" y1="{my}" x2="{rnode_x}" y2="{my}" stroke="#64748b" stroke-width="1.5"/>')
            # 方塊背景
            parts_b.append(f'<rect x="{box_x}" y="{yb}" width="{pbw}" height="{pbh}" rx="7" fill="{bg}" stroke="{bc}" stroke-width="2"/>')
            # 橫向填充條（可靠度視覺化）
            parts_b.append(f'<clipPath id="pB{i}"><rect x="{box_x}" y="{yb}" width="{pbw}" height="{pbh}" rx="7"/></clipPath>')
            parts_b.append(f'<rect x="{box_x}" y="{yb}" width="{bar_w}" height="{pbh}" fill="{bc}" opacity="0.15" clip-path="url(#pB{i})"/>')
            # 第一行：「P₁  液壓缸 1」合在一起，放在方塊上半
            parts_b.append(f'<text x="{box_x+pbw//2}" y="{yb+16}" text-anchor="middle" font-size="11" font-weight="700" fill="{bc}">{num}　{name}</text>')
            # 第二行：可靠度%，放在方塊下半
            parts_b.append(f'<text x="{box_x+pbw//2}" y="{yb+34}" text-anchor="middle" font-size="14" font-weight="900" fill="{bc}">{rv:.0%}</text>')

        # 右輸出線 + Rₛ 框（固定高，垂直置中）
        rs_c  = _pc(Rs_par)
        rs_bg = _pbg(Rs_par)
        rx    = rnode_x + out_len
        ry    = sys_cy - rs_h//2
        parts_b += [
            f'<line x1="{rnode_x}" y1="{sys_cy}" x2="{rx}" y2="{sys_cy}" stroke="#64748b" stroke-width="2"/>',
            f'<rect x="{rx}" y="{ry}" width="{rs_w}" height="{rs_h}" rx="8" fill="{rs_bg}" stroke="{rs_c}" stroke-width="2"/>',
            f'<text x="{rx+rs_w//2}" y="{ry+16}" text-anchor="middle" font-size="10" fill="#64748b">並聯系統可靠度</text>',
            f'<text x="{rx+rs_w//2}" y="{ry+36}" text-anchor="middle" font-size="17" font-weight="900" fill="{rs_c}">Rₛ = {Rs_par:.4f}</text>',
            f'<text x="{rx+rs_w//2}" y="{ry+52}" text-anchor="middle" font-size="10" fill="#94a3b8">故障率 = {fail_rate:.4f}</text>',
        ]

        # 計算式列（底部）
        ct = title_h + grp_h + 4
        eq_b = f"1−(1−{P1:.2f})(1−{P2:.2f})(1−{P3:.2f}) = 1−{fail_rate:.4f} = {Rs_par:.4f}"
        parts_b += [
            f'<rect x="4" y="{ct}" width="{SVG_W-8}" height="{calc_h-2}" rx="5" fill="#f1f5f9"/>',
            f'<text x="{SVG_W//2}" y="{ct+18}" text-anchor="middle" font-size="11" fill="#475569">Rₛ = {eq_b}</text>',
        ]
        parts_b.append("</svg>")
        st.markdown("".join(parts_b), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        fig5b = go.Figure(go.Bar(
            x=["P₁","P₂","P₃","並聯 Rₛ","串聯（對比）"],
            y=[P1, P2, P3, Rs_par, Rs_ser2],
            marker_color=[_pc(P1), _pc(P2), _pc(P3), "#22c55e","#ef4444"],
            text=[f"{v:.1%}" for v in [P1, P2, P3, Rs_par, Rs_ser2]],
            textposition="outside", textfont=dict(size=13),
            hovertemplate="%{x}<br>可靠度: %{y:.4f}<extra></extra>"
        ))
        fig5b.add_hline(y=max_p, line_dash="dash", line_color="#3b82f6", line_width=2,
                        annotation_text="最大單元=" + str(round(max_p,2)),
                        annotation_position="top right", annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig5b, "並聯 vs 串聯系統可靠度比較", "單元 / 系統", "可靠度")
        fig5b.update_layout(height=360, yaxis=dict(range=[0, 1.15]),
                            margin=dict(t=60, b=40, l=50, r=20))
        st.plotly_chart(fig5b, use_container_width=True)

        if p1==40 and p2==50 and p3==60:
            _card("#0369a1","#e0f2fe","#0c4a6e","📖 課本圖 3.8 對照（R₁=0.4, R₂=0.5, R₃=0.6）",
                  "Rₛ = 1 − (0.6×0.5×0.4) = 1 − 0.12 = <b>0.88</b>（課本答案）。"
                  "並聯讓可靠度從最高單元 0.6 躍升到 0.88！")
        else:
            _card("#22c55e","#f0fdf4","#166534","⚡ 並聯效果",
                  "並聯 Rₛ = " + str(Rs_par) + "，遠高於串聯 = " + str(Rs_ser2) +
                  "。冗餘設計是提升可靠度最有效的策略。")

    # ── 互動實驗室 C：三方案比較（課本圖 3.9）───────────────────────────
    with st.expander("🔧 設計挑戰：升級 vs 並聯備援，哪種策略更划算？（課本圖 3.9）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>情境：</b>原始串聯系統 R₁=0.90、R₂=0.80、R₃=0.95，系統可靠度 Rₛ = 0.684。<br>
                <b>工程任務：</b>預算只夠改善「最弱單元 R₂」。拉動下方滑桿，觀察系統架構圖如何變化，哪種策略效果更好？
            </div>
        </div>
        ''', unsafe_allow_html=True)

        R1_fix, R3_fix = 0.90, 0.95
        Ra = round(R1_fix * 0.80 * R3_fix, 4)

        col_sl1, col_sl2 = st.columns(2)
        with col_sl1:
            st.markdown("**① 升級策略：R₂ 升級至**")
            R2_upgrade = st.slider("升級後的 R₂", 0.80, 1.00, 0.95, 0.01, key="w3_r2_upgrade",
                                   format="%.2f", help="原始 R₂ = 0.80，往右拉代表升級品質")
        with col_sl2:
            st.markdown("**② 並聯備援：R₂ 共幾個並聯**")
            n_redundant = st.slider("並聯單元數", 2, 4, 2, 1, key="w3_n_redundant",
                                    help="2 = 原本1個 + 新增1個備援（R₂=0.80 不變）")

        check_slider("w3_r2_upgrade",  "t5_design")
        check_slider("w3_n_redundant", "t5_design")

        Rb = round(R1_fix * R2_upgrade * R3_fix, 4)
        R2_parallel = round(1 - (1 - 0.80)**n_redundant, 4)
        Rc = round(R1_fix * R2_parallel * R3_fix, 4)

        # ── SVG 架構圖：三種方案並排 ─────────────────────────────────
        def _box_color(r):
            if r >= 0.95: return "#16a34a"
            if r >= 0.85: return "#2563eb"
            if r >= 0.75: return "#d97706"
            return "#dc2626"

        def _rs_color(rs, baseline):
            return "#16a34a" if rs > baseline + 0.001 else "#1e3a5f"

        # ── 動態計算各色塊高度 ──────────────────────────────────────────
        bw, bh = 64, 36          # 方塊尺寸
        band_pad = 14            # 色塊上下 padding
        band_gap = 16            # 色塊間距
        box_gap  = 44            # 並聯方塊間距

        h_a = bh + band_pad * 2                              # (a) 色塊高度
        h_b = bh + band_pad * 2                              # (b) 色塊高度
        # (c) 高度依並聯數動態算：n 個方塊 + 間距 + padding
        h_c = n_redundant * bh + (n_redundant - 1) * (box_gap - bh) + band_pad * 2 + 10

        y_a = 20                          # (a) 色塊起點
        y_b = y_a + h_a + band_gap        # (b) 色塊起點
        y_c = y_b + h_b + band_gap        # (c) 色塊起點
        W   = 860
        H   = y_c + h_c + 20             # SVG 總高度

        # 各方案中心線 y
        mid_a = y_a + band_pad + bh // 2
        mid_b = y_b + band_pad + bh // 2

        # x 座標
        x_in = 30; x1 = 85; x2 = 245; x3 = 405; x_out = 490
        lx   = 600   # 圖例 x

        def block(x, y, label, r, highlight=False):
            bc     = _box_color(r)
            stroke = "#f59e0b" if highlight else bc
            sw     = 3 if highlight else 2
            return (
                f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" '
                f'fill="white" stroke="{stroke}" stroke-width="{sw}"/>'
                f'<text x="{x+bw//2}" y="{y+bh//2-6}" text-anchor="middle" '
                f'font-size="13" font-weight="700" fill="{bc}">{label}</text>'
                f'<text x="{x+bw//2}" y="{y+bh//2+10}" text-anchor="middle" '
                f'font-size="12" fill="#374151">{r:.2f}</text>'
            )

        def hline(x1, x2, y):
            return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#64748b" stroke-width="1.5"/>'

        def rs_badge(band_x2, band_y, band_h, rs_val, baseline, delta=None):
            """在色塊右上角畫 Rₛ badge（不會超出色塊）"""
            tx = band_x2 - 6      # 右上角，右對齊
            ty = band_y + 18      # 距頂端 18px
            color = _rs_color(rs_val, baseline)
            parts = [
                f'<text x="{tx}" y="{ty}" text-anchor="end" '
                f'font-size="13" font-weight="800" fill="{color}">Rₛ = {rs_val:.3f}</text>'
            ]
            if delta is not None:
                parts.append(
                    f'<text x="{tx}" y="{ty+16}" text-anchor="end" '
                    f'font-size="11" fill="#6b7280">+{delta:.3f}</text>'
                )
            return "".join(parts)

        svg_parts = [
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'style="background:white;border-radius:12px;border:1px solid #e2e8f0;width:100%;">',
            # ── 背景色塊（寬度到 x_out + margin）──
            f'<rect x="10" y="{y_a}" width="560" height="{h_a}" rx="8" fill="#f8fafc" stroke="#e2e8f0"/>',
            f'<rect x="10" y="{y_b}" width="560" height="{h_b}" rx="8" fill="#eff6ff" stroke="#bfdbfe"/>',
            f'<rect x="10" y="{y_c}" width="560" height="{h_c}" rx="8" fill="#f0fdf4" stroke="#86efac"/>',
            # ── 標籤（嵌在色塊內左上角）──
            f'<text x="20" y="{y_a+17}" font-size="13" font-weight="700" fill="#475569">(a) 原始串聯</text>',
            f'<text x="20" y="{y_b+17}" font-size="13" font-weight="700" fill="#1d4ed8">(b) 升級單元 2</text>',
            f'<text x="20" y="{y_c+17}" font-size="13" font-weight="700" fill="#15803d">(c) 並聯備援</text>',
        ]

        # ── (a) 原始串聯 ──────────────────────────────────────────────
        svg_parts += [
            hline(x_in, x1, mid_a),
            block(x1, mid_a - bh//2, "1", 0.90),
            hline(x1+bw, x2, mid_a),
            block(x2, mid_a - bh//2, "2", 0.80, highlight=True),
            hline(x2+bw, x3, mid_a),
            block(x3, mid_a - bh//2, "3", 0.95),
            hline(x3+bw, x_out, mid_a),
            rs_badge(570, y_a, h_a, Ra, Ra),
        ]

        # ── (b) 升級策略 ──────────────────────────────────────────────
        svg_parts += [
            hline(x_in, x1, mid_b),
            block(x1, mid_b - bh//2, "1", 0.90),
            hline(x1+bw, x2, mid_b),
            block(x2, mid_b - bh//2, "2", R2_upgrade, highlight=True),
            hline(x2+bw, x3, mid_b),
            block(x3, mid_b - bh//2, "3", 0.95),
            hline(x3+bw, x_out, mid_b),
            rs_badge(570, y_b, h_b, Rb, Ra, Rb - Ra),
        ]

        # ── (c) 並聯備援 ──────────────────────────────────────────────
        par_y_start = y_c + band_pad + 8
        par_ys      = [par_y_start + i * box_gap for i in range(n_redundant)]
        par_cy      = (par_ys[0] + par_ys[-1]) // 2 + bh // 2
        x_par_in    = x2 - 20
        x_par_out   = x2 + bw + 20

        svg_parts += [
            hline(x_in, x1, par_cy),
            block(x1, par_cy - bh//2, "1", 0.90),
            hline(x1+bw, x_par_in, par_cy),
            f'<line x1="{x_par_in}" y1="{par_ys[0]+bh//2}" x2="{x_par_in}" y2="{par_ys[-1]+bh//2}" stroke="#64748b" stroke-width="1.5"/>',
            f'<line x1="{x_par_out}" y1="{par_ys[0]+bh//2}" x2="{x_par_out}" y2="{par_ys[-1]+bh//2}" stroke="#64748b" stroke-width="1.5"/>',
        ]
        for i, py in enumerate(par_ys):
            lbl = "2" if i == 0 else "2'"
            svg_parts += [
                hline(x_par_in, x2, py + bh//2),
                block(x2, py, lbl, 0.80, highlight=True),
                hline(x2+bw, x_par_out, py + bh//2),
            ]
        svg_parts += [
            hline(x_par_out, x3, par_cy),
            block(x3, par_cy - bh//2, "3", 0.95),
            hline(x3+bw, x_out, par_cy),
            rs_badge(570, y_c, h_c, Rc, Ra, Rc - Ra),
        ]

        # ── 圖例 ──────────────────────────────────────────────────────
        leg_y = y_a
        svg_parts += [
            f'<text x="{lx}" y="{leg_y+14}" font-size="13" font-weight="700" fill="#1e3a5f">方塊顏色 = 可靠度</text>',
            f'<rect x="{lx}" y="{leg_y+22}" width="14" height="14" fill="#16a34a" rx="3"/>'
            f'<text x="{lx+20}" y="{leg_y+34}" font-size="12" fill="#374151">≥ 0.95</text>',
            f'<rect x="{lx}" y="{leg_y+44}" width="14" height="14" fill="#2563eb" rx="3"/>'
            f'<text x="{lx+20}" y="{leg_y+56}" font-size="12" fill="#374151">≥ 0.85</text>',
            f'<rect x="{lx}" y="{leg_y+66}" width="14" height="14" fill="#d97706" rx="3"/>'
            f'<text x="{lx+20}" y="{leg_y+78}" font-size="12" fill="#374151">≥ 0.75</text>',
            f'<rect x="{lx}" y="{leg_y+88}" width="14" height="14" fill="#dc2626" rx="3"/>'
            f'<text x="{lx+20}" y="{leg_y+100}" font-size="12" fill="#374151">&lt; 0.75</text>',
            f'<rect x="{lx}" y="{leg_y+114}" width="14" height="14" fill="white" stroke="#f59e0b" stroke-width="3" rx="3"/>',
            f'<text x="{lx+20}" y="{leg_y+126}" font-size="12" fill="#374151">= 被改善的單元</text>',
            # Rₛ 比較
            f'<text x="{lx}" y="{leg_y+155}" font-size="13" font-weight="700" fill="#1e3a5f">Rₛ 比較</text>',
            f'<text x="{lx}" y="{leg_y+173}" font-size="13" fill="#475569">(a) {Ra:.3f}</text>',
            f'<text x="{lx}" y="{leg_y+191}" font-size="13" fill="{_rs_color(Rb,Ra)}" font-weight="700">(b) {Rb:.3f}</text>',
            f'<text x="{lx}" y="{leg_y+209}" font-size="13" fill="{_rs_color(Rc,Ra)}" font-weight="700">(c) {Rc:.3f}</text>',
        ]

        # 勝者標示
        winner = "b" if Rb > Rc else ("c" if Rc > Rb else "tie")
        if winner == "b":
            svg_parts.append(f'<text x="{lx}" y="{leg_y+229}" font-size="12" fill="#1d4ed8" font-weight="700">▲ 升級策略較優</text>')
        elif winner == "c":
            svg_parts.append(f'<text x="{lx}" y="{leg_y+229}" font-size="12" fill="#15803d" font-weight="700">▲ 並聯備援較優</text>')
        else:
            svg_parts.append(f'<text x="{lx}" y="{leg_y+229}" font-size="12" fill="#7c3aed" font-weight="700">= 效果相同</text>')

        svg_parts.append("</svg>")
        st.markdown("".join(svg_parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_ra, col_rb, col_rc = st.columns(3)
        with col_ra: st.metric("(a) 原始 Rₛ",           f"{Ra:.4f}")
        with col_rb: st.metric(f"(b) 升級 R₂→{R2_upgrade:.2f}", f"{Rb:.4f}",
                               delta=f"+{Rb-Ra:.4f}", delta_color="normal")
        with col_rc: st.metric(f"(c) 並聯 {n_redundant} 個 R₂",  f"{Rc:.4f}",
                               delta=f"+{Rc-Ra:.4f}", delta_color="normal")

        if Rc > Rb:
            _card("#22c55e","#f0fdf4","#166534","💡 並聯備援效果更好！",
                  f"並聯 {n_redundant} 個（Rₛ = {Rc:.4f}）> 升級至 {R2_upgrade:.2f}（Rₛ = {Rb:.4f}）。<br>"
                  "不需要提升每個元件品質，只要增加備援即可大幅提升系統可靠度——這是「多餘系統（Redundant System）」的工程價值。")
        elif Rb > Rc:
            _card("#3b82f6","#eff6ff","#1e40af","💡 升級策略效果更好！",
                  f"升級至 {R2_upgrade:.2f}（Rₛ = {Rb:.4f}）> 並聯 {n_redundant} 個（Rₛ = {Rc:.4f}）。<br>"
                  "試試看：把備援數增加到 3 個，結果會如何改變？")
        else:
            _card("#7c3aed","#f5f3ff","#4c1d95","⚖️ 兩種策略效果相同",
                  f"升級與並聯備援的系統可靠度均為 {Rb:.4f}，效益相當。")

    # ── 隨堂小測驗 tab5 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§3.5 系統可靠度</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q5 = st.radio(
        "📍 **題目：某系統含 3 個並聯單元，各單元可靠度均為 0.80，整體系統可靠度 Rₛ = ？**",
        ["請選擇...", "A. 0.512", "B. 0.992", "C. 0.800", "D. 0.240"],
        key="w3_q5_radio"
    )
    if st.button("送出答案", key="w3_q5_btn"):
        if q5 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "B." in q5:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "並聯 Rₛ = 1 − (1−0.8)³ = 1 − 0.008 = 0.992。"
                  "三個 80% 可靠度的單元並聯後系統達 99.2%——冗餘備援的強大效益！")
            mark_done("t5_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "並聯公式：Rₛ = 1 − (1−R₁)(1−R₂)(1−R₃) = 1 − (0.2)³，先算故障率再相乘，最後用 1 減去。")


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
    "wp":          "w3",
    "sheet_name":  "Week 03 互動",
    "track_keys":  TRACK_KEYS,
    "groups":      GROUPS_IA,
    "labels":      LABELS_IA,
    "done_count":  done_count,
    "total_count": total_count,
    "pct":         pct_done,
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

real_password = get_weekly_password("Week 03")
if not real_password:
    real_password = "888888"

_card("#475569","#f8fafc","#334155","🔒 測驗鎖定中",
      "請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。")
_col_pw, _col_btn = st.columns([5, 1])
with _col_pw:
    user_code = st.text_input("密碼", type="password", key="w3_unlock_code",
                               label_visibility="collapsed",
                               placeholder="🔑 請輸入 6 位數解鎖密碼…")
with _col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w3_unlock_btn")

if user_code != real_password:
    if user_code != "":
        _card("#ef4444","#fef2f2","#991b1b","❌ 密碼錯誤","請確認字母與數字是否正確！")
else:
    if "w3_locked" not in st.session_state:
        st.session_state.w3_locked = False
    _card("#22c55e","#f0fdf4","#166534","🔓 密碼正確！","測驗已解鎖，請完成以下題目後送出。")
    _card("#3b82f6","#eff6ff","#1e40af","📋 測驗說明",
          "4 題，每題 25 分，共 100 分。作答送出後即鎖定成績，請確實核對學號與驗證碼！")

    st.markdown(
        '<style>'
        '.st-key-w3_quiz_container > div:first-child {'
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
    with st.container(border=True, key="w3_quiz_container"):
        c_id, c_name, c_code = st.columns(3)
        with c_id:   st_id    = st.text_input("📝 學號",   key="w3_quiz_id",   placeholder="請輸入學號")
        with c_name: st_name  = st.text_input("📝 姓名",   key="w3_quiz_name", placeholder="請輸入姓名")
        with c_code: st_vcode = st.text_input("🔑 驗證碼", key="w3_quiz_code", placeholder="個人驗證碼", type="password")
    with st.form("week3_unified_quiz"):
        st.markdown("---")

        q1f = st.radio(
            "**Q1（§3.1）：某批 50 個混凝土試體中，強度合格 42 個、不合格 8 個。"
            "隨機抽 1 個，P(合格) = ？**",
            ["請選擇...", "A. 42/50 = 0.84", "B. 8/50 = 0.16", "C. 42/8 = 5.25", "D. 無法確定"],
            key="w3_qf1"
        )
        q2f = st.radio(
            "**Q2（§3.2）：P(A)=0.5，P(B)=0.4，P(A∩B)=0.2，則 P(A∪B) = ？**",
            ["請選擇...", "A. 0.90", "B. 0.70", "C. 0.20", "D. 0.30"],
            key="w3_qf2"
        )
        q3f = st.radio(
            "**Q3（§3.3）：P(A∩B)=0.12，P(B)=0.4，P(A)=0.3，"
            "則 P(A|B) = ？且 A 與 B 是否統計獨立？**",
            ["請選擇...",
             "A. P(A|B)=0.30，統計獨立",
             "B. P(A|B)=0.48，相依",
             "C. P(A|B)=0.20，相依",
             "D. P(A|B)=0.30，相依"],
            key="w3_qf3"
        )
        q4f = st.radio(
            "**Q4（§3.5）：原始串聯系統 R₁=0.90, R₂=0.80, R₃=0.95（Rₛ=0.684）。"
            "若對單元 2 新增一個相同規格的並聯備援（R₂'=0.80），升級後整體系統可靠度最接近？**",
            ["請選擇...", "A. 0.684", "B. 0.812", "C. 0.821", "D. 0.950"],
            key="w3_qf4"
        )
        st.markdown("---")

        if st.form_submit_button("✅ 簽署並送出本週測驗",
                                  disabled=st.session_state.w3_locked):
            if st_id and st_name and st_vcode:
                is_valid, student_idx = verify_student(st_id, st_name, st_vcode)
                if not is_valid:
                    _card("#ef4444","#fef2f2","#991b1b","⛔ 身分驗證失敗",
                          "您輸入的學號、姓名或驗證碼有誤，請重新確認！")
                elif check_has_submitted(st_id, "Week 03"):
                    _card("#ef4444","#fef2f2","#991b1b","⛔ 拒絕送出",
                          "系統查詢到您已繳交過 Week 03 的測驗！請勿重複作答。")
                else:
                    score = 0
                    if q1f.startswith("A."): score += 25   # 0.84
                    if q2f.startswith("B."): score += 25   # 0.70
                    if q3f.startswith("A."): score += 25   # P(A|B)=0.30，獨立
                    if q4f.startswith("C."): score += 25   # 0.821
                    detail_str = ("Q1:" + q1f[:2] + ",Q2:" + q2f[:2] +
                                  ",Q3:" + q3f[:2] + ",Q4:" + q4f[:2])
                    success = save_score(student_idx, st_id, st_name,
                                         "Week 03", detail_str, score)
                    if success:
                        st.session_state.w3_locked = True
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
                                  "機率與系統可靠度的核心概念全數掌握！")
                        elif score >= 75:
                            _card("#3b82f6","#eff6ff","#1e40af","👍 表現不錯！",
                                  "建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。")
                        else:
                            _card("#f59e0b","#fffbeb","#92400e","📖 繼續加油！",
                                  "請回顧本週各節的概念說明與互動實驗，機率的邏輯需要多練習！")
            else:
                _card("#f59e0b","#fffbeb","#92400e","⚠️ 資料不完整",
                      "請完整填寫學號、姓名與驗證碼再送出表單。")

    if st.session_state.w3_locked:
        _card("#475569","#f8fafc","#334155","🔒 測驗已鎖定",
              "系統已安全登錄您的成績，如有疑問請聯繫授課教師。")


# ══════════════════════════════════════════════════════════════════════
#  底部速查卡
# ══════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("📚 本週核心概念速查卡（考前複習用）", expanded=False):
    _cards = [
        ("#0f766e","#f0fdfa","#134e4a","📌 §3.1 統計基本概念",
         ["P(事件) = 事件集 ÷ 樣本空間（等機率）",
          "餘事件：P(A) = 1 − P(非A)",
          "互斥事件：P(A且B) = 0",
          "機率範圍：0 ≤ P(A) ≤ 1"]),
        ("#7c3aed","#f5f3ff","#4c1d95","📐 §3.2 複合事件",
         ["加法通式：P(A∪B) = P(A)+P(B)−P(A∩B)",
          "互斥加法：P(A∪B) = P(A)+P(B)",
          "獨立乘法：P(A∩B) = P(A)×P(B)",
          "至少1次 = 1 − 全無（餘事件法則）"]),
        ("#0369a1","#e0f2fe","#0c4a6e","🔍 §3.3 條件機率",
         ["P(A|B) = P(A∩B) ÷ P(B)",
          "獨立判斷：P(A|B)=P(A) ⟺ 統計獨立",
          "相依事件：P(A|B) ≠ P(A)",
          "非條件機率 P(A) 不受其他事件影響"]),
        ("#d97706","#fef3c7","#92400e","🌳 §3.4 乘法法則與機率樹",
         ["通式：P(A∩B) = P(A)×P(B|A)",
          "機率樹路徑機率 = 各枝乘積",
          "各路徑總和恆為 1（完備性）",
          "不還原抽樣：分母逐次遞減"]),
        ("#22c55e","#f0fdf4","#166534","⚙️ §3.5 系統可靠度",
         ["串聯：Rₛ = R₁×R₂×…×Rₙ ≤ min(Rᵢ)",
          "並聯：Rₛ = 1−(1−R₁)…(1−Rₙ) ≥ max(Rᵢ)",
          "複合系統：先算子系統再整合",
          "重複（並聯備援）> 升級單元"]),
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

# ── 版權 badge
render_copyright()