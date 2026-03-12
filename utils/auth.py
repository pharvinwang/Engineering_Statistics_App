# 檔案位置： D:\Engineering_Statistics_App\utils\auth.py
"""
各週次頁面共用的登入驗證守衛。
用法：在每個 pages/0X_Week_XX.py 頂端加入：

    from utils.auth import require_login
    require_login()
"""
import streamlit as st


def require_login():
    """若尚未通過 Home.py 的密碼驗證，顯示提示卡並停止頁面執行。"""        
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
            <div style="
                color:#fde68a;
                font-size:1.25rem;font-weight:700;line-height:1.8;">
                此頁面需要登入才能存取。<br>
                請先回到首頁輸入課程密碼。
            </div>
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