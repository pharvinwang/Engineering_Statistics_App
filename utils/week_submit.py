# 檔案位置： D:\Engineering_Statistics_App\utils\week_submit.py
import streamlit as st
import time

try:
    from utils.gsheets_db import (
        save_score, verify_student, get_saved_progress)
except ImportError:
    def save_score(*a,**k): return False
    def verify_student(*a,**k): return False,None
    def get_saved_progress(*a,**k): return None

from utils.week_components import (
    card, render_completion_rate,
    render_progress_card, render_progress_summary,
    render_teal_input_block)

_COOLDOWN = 10   # 冷卻秒數（全域設定，改這裡即可）


def _countdown(placeholder, seconds: int, msg: str):
    """在 placeholder 裡倒數 seconds 秒，每秒更新一次。"""
    for i in range(seconds, 0, -1):
        placeholder.warning(f"⏳ {msg}（{i} 秒後解除）")
        time.sleep(1)
    placeholder.empty()


def render_ia_section(cfg: dict):
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
    cooling_key   = f"{wp}_ia_cooling"

    # 1. 完成率
    render_completion_rate(done_count, total_count)

    # 2. 進度卡片
    render_progress_card(track_prefix, groups, labels)

    # 3. 公版青綠輸入區塊
    ia_id, ia_name, ia_code = render_teal_input_block(
        container_key = f"{wp}_submit_container",
        title         = "📤 送出互動參與記錄",
        subtitle      = "請填寫學號、姓名與驗證碼後送出，系統將記錄本週互動完成狀況。",
        id_key        = f"{wp}_ia_id",
        name_key      = f"{wp}_ia_name",
        code_key      = f"{wp}_ia_code",
    )

    # 4. 進度摘要
    cur_done = sum(1 for k in track_keys
                   if st.session_state.get(track_prefix + k, False))
    render_progress_summary(cur_done, total_count)

    # 5. 送出按鈕（冷卻期間 disabled）
    in_cooling = st.session_state.get(cooling_key, False)
    if st.button("📤 送出本週互動記錄", key=submit_key,
                 use_container_width=True, disabled=in_cooling):

        # ── 基本欄位檢查（不啟動冷卻，讓同學補填）──────────────────
        if not (ia_id and ia_name and ia_code):
            card("#f59e0b","#fffbeb","#92400e","⚠️ 資料不完整",
                 "請完整填寫學號、姓名與驗證碼。")
            st.stop()

        # ── 身分驗證（不啟動冷卻，讓同學修正）─────────────────────
        is_valid, student_idx = verify_student(ia_id, ia_name, ia_code)
        if not is_valid:
            card("#ef4444","#fef2f2","#991b1b","⛔ 身分驗證失敗",
                 "學號、姓名或驗證碼有誤，請重新確認！")
            st.stop()

        # ── 驗證通過，啟動冷卻 ──────────────────────────────────────
        st.session_state[cooling_key] = True
        ph = st.empty()   # 倒數訊息佔位

        # 準備寫入資料
        # ── ia_record 格式與 Week 01/02 完全一致 ──────────────────
        # 格式：「7% (1/14) | t1_prob:V | t1_add:- | ...」
        # 00_成績查詢.py 的 regex r'\((\d+)/(\d+)\)' 才能正確解析出 done/total
        def _make_detail(keys, prefix):
            parts = [k + (":" + ("V" if st.session_state.get(prefix + k, False) else "-"))
                     for k in keys]
            return " | ".join(parts)

        cur_pct    = int(cur_done / total_count * 100) if total_count else 0
        cur_detail_raw = _make_detail(track_keys, track_prefix)
        cur_record = f"{cur_pct}% ({cur_done}/{total_count}) | {cur_detail_raw}"

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
                cur_done   = sum(1 for k in track_keys
                                 if st.session_state.get(track_prefix + k, False))
                cur_pct    = int(cur_done / total_count * 100)
                cur_detail_raw = _make_detail(track_keys, track_prefix)
                cur_record = f"{cur_pct}% ({cur_done}/{total_count}) | {cur_detail_raw}"
        except Exception:
            pass

        # ── 第 1 次寫入 ─────────────────────────────────────────────
        ok = save_score(student_idx, ia_id, ia_name,
                        sheet_name, cur_record, cur_pct)
        if ok:
            _countdown(ph, _COOLDOWN, "系統寫入成功，防止重複送出")
            st.session_state[cooling_key] = False
            st.session_state[submitted_key] = {
                "name": ia_name, "id": ia_id,
                "pct": cur_pct, "done": cur_done, "total": total_count}
            st.rerun()

        # ── 第 1 次失敗 → 倒數後自動第 2 次 ────────────────────────
        _countdown(ph, _COOLDOWN, "寫入失敗，目前自動第 1 次嘗試寫入")
        ok = save_score(student_idx, ia_id, ia_name,
                        sheet_name, cur_record, cur_pct)
        if ok:
            _countdown(ph, _COOLDOWN, "系統寫入成功，防止重複送出")
            st.session_state[cooling_key] = False
            st.session_state[submitted_key] = {
                "name": ia_name, "id": ia_id,
                "pct": cur_pct, "done": cur_done, "total": total_count}
            st.rerun()

        # ── 第 2 次失敗 → 倒數後自動第 3 次 ────────────────────────
        _countdown(ph, _COOLDOWN, "寫入失敗，目前自動第 2 次嘗試寫入")
        ok = save_score(student_idx, ia_id, ia_name,
                        sheet_name, cur_record, cur_pct)
        if ok:
            st.session_state[cooling_key] = False
            st.session_state[submitted_key] = {
                "name": ia_name, "id": ia_id,
                "pct": cur_pct, "done": cur_done, "total": total_count}
            st.rerun()
        else:
            # ── 3 次全部失敗，解除冷卻，請同學稍後自行重試 ─────────
            st.session_state[cooling_key] = False
            card("#ef4444","#fef2f2","#991b1b","❌ 經 2 次自動嘗試仍寫入失敗",
                 "請稍待一會後再自行按下送出，或聯繫授課教師。")

    # 6. 送出成功持久顯示
    _r = st.session_state.get(submitted_key)
    if _r:
        card("#22c55e","#f0fdf4","#166534","✅ 互動參與記錄已送出！",
             f"👤 {_r['name']}（{_r['id']}）<br>"
             f"📊 本週互動完成率：<b>{_r['pct']}%</b>（{_r['done']}/{_r['total']} 項）<br>"
             "可繼續完成未做的互動後再次送出，記錄會自動更新。")