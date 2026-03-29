# 檔案位置： D:\Engineering_Statistics_App\pages\05_Week_05.py
import streamlit as st
import pandas as pd
import numpy as np
import math
from scipy import stats as scipy_stats

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
from utils.week_submit import render_ia_section, render_quiz_section
apply_week_css()

# 2. 登入防護
from utils.auth import require_login
require_login()

# 3. 後端資料庫
try:
    from utils.gsheets_db import (
        save_score, check_has_submitted, verify_student,
        get_weekly_password, get_weekly_password_safe, get_saved_progress
    )
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

# ── Session State 初始化 ──────────────────────────────────────────────
if "w5_locked" not in st.session_state:
    st.session_state.w5_locked = False

if _sidebar_ok:
    render_sidebar(current_page="Week 05")

# ── 互動追蹤 key 清單（Section 2a 用）────────────────────────────────
TRACK_KEYS = {
    "t1_curve":  False,   # Tab1 §5.1 常態曲線滑桿（需移動才算）
    "t1_calc":   False,   # Tab1 §5.1 Z轉換逐步計算（完成才算）
    "t1_quiz":   False,   # Tab1 §5.1 隨堂測驗（答對才算）
    "t2_bar":    False,   # Tab2 §5.2 卜瓦松滑桿（需移動才算）
    "t2_calc":   False,   # Tab2 §5.2 龍捲風計算（完成才算）
    "t2_quiz":   False,   # Tab2 §5.2 隨堂測驗（答對才算）
    "t3_exp":    False,   # Tab3 §5.3 指數可靠度滑桿（需移動才算）
    "t3_calc":   False,   # Tab3 §5.3 MTBF逐步計算（完成才算）
    "t3_quiz":   False,   # Tab3 §5.3 隨堂測驗（答對才算）
    "t4_weibull":False,   # Tab4 §5.5 Weibull浴缸曲線滑桿（需移動才算）
    "t4_calc":   False,   # Tab4 §5.5 例題5.7逐步計算（完成才算）
    "t4_quiz":   False,   # Tab4 §5.5 隨堂測驗（答對才算）
    "t5_hyper":  False,   # Tab5 §5.6 超幾何滑桿（需移動才算）
    "t5_quiz":   False,   # Tab5 §5.6 隨堂測驗（答對才算）
}

# ── 互動參與送出：分組與標籤（傳給 render_ia_section）────────────
GROUPS_IA = {
    "Tab1 §5.1 常態分配":     ["t1_curve", "t1_calc", "t1_quiz"],
    "Tab2 §5.2 卜瓦松分配":   ["t2_bar",   "t2_calc", "t2_quiz"],
    "Tab3 §5.3 指數分配":     ["t3_exp",   "t3_calc", "t3_quiz"],
    "Tab4 §5.5 Weibull分配":  ["t4_weibull","t4_calc","t4_quiz"],
    "Tab5 §5.6 超幾何分配":   ["t5_hyper", "t5_quiz"],
}
LABELS_IA = {
    "t1_curve":   "常態曲線滑桿",   "t1_calc":   "Z轉換計算",   "t1_quiz":   "隨堂測驗",
    "t2_bar":     "卜瓦松滑桿",     "t2_calc":   "龍捲風計算",  "t2_quiz":   "隨堂測驗",
    "t3_exp":     "指數可靠度滑桿", "t3_calc":   "MTBF計算",    "t3_quiz":   "隨堂測驗",
    "t4_weibull": "Weibull浴缸滑桿","t4_calc":   "例題5.7計算", "t4_quiz":   "隨堂測驗",
    "t5_hyper":   "超幾何探索滑桿", "t5_quiz":   "隨堂測驗",
}

for k in TRACK_KEYS:
    if "w5_track_" + k not in st.session_state:
        st.session_state["w5_track_" + k] = False

# 滑桿初始值記錄（偵測是否真正移動過）
# ★ 注意：此處數值必須與各 st.slider(..., value=...) 的預設值完全一致
_SLIDER_INIT = {
    "w5_mu":     1.000,   # slider value=1.000（吋）
    "w5_sigma":  0.001,   # slider value=0.001（吋）
    "w5_lambda_poisson": 600,   # slider value=600（輛/小時）
    "w5_t_poisson":      12,    # slider value=12（秒）
    "w5_lambda_exp":     0.4,
    "w5_t_exp":          1.0,
    "w5_lam_weibull":    0.1,
    "w5_beta_weibull":   1.0,
    "w5_N_hyper":        25,
    "w5_n_hyper":        4,
    "w5_pi_hyper":       20,
}
for _sk in _SLIDER_INIT:
    if "w5_sld_moved_" + _sk not in st.session_state:
        st.session_state["w5_sld_moved_" + _sk] = False

def mark_done(key):
    st.session_state["w5_track_" + key] = True

def check_slider(slider_key, track_key):
    current_val = st.session_state.get(slider_key, None)
    init_val    = _SLIDER_INIT.get(slider_key, None)
    if current_val is not None and current_val != init_val:
        if not st.session_state.get("w5_sld_moved_" + slider_key, False):
            st.session_state["w5_sld_moved_" + slider_key] = True
        mark_done(track_key)

def count_done():
    return sum(1 for k in TRACK_KEYS if st.session_state.get("w5_track_" + k, False))

# ══════════════════════════════════════════════════════════════════════
#  HERO 卡片
# ══════════════════════════════════════════════════════════════════════
st.markdown('''
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
    border-radius:16px;padding:28px 40px 24px 40px;
    margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">
    <div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;margin:0 0 8px 0;line-height:1.25;">
        Week 05｜連續機率分配與壽命工程 📈
    </div>
    <div style="color:#94a3b8;font-size:1.05rem;margin:0 0 10px 0;">
        Continuous Distributions &amp; Life Engineering · Chapter 5
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.22);
        border-radius:20px;padding:5px 16px;">
        <span style="color:#93c5fd;font-size:0.82rem;">📖</span>
        <span style="color:#e2e8f0;font-size:0.82rem;font-weight:600;">課本第 5 章 · §5.1–5.6</span>
        <span style="color:#64748b;font-size:0.78rem;">｜《工程統計》Lapin 著</span>
    </div>
</div>
''', unsafe_allow_html=True)

# ── 翻譯提示列 ───────────────────────────────────────────────────────
st.markdown('''
<div style="margin:0 0 10px 0;text-align:center;">
    <span style="display:inline-block;background:#eff6ff;border:1px solid #bfdbfe;
        border-radius:20px;padding:4px 16px;color:#3b82f6;font-size:0.75rem;line-height:1.6;">
        🌐 <b>For English:</b> Right-click anywhere on the page → "Translate to English" (Chrome / Edge built-in translation)
    </span>
</div>
''', unsafe_allow_html=True)

# ── 學習路線提示框 ────────────────────────────────────────────────────
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
            §5.1 常態分配 → §5.2 卜瓦松分配 → §5.3 指數分配 → §5.5 Weibull分配（浴缸曲線）→ §5.6 超幾何分配
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

# ── Section 1 Header ──────────────────────────────────────────────────
st.markdown('''
<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
    border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
    <span style="color:#ffffff;font-size:1.3rem;font-weight:800;">📈 1. 本週核心理論與互動實驗室</span>
</div>
''', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標籤，完成理論閱讀與互動實驗</p>',
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔔 5.1 常態分配",
    "📊 5.2 卜瓦松分配",
    "⏱️ 5.3 指數分配",
    "🛁 5.5 Weibull分配",
    "🎰 5.6 超幾何分配",
])

# ══════════════════════════════════════════════════════════════════════
#  Tab 1：§5.1 常態分配
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§5.1 常態分配</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>常態分配 (Normal Distribution)</b>：統計學最重要的連續分配，由 μ（均值）和 σ（標準差）決定。<br>
            <b>機率密度函數</b>：f(x) = [1/(√2π σ)] × exp[−(x−μ)²/(2σ²)]，−∞ &lt; x &lt; ∞<br>
            <b>特性</b>：對稱鐘形曲線，以 μ 為中心；μ±σ 含 68.26%，μ±2σ 含 95.44%，μ±3σ 含 99.73%。<br>
            <b>標準化</b>：z = (x − μ) / σ，將任意常態分配轉換為標準常態（μ=0, σ=1），查同一張 Z 表。<br><br>
            ▸ <b>百分位數反查</b>：x = μ + z·σ<br>
            ▸ <b>圖 5.2 軸承直徑</b>：μ=1吋，σ=0.001吋，展示 μ±3σ 幾乎涵蓋全部直徑
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#fefce8;border:1px solid #fde047;border-left:4px solid #eab308;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
    <b>🔧 為什麼工程師重視常態分配？</b><br>
    軸承直徑、混凝土強度、人員反應時間……這些工程量測值都近似常態分配。
    掌握常態分配，就能回答「多少比例的產品在規格內」「設計壽命需幾個標準差的裕度」等關鍵問題。
    </div>
    ''', unsafe_allow_html=True)

    # ── 公式卡 ────────────────────────────────────────────────────────
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 標準化轉換</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                z = (x − μ) / σ<br>
                <small style="color:#7c3aed;font-size:0.88rem;">查附錄表 D 取 Φ(z)，即 P(Z ≤ z)</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 百分位數反查</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                x = μ + z·σ<br>
                <small style="color:#7c3aed;font-size:0.88rem;">由機率 p 查 z，再回推原始值 x</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 期望值與變異數</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                E(X) = μ<br>
                Var(X) = σ²
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 靜態四宮格示意圖：σ 對形狀的影響 ──────────────────────────────
    st.markdown("**📊 σ 的大小如何影響常態曲線形狀（靜態預覽）**")
    _x_demo = np.linspace(60, 140, 400)
    _params_demo = [
        (100, 3,  "#1e3a5f", "σ=3（精密）"),
        (100, 7,  "#3b82f6", "σ=7（一般）"),
        (100, 12, "#22c55e", "σ=12（粗糙）"),
        (100, 18, "#ef4444", "σ=18（最寬）"),
    ]
    _fig_demo = go.Figure()
    for _mu0, _sig0, _col0, _lbl0 in _params_demo:
        _y0 = scipy_stats.norm.pdf(_x_demo, _mu0, _sig0)
        _fig_demo.add_trace(go.Scatter(
            x=_x_demo, y=_y0, mode="lines",
            line=dict(color=_col0, width=2.5),
            name=_lbl0,
            hovertemplate=f"x=%{{x:.1f}}<br>f(x)=%{{y:.4f}}<extra>{_lbl0}</extra>"
        ))
    _fig_demo.add_vline(x=100, line_dash="dash", line_color="#94a3b8",
                        annotation_text="μ=100", annotation_position="top right",
                        annotation_font_size=F_ANNOTATION)
    set_chart_layout(_fig_demo, "不同 σ 值的常態曲線（μ=100 固定）", "x 值", "機率密度 f(x)")
    _fig_demo.update_layout(height=300, margin=dict(t=40, b=30))
    st.plotly_chart(_fig_demo, use_container_width=True)

    # ── 互動實驗室 A：常態曲線滑桿探索 ──────────────────────────────
    with st.expander("🛠️ 展開實驗室 A：調整 μ 與 σ，觀察軸承直徑的規格合格率", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受 μ 與 σ 如何決定常態曲線的位置與寬度，以及超出規格（±3σ）的比例。<br>
                <b>你會發現：</b>σ 愈小，合格率愈高；μ 偏離規格中心，超規率急遽上升——這正是製程能力 Cpk 的直觀基礎。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 情境：課本圖 5.2 軸承直徑（單位：吋）</b><br>
        規格中心 = 1.000 吋，工程規格為 ±0.003 吋（即 [0.997, 1.003]）。<br>
        調整滑桿，觀察不同製程參數下，軸承直徑落在規格範圍內的比例如何變化。
        </div>
        ''', unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            mu_val  = st.slider("設定平均值 μ（吋）", 0.998, 1.002, 1.000, 0.0001,
                                format="%.4f", key="w5_mu")
        with col_s2:
            sig_val = st.slider("設定標準差 σ（吋）", 0.0005, 0.003, 0.001, 0.0001,
                                format="%.4f", key="w5_sigma")

        check_slider("w5_mu",    "t1_curve")
        check_slider("w5_sigma", "t1_curve")

        spec_lo, spec_hi = 0.997, 1.003
        p_in_spec = scipy_stats.norm.cdf(spec_hi, mu_val, sig_val) - \
                    scipy_stats.norm.cdf(spec_lo, mu_val, sig_val)
        p_out     = 1.0 - p_in_spec
        z_lo      = (spec_lo - mu_val) / sig_val
        z_hi      = (spec_hi - mu_val) / sig_val

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.metric("合格率 P(規格內)",  f"{p_in_spec*100:.3f}%")
        with col_m2: st.metric("超規率 P(規格外)",  f"{p_out*100:.4f}%")
        with col_m3: st.metric("z 值範圍",
                               f"[{z_lo:.2f}, {z_hi:.2f}]")

        x_plot = np.linspace(mu_val - 4.5*sig_val, mu_val + 4.5*sig_val, 500)
        y_plot = scipy_stats.norm.pdf(x_plot, mu_val, sig_val)
        x_in   = x_plot[(x_plot >= spec_lo) & (x_plot <= spec_hi)]
        y_in   = scipy_stats.norm.pdf(x_in,  mu_val, sig_val)
        x_lo   = x_plot[x_plot < spec_lo]
        y_lo   = scipy_stats.norm.pdf(x_lo,  mu_val, sig_val)
        x_hi   = x_plot[x_plot > spec_hi]
        y_hi   = scipy_stats.norm.pdf(x_hi,  mu_val, sig_val)

        fig1a = go.Figure()
        if len(x_in) > 1:
            fig1a.add_trace(go.Scatter(
                x=np.concatenate([[x_in[0]], x_in, [x_in[-1]]]),
                y=np.concatenate([[0], y_in, [0]]),
                fill="tozeroy", fillcolor="rgba(34,197,94,0.25)",
                line=dict(width=0), name=f"合規 {p_in_spec*100:.2f}%",
                hovertemplate="直徑: %{x:.4f} 吋<br>密度: %{y:.2f}<extra></extra>"
            ))
        if len(x_lo) > 1:
            fig1a.add_trace(go.Scatter(
                x=np.concatenate([[x_lo[0]], x_lo, [x_lo[-1]]]),
                y=np.concatenate([[0], y_lo, [0]]),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.35)",
                line=dict(width=0), name="超規（偏小）",
                hovertemplate="直徑: %{x:.4f} 吋<br>密度: %{y:.2f}<extra></extra>"
            ))
        if len(x_hi) > 1:
            fig1a.add_trace(go.Scatter(
                x=np.concatenate([[x_hi[0]], x_hi, [x_hi[-1]]]),
                y=np.concatenate([[0], y_hi, [0]]),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.35)",
                line=dict(width=0), name="超規（偏大）",
                hovertemplate="直徑: %{x:.4f} 吋<br>密度: %{y:.2f}<extra></extra>"
            ))
        fig1a.add_trace(go.Scatter(
            x=x_plot, y=y_plot, mode="lines",
            line=dict(color="#1e3a5f", width=3), name="常態曲線",
            hovertemplate="直徑: %{x:.4f} 吋<br>密度: %{y:.2f}<extra></extra>"
        ))
        # 當前 μ 標記點
        fig1a.add_trace(go.Scatter(
            x=[mu_val], y=[scipy_stats.norm.pdf(mu_val, mu_val, sig_val)],
            mode="markers", marker=dict(color="#ef4444", size=14, symbol="diamond"),
            name=f"μ = {mu_val:.4f}",
            hovertemplate=f"μ = {mu_val:.4f} 吋<extra></extra>"
        ))
        fig1a.add_vline(x=spec_lo, line_dash="dash", line_color="#94a3b8",
                        annotation_text=f"LSL={spec_lo}", annotation_position="top left",
                        annotation_font_size=F_ANNOTATION)
        fig1a.add_vline(x=spec_hi, line_dash="dash", line_color="#94a3b8",
                        annotation_text=f"USL={spec_hi}", annotation_position="top right",
                        annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig1a, f"軸承直徑常態分配（μ={mu_val:.4f}吋, σ={sig_val:.4f}吋）",
                         "直徑（吋）", "機率密度 f(x)")
        fig1a.update_layout(height=420, yaxis=dict(range=[-20, scipy_stats.norm.pdf(mu_val,mu_val,sig_val)*1.15]))
        st.plotly_chart(fig1a, use_container_width=True)

        if p_in_spec >= 0.9973:
            _card("#22c55e","#f0fdf4","#166534","✅ 達到 ±3σ 以上水準",
                  f"合格率 {p_in_spec*100:.3f}%，超出規格的軸承每千個不到 3 個——製程能力優良！")
        elif p_in_spec >= 0.9544:
            _card("#0369a1","#e0f2fe","#0c4a6e","📊 製程水準：±2σ",
                  f"合格率 {p_in_spec*100:.3f}%。σ 還有壓縮空間，100 個中約有 {(1-p_in_spec)*100:.2f}% 超規。")
        else:
            _card("#ef4444","#fef2f2","#991b1b","⚠️ 合格率偏低",
                  f"合格率僅 {p_in_spec*100:.2f}%，超規率 {p_out*100:.2f}%。考慮縮小 σ 或修正製程中心！")

        if st.button("🔄 重新開始實驗室 A", key="w5_reset_curve"):
            for k in ["w5_mu", "w5_sigma",
                      "w5_sld_moved_w5_mu", "w5_sld_moved_w5_sigma"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 互動實驗室 B：Z轉換逐步計算（例題 5.2 核電廠）────────────────
    with st.expander("🛠️ 展開實驗室 B：Z轉換逐步計算──核電廠例題 5.2", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>熟練「原始值 → z 值 → 查 Z 表 → 機率」的完整四步驟流程。<br>
                <b>你會發現：</b>任何常態分配只要標準化，都能用同一張 Z 表查機率——這正是常態分配的強大之處。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 課本例題 5.2（核電廠安全）</b><br>
        核電廠安全操作人員反應時間 X ~ N(μ=45秒, σ=8秒)。<br>
        <b>問</b>：預警器響起後，操作人員「在 60 秒內完成反應」的機率為何？
        </div>
        ''', unsafe_allow_html=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：計算 z 值",
              "z = (x − μ) / σ = (60 − 45) / 8 = ?（保留小數第 2 位）")
        z_input = st.number_input("z = (60 − 45) / 8 = ?",
                                   value=0.0, step=0.01, format="%.2f", key="w5_calc_z")
        step1_ok = False
        if z_input != 0.0:
            if abs(z_input - 1.88) < 0.015:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟一正確！",
                      "z = (60−45)/8 = 15/8 = <b>1.88</b>。表示 60 秒距離平均值 1.88 個標準差。")
                step1_ok = True
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算一次",
                      f"(60−45)/8 = 15/8 = 1.875 ≈ 1.88（你填了 {z_input:.2f}）")

        if step1_ok:
            st.markdown("---")
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：查 Z 表，Φ(1.88) = ?",
                  "由附錄表 D（標準常態累積機率表）查出 Φ(1.88)，即 P(Z ≤ 1.88)（保留小數第 4 位）")
            phi_input = st.number_input("Φ(1.88) = P(Z ≤ 1.88) = ?",
                                         value=0.0, step=0.0001, format="%.4f", key="w5_calc_phi")
            step2_ok = False
            if phi_input != 0.0:
                if abs(phi_input - 0.9699) < 0.0015:
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                          "Φ(1.88) = <b>0.9699</b>。查表 D：z=1.88 對應累積機率 0.9699。")
                    step2_ok = True
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再查查表 D",
                          f"Φ(1.88) 應為 0.9699（你填了 {phi_input:.4f}）")

            if step2_ok:
                st.markdown("---")
                _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：最終答案",
                      "P(X ≤ 60) = Φ(1.88) = ?（直接填入查到的機率值）")
                ans_input = st.number_input("P(X ≤ 60) = Φ(1.88) = ?",
                                             value=0.0, step=0.0001, format="%.4f", key="w5_calc_ans")
                if ans_input != 0.0:
                    if abs(ans_input - 0.9699) < 0.0015:
                        mark_done("t1_calc")
                        # ─ 完整結果解鎖（v2.3：紫色卡片）
                        _card("#7c3aed","#f5f3ff","#4c1d95","🏆 計算完成，完整結果解鎖！",
                              "P(X ≤ 60) = Φ(z) = Φ(1.88) = 0.9699\n\n"
                              "工程結論：約 97% 的操作人員能在 60 秒內完成反應，"
                              "核電廠安全設計達到極高標準。\n\n"
                              "反查延伸：若要保障 99% 人員在時限內反應，"
                              "應設計多少秒？x = 45 + 2.33 × 8 = 63.64 秒。")

                        # 視覺解鎖：機率面積圖
                        x_ex = np.linspace(20, 80, 400)
                        y_ex = scipy_stats.norm.pdf(x_ex, 45, 8)
                        x_shade = x_ex[x_ex <= 60]
                        y_shade = scipy_stats.norm.pdf(x_shade, 45, 8)
                        fig_ex = go.Figure()
                        fig_ex.add_trace(go.Scatter(
                            x=np.concatenate([[x_shade[0]], x_shade, [x_shade[-1]]]),
                            y=np.concatenate([[0], y_shade, [0]]),
                            fill="tozeroy", fillcolor="rgba(34,197,94,0.30)",
                            line=dict(width=0), name="P(X≤60)=0.9699",
                            hovertemplate="反應時間: %{x:.1f}秒<br>密度: %{y:.4f}<extra></extra>"
                        ))
                        fig_ex.add_trace(go.Scatter(
                            x=x_ex, y=y_ex, mode="lines",
                            line=dict(color="#1e3a5f", width=3),
                            name="反應時間分配",
                            hovertemplate="反應時間: %{x:.1f}秒<br>密度: %{y:.4f}<extra></extra>"
                        ))
                        fig_ex.add_trace(go.Scatter(
                            x=[60], y=[scipy_stats.norm.pdf(60, 45, 8)],
                            mode="markers", marker=dict(color="#ef4444", size=14, symbol="diamond"),
                            name="60秒（查詢點）",
                            hovertemplate="x=60秒<extra></extra>"
                        ))
                        fig_ex.add_vline(x=45, line_dash="dash", line_color="#94a3b8",
                                         annotation_text="μ=45秒", annotation_position="top right",
                                         annotation_font_size=F_ANNOTATION)
                        set_chart_layout(fig_ex,
                                         "核電廠操作人員反應時間 X~N(45, 8²)",
                                         "反應時間（秒）", "機率密度 f(x)")
                        fig_ex.update_layout(height=420)
                        st.plotly_chart(fig_ex, use_container_width=True)

                        col_r1, col_r2 = st.columns(2)
                        with col_r1: st.metric("z 值", "1.88")
                        with col_r2: st.metric("P(X ≤ 60)", "0.9699 ≈ 96.99%")
                    else:
                        _card("#ef4444","#fef2f2","#991b1b","❌ 再確認",
                              f"P(X ≤ 60) = Φ(1.88) = 0.9699（你填了 {ans_input:.4f}）")

        if st.button("🔄 重新開始實驗室 B", key="w5_reset_calc"):
            for k in ["w5_calc_z", "w5_calc_phi", "w5_calc_ans"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §5.1 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§5.1 常態分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q1 = st.radio(
        "📍 **題目：某化學製程的平均產量 X ~ N(μ=30克, σ=0.2克)。"
        "若要使產量大於某規格下限的機率達到 99%，則規格下限應設在幾克？"
        "（提示：P(Z ≤ −2.33) ≈ 0.01，x = μ + z·σ）**",
        ["請選擇...",
         "A. 29.53 克",
         "B. 30.47 克",
         "C. 29.41 克",
         "D. 30.53 克"],
        key="w5_q1_radio"
    )
    if st.button("送出答案", key="w5_q1_btn"):
        if q1 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q1:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "P(X > x) = 0.99 → P(X ≤ x) = 0.01 → z = −2.33。"
                  "x = μ + z·σ = 30 + (−2.33)(0.2) = 30 − 0.466 = 29.53 克。"
                  "這代表 99% 的製程產量都超過 29.53 克，可作為規格下限。")
            mark_done("t1_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "P(X > x) = 99% 表示 P(X ≤ x) = 1%，查表 z ≈ −2.33，"
                  "再代入 x = 30 + (−2.33)(0.2)。注意 z 是負值，x 在 μ 左側！")


# ══════════════════════════════════════════════════════════════════════
#  Tab 2：§5.2 卜瓦松分配
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§5.2 卜瓦松分配</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>卜瓦松過程 (Poisson Process)</b>：事件在時間或空間中以固定平均率 λ 發生，且各段時間相互獨立、無記憶性。<br>
            <b>機率質量函數</b>：p(x; λ, t) = (λt)ˣ e^(−λt) / x!，x = 0, 1, 2, …<br>
            <b>期望值與變異數</b>：E(X) = λt，Var(X) = λt（兩者相等！）<br><br>
            ▸ <b>應用</b>：車輛到收費亭、電報輸入錯誤、瑕疵點分佈、設備故障次數<br>
            ▸ <b>卜瓦松 → 常態近似</b>：當 λt 足夠大（≥ 5），可用常態分配近似
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#fefce8;border:1px solid #fde047;border-left:4px solid #eab308;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
    <b>🔧 為什麼工程師需要卜瓦松分配？</b><br>
    橋梁每年遭遇超重卡車次數、核反應爐冷卻系統每年故障次數、網路封包錯誤率……
    這些「稀有事件」在時間或空間的特定段落中發生次數，都服從卜瓦松分配。
    卜瓦松分配是連接「平均率 λ」與「發生次數機率」的橋梁。
    </div>
    ''', unsafe_allow_html=True)

    # ── 公式卡 ────────────────────────────────────────────────────────
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 卜瓦松機率公式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                p(x; λ, t) = (λt)ˣ · e^(−λt) / x!<br>
                <small style="color:#7c3aed;font-size:0.88rem;">e^(−λt) 查附錄表 B（負指數表）</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 期望值與變異數</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                E(X) = λt<br>
                Var(X) = λt<br>
                <small style="color:#7c3aed;font-size:0.88rem;">期望值 = 變異數（卜瓦松特性）</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：卜瓦松分配長條圖探索 ──────────────────────────
    with st.expander("🛠️ 展開實驗室 A：調整 λ 與 t，觀察卜瓦松分配形狀", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受 λt（期望次數）如何決定卜瓦松分配的形狀與中心位置。<br>
                <b>你會發現：</b>λt 愈大，分配愈對稱、尾部愈長；λt 極小時呈高度右偏，大部分機率集中在 0。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 情境：舊金山大橋收費站（課本例題 §5.2）</b><br>
        尖峰時段車輛到達率 λ=600 輛/小時。觀察 t 秒內，到達車輛數的機率分配。
        </div>
        ''', unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            lam_p = st.slider("平均發生率 λ（輛/小時）", 100, 1000, 600, 50,
                              key="w5_lambda_poisson")
        with col_s2:
            t_p   = st.slider("觀察時段 t（秒，以 1/3600 小時換算）",
                               1, 30, 12, 1, key="w5_t_poisson")

        check_slider("w5_lambda_poisson", "t2_bar")
        check_slider("w5_t_poisson",      "t2_bar")

        lam_t = lam_p * (t_p / 3600)   # 換算成小時單位
        x_pois = np.arange(0, max(int(lam_t * 3) + 5, 10))
        pmf_vals = scipy_stats.poisson.pmf(x_pois, lam_t)
        cdf_vals = scipy_stats.poisson.cdf(x_pois, lam_t)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.metric("λt（期望到達數）", f"{lam_t:.3f}")
        with col_m2: st.metric("E(X) = λt",         f"{lam_t:.3f}")
        with col_m3: st.metric("Var(X) = λt",        f"{lam_t:.3f}")

        fig2a = go.Figure()
        colors_bar = ["#1e3a5f" if abs(x - round(lam_t)) <= 1 else "#60a5fa"
                      for x in x_pois]
        fig2a.add_trace(go.Bar(
            x=x_pois, y=pmf_vals,
            marker_color=colors_bar,
            name="p(x)",
            hovertemplate="到達數 x=%{x}<br>P(X=x)=%{y:.4f}<extra></extra>"
        ))
        fig2a.add_trace(go.Scatter(
            x=x_pois, y=cdf_vals, mode="lines+markers",
            line=dict(color="#22c55e", width=2), yaxis="y2",
            name="累積 F(x)",
            hovertemplate="到達數 x=%{x}<br>P(X≤x)=%{y:.4f}<extra></extra>"
        ))
        # 當前 E(X) 標記
        peak_x = round(lam_t)
        if 0 <= peak_x < len(pmf_vals):
            fig2a.add_trace(go.Scatter(
                x=[peak_x], y=[pmf_vals[peak_x]],
                mode="markers", marker=dict(color="#ef4444", size=14, symbol="diamond"),
                name=f"E(X)={lam_t:.2f}",
                hovertemplate=f"E(X)={lam_t:.2f}<extra></extra>"
            ))
        set_chart_layout(fig2a, f"卜瓦松分配：λ={lam_p}/hr, t={t_p}秒, λt={lam_t:.3f}",
                         "到達車輛數 x", "機率 p(x)")
        fig2a.update_layout(
            height=420,
            yaxis2=dict(overlaying="y", side="right", title="累積機率 F(x)",
                        range=[0, 1.1], showgrid=False)
        )
        st.plotly_chart(fig2a, use_container_width=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","📊 觀察重點",
              f"λt = {lam_t:.3f}，期望在 {t_p} 秒內有 {lam_t:.2f} 輛車到達。"
              f"E(X)=Var(X)={lam_t:.3f}——這是卜瓦松分配的標誌性特徵！")

        if st.button("🔄 重新開始實驗室 A（卜瓦松）", key="w5_reset_pois"):
            for k in ["w5_lambda_poisson", "w5_t_poisson",
                      "w5_sld_moved_w5_lambda_poisson", "w5_sld_moved_w5_t_poisson"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 互動實驗室 B：龍捲風例題 5.4 逐步計算 ───────────────────────
    with st.expander("🛠️ 展開實驗室 B：龍捲風卜瓦松計算──課本例題 5.4", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>完整套用卜瓦松公式，從 λ、t 算到 p(x)，再用餘事件法則算「至少發生一次」。<br>
                <b>你會發現：</b>即使單次機率不高（36%），10 年內「至少一次」的機率竟高達 99.97%！
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 課本例題 5.4（美國中西部龍捲風）</b><br>
        某城市面積 t = 8,000 英畝，每年每英畝被龍捲風覆蓋的密度 λ = 0.0001。<br>
        求（a）一年內恰好發生 1 次；（b）一年內至少發生 1 次。
        </div>
        ''', unsafe_allow_html=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：計算 λt",
              "λt = 0.0001 × 8,000 = ?（這代表一年內預期龍捲風影響的面積比例）")
        lt_input = st.number_input("λt = 0.0001 × 8,000 = ?",
                                    value=0.0, step=0.1, format="%.2f", key="w5_lt")
        step1_ok2 = False
        if lt_input != 0.0:
            if abs(lt_input - 0.8) < 0.05:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟一正確！",
                      "λt = 0.0001 × 8,000 = <b>0.8</b>，平均一年有 0.8 次龍捲風影響。")
                step1_ok2 = True
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算一次",
                      f"0.0001 × 8000 = 0.8（你填了 {lt_input:.2f}）")

        if step1_ok2:
            st.markdown("---")
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算 p(1; 0.0001, 8000)",
                  "p(1) = (λt)¹ · e^(−λt) / 1! = (0.8)¹ · e^(−0.8) / 1。"
                  "提示：e^(−0.8) ≈ 0.4493（查附錄表 B）")
            p1_input = st.number_input("p(1) = (0.8)¹ × e^(−0.8) / 1! ≈ ?（保留小數第 4 位）",
                                        value=0.0, step=0.0001, format="%.4f", key="w5_p1")
            step2_ok2 = False
            if p1_input != 0.0:
                if abs(p1_input - 0.3595) < 0.002:
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                          "p(1) = 0.8 × 0.4493 / 1 = <b>0.3595</b>。一年內恰好一次龍捲風的機率約 36%。")
                    step2_ok2 = True
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再計算",
                          f"0.8 × 0.4493 = {0.8*0.4493:.4f}（你填了 {p1_input:.4f}）")

            if step2_ok2:
                st.markdown("---")
                _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：計算「至少一次」的機率",
                      "P(至少 1 次) = 1 − P(0 次) = 1 − e^(−0.8) = 1 − 0.4493 = ?")
                atleast_input = st.number_input("1 − e^(−0.8) = 1 − 0.4493 = ?（保留小數第 4 位）",
                                                 value=0.0, step=0.0001, format="%.4f", key="w5_atleast")
                if atleast_input != 0.0:
                    if abs(atleast_input - 0.5507) < 0.002:
                        mark_done("t2_calc")
                        _card("#7c3aed","#f5f3ff","#4c1d95","🏆 計算完成，完整結果解鎖！",
                              "P(至少 1 次龍捲風) = 1 − 0.4493 = 0.5507\n\n"
                              "一年內有 55% 的機率受到龍捲風影響。\n\n"
                              "延伸：十年內皆無龍捲風的機率 = (0.4493)^10 = 0.000335，\n"
                              "故十年內至少一次的機率高達 99.97%！")

                        yr_arr = np.arange(1, 21)
                        p_no_arr   = 0.4493 ** yr_arr
                        p_some_arr = 1 - p_no_arr
                        fig2b = go.Figure()
                        fig2b.add_trace(go.Bar(
                            x=yr_arr, y=p_some_arr,
                            marker_color=["#ef4444" if p >= 0.99 else
                                          "#f59e0b" if p >= 0.80 else "#3b82f6"
                                          for p in p_some_arr],
                            hovertemplate="年數=%{x}年<br>P(至少一次)=%{y:.4f}<extra></extra>",
                            name="P(至少一次)"
                        ))
                        fig2b.add_hline(y=0.99, line_dash="dash", line_color="#22c55e",
                                        annotation_text="99%", annotation_position="right",
                                        annotation_font_size=F_ANNOTATION)
                        fig2b.add_trace(go.Scatter(
                            x=[1], y=[0.5507],
                            mode="markers", marker=dict(color="#1e3a5f", size=14, symbol="diamond"),
                            name="第 1 年：55%",
                            hovertemplate="第 1 年 P=0.5507<extra></extra>"
                        ))
                        set_chart_layout(fig2b, "累積年數內至少發生一次龍捲風的機率",
                                         "年數 t", "P(至少一次龍捲風)")
                        fig2b.update_layout(height=420, yaxis=dict(range=[0, 1.05]))
                        st.plotly_chart(fig2b, use_container_width=True)

                        col_r1, col_r2 = st.columns(2)
                        with col_r1: st.metric("一年內 P(恰好一次)", "0.3595")
                        with col_r2: st.metric("一年內 P(至少一次)", "0.5507")
                    else:
                        _card("#ef4444","#fef2f2","#991b1b","❌ 再算",
                              f"1 − 0.4493 = 0.5507（你填了 {atleast_input:.4f}）")

        if st.button("🔄 重新開始實驗室 B（龍捲風）", key="w5_reset_tornado"):
            for k in ["w5_lt", "w5_p1", "w5_atleast"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §5.2 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§5.2 卜瓦松分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q2 = st.radio(
        "📍 **題目：某錄影帶每英呎平均出現 0.1 個雜訊點（λ=0.1）。"
        "考察 200 英呎（λt=20）長的錄影帶，雜訊點剛好等於 20 個的機率"
        "P(X=20) = P(20) − P(19) = 0.5591 − 0.4703 = ？**",
        ["請選擇...",
         "A. 0.0888",
         "B. 0.5591",
         "C. 0.4409",
         "D. 0.1049"],
        key="w5_q2_radio"
    )
    if st.button("送出答案", key="w5_q2_btn"):
        if q2 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q2:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "P(X=20) = P(20) − P(19) = 0.5591 − 0.4703 = 0.0888。"
                  "個別的 p(x) = 累積 F(x) − 累積 F(x−1)——這是由累積機率表求個別機率的關鍵技巧。")
            mark_done("t2_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "P(X=20) 不等於累積 P(X≤20)=0.5591，應用差分公式：P(X=k) = F(k) − F(k−1)。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 3：§5.3 指數分配
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§5.3 指數分配</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>指數分配 (Exponential Distribution)</b>：描述卜瓦松過程中連續兩事件的間隔時間（或距離）。<br>
            <b>CDF</b>：F(t) = P(T ≤ t) = 1 − e^(−λt)，t ≥ 0<br>
            <b>可靠度函數</b>：R(t) = P(T > t) = e^(−λt)（元件能存活超過時間 t 的機率）<br>
            <b>期望值</b>：E(T) = 1/λ = MTBF（平均故障間隔時間）；Var(T) = 1/λ²<br><br>
            ▸ <b>無記憶性</b>：P(T > t+h | T > t) = P(T > h)——舊元件與新元件的剩餘壽命機率相同！<br>
            ▸ <b>應用</b>：電力故障間隔、收費站到達間隔、設備維修等候時間
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#fefce8;border:1px solid #fde047;border-left:4px solid #eab308;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
    <b>🔧 指數分配的工程意義</b><br>
    指數分配是可靠度工程的基礎。若元件的故障符合卜瓦松過程（隨機發生、無磨耗），
    其故障間隔時間就服從指數分配。λ 愈小，MTBF 愈大，元件愈可靠。
    但指數分配的無記憶性也告訴我們：更換元件不一定延長壽命！
    </div>
    ''', unsafe_allow_html=True)

    # ── 公式卡 ────────────────────────────────────────────────────────
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 指數分配 CDF</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                F(t) = 1 − e^(−λt)<br>
                P(T &gt; t) = e^(−λt) = R(t)
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 期望值與百分位數</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                E(T) = 1/λ（MTBF）<br>
                第 p 百分位數：t = −ln(1−p) / λ
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 互動實驗室 A：指數可靠度曲線滑桿 ────────────────────────────
    with st.expander("🛠️ 展開實驗室 A：調整 λ，觀察可靠度如何隨時間衰減", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受故障率 λ 如何影響可靠度曲線的衰減速率，以及 MTBF 的工程意義。<br>
                <b>你會發現：</b>當 t = MTBF = 1/λ 時，可靠度恰好是 e^(−1) ≈ 0.368——元件存活率不到 37%！
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 情境：電力系統故障分析（課本例題 5.5）</b><br>
        電力系統平均每 2.5 年發生一次故障，λ = 1/2.5 = 0.4/年。<br>
        滑桿範圍對應不同系統的可靠度特性。
        </div>
        ''', unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            lam_e = st.slider("故障率 λ（次/年）", 0.1, 2.0, 0.4, 0.05,
                               format="%.2f", key="w5_lambda_exp")
        with col_s2:
            t_e   = st.slider("查詢時間點 t（年）", 0.5, 10.0, 1.0, 0.5,
                               format="%.1f", key="w5_t_exp")

        check_slider("w5_lambda_exp", "t3_exp")
        check_slider("w5_t_exp",      "t3_exp")

        mtbf   = 1.0 / lam_e
        r_t    = math.exp(-lam_e * t_e)
        f_t    = 1 - r_t

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.metric("MTBF = 1/λ",         f"{mtbf:.2f} 年")
        with col_m2: st.metric(f"R({t_e:.1f}) 可靠度",  f"{r_t:.4f}")
        with col_m3: st.metric(f"F({t_e:.1f}) 故障機率", f"{f_t:.4f}")

        t_plot   = np.linspace(0, 15, 400)
        r_plot   = np.exp(-lam_e * t_plot)
        fig3a = go.Figure()
        fig3a.add_trace(go.Scatter(
            x=t_plot, y=r_plot, mode="lines",
            line=dict(color="#22c55e", width=3),
            name="R(t) = e^(−λt)",
            hovertemplate="t=%{x:.1f}年<br>R(t)=%{y:.4f}<extra></extra>"
        ))
        # 當前查詢點
        fig3a.add_trace(go.Scatter(
            x=[t_e], y=[r_t], mode="markers",
            marker=dict(color="#ef4444", size=14, symbol="diamond"),
            name=f"t={t_e:.1f}年, R={r_t:.4f}",
            hovertemplate=f"t={t_e:.1f}年<br>R={r_t:.4f}<extra></extra>"
        ))
        # MTBF 標記線
        r_mtbf = math.exp(-1)
        fig3a.add_vline(x=mtbf, line_dash="dash", line_color="#3b82f6",
                        annotation_text=f"MTBF={mtbf:.2f}年",
                        annotation_position="top right",
                        annotation_font_size=F_ANNOTATION)
        fig3a.add_hline(y=r_mtbf, line_dash="dash", line_color="#3b82f6",
                        annotation_text=f"R(MTBF)=e⁻¹≈{r_mtbf:.4f}",
                        annotation_position="right",
                        annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig3a, f"指數分配可靠度曲線（λ={lam_e:.2f}/年）",
                         "時間 t（年）", "可靠度 R(t)")
        fig3a.update_layout(height=420, yaxis=dict(range=[-0.05, 1.1]))
        st.plotly_chart(fig3a, use_container_width=True)

        if abs(t_e - mtbf) < 0.3:
            _card("#f59e0b","#fffbeb","#92400e","💡 你找到 MTBF 時間點了！",
                  f"當 t = MTBF = {mtbf:.2f} 年時，R(t) = e^(−1) ≈ 0.3679。"
                  "這意味著：即使元件還在「平均壽命」內，仍有約 63% 的機率已故障！")
        else:
            _card("#0369a1","#e0f2fe","#0c4a6e","📊 觀察重點",
                  f"λ={lam_e:.2f} 時，MTBF = {mtbf:.2f} 年，"
                  f"在 t={t_e:.1f} 年時系統尚能運作的機率為 {r_t:.4f}。")

        if st.button("🔄 重新開始實驗室 A（指數）", key="w5_reset_exp"):
            for k in ["w5_lambda_exp", "w5_t_exp",
                      "w5_sld_moved_w5_lambda_exp", "w5_sld_moved_w5_t_exp"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 互動實驗室 B：例題 5.5 電力故障逐步計算 ─────────────────────
    with st.expander("🛠️ 展開實驗室 B：電力故障機率計算──課本例題 5.5", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>從 MTBF 算出 λ，再套用指數 CDF 求機率，並比較改善前後的效益。<br>
                <b>你會發現：</b>花費 100 萬改善設備後，故障機率從 33% 降到 18%——工程師可用此數據評估投資效益。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 課本例題 5.5（電力公用設備）</b><br>
        MTBF = 2.5 年，λ = 0.4/年。<br>
        問：（a）未來一年內至少一次故障的機率？（b）若投資將 λ 降至 0.2，新的故障機率？
        </div>
        ''', unsafe_allow_html=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：計算 F(1)（未改善）",
              "F(1) = 1 − e^(−λt) = 1 − e^(−0.4×1) = 1 − e^(−0.4)。"
              "提示：e^(−0.4) ≈ 0.6703（查附錄表 B）")
        f1_input = st.number_input("F(1) = 1 − 0.6703 = ?（保留 4 位小數）",
                                    value=0.0, step=0.0001, format="%.4f", key="w5_exp_f1")
        step1_ok3 = False
        if f1_input != 0.0:
            if abs(f1_input - 0.3297) < 0.002:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟一正確！",
                      "F(1) = 1 − e^(−0.4) = 1 − 0.6703 = <b>0.3297</b>。"
                      "未來一年約有 33% 的機率發生故障。")
                step1_ok3 = True
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ 再算",
                      f"1 − 0.6703 = 0.3297（你填了 {f1_input:.4f}）")

        if step1_ok3:
            st.markdown("---")
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算改善後 F(1)（λ 降至 0.2）",
                  "改善後 F(1) = 1 − e^(−0.2×1)。提示：e^(−0.2) ≈ 0.8187")
            f1_new_input = st.number_input("改善後 F(1) = 1 − 0.8187 = ?（保留 4 位小數）",
                                            value=0.0, step=0.0001, format="%.4f", key="w5_exp_f1new")
            step2_ok3 = False
            if f1_new_input != 0.0:
                if abs(f1_new_input - 0.1813) < 0.002:
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                          "改善後 F(1) = 0.1813，故障率降至約 18%。")
                    step2_ok3 = True
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌ 再算",
                          f"1 − 0.8187 = 0.1813（你填了 {f1_new_input:.4f}）")

            if step2_ok3:
                st.markdown("---")
                _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：效益評估",
                      "改善使每年故障機率降低了多少個百分點？（0.3297 − 0.1813 = ?）")
                diff_input = st.number_input("降低幅度 = 0.3297 − 0.1813 = ?（保留 4 位小數）",
                                              value=0.0, step=0.0001, format="%.4f", key="w5_exp_diff")
                if diff_input != 0.0:
                    if abs(diff_input - 0.1484) < 0.003:
                        mark_done("t3_calc")
                        _card("#7c3aed","#f5f3ff","#4c1d95","🏆 計算完成，完整結果解鎖！",
                              "投資 100 萬後，每年故障機率從 32.97% 降至 18.13%，降低約 14.84 個百分點。\n\n"
                              "這降幅不算大——每年只減少不到 15% 的故障率，"
                              "若每次故障損失 < 67 萬元，投資效益就不明顯。\n\n"
                              "課本結論：公司管理階層決定不購買，因可靠度提高不大！")

                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1: st.metric("未改善 F(1)",  "0.3297 (33%)")
                        with col_r2: st.metric("改善後 F(1)",  "0.1813 (18%)")
                        with col_r3: st.metric("降幅", "14.84%")
                    else:
                        _card("#ef4444","#fef2f2","#991b1b","❌ 再算",
                              f"0.3297 − 0.1813 = 0.1484（你填了 {diff_input:.4f}）")

        if st.button("🔄 重新開始實驗室 B（電力故障）", key="w5_reset_exp_b"):
            for k in ["w5_exp_f1", "w5_exp_f1new", "w5_exp_diff"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §5.3 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§5.3 指數分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q3 = st.radio(
        "📍 **題目：某電容器 MTBF = 5 年，故障符合指數分配。"
        "P(連續運作超過 5 年) = R(5) = ？**",
        ["請選擇...",
         "A. e^(−1) ≈ 0.3679",
         "B. 0.5000",
         "C. 1 − e^(−1) ≈ 0.6321",
         "D. e^(−5) ≈ 0.0067"],
        key="w5_q3_radio"
    )
    if st.button("送出答案", key="w5_q3_btn"):
        if q3 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q3:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "MTBF=5年 → λ=1/5=0.2/年。R(5) = e^(−0.2×5) = e^(−1) ≈ 0.3679。"
                  "換言之，即使元件尚在「平均壽命」內，仍有約 63% 已故障──這體現了指數分配的無記憶性。")
            mark_done("t3_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "λ = 1/MTBF = 1/5 = 0.2，R(t) = e^(−λt) = e^(−0.2×5) = e^(−1)。"
                  "當 t = MTBF 時，可靠度恆為 e^(−1) ≈ 0.3679，這是指數分配的重要特性！")


# ══════════════════════════════════════════════════════════════════════
#  Tab 4：§5.5 Weibull 分配（浴缸曲線）
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§5.5 Weibull 分配（浴缸曲線）</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>Weibull 分配</b>：可靠度分析最彈性的壽命時間分配，含兩個參數：<br>
            　λ（尺度參數，scale）：控制曲線的橫向伸縮<br>
            　β（形狀參數，shape）：決定故障率函數的趨勢<br>
            <b>CDF</b>：F(t) = 1 − e^(−(λt)^β)<br>
            <b>可靠度</b>：R(t) = e^(−(λt)^β)<br>
            <b>故障率</b>：h(t) = λβ(λt)^(β−1)<br><br>
            ▸ β &lt; 1：故障率遞減（早期失效 / 設計缺陷）<br>
            ▸ β = 1：故障率固定（隨機失效，退化為指數分配）<br>
            ▸ β &gt; 1：故障率遞增（磨耗失效 / 老化）
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#fefce8;border:1px solid #fde047;border-left:4px solid #eab308;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
    <b>🔧 浴缸曲線（Bathtub Curve）是壽命工程的核心</b><br>
    任何機械元件或系統，其故障率隨時間的變化都呈現「浴缸」形狀：<br>
    ① 初生期（DFR, β&lt;1）：製造缺陷導致高初始故障率，隨時間快速下降<br>
    ② 穩定期（CFR, β=1）：隨機故障，使用指數分配描述最合適<br>
    ③ 磨耗期（IFR, β&gt;1）：元件老化，故障率快速上升
    </div>
    ''', unsafe_allow_html=True)

    # ── SVG 浴缸曲線架構圖（自繪，符合 v2.4 B-2 規範）────────────────
    def _make_bathtub_svg(beta, lam, t_query):
        """動態生成 Weibull 浴缸曲線 SVG"""
        W, H = 680, 300
        pad_l, pad_r, pad_t, pad_b = 60, 30, 50, 55
        chart_w = W - pad_l - pad_r
        chart_h = H - pad_t - pad_b
        t_max   = 20.0

        # 計算浴缸曲線數據
        ts = np.linspace(0.05, t_max, 300)
        ht = lam * beta * (lam * ts) ** (beta - 1)
        ht_clipped = np.clip(ht, 0, 3.0)
        h_max = min(float(ht_clipped.max()) * 1.1, 3.0)
        if h_max <= 0: h_max = 1.0

        def tx(t): return pad_l + (t / t_max) * chart_w
        def ty(h): return pad_t + chart_h - (h / h_max) * chart_h

        # 構建曲線路徑
        pts = []
        for ti, hi in zip(ts, ht_clipped):
            pts.append(f"{tx(ti):.1f},{ty(hi):.1f}")
        path_d = "M " + " L ".join(pts[:1]) + " " + " L ".join(pts[1:])

        # 查詢點
        ht_query = lam * beta * (lam * t_query) ** (beta - 1)
        ht_query_clipped = min(ht_query, h_max)
        qx = tx(t_query); qy = ty(ht_query_clipped)

        # β 對應文字與顏色
        if   beta < 0.9:  stage_text = "早期失效 DFR (β<1)";  curve_color = "#ef4444"
        elif beta > 1.1:  stage_text = "磨耗失效 IFR (β>1)";  curve_color = "#f59e0b"
        else:             stage_text = "隨機失效 CFR (β≈1)";  curve_color = "#22c55e"

        # MTBF 線
        mtbf = (1.0 / lam) * (1.0 if beta == 1 else 1.0)
        mtbf_x = min(tx(mtbf), pad_l + chart_w) if mtbf <= t_max else pad_l + chart_w

        svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"
                  style="width:100%;max-width:{W}px;margin:0 auto;display:block;
                         background:#0f172a;border-radius:12px;">
  <!-- 標題 -->
  <text x="{W/2:.0f}" y="26" text-anchor="middle" fill="#f1f5f9"
        font-size="14" font-weight="700">
    浴缸曲線（Bathtub Curve）｜λ={lam:.3f}, β={beta:.2f}
  </text>
  <!-- 背景分區 -->
  <rect x="{pad_l}" y="{pad_t}" width="{chart_w*0.25:.0f}" height="{chart_h}"
        fill="rgba(239,68,68,0.08)" rx="0"/>
  <rect x="{pad_l + chart_w*0.25:.0f}" y="{pad_t}" width="{chart_w*0.50:.0f}" height="{chart_h}"
        fill="rgba(34,197,94,0.06)" rx="0"/>
  <rect x="{pad_l + chart_w*0.75:.0f}" y="{pad_t}" width="{chart_w*0.25:.0f}" height="{chart_h}"
        fill="rgba(239,68,68,0.08)" rx="0"/>
  <!-- 軸線 -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+chart_h}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{pad_t+chart_h}" x2="{pad_l+chart_w}" y2="{pad_t+chart_h}"
        stroke="#475569" stroke-width="1.5"/>
  <!-- 軸標籤 -->
  <text x="{W/2:.0f}" y="{H-10}" text-anchor="middle" fill="#94a3b8" font-size="12">時間 t（年）</text>
  <text x="15" y="{pad_t + chart_h/2:.0f}" text-anchor="middle" fill="#94a3b8" font-size="12"
        transform="rotate(-90,15,{pad_t + chart_h/2:.0f})">故障率 h(t)</text>
  <!-- 分區標籤 -->
  <text x="{pad_l + chart_w*0.125:.0f}" y="{pad_t+16}" text-anchor="middle"
        fill="#fca5a5" font-size="11" font-weight="600">初生期</text>
  <text x="{pad_l + chart_w*0.50:.0f}" y="{pad_t+16}" text-anchor="middle"
        fill="#86efac" font-size="11" font-weight="600">使用期（隨機故障）</text>
  <text x="{pad_l + chart_w*0.875:.0f}" y="{pad_t+16}" text-anchor="middle"
        fill="#fca5a5" font-size="11" font-weight="600">磨耗期</text>
  <!-- Weibull 曲線 -->
  <path d="{path_d}" fill="none" stroke="{curve_color}" stroke-width="3" stroke-linecap="round"/>
  <!-- 當前查詢點 -->
  <circle cx="{qx:.1f}" cy="{qy:.1f}" r="7" fill="#f59e0b" stroke="white" stroke-width="2"/>
  <line x1="{qx:.1f}" y1="{qy:.1f}" x2="{qx:.1f}" y2="{pad_t+chart_h}"
        stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="{min(qx+8, pad_l+chart_w-60):.0f}" y="{min(qy-8, pad_t+chart_h-10):.0f}"
        fill="#fbbf24" font-size="11">h({t_query:.1f})={ht_query:.3f}</text>
  <!-- β 說明框 -->
  <rect x="{pad_l+chart_w-190}" y="{pad_t+chart_h-68}" width="185" height="64"
        fill="rgba(30,58,95,0.85)" rx="6"/>
  <text x="{pad_l+chart_w-100:.0f}" y="{pad_t+chart_h-52}" text-anchor="middle"
        fill="#f59e0b" font-size="12" font-weight="700">{stage_text}</text>
  <text x="{pad_l+chart_w-100:.0f}" y="{pad_t+chart_h-36}" text-anchor="middle"
        fill="#e2e8f0" font-size="11">h({t_query:.1f}) = {ht_query:.4f}/年</text>
  <text x="{pad_l+chart_w-100:.0f}" y="{pad_t+chart_h-20}" text-anchor="middle"
        fill="#e2e8f0" font-size="11">R({t_query:.1f}) = {math.exp(-(lam*t_query)**beta):.4f}</text>
</svg>'''
        return svg

    # ── 互動實驗室 A：Weibull 浴缸曲線滑桿 ──────────────────────────
    with st.expander("🛠️ 展開實驗室 A：調整 β 與 λ，看浴缸曲線如何變化", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>親眼看到形狀參數 β 如何決定故障率的上升、水平或下降趨勢。<br>
                <b>你會發現：</b>β=1 時曲線是水平線（指數分配）；β&gt;2 時故障率在壽命末期急遽飆升。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            lam_w = st.slider("尺度參數 λ（1/年）", 0.05, 0.50, 0.10, 0.01,
                               format="%.2f", key="w5_lam_weibull")
        with col_s2:
            beta_w = st.slider("形狀參數 β（浴缸關鍵）", 0.2, 4.0, 1.0, 0.1,
                                format="%.1f", key="w5_beta_weibull")
        with col_s3:
            t_w = st.slider("查詢時間 t（年）", 1, 20, 5, 1, key="w5_t_weibull")

        check_slider("w5_lam_weibull",  "t4_weibull")
        check_slider("w5_beta_weibull", "t4_weibull")

        ht_w = lam_w * beta_w * (lam_w * t_w) ** (beta_w - 1)
        rt_w = math.exp(-(lam_w * t_w) ** beta_w)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.metric(f"h({t_w}) 故障率", f"{ht_w:.4f}/年")
        with col_m2: st.metric(f"R({t_w}) 可靠度",  f"{rt_w:.4f}")
        with col_m3:
            if   beta_w < 0.9: st.metric("β 故障型態", "早期失效 DFR")
            elif beta_w > 1.1: st.metric("β 故障型態", "磨耗失效 IFR")
            else:              st.metric("β 故障型態", "隨機失效 CFR")

        # 自繪 SVG 浴缸曲線
        svg_str = _make_bathtub_svg(beta_w, lam_w, t_w)
        st.markdown(svg_str, unsafe_allow_html=True)

        # Plotly 曲線（可靠度 + 故障率）
        t_arr  = np.linspace(0.1, 20, 400)
        ht_arr = lam_w * beta_w * (lam_w * t_arr) ** (beta_w - 1)
        rt_arr = np.exp(-(lam_w * t_arr) ** beta_w)
        fig4a  = go.Figure()
        fig4a.add_trace(go.Scatter(
            x=t_arr, y=ht_arr, mode="lines",
            line=dict(color="#ef4444", width=2.5), name="h(t) 故障率",
            hovertemplate="t=%{x:.1f}年<br>h(t)=%{y:.4f}<extra></extra>"
        ))
        fig4a.add_trace(go.Scatter(
            x=t_arr, y=rt_arr, mode="lines",
            line=dict(color="#22c55e", width=2.5), yaxis="y2", name="R(t) 可靠度",
            hovertemplate="t=%{x:.1f}年<br>R(t)=%{y:.4f}<extra></extra>"
        ))
        fig4a.add_trace(go.Scatter(
            x=[t_w], y=[ht_w], mode="markers",
            marker=dict(color="#ef4444", size=14, symbol="diamond"),
            name=f"h({t_w})={ht_w:.4f}",
            hovertemplate=f"h({t_w:.1f})={ht_w:.4f}<extra></extra>"
        ))
        set_chart_layout(fig4a, f"Weibull 故障率 h(t) 與可靠度 R(t)（β={beta_w:.1f}, λ={lam_w:.2f}）",
                         "時間 t（年）", "故障率 h(t)")
        fig4a.update_layout(
            height=420,
            yaxis2=dict(overlaying="y", side="right", title="可靠度 R(t)",
                        range=[-0.05, 1.1], showgrid=False)
        )
        st.plotly_chart(fig4a, use_container_width=True)

        if   beta_w < 0.9:
            _card("#ef4444","#fef2f2","#991b1b","🔺 早期失效期（β < 1）",
                  f"β={beta_w:.1f}，故障率隨時間遞減。工程對策：燒機測試（Burn-In Test）篩選出缺陷品。")
        elif beta_w > 1.1:
            _card("#f59e0b","#fffbeb","#92400e","🔺 磨耗失效期（β > 1）",
                  f"β={beta_w:.1f}，故障率隨時間遞增。工程對策：預防保養（Preventive Maintenance），在壽命末期前更換。")
        else:
            _card("#22c55e","#f0fdf4","#166534","✅ 隨機失效期（β ≈ 1）",
                  f"β≈1，Weibull 退化為指數分配，故障率約為常數 λ={lam_w:.2f}。使用 MTBF 進行可靠度分析。")

        if st.button("🔄 重新開始實驗室 A（Weibull）", key="w5_reset_weibull"):
            for k in ["w5_lam_weibull", "w5_beta_weibull", "w5_t_weibull",
                      "w5_sld_moved_w5_lam_weibull", "w5_sld_moved_w5_beta_weibull"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 互動實驗室 B：例題 5.7 保險絲逐步計算 ───────────────────────
    with st.expander("🛠️ 展開實驗室 B：Weibull 逐步計算──課本例題 5.7 保險絲", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>掌握 Weibull 可靠度公式的計算步驟，特別是含有分數次方的對數處理技巧。<br>
                <b>你會發現：</b>β=0.1（早期失效），保險絲運作 5 年與 15 年的可靠度幾乎相同——因故障率已極低！
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 課本例題 5.7（保險絲壽命）</b><br>
        保險絲壽命 T ~ Weibull，參數：λ=0.005/年，β=0.1。<br>
        <b>求</b>：保險絲可運作超過 10 年的機率 R(10) = e^(−(λ×10)^β)
        </div>
        ''', unsafe_allow_html=True)

        _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟一：計算 λt = 0.005 × 10",
              "λt 是 Weibull 指數項的基底。")
        s1_input = st.number_input("λt = 0.005 × 10 = ?（保留 3 位小數）",
                                    value=0.0, step=0.001, format="%.3f", key="w5_wb_s1")
        wb_s1_ok = False
        if s1_input != 0.0:
            if abs(s1_input - 0.05) < 0.002:
                _card("#22c55e","#f0fdf4","#166534","✅ 步驟一正確！",
                      "λt = 0.005 × 10 = <b>0.05</b>。")
                wb_s1_ok = True
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌", f"0.005 × 10 = 0.05（你填了 {s1_input:.3f}）")

        if wb_s1_ok:
            st.markdown("---")
            _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟二：計算 β × ln(λt) = 0.1 × ln(0.05)",
                  "利用對數化簡 (λt)^β：先求 ln(0.05)≈ −2.9957，再乘以 β=0.1。")
            s2_input = st.number_input("0.1 × ln(0.05) = 0.1 × (−2.9957) ≈ ?（保留 4 位小數）",
                                        value=0.0, step=0.0001, format="%.4f", key="w5_wb_s2")
            wb_s2_ok = False
            if s2_input != 0.0:
                if abs(s2_input - (-0.2996)) < 0.003:
                    _card("#22c55e","#f0fdf4","#166534","✅ 步驟二正確！",
                          "0.1 × (−2.9957) = <b>−0.2996</b>（即 ln[(0.05)^0.1]）。")
                    wb_s2_ok = True
                else:
                    _card("#ef4444","#fef2f2","#991b1b","❌",
                          f"應為 −0.2996（你填了 {s2_input:.4f}），注意 ln(0.05) = ln(5/100) ≈ −2.9957。")

            if wb_s2_ok:
                st.markdown("---")
                _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟三：計算 (λt)^β = exp(−0.2996)",
                      "e^(−0.2996) ≈ ?（保留 4 位小數）")
                s3_input = st.number_input("e^(−0.2996) ≈ ?（保留 4 位小數）",
                                            value=0.0, step=0.0001, format="%.4f", key="w5_wb_s3")
                wb_s3_ok = False
                if s3_input != 0.0:
                    if abs(s3_input - 0.7411) < 0.003:
                        _card("#22c55e","#f0fdf4","#166534","✅ 步驟三正確！",
                              "e^(−0.2996) = <b>0.7411</b>，即 (0.05)^0.1 = 0.7411。")
                        wb_s3_ok = True
                    else:
                        _card("#ef4444","#fef2f2","#991b1b","❌",
                              f"e^(−0.2996)≈0.7411（你填了 {s3_input:.4f}）")

                if wb_s3_ok:
                    st.markdown("---")
                    _card("#0369a1","#e0f2fe","#0c4a6e","✏️ 步驟四：R(10) = exp(−(λt)^β) = exp(−0.7411)",
                          "最後一步：R(10) = e^(−0.7411) ≈ ?（保留 4 位小數）")
                    s4_input = st.number_input("R(10) = e^(−0.7411) ≈ ?（保留 4 位小數）",
                                                value=0.0, step=0.0001, format="%.4f", key="w5_wb_s4")
                    if s4_input != 0.0:
                        if abs(s4_input - 0.4766) < 0.003:
                            mark_done("t4_calc")
                            _card("#7c3aed","#f5f3ff","#4c1d95","🏆 計算完成，完整結果解鎖！",
                                  "R(10) = e^(−(0.005×10)^0.1) = e^(−0.7411) ≈ 0.4766\n\n"
                                  "保險絲可運作超過 10 年的機率約 47.7%。\n\n"
                                  "延伸對比：R(5) ≈ 0.5008，R(15) ≈ 0.4622——"
                                  "三者相差極小，因為 β=0.1 < 1，故障率隨時間遞減已趨近於 0！")

                            # 解鎖完整比較表
                            t_arr_wb = [5, 10, 15, 20]
                            r_arr_wb = [round(math.exp(-(0.005 * t) ** 0.1), 4) for t in t_arr_wb]
                            h_arr_wb = [round(0.005 * 0.1 * (0.005 * t) ** (0.1 - 1), 4) for t in t_arr_wb]
                            df_wb = pd.DataFrame({
                                "時間 t（年）":  t_arr_wb,
                                "R(t) 可靠度":  r_arr_wb,
                                "h(t) 故障率":  h_arr_wb,
                            })
                            st.dataframe(df_wb, use_container_width=True, hide_index=True)
                        else:
                            _card("#ef4444","#fef2f2","#991b1b","❌",
                                  f"e^(−0.7411)≈0.4766（你填了 {s4_input:.4f}）")

        if st.button("🔄 重新開始實驗室 B（Weibull）", key="w5_reset_wb_b"):
            for k in ["w5_wb_s1","w5_wb_s2","w5_wb_s3","w5_wb_s4"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §5.5 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§5.5 Weibull 分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q4 = st.radio(
        "📍 **題目：某渦輪葉片的故障時間符合 Weibull 分配，β = 2.5（磨耗型）。"
        "若在 t = MTTF 前進行預防更換，這種策略適合哪一種浴缸曲線階段的元件？**",
        ["請選擇...",
         "A. β < 1 的元件（早期失效），提前更換可有效降低故障率",
         "B. β > 1 的元件（磨耗失效），故障率隨時間遞增，在失效前更換最合理",
         "C. β = 1 的元件（隨機失效），無記憶性，更換不影響故障率",
         "D. β 的大小不影響預防保養策略"],
        key="w5_q4_radio"
    )
    if st.button("送出答案", key="w5_q4_btn"):
        if q4 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "B." in q4:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "β > 1 表示磨耗失效（IFR），故障率隨使用時間遞增，預防保養最有意義。"
                  "β < 1（早期失效）：更換新品反而重置高故障率，沒有好處。"
                  "β = 1（隨機失效）：無記憶性，更換不影響可靠度。")
            mark_done("t4_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "預防保養（在壽命末期前更換）只對「磨耗失效（β > 1）」有效！"
                  "對隨機失效（β=1）無效；對早期失效（β<1）甚至有反效果。")


# ══════════════════════════════════════════════════════════════════════
#  Tab 5：§5.6 超幾何分配
# ══════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #99f6e4;margin:8px 0 14px 0;">
        <div style="background:#0f766e;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">📌 核心概念：§5.6 超幾何分配</span>
        </div>
        <div style="background:#f0fdfa;padding:14px 18px;color:#134e4a;font-size:1.05rem;line-height:1.8;">
            <b>超幾何分配 (Hypergeometric Distribution)</b>：<br>
            適用於<b>有限母體</b>、<b>不放回（不還原）抽樣</b>的情況。<br>
            與二項分配不同：各次試驗<b>非獨立</b>（因為已抽出的項目不放回）。<br>
            <b>機率公式</b>：h(r; n, π, N) = C(πN, r) × C((1−π)N, n−r) / C(N, n)<br>
            <b>期望值</b>：E(R) = nπ（與二項相同！）<br>
            <b>變異數</b>：Var(R) = nπ(1−π) × (N−n)/(N−1)（比二項多乘有限母體校正因子）
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="background:#fefce8;border:1px solid #fde047;border-left:4px solid #eab308;
                border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
    <b>🔧 超幾何 vs 二項：什麼時候要用超幾何？</b><br>
    ① 母體有限（如：一批 25 個變壓器中取 4 個測試）<br>
    ② 不放回抽樣（電子元件破壞性測試後無法放回）<br>
    ③ n/N > 5%（樣本佔母體比例不可忽略）<br>
    → 三個條件同時滿足時，必須用超幾何分配，不能用二項近似！
    </div>
    ''', unsafe_allow_html=True)

    # ── 公式卡 ────────────────────────────────────────────────────────
    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 超幾何機率公式</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                h(r; n, π, N) = C(πN,r)·C((1−π)N, n−r) / C(N, n)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">C(n,k) = n! / (k!(n−k)!)</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 有限母體校正因子</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;
                        color:#4c1d95;font-size:1.1rem;line-height:1.9;text-align:center;">
                Var(R) = nπ(1−π) × (N−n)/(N−1)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">n/N ≤ 0.05 時可用二項近似</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 靜態示意圖：超幾何 vs 二項 機率比較（課本表 5.1）──────────────
    st.markdown("**📊 課本表 5.1：N=25 時超幾何（精確）vs 二項（近似）機率比較（n=4, π=0.2）**")
    _df_comp = pd.DataFrame({
        "瑕疵品數 r": [0, 1, 2, 3, 4],
        "二項近似 b(r;4,0.2)": [0.4096, 0.4096, 0.1536, 0.0256, 0.0016],
        "超幾何精確 N=25":     [0.38300, 0.45059, 0.15020, 0.01581, 0.00040],
        "超幾何精確 N=100":    [0.40333, 0.41905, 0.15312, 0.02326, 0.00124],
    })
    st.dataframe(_df_comp, use_container_width=True, hide_index=True)
    _card("#0369a1","#e0f2fe","#0c4a6e","📊 觀察重點",
          "N=100 時超幾何機率更接近二項近似（因 n/N = 4/100 = 4% < 5%）；"
          "N=25 時差異明顯（n/N = 16%），不可用二項近似！")

    # ── 互動實驗室 A：超幾何 vs 二項對比滑桿 ────────────────────────
    with st.expander("🛠️ 展開實驗室 A：探索超幾何分配與二項近似的差距", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;
                        letter-spacing:0.05em;text-transform:uppercase;margin-bottom:5px;">
                🎯 本實驗室教學目的
            </div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>感受 N 大小如何決定超幾何與二項分配的差異，以及有限母體校正因子的效果。<br>
                <b>你會發現：</b>N 愈大，n/N 愈小，超幾何愈接近二項——這說明了何時可以用二項「近似」超幾何。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                    padding:10px 14px;margin:0 0 12px 0;color:#1e40af;font-size:0.97rem;">
        <b>📋 情境：電子元件批次驗收（不放回破壞性測試）</b><br>
        一批 N 個印刷電路板，其中 π% 為瑕疵品，隨機抽取 n 個進行破壞性測試（抽後不放回）。
        </div>
        ''', unsafe_allow_html=True)

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            N_h = st.slider("母體大小 N（批量）", 20, 200, 25, 5, key="w5_N_hyper")
        with col_s2:
            n_h = st.slider("樣本數 n（抽測個數）", 2, 15, 4, 1, key="w5_n_hyper")
        with col_s3:
            pi_h = st.slider("瑕疵率 π（%）", 5, 50, 20, 5, key="w5_pi_hyper")

        check_slider("w5_N_hyper",  "t5_hyper")
        check_slider("w5_n_hyper",  "t5_hyper")
        check_slider("w5_pi_hyper", "t5_hyper")

        pi_frac = pi_h / 100.0
        D_h = int(N_h * pi_frac)   # 瑕疵品數
        G_h = N_h - D_h            # 合格品數
        ratio_nN = n_h / N_h
        fpc = (N_h - n_h) / (N_h - 1) if N_h > 1 else 1.0
        e_r = n_h * pi_frac
        var_hyper = n_h * pi_frac * (1 - pi_frac) * fpc
        var_binom = n_h * pi_frac * (1 - pi_frac)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1: st.metric("n/N 比例",     f"{ratio_nN:.3f}")
        with col_m2: st.metric("有限母體校正因子", f"{fpc:.4f}")
        with col_m3: st.metric("超幾何 Var(R)", f"{var_hyper:.4f}")
        with col_m4: st.metric("二項 Var(R)",   f"{var_binom:.4f}")

        # 計算超幾何機率（精確）
        from math import comb
        r_max_h = min(n_h, D_h)
        r_vals_h = list(range(0, r_max_h + 1))
        def hyper_pmf(r, D, G, n, N):
            if r > D or n - r > G or n - r < 0: return 0.0
            return comb(D, r) * comb(G, n - r) / comb(N, n)
        hyper_probs = [hyper_pmf(r, D_h, G_h, n_h, N_h) for r in r_vals_h]
        binom_probs = [scipy_stats.binom.pmf(r, n_h, pi_frac) for r in r_vals_h]

        fig5a = go.Figure()
        x_offset = 0.2
        fig5a.add_trace(go.Bar(
            x=[r - x_offset for r in r_vals_h], y=hyper_probs,
            width=0.35, marker_color="#1e3a5f",
            name="超幾何（精確）",
            hovertemplate="r=%{x:.0f}<br>超幾何機率=%{y:.4f}<extra></extra>"
        ))
        fig5a.add_trace(go.Bar(
            x=[r + x_offset for r in r_vals_h], y=binom_probs,
            width=0.35, marker_color="#60a5fa",
            name="二項（近似）",
            hovertemplate="r=%{x:.0f}<br>二項機率=%{y:.4f}<extra></extra>"
        ))
        set_chart_layout(fig5a,
                         f"超幾何 vs 二項（N={N_h}, n={n_h}, π={pi_h}%, n/N={ratio_nN:.2%}）",
                         "抽到的瑕疵品數 r", "機率")
        fig5a.update_layout(height=420, barmode="overlay")
        st.plotly_chart(fig5a, use_container_width=True)

        if ratio_nN <= 0.05:
            _card("#22c55e","#f0fdf4","#166534","✅ n/N ≤ 5%，可用二項分配近似",
                  f"n/N = {ratio_nN:.3f} ≤ 0.05，有限母體校正因子 {fpc:.4f} ≈ 1，兩柱高度幾乎相同。")
        else:
            _card("#ef4444","#fef2f2","#991b1b","⚠️ n/N > 5%，應使用精確的超幾何分配",
                  f"n/N = {ratio_nN:.3f} > 0.05，有限母體效應顯著（FPC={fpc:.4f}），二項近似誤差不可忽略！")

        if st.button("🔄 重新開始實驗室 A（超幾何）", key="w5_reset_hyper"):
            for k in ["w5_N_hyper", "w5_n_hyper", "w5_pi_hyper",
                      "w5_sld_moved_w5_N_hyper", "w5_sld_moved_w5_n_hyper", "w5_sld_moved_w5_pi_hyper"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # ── 隨堂小測驗 §5.6 ───────────────────────────────────────────────
    st.markdown('''
    <div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                border:1px solid #fde68a;margin:8px 0 10px 0;">
        <div style="background:#d97706;padding:10px 18px;">
            <span style="color:white;font-weight:700;font-size:1.0rem;">💡 隨堂小測驗：§5.6 超幾何分配</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    q5 = st.radio(
        "📍 **題目：運送 25 個變壓器（N=25），其中 5 個瑕疵品（π=0.2），"
        "隨機抽取 4 個測試（n=4，不放回）。"
        "以下哪項計算正確求得 P(R=2)？**",
        ["請選擇...",
         "A. C(5,2)×C(20,2) / C(25,4) = 10×190/12650 ≈ 0.1502",
         "B. C(4,2) × 0.2² × 0.8² ≈ 0.1536（用二項公式）",
         "C. C(5,2) × C(20,2) = 1,900 ≈ 0.1900",
         "D. 5/25 × 4/24 ≈ 0.0333"],
        key="w5_q5_radio"
    )
    if st.button("送出答案", key="w5_q5_btn"):
        if q5 == "請選擇...":
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 請先選擇答案","請勾選一個選項再送出。")
        elif "A." in q5:
            _card("#22c55e","#f0fdf4","#166534","🎉 恭喜答對！",
                  "超幾何公式：h(2;4,0.2,25) = C(5,2)×C(20,2)/C(25,4) = 10×190/12650 = 0.1502。"
                  "（選項B是二項近似值 0.1536，誤差較大，因為 n/N=16% > 5%）")
            mark_done("t5_quiz")
        else:
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示",
                  "超幾何公式：h(r) = C(瑕疵品數,r) × C(良品數,n−r) / C(N,n)。"
                  "注意分子是「從瑕疵品選 r 個」×「從良品選 n−r 個」的組合數，分母是從全部 N 個中選 n 個。")


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
    "wp":          "w5",
    "sheet_name":  "Week 05 互動",
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

real_password = get_weekly_password_safe("Week 05")
if not real_password:
    real_password = "888888"

_card("#475569","#f8fafc","#334155","🔒 測驗鎖定中",
      "請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。")
_col_pw, _col_btn = st.columns([5, 1])
with _col_pw:
    user_code = st.text_input("密碼", type="password", key="w5_unlock_code",
                               label_visibility="collapsed",
                               placeholder="🔑 請輸入 6 位數解鎖密碼…")
with _col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w5_unlock_btn")

if user_code != real_password:
    if user_code != "":
        _card("#ef4444","#fef2f2","#991b1b","❌ 密碼錯誤","請確認字母與數字是否正確！")
else:
    render_quiz_section({
        "wp":           "w5",
        "sheet_name":   "Week 05",
        "form_key":     "week5_unified_quiz",
        "perfect_msg":  '連續機率分配五大主題全數掌握！壽命工程推論能力大躍進。',
        "good_msg":     '建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。',
        "retry_msg":    '請回顧本週各節的概念說明與互動實驗，常態 Z 轉換需要多練習！',
        "questions": [
            {
                "key":         "qf1",
                "text":        '**Q1（§5.1）：某鋼索在重複荷載下的斷裂強度 X ~ N(μ=500 MPa, σ=20 MPa)。若設計荷載上限為 540 MPa，則超過設計荷載的機率 P(X > 540) = ？',
                "options":     ['請選擇...', 'A. Φ(2.0) = 0.9772', 'B. 1 − Φ(2.0) = 0.0228', 'C. Φ(−2.0) = 0.0228', 'D. 2 × [1 − Φ(2.0)] = 0.0456'],
                "correct":     "B.",
                "points":      25,
                "explanation": '§5.1：z=(540−500)/20=2.0，P(X>540)=1−Φ(2.0)=1−0.9772=0.0228。超過設計荷載的機率僅約 2.3%，符合工程設計安全裕度。',
            },
            {
                "key":         "qf2",
                "text":        '**Q2（§5.2）：某海洋浮標的感應器每年平均遭遇 0.5 次重大衝擊（λ=0.5/年）。在未來 3 年（λt=1.5）中，剛好 2 次重大衝擊的機率p(2) = (1.5)² × e^(−1.5) / 2! ≈ ？（e^(−1.5)≈0.2231）',
                "options":     ['請選擇...', 'A. 0.2510', 'B. 0.3347', 'C. 0.2231', 'D. 0.1255'],
                "correct":     "A.",
                "points":      25,
                "explanation": '§5.2：λt=0.5×3=1.5，p(2)=(1.5)²×e^(−1.5)/2! = 2.25×0.2231/2 = 0.2510。注意 e^(−1.5)≈0.2231（查附錄表 B）。',
            },
            {
                "key":         "qf3",
                "text":        '**Q3（§5.3）：某橋梁電腦監控系統 MTBF = 4 年（λ=0.25/年）。系統在接下來 2 年內不發生故障的機率 R(2) = ？',
                "options":     ['請選擇...', 'A. 1 − e^(−0.5) ≈ 0.3935', 'B. e^(−0.5) ≈ 0.6065', 'C. e^(−2) ≈ 0.1353', 'D. 1 − e^(−2) ≈ 0.8647'],
                "correct":     "B.",
                "points":      25,
                "explanation": '§5.3：λ=1/MTBF=1/4=0.25/年，R(2)=e^(−λt)=e^(−0.25×2)=e^(−0.5)≈0.6065。系統在 2 年內正常運作的機率約 60.7%。',
            },
            {
                "key":         "qf4",
                "text":        '**Q4（§5.6）：某批次共 50 個矽晶圓（N=50），其中有 10 個（π=0.2）有微缺陷。品管員隨機抽取 n=5 個進行破壞性測試（不放回）。以下哪項描述正確？',
                "options":     ['請選擇...', 'A. n/N = 10%，超過 5%，必須使用超幾何分配，不可用二項近似', 'B. n/N = 10%，但因批量大，仍可用二項分配', 'C. 由於 π=0.2 不算小，不適合用超幾何分配', 'D. 放回或不放回對機率計算結果沒有影響'],
                "correct":     "A.",
                "points":      25,
                "explanation": '§5.6：n/N = 5/50 = 10% > 5%，有限母體效應顯著（FPC=(50−5)/(50−1)=0.918）。不放回抽樣且 n/N > 5%，必須使用超幾何分配。',
            },
        ],
    })

#  底部速查卡
# ══════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("📚 本週核心概念速查卡（考前複習用）", expanded=False):
    _cards = [
        ("#0f766e","#f0fdfa","#134e4a","📌 §5.1 常態分配",
         ["PDF：f(x)=1/(√2πσ)·exp[−(x−μ)²/(2σ²)]",
          "標準化：z = (x−μ)/σ，查附錄表 D",
          "μ±σ：68.26%；μ±2σ：95.44%；μ±3σ：99.73%",
          "百分位數反查：x = μ + z·σ"]),
        ("#7c3aed","#f5f3ff","#4c1d95","📐 §5.2 卜瓦松分配",
         ["p(x;λ,t) = (λt)ˣ·e^(−λt)/x!，查附錄表 B, C",
          "E(X) = Var(X) = λt（期望值等於變異數！）",
          "三假設：獨立、常數率、不可同時",
          "卜瓦松 → 常態近似：λt ≥ 5 時"]),
        ("#0369a1","#e0f2fe","#0c4a6e","⏱️ §5.3 指數分配",
         ["F(t)=1−e^(−λt)，R(t)=e^(−λt)（可靠度）",
          "E(T)=1/λ=MTBF，Var(T)=1/λ²",
          "t=MTBF 時 R = e^(−1) ≈ 0.3679",
          "無記憶性：P(T>t+h|T>t)=P(T>h)"]),
        ("#d97706","#fef3c7","#92400e","🛁 §5.5 Weibull 分配",
         ["F(t)=1−e^(−(λt)^β)，R(t)=e^(−(λt)^β)",
          "h(t)=λβ(λt)^(β−1)（故障率函數）",
          "β<1：DFR 早期失效；β=1：CFR 隨機失效（指數）",
          "β>1：IFR 磨耗失效；β=2：Rayleigh 分配"]),
        ("#22c55e","#f0fdf4","#166534","🎰 §5.6 超幾何分配",
         ["h(r;n,π,N)=C(πN,r)·C((1−π)N,n−r)/C(N,n)",
          "E(R)=nπ（同二項）",
          "Var(R)=nπ(1−π)·(N−n)/(N−1)（比二項多 FPC）",
          "n/N ≤ 5% 時可用二項近似"]),
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