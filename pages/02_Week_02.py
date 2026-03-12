# 檔案位置： D:\Engineering_Statistics_App\pages\02_Week_02.py
from utils.auth import require_login
require_login()
try:
    from utils.sidebar import render_sidebar
    _sidebar_ok = True
except Exception:
    _sidebar_ok = False

import streamlit as st
import pandas as pd
import numpy as np

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

try:
    from utils.gsheets_db import save_score, check_has_submitted, verify_student, get_weekly_password
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
if "w2_locked" not in st.session_state:
    st.session_state.w2_locked = False

# ── 互動追蹤 key 清單（Section 2a 用）────────────────────────────────

if _sidebar_ok:
    render_sidebar(current_page="Week 02")

TRACK_KEYS = {
    "t1_bins":   False,   # Tab1 實驗室C 組數滑桿（需移動才算）
    "t1_stem":   False,   # Tab1 實驗室B 莖葉圖（展開才算）
    "t1_table":  False,   # Tab1 實驗室A 逐步次數分配表（完成才算）
    "t1_quiz":   False,   # Tab1 隨堂測驗（答對才算）
    "t2_skew":   False,   # Tab2 偏態滑桿（需移動才算）
    "t2_calc":   False,   # Tab2 逐步計算（完成才算）
    "t2_quiz":   False,   # Tab2 隨堂測驗（答對才算）
    "t3_std":    False,   # Tab3 標準差滑桿（需移動才算）
    "t3_box":    False,   # Tab3 箱型圖滑桿（需移動才算）
    "t3_calc":   False,   # Tab3 逐步計算（完成才算）
    "t3_quiz":   False,   # Tab3 隨堂測驗（答對才算）
    "t4_prop":   False,   # Tab4 比例滑桿（需移動才算）
    "t4_calc":   False,   # Tab4 逐步計算（完成才算）
    "t4_quiz":   False,   # Tab4 隨堂測驗（答對才算）
}
for k in TRACK_KEYS:
    if "w2_track_" + k not in st.session_state:
        st.session_state["w2_track_" + k] = False

# 滑桿初始值記錄（偵測是否真正移動過）
_SLIDER_INIT = {
    "w2_bins_slider": 8,
    "w2_skew_slider": 120,
    "w2_tol": 5, "w2_sd1": 2, "w2_sd2": 4,
    "w2_kpct": 85,
    "w2_prop_n": 10,
}
for _sk in _SLIDER_INIT:
    if "w2_sld_moved_" + _sk not in st.session_state:
        st.session_state["w2_sld_moved_" + _sk] = False

def mark_done(key):
    st.session_state["w2_track_" + key] = True

def check_slider(slider_key, track_key):
    """若滑桿已從初始值移動，標記為完成"""
    cur = st.session_state.get(slider_key)
    init = _SLIDER_INIT.get(slider_key)
    if cur is not None and cur != init:
        st.session_state["w2_sld_moved_" + slider_key] = True
    if st.session_state.get("w2_sld_moved_" + slider_key, False):
        mark_done(track_key)

def count_done():
    return sum(1 for k in TRACK_KEYS if st.session_state.get("w2_track_" + k, False))

# =====================================================================
# Hero 卡片
# =====================================================================
st.markdown('''
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
    border-radius:16px;padding:28px 40px 24px 40px;
    margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">
    <div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;margin:0 0 8px 0;line-height:1.25;">
        Week 02｜統計資料之描述與探討 📊
    </div>
    <div style="color:#94a3b8;font-size:1.05rem;margin:0 0 10px 0;">
        Describing &amp; Presenting Statistical Data · Chapter 2
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.22);
        border-radius:20px;padding:5px 16px;">
        <span style="color:#93c5fd;font-size:0.82rem;">📖</span>
        <span style="color:#e2e8f0;font-size:0.82rem;font-weight:600;">課本第 2 章 · §2.1–2.4</span>
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

# 學習路線
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
            §2.1 次數分配 → §2.2 位置的測度 → §2.3 差異性的量度 → §2.4 比例
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

# Section 1 Header
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📚 1. 本週核心理論與互動實驗室</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標籤，完成理論閱讀與互動實驗</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 2.1 次數分配",
    "📍 2.2 位置的測度",
    "📦 2.3 差異性的量度",
    "⚖️ 2.4 比例",
])

# =====================================================================
# ██████████  TAB 1 — §2.1 次數分配  ██████████
# =====================================================================
with tab1:

    # ── 層次 1 核心概念 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§2.1 次數分配</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>次數分配 (Frequency Distribution)</b>：將大量原始資料依據數值大小，
            分組整理成各組出現次數的彙總表，是資料描述的第一步。<br><br>
            ▸ <b>組數 (k)</b>：通常取 5～20 組，組數太少失去細節，太多看不出趨勢<br>
            ▸ <b>組距 (w)</b>：w = (最大值 − 最小值) ÷ k，各組寬度一致<br>
            ▸ <b>組中點 (mₖ)</b>：每組上下限的平均值，是該組資料的代表值<br>
            ▸ <b>累積次數</b>：由小到大累加各組次數，用於繪製 Ogive 曲線<br>
            ▸ <b>莖葉圖 (Stem-and-Leaf)</b>：保留原始數值的圖形化次數分配，莖=前位數，葉=末位數
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#f8fafc;border:1px solid #e2e8f0;
                border-left:4px solid #0369a1;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
        <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                    letter-spacing:0.05em;margin-bottom:5px;">🔧 工程應用場景</div>
        <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
            <b>情境：精密零件檢查時間（秒）</b><br>
            品管部門對 100 個精密零件逐一進行外觀檢查，記錄每個零件的檢查時間（秒）。
            資料範圍 10～22 秒。工程師需要整理成次數分配表，以便了解檢查效率分佈，
            決定是否需要優化作業流程。
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 四工具小卡片（R2 風格，補入莖葉圖）────────────────────────────
    st.markdown('''
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin:14px 0 6px 0;">
        <div style="border-radius:12px;overflow:hidden;border:1px solid #99f6e4;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#0f766e;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.9rem;">📋 次數分配表</span>
            </div>
            <div style="background:#f0fdfa;padding:11px 14px;color:#134e4a;font-size:0.9rem;line-height:1.7;">
                將資料依數值大小分組，列出各組的資料個數（次數）。是所有圖表的資料來源。
            </div>
        </div>
        <div style="border-radius:12px;overflow:hidden;border:1px solid #99f6e4;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#0f766e;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.9rem;">📊 直方圖 (Histogram)</span>
            </div>
            <div style="background:#f0fdfa;padding:11px 14px;color:#134e4a;font-size:0.9rem;line-height:1.7;">
                以相連矩形的<b>面積</b>代表次數。能直觀看出資料分布的形狀，是品管最常用的圖。
            </div>
        </div>
        <div style="border-radius:12px;overflow:hidden;border:1px solid #99f6e4;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#0f766e;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.9rem;">📈 Ogive（累積次數多邊形）</span>
            </div>
            <div style="background:#f0fdfa;padding:11px 14px;color:#134e4a;font-size:0.9rem;line-height:1.7;">
                描繪「截至某值共有多少資料」。可快速回答：「有幾 % 的產品低於規格？」
            </div>
        </div>
        <div style="border-radius:12px;overflow:hidden;border:1px solid #99f6e4;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#0f766e;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.9rem;">🌿 莖葉圖 (Stem-and-Leaf)</span>
            </div>
            <div style="background:#f0fdfa;padding:11px 14px;color:#134e4a;font-size:0.9rem;line-height:1.7;">
                保留每個原始數值，莖=前位數，葉=末位數。旋轉 90° 即為直方圖，適合小中型資料。
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 四工具示意圖（2×2 四宮格，簡潔版）─────────────────────────────
    import pandas as _pd2

    # 資料（課本表 2.2，n=100）
    _freqs_demo  = [2, 16, 29, 27, 11, 6, 4, 2, 2, 1]
    _mids_demo   = [11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5,20.5]
    _uppers_demo = [12,13,14,15,16,17,18,19,20,21]
    _cumfreq_demo= [2,18,47,74,85,91,95,97,99,100]
    _x_og_demo   = [11.0] + _uppers_demo
    _y_og_demo   = [0] + _cumfreq_demo

    _col_a, _col_b = st.columns(2)
    _col_c, _col_d = st.columns(2)

    # ① 次數分配表
    with _col_a:
        st.markdown('<div style="color:#0f766e;font-weight:700;font-size:0.88rem;'
                    'margin-bottom:3px;">① 次數分配表（課本表 2.2）</div>',
                    unsafe_allow_html=True)
        _df_show = _pd2.DataFrame({
            "時間（秒）": [
                "11.0 – 小於 12.0", "12.0 – 小於 13.0", "13.0 – 小於 14.0",
                "14.0 – 小於 15.0", "15.0 – 小於 16.0", "16.0 – 小於 17.0",
                "17.0 – 小於 18.0", "18.0 – 小於 19.0", "19.0 – 小於 20.0",
                "20.0 – 小於 21.0",
            ],
            "檢查次數": _freqs_demo,
        })
        # 加總列
        import pandas as _pd3
        _df_total = _pd3.DataFrame({"時間（秒）": ["總次數"], "檢查次數": [100]})
        _df_full  = _pd3.concat([_df_show, _df_total], ignore_index=True)
        st.dataframe(_df_full, hide_index=True, use_container_width=True, height=420)

    # ② 直方圖
    with _col_b:
        st.markdown('<div style="color:#0f766e;font-weight:700;font-size:0.88rem;'
                    'margin-bottom:3px;">② 直方圖 (Histogram)</div>',
                    unsafe_allow_html=True)
        _fig_hist2 = go.Figure(go.Bar(
            x=_mids_demo, y=_freqs_demo, width=0.88,
            marker_color='#0f766e', opacity=0.85,
            text=_freqs_demo, textposition='outside', textfont=dict(size=10),
        ))
        _fig_hist2.update_layout(
            height=330, margin=dict(t=10, b=40, l=40, r=10),
            paper_bgcolor='#f0fdfa', plot_bgcolor='#f0fdfa',
            xaxis=dict(title='時間（秒）', showgrid=False),
            yaxis=dict(title='次數', showgrid=True, gridcolor='#e2e8f0'),
        )
        st.plotly_chart(_fig_hist2, use_container_width=True)

    # ③ Ogive
    with _col_c:
        st.markdown('<div style="color:#0f766e;font-weight:700;font-size:0.88rem;'
                    'margin-bottom:3px;">③ Ogive（累積次數曲線）</div>',
                    unsafe_allow_html=True)
        _fig_og2 = go.Figure(go.Scatter(
            x=_x_og_demo, y=_y_og_demo, mode='lines+markers',
            line=dict(color='#0f766e', width=2.5),
            marker=dict(size=7, color='#0f766e'),
        ))
        _fig_og2.update_layout(
            height=280, margin=dict(t=10, b=40, l=50, r=10),
            paper_bgcolor='#f0fdfa', plot_bgcolor='#f0fdfa',
            xaxis=dict(title='時間（秒）', showgrid=False),
            yaxis=dict(title='累積次數', showgrid=True, gridcolor='#e2e8f0', range=[0,110]),
        )
        st.plotly_chart(_fig_og2, use_container_width=True)

    # ④ 莖葉圖
    with _col_d:
        st.markdown('<div style="color:#0f766e;font-weight:700;font-size:0.88rem;'
                    'margin-bottom:3px;">④ 莖葉圖（每格都是真實數值）</div>',
                    unsafe_allow_html=True)
        _stem_txt = (
            "莖 │ 葉\n"
            "───┼────────────────────────────────\n"
            "11 │ 5  7\n"
            "12 │ 0  0  0  3  4  4  5  5  6  7  8  8  8  9  9  9\n"
            "13 │ 0  0  1  1  1  2  2  2  3  3  4  5  5  5  6  6\n"
            "   │ 6  6  8  8  8  8  8  9  9\n"
            "14 │ 0  0  1  2  2  2  3  3  3  3  4  4  4  5  5  6\n"
            "   │ 6  7  7  7  8  9  9  9  9  9  9\n"
            "15 │ 2  2  5  5  5  7  7  8  8  9  9\n"
            "16 │ 1  2  5  6  7  8\n"
            "17 │ 1  2  3  4\n"
            "18 │ 2  5\n"
            "19 │ 4  7\n"
            "20 │ 6\n"
            "───┴────────────────────────────────\n"
            "莖=整數秒，葉=小數第一位\n"
            "例：13│5 = 13.5 秒"
        )
        st.code(_stem_txt, language=None)

        # ── 產生固定情境資料（檢查時間，整數，n=100，範圍10~22）────────
    np.random.seed(42)
    raw_times = np.concatenate([
        np.random.randint(10, 15, 25),
        np.random.randint(13, 19, 50),
        np.random.randint(17, 23, 25)
    ])
    np.random.shuffle(raw_times)
    raw_times = np.clip(raw_times, 10, 22)

    # =====================================================================
    # 實驗室 A：逐步手算次數分配表（層次 5b）—— 先填表，建立分組概念
    # =====================================================================
    with st.expander("✏️ 展開實驗室 A：逐步手算次數分配表（課本表 2.1 互動版）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>親手計算「組中點」與「累積次數」，理解次數分配表每欄的含義<br>
                <b>你會發現：</b>組中點是組距的幾何中心，累積次數是從小到大依序疊加的結果
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # 定義 6 組（k=6，組距=2）
        groups_c = [
            {"label": "10 ~ 12", "lower": 10, "upper": 12, "freq": int(np.sum((raw_times >= 10) & (raw_times <= 11)))},
            {"label": "12 ~ 14", "lower": 12, "upper": 14, "freq": int(np.sum((raw_times >= 12) & (raw_times <= 13)))},
            {"label": "14 ~ 16", "lower": 14, "upper": 16, "freq": int(np.sum((raw_times >= 14) & (raw_times <= 15)))},
            {"label": "16 ~ 18", "lower": 16, "upper": 18, "freq": int(np.sum((raw_times >= 16) & (raw_times <= 17)))},
            {"label": "18 ~ 20", "lower": 18, "upper": 20, "freq": int(np.sum((raw_times >= 18) & (raw_times <= 19)))},
            {"label": "20 ~ 22", "lower": 20, "upper": 22, "freq": int(np.sum((raw_times >= 20) & (raw_times <= 22)))},
        ]
        true_midpoints_c = [(g["lower"] + g["upper"]) / 2 for g in groups_c]
        true_cumfreq_c   = list(np.cumsum([g["freq"] for g in groups_c]))
        n_total_c        = sum(g["freq"] for g in groups_c)

        _card("#0369a1", "#e0f2fe", "#0c4a6e", "📋 步驟一：觀察次數資料",
              "以下為 k=6 組（組距=2秒）的分組次數，已幫你統計好。"
              "請先確認各組次數，再進行步驟二。")

        df_given_c = pd.DataFrame({
            "組別": [g["label"] for g in groups_c],
            "次數 fₖ": [g["freq"] for g in groups_c],
        })
        st.dataframe(df_given_c, hide_index=True, use_container_width=True)
        st.markdown("**➡️ 樣本總數 n = " + str(n_total_c) + " 筆**")
        st.markdown("---")

        # 步驟二：填組中點
        _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟二：計算各組的組中點 mₖ",
              "組中點 = (組下限 + 組上限) ÷ 2，請填入前 3 組的組中點（整數或 .0 均可）：")

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            m1 = st.number_input("第 1 組 (10~12)", value=0.0, step=0.5, format="%.1f", key="w2_c_m1")
        with col_m2:
            m2 = st.number_input("第 2 組 (12~14)", value=0.0, step=0.5, format="%.1f", key="w2_c_m2")
        with col_m3:
            m3 = st.number_input("第 3 組 (14~16)", value=0.0, step=0.5, format="%.1f", key="w2_c_m3")

        step2c_errors = []
        step2c_done = False
        inputs_m = [m1, m2, m3]
        # 只驗證「已動過」的格（不等於預設 0.0），避免還沒填就顯示錯誤
        _filled = [(i, inp) for i, inp in enumerate(inputs_m) if inp != 0.0]
        if _filled:
            for i, inp in _filled:
                true_m = true_midpoints_c[i]
                if abs(inp - true_m) > 0.01:
                    step2c_errors.append(
                        "第 " + str(i+1) + " 組：(" + str(groups_c[i]["lower"]) +
                        "+" + str(groups_c[i]["upper"]) + ")÷2 = <b>" + str(true_m) + "</b>，你填了 " + str(inp)
                    )
            if step2c_errors:
                for e in step2c_errors:
                    _card("#ef4444", "#fef2f2", "#991b1b", "❌ 組中點有誤", e)
            elif len(_filled) == 3:
                # 三格都填且全對才顯示完成
                step2c_done = True
                _card("#22c55e", "#f0fdf4", "#166534", "✅ 步驟二完成！",
                      "三組組中點均正確：11.0、13.0、15.0 秒。其餘各組（17.0、19.0、21.0）系統已自動帶入，請繼續步驟三。")
                mark_done("t1_table")
            else:
                # 已填的格都正確，但還沒填完，給鼓勵提示
                _card("#0369a1", "#e0f2fe", "#0c4a6e", "✅ 已填的組中點正確！",
                      "請繼續填入其餘組的組中點。")
        st.markdown("---")

        # 步驟三：填最後一組累積次數
        _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟三：計算第 6 組的累積次數",
              "累積次數 = 從第 1 組到本組次數的加總。第 6 組的累積次數是多少？")

        cum6 = st.number_input("第 6 組累積次數 = ?", value=0, step=1, key="w2_c_cum6")
        step3c_done = False
        if cum6 != 0:
            if cum6 == true_cumfreq_c[5]:
                step3c_done = True
                _card("#22c55e", "#f0fdf4", "#166534",
                      "✅ 正確！累積次數 = " + str(true_cumfreq_c[5]),
                      "第 6 組的累積次數等於樣本總數 n=" + str(n_total_c) + "，因為全部資料都已涵蓋在內。")
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再確認一次",
                      "提示：第 6 組的累積次數 = 所有組次數的總和 = n，你填了 " + str(cum6))

        # 解鎖完整表格
        if step2c_done and step3c_done:
            st.markdown("---")
            _card("#7c3aed", "#f5f3ff", "#4c1d95", "🎉 完整次數分配表已解鎖！", "以下是完整的次數分配表——包含組中點與累積次數：")

            df_full_c = pd.DataFrame({
                "組別":    [g["label"] for g in groups_c],
                "次數 fₖ": [g["freq"]  for g in groups_c],
                "組中點 mₖ": true_midpoints_c,
                "累積次數": true_cumfreq_c,
                "累積 %":  [f"{v/n_total_c*100:.1f}%" for v in true_cumfreq_c],
            })
            st.dataframe(df_full_c, hide_index=True, use_container_width=True)
        else:
            if not step2c_done:
                st.info("💡 請先完成步驟二（正確填入前 3 組組中點），再繼續步驟三。")
            elif not step3c_done:
                st.info("💡 請完成步驟三（填入第 6 組累積次數），即可解鎖完整表格。")

        col_r, _ = st.columns([1, 4])
        with col_r:
            if st.button("🔄 重新開始實驗室 A", key="w2_reset_a"):
                for k in ["w2_c_m1", "w2_c_m2", "w2_c_m3", "w2_c_cum6"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # 實驗室 B：莖葉圖（等寬字體對齊）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 B：莖葉圖（保留原始數值的次數分配）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解莖葉圖如何在「彙整」的同時「保留」每一個原始數值<br>
                <b>你會發現：</b>莖葉圖旋轉 90° 就是直方圖，但多了可以還原個別數值的能力
            </div>
        </div>
        ''', unsafe_allow_html=True)

        mark_done("t1_stem")

        # 建立莖葉圖（莖 = 十位數，葉 = 個位數）
        stem_dict = {}
        for v in sorted(raw_times):
            stem = v // 10
            leaf = v % 10
            stem_dict.setdefault(stem, []).append(leaf)

        stem_lines = []
        for s in sorted(stem_dict.keys()):
            leaves_str = " ".join(str(l) for l in sorted(stem_dict[s]))
            count = len(stem_dict[s])
            stem_lines.append(f"  {s} │ {leaves_str:<30s} ({count:2d})")

        stem_text = "莖 │ 葉\n" + "─" * 45 + "\n"
        stem_text += "\n".join(stem_lines)
        stem_text += "\n" + "─" * 45
        stem_text += "\n說明：莖 = 十位數，葉 = 個位數"
        stem_text += "\n       例：1 │ 3 表示數值 13（秒）"

        st.markdown('''
        <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                    border:1px solid #99f6e4;margin:8px 0 14px 0;">
            <div style="background:#0f766e;padding:10px 18px;">
                <span style="color:white;font-weight:700;font-size:1.0rem;">
                    🌿 莖葉圖｜100 個零件檢查時間（秒）
                </span>
            </div>
            <div style="background:#f0fdfa;padding:16px 20px;">
        ''', unsafe_allow_html=True)

        st.code(stem_text, language=None)

        st.markdown('''
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #7c3aed;
                    border-radius:8px;padding:10px 16px;margin:8px 0;">
            <div style="color:#4c1d95;font-size:1.0rem;line-height:1.7;">
                📐 <b>莖葉圖的優勢</b>：<br>
                ① 直接顯示每個原始數值（不遺失資料）<br>
                ② 旋轉 90° 即等同直方圖，可直接比較各組次數<br>
                ③ 適合 n ≤ 150 的小中型資料集，n 太大則葉片太多難以閱讀
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # =====================================================================
    # 實驗室 C：組數滑桿探索（直方圖 + Ogive）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 C：組數選擇對直方圖的影響", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解「組數選擇」如何影響資料的呈現方式與可讀性<br>
                <b>你會發現：</b>組數太少→資訊被掩蓋；組數太多→每組稀疏看不出趨勢；
                適當組數才能讓資料的分佈形狀清晰顯現
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("**📋 原始資料（100 個零件檢查時間，單位：秒）**")
        raw_str = "  ".join(str(x) for x in raw_times)
        st.code(raw_str, language=None)

        n_bins = st.slider("🔢 請選擇組數 k — 拖動滑桿觀察直方圖變化（建議範圍 5～20）", 3, 20, 8, 1, key="w2_bins_slider")
        check_slider("w2_bins_slider", "t1_bins")

        # 計算組距與各組
        data_min, data_max = int(raw_times.min()), int(raw_times.max())
        w = (data_max - data_min) / n_bins

        col_hist, col_ogive = st.columns(2)

        with col_hist:
            fig_hist = go.Figure()
            counts, bin_edges = np.histogram(raw_times, bins=n_bins,
                                             range=(data_min, data_max + 0.01))
            midpoints = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(counts))]
            labels = [f"{bin_edges[i]:.1f}~{bin_edges[i+1]:.1f}" for i in range(len(counts))]

            fig_hist.add_trace(go.Bar(
                x=midpoints, y=counts,
                width=[w * 0.92] * len(counts),
                marker_color="#0f766e",
                text=counts, textposition="outside",
                textfont=dict(size=F_ANNOTATION),
                hovertemplate="區間：%{customdata}<br>次數：%{y}<extra></extra>",
                customdata=labels, name="次數"
            ))
            set_chart_layout(fig_hist, "直方圖（k=" + str(n_bins) + " 組）", "檢查時間（秒）", "次數")
            fig_hist.update_layout(
                height=420,
                yaxis=dict(range=[0, max(counts) * 1.3]),
                margin=dict(t=60, b=40, l=50, r=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_ogive:
            cum_counts = np.cumsum(counts)
            cum_pct = cum_counts / len(raw_times) * 100
            upper_bounds = [bin_edges[i+1] for i in range(len(counts))]
            x_ogive = [bin_edges[0]] + list(upper_bounds)
            y_ogive = [0] + list(cum_pct)

            fig_ogive = go.Figure()
            fig_ogive.add_trace(go.Scatter(
                x=x_ogive, y=y_ogive,
                mode="lines+markers",
                line=dict(color="#0f766e", width=3),
                marker=dict(size=8, color="#0f766e"),
                hovertemplate="上限：%{x:.1f} 秒<br>累積：%{y:.1f}%<extra></extra>",
                name="累積 %"
            ))
            set_chart_layout(fig_ogive, "Ogive 累積次數曲線", "檢查時間（秒）", "累積百分比（%）")
            fig_ogive.update_layout(height=420, yaxis=dict(range=[0, 110]),
                                    margin=dict(t=60, b=40, l=50, r=20))
            st.plotly_chart(fig_ogive, use_container_width=True)

        # 即時回饋
        w_actual = (data_max - data_min) / n_bins
        if n_bins < 5:
            _card("#ef4444", "#fef2f2", "#991b1b", "⚠️ 組數太少",
                  "只有 " + str(n_bins) + " 組，組距 " + f"{w_actual:.1f}" +
                  " 秒，太寬了！大量資料被合併在同一組，分佈形狀完全看不出來。")
        elif n_bins > 15:
            _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 組數太多",
                  str(n_bins) + " 組，組距 " + f"{w_actual:.1f}" +
                  " 秒，每組資料太少（可能只有 0~1 筆），折線圖變成鋸齒狀，失去彙整意義。")
        else:
            _card("#22c55e", "#f0fdf4", "#166534", "✅ 組數適當",
                  str(n_bins) + " 組，組距 " + f"{w_actual:.1f}" +
                  " 秒。這個範圍（5~15 組）能清楚顯示資料的分佈趨勢，右側 Ogive 曲線也平滑。")

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #22c55e;
                    border-radius:8px;padding:10px 16px;margin:12px 0 0 0;">
            <div style="color:#166534;font-size:1.0rem;line-height:1.7;">
                💡 <b>工程決策應用</b>：從 Ogive 曲線估算「規格內良率」——
                例如品管要求檢查時間不超過 18 秒，從曲線直接讀出累積百分比，
                就是符合規格的零件比例，不需要計算每一個！
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # =====================================================================
    # ── 隨堂測驗 Tab1 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:16px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：次數分配的判斷</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    q1 = st.radio(
        "📍 **組距 = (最大值 − 最小值) ÷ k。若資料範圍為 10～22 秒，想分成 6 組，組距應為多少秒？**",
        ["請選擇...", "A. 1 秒", "B. 2 秒", "C. 3 秒", "D. 6 秒"],
        key="w2_q1"
    )
    if st.button("送出答案", key="w2_btn_q1"):
        if q1 == "請選擇...":
            _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 請先選擇答案", "請先勾選一個選項再送出。")
        elif q1 == "B. 2 秒":
            _card("#22c55e", "#f0fdf4", "#166534", "🎉 恭喜答對！",
                  "組距 = (22 − 10) ÷ 6 = 12 ÷ 6 = <b>2 秒</b>。每組涵蓋 2 秒的範圍，共 6 組可完整涵蓋資料。")
            mark_done("t1_quiz")
        else:
            _card("#ef4444", "#fef2f2", "#991b1b", "❌ 提示",
                  "代入公式：組距 = (最大值 − 最小值) ÷ 組數 = (22 − 10) ÷ 6 = ？")


# =====================================================================
# ██████████  TAB 2 — §2.2 位置的測度  ██████████
# =====================================================================
with tab2:

    # ── 層次 1 核心概念 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§2.2 位置的測度</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            位置的測度描述資料「集中在哪裡」，常用三種：<br><br>
            ▸ <b>算術平均數 X̄</b>：所有觀測值的總和除以 n。受極端值影響大。<br>
            ▸ <b>中位數 (Median)</b>：資料由小到大排列後，位於正中間的值。對極端值不敏感。<br>
            ▸ <b>眾數 (Mode)</b>：出現次數最多的值。<br><br>
            ▸ <b>偏態（Skewness）與三者關係</b>：<br>
            &nbsp;&nbsp;&nbsp;右偏（正偏）→ 右尾較長 → 均值 &gt; 中位數 &gt; 眾數<br>
            &nbsp;&nbsp;&nbsp;左偏（負偏）→ 左尾較長 → 均值 &lt; 中位數 &lt; 眾數<br>
            &nbsp;&nbsp;&nbsp;對稱分佈 → 均值 ≈ 中位數 ≈ 眾數
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 公式卡 ────────────────────────────────────────────────────────
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;
                background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 算術平均數（原始資料）</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                X̄ = Σxᵢ / n<br>
                <small style="color:#7c3aed;font-size:0.88rem;">xᵢ：每個觀測值；n：樣本數</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 中位數（奇數 n）</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                Median = x₍ₙ₊₁₎/₂<br>
                <small style="color:#7c3aed;font-size:0.88rem;">排序後第 (n+1)/2 個值</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 名詞卡片：均值 / 中位數 / 眾數 ─────────────────────────────────
    st.markdown('''
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin:14px 0;">
        <div style="border-radius:12px;overflow:hidden;border:1px solid #ddd6fe;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#7c3aed;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 算術平均數 X̄</span>
            </div>
            <div style="background:#f5f3ff;padding:12px 14px;color:#4c1d95;font-size:0.95rem;line-height:1.8;">
                <b>X̄ = Σxᵢ / n</b><br>
                所有觀測值加總再除以 n<br>
                <span style="color:#7c3aed;font-size:0.88rem;">⚠️ 受極端值影響大</span>
            </div>
        </div>
        <div style="border-radius:12px;overflow:hidden;border:1px solid #bfdbfe;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#0369a1;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 中位數 Median</span>
            </div>
            <div style="background:#e0f2fe;padding:12px 14px;color:#0c4a6e;font-size:0.95rem;line-height:1.8;">
                排序後位於<b>中間</b>的值<br>
                n 為奇數：第 (n+1)/2 個<br>
                <span style="color:#0369a1;font-size:0.88rem;">✅ 對極端值不敏感</span>
            </div>
        </div>
        <div style="border-radius:12px;overflow:hidden;border:1px solid #bbf7d0;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="background:#15803d;padding:9px 14px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 眾數 Mode</span>
            </div>
            <div style="background:#f0fdf4;padding:12px 14px;color:#14532d;font-size:0.95rem;line-height:1.8;">
                出現<b>次數最多</b>的值<br>
                可能有多個或不存在<br>
                <span style="color:#15803d;font-size:0.88rem;">適合類別型資料</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 偏態與三量數關係示意 ─────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;margin:0 0 14px 0;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
        <div style="background:#1e3a5f;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📊 偏態（Skewness）與三個位置量數的關係</span>
        </div>
        <div style="background:#f8fafc;padding:14px 18px;">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;">
                <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:12px 14px;text-align:center;">
                    <div style="font-size:1.1rem;font-weight:700;color:#c2410c;margin-bottom:6px;">右偏（正偏）</div>
                    <div style="color:#7c3aed;font-size:1.05rem;font-weight:600;">眾數 &lt; 中位數 &lt; 均值</div>
                    <div style="color:#6b7280;font-size:0.88rem;margin-top:6px;line-height:1.5;">
                        右尾較長<br>少數高值把均值往右拉<br>
                        <b>例：工程師薪資、洪峰流量</b>
                    </div>
                </div>
                <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:12px 14px;text-align:center;">
                    <div style="font-size:1.1rem;font-weight:700;color:#15803d;margin-bottom:6px;">對稱分佈</div>
                    <div style="color:#7c3aed;font-size:1.05rem;font-weight:600;">眾數 ≈ 中位數 ≈ 均值</div>
                    <div style="color:#6b7280;font-size:0.88rem;margin-top:6px;line-height:1.5;">
                        左右尾等長<br>三量數幾乎重疊<br>
                        <b>例：精密零件直徑（常態分佈）</b>
                    </div>
                </div>
                <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px 14px;text-align:center;">
                    <div style="font-size:1.1rem;font-weight:700;color:#1d4ed8;margin-bottom:6px;">左偏（負偏）</div>
                    <div style="color:#7c3aed;font-size:1.05rem;font-weight:600;">均值 &lt; 中位數 &lt; 眾數</div>
                    <div style="color:#6b7280;font-size:0.88rem;margin-top:6px;line-height:1.5;">
                        左尾較長<br>少數低值把均值往左拉<br>
                        <b>例：零件壽命（早期失效型）</b>
                    </div>
                </div>
            </div>
            <div style="margin-top:10px;color:#64748b;font-size:0.88rem;background:#f1f5f9;padding:8px 12px;border-radius:8px;">
                💡 <b>記憶訣：</b>右偏=右尾長=均值被拉往右邊，所以均值 &gt; 中位數 &gt; 眾數。
                左偏=左尾長=均值被拉往左邊，所以均值 &lt; 中位數 &lt; 眾數。
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # =====================================================================
    # 實驗室 A：偏態與極端值的影響（情境資料 + 滑桿）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 A：極端值如何影響均值與中位數？", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>透過真實情境，感受「少數極端值」如何把均值往右拉，而中位數幾乎不動<br>
                <b>你會發現：</b>這正是右偏資料中「均值 &gt; 中位數」的根本原因
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 12px 0;">
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>情境：工程師年薪（萬元/年）</b><br>
                某公司有 30 位工程師，其中 <b>28 位一般工程師</b>年薪集中在 60～90 萬，
                另有 <b>2 位資深主管</b>年薪較高。<br>
                下方滑桿調整的是那 <b>2 位主管的年薪數值</b>（不是增加人數），
                觀察當主管薪資越來越高時，均值（紅線）和中位數（紫線）的變化。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        np.random.seed(7)
        base_salaries = np.round(np.random.normal(72, 8, 28)).astype(int)
        base_salaries = np.clip(base_salaries, 60, 90)

        mgr_salary = st.slider(
            "💼 兩位資深主管的年薪（萬元/年）",
            min_value=70, max_value=500, value=120, step=10,
            key="w2_skew_slider"
        )
        check_slider("w2_skew_slider", "t2_skew")

        full_data = np.concatenate([base_salaries, [mgr_salary, mgr_salary]])
        mean_val   = float(np.mean(full_data))
        median_val = float(np.median(full_data))
        mode_candidates = [int(x) for x in base_salaries]
        from collections import Counter
        mode_val = Counter(mode_candidates).most_common(1)[0][0]

        col_dist, col_stats = st.columns([3, 1])
        with col_dist:
            fig_sk = go.Figure()
            fig_sk.add_trace(go.Histogram(
                x=full_data, nbinsx=20,
                marker_color="#93c5fd", opacity=0.8,
                hovertemplate="薪資區間：%{x} 萬<br>人數：%{y}<extra></extra>",
                name="人數"
            ))
            fig_sk.add_vline(x=mean_val, line_color="red", line_width=3,
                             annotation_text="均值 " + f"{mean_val:.1f}",
                             annotation_position="top right",
                             annotation_font_size=F_ANNOTATION,
                             annotation_font_color="red")
            fig_sk.add_vline(x=median_val, line_color="#7c3aed", line_width=3,
                             line_dash="dash",
                             annotation_text="中位數 " + f"{median_val:.1f}",
                             annotation_position="top left",
                             annotation_font_size=F_ANNOTATION,
                             annotation_font_color="#7c3aed")
            set_chart_layout(fig_sk, "工程師年薪分佈（n=30）", "年薪（萬元/年）", "人數")
            fig_sk.update_layout(height=420, margin=dict(t=60, b=40, l=50, r=20))
            st.plotly_chart(fig_sk, use_container_width=True)

        with col_stats:
            st.metric("均值 X̄", f"{mean_val:.1f} 萬")
            st.metric("中位數", f"{median_val:.1f} 萬")
            st.metric("眾數（最常見）", f"{mode_val} 萬")
            gap = mean_val - median_val
            if gap > 5:
                st.markdown("🔴 **右偏**<br>均值被極端值拉高", unsafe_allow_html=True)
            elif gap < -5:
                st.markdown("🔵 **左偏**<br>均值被低值拉低", unsafe_allow_html=True)
            else:
                st.markdown("🟢 **近似對稱**<br>均值 ≈ 中位數", unsafe_allow_html=True)

        # 文字解析
        if mgr_salary <= 100:
            _card("#22c55e", "#f0fdf4", "#166534", "📊 目前：近似對稱分佈",
                  "主管薪資與一般工程師差距不大，均值和中位數相近。"
                  "分佈左右大致對稱，三個位置測度幾乎重疊。")
        elif mgr_salary <= 250:
            _card("#f59e0b", "#fffbeb", "#92400e", "📊 目前：輕微右偏",
                  "主管薪資拉高均值至 " + f"{mean_val:.1f}" + " 萬，"
                  "而中位數仍在 " + f"{median_val:.1f}" + " 萬（幾乎不動）。"
                  "均值 > 中位數，右側出現長尾，這就是「右偏」的特徵。")
        else:
            _card("#ef4444", "#fef2f2", "#991b1b", "📊 目前：明顯右偏",
                  "主管薪資高達 " + str(mgr_salary) + " 萬，嚴重拉高均值（" + f"{mean_val:.1f}" + " 萬），"
                  "但中位數（" + f"{median_val:.1f}" + " 萬）幾乎沒變！"
                  "這說明：當資料右偏時，<b>中位數更能代表「一般員工」的薪資水準</b>，"
                  "均值已被少數高薪者嚴重扭曲。")

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #22c55e;
                    border-radius:8px;padding:10px 16px;margin:12px 0 0 0;">
            <div style="color:#166534;font-size:1.0rem;line-height:1.7;">
                💡 <b>工程應用結論</b>：薪資、財富、洪峰流量等資料通常右偏。
                此時應優先報告<b>中位數</b>作為「代表性位置」，均值僅作輔助。
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # =====================================================================
    # 實驗室 B：逐步計算中位數與百分位數（課本方法）
    # =====================================================================
    with st.expander("✏️ 展開實驗室 B：逐步計算中位數與四分位數", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用課本方法逐步求出中位數（Q2）、Q1、Q3<br>
                <b>你會發現：</b>百分位數的核心是「位置」計算，不是直接平均
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # 使用小資料集（15 筆鋼棒直徑，對稱分佈）
        steel_data_raw = [19.2, 19.5, 19.7, 19.8, 19.9, 20.0, 20.0,
                          20.1, 20.1, 20.2, 20.3, 20.4, 20.5, 20.7, 20.9]
        steel_data = sorted(steel_data_raw)
        n_st = len(steel_data)

        st.markdown("**情境：15 根鋼棒直徑（mm），已由小到大排序**")
        st.dataframe(
            pd.DataFrame({"排序位置": list(range(1, n_st+1)),
                          "直徑（mm）": steel_data}).T,
            hide_index=False, use_container_width=True
        )

        _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟一：求中位數（Q2）的位置",
              "n=15（奇數），中位數在第 (n+1)/2 = (15+1)/2 = <b>第 8 個</b>位置。<br>"
              "請填入第 8 個數值（即中位數）：")

        median_input = st.number_input("中位數 Q2 = 排序後第 8 個值 = ?",
                                       value=0.0, step=0.1, format="%.1f", key="w2_b_median")
        true_median_st = steel_data[7]
        step_b1_done = False
        if median_input != 0.0:
            if abs(median_input - true_median_st) < 0.01:
                step_b1_done = True
                _card("#22c55e", "#f0fdf4", "#166534",
                      "✅ 正確！Q2 = " + str(true_median_st) + " mm",
                      "排序後第 8 個值 = " + str(true_median_st) + " mm，這就是中位數。請繼續步驟二。")
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再確認一次",
                      "請從上方表格找到第 8 個值（你填了 " + str(median_input) + "）")

        if step_b1_done:
            st.markdown("---")
            _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟二：求 Q1（第 25 百分位數）",
                  "Q1 位置 = (25/100) × n = 0.25 × 15 = 3.75，"
                  "取第 4 個值（無條件進位）。請填入 Q1：")

            q1_input = st.number_input("Q1 = 排序後第 4 個值 = ?",
                                       value=0.0, step=0.1, format="%.1f", key="w2_b_q1")
            true_q1_st = steel_data[3]
            step_b2_done = False
            if q1_input != 0.0:
                if abs(q1_input - true_q1_st) < 0.01:
                    step_b2_done = True
                    _card("#22c55e", "#f0fdf4", "#166534",
                          "✅ 正確！Q1 = " + str(true_q1_st) + " mm",
                          "25% 的鋼棒直徑小於 " + str(true_q1_st) + " mm，75% 大於此值。")
                else:
                    _card("#ef4444", "#fef2f2", "#991b1b", "❌ 提示",
                          "位置 = 無條件進位(3.75) = 第 4 個值。你填了 " + str(q1_input))

            if step_b2_done:
                st.markdown("---")
                _card("#7c3aed", "#f5f3ff", "#4c1d95", "🎉 三個位置測度已解鎖！",
                      "Q1=" + str(steel_data[3]) + " mm，Q2（中位數）=" + str(true_median_st) +
                      " mm，Q3=" + str(steel_data[11]) + " mm<br>"
                      "四分位距 IQR = Q3 - Q1 = " +
                      str(round(steel_data[11] - steel_data[3], 1)) + " mm")
                mark_done("t2_calc")

        col_rb, _ = st.columns([1, 4])
        with col_rb:
            if st.button("🔄 重新開始實驗室 B", key="w2_reset_b"):
                for k in ["w2_b_median", "w2_b_q1"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # ── 隨堂測驗 Tab2 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:16px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：偏態與位置測度</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    q2 = st.radio(
        "📍 **某地區洪峰流量的分佈呈右偏（正偏），下列何者正確？**",
        ["請選擇...", "A. 均值 < 中位數 < 眾數",
         "B. 眾數 < 中位數 < 均值",
         "C. 均值 = 中位數 = 眾數",
         "D. 中位數 > 均值 > 眾數"],
        key="w2_q2"
    )
    if st.button("送出答案", key="w2_btn_q2"):
        if q2 == "請選擇...":
            _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 請先選擇答案", "請先勾選一個選項再送出。")
        elif q2 == "B. 眾數 < 中位數 < 均值":
            _card("#22c55e", "#f0fdf4", "#166534", "🎉 恭喜答對！",
                  "右偏（正偏）：右尾較長，少數極大值把均值往右拉。"
                  "大小關係：<b>眾數 &lt; 中位數 &lt; 均值</b>。"
                  "工程上洪峰流量常呈右偏，應用中位數描述「一般水位」更為適當。")
            mark_done("t2_quiz")
        else:
            _card("#ef4444", "#fef2f2", "#991b1b", "❌ 提示",
                  "右偏 = 右尾較長 = 有少數極大值。極大值會把均值往哪個方向拉？")


# =====================================================================
# ██████████  TAB 3 — §2.3 差異性的量度  ██████████
# =====================================================================
with tab3:

    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§2.3 差異性的量度</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            差異性描述資料「散布程度」——光知道平均值不夠，還要知道數值是否集中。<br><br>
            ▸ <b>全距 (Range)</b>：最大值 − 最小值。簡單但受極端值影響大。<br>
            ▸ <b>樣本變異數 s²</b>：s² = Σ(xᵢ − X̄)² / (n−1)。各值偏離均值的平均平方距離。<br>
            ▸ <b>樣本標準差 s</b>：s = √s²。與原始資料同單位，最常用。<br>
            ▸ <b>變異係數 CV</b>：CV = (s / X̄) × 100%。無單位，用於跨組比較。<br>
            ▸ <b>四分位距 IQR</b>：Q3 − Q1。中間 50% 資料的範圍，不受極端值影響。
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;
                background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 樣本變異數</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                s² = Σ(xᵢ − X̄)² / (n−1)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">除以 (n−1) 而非 n，確保不偏估計</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 變異係數 CV</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                CV = (s / X̄) × 100%<br>
                <small style="color:#7c3aed;font-size:0.88rem;">跨組或跨單位比較離散程度</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # =====================================================================
    # 實驗室 A：兩條生產線的標準差 vs 不良率（滑桿）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 A：標準差與製程不良率的關係", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解「兩條生產線平均重量相同，但標準差不同」時，不良率有多大差異<br>
                <b>你會發現：</b>標準差與不良率的關係是<b>非線性的</b>——標準差加倍，不良率可能暴增數十倍
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 12px 0;">
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>情境：兩條齒輪零件生產線</b><br>
                品管規格：零件重量須在 <b>100 ± 容差</b> 克以內（即 [100−容差, 100+容差]）。<br>
                兩條線的平均重量都是 <b>100 克</b>，差別在於標準差不同。<br>
                調整下方兩條線的標準差，觀察不良率（超出規格的比例）如何變化。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        from scipy import stats as scipy_stats

        tol_range = st.slider("📏 品管容差（克）：規格 = 100 ± 此值", 1, 10, 5, 1, key="w2_tol")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sd1 = st.slider("生產線 A 標準差 sA（克）", 1, 8, 2, 1, key="w2_sd1")
        with col_s2:
            sd2 = st.slider("生產線 B 標準差 sB（克）", 1, 8, 4, 1, key="w2_sd2")

        check_slider("w2_tol", "t3_std")
        check_slider("w2_sd1", "t3_std")
        check_slider("w2_sd2", "t3_std")

        spec_lo, spec_hi = 100 - tol_range, 100 + tol_range
        defect_a = (1 - (scipy_stats.norm.cdf(spec_hi, 100, sd1) - scipy_stats.norm.cdf(spec_lo, 100, sd1))) * 100
        defect_b = (1 - (scipy_stats.norm.cdf(spec_hi, 100, sd2) - scipy_stats.norm.cdf(spec_lo, 100, sd2))) * 100

        x_range = np.linspace(70, 130, 500)
        fig_sd = go.Figure()
        fig_sd.add_trace(go.Scatter(
            x=x_range, y=scipy_stats.norm.pdf(x_range, 100, sd1),
            mode="lines", line=dict(color="#0f766e", width=3),
            name="生產線 A (s=" + str(sd1) + "g)",
            hovertemplate="重量：%{x:.1f}g<extra>生產線A</extra>"
        ))
        fig_sd.add_trace(go.Scatter(
            x=x_range, y=scipy_stats.norm.pdf(x_range, 100, sd2),
            mode="lines", line=dict(color="#ef4444", width=3),
            name="生產線 B (s=" + str(sd2) + "g)",
            hovertemplate="重量：%{x:.1f}g<extra>生產線B</extra>"
        ))
        fig_sd.add_vrect(x0=spec_lo, x1=spec_hi, fillcolor="#22c55e", opacity=0.1,
                         annotation_text="規格範圍", annotation_position="top left",
                         annotation_font_size=F_ANNOTATION)
        fig_sd.add_vline(x=spec_lo, line_color="#166534", line_dash="dash", line_width=2)
        fig_sd.add_vline(x=spec_hi, line_color="#166534", line_dash="dash", line_width=2)
        set_chart_layout(fig_sd, "兩條生產線的重量分佈（平均值均=100g）", "零件重量（克）", "機率密度")
        fig_sd.update_layout(height=420, legend=dict(font=dict(size=F_ANNOTATION-2)),
                             margin=dict(t=60, b=40, l=50, r=20))
        st.plotly_chart(fig_sd, use_container_width=True)

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("生產線 A 不良率", f"{defect_a:.2f}%", delta=None)
        with col_res2:
            st.metric("生產線 B 不良率", f"{defect_b:.2f}%", delta=None)

        if defect_b > defect_a * 3:
            _card("#ef4444", "#fef2f2", "#991b1b", "⚠️ 標準差的非線性影響",
                  "B 線不良率（" + f"{defect_b:.2f}%" + "）比 A 線（" + f"{defect_a:.2f}%" + "）高出 " +
                  f"{defect_b/max(defect_a,0.001):.1f}" + " 倍！"
                  "標準差加大，不良率以非線性方式暴增——這就是為什麼品管工程師拼命壓縮標準差。")
        else:
            _card("#0369a1", "#e0f2fe", "#0c4a6e", "📊 目前兩條線差異",
                  "A 線不良率：" + f"{defect_a:.2f}%" + "，B 線：" + f"{defect_b:.2f}%" +
                  "。試著把 B 線標準差拉到 A 線的 2 倍，觀察不良率的爆炸性增長！")

    # =====================================================================
    # 實驗室 B：逐步計算變異數（層次 5b）
    # =====================================================================
    with st.expander("✏️ 展開實驗室 B：逐步手算樣本標準差", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>逐步計算偏差平方表 → 得出 s² → 開根號求 s<br>
                <b>你會發現：</b>標準差的計算核心是「每個數值距離均值多遠？」
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # 6 筆小資料集（零件直徑）
        small_data = [19, 21, 20, 22, 18, 20]
        n_sm = len(small_data)
        mean_sm = sum(small_data) / n_sm
        devs = [x - mean_sm for x in small_data]
        devs_sq = [d**2 for d in devs]
        var_sm = sum(devs_sq) / (n_sm - 1)
        std_sm = var_sm ** 0.5

        st.markdown("**情境：6 個零件直徑（mm）**")
        st.dataframe(pd.DataFrame({"編號": list(range(1, n_sm+1)), "直徑 xᵢ": small_data}).T,
                     hide_index=False, use_container_width=True)
        st.markdown("**➡️ 均值 X̄ = " + str(mean_sm) + " mm（系統已計算）**")
        st.markdown("---")

        _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟一：填入第 2 個數值的偏差平方",
              "偏差 = xᵢ − X̄ = 21 − " + str(mean_sm) + " = <b>" + str(devs[1]) +
              "</b>，偏差平方 = " + str(devs[1]) + "² = ？")

        dev2_sq_input = st.number_input("第 2 個值的偏差平方 (xᵢ−X̄)² = ?",
                                        value=0.0, step=0.5, format="%.1f", key="w2_dev2sq")
        step3_done_b = False
        if dev2_sq_input != 0.0:
            if abs(dev2_sq_input - devs_sq[1]) < 0.01:
                step3_done_b = True
                _card("#22c55e", "#f0fdf4", "#166534",
                      "✅ 正確！偏差平方 = " + str(devs_sq[1]),
                      "(" + str(devs[1]) + ")² = " + str(devs_sq[1]) + "。請繼續步驟二。")
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再算一次",
                      "偏差 = 21 − " + str(mean_sm) + " = " + str(devs[1]) +
                      "；(" + str(devs[1]) + ")² = ？（你填了 " + str(dev2_sq_input) + "）")

        if step3_done_b:
            st.markdown("---")
            _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟二：填入 Σ(xᵢ−X̄)²（所有偏差平方的總和）",
                  "系統已計算各組偏差平方，請填入總和：")

            sum_sq_input = st.number_input("Σ(xᵢ−X̄)² = ?", value=0.0, step=0.5, format="%.1f", key="w2_sumdev")
            true_sum_sq = sum(devs_sq)
            step4_done_b = False
            if sum_sq_input != 0.0:
                if abs(sum_sq_input - true_sum_sq) < 0.01:
                    step4_done_b = True
                    _card("#22c55e", "#f0fdf4", "#166534",
                          "✅ 正確！Σ(xᵢ−X̄)² = " + str(true_sum_sq),
                          "所有 6 個偏差平方之總和。請繼續步驟三，計算標準差。")
                else:
                    _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再確認",
                          "各偏差平方：" + str([round(d, 1) for d in devs_sq]) +
                          "，請加總（你填了 " + str(sum_sq_input) + "）")

            if step4_done_b:
                st.markdown("---")
                _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟三：計算標準差 s",
                      "s² = " + str(true_sum_sq) + " / (6−1) = " + f"{var_sm:.2f}" +
                      "；s = √" + f"{var_sm:.2f}" + " = ？（保留兩位小數）")

                std_input = st.number_input("s = ?", value=0.0, step=0.01, format="%.2f", key="w2_std")
                if std_input != 0.0:
                    if abs(std_input - std_sm) < 0.015:
                        _card("#22c55e", "#f0fdf4", "#166534",
                              "🎊 完全正確！s = " + f"{std_sm:.2f}" + " mm",
                              "這 6 個零件直徑的標準差為 " + f"{std_sm:.2f}" + " mm，"
                              "表示典型偏差約 " + f"{std_sm:.2f}" + " mm。"
                              "變異係數 CV = " + f"{std_sm/mean_sm*100:.1f}" + "%（相對離散程度）。")
                        mark_done("t3_calc")

                        # 完整表格
                        df_dev = pd.DataFrame({
                            "xᵢ": small_data,
                            "xᵢ − X̄": [round(d, 1) for d in devs],
                            "(xᵢ − X̄)²": [round(d, 1) for d in devs_sq],
                        })
                        st.dataframe(df_dev, hide_index=True, use_container_width=True)
                        st.metric("Σ(xᵢ−X̄)²", str(true_sum_sq))
                        st.metric("s²（樣本變異數）", f"{var_sm:.2f}")
                        st.metric("s（樣本標準差）", f"{std_sm:.2f} mm")
                    else:
                        _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再確認",
                              "s = √" + f"{var_sm:.2f}" + " ≈ ？（你填了 " + str(std_input) + "）")

        col_r3, _ = st.columns([1, 4])
        with col_r3:
            if st.button("🔄 重新開始實驗室 B", key="w2_reset_t3b"):
                for k in ["w2_dev2sq", "w2_sumdev", "w2_std"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # =====================================================================
    # 實驗室 C：百分位數與箱型圖（IQR + 1.5×IQR 離群值規則）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 C：百分位數與箱型圖（工程規格神器）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用箱型圖快速掌握資料分佈的五個關鍵數字，並用 1.5×IQR 規則識別離群值<br>
                <b>你會發現：</b>拖動百分位數滑桿，觀察 Pₖ 在箱型圖上的位置；IQR 是比全距更穩健的離散度量
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 12px 0;">
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>情境：100 根螺栓直徑（mm）</b><br>
                品管部門抽取 100 根螺栓，量測直徑（平均約 50 mm，標準差約 5 mm）。<br>
                <b>百分位數 Pₖ</b>：排序後有 k% 的資料小於等於此值。<br>
                <b>四分位距 IQR = Q3 − Q1</b>：中間 50% 資料的涵蓋範圍，不受極端值影響。<br>
                <b>1.5×IQR 規則</b>：超出 [Q1−1.5×IQR, Q3+1.5×IQR] 的值為離群值（John Tukey 提出的業界標準）。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        np.random.seed(2)
        bolt_data = np.random.normal(50, 5, 100)

        k_pct = st.slider("🔢 查詢第 k 百分位數 Pₖ — 拖動滑桿觀察百分位數位置", 1, 99, 85, key="w2_kpct")
        check_slider("w2_kpct", "t3_box")

        pk_val = float(np.percentile(bolt_data, k_pct))
        q1_bx = float(np.percentile(bolt_data, 25))
        q3_bx = float(np.percentile(bolt_data, 75))
        iqr_bx = q3_bx - q1_bx
        lower_fence = q1_bx - 1.5 * iqr_bx
        upper_fence = q3_bx + 1.5 * iqr_bx
        outliers_bx = bolt_data[(bolt_data < lower_fence) | (bolt_data > upper_fence)]

        col_bx1, col_bx2, col_bx3, col_bx4 = st.columns(4)
        col_bx1.metric(f"P{k_pct}", f"{pk_val:.2f} mm")
        col_bx2.metric("Q1 (P25)", f"{q1_bx:.2f} mm")
        col_bx3.metric("Q3 (P75)", f"{q3_bx:.2f} mm")
        col_bx4.metric("IQR = Q3-Q1", f"{iqr_bx:.2f} mm")

        fig_bx = go.Figure()
        fig_bx.add_trace(go.Box(
            x=bolt_data, name="螺栓直徑",
            boxpoints="all", jitter=0.4, pointpos=0,
            marker=dict(color="rgba(59,130,246,0.4)", size=4),
            line=dict(color="#3b82f6"),
            hovertemplate="直徑：%{x:.2f} mm<extra></extra>"
        ))
        fig_bx.add_vline(x=lower_fence, line_dash="dash", line_color="red", line_width=2,
                         annotation_text="下邊界 " + f"{lower_fence:.1f}",
                         annotation_position="bottom right",
                         annotation_font_size=F_ANNOTATION)
        fig_bx.add_vline(x=upper_fence, line_dash="dash", line_color="red", line_width=2,
                         annotation_text="上邊界 " + f"{upper_fence:.1f}",
                         annotation_position="top right",
                         annotation_font_size=F_ANNOTATION)
        fig_bx.add_vline(x=pk_val, line_dash="dot", line_color="#22c55e", line_width=2.5,
                         annotation_text="P" + str(k_pct) + " = " + f"{pk_val:.1f}",
                         annotation_position="top left",
                         annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig_bx,
                         "箱型圖 + 1.5×IQR 離群值邊界（P" + str(k_pct) + " 標示）",
                         "直徑（mm）", "")
        fig_bx.update_layout(height=360, margin=dict(t=60, b=40, l=50, r=20))
        st.plotly_chart(fig_bx, use_container_width=True)

        if len(outliers_bx) > 0:
            _card("#f59e0b", "#fffbeb", "#92400e",
                  "🔍 偵測到 " + str(len(outliers_bx)) + " 個離群值",
                  "離群值：" + str(np.round(outliers_bx, 2).tolist()) + "<br>"
                  "這些螺栓直徑超出 1.5×IQR 邊界，建議工程師進一步檢查是否為量測誤差或製程異常。")
        else:
            _card("#22c55e", "#f0fdf4", "#166534", "✅ 無離群值",
                  "所有螺栓直徑均在 1.5×IQR 邊界內（" + f"{lower_fence:.1f}" +
                  " ~ " + f"{upper_fence:.1f}" + " mm），製程穩定。")

        _card("#0369a1", "#e0f2fe", "#0c4a6e", "📖 箱型圖五數摘要",
              "最小值：" + f"{float(np.min(bolt_data)):.2f}" +
              " mm　│　Q1：" + f"{q1_bx:.2f}" +
              " mm　│　中位數：" + f"{float(np.median(bolt_data)):.2f}" +
              " mm　│　Q3：" + f"{q3_bx:.2f}" +
              " mm　│　最大值：" + f"{float(np.max(bolt_data)):.2f}" + " mm<br>"
              "IQR = " + f"{iqr_bx:.2f}" + " mm（比全距更穩健，不受極端值影響）")

    # ── 隨堂測驗 Tab3 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:16px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：標準差的意義</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    q3 = st.radio(
        "📍 **甲廠混凝土抗壓強度：X̄=30 MPa，s=3 MPa；乙廠：X̄=50 MPa，s=4 MPa。哪廠製程相對較穩定？**",
        ["請選擇...",
         "A. 甲廠（s 較小）",
         "B. 乙廠（s 較小）",
         "C. 甲廠（CV 較小）",
         "D. 乙廠（CV 較小）"],
        key="w2_q3"
    )
    if st.button("送出答案", key="w2_btn_q3"):
        if q3 == "請選擇...":
            _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 請先選擇答案", "請先勾選一個選項再送出。")
        elif q3 == "D. 乙廠（CV 較小）":
            _card("#22c55e", "#f0fdf4", "#166534", "🎉 恭喜答對！",
                  "甲廠 CV = 3/30×100% = <b>10%</b>；乙廠 CV = 4/50×100% = <b>8%</b>。"
                  "乙廠 CV 較小，製程相對較穩定。"
                  "直接比較 s 會被均值大小誤導，CV 才是跨組比較差異性的正確工具。")
            mark_done("t3_quiz")
        else:
            _card("#ef4444", "#fef2f2", "#991b1b", "❌ 提示",
                  "兩廠均值不同，不能直接比較 s。需計算 CV = (s/X̄)×100%，再互相比較。")


# =====================================================================
# ██████████  TAB 4 — §2.4 比例  ██████████
# =====================================================================
with tab4:

    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§2.4 比例</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>比例 (Proportion) P</b>：樣本中具有某一特徵之觀測值的比例，
            用於描述「屬性型」（二元或多類別）資料的分佈。<br><br>
            ▸ 計算公式：<b>P = f / n</b>，其中 f 為具備該特徵的次數，n 為樣本總數<br>
            ▸ 比例範圍：0 ≤ P ≤ 1（通常以百分比表示）<br>
            ▸ <b>課本例題 2.4</b>：造紙廠 10 台設備的狀態調查——正常、失常、無法操作<br>
            ▸ 工程上常用比例作為「不良率」「完好率」「可用率」的估算基礎
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # 公式卡
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #ddd6fe;margin:8px 0 14px 0;">
        <div style="background:#7c3aed;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📐 比例公式</span>
        </div>
        <div style="background:#f5f3ff;padding:16px 18px;color:#4c1d95;
                    font-size:1.1rem;line-height:1.9;text-align:center;">
            P = f / n<br>
            <small style="color:#7c3aed;font-size:0.88rem;">f：符合條件的次數；n：樣本總數</small>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # =====================================================================
    # 實驗室 A：樣本大小對比例穩定性的影響（滑桿）
    # =====================================================================
    with st.expander("🛠️ 展開實驗室 A：樣本數越大，比例越穩定？", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>觀察不同樣本數下，樣本比例 P 的波動程度<br>
                <b>你會發現：</b>樣本數越大，P 越接近真實母體比例，波動越小
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 12px 0;">
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>情境：造紙廠設備可用率調查</b><br>
                假設造紙廠有大量設備，真實可用率（正常運作）為 <b>70%</b>。
                下方滑桿調整「抽查幾台設備（樣本數 n）」，
                觀察每次樣本抽到的「正常設備比例」是否穩定。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        n_sample = st.slider("🔢 抽查設備數 n（台）", 5, 200, 10, 5, key="w2_prop_n")
        check_slider("w2_prop_n", "t4_prop")

        # 模擬多次抽樣（固定種子 + n）
        np.random.seed(2024)
        n_trials = 30
        true_p = 0.70
        sample_ps = [np.mean(np.random.binomial(1, true_p, n_sample)) for _ in range(n_trials)]

        fig_prop = go.Figure()
        fig_prop.add_trace(go.Scatter(
            x=list(range(1, n_trials+1)), y=sample_ps,
            mode="lines+markers",
            line=dict(color="#0369a1", width=2),
            marker=dict(size=7, color="#0369a1"),
            name="各次樣本比例 P",
            hovertemplate="第 %{x} 次<br>P = %{y:.3f}<extra></extra>"
        ))
        fig_prop.add_hline(y=true_p, line_color="#22c55e", line_width=2, line_dash="dash",
                           annotation_text="真實比例 70%",
                           annotation_position="right",
                           annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig_prop, "30 次重複抽樣的比例估計值（n=" + str(n_sample) + "）",
                         "抽樣次數", "正常設備比例 P")
        fig_prop.update_layout(height=420, yaxis=dict(range=[0, 1.05]),
                               margin=dict(t=60, b=40, l=50, r=20))
        st.plotly_chart(fig_prop, use_container_width=True)

        p_std = float(np.std(sample_ps))
        p_mean = float(np.mean(sample_ps))
        _card("#0369a1", "#e0f2fe", "#0c4a6e", "📊 本次抽樣結果",
              "n=" + str(n_sample) + "，30 次抽樣的平均比例=" + f"{p_mean:.3f}" +
              "，標準差=" + f"{p_std:.3f}" + "。" +
              ("樣本數較小，每次抽到的比例波動很大，估計不穩定。" if n_sample < 30 else
               "樣本數較大，每次估計值都接近真實比例 0.70，估計穩定可靠。"))

    # =====================================================================
    # 實驗室 B：課本例題 2.4 逐步計算（造紙廠設備比例）
    # =====================================================================
    with st.expander("✏️ 展開實驗室 B：課本例題 2.4 比例計算（造紙廠設備調查）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用課本例題 2.4 的原始資料計算各類設備比例<br>
                <b>你會發現：</b>比例計算的核心就是 P = f / n，但要注意「f」對應哪一類別
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # 課本例題 2.4 資料
        equipment_data = {
            "正常 (Normal)": 6,
            "失常 (Malfunctioning)": 2,
            "無法操作 (Inoperable)": 2,
        }
        n_eq = sum(equipment_data.values())  # = 10

        st.markdown("**課本例題 2.4：造紙廠 10 台設備狀態**")
        df_eq = pd.DataFrame({
            "設備狀態": list(equipment_data.keys()),
            "台數 f": list(equipment_data.values()),
        })
        st.dataframe(df_eq, hide_index=True, use_container_width=True)
        st.markdown("**➡️ 樣本總數 n = " + str(n_eq) + " 台**")
        st.markdown("---")

        _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟一：計算正常設備比例 P（正常）",
              "P = f（正常）/ n = 6 / 10 = ？（填小數，如 0.60）")

        p_normal_input = st.number_input("P（正常）= ?", value=0.0, step=0.01, format="%.2f", key="w2_peq1")
        true_p_normal = equipment_data["正常 (Normal)"] / n_eq
        step4a_done = False
        if p_normal_input != 0.0:
            if abs(p_normal_input - true_p_normal) < 0.01:
                step4a_done = True
                _card("#22c55e", "#f0fdf4", "#166534",
                      "✅ 正確！P（正常）= " + f"{true_p_normal:.2f}",
                      "6 台正常 ÷ 10 台 = 0.60，即 60% 設備正常運作。請繼續步驟二。")
                mark_done("t4_calc")
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再算一次",
                      "P = f/n = 6/10 = ？（你填了 " + str(p_normal_input) + "）")

        if step4a_done:
            st.markdown("---")
            _card("#0369a1", "#e0f2fe", "#0c4a6e", "✏️ 步驟二：計算需要處理的設備比例（失常＋無法操作）",
                  "P（需要處理）= （失常台數＋無法操作台數）/ n = (2+2)/10 = ？")

            p_fix_input = st.number_input("P（需要處理）= ?", value=0.0, step=0.01, format="%.2f", key="w2_peq2")
            true_p_fix = (equipment_data["失常 (Malfunctioning)"] + equipment_data["無法操作 (Inoperable)"]) / n_eq
            if p_fix_input != 0.0:
                if abs(p_fix_input - true_p_fix) < 0.01:
                    _card("#22c55e", "#f0fdf4", "#166534", "🎉 全部完成！",
                          "P（需要處理）= (2+2)/10 = <b>0.40</b>，即 40% 設備需要維修或停機處理。<br>"
                          "品管決策：若規定「可用率需 ≥ 80%」，目前 60% 低於標準，應立即排定維修計畫！")

                    # 圓餅圖
                    fig_pie = go.Figure(go.Pie(
                        labels=list(equipment_data.keys()),
                        values=list(equipment_data.values()),
                        hole=0.35,
                        marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
                        textinfo="label+percent",
                        textfont=dict(size=F_ANNOTATION)
                    ))
                    fig_pie.update_layout(
                        title=dict(text="造紙廠設備狀態分佈（課本例題 2.4）",
                                   font=dict(size=F_TITLE)),
                        height=420,
                        legend=dict(font=dict(size=F_ANNOTATION-2)),
                        margin=dict(t=60, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    _card("#ef4444", "#fef2f2", "#991b1b", "❌ 再算一次",
                          "失常 2 台＋無法操作 2 台 = 4 台，P = 4/10 = ？（你填了 " + str(p_fix_input) + "）")

        col_r4, _ = st.columns([1, 4])
        with col_r4:
            if st.button("🔄 重新開始實驗室 B", key="w2_reset_t4b"):
                for k in ["w2_peq1", "w2_peq2"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # ── 隨堂測驗 Tab4 ─────────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:16px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：比例的計算與應用</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    q4 = st.radio(
        "📍 **抽查 50 個焊接點，發現 8 個有瑕疵。樣本瑕疵比例 P 為多少？**",
        ["請選擇...", "A. 8%", "B. 16%", "C. 0.08", "D. 0.16"],
        key="w2_q4"
    )
    if st.button("送出答案", key="w2_btn_q4"):
        if q4 == "請選擇...":
            _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 請先選擇答案", "請先勾選一個選項再送出。")
        elif q4 == "D. 0.16":
            _card("#22c55e", "#f0fdf4", "#166534", "🎉 恭喜答對！",
                  "P = f/n = 8/50 = <b>0.16</b>（即 16%）。"
                  "選項 C（0.08）是 8/100 的結果，不是本題的 n=50。"
                  "比例通常以小數表示（0～1），百分比僅為展示用途。")
            mark_done("t4_quiz")
        else:
            _card("#ef4444", "#fef2f2", "#991b1b", "❌ 提示",
                  "P = f/n，f=8（瑕疵數），n=50（樣本數）。8÷50=？注意是小數還是百分比。")


# =====================================================================
# ██  SECTION 2：互動參與進度記錄（Section 2a）  ██
# =====================================================================
st.divider()
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📝 2a. 本週互動參與記錄</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">完成上方各節互動後，在此送出本週參與記錄（不計分，僅記錄完成狀況）</p>',
            unsafe_allow_html=True)

done_count = count_done()
total_count = len(TRACK_KEYS)
done_pct = int(done_count / total_count * 100)

# 進度顯示
tab_labels = ["Tab1 次數分配", "Tab2 位置測度", "Tab3 差異性", "Tab4 比例"]
tab_keys_map = {
    "Tab1 次數分配":  ["t1_bins", "t1_stem", "t1_table", "t1_quiz"],
    "Tab2 位置測度":  ["t2_skew", "t2_calc", "t2_quiz"],
    "Tab3 差異性":    ["t3_std", "t3_box", "t3_calc", "t3_quiz"],
    "Tab4 比例":      ["t4_prop", "t4_calc", "t4_quiz"],
}
track_labels = {
    "t1_bins":  "直方圖滑桿",   "t1_stem":  "莖葉圖",
    "t1_table": "次數分配表",   "t1_quiz":  "隨堂測驗",
    "t2_skew":  "偏態滑桿",     "t2_calc":  "逐步計算",
    "t2_quiz":  "隨堂測驗",     "t3_std":   "標準差滑桿",   "t3_box":   "箱型圖滑桿",
    "t3_calc":  "逐步計算",     "t3_quiz":  "隨堂測驗",
    "t4_prop":  "比例滑桿",     "t4_calc":  "逐步計算",
    "t4_quiz":  "隨堂測驗",
}

progress_cols = st.columns(4)
for col_i, (tab_label, keys) in enumerate(tab_keys_map.items()):
    with progress_cols[col_i]:
        done_in_tab = sum(1 for k in keys if st.session_state.get("w2_track_" + k, False))
        items_html = ""
        for k in keys:
            done_flag = st.session_state.get("w2_track_" + k, False)
            icon = "✅" if done_flag else "⬜"
            items_html += '<li style="margin:3px 0;font-size:0.88rem;">' + icon + " " + track_labels[k] + "</li>"
        st.markdown(
            '<div style="border-radius:10px;overflow:hidden;border:1px solid #e2e8f0;margin-bottom:8px;">'
            '<div style="background:#1e3a5f;padding:8px 12px;">'
            '<span style="color:white;font-size:0.88rem;font-weight:700;">' + tab_label + '</span>'
            ' <span style="color:#93c5fd;font-size:0.8rem;">(' + str(done_in_tab) + '/' + str(len(keys)) + ')</span>'
            '</div>'
            '<div style="background:#f8fafc;padding:10px 14px;">'
            '<ul style="margin:0;padding-left:16px;">' + items_html + '</ul>'
            '</div></div>',
            unsafe_allow_html=True
        )

_card("#0369a1", "#e0f2fe", "#0c4a6e", "📊 本週互動完成率",
      "已完成 <b>" + str(done_count) + "/" + str(total_count) + "</b> 項互動（" + str(done_pct) + "%）")

# 送出表單（Section 2a）
_card("#475569", "#f8fafc", "#334155", "📤 送出互動參與記錄",
      "請填寫學號、姓名與驗證碼後送出，系統將記錄本週互動完成狀況。")

col_2a_id, col_2a_name, col_2a_code = st.columns(3)
with col_2a_id:   ia_id   = st.text_input("📝 學號", key="w2_ia_id")
with col_2a_name: ia_name = st.text_input("📝 姓名", key="w2_ia_name")
with col_2a_code: ia_code = st.text_input("🔑 驗證碼", type="password", key="w2_ia_code")

# ── 送出成功後的持久顯示訊息 ──────────────────────────────────────
_ia_result = st.session_state.get("w2_ia_submitted")
if _ia_result:
    _card("#22c55e", "#f0fdf4", "#166534", "✅ 互動參與記錄已送出！",
          _ia_result["name"] + "（" + _ia_result["id"] + "）驗證通過<br>"
          "本週互動完成率：<b>" + str(_ia_result["pct"]) + "%</b>"
          "（" + str(_ia_result["done"]) + "/" + str(_ia_result["total"]) + " 項）<br>"
          "可繼續完成未做的互動後再次送出，記錄會自動更新。")


if st.button("📤 送出本週互動記錄", key="w2_ia_submit", use_container_width=True):
    if ia_id and ia_name and ia_code:
        is_valid_ia, student_idx_ia = verify_student(ia_id, ia_name, ia_code)
        if not is_valid_ia:
            _card("#ef4444", "#fef2f2", "#991b1b", "⛔ 身分驗證失敗",
                  "學號、姓名或驗證碼有誤，請重新確認！")
        else:
            # 建立詳細記錄字串
            detail_parts = []
            for k in TRACK_KEYS:
                done_flag = st.session_state.get("w2_track_" + k, False)
                symbol = "V" if done_flag else "-"
                detail_parts.append(k + ":" + symbol)
            detail_str = " | ".join(detail_parts)
            ia_record = str(done_pct) + "% (" + str(done_count) + "/" + str(total_count) + ") | " + detail_str

            success_ia = save_score(student_idx_ia, ia_id, ia_name, "Week 02 互動", ia_record, done_pct)
            if success_ia:
                # 先把成功狀態存入 session_state，讓重跑後仍能顯示
                st.session_state["w2_ia_submitted"] = {
                    "name": ia_name, "id": ia_id,
                    "pct": done_pct, "done": done_count, "total": total_count
                }
                # 清除互動追蹤（防止下一位同學借用）
                for k in [k for k in list(st.session_state.keys()) if k.startswith("w2_track_")]:
                    del st.session_state[k]
                st.rerun()
            else:
                _card("#ef4444", "#fef2f2", "#991b1b", "❌ 送出失敗",
                      "資料庫連線問題，請稍後再試或聯繫老師。")
    else:
        _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 資料不完整",
              "請完整填寫學號、姓名與驗證碼再送出。")


# =====================================================================
# ██  SECTION 2b：整合性總測驗  ██
# =====================================================================
st.divider()
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">🎯 2b. 本週整合性總測驗</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">完成上方所有互動後，輸入老師公布的密碼開始作答</p>',
            unsafe_allow_html=True)

real_password = get_weekly_password("Week 02")
if not real_password:
    real_password = "888888"

_card("#475569", "#f8fafc", "#334155", "🔒 測驗鎖定中",
      "請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。")

col_pw, col_btn = st.columns([5, 1])
with col_pw:
    user_code = st.text_input("密碼", type="password", key="w2_unlock_code",
                               label_visibility="collapsed",
                               placeholder="🔑 請輸入 6 位數解鎖密碼…")
with col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w2_unlock_btn")

if user_code != real_password:
    if user_code != "":
        _card("#ef4444", "#fef2f2", "#991b1b", "❌ 密碼錯誤", "請確認字母與數字是否正確！")
else:
    _card("#22c55e", "#f0fdf4", "#166534", "🔓 密碼正確！", "測驗已解鎖，請完成以下題目後送出。")
    _card("#3b82f6", "#eff6ff", "#1e40af", "📋 測驗說明",
          "4 題，每題 25 分，共 100 分。作答送出後即鎖定成績，請確實核對學號與驗證碼！")

    with st.form("week02_quiz"):
        c_id, c_name, c_code = st.columns(3)
        with c_id:   st_id    = st.text_input("📝 學號")
        with c_name: st_name  = st.text_input("📝 姓名")
        with c_code: st_vcode = st.text_input("🔑 驗證碼", type="password")
        st.markdown("---")

        q_1 = st.radio(
            "**Q1（§2.1）：次數分配表中「組中點」的計算方式為何？**",
            ["請選擇...",
             "A. (組下限 × 組上限) / 2",
             "B. (組下限 + 組上限) / 2",
             "C. 組上限 − 組下限",
             "D. 次數 / 樣本數"],
            key="w2_final_q1"
        )
        q_2 = st.radio(
            "**Q2（§2.2）：右偏（正偏）資料中，均值、中位數、眾數的大小關係為？**",
            ["請選擇...",
             "A. 均值 < 中位數 < 眾數",
             "B. 眾數 < 中位數 < 均值",
             "C. 均值 = 中位數 = 眾數",
             "D. 中位數 > 均值 > 眾數"],
            key="w2_final_q2"
        )
        q_3 = st.radio(
            "**Q3（§2.3）：甲廠抗壓強度 X̄=30 MPa，s=3 MPa；乙廠 X̄=50 MPa，s=4 MPa。哪廠製程相對較穩定？**",
            ["請選擇...",
             "A. 甲廠（因為 s 較小）",
             "B. 乙廠（因為 s 較小）",
             "C. 甲廠（因為 CV 較小）",
             "D. 乙廠（因為 CV 較小）"],
            key="w2_final_q3"
        )
        q_4 = st.radio(
            "**Q4（§2.4）：抽查 50 個焊接點，8 個有瑕疵。樣本瑕疵比例 P 為多少？**",
            ["請選擇...",
             "A. 0.08",
             "B. 8%",
             "C. 0.16",
             "D. 16%"],
            key="w2_final_q4"
        )
        st.markdown("---")

        if st.form_submit_button("✅ 簽署並送出本週測驗",
                                  disabled=st.session_state.w2_locked):
            if st_id and st_name and st_vcode:
                is_valid, student_idx = verify_student(st_id, st_name, st_vcode)
                if not is_valid:
                    _card("#ef4444", "#fef2f2", "#991b1b", "⛔ 身分驗證失敗",
                          "您輸入的學號、姓名或驗證碼有誤，請重新確認！")
                elif check_has_submitted(st_id, "Week 02"):
                    _card("#ef4444", "#fef2f2", "#991b1b", "⛔ 拒絕送出",
                          "系統查詢到您已繳交過 Week 02 的測驗！請勿重複作答。")
                else:
                    score = 0
                    if q_1 == "B. (組下限 + 組上限) / 2":   score += 25
                    if q_2 == "B. 眾數 < 中位數 < 均值":     score += 25
                    if q_3 == "D. 乙廠（因為 CV 較小）":      score += 25
                    if q_4 == "C. 0.16":                      score += 25

                    ans_str = (
                        "Q1:" + q_1[:2] + ",Q2:" + q_2[:2] +
                        ",Q3:" + q_3[:2] + ",Q4:" + q_4[:2]
                    )
                    success = save_score(student_idx, st_id, st_name, "Week 02", ans_str, score)

                    if success:
                        st.session_state.w2_locked = True
                        success_html = (
                            '<div style="border-radius:12px;overflow:hidden;'
                            'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
                            'border:1px solid #e2e8f0;margin:8px 0;">'
                            '<div style="background:#22c55e;padding:10px 18px;">'
                            '<span style="color:white;font-weight:700;font-size:1.0rem;">🎊 上傳成功！</span></div>'
                            '<div style="background:#f0fdf4;padding:14px 18px;color:#166534;">'
                            '<b>' + st_name + '</b>（' + st_id + '）驗證通過<br>'
                            '<span style="font-size:2.0rem;font-weight:900;color:#15803d;">' + str(score) + '</span>'
                            '<span style="font-size:1.0rem;"> 分　成績已鎖定！</span>'
                            '</div></div>'
                        )
                        st.markdown(success_html, unsafe_allow_html=True)
                        if score == 100:
                            st.balloons()
                            _card("#7c3aed", "#f5f3ff", "#4c1d95", "🏆 滿分 100！",
                                  "本週第 2 章所有核心概念全數掌握！統計描述你已完全搞定！")
                        elif score >= 75:
                            _card("#3b82f6", "#eff6ff", "#1e40af", "👍 表現不錯！",
                                  "建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。")
                        else:
                            _card("#f59e0b", "#fffbeb", "#92400e", "📖 繼續加油！",
                                  "請回顧本週各節的概念說明與互動實驗，理解比死背更重要！")
            else:
                _card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 資料不完整",
                      "請完整填寫學號、姓名與驗證碼再送出表單。")

    if st.session_state.w2_locked:
        _card("#475569", "#f8fafc", "#334155", "🔒 測驗已鎖定",
              "系統已安全登錄您的成績，如有疑問請聯繫授課教師。")


# =====================================================================
# 底部速查卡
# =====================================================================
st.divider()
with st.expander("📚 本週核心概念速查卡（考前複習用）", expanded=False):
    _cards_ref = [
        ("#0f766e", "#f0fdfa", "#134e4a", "📊 §2.1 次數分配",
         ["次數分配：資料分組彙整的第一步",
          "組距 w = (最大值−最小值) ÷ k",
          "組中點 mₖ = (下限+上限) ÷ 2",
          "Ogive：累積次數曲線，估良率用",
          "莖葉圖：保留原始數值的次數分配"]),
        ("#7c3aed", "#f5f3ff", "#4c1d95", "📍 §2.2 位置的測度",
         ["X̄ = Σxᵢ/n（受極端值影響大）",
          "中位數：排序後中間值，穩健",
          "右偏：均值 > 中位數 > 眾數",
          "左偏：均值 < 中位數 < 眾數",
          "薪資/流量資料常右偏→用中位數"]),
        ("#0369a1", "#e0f2fe", "#0c4a6e", "📦 §2.3 差異性的量度",
         ["s² = Σ(xᵢ−X̄)²/(n−1)（不偏）",
          "s = √s²（與資料同單位）",
          "CV = s/X̄ × 100%（跨組比較）",
          "IQR = Q3−Q1（抗極端值）",
          "標準差↑ → 不良率非線性暴增"]),
        ("#22c55e", "#f0fdf4", "#166534", "⚖️ §2.4 比例",
         ["P = f/n（0 ≤ P ≤ 1）",
          "課本例 2.4：造紙廠設備可用率",
          "正常 6/10 = 60%；需維修 4/10 = 40%",
          "n 越大，P 估計越穩定",
          "品管決策：P < 規格下限→停線"]),
    ]
    # 2×2 版面：上排 §2.1 §2.2，下排 §2.3 §2.4
    _ref_row1 = st.columns(2)
    _ref_row2 = st.columns(2)
    _ref_all_cols = _ref_row1 + _ref_row2
    for _i, (_hc, _bc, _tc, _title, _items) in enumerate(_cards_ref):
        with _ref_all_cols[_i]:
            _ihtml = "".join(
                '<li style="margin:4px 0;color:' + _tc + ';font-size:0.92rem;">' + it + '</li>'
                for it in _items
            )
            st.markdown(
                '<div style="border-radius:12px;overflow:hidden;'
                'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
                'border:1px solid #e2e8f0;margin-bottom:14px;">'
                '<div style="background:' + _hc + ';padding:9px 16px;">'
                '<span style="color:white;font-weight:800;font-size:0.95rem;">' + _title + '</span></div>'
                '<div style="background:' + _bc + ';padding:11px 16px;">'
                '<ul style="margin:0;padding-left:16px;">' + _ihtml + '</ul></div></div>',
                unsafe_allow_html=True
            )

# =====================================================================
# 版權 badge
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