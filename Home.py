# 檔案位置： D:\Engineering_Statistics_App\Home.py
import streamlit as st
from utils.style import apply_theme

# 1. 基本設定 (必須在第一行)
st.set_page_config(page_title="工程統計：數據驅動的風險導航", layout="wide")

# 2. 載入我們剛剛寫好的統一視覺樣式
apply_theme()

# ==========================================
# 登入與權限驗證
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🛡️ 工程統計 - 課程登入")
        st.info("請輸入課程專屬密碼以進入互動平台。")
        pwd = st.text_input("🔑 密碼", type="password")
        if st.button("登入"):
            if pwd == "ncyu_stat2026":  
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("密碼錯誤，請洽教授或助教。")
        return False
    return True

if check_password():
    # 融合您舊版 app.py 的優美文案
    st.title("🏠 工程統計：從工程現象到決策")
    st.caption("Department of Civil & Water Resources Engineering")
    
    st.markdown("""
    歡迎來到 **工程統計互動學習平台**。
    
    這不是一門只教你「怎麼算」的課，而是一門要讓你思考：
    > **在資料有限、不確定存在的工程世界中，你敢不敢做判斷？**
    """)
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("👨‍🏫 **班級資訊**\n*  **土木與水資源工程學系 工程統計**。\n* 使用教材：*Modern Engineering Statistics 《工程統計》 * (Lawrence L. Lapin 著 潘南飛,溫志中 編譯)")
    with col2:
        st.success("🗺️ **課程階段**\n* 第一階段：數據描述與機率風險 (W1-W7)\n* 第二階段：抽樣推論與工程設計值 (W9-W15)")
        
    st.warning("""
    ⚠️ **重要提醒**\n
    工程統計 **不是保證你一定是對的工具**，而是讓你 **知道自己可能錯在哪裡、錯多大**。這也是工程專業的一部分。
    """)
        
    st.sidebar.success("👆 請從上方選單選擇學習週次。")

