# 檔案位置： D:\Engineering_Statistics_App\utils\gsheets_db.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import time
import os

def init_connection():
    """初始化 Google Sheets 連線 (完美支援離線與雲端自動切換)"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 優先檢查本地端是否有 json 檔案 (離線測試用)
    if os.path.exists('google_key.json'):
        creds = ServiceAccountCredentials.from_json_keyfile_name('google_key.json', scope)
    # 若本地沒有，則嘗試讀取 Streamlit Cloud 的 Secrets
    elif "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        raise FileNotFoundError("找不到 Google 金鑰檔案！請確認 google_key.json 存在或已設定 Secrets。")
        
    return gspread.authorize(creds)

SPREADSHEET_ID = "1HPUEl3cAzfxwTvkcVU1PU9bBxqvWdX4NWjRbuZ9Qlcg"

def verify_student(student_id, name, v_code):
    """【防偷窺機制】驗證身分，若成功則順便回傳該生的「編號」"""
    try:
        client = init_connection()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Students")
        data = sheet.get_all_values()
        
        for row in data[1:]:
            if len(row) >= 4:
                if str(row[1]).strip() == str(student_id).strip() and \
                   str(row[2]).strip() == str(name).strip() and \
                   str(row[3]).strip() == str(v_code).strip():
                    return True, str(row[0]).strip()
        return False, None
    except Exception as e:
        st.error(f"資料庫連線異常：{e}")
        return False, None

def ensure_quiz_sheet_exists(client, spreadsheet, week_name):
    """【自動生成】建立新表單並複製：編號、學號、姓名"""
    try:
        sheet = spreadsheet.worksheet(week_name)
        return sheet
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=week_name, rows=100, cols=10)
        students_data = spreadsheet.worksheet("Students").get_all_values()
        
        bulk_data = [["編號", "學號", "姓名", "測驗時間", "答案紀錄", "測驗分數"]]
        for row in students_data[1:]:
            if len(row) >= 3 and str(row[1]).strip() != "":
                bulk_data.append([str(row[0]).strip(), str(row[1]).strip(), str(row[2]).strip(), "", "", ""])
        
        sheet.update(values=bulk_data, range_name="A1")
        return sheet

def check_has_submitted(student_id, week):
    """檢查是否已經作答過"""
    try:
        client = init_connection()
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        try:
            sheet = spreadsheet.worksheet(week)
        except gspread.exceptions.WorksheetNotFound:
            return False 
        
        ids = sheet.col_values(2) 
        student_id_str = str(student_id).strip()
        
        if student_id_str in ids:
            row_idx = ids.index(student_id_str) + 1
            row_data = sheet.row_values(row_idx)
            if len(row_data) >= 6 and str(row_data[5]).strip() != "":
                return True
        return False
    except Exception as e:
        return False

def save_score(student_idx, student_id, name, week, answer, score):
    """【無敵寫入】按學號對號入座，若為加選生則自動新增列"""
    for attempt in range(5):
        try:
            client = init_connection()
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            sheet = ensure_quiz_sheet_exists(client, spreadsheet, week)
            
            tw_tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            
            ids = sheet.col_values(2)
            student_id_str = str(student_id).strip()
            
            if student_id_str in ids:
                row_idx = ids.index(student_id_str) + 1
                sheet.update(values=[[current_time, answer, score]], range_name=f"D{row_idx}:F{row_idx}")
            else:
                sheet.append_row([student_idx, student_id_str, name, current_time, answer, score])
            
            return True

        except gspread.exceptions.APIError as api_err:
            if attempt < 4:
                time.sleep(1.5 ** attempt)
            else:
                st.error("伺服器目前人數較多，請稍候 10 秒再按一次送出！")
                return False
        except Exception as e:
            st.error(f"寫入失敗，錯誤代碼：{e}")
            return False