# 檔案位置： D:\Engineering_Statistics_App\pages\02_Week_02.py
import streamlit as st
import pandas as pd
import numpy as np
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    import subprocess as _sp, sys
    _sp.check_call([sys.executable,"-m","pip","install","plotly","--quiet"])
    import plotly.express as px
    import plotly.graph_objects as go

# ── 匯入統一樣式庫 (從 utils/style.py 抓取魔法函數) ─────────
try:
    from utils.style import apply_theme, set_chart_layout, F_ANNOTATION, F_TITLE
    apply_theme()
except Exception as e:
    st.error(f"樣式載入失敗，請確認 utils/style.py 存在。錯誤：{e}")
    # 容錯預設值，避免網頁崩潰
    F_ANNOTATION = 20
    F_TITLE = 24
    def set_chart_layout(fig, *args, **kwargs): return fig

# ── 後端資料庫 ────────────────────────────────────────────
try:
    from utils.gsheets_db import save_score, check_has_submitted, verify_student, get_weekly_password
except ImportError:
    def save_score(*a, **k): return False
    def check_has_submitted(*a, **k): return False
    def verify_student(*a, **k): return False, None
    def get_weekly_password(*a, **k): return "888888"

# ── Card helper (injected by patch) ─────────────────────────────────
def _card(color, bg, tc, title, msg, fstr=False):
    html = (
        f'<div style="border-radius:12px;overflow:hidden;'
        f'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
        f'border:1px solid #e2e8f0;margin:8px 0;">'
        f'<div style="background:{color};padding:10px 18px;">'
        f'<span style="color:white;font-weight:700;font-size:1.0rem;">{title}</span></div>'
        f'<div style="background:{bg};padding:14px 18px;'
        f'color:{tc};font-size:1.05rem;line-height:1.7;">{msg}</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────


# ── 登入防護 ──────────────────────────────────────────────
if "password_correct" not in st.session_state or not st.session_state.password_correct:
    st.markdown("""
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
    """, unsafe_allow_html=True)
    st.stop()


# =====================================================================
# 標題與學習地圖
# =====================================================================
st.markdown(
    '<div style="background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);'
    'border-radius:16px;padding:28px 40px 24px 40px;'
    'margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.2);text-align:center;">'
    '<div style="color:#f1f5f9;font-size:2.2rem;font-weight:900;margin:0 0 8px 0;">'
    'Week 02&#65372;&#32479;&#35336;&#36039;&#26009;&#20043;&#25551;&#36848;&#12289;&#38515;&#31034;&#21450;&#25216;&#35676; 📊</div>'
    '<div style="color:#94a3b8;font-size:1.05rem;margin:0;">'
    'Describing, Presenting and Exploring Statistical Data · Chapter 2</div>'
    '</div>',
    unsafe_allow_html=True)

st.markdown(
    '<div style="background:#eff6ff;border-left:5px solid #3b82f6;border-radius:8px;'
    'padding:12px 20px;color:#1e40af;font-size:1.05rem;margin-bottom:16px;line-height:1.6;">'
    '📌 本週學習路線：請依序點選下方各小節的標簺，完成理論閱讀與互動實驗。'
    '完成所有標簺後，再挑戰最後的<strong>整合性總測驗</strong>！</div>',
    unsafe_allow_html=True)

st.markdown(
    '<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);'
    'border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">'
    '<span style="color:#fff;font-size:1.3rem;font-weight:800;">📚 1. 核心理論與互動實驗室</span></div>',
    unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 10px 4px;">👆 請依序點選下方各小節標簺，完成理論閱讀與互動實驗</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 2.1 次數分配",
    "📍 2.2 位置的測度",
    "📦 2.3 差異性的量度",
    "⚖️ 2.4 比例"
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1：次數分配
# ═══════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📊 2.1 次數分配 (Frequency Distribution)")

    _card("#0f766e","#f0fdfa","#134e4a","📌 核心概念",
          "直接蒐集、尚未整理的資料稱為 <b>原始資料 (raw data)</b>。"
          "將原始資料分類整理，就是 <b>敘述統計 (descriptive statistics)</b> 的主要工作。")

    st.markdown("""
    <div class="why-box">
    <b>🔧 為什麼工程師需要這個？</b><br>
    想像你量測了 200 根螺栓的直徑——這 200 個數字本身無法告訴你任何事。
    把它們「整理成次數分配表、畫成直方圖」後，你才能看出：<br>
    • 大部分直徑集中在哪裡？&nbsp;&nbsp;• 有沒有異常的極端值？&nbsp;&nbsp;• 分佈是否對稱？
    </div>
    """, unsafe_allow_html=True)

    st.markdown('''
    <div style="display:flex;gap:14px;margin:10px 0 14px 0;background:#f0fdfa;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #99f6e4;">
            <div style="background:#0f766e;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:1.0rem;">📋 次數分配表</span>
            </div>
            <div style="background:#f0fdfa;padding:14px 16px;color:#134e4a;
                        font-size:1.05rem;line-height:1.75;">
                將資料依數值大小分組，列出各組的資料個數（次數）。是所有圖表的資料來源。
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #99f6e4;">
            <div style="background:#0f766e;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:1.0rem;">📊 直方圖 (Histogram)</span>
            </div>
            <div style="background:#f0fdfa;padding:14px 16px;color:#134e4a;
                        font-size:1.05rem;line-height:1.75;">
                以相連矩形的<b>面積</b>代表次數。能直觀看出資料分布的形狀，是工程品管最常用的圖。
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #99f6e4;">
            <div style="background:#0f766e;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:1.0rem;">📈 累積次數多邊形 (Ogive)</span>
            </div>
            <div style="background:#f0fdfa;padding:14px 16px;color:#134e4a;
                        font-size:1.05rem;line-height:1.75;">
                描繪「截至某值共有多少資料」。可快速回答：「有幾 % 的產品低於規格？」
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="discover-box">
    <b>🔬 發現式實驗室 A：組距的黃金平衡</b><br>
    拖動滑桿，親眼看看「組距設太細」與「設太粗」各自的問題。
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室 A：從原始資料到直方圖（認識組距的影響）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>理解「組距」的選擇如何影響直方圖傳達的資訊。<br>
                <b>你會發現：</b>組距太細 → 雜訊太多看不出規律；組距太粗 → 細節被掩蓋；最佳組數約為 √n。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        np.random.seed(42)
        raw_data_demo = np.concatenate([
            np.random.normal(72, 3, 120),
            np.random.normal(80, 1.5, 20),
            [60, 61, 88, 90]
        ])

        st.write("📐 **工程場景**：某製程共量測了 **144 根螺栓** 的直徑（mm），以下是原始資料片段：")
        st.code(f"{sorted(raw_data_demo[:20].tolist())!r}  ...（共 144 筆）")

        if st.button("🔄 復原預設值", key="reset_demo"):
            st.session_state["demo_bins"] = 10
            st.rerun()

        n_bins_demo = st.slider("⬅️ 請調整組數（分組數量）", min_value=2, max_value=80, value=10, key="demo_bins")

        counts_d, edges_d = np.histogram(raw_data_demo, bins=n_bins_demo)
        bin_width = edges_d[1] - edges_d[0]
        n_empty = np.sum(counts_d == 0)

        bin_centers = (edges_d[:-1] + edges_d[1:]) / 2
        # 標籤策略：≤20 組顯示在外、≤40 組顯示在內、>40 組隱藏（hover 看）
        y_max_hist = int(max(counts_d) * 1.30) + 1
        if n_bins_demo <= 20:
            _txt_pos, _txt_size = "outside", max(11, min(F_ANNOTATION, int(220 // max(n_bins_demo, 1))))
        elif n_bins_demo <= 40:
            _txt_pos, _txt_size = "inside",  max(9,  int(160 // max(n_bins_demo, 1)))
        else:
            _txt_pos, _txt_size = "none", 9

        fig_demo = go.Figure(go.Bar(
            x=bin_centers, y=counts_d, width=bin_width * 0.98,
            marker_color="#3b82f6",
            text=counts_d if _txt_pos != "none" else None,
            textposition=_txt_pos,
            textfont=dict(size=_txt_size),
            hovertemplate="組中點: %{x:.1f} mm<br>次數: %{y}<extra></extra>"
        ))
        set_chart_layout(fig_demo, f"直方圖 — 分 {n_bins_demo} 組（組距 ≈ {bin_width:.1f} mm）", "直徑 (mm)", "次數")
        fig_demo.update_layout(
            bargap=0.02,
            height=380,
            yaxis=dict(range=[0, y_max_hist]),
            margin=dict(t=50, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_demo, use_container_width=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("組距", f"{bin_width:.2f} mm")
        col_m2.metric("空組數量", f"{n_empty} 組")
        col_m3.metric("建議組數（√n 法則）", f"≈ {int(np.sqrt(len(raw_data_demo)))} 組")

        if n_bins_demo <= 4:
            _card("#ef4444","#fef2f2","#991b1b","❌ 組數太少","許多細節被掩蓋，看不出資料的真實分佈形狀。")
        elif n_bins_demo >= 40:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 組數過多",f"出現 {n_empty} 個空組，雜訊太多，反而看不清楚整體趨勢。")
        else:
            _card("#22c55e","#f0fdf4","#166534","✅ 組數適中",f"分佈形狀清晰可辨，兩個群集清楚可見！")

        st.markdown("""
        <div class="discover-box">
        💡 <b>實驗結論</b>：組數大約取 <b>√n</b>（樣本數的平方根）是個好的起點。
        分組的目的是「化繁為簡」，不是保留所有細節，也不是過度壓縮。
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室 B：Ogive 累積次數多邊形（工程規格查核利器）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>學會用 Ogive 圖目視估讀「有多少比例的資料低於某規格值」，不需計算。<br>
                <b>你會發現：</b>拖動規格線後，圖上紅點直接告訴你幾 % 的產品合格；這正是品管最常用的快速決策工具。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("**工程應用**：品管工程師常問：「有多少百分比的產品直徑低於 74 mm（規格下限）？」Ogive 讓你不用計算就能目視估讀。")

        OG_DEFAULT_DATA = "22,25,28,30,31,31,32,35,36,38,40,41,45,48,50,55,58,60,62,65"
        if st.button("🔄 復原預設值", key="og_reset"):
            st.session_state["og_input"] = OG_DEFAULT_DATA
            st.session_state["og_spec"] = 55.0
            st.session_state["sl_og"] = 6
            st.rerun()

        user_input_og = st.text_input("輸入量測數據（逗號分隔）", OG_DEFAULT_DATA, key="og_input")
        spec_line = st.number_input("📏 輸入規格上限值（畫紅線）", value=st.session_state.get("og_spec", 55.0), step=1.0, key="og_spec")

        try:
            data_og = np.array([float(x.strip()) for x in user_input_og.split(',')])
            bins_og = st.slider("選擇分組數量", 3, 15, 6, key="sl_og")
            counts_og, bin_edges_og = np.histogram(data_og, bins=bins_og)
            cum_counts_og = np.cumsum(counts_og)
            cum_pct = cum_counts_og / len(data_og) * 100

            df_freq = pd.DataFrame({
                '組下限': np.round(bin_edges_og[:-1], 2),
                '組上限': np.round(bin_edges_og[1:], 2),
                '次數 (f)': counts_og,
                '累積次數 (F)': cum_counts_og,
                '累積 %': np.round(cum_pct, 1)
            })
            
            df_freq_str = df_freq.copy()
            df_freq_str['組下限'] = df_freq_str['組下限'].map(lambda x: f"{x:.2f}")
            df_freq_str['組上限'] = df_freq_str['組上限'].map(lambda x: f"{x:.2f}")
            df_freq_str['累積 %'] = df_freq_str['累積 %'].map(lambda x: f"{x:.1f}")
            st.markdown(f'<div class="big-table">{df_freq_str.to_html(index=False)}</div>', unsafe_allow_html=True)

            fig_og = go.Figure()
            fig_og.add_trace(go.Scatter(x=np.append(bin_edges_og[0], bin_edges_og[1:]), y=np.append(0, cum_pct),
                                        mode='lines+markers', name='累積百分比 (%)', line=dict(color='#3b82f6', width=2.5), marker=dict(size=8)))
            
            # ✨ 移到右下方防重疊 ✨
            fig_og.add_vline(x=spec_line, line_color="red", line_dash="dash", line_width=2,
                             annotation_text=f"規格上限 {spec_line}", annotation_position="bottom right", 
                             annotation_font_size=F_ANNOTATION)

            idx = np.searchsorted(bin_edges_og[1:], spec_line)
            if 0 <= idx < len(cum_pct):
                est_pct = cum_pct[idx]
                fig_og.add_annotation(x=spec_line, y=est_pct, text=f"≈ {est_pct:.0f}% 低於此值",
                                      showarrow=True, arrowhead=2, bgcolor="rgba(220,38,38,0.8)", font=dict(color="white", size=F_ANNOTATION))

            set_chart_layout(fig_og, "累積次數多邊形 (Ogive)", "數值", "累積百分比 (%)")
            fig_og.update_layout(
                height=360,
                yaxis=dict(range=[0, 108]),
                margin=dict(t=50, b=40, l=50, r=20)
            )
            st.plotly_chart(fig_og, use_container_width=True)
        except Exception:
            _card("#ef4444","#fef2f2","#991b1b","❌ 格式錯誤","請確保輸入的是以逗號分隔的數字。")

    _card("#d97706","#fffbeb","#92400e","💡 2.1 隨堂小測驗","請根據直方圖的概念作答：")
    q_tab1 = st.radio("📍 **在繪製工程數據的直方圖時，如果將「組距」設定得非常小（分組數極多），會發生什麼現象？**",
        ["請選擇...", "A. 直方圖會變成一條完美的平滑曲線，呈現最詳細的資料分佈", "B. 會產生過多空組與雜訊，反而失去彙總資料的意義"], key="q_tab1")
    if st.button("送出答案", key="btn_t1"):
        if q_tab1 == "B. 會產生過多空組與雜訊，反而失去彙總資料的意義":
            _card("#22c55e","#f0fdf4","#166534","🎉 正確！","切得太細，每組只剩 0~1 筆資料，就喪失了彙整的意義。")
        elif q_tab1 != "請選擇...":
            _card("#ef4444","#fef2f2","#991b1b","❌ 思考提示","平滑曲線需要的是「足夠多的資料筆數」，而不是無限多的組數。")


# ═══════════════════════════════════════════════════════════════════
# TAB 2：位置的測度
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📍 2.2 統計量數：位置的測度")

    _card("#0f766e","#f0fdfa","#134e4a","📌 核心概念",
          "「位置的測度」告訴我們資料的「中心」或某個「相對位置」在哪裡。"
          "工程上最常用的有三種：<b>平均數、中位數、百分位數</b>。")

    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 算術平均數</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;color:#4c1d95;font-size:1.05rem;line-height:1.9;text-align:center;">
                X&#772; = &#931; X&#7522; / n<br>
                <small style="color:#7c3aed;font-size:0.88rem;">所有觀測值加總 ÷ 個數</small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 中位數 (m)</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;color:#4c1d95;font-size:1.05rem;line-height:1.9;text-align:center;">
                排序後位於正中間的值<br>
                <small style="color:#7c3aed;font-size:0.88rem;">
                    n 為奇數 → 第 (n+1)/2 個值<br>
                    n 為偶數 → 中間兩個值的平均
                </small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("""
    <div class="why-box">
    <b>🔧 為什麼工程師需要區分兩者？</b><br>
    • <b>平均數</b>：反映「整體總量」，但容易被極端值拉偏，就像一個重量很大的砝碼把蹺蹺板壓歪。<br>
    • <b>中位數</b>：反映「典型狀況」，對極端值有抵抗力。適合描述「一般情況下」的狀態。<br>
    工程師必須根據場景選擇正確的量數，才不會做出誤導性的報告！
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室 A：極端值的拉力戰（互動發現）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>親眼見識平均數和中位數面對異常值時的不同反應，建立「選錯量數會誤導決策」的直覺。<br>
                <b>你會發現：</b>注入越多異常值，平均數被拉得越遠；而中位數幾乎紋風不動——這就是為什麼工程報告要選對量數。
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col_o1, col_o2 = st.columns(2)
        with col_o1: out_cnt = st.slider("💉 注入的異常值數量", 0, 30, 0, key="out_cnt")
        with col_o2: out_val = st.slider("📈 異常值的大小", 60, 200, 150, key="out_val")

        np.random.seed(2)
        base_d = np.random.normal(50, 5, 100).tolist()
        full_d = np.array(base_d + [out_val] * out_cnt)

        mean_v, median_v = np.mean(full_d), np.median(full_d)
        std_v = np.std(full_d, ddof=1)
        sk_v = 3 * (mean_v - median_v) / std_v if std_v > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📊 樣本數 n", len(full_d))
        c2.metric("🔴 平均數", f"{mean_v:.2f}", delta=f"{mean_v - 50:.2f} vs 真實均值50")
        c3.metric("🔵 中位數", f"{median_v:.2f}", delta=f"{median_v - 50:.2f} vs 真實均值50")
        c4.metric("📐 偏態係數 SK", f"{sk_v:.3f}")

        fig_skew = px.histogram(x=full_d, nbins=40, color_discrete_sequence=["#94a3b8"])
        
        # ✨ 防重疊：平均數在上，中位數在下 ✨
        pos_mean = "top right" if mean_v >= median_v else "top left"
        pos_med = "bottom left" if mean_v >= median_v else "bottom right"

        fig_skew.add_vline(x=mean_v, line_color="red", line_width=3, annotation_text=f"平均數: {mean_v:.1f}", annotation_position=pos_mean, annotation_font_size=F_ANNOTATION)
        fig_skew.add_vline(x=median_v, line_color="#3b82f6", line_width=3, annotation_text=f"中位數: {median_v:.1f}", annotation_position=pos_med, annotation_font_size=F_ANNOTATION)
        
        set_chart_layout(fig_skew, f"資料分佈 — 含 {out_cnt} 個異常值（大小={out_val}），SK = {sk_v:.3f}", "數值", "次數")
        fig_skew.update_layout(
            height=360,
            margin=dict(t=60, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_skew, use_container_width=True)

        if out_cnt == 0:
            _card("#3b82f6","#eff6ff","#1e40af","📊 目前無異常値","平均數與中位數幾乎重合（正態分佈的特徵）。")
        elif out_cnt <= 5:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 注意：異常値影響",f"注入少量異常値後，平均數已被拉至 {mean_v:.1f}，而中位數僅微移至 {median_v:.1f}。")
        else:
            _card("#ef4444","#fef2f2","#991b1b","🚨 異常値嚴重拉偏",f"平均數 {mean_v:.1f} 已遠離真實中心 50，而中位數 {median_v:.1f} 仍接近真實値。")

        st.markdown("""
        <div class="discover-box">
        💡 <b>設計思考</b>：在橋樑設計中，若用「含少數超大荷載的平均值」來代表「典型荷載」，
        可能導致設計值被高估，增加不必要的工程成本。反之亦然——若異常大值代表的是真實的極端情境，
        就不能用中位數忽略它。統計工具沒有對錯，<b>關鍵在於你的工程問題是什麼</b>。
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室 B：百分位數與箱形圖解讀（工程規格神器）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>學會用箱形圖快速掌握資料分佈的五個關鍵數字，並用 1.5×IQR 規則識別離群值。<br>
                <b>你會發現：</b>拖動 k 值查看對應百分位數位置；調整後可看出哪些螺栓直徑超出「合理範圍」，需要工程師進一步調查。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("""
        **百分位數 $P_k$**：排序後有 k% 的資料小於等於此值。  
        **四分位距 IQR = Q3 - Q1**：中間 50% 資料的涵蓋範圍，是工程上偵測離群值的標準工具。
        """)

        np.random.seed(2)
        base_d_pct = np.random.normal(50, 5, 100)

        if st.button("🔄 復原預設值", key="reset_pct"):
            st.session_state["k_pct"] = 85
            st.rerun()

        k_pct = st.slider("查詢第 k 百分位數 (Pₖ)", 1, 99, 85, key="k_pct")
        pk_val = np.percentile(base_d_pct, k_pct)
        q1_v, q3_v = np.percentile(base_d_pct, [25, 75])
        iqr_v = q3_v - q1_v
        lower_fence, upper_fence = q1_v - 1.5 * iqr_v, q3_v + 1.5 * iqr_v
        outliers = base_d_pct[(base_d_pct < lower_fence) | (base_d_pct > upper_fence)]

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric(f"P{k_pct}", f"{pk_val:.2f}"); col_p2.metric("Q1 (P25)", f"{q1_v:.2f}")
        col_p3.metric("Q3 (P75)", f"{q3_v:.2f}"); col_p4.metric("IQR = Q3-Q1", f"{iqr_v:.2f}")

        fig_bx = go.Figure()
        fig_bx.add_trace(go.Box(x=base_d_pct, name='螺栓直徑', boxpoints='all', jitter=0.4, pointpos=0, marker=dict(color='rgba(59,130,246,0.4)', size=4), line=dict(color='#3b82f6')))
        
        fig_bx.add_vline(x=lower_fence, line_dash="dash", line_color="red", line_width=2, annotation_text=f"下邊界 {lower_fence:.1f}", annotation_position="bottom right", annotation_font_size=F_ANNOTATION)
        fig_bx.add_vline(x=upper_fence, line_dash="dash", line_color="red", line_width=2, annotation_text=f"上邊界 {upper_fence:.1f}", annotation_position="top right", annotation_font_size=F_ANNOTATION)
        fig_bx.add_vline(x=pk_val, line_dash="dot", line_color="#22c55e", line_width=2.5, annotation_text=f"P{k_pct} = {pk_val:.1f}", annotation_position="top left", annotation_font_size=F_ANNOTATION)
        
        set_chart_layout(fig_bx, f"箱形圖 ＋ 1.5×IQR 離群值邊界（P{k_pct} 標示）", "測量值")
        fig_bx.update_layout(
            height=320,
            margin=dict(t=50, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_bx, use_container_width=True)

        if len(outliers) > 0: _card("#f59e0b","#fffbeb","#92400e",f"🔍 偵測到 {len(outliers)} 個離群値",f"發現 {len(outliers)} 個離群値：{np.round(outliers, 2).tolist()}")

        _card("#0369a1","#f0f9ff","#0c4a6e","📖 箱形圖五數綜覽",
              f"最小值: {np.min(base_d_pct):.2f} &nbsp;│&nbsp; Q1: {q1_v:.2f} &nbsp;│&nbsp; "
              f"中位數: {np.median(base_d_pct):.2f} &nbsp;│&nbsp; Q3: {q3_v:.2f} &nbsp;│&nbsp; "
              f"最大值: {np.max(base_d_pct):.2f}<br>"
              "「1.5×IQR 規則」是 John Tukey 提出的業界標準——超出此範圍的值應接受工程師進一步調查。")

    st.markdown("---")
    _card("#d97706","#fffbeb","#92400e","💡 2.2 隨堂小測驗","請根據平均數與中位數的概念作答：")
    q_tab2 = st.radio(
        "📍 **某工程師團隊 5 人的月薪為 5萬、5萬、6萬、6萬，及計畫主持人的 50 萬。用哪個量數「客觀描述一般工程師薪資」？**",
        ["請選擇...", "A. 平均數 (14.4 萬)", "B. 中位數 (6 萬)"],
        key="q_tab2"
    )
    if st.button("送出答案", key="btn_t2"):
        if q_tab2 == "B. 中位數 (6 萬)":
            _card("#22c55e","#f0fdf4","#166534","🎉 正確！","計畫主持人的 50 萬是極端値，將平均數從 6 萬拉升至 14.4 萬，嚴重失真。中位數 6 萬才能客觀反映基層工程師的典型薪資。")
        elif q_tab2 != "請選擇...":
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示","算算看：(5+5+6+6+50)/5 = 14.4 萬。誰把這個數字拉這麼高？")


# ═══════════════════════════════════════════════════════════════════
# TAB 3：差異性的量度
# ═══════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📦 2.3 差異性的量度 (Measures of Variability)")

    st.markdown("""
    <div class="why-box">
    <b>🔧 為什麼「差異性」比「平均值」更重要？</b><br>
    兩家工廠都宣稱平均強度 = 50 MPa，但 A 廠每根都是 50 MPa，B 廠有些是 30 有些是 70。
    你會選哪家的材料？——<b>平均數相同，但風險天差地別！</b><br>
    變異度是工程品質的核心指標：變異越大 = 產品越不穩定 = 工程風險越高。
    </div>
    """, unsafe_allow_html=True)

    st.markdown('''
    <div style="display:flex;gap:16px;margin:12px 0;background:#f5f3ff;padding:14px;border-radius:14px;">
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 樣本變異數 s²</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;color:#4c1d95;font-size:1.05rem;line-height:1.9;text-align:center;">
                s² = &#931;(X&#7522; − X&#772;)² / (n−1)<br>
                <small style="color:#7c3aed;font-size:0.88rem;">
                    除以 n−1（不是 n）是為了讓 s² 成為<br>母體變異數 &#963;² 的「不偏估計量」
                </small>
            </div>
        </div>
        <div style="flex:1;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #ddd6fe;">
            <div style="background:#7c3aed;padding:9px 16px;">
                <span style="color:white;font-weight:700;font-size:0.95rem;">📐 偏態係數 SK</span>
            </div>
            <div style="flex:1;background:#f5f3ff;padding:18px 16px;color:#4c1d95;font-size:1.05rem;line-height:1.9;text-align:center;">
                SK = 3(X&#772; − m) / s<br>
                <small style="color:#7c3aed;font-size:0.88rem;">
                    SK &gt; 0 → 正偏態（右偏，平均數 &gt; 中位數）<br>
                    SK &lt; 0 → 負偏態（左偏，平均數 &lt; 中位數）<br>
                    SK ≈ 0 → 對稱分佈
                </small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    with st.expander("📖 課本例題 2.3 重現：等候上機方式的比較（動態調整版）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">📖 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用課本例題驗證「標準差」決定了服務品質的穩定性，而不只是平均值。<br>
                <b>你會發現：</b>調整兩種排隊方式的標準差後，箱形圖寬度與「等超過 30 分鐘的機率」會同步變化——標準差越小，服務越可預期。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("""
        **💻 工程場景**：電腦機房有 3 台電腦，有兩種排隊方式：
        - **方法 A（各自排隊）**：每台電腦前各排一列，共 3 列
        - **方法 B（單一排隊）**：所有人排同一列，輪到誰就用哪台空出的電腦
        兩種方法的**平均等候時間都是 15 分鐘**，但體驗完全不同！
        """)

        if st.button("🔄 復原預設值", key="reset_wait"):
            st.session_state["std_A"] = 6.5
            st.session_state["std_B"] = 1.5
            st.rerun()

        cA, cB = st.columns(2)
        with cA: std_A = st.slider("方法 A 標準差 (σ_A)", 1.0, 12.0, 6.5, step=0.5, key="std_A")
        with cB: std_B = st.slider("方法 B 標準差 (σ_B)", 0.5, 6.0, 1.5, step=0.5, key="std_B")

        np.random.seed(3)
        data_A, data_B = np.random.normal(15, std_A, 300), np.random.normal(15, std_B, 300)
        pct_A_over30, pct_B_over30 = (data_A > 30).mean() * 100, (data_B > 30).mean() * 100

        df_ab = pd.DataFrame({'等候時間 (分鐘)': np.concatenate([data_A, data_B]), '方式': ['A（各自排隊）'] * 300 + ['B（單一排隊）'] * 300})
        fig_ab = px.box(df_ab, x='方式', y='等候時間 (分鐘)', color='方式', points="outliers", color_discrete_map={'A（各自排隊）': '#f97316', 'B（單一排隊）': '#3b82f6'})
        
        fig_ab.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="超過 30 分鐘（忍耐極限）", annotation_font_size=F_ANNOTATION)
        set_chart_layout(fig_ab, "等候時間分佈比較（平均數皆為 15 分鐘）", "排隊方式", "等候時間 (分鐘)")
        fig_ab.update_layout(
            height=360,
            margin=dict(t=55, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_ab, use_container_width=True)

        col_ab1, col_ab2 = st.columns(2)
        with col_ab1:
            st.markdown(f"**方法 A 統計摘要**\n- 標準差 = **{std_A:.1f} 分鐘**\n- 等超過 30 分鐘的機率 ≈ **{pct_A_over30:.1f}%**")
        with col_ab2:
            st.markdown(f"**方法 B 統計摘要**\n- 標準差 = **{std_B:.1f} 分鐘**\n- 等超過 30 分鐘的機率 ≈ **{pct_B_over30:.1f}%**")

        st.markdown(f"""
        <div class="discover-box">
        💡 <b>工程結論</b>：平均等候時間相同，但方法 B 的標準差更小（更穩定）。
        顧客排方法 B「等超過 30 分鐘」的機率從 {pct_A_over30:.1f}% 降到 {pct_B_over30:.1f}%。
        <b>這就是為什麼麥當勞、銀行都改用「單一排隊制」——降低變異才能提升服務品質！</b>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室：分組資料統計量計算器（逐步推導）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>練習在只有次數分配表（沒有原始數據）時，用組中點近似計算平均數與變異數。<br>
                <b>你會發現：</b>填入組中點、平均數、變異數後，系統逐步驗證你的計算過程，讓你確認自己理解「除以 n-1」的意義。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("只有「次數分配表」時，必須用**組中點 mᵢ** 近似代表每組資料，再進行計算。")
        _card("#7c3aed","#f5f3ff","#4c1d95","📐 分組資料公式",
              "X&#772; = &#931;(f&#7522; &times; m&#7522;) / n"
              "&emsp;&emsp;s² = &#931;f&#7522;(m&#7522; &minus; X&#772;)² / (n&minus;1)")

        st.write("📋 **請使用下表資料作練習（課本習題）：**")
        df_ex = pd.DataFrame({'組別': ['10 - 小於 30', '30 - 小於 50', '50 - 小於 70'], '次數 fᵢ': [2, 6, 2], '組中點 mᵢ': ['?', '?', '?'], 'fᵢ × mᵢ': ['?', '?', '?']})
        st.markdown(f'<div class="big-table">{df_ex.to_html(index=False)}</div>', unsafe_allow_html=True)

        if st.button("🔄 復原預設值", key="reset_calc"):
            st.session_state["am1"], st.session_state["amean"], st.session_state["avar"] = 0.0, 0.0, 0.0
            st.rerun()

        c1, c2, c3 = st.columns(3)
        with c1: a_m1 = st.number_input("① 第一組的組中點", value=0.0, step=1.0, key="am1")
        with c2: a_mean = st.number_input("② 近似平均數 X̄", value=0.0, step=1.0, key="amean")
        with c3: a_var = st.number_input("③ 樣本變異數 s²", value=0.0, step=0.1, key="avar")

        if st.button("送出檢核", key="btn_t3"):
            st.markdown("---")
            st.markdown("**📝 逐步解析：**")
            cc = 0
            if a_m1 == 20.0:
                _card("#22c55e","#f0fdf4","#166534","✅ ① 組中點正確 = 20","(10+30)/2 = 20 ✓"); cc += 1
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ ① 組中點錯誤",f"= (組下限 + 組上限) / 2 = (10+30)/2 = 20（你填了 {a_m1}）")

            st.markdown("```\n組中點：m₁=20, m₂=40, m₃=60\nn = 2 + 6 + 2 = 10\nX̄ = (2×20 + 6×40 + 2×60) / 10\n  = (40 + 240 + 120) / 10 = 400 / 10 = 40\n```")

            if a_mean == 40.0:
                _card("#22c55e","#f0fdf4","#166534","✅ ② 近似平均數正確 = 40","Σ(f×m)/n = 400/10 = 40 ✓"); cc += 1
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ ② 近似平均數錯誤",f"= Σ(f×m)/n = 400/10 = 40（你填了 {a_mean}）")

            st.markdown("```\ns² = [2(20-40)² + 6(40-40)² + 2(60-40)²] / (10-1)\n   = [2×400 + 6×0 + 2×400] / 9\n   = [800 + 0 + 800] / 9\n   = 1600 / 9 ≈ 177.8\n注意：除以 n-1 = 9，而非 n = 10！\n```")

            if round(a_var, 1) == 177.8:
                _card("#22c55e","#f0fdf4","#166534","✅ ③ 變異數正確 ≈ 177.8","1600/9 ≈ 177.8 ✓"); cc += 1
            else:
                _card("#ef4444","#fef2f2","#991b1b","❌ ③ 變異數錯誤",f"= 1600/9 ≈ 177.8（你填了 {a_var}）。記得除以 n-1！")

            if cc == 3:
                st.balloons(); _card("#7c3aed","#f5f3ff","#4c1d95","🎊 三題全對！","你已掌握分組資料的統計量計算。")

    with st.expander("🛠️ 展開實驗室：偏態係數視覺化（SK 的直覺理解）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用視覺化理解 SK 公式的含義：平均數與中位數的相對位置如何決定分佈的偏斜方向。<br>
                <b>你會發現：</b>切換三種偏態類型後，觀察直方圖的「尾巴方向」與紅/藍垂直線的相對位置——SK 符號的正負就來自這個差距。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("**SK = 3(X̄ - m) / s**：這個公式在說什麼？讓圖形告訴你。")

        if st.button("🔄 復原預設值", key="reset_skew_btn"):
            st.session_state["skew_sel"] = "正偏態（右偏）"
            st.rerun()

        skew_type = st.selectbox("選擇偏態類型", ["正偏態（右偏）", "對稱（常態）", "負偏態（左偏）"], key="skew_sel")

        np.random.seed(7)
        if "正偏態" in skew_type:
            sk_data, sk_color = np.concatenate([np.random.normal(30, 5, 180), np.random.exponential(15, 60) + 30]), "#f97316"
        elif "負偏態" in skew_type:
            sk_data, sk_color = np.concatenate([np.random.normal(70, 5, 180), -np.random.exponential(15, 60) + 70]), "#a855f7"
        else:
            sk_data, sk_color = np.random.normal(50, 10, 240), "#3b82f6"

        sk_mean, sk_median = np.mean(sk_data), np.median(sk_data)
        sk_std = np.std(sk_data, ddof=1)
        sk_val = 3 * (sk_mean - sk_median) / sk_std

        fig_sk = px.histogram(x=sk_data, nbins=35, color_discrete_sequence=[sk_color])
        
        # ✨ 防重疊：平均數在上，中位數在下 ✨
        pos_mean_sk = "top right" if sk_mean >= sk_median else "top left"
        pos_med_sk = "bottom left" if sk_mean >= sk_median else "bottom right"

        fig_sk.add_vline(x=sk_mean, line_color="red", line_width=2.5, annotation_text=f"X̄={sk_mean:.1f}", annotation_position=pos_mean_sk, annotation_font_size=F_ANNOTATION)
        fig_sk.add_vline(x=sk_median, line_color="blue", line_width=2.5, annotation_text=f"m={sk_median:.1f}", annotation_position=pos_med_sk, annotation_font_size=F_ANNOTATION)
        
        set_chart_layout(fig_sk, f"偏態係數 SK = {sk_val:.3f}", "數值", "次數")
        st.plotly_chart(fig_sk, use_container_width=True)

        if sk_val > 0.1:
            _card("#3b82f6","#eff6ff","#1e40af",f"📊 正偏態（右偏）SK={sk_val:.2f}",f"平均數({sk_mean:.1f})被右側大値拉高，超過中位數({sk_median:.1f})。直方圖右尾較長。")
        elif sk_val < -0.1:
            _card("#6366f1","#eef2ff","#3730a3",f"📊 負偏態（左偏）SK={sk_val:.2f}",f"平均數({sk_mean:.1f})被左側小値拉低，低於中位數({sk_median:.1f})。直方圖左尾較長。")
        else:
            _card("#22c55e","#f0fdf4","#166534",f"📊 接近對稱 SK={sk_val:.2f}",f"平均數({sk_mean:.1f})與中位數({sk_median:.1f})幾乎相同。")


# ═══════════════════════════════════════════════════════════════════
# TAB 4：比例
# ═══════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⚖️ 2.4 比例 (Proportion)")

    _card("#0f766e","#f0fdfa","#134e4a","📌 核心概念",
          "比例 (Proportion) 用於衡量「屬性資料」，即某個特性在樣本中出現的相對頻率。<br>"
          "• <b>母體比例 &#960; (pi)</b>：真實的母體不良率（通常未知）<br>"
          "• <b>樣本比例 P</b>：用來估計 &#960; 的樣本統計量")

    _card("#7c3aed","#f5f3ff","#4c1d95","📐 比例公式",
          "P = 屬於某類別之觀測數目 / 樣本大小")

    st.markdown("""
    <div class="why-box">
    <b>🔧 為什麼比例在工程中至關重要？</b><br>
    • <b>品質管制</b>：每批晶片的不良比例 P 決定是否出貨或退貨<br>
    • <b>製程警示</b>：若 P 持續超過規格值 π₀，需立即停機校正<br>
    • <b>可靠度評估</b>：造紙機「失常比例 0.311 + 無法操作比例 0.111 = 0.422」→ 近一半時間機器出問題，維修成本高昂！
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 課本例題 2.4 重現：造紙機維修決策分析", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">📖 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>用比例數字讀懂課本例題的工程含義：失常比例有多高，才需要改變維修政策？<br>
                <b>你會發現：</b>圓餅圖把三種設備狀態的比例視覺化後，「失常＋無法操作 ≈ 42%」這個數字立刻變得很有衝擊力。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("**某造紙廠抽樣 135 次的設備狀態紀錄如下：**")
        df_paper = pd.DataFrame({
            '設備狀態': ['正常運作', '失常（需調整）', '無法操作（需修復）'],
            '出現次數': [78, 42, 15],
            '比例 P': [78/135, 42/135, 15/135],
            '百分比': [f"{78/135*100:.1f}%", f"{42/135*100:.1f}%", f"{15/135*100:.1f}%"]
        })
        
        df_paper_str = df_paper.copy()
        df_paper_str['比例 P'] = df_paper_str['比例 P'].map(lambda x: f"{x:.3f}")
        st.markdown(f'<div class="big-table">{df_paper_str.to_html(index=False)}</div>', unsafe_allow_html=True)

        fig_paper = go.Figure(data=[go.Pie(labels=df_paper['設備狀態'], values=df_paper['出現次數'], hole=0.4, marker_colors=['#22c55e', '#f97316', '#ef4444'])])
        set_chart_layout(fig_paper, "造紙機設備狀態分佈")
        fig_paper.update_layout(
            annotations=[dict(text='135<br>次抽樣', x=0.5, y=0.5, font_size=F_TITLE, showarrow=False)],
            height=340,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_paper, use_container_width=True)

        st.markdown("""
        <div class="discover-box">
        💡 <b>工程師的決策</b>：失常 + 無法操作 = 42.2%，接近「一半時間機器都有問題」！
        這個比例數字直接指向：現有維修政策需要根本性改變（例如：增加預防性保養頻率）。
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🛠️ 展開實驗室：製程偏移與不良比例模擬器（品管決策練習）", expanded=False):
        st.markdown('''
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #0369a1;
                    border-radius:8px;padding:10px 16px;margin:0 0 14px 0;">
            <div style="color:#0369a1;font-size:0.85rem;font-weight:700;letter-spacing:0.05em;
                        text-transform:uppercase;margin-bottom:5px;">🎯 本實驗室教學目的</div>
            <div style="color:#334155;font-size:1.0rem;line-height:1.7;">
                <b>學習目標：</b>體驗製程平均值偏移時，不良比例 P 如何非線性地快速上升，強化「製程穩定」的工程直覺。<br>
                <b>你會發現：</b>拖動平均溫度滑桿，當 μ 接近規格上限 100°C 時，不良率會突然暴增——這就是為何品管不只看平均值，更要監控標準差。
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("""
        **場景**：晶片製程中，溫度超過 **100°C** 就視為不良品。
        當機台平均操作溫度偏移時，不良比例 P 如何變化？
        """)

        if st.button("🔄 復原預設值", key="reset_proc"):
            st.session_state["proc_mean"] = 88.0
            st.session_state["proc_std"] = 5.0
            st.rerun()

        col_proc1, col_proc2 = st.columns(2)
        with col_proc1: mean_t = st.slider("機台平均操作溫度 μ (°C)", 80.0, 105.0, 88.0, step=0.5, key="proc_mean")
        with col_proc2: std_t = st.slider("製程標準差 σ (°C)", 1.0, 10.0, 5.0, step=0.5, key="proc_std")

        np.random.seed(4)
        temps = np.random.normal(mean_t, std_t, 500)
        defects = sum(temps > 100)
        p_defect = defects / 500.0
        spec_limit = 0.02

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("不良比例 P", f"{p_defect:.4f}", delta=f"{p_defect-0.001:.4f} vs 理想值")
        col_r2.metric("不良數量", f"{defects} / 500 件")
        col_r3.metric("規格上限", f"{spec_limit:.2f} (2%)")

        fig_proc = px.histogram(x=temps, nbins=40, color_discrete_sequence=["#fbbf24"])
        if [t for t in temps if t > 100]:
            fig_proc.add_vrect(x0=100, x1=max(temps)+5, fillcolor="rgba(239,68,68,0.15)", line_width=0, annotation_text="不良區域", annotation_position="top right", annotation_font_size=F_ANNOTATION)
        fig_proc.add_vline(x=100, line_color="red", line_dash="dash", line_width=2.5, annotation_text="規格上限 100°C", annotation_position="top left", annotation_font_size=F_ANNOTATION)
        fig_proc.add_vline(x=mean_t, line_color="#3b82f6", line_width=2, annotation_text=f"μ={mean_t}°C", annotation_position="top left", annotation_font_size=F_ANNOTATION)
        
        set_chart_layout(fig_proc, f"晶片溫度分佈 ── 不良比例 P = {p_defect:.4f} ({p_defect*100:.2f}%)", "操作溫度 (°C)", "次數")
        fig_proc.update_layout(
            height=360,
            margin=dict(t=60, b=40, l=50, r=20)
        )
        st.plotly_chart(fig_proc, use_container_width=True)

        if p_defect > spec_limit:
            _card("#ef4444","#fef2f2","#991b1b",f"🚨 超標警告！必須立即停機校正",f"不良比例 P = {p_defect:.4f} > 規格上限 0.02")
        elif p_defect > spec_limit * 0.5:
            _card("#f59e0b","#fffbeb","#92400e","⚠️ 接近上限，請加強監控",f"不良比例 P = {p_defect:.4f}，已達規格上限的 {p_defect/spec_limit*100:.0f}%，請密切監控。")
        else:
            _card("#22c55e","#f0fdf4","#166534","✅ 製程正常",f"不良比例 P = {p_defect:.4f}，遠低於規格上限 0.02。")

    st.markdown("---")
    _card("#d97706","#fffbeb","#92400e","💡 2.4 隨堂小測驗","請根據比例的概念作答：")
    q_tab4 = st.radio(
        "📍 **在 37 個生產的矽晶片中發現 3 個毀壞。樣本毀壞比例 P 約為何？**",
        ["請選擇...", "A. 0.08（3/37 ≈ 0.081）", "B. 0.12（3/25 = 0.12）"],
        key="q_tab4"
    )
    if st.button("送出答案", key="btn_t4"):
        if q_tab4 == "A. 0.08（3/37 ≈ 0.081）":
            _card("#22c55e","#f0fdf4","#166534","🎉 正確！","P = 3 ÷ 37 = 0.0811 ≈ 0.08。分母是「總樣本數 37」，不是其他數字。")
        elif q_tab4 != "請選擇...":
            _card("#ef4444","#fef2f2","#991b1b","❌ 提示","P = 不良品數 / 樣本大小 = 3 / 37。請確認分母是「全部抽驗的數量」。")


# =====================================================================
# 整合性總測驗
# =====================================================================
st.divider()
st.markdown(
    '<div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);'
    'border-radius:10px;padding:12px 24px;margin:8px 0 6px 0;">'
    '<span style="color:#fff;font-size:1.3rem;font-weight:800;">📝 2. 本週整合性總測驗</span></div>',
    unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin:0 0 16px 4px;">完成所有理論閱讀後，輸入老師公布的解鎖密碼開始作答</p>', unsafe_allow_html=True)

real_password = get_weekly_password("Week 02")
if not real_password: real_password = "ADMIN" 

_card("#475569","#f8fafc","#334155","🔒 測驗鎖定中","請輸入老師於課堂上公布的 6 位數解鎖密碼，即可開始作答。")
_col_pw, _col_btn = st.columns([5, 1])
with _col_pw:
    user_code = st.text_input("密碼", type="password", key="w2_unlock_code",
                              label_visibility="collapsed",
                              placeholder="🔑 請輸入 6 位數解鎖密碼…")
with _col_btn:
    st.button("🔓 解鎖", use_container_width=True, key="w2_unlock_btn")

if user_code != real_password:
    if user_code != "": _card("#ef4444","#fef2f2","#991b1b","❌ 密碼錯誤","請確認您輸入的字母與數字是否正確！")
else:
    _card("#22c55e","#f0fdf4","#166534","🔓 密碼正確！測驗已解鎖","請完成以下題目後送出。")
    st.markdown("""
    <div class="concept-box">
    <b>📋 測驗說明</b>：以下 4 題涵蓋本週四個核心節次，每題 25 分，共 100 分。
    作答送出後成績即時鎖定，請確認後再送出。
    </div>
    """, unsafe_allow_html=True)

    if "w2_locked" not in st.session_state: st.session_state.w2_locked = False

    with st.form("week2_unified_quiz"):
        c_id, c_name, c_code = st.columns(3)
        with c_id: st_id = st.text_input("📝 學號")
        with c_name: st_name = st.text_input("📝 姓名")
        with c_code: st_vcode = st.text_input("🔑 驗證碼", type="password")
        st.markdown("---")

        q1 = st.radio(
            "**Q1 (2.1節)：將原始資料整理分類後，最常使用哪一種圖表直觀顯示數值資料的分配形狀與次數？**",
            ["名目圖 (Bar Chart)", "直方圖 (Histogram)", "散佈圖 (Scatter Plot)", "管制圖 (Control Chart)"]
        )
        st.caption("💭 提示：這種圖的每個矩形代表一個「組距」，矩形面積代表次數，且矩形之間相連無空隙。")

        q2 = st.radio(
            "**Q2 (2.2節)：當工程資料中存在極端的「異常值」時，哪一種位置測度最不容易受到影響？**",
            ["算術平均數 (Mean)", "變異數 (Variance)", "中位數 (Median)", "全距 (Range)"]
        )
        st.caption("💭 提示：想想在「拉力戰實驗室」中，哪條線幾乎沒有移動？")

        q3 = st.radio(
            "**Q3 (2.3節)：在只有次數分配表（無原始數據）的情況下，進行近似計算時必須使用？**",
            ["組下限 (Lower Boundary)", "組上限 (Upper Boundary)", "組中點 mᵢ (Midpoint)", "累積次數 (Cumulative Frequency)"]
        )
        st.caption("💭 提示：在課本例題計算練習中，你用哪個數值代表每一組的所有資料？")

        q4 = st.radio(
            "**Q4 (2.3節)：若平均數被極端大值拉抬至高於中位數，根據偏態係數 SK = 3(X̄ - m) / s，此分配呈現？**",
            ["無偏態（SK ≈ 0，對稱分佈）", "正偏態（SK > 0，右偏）", "負偏態（SK < 0，左偏）", "雙峰偏態（SK 無法判斷）"]
        )
        st.caption("💭 提示：X̄ > m → (X̄ - m) > 0 → SK > 0 → 尾巴在哪一側？")

        st.markdown("---")
        if st.form_submit_button("✅ 簽署並送出本週測驗", disabled=st.session_state.w2_locked, type="primary"):
            if st_id and st_name and st_vcode:
                with st.spinner("評分中..."):
                    is_valid, s_idx = verify_student(st_id, st_name, st_vcode)
                    if not is_valid:
                        _card("#ef4444","#fef2f2","#991b1b","⛔ 身分驗證失敗","您輸入的學號、姓名或驗證碼有誤，請重新確認！（為保護成績安全，不予顯示作答結果）")
                    elif check_has_submitted(st_id, "Week 02"):
                        _card("#ef4444","#fef2f2","#991b1b","⛔ 拒絕送出","系統查詢到您已繳交過 Week 02 的測驗！請勿重複作答。")
                    else:
                        correct_ans = ["直方圖 (Histogram)", "中位數 (Median)", "組中點 mᵢ (Midpoint)", "正偏態（SK > 0，右偏）"]
                        student_ans = [q1, q2, q3, q4]
                        score = sum(25 for a, c in zip(student_ans, correct_ans) if a == c)
                        ans_str = f"Q1:{q1[:4]}, Q2:{q2[:4]}, Q3:{q3[:4]}, Q4:{q4[:4]}"

                        if save_score(s_idx, st_id, st_name, "Week 02", ans_str, score):
                            st.session_state.w2_locked = True
                            st.markdown(
    f'<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin:8px 0;">'  
    f'<div style="background:#22c55e;padding:9px 18px;"><span style="color:white;font-weight:700;">🎊 上傳成功！</span></div>'  
    f'<div style="background:#f0fdf4;padding:14px 18px;color:#166534;font-size:1.0rem;line-height:1.65;">'  
    f'<b>{st_name}</b>（{st_id}）驗證通過<br>'  
    f'<span style="font-size:2rem;font-weight:900;color:#15803d;">{score}</span>'  
    f' 分　成績已鎖定寫入資料庫！</div></div>',
    unsafe_allow_html=True)
                            if score == 100:
                                st.balloons()
                                _card("#7c3aed","#f5f3ff","#4c1d95","🏆 湿分 100！","四個核心概念全數掌握，Week 02 完美制霸！")
                            elif score >= 75:
                                _card("#3b82f6","#eff6ff","#1e40af","👍 表現不錯！","建議回頭看看答錯的題目，對應節次的「互動實驗室」有詳細解說，複習一遇會更紾實喉！")
                            else:
                                _card("#f59e0b","#fffbeb","#92400e","📖 繼續加油！","請回顧本週各節的「概念說明」與「互動實驗室」，特別是不確定的題目——理解比死背更重要！")
            else:
                _card("#f59e0b","#fffbeb","#92400e","⚠️ 資料不完整","請完整填寫學號、姓名與驗證碼。")

    if st.session_state.w2_locked:
        _card("#475569","#f8fafc","#334155","🔒 測驗已鎖定","系統已安全登錄您的成績，如有疑問請聯繫授課教師。")

# =====================================================================
# 頁面底部：本週學習摘要
# =====================================================================
st.divider()
with st.expander("📚 本週核心公式速查卡（考前複習用）", expanded=False):
    _qcards = [
        ("#3b82f6","#eff6ff","#1e40af","2.1 次數分配",["\u5efa議組數 ≈ √n","\u7d44距 = (最大値 − 最小値) / 組數","Ogive：各組上限 vs 累積次數（或累積 %）"]),
        ("#6366f1","#eef2ff","#3730a3","2.2 位置的測度",["平均數：X̅ = Σxᵢ / n","中位數 m：排序後正中間的値","分組平均：X̅ = Σ(fᵢ × mᵢ) / n","百分位數 Pₖ：有 k% 資料小於等於此値"]),
        ("#22c55e","#f0fdf4","#166534","2.3 差異性的量度",["樣本變異數：s² = Σ(xᵢ − X̅)² / (n−1)","樣本標準差：s = √s²","分組變異數：s² = Σfᵢ(mᵢ − X̅)² / (n−1)","偏態係數：SK = 3(X̅ − m) / s","SK > 0 → 右偏；SK < 0 → 左偏"]),
        ("#f59e0b","#fffbeb","#92400e","2.4 比例",["P = 某類別觀測個數 / 總觀測個數","0 ≤ P ≤ 1","工程應用：不良率、合格率、達標比例"]),
    ]
    _qcols = st.columns(2)
    for _qi, (_qhc, _qbc, _qtc, _qtitle, _qitems) in enumerate(_qcards):
        with _qcols[_qi % 2]:
            _qihtml = "".join(f'<li style="margin:4px 0;color:{_qtc};font-size:0.92rem;">{it}</li>' for it in _qitems)
            st.markdown(
                f'<div style="border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #e2e8f0;margin-bottom:14px;">'  
                f'<div style="background:{_qhc};padding:9px 16px;"><span style="color:white;font-weight:800;font-size:0.92rem;">{_qtitle}</span></div>'  
                f'<div style="background:{_qbc};padding:11px 16px;"><ul style="margin:0;padding-left:16px;">{_qihtml}</ul></div></div>',
                unsafe_allow_html=True)