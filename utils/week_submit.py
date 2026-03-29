# 檔案位置： D:\Engineering_Statistics_App\utils\week_submit.py
# v2.1 重大修正：
#   - 移除 _countdown() 中的 time.sleep() 阻塞（Streamlit 同步框架，
#     sleep 期間 worker thread 被佔用，55人並發時嚴重影響其他人的回應速度）
#   - 改用與 00_成績查詢.py 相同的 timestamp-based 冷卻機制
#   - 移除應用層三次重試（gsheets_db.save_score 內部已有 6 次指數退避重試）
#   - 新增 render_quiz_section()，統一小考送出邏輯

import streamlit as st
import time

try:
    from utils.gsheets_db import (
        save_score, verify_student, get_saved_progress, check_has_submitted)
except ImportError:
    def save_score(*a, **k): return False
    def verify_student(*a, **k): return False, None
    def get_saved_progress(*a, **k): return None
    def check_has_submitted(*a, **k): return False

from utils.week_components import (
    card, render_completion_rate,
    render_progress_card, render_progress_summary,
    render_teal_input_block)

_COOLDOWN = 10   # 互動參與送出冷卻秒數（全域設定，改這裡即可）


# ══════════════════════════════════════════════════════════════════════
# 互動參與送出區塊（Section 2a）
# ══════════════════════════════════════════════════════════════════════

def render_ia_section(cfg: dict):
    """
    渲染互動參與送出區塊。

    cfg 必要欄位：
        wp          : str   週次前綴，如 "w3"
        sheet_name  : str   Google Sheets 分頁名稱，如 "Week 03 互動"
        track_keys  : list  互動追蹤 key 清單（不含 prefix）
        groups      : dict  {群組名稱: [key, ...]}
        labels      : dict  {key: 顯示標籤}
        done_count  : int   目前已完成項目數
        total_count : int   總項目數
    """
    wp          = cfg["wp"]
    sheet_name  = cfg["sheet_name"]
    track_keys  = cfg["track_keys"]
    groups      = cfg["groups"]
    labels      = cfg["labels"]
    done_count  = cfg["done_count"]
    total_count = cfg["total_count"]

    track_prefix  = f"{wp}_track_"
    submit_key    = f"{wp}_ia_submit"
    submitted_key = f"{wp}_ia_submitted"
    cool_end_key  = f"{wp}_ia_cool_end_ts"   # ★ v2.1：timestamp-based

    # ── 1. 完成率 ──────────────────────────────────────────────────────
    render_completion_rate(done_count, total_count)

    # ── 2. 進度卡片 ────────────────────────────────────────────────────
    render_progress_card(track_prefix, groups, labels)

    # ── 3. 公版青綠輸入區塊 ────────────────────────────────────────────
    ia_id, ia_name, ia_code = render_teal_input_block(
        container_key = f"{wp}_submit_container",
        title         = "📤 送出互動參與記錄",
        subtitle      = "請填寫學號、姓名與驗證碼後送出，系統將記錄本週互動完成狀況。",
        id_key        = f"{wp}_ia_id",
        name_key      = f"{wp}_ia_name",
        code_key      = f"{wp}_ia_code",
    )

    # ── 4. 進度摘要 ────────────────────────────────────────────────────
    cur_done = sum(1 for k in track_keys
                   if st.session_state.get(track_prefix + k, False))
    render_progress_summary(cur_done, total_count)

    # ── 5. Timestamp-based 冷卻判斷（★ v2.1：不再 time.sleep(10)）─────
    now_ts   = time.monotonic()
    cool_end = st.session_state.get(cool_end_key, 0)
    in_cool  = now_ts < cool_end

    if in_cool:
        remain = max(0, int(cool_end - now_ts))
        st.info(f"⏳ {remain} 秒後可再次送出")
        time.sleep(1)    # 每次只 sleep 1 秒後 rerun，不阻塞整個 thread
        st.rerun()
        return

    # ── 6. 送出按鈕 ────────────────────────────────────────────────────
    if st.button("📤 送出本週互動記錄", key=submit_key, use_container_width=True):

        # 基本欄位檢查（不啟動冷卻）
        if not (ia_id and ia_name and ia_code):
            card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 資料不完整",
                 "請完整填寫學號、姓名與驗證碼。")
            st.stop()

        # 身分驗證（不啟動冷卻）
        is_valid, student_idx = verify_student(ia_id, ia_name, ia_code)
        if not is_valid:
            card("#ef4444", "#fef2f2", "#991b1b", "⛔ 身分驗證失敗",
                 "學號、姓名或驗證碼有誤，請重新確認！")
            st.stop()

        # ── 準備寫入資料 ───────────────────────────────────────────────
        # ia_record 格式與 Week 01/02 完全一致
        # 格式：「7% (1/14) | t1_prob:V | t1_add:- | ...」
        # 00_成績查詢.py 的 regex r'\((\d+)/(\d+)\)' 才能正確解析出 done/total
        def _make_detail(keys, prefix):
            return " | ".join(
                k + (":" + ("V" if st.session_state.get(prefix + k, False) else "-"))
                for k in keys)

        cur_pct        = int(cur_done / total_count * 100) if total_count else 0
        cur_detail_raw = _make_detail(track_keys, track_prefix)
        cur_record     = f"{cur_pct}% ({cur_done}/{total_count}) | {cur_detail_raw}"

        # ── 合併伺服器已儲存的更高進度（防止 session 重連後低分蓋高分）──
        try:
            saved = get_saved_progress(ia_id, sheet_name)
            if saved and saved["pct"] > cur_pct:
                # 解析舊格式（"k:V | k2:- | ..." 或舊逗號格式）
                saved_detail = saved.get("detail", "")
                if ":" in saved_detail:
                    for part in saved_detail.split("|"):
                        part = part.strip()
                        if ":" in part:
                            _k, _v = part.split(":", 1)
                            _k = _k.strip()
                            if _k in track_keys and _v.strip() == "V":
                                st.session_state[track_prefix + _k] = True
                else:
                    # 舊逗號格式相容
                    for _k in saved_detail.split(","):
                        _k = _k.strip()
                        if _k in track_keys:
                            st.session_state[track_prefix + _k] = True
                cur_done       = sum(1 for k in track_keys
                                     if st.session_state.get(track_prefix + k, False))
                cur_pct        = int(cur_done / total_count * 100) if total_count else 0
                cur_detail_raw = _make_detail(track_keys, track_prefix)
                cur_record     = f"{cur_pct}% ({cur_done}/{total_count}) | {cur_detail_raw}"
        except Exception:
            pass

        # ── 寫入（gsheets_db 內部已有 6 次指數退避重試，無需應用層重試）──
        with st.spinner("📡 寫入中…"):
            ok = save_score(student_idx, ia_id, ia_name,
                            sheet_name, cur_record, cur_pct)

        if ok:
            # ★ 冷卻啟動（寫入成功後才啟動）
            st.session_state[cool_end_key] = time.monotonic() + _COOLDOWN
            st.session_state[submitted_key] = {
                "name": ia_name, "id": ia_id,
                "pct": cur_pct, "done": cur_done, "total": total_count}
            st.rerun()
        else:
            card("#ef4444", "#fef2f2", "#991b1b", "❌ 寫入失敗",
                 "請稍待一會後再按一次「送出」，或聯繫授課教師。<br>"
                 "（您的互動進度完全保留，不需要重做）")

    # ── 7. 送出成功持久顯示 ────────────────────────────────────────────
    _r = st.session_state.get(submitted_key)
    if _r:
        card("#22c55e", "#f0fdf4", "#166534", "✅ 互動參與記錄已送出！",
             f"👤 {_r['name']}（{_r['id']}）<br>"
             f"📊 本週互動完成率：<b>{_r['pct']}%</b>（{_r['done']}/{_r['total']} 項）<br>"
             "可繼續完成未做的互動後再次送出，記錄會自動更新。")


# ══════════════════════════════════════════════════════════════════════
# 小考送出區塊（Section 2b）— ★ v2.1 新增
# ══════════════════════════════════════════════════════════════════════

def render_quiz_section(cfg: dict):
    """
    渲染統一小考區塊（密碼解鎖 → 身分驗證 → 作答 → 計分 → 儲存）。

    cfg 必要欄位：
        wp           : str    週次前綴，如 "w3"
        sheet_name   : str    Google Sheets 分頁名稱，如 "Week 03"
        form_key     : str    st.form 的唯一 key，如 "week3_unified_quiz"
        real_password: str    已從 get_weekly_password_safe() 取得的密碼
        questions    : list   題目清單，每題為 dict，格式如下：
            key         : str   唯一後綴，如 "qf1"（完整 widget key = wp + "_" + key）
            text        : str   題目文字（不含 **，函式自動加粗）
            options     : list  選項，第一個必須為 "請選擇..."
            correct     : str   正確答案前綴，如 "A." 或 "B."
            points      : int   該題配分，通常為 25
            explanation : str   作答後顯示的解析文字

    cfg 選填欄位：
        perfect_msg  : str    100 分時的鼓勵訊息（預設：全數掌握！）
        good_msg     : str    ≥75 分時的鼓勵訊息
        retry_msg    : str    <75 分時的鼓勵訊息

    使用範例（在各週 .py 的小考區塊）：
    ─────────────────────────────────────────────────────────────────
        from utils.week_submit import render_quiz_section

        real_password = get_weekly_password_safe("Week 03")
        if not real_password:
            real_password = "888888"

        # ── 密碼解鎖 UI ──────────────────────────────────────
        _card("🔒 測驗鎖定中", ...)
        _col_pw, _col_btn = st.columns([5, 1])
        with _col_pw:
            user_code = st.text_input("密碼", type="password",
                                      key="w3_unlock_code", ...)
        with _col_btn:
            st.button("🔓 解鎖", key="w3_unlock_btn", ...)

        if user_code != real_password:
            if user_code:
                _card("❌ 密碼錯誤", ...)
        else:
            render_quiz_section({
                "wp":            "w3",
                "sheet_name":    "Week 03",
                "form_key":      "week3_unified_quiz",
                "real_password": real_password,
                "perfect_msg":   "機率與系統可靠度的核心概念全數掌握！",
                "good_msg":      "建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。",
                "retry_msg":     "請回顧本週各節的概念說明與互動實驗，機率的邏輯需要多練習！",
                "questions": [
                    {
                        "key":         "qf1",
                        "text":        "Q1（§3.1）：...",
                        "options":     ["請選擇...", "A. ...", "B. ...", "C. ...", "D. ..."],
                        "correct":     "A.",
                        "points":      25,
                        "explanation": "§3.1：..."
                    },
                    # Q2, Q3, Q4 同上
                ],
            })
    ─────────────────────────────────────────────────────────────────
    """
    wp            = cfg["wp"]
    sheet_name    = cfg["sheet_name"]
    form_key      = cfg["form_key"]
    questions     = cfg["questions"]
    perfect_msg   = cfg.get("perfect_msg", "本週核心概念全數掌握！")
    good_msg      = cfg.get("good_msg",
                            "建議回頭看看答錯的題目，對應 Tab 的互動實驗有詳細解析。")
    retry_msg     = cfg.get("retry_msg",
                            "請回顧本週各節的概念說明與互動實驗，加強練習！")

    locked_key    = f"{wp}_locked"    # 與現有週次程式的命名一致

    # ── 初始化鎖定狀態 ─────────────────────────────────────────────────
    if locked_key not in st.session_state:
        st.session_state[locked_key] = False

    total_points  = sum(q["points"] for q in questions)
    n_questions   = len(questions)

    # ── 解鎖成功提示 ────────────────────────────────────────────────────
    card("#22c55e", "#f0fdf4", "#166534", "🔓 密碼正確！",
         "測驗已解鎖，請完成以下題目後送出。")
    card("#3b82f6", "#eff6ff", "#1e40af", "📋 測驗說明",
         f"{n_questions} 題，每題 {total_points // n_questions} 分，"
         f"共 {total_points} 分。作答送出後即鎖定成績，請確實核對學號與驗證碼！")

    # ── 身分輸入（在 form 外，表單提交時直接用回傳的局部變數）───────────
    st_id, st_name, st_vcode = render_teal_input_block(
        container_key = f"{wp}_quiz_container",
        title         = "📝 填寫身分資料",
        subtitle      = "請填寫學號、姓名與驗證碼，系統將驗證後鎖定成績。",
        id_key        = f"{wp}_quiz_id",
        name_key      = f"{wp}_quiz_name",
        code_key      = f"{wp}_quiz_code",
    )

    # ── 作答表單 ────────────────────────────────────────────────────────
    with st.form(form_key):
        st.markdown("---")

        answers = []
        for q in questions:
            ans = st.radio(
                f"**{q['text']}**",
                q["options"],
                key=f"{wp}_{q['key']}"
            )
            answers.append(ans)

        st.markdown("---")

        if st.form_submit_button(
                "✅ 簽署並送出本週測驗",
                use_container_width=True,
                type="primary",
                disabled=st.session_state[locked_key]):

            # ── 欄位完整性檢查 ──────────────────────────────────────────
            if not (st_id and st_name and st_vcode):
                card("#f59e0b", "#fffbeb", "#92400e", "⚠️ 資料不完整",
                     "請完整填寫學號、姓名與驗證碼再送出表單。")
            else:
                is_valid, student_idx = verify_student(st_id, st_name, st_vcode)
                if not is_valid:
                    card("#ef4444", "#fef2f2", "#991b1b", "⛔ 身分驗證失敗",
                         "您輸入的學號、姓名或驗證碼有誤，請重新確認！")
                elif check_has_submitted(st_id, sheet_name):
                    card("#ef4444", "#fef2f2", "#991b1b", "⛔ 拒絕送出",
                         f"系統查詢到您已繳交過 {sheet_name} 的測驗！請勿重複作答。")
                else:
                    # ── 計分 ────────────────────────────────────────────
                    score = sum(
                        q["points"] for q, ans in zip(questions, answers)
                        if ans.startswith(q["correct"])
                    )
                    detail_str = ",".join(
                        f"Q{i+1}:{ans[:2]}" for i, ans in enumerate(answers)
                    )

                    success = save_score(student_idx, st_id, st_name,
                                         sheet_name, detail_str, score)
                    if not success:
                        card("#ef4444", "#fef2f2", "#991b1b", "❌ 送出失敗",
                             "請稍待一會後再按一次「送出本週測驗」，或聯繫授課教師。")
                    else:
                        st.session_state[locked_key] = True

                        # 分數卡
                        st.markdown(
                            '<div style="border-radius:12px;overflow:hidden;'
                            'box-shadow:0 2px 10px rgba(0,0,0,0.07);'
                            'border:1px solid #e2e8f0;margin:8px 0;">'
                            '<div style="background:#22c55e;padding:10px 18px;">'
                            '<span style="color:white;font-weight:700;font-size:1.0rem;">'
                            '🎊 上傳成功！</span></div>'
                            '<div style="background:#f0fdf4;padding:14px 18px;color:#166534;">'
                            f'<b>{st_name}</b>（{st_id}）驗證通過<br>'
                            f'<span style="font-size:2.0rem;font-weight:900;color:#15803d;">'
                            f'{score}</span>'
                            f'<span style="font-size:1.0rem;"> 分　成績已鎖定！</span>'
                            '</div></div>',
                            unsafe_allow_html=True)

                        # 鼓勵訊息
                        if score == total_points:
                            st.balloons()
                            card("#7c3aed", "#f5f3ff", "#4c1d95",
                                 "🏆 滿分！", perfect_msg)
                        elif score >= total_points * 0.75:
                            card("#3b82f6", "#eff6ff", "#1e40af",
                                 "👍 表現不錯！", good_msg)
                        else:
                            card("#f59e0b", "#fffbeb", "#92400e",
                                 "📖 繼續加油！", retry_msg)

                        # 逐題解析
                        rows_html = ""
                        for i, (q, ans) in enumerate(zip(questions, answers)):
                            correct_full = next(
                                (opt for opt in q["options"]
                                 if opt.startswith(q["correct"])), q["correct"])
                            ok     = ans.startswith(q["correct"])
                            hbg    = "#15803d" if ok else "#dc2626"
                            bbg    = "#f0fdf4" if ok else "#fef2f2"
                            tc2    = "#166534" if ok else "#991b1b"
                            icon   = "✅" if ok else "❌"
                            status = "答對" if ok else "答錯"
                            rows_html += (
                                f'<div style="border-radius:10px;overflow:hidden;'
                                f'border:1px solid #e2e8f0;margin:8px 0;">'
                                f'<div style="background:{hbg};padding:8px 16px;">'
                                f'<span style="color:white;font-weight:700;">'
                                f'{icon} Q{i+1}　{status}</span></div>'
                                f'<div style="background:{bbg};padding:12px 16px;'
                                f'color:{tc2};font-size:0.97rem;line-height:1.7;">'
                                f'<b>您的答案：</b>{ans}<br>'
                                + ('' if ok else f'<b>正確答案：</b>{correct_full}<br>')
                                + f'<b>解析：</b>{q["explanation"]}'
                                f'</div></div>'
                            )
                        st.markdown(
                            '<div style="background:#1e3a5f;border-radius:12px;'
                            'padding:10px 18px;margin:14px 0 6px 0;">'
                            '<span style="color:white;font-weight:800;font-size:1.05rem;">'
                            '📋 本次作答詳細解析</span></div>'
                            + rows_html,
                            unsafe_allow_html=True)

    # ── 已鎖定提示（form 外，頁面 rerun 後仍顯示）──────────────────────
    if st.session_state.get(locked_key, False):
        card("#475569", "#f8fafc", "#334155", "🔒 測驗已鎖定",
             "系統已安全登錄您的成績，如有疑問請聯繫授課教師。")