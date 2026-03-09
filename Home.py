# 檔案位置： D:\Engineering_Statistics_App\Home.py
import streamlit as st
from utils.style import apply_theme

# 1. 基本設定 (必須在第一行)
st.set_page_config(page_title="工程統計：數據驅動的風險導航", layout="wide")

# 2. 載入統一視覺樣式
apply_theme()

# ── 額外注入 Home 專屬動畫與樣式 ─────────────────────────────
st.markdown("""
<style>
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(1.2); }
}
.home-fade   { animation: fadeInUp 0.55s 0.00s ease both; }
.home-fade-1 { animation: fadeInUp 0.55s 0.08s ease both; }
.home-fade-2 { animation: fadeInUp 0.55s 0.16s ease both; }
.home-fade-3 { animation: fadeInUp 0.55s 0.24s ease both; }
.home-fade-4 { animation: fadeInUp 0.55s 0.32s ease both; }
.home-fade-5 { animation: fadeInUp 0.55s 0.40s ease both; }

.week-card {
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    padding: 20px 22px;
    background: #ffffff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    height: 100%;
}
.week-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(37,99,235,0.12);
    border-color: #93c5fd;
}
.pulse-dot {
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse-dot 1.8s ease-in-out infinite;
    vertical-align: middle;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 登入
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.markdown("""
        <div class="home-fade" style="
            max-width: 360px; margin: 48px auto 0 auto;
            background: linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
            border-radius: 16px; padding: 30px 36px 28px 36px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.22);
            text-align: center; position: relative; overflow: hidden;
        ">
            <div style="font-size:36px;margin-bottom:12px;line-height:1;">🛡️</div>
            <div style="color:#f1f5f9;font-size:20px;font-weight:900;margin:0 0 6px 0;line-height:1.25;">
                工程統計 — 課程登入
            </div>
            <div style="color:#93c5fd;font-size:11px;font-weight:700;
                        letter-spacing:0.15em;margin:0 0 3px 0;text-transform:uppercase;">
                National Chiayi University
            </div>
            <div style="color:#475569;font-size:12px;margin:0 0 18px 0;">
                土木與水資源工程學系 · Engineering Statistics
            </div>
            <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
                        border-radius:8px;padding:9px 14px;
                        color:#94a3b8;font-size:12px;line-height:1.6;">
                🔐 請輸入本學期課程密碼以進入互動平台
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        _, col_center, _ = st.columns([1.4, 1.2, 1.4])
        with col_center:
            pwd = st.text_input("課程密碼", type="password",
                                label_visibility="collapsed", placeholder="🔑 請輸入密碼…")
            login_btn = st.button("🚀 進入課程", use_container_width=True, type="primary")
            if login_btn:
                if pwd == "ncyu_stat2026":
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.markdown("""
                    <div style="background:#fef2f2;border:1px solid #fecaca;
                        border-left:4px solid #ef4444;border-radius:10px;
                        padding:11px 16px;color:#991b1b;font-size:0.93rem;margin-top:8px;">
                        ❌ 密碼錯誤，請洽教授或助教取得本學期密碼。
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('<p style="color:#64748b;font-size:13px;text-align:center;margin-top:14px;">'
                    '本平台僅供修課學生使用 · 如遇問題請聯繫授課教師</p>',
                    unsafe_allow_html=True)
        return False
    return True


# ==========================================
# 主頁面
# ==========================================
if check_password():

    # ── Hero ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="home-fade" style="
        background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
        border-radius:18px; padding:44px 52px 40px 52px;
        margin-bottom:20px; box-shadow:0 4px 28px rgba(0,0,0,0.18);
        position:relative; overflow:hidden;
    ">
        <div style="position:absolute;top:-80px;right:-80px;width:320px;height:320px;
            border-radius:50%;background:radial-gradient(circle,rgba(59,130,246,0.12) 0%,transparent 65%);
            pointer-events:none;"></div>
        <div style="position:absolute;bottom:-40px;left:35%;width:200px;height:200px;
            border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,0.10) 0%,transparent 70%);
            pointer-events:none;"></div>
        <div style="color:#93c5fd;font-size:11.5px;letter-spacing:0.22em;
                    font-weight:700;margin:0 0 14px 0;text-transform:uppercase;">
            National Chiayi University &nbsp;·&nbsp; Civil &amp; Water Resources Engineering
        </div>
        <div style="color:#f1f5f9;font-size:2.3rem;font-weight:900;
                    margin:0 0 6px 0;line-height:1.2;">
            工程統計：數據驅動的風險導航 📐
        </div>
        <div style="color:#94a3b8;font-size:1.02rem;margin:0 0 26px 0;">
            Engineering Statistics — Data-Driven Risk Navigation
        </div>
        <div style="background:rgba(255,255,255,0.07);border-left:4px solid #3b82f6;
                    border-radius:8px;padding:15px 20px;
                    color:#cbd5e1;font-size:1.05rem;font-style:italic;
                    line-height:1.75;max-width:680px;">
            這不是一門只教你「怎麼算」的課，而是一門要讓你思考：<br>
            <span style="color:#60a5fa;font-weight:700;">
                在資料有限、不確定存在的工程世界中，你敢不敢做判斷？
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 資訊三欄 ────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([5, 5, 4])

    with col_a:
        st.markdown("""
        <div class="home-fade-1" style="
            background:#eff6ff;border:1px solid #bfdbfe;
            border-left:5px solid #3b82f6;border-radius:14px;
            padding:22px 26px;
        ">
            <div style="color:#1d4ed8;font-size:1.1rem;font-weight:800;margin:0 0 13px 0;">
                👨‍🏫 班級資訊
            </div>
            <div style="color:#1e40af;font-size:0.97rem;font-weight:700;margin:0 0 10px 0;">
                🏫 土木與水資源工程學系
            </div>
            <div style="color:#334155;font-size:0.92rem;line-height:1.8;">
                📖 <strong>教材</strong><br>
                <span style="padding-left:1.2em;display:block;">
                    <em>Modern Engineering Statistics</em><br>
                    Lawrence L. Lapin 著<br>
                    潘南飛、溫志中 編譯
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        # ✅ 修正：四個正確階段（依教學大綱）
        st.markdown("""
        <div class="home-fade-2" style="
            background:#f0fdf4;border:1px solid #bbf7d0;
            border-left:5px solid #22c55e;border-radius:14px;
            padding:22px 26px;
        ">
            <div style="color:#15803d;font-size:1.1rem;font-weight:800;margin:0 0 10px 0;">
                🗺️ 課程階段
            </div>
            <div style="margin:0 0 12px 0;">
                <span style="background:#dcfce7;color:#166534;font-size:0.75rem;
                    font-weight:700;padding:2px 10px;border-radius:20px;letter-spacing:0.05em;">
                    ▶ 進行中
                </span>
            </div>
            <div style="color:#166534;font-size:0.88rem;line-height:1.9;">
                📊 <strong>第一階段</strong>：數據描述與機率風險<br>
                <span style="color:#16a34a;font-size:0.80rem;padding-left:1.4em;">W1 – W5</span><br>
                🔬 <strong>第二階段</strong>：抽樣推論與工程設計值<br>
                <span style="color:#16a34a;font-size:0.80rem;padding-left:1.4em;">W6 – W7</span><br>
                ⚖️ <strong>第三階段</strong>：統計檢定與工法比較<br>
                <span style="color:#16a34a;font-size:0.80rem;padding-left:1.4em;">W9 – W11</span><br>
                📐 <strong>第四階段</strong>：模型預測・DOE・品質放行<br>
                <span style="color:#86efac;font-size:0.80rem;padding-left:1.4em;">W12 – W15</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown("""
        <div class="home-fade-3" style="
            background:linear-gradient(135deg,#1e3a5f 0%,#0f2440 100%);
            border:1px solid #1e3a5f;border-radius:14px;padding:22px 26px;
        ">
            <div style="color:#93c5fd;font-size:1.1rem;font-weight:800;margin:0 0 14px 0;">
                📡 學習狀態
            </div>
            <div style="margin:0 0 16px 0;">
                <span class="pulse-dot"></span>
                <span style="color:#f1f5f9;font-size:0.92rem;font-weight:600;">平台運作中</span>
            </div>
            <div style="color:#475569;font-size:0.78rem;text-transform:uppercase;
                        letter-spacing:0.1em;margin:0 0 6px 0;">本學期進度</div>
            <div style="background:rgba(255,255,255,0.08);border-radius:6px;
                        height:7px;margin:0 0 6px 0;overflow:hidden;">
                <div style="background:linear-gradient(90deg,#3b82f6,#60a5fa);
                            width:13%;height:100%;border-radius:6px;"></div>
            </div>
            <div style="color:#64748b;font-size:0.8rem;margin:0 0 14px 0;">Week 2 / 16 完成</div>
            <div style="color:#64748b;font-size:0.8rem;line-height:1.6;">
                👈 請從左側選單<br>選擇本週週次開始
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # ── 週次一覽 header ─────────────────────────────────────────────
    st.markdown("""
    <div class="home-fade-4">
        <div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
            border-radius:10px;padding:12px 24px;margin:0 0 6px 0;">
            <span style="color:#fff;font-size:1.3rem;font-weight:800;">📚 課程週次一覽</span>
        </div>
        <p style="color:#94a3b8;font-size:0.88rem;margin:0 0 14px 4px;">
            點擊左側導覽列進入對應週次的互動學習內容
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Week 卡片 Row 1（W01–W04）────────────────────────────────────
    # ✅ 修正：章節描述依教學大綱；Week03 改 #0369a1（禁用 #6366f1）
    weeks_r1 = [
        ("01", "統計在工程決策中的角色",
         "§1.1–1.6｜資料型態、母體與樣本、統計工程應用",
         "#3b82f6", "#eff6ff", "#1e40af", "✅ 已開放"),
        ("02", "統計資料之描述與探討",
         "§2.1–2.4｜次數分配、位置測度、差異性量度、比例",
         "#22c55e", "#f0fdf4", "#166534", "✅ 已開放"),
        ("03", "機率與系統可靠度",
         "§3.1–3.5｜條件機率、串並聯系統失效風險",
         "#0369a1", "#e0f2fe", "#0c4a6e", "🔒 即將開放"),
        ("04", "離散機率分配",
         "§4.1–4.3｜二項分配、品管抽驗合格率",
         "#f59e0b", "#fffbeb", "#92400e", "🔒 即將開放"),
    ]
    cols_r1 = st.columns(4)
    for col, (wk, title, desc, hc, bc, tc, status) in zip(cols_r1, weeks_r1):
        locked = "🔒" in status
        op = "0.52" if locked else "1"
        with col:
            st.markdown(f"""
            <div class="week-card home-fade-4" style="opacity:{op};">
                <div style="background:{hc};color:white;font-size:0.74rem;font-weight:800;
                    padding:2px 10px;border-radius:20px;display:inline-block;
                    margin:0 0 10px 0;letter-spacing:0.06em;">WEEK {wk}</div>
                <div style="color:#0f172a;font-size:0.96rem;font-weight:800;
                    line-height:1.3;margin:0 0 7px 0;">{title}</div>
                <div style="color:#64748b;font-size:0.80rem;line-height:1.55;
                    margin:0 0 12px 0;">{desc}</div>
                <div style="background:{bc};color:{tc};font-size:0.75rem;font-weight:700;
                    padding:3px 10px;border-radius:6px;display:inline-block;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # ── Week 卡片 Row 2（W05–W08）────────────────────────────────────
    # ✅ 修正：章節描述依教學大綱；Week08 為期中考試
    weeks_r2 = [
        ("05", "連續機率分配與壽命工程",
         "§5.1–5.6｜常態分配、Weibull 分配、浴缸型故障率",
         "#ec4899", "#fdf2f8", "#9d174d", "🔒 即將開放"),
        ("06", "抽樣分配與中央極限定理",
         "§6.1–6.6｜CLT、樣本均值分配、t 分配",
         "#14b8a6", "#f0fdfa", "#134e4a", "🔒 即將開放"),
        ("07", "點估計與信賴區間",
         "§7.1–7.6｜信賴區間、Student-t、樣本大小",
         "#8b5cf6", "#f5f3ff", "#4c1d95", "🔒 即將開放"),
        ("08", "期中考試",
         "第 1–7 週核心概念整合評量",
         "#ef4444", "#fef2f2", "#991b1b", "🗓️ 期中考試"),
    ]
    cols_r2 = st.columns(4)
    for col, (wk, title, desc, hc, bc, tc, status) in zip(cols_r2, weeks_r2):
        with col:
            st.markdown(f"""
            <div class="week-card home-fade-5" style="opacity:0.52;">
                <div style="background:{hc};color:white;font-size:0.74rem;font-weight:800;
                    padding:2px 10px;border-radius:20px;display:inline-block;
                    margin:0 0 10px 0;letter-spacing:0.06em;">WEEK {wk}</div>
                <div style="color:#0f172a;font-size:0.96rem;font-weight:800;
                    line-height:1.3;margin:0 0 7px 0;">{title}</div>
                <div style="color:#64748b;font-size:0.80rem;line-height:1.55;
                    margin:0 0 12px 0;">{desc}</div>
                <div style="background:{bc};color:{tc};font-size:0.75rem;font-weight:700;
                    padding:3px 10px;border-radius:6px;display:inline-block;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # ── Week 卡片 Row 3（W09–W12）────────────────────────────────────
    # ✅ 新增：W09–W11 第三階段（原版缺少）
    weeks_r3 = [
        ("09", "統計假設檢定程序",
         "§8.1–8.2｜H₀、型 I / II 誤差、生產者與消費者風險",
         "#7c3aed", "#f5f3ff", "#4c1d95", "🔒 即將開放"),
        ("10", "母體比例與兩母體比較",
         "§8.3–8.4｜單尾／雙尾檢定、兩工法方案比較",
         "#7c3aed", "#f5f3ff", "#4c1d95", "🔒 即將開放"),
        ("11", "變異數分析 (ANOVA)",
         "§9.1–9.6｜單因子、雙因子 ANOVA、隨機集區",
         "#d97706", "#fffbeb", "#92400e", "🔒 即將開放"),
        ("12", "迴歸分析（前半）",
         "§10.1–10.9｜線性迴歸、判定係數、共線性陷阱",
         "#0f766e", "#f0fdfa", "#134e4a", "🔒 即將開放"),
    ]
    cols_r3 = st.columns(4)
    for col, (wk, title, desc, hc, bc, tc, status) in zip(cols_r3, weeks_r3):
        with col:
            st.markdown(f"""
            <div class="week-card home-fade-5" style="opacity:0.52;">
                <div style="background:{hc};color:white;font-size:0.74rem;font-weight:800;
                    padding:2px 10px;border-radius:20px;display:inline-block;
                    margin:0 0 10px 0;letter-spacing:0.06em;">WEEK {wk}</div>
                <div style="color:#0f172a;font-size:0.96rem;font-weight:800;
                    line-height:1.3;margin:0 0 7px 0;">{title}</div>
                <div style="color:#64748b;font-size:0.80rem;line-height:1.55;
                    margin:0 0 12px 0;">{desc}</div>
                <div style="background:{bc};color:{tc};font-size:0.75rem;font-weight:700;
                    padding:3px 10px;border-radius:6px;display:inline-block;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # ── Week 卡片 Row 4（W13–W16）────────────────────────────────────
    # ✅ 新增：W13–W16 第四階段 + 期末考試（原版缺少）
    weeks_r4 = [
        ("13", "迴歸分析與多維數據決策（後半）",
         "§10.1–10.9｜多維決策、7 天強度預測拆模案例",
         "#0f766e", "#f0fdfa", "#134e4a", "🔒 即將開放"),
        ("14", "實驗設計 (DOE)",
         "§11.1–11.3｜因子設計、交互作用、田口方法",
         "#3b82f6", "#eff6ff", "#1e40af", "🔒 即將開放"),
        ("15", "製程能力與產品放行決策",
         "§12.1–12.4｜Cpk、管制圖、抽樣驗收",
         "#3b82f6", "#eff6ff", "#1e40af", "🔒 即將開放"),
        ("16", "期末考試",
         "全學期核心概念整合評量",
         "#ef4444", "#fef2f2", "#991b1b", "🗓️ 期末考試"),
    ]
    cols_r4 = st.columns(4)
    for col, (wk, title, desc, hc, bc, tc, status) in zip(cols_r4, weeks_r4):
        with col:
            st.markdown(f"""
            <div class="week-card home-fade-5" style="opacity:0.52;">
                <div style="background:{hc};color:white;font-size:0.74rem;font-weight:800;
                    padding:2px 10px;border-radius:20px;display:inline-block;
                    margin:0 0 10px 0;letter-spacing:0.06em;">WEEK {wk}</div>
                <div style="color:#0f172a;font-size:0.96rem;font-weight:800;
                    line-height:1.3;margin:0 0 7px 0;">{title}</div>
                <div style="color:#64748b;font-size:0.80rem;line-height:1.55;
                    margin:0 0 12px 0;">{desc}</div>
                <div style="background:{bc};color:{tc};font-size:0.75rem;font-weight:700;
                    padding:3px 10px;border-radius:6px;display:inline-block;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # ── 重要提醒 ────────────────────────────────────────────────────
    st.markdown("""
    <div class="home-fade-5" style="
        background:#fffbeb;border:1px solid #fde68a;
        border-left:5px solid #f59e0b;border-radius:14px;
        padding:22px 30px;margin-bottom:4px;
    ">
        <div style="color:#92400e;font-size:1.05rem;font-weight:800;margin:0 0 10px 0;">
            ⚠️ 重要提醒
        </div>
        <div style="color:#78350f;font-size:0.95rem;line-height:1.85;">
            工程統計 <strong>不是保證你一定是對的工具</strong>，而是讓你
            <strong>知道自己可能錯在哪裡、錯多大</strong>。<br>
            學會與不確定性共處，正是工程專業判斷力的核心。<br>
            <span style="color:#b45309;font-size:0.87rem;">
                ☑ 每週測驗僅能作答一次，成績送出後即鎖定，請確認後再送出。
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

    # ── 課程地圖：週次與課本章節對照表 ─────────────────────────────
    # ✅ 新增區塊（依教學大綱，16 週完整對照）
    st.markdown('''
    <div style="background:linear-gradient(90deg,#2563eb 0%,#3b82f6 100%);
        border-radius:10px;padding:10px 24px;margin:0 0 6px 0;">
        <span style="color:#ffffff;font-size:1.1rem;font-weight:800;">
            🗓️ 課程地圖：週次與課本章節對照表
        </span>
    </div>
    <p style="color:#94a3b8;font-size:0.85rem;margin:0 0 10px 4px;">
        本課程依據《工程統計》Lapin 著，共分四個學習階段，請依序完成各週互動實驗與測驗。
    </p>
    ''', unsafe_allow_html=True)

    _phase_colors = {
        "第一階段": "#0369a1",
        "第二階段": "#0f766e",
        "第三階段": "#7c3aed",
        "第四階段": "#d97706",
        "考試":     "#475569",
    }

    _course_map = [
        ("Week 01", "第 1 章",  "§1.1–1.6",  "統計在工程決策中的角色",              "The Role of Statistics in Engineering",       "第一階段"),
        ("Week 02", "第 2 章",  "§2.1–2.4",  "統計資料之描述與探討",                "Describing & Presenting Statistical Data",    "第一階段"),
        ("Week 03", "第 3 章",  "§3.1–3.5",  "機率與系統可靠度",                    "Probability & System Reliability",            "第一階段"),
        ("Week 04", "第 4 章",  "§4.1–4.3",  "離散機率分配",                        "Discrete Probability Distributions",          "第一階段"),
        ("Week 05", "第 5 章",  "§5.1–5.6",  "連續機率分配與壽命工程",              "Continuous Distributions & Life Engineering", "第一階段"),
        ("Week 06", "第 6 章",  "§6.1–6.6",  "抽樣分配與中央極限定理",              "Sampling Distributions & CLT",                "第二階段"),
        ("Week 07", "第 7 章",  "§7.1–7.6",  "點估計與信賴區間",                    "Estimation & Confidence Intervals",           "第二階段"),
        ("Week 08", "—",        "—",          "期中考試",                            "Midterm Examination",                         "考試"),
        ("Week 09", "第 8 章",  "§8.1–8.2",  "統計假設檢定程序",                    "Hypothesis Testing Procedures",               "第三階段"),
        ("Week 10", "第 8 章",  "§8.3–8.4",  "母體比例與兩母體比較",                "Proportions & Two-Population Tests",          "第三階段"),
        ("Week 11", "第 9 章",  "§9.1–9.6",  "變異數分析 (ANOVA)",                  "Analysis of Variance",                        "第三階段"),
        ("Week 12", "第 10 章", "§10.1–10.9","迴歸分析（前半）",                    "Regression Analysis (Part 1)",                "第四階段"),
        ("Week 13", "第 10 章", "§10.1–10.9","迴歸分析與多維數據決策（後半）",       "Regression & Multivariate Decision",          "第四階段"),
        ("Week 14", "第 11 章", "§11.1–11.3","實驗設計 (DOE)",                      "Design of Experiments",                       "第四階段"),
        ("Week 15", "第 12 章", "§12.1–12.4","製程能力與產品放行決策",              "Process Capability & SPC",                    "第四階段"),
        ("Week 16", "—",        "—",          "期末考試",                            "Final Examination",                           "考試"),
    ]

    _rows = ""
    for _i, (_wk, _ch, _sec, _zh, _en, _phase) in enumerate(_course_map):
        _bg = "#f8fafc" if _i % 2 == 0 else "#ffffff"
        _pc = _phase_colors.get(_phase, "#475569")
        _rows += (
            f'<tr style="background:{_bg};">'
            f'<td style="padding:8px 14px;font-weight:700;color:#1e40af;white-space:nowrap;">{_wk}</td>'
            f'<td style="padding:8px 14px;white-space:nowrap;">'
            f'<span style="background:{_pc};color:white;font-size:0.72rem;font-weight:700;'
            f'padding:2px 8px;border-radius:10px;">{_phase}</span></td>'
            f'<td style="padding:8px 14px;color:#0369a1;white-space:nowrap;">{_ch}</td>'
            f'<td style="padding:8px 14px;color:#64748b;font-size:0.85rem;white-space:nowrap;">{_sec}</td>'
            f'<td style="padding:8px 14px;color:#0f172a;font-weight:600;">{_zh}</td>'
            f'<td style="padding:8px 14px;color:#94a3b8;font-size:0.82rem;">{_en}</td>'
            f'</tr>'
        )

    st.markdown(
        '<div style="overflow-x:auto;border-radius:10px;border:1px solid #e2e8f0;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:6px;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.92rem;">'
        '<thead><tr style="background:#1e3a5f;">'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;white-space:nowrap;">週次</th>'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;white-space:nowrap;">學習階段</th>'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;white-space:nowrap;">課本章節</th>'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;white-space:nowrap;">節次</th>'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;">主題（中文）</th>'
        '<th style="padding:10px 14px;color:#93c5fd;text-align:left;">Topic (English)</th>'
        '</tr></thead>'
        '<tbody>' + _rows + '</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )

    st.markdown('''
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:4px 0 24px 0;">
        <span style="background:#0369a1;color:white;font-size:0.75rem;font-weight:700;
            padding:3px 12px;border-radius:12px;">
            第一階段：數據描述與機率風險 (W1–W5)</span>
        <span style="background:#0f766e;color:white;font-size:0.75rem;font-weight:700;
            padding:3px 12px;border-radius:12px;">
            第二階段：抽樣推論與工程設計值 (W6–W7)</span>
        <span style="background:#7c3aed;color:white;font-size:0.75rem;font-weight:700;
            padding:3px 12px;border-radius:12px;">
            第三階段：統計檢定與工法比較 (W9–W11)</span>
        <span style="background:#d97706;color:white;font-size:0.75rem;font-weight:700;
            padding:3px 12px;border-radius:12px;">
            第四階段：模型預測・DOE・品質放行 (W12–W15)</span>
    </div>
    ''', unsafe_allow_html=True)

    # ── 版權聲明 ─────────────────────────────────────────────────────
    # ✅ 新增區塊
    st.divider()

    st.markdown('''
    <div style="border-radius:14px;overflow:hidden;
        box-shadow:0 2px 12px rgba(0,0,0,0.08);
        border:1px solid #e2e8f0;margin:8px 0 20px 0;">
        <div style="background:#1e3a5f;padding:12px 22px;
            display:flex;align-items:center;gap:10px;">
            <span style="color:#93c5fd;font-size:1.2rem;">©</span>
            <span style="color:#f1f5f9;font-weight:800;font-size:0.97rem;">
                教材版權聲明 · Educational Use Disclaimer
            </span>
        </div>
        <div style="background:#f8fafc;padding:18px 22px;
            color:#334155;font-size:0.88rem;line-height:1.9;">
            <p style="margin:0 0 12px 0;">
                本互動式學習平台為<strong>教學輔助工具</strong>，
                其互動實驗室、視覺化圖表、程式碼及測驗題目均為<strong>原創設計</strong>，
                旨在幫助修課學生透過互動方式加深對統計概念的理解。
            </p>
            <p style="margin:0 0 10px 0;">
                部分<strong>課本例題場景、數據與術語</strong>引用自下列著作，
                僅供課堂教學說明之用，<strong>非商業用途，未重製原著文字內容</strong>：
            </p>
            <div style="background:#eff6ff;border-left:4px solid #3b82f6;
                border-radius:0 6px 6px 0;padding:11px 18px;
                margin:10px 0 14px 0;font-size:0.87rem;color:#1e40af;line-height:1.9;">
                <strong>Lawrence L. Lapin</strong> 著；潘南飛、溫志中 編譯<br>
                《工程統計》（<em>Modern Engineering Statistics</em>）修訂三版<br>
                Cengage Learning Asia Pte. Ltd.，2021
                　<strong>ISBN 978-957-9282-94-9</strong>
            </div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div style="flex:1;min-width:200px;background:#f0fdf4;
                    border:1px solid #bbf7d0;border-radius:8px;padding:10px 14px;">
                    <div style="color:#166534;font-weight:700;font-size:0.85rem;margin-bottom:4px;">
                        ✅ 本平台的原創部分</div>
                    <div style="color:#334155;font-size:0.83rem;line-height:1.7;">
                        互動實驗室設計 · 視覺化圖表<br>
                        測驗題目 · Streamlit 程式碼 · 工程情境案例
                    </div>
                </div>
                <div style="flex:1;min-width:200px;background:#fef9c3;
                    border:1px solid #fde68a;border-radius:8px;padding:10px 14px;">
                    <div style="color:#92400e;font-weight:700;font-size:0.85rem;margin-bottom:4px;">
                        ⚠️ 引用自課本的部分</div>
                    <div style="color:#334155;font-size:0.83rem;line-height:1.7;">
                        部分例題數據（如表 2.6）· 專有名詞<br>
                        章節架構參照 · 公式符號表示
                    </div>
                </div>
            </div>
            <p style="margin:14px 0 0 0;color:#64748b;font-size:0.82rem;
                border-top:1px solid #e2e8f0;padding-top:10px;">
                ⚠️ 本平台內容受著作權保護。學生請勿將本平台內容截圖、複製、錄製或散佈於授課範圍外。
                如對版權有任何疑問，請聯繫授課教師。
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ── 側邊欄 ──────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a5f,#0f2440);
        border-radius:10px;padding:16px 18px;margin-bottom:12px;">
        <div style="color:#93c5fd;font-size:0.72rem;font-weight:700;
                    letter-spacing:0.14em;text-transform:uppercase;margin:0 0 8px 0;">
            學習導覽
        </div>
        <div style="color:#e2e8f0;font-size:0.98rem;line-height:1.7;">
            👆 <strong>請從上方選單</strong><br>選擇本週學習週次開始上課
        </div>
    </div>
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;
        border-radius:10px;padding:14px 16px;">
        <div style="color:#15803d;font-size:0.86rem;font-weight:700;margin:0 0 8px 0;">
            📊 本學期進度
        </div>
        <div style="color:#166534;font-size:0.82rem;line-height:1.7;">
            ✅ Week 01 已完成<br>
            ✅ Week 02 已完成<br>
            <span style="color:#94a3b8;">⬜ Week 03 即將開放</span>
        </div>
    </div>
    """, unsafe_allow_html=True)