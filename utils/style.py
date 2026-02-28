# 檔案位置： D:\Engineering_Statistics_App\utils\style.py
import streamlit as st

def apply_theme():
    """全域字體放大與視覺優化設定 (移除會造成閃爍的替換語法)"""
    st.markdown("""
    <style>
        /* 放大一般內文與清單 */
        .stMarkdown p, .stMarkdown li { font-size: 20px !important; line-height: 1.8 !important; }
        /* 放大提示框 */
        .stAlert p { font-size: 19px !important; line-height: 1.6 !important; }
        /* 放大輸入框標題 */
        label[data-testid="stWidgetLabel"] p { font-size: 22px !important; font-weight: bold !important; color: #1E3A8A !important; }
        /* 放大選項文字 */
        div[role="radiogroup"] p, div[data-baseweb="checkbox"] p, div[data-baseweb="select"] span { font-size: 20px !important; color: #333333 !important; }
        /* 放大分頁籤 */
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span { font-size: 20px !important; font-weight: bold !important; }
        /* 放大拉桿數字 */
        div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"], div[data-testid="stThumbValue"] { font-size: 16px !important; font-weight: bold !important;}
        /* 放大按鈕 */
        .stButton button p { font-size: 20px !important; font-weight: bold !important; }
        /* 放大折疊面板與側邊欄 */
        div[data-testid="stExpander"] summary p { font-size: 22px !important; font-weight: bold !important; }
        [data-testid="stSidebar"] p { font-size: 18px !important; }
        [data-testid="stSidebarNav"] span { font-size: 20px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)