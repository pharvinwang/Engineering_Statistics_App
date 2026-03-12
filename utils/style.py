# 檔案位置： D:\Engineering_Statistics_App\utils\style.py
import streamlit as st

# ── 共用 Plotly 字體大小設定 (完美大圖表不重疊設定) ─────
F_GLOBAL = 18       
F_TITLE = 24        
F_AXIS = 20         
F_TICK = 18         
F_ANNOTATION = 20   

def apply_theme():
    """全域樣式注入 (終極暴力破解法，直接強制放大底層標籤)"""
    st.markdown("""
    <style>
    /* ══════════════════════════════════════════════
       Streamlit 專用字體系統（依實際 HTML 結構設計）
       ══════════════════════════════════════════════ */

    /* ── st.title() / st.header() / st.subheader() 正確選擇器 ── */
    div[data-testid="stHeading"] h1,
    h1[id] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        line-height: 1.3 !important;
    }
    div[data-testid="stHeading"] h2,
    h2[id] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
    }
    div[data-testid="stHeading"] h3,
    h3[id] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        line-height: 1.4 !important;
    }

    /* ── 一般段落 / st.write() / st.markdown() ── */
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] td,
    div[data-testid="stMarkdownContainer"] th {
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
    }

    /* ── st.caption() ── */
    div[data-testid="stCaptionContainer"] p {
        font-size: 1.0rem !important;
    }

    /* ── Widget 深藍色標籤 (slider / input / selectbox ...) ── */
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {
        font-size: 1.2rem !important;
        line-height: 1.6 !important;
    }

    /* ── Radio / Checkbox 選項文字 ── */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span {
        font-size: 1.2rem !important;
        line-height: 1.7 !important;
    }

    /* ── Radio 題目本身（st.radio 的問題文字）── */
    div[data-testid="stRadio"] > label,
    div[data-testid="stRadio"] > div > label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        line-height: 1.7 !important;
    }

    /* ── Expander 標題 ── */
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }

    /* ── Form 內的文字（整合性總測驗 Q1~Q4）── */
    div[data-testid="stForm"] p,
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] span {
        font-size: 1.2rem !important;
        line-height: 1.7 !important;
    }

    /* ── st.caption() ── */
    div[data-testid="stCaptionContainer"] p {
        font-size: 1.05rem !important;
    }

    /* ── st.metric() ── */
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] p { font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700 !important; }

    /* ── st.write() 一般文字 ── */
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] td,
    div[data-testid="stMarkdownContainer"] th,
    div[data-testid="stMarkdownContainer"] span {
        font-size: 1.2rem !important;
        line-height: 1.7 !important;
    }

    /* ── st.code() ── */
    div[data-testid="stCode"] pre,
    div[data-testid="stCode"] code {
        font-size: 1.0rem !important;
    }

    /* ── Tab 標籤 ── */
    div[data-testid="stTabs"] button[role="tab"] {
        background: #f1f5f9 !important;
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #e2e8f0 !important;
        border-bottom: none !important;
        margin-right: 4px !important;
        padding: 6px 16px !important;
        transition: background 0.2s !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        background: #dbeafe !important;
        border-color: #93c5fd !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #2563eb !important;
        border-color: #2563eb !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: 1.0rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* ── 側邊欄寬度 ── */
    section[data-testid="stSidebar"] {
        width: 240px !important;
        min-width: 240px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 240px !important;
    }

    /* ── 側邊欄自動頁面導覽列：縮小字體、減少 padding ── */
    [data-testid="stSidebarNav"] li a span,
    [data-testid="stSidebarNav"] li a p,
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p,
    nav[data-testid="stSidebarNav"] li span {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #334155 !important;
        line-height: 1.4 !important;
    }
    [data-testid="stSidebarNav"] li {
        padding: 1px 0 !important;
    }
    [data-testid="stSidebarNav"] a {
        padding: 4px 8px !important;
    }

    /* ── 自訂卡片與徽章 ── */
    .concept-box { background: linear-gradient(135deg, #1e3a5f 0%, #0f2440 100%); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px 20px; margin: 12px 0; color: #e2e8f0; font-size: 1.0rem; line-height: 1.7; }
    .why-box { background: linear-gradient(135deg, #1a3a2a 0%, #0d2218 100%); border-left: 4px solid #22c55e; border-radius: 8px; padding: 14px 18px; margin: 10px 0; color: #d1fae5; font-size: 1.0rem; line-height: 1.7; }
    .formula-box { background: #1e1b4b; border: 1px solid #4f46e5; border-radius: 8px; padding: 14px 18px; margin: 10px 0; text-align: center; color: #c7d2fe; font-size: 1.2rem; line-height: 1.6; }
    .discover-box { background: linear-gradient(135deg, #3a1a00 0%, #1f0e00 100%); border-left: 4px solid #f97316; border-radius: 8px; padding: 14px 18px; margin: 10px 0; color: #fed7aa; font-size: 1.0rem; line-height: 1.7; }
    .step-badge { display: inline-block; background: #3b82f6; color: white; border-radius: 50%; width: 26px; height: 26px; text-align: center; line-height: 26px; font-weight: bold; margin-right: 8px; }

    /* ── 6. 您的自訂淺色大表格 ── */
    .big-table { border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e2e8f0; margin-bottom: 20px; background-color: white; }
    .big-table table { width: 100%; font-size: 1.2rem !important; border-collapse: collapse; text-align: center; margin-bottom: 0; }
    .big-table th { background-color: #f8fafc; color: #475569; text-align: center !important; padding: 14px; border-bottom: 2px solid #e2e8f0; font-weight: 700; font-size: 1.2rem !important; }
    .big-table td { padding: 14px; border-bottom: 1px solid #f1f5f9; color: #334155; font-size: 1.2rem !important; }
    .big-table tr:last-child td { border-bottom: none; }
    .big-table tbody tr:hover { background-color: #f1f5f9; }

    /* ── 7. st.table() 原生表格 ── */
    .element-container table td,
    .element-container table th {
        font-size: 1.2rem !important;
        padding: 10px 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def set_chart_layout(fig, title_text=None, x_title=None, y_title=None):
    """共用圖表佈局設定器"""
    layout_updates = dict(font=dict(size=F_GLOBAL))
    if title_text:
        layout_updates['title'] = dict(text=title_text, font=dict(size=F_TITLE))
    if x_title:
        layout_updates['xaxis'] = dict(title=dict(text=x_title, font=dict(size=F_AXIS)), tickfont=dict(size=F_TICK))
    if y_title:
        layout_updates['yaxis'] = dict(title=dict(text=y_title, font=dict(size=F_AXIS)), tickfont=dict(size=F_TICK))
    
    fig.update_layout(**layout_updates)
    return fig