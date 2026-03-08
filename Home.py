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
            工程統計：從工程現象到決策 📐
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
            <div style="color:#166534;font-size:0.92rem;line-height:1.9;">
                📊 <strong>第一階段</strong>：數據描述與機率風險<br>
                <span style="color:#16a34a;font-size:0.82rem;padding-left:1.4em;">W1 – W7</span><br>
                📐 <strong>第二階段</strong>：抽樣推論與工程設計值<br>
                <span style="color:#86efac;font-size:0.82rem;padding-left:1.4em;">W9 – W15</span>
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
                            width:18%;height:100%;border-radius:6px;"></div>
            </div>
            <div style="color:#64748b;font-size:0.8rem;margin:0 0 14px 0;">Week 2 / 15 完成</div>
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

    # ── Week 卡片 Row 1 ─────────────────────────────────────────────
    weeks_r1 = [
        ("01","統計在工程決策中的角色",
         "資料型態、母體與樣本、統計工程應用",
         "#3b82f6","#eff6ff","#1e40af","✅ 已開放"),
        ("02","統計資料之描述與陳示",
         "次數分配、位置測度、差異性量度、比例",
         "#22c55e","#f0fdf4","#166534","✅ 已開放"),
        ("03","機率概念與規則",
         "機率公理、條件機率、貝氏定理",
         "#6366f1","#eef2ff","#3730a3","🔒 即將開放"),
        ("04","機率分配",
         "期望值、二項分配、超幾何分配",
         "#f59e0b","#fffbeb","#92400e","🔒 即將開放"),
    ]
    cols_r1 = st.columns(4)
    for col, (wk,title,desc,hc,bc,tc,status) in zip(cols_r1, weeks_r1):
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

    # ── Week 卡片 Row 2 ─────────────────────────────────────────────
    weeks_r2 = [
        ("05","常態分配",
         "標準常態分配、常態近似、中央極限定理",
         "#ec4899","#fdf2f8","#9d174d","🔒 即將開放"),
        ("06","抽樣分配",
         "樣本均值分配、t 分配、χ² 分配",
         "#14b8a6","#f0fdfa","#134e4a","🔒 即將開放"),
        ("07","估計",
         "點估計、信賴區間、樣本大小決定",
         "#8b5cf6","#f5f3ff","#4c1d95","🔒 即將開放"),
        ("08","期中考評量",
         "第 1–7 週核心概念總整理與評量",
         "#ef4444","#fef2f2","#991b1b","🗓️ 期中評量"),
    ]
    cols_r2 = st.columns(4)
    for col, (wk,title,desc,hc,bc,tc,status) in zip(cols_r2, weeks_r2):
        locked = True
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