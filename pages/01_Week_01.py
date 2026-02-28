# 檔案位置： D:\Engineering_Statistics_App\pages\01_Week_01.py
import streamlit as st
import random
from utils.style import apply_theme

apply_theme()  # 呼叫樣式函數

# 匯入後端資料庫工具 (確保匯入了 verify_student, check_has_submitted, save_score)
try:
    from utils.gsheets_db import save_score, check_has_submitted, verify_student
except ImportError:
    def save_score(*args, **kwargs): return False
    def check_has_submitted(*args, **kwargs): return False
    def verify_student(*args, **kwargs): return False, None

# 確保未登入者不能直接網址輸入進入此頁
if "password_correct" not in st.session_state or not st.session_state.password_correct:
    st.warning("請先回到首頁進行登入。")
    st.stop()

# ==========================================
# 頁面標題與內容
# ==========================================
st.title("Week 01｜統計在工程決策中的角色 🎯")
st.caption("對應教材：Lawrence L. Lapin《工程統計》第 1 章 (1.1 – 1.6)")

st.header("1. 本週核心理論與互動")
st.write("請依序點選下方各小節的標籤，完成理論閱讀與互動實驗。")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1.1-1.2 統計與資料型態", 
    "1.3 母體、樣本與推論", 
    "1.4 需要樣本的理由", 
    "1.5 樣本的選取", 
    "1.6 統計工程應用"
])

# ------------------------------------------
# Tab 1: 1.1 - 1.2 統計資料型態
# ------------------------------------------
with tab1:
    st.subheader("📊 統計學的意義與資料型態")
    st.markdown("**統計學 (Statistics)** 為透過數值資料的分析，提供人們在不確定情況下作成適當決策或傳達有用資訊的科學方法。")
    st.write("資料依不同的衡量方式（尺度），可分為四大類型：")
    st.markdown("""
    * **名目資料 (Nominal)**：僅代表分類（如電機系代號1、土木系代號2）。
    * **順序資料 (Ordinal)**：具有分級或排序（如蒲福風級表中，3代表微風，6代表強風）。
    * **區間資料 (Interval)**：可排序且差距有意義，但無真正零點（如溫度：攝氏 100°C 與 50°C）。
    * **比率資料 (Ratio)**：具真正零點，可作乘除運算（如時間、重量、長度）。
    """)
    st.divider()
    st.info("💡 **隨堂小測驗：資料型態鑑定儀**")
    data_example = st.radio("📍 **題目：『橋樑基座承受的載重 (噸)』是屬於哪一種資料型態？你覺得是以下哪一個呢？請勾選你覺得的答案：**", 
                            ["請選擇您的答案...", "A. 名目資料 (Nominal)", "B. 順序資料 (Ordinal)", "C. 區間資料 (Interval)", "D. 比率資料 (Ratio)"])
    if st.button("送出鑑定", key="btn_tab1"):
        if data_example == "請選擇您的答案...":
            st.warning("⚠️ 嘿！您還沒選擇答案喔，請先勾選一個再送出。")
        elif data_example == "D. 比率資料 (Ratio)":
            st.success("🎉 **恭喜您答對了！您很清楚定義。** \n\n**解析**：重量有絕對的零點（0噸代表沒有重量），且 20 噸的載重確實是 10 噸的兩倍，可以進行乘除運算。")
        else:
            st.error("❌ **答錯囉！請再看一下上面的定義。** \n\n**提示**：想想看，載重有沒有「真正的零點」？能不能說 20 噸是 10 噸的兩倍呢？")

# ------------------------------------------
# Tab 2: 1.3 母體與樣本 (演繹與歸納)
# ------------------------------------------
with tab2:
    st.subheader("🔍 母體與樣本、演繹與歸納統計")
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        st.markdown("🎯 **母體 (Population)**：所感興趣之對象特徵的所有可能觀察結果的集合。")
        st.markdown("🧩 **樣本 (Sample)**：由母體選出的部分觀測值的集合。")
    with col2_2:
        st.markdown("⬇️ **演繹統計 (Deductive)**：由充分已知的母體特性來探討樣本的相關特性。")
        st.markdown("⬆️ **歸納/推論統計 (Inductive)**：研究如何由已知的樣本特性來推論其未知母體特性。")
    st.divider()
    st.info("💡 **隨堂小測驗：你是哪一種統計學家？**")
    reasoning_type = st.radio("📍 **題目：『我隨機抽了 3 支鋼材發現有 1 支瑕疵，我想以此推估整批鋼材的總不良率。』請問這屬於哪一種統計推論？**", 
                              ["請選擇您的答案...", "A. 演繹統計 (Deductive)", "B. 歸納/推論統計 (Inductive)"])
    if st.button("送出解答", key="btn_tab2"):
        if reasoning_type == "請選擇您的答案...":
            st.warning("⚠️ 請先勾選一個答案再送出喔！")
        elif reasoning_type == "B. 歸納/推論統計 (Inductive)":
            st.success("🎉 **恭喜您答對了！完全正確。** \n\n**解析**：這是在不確定情況下，從「已知的樣本結果」反向推估「未知的母體特徵」，這正是工程統計的核心精神！")
        else:
            st.error("❌ **噢不，答錯了！請再往上看一下兩者的定義差異。** \n\n**提示**：仔細看題目，我們是從「樣本推回母體」還是從「母體推向樣本」呢？")

# ------------------------------------------
# Tab 3: 1.4 需要樣本的理由
# ------------------------------------------
with tab3:
    st.subheader("💰 為何工程上多依賴「抽樣」而非「普查」？")
    st.write("以抽樣取代普查最主要的原因乃是因為其經濟上的優點之故，而且樣本可節省的成本通常是非常顯著的。 此外還有以下原因：")
    st.markdown("""
    1. **時間 (Timeliness)**：普查需花費很長的時間，如調查某新產品接受度，普查完成時產品可能已過時。
    2. **大母體 (Large Populations)**：如每日生產數仟個罐頭，母體太大（或無限）無法全部觀測。
    3. **具有破壞性特質的觀測 (Destructive Nature)**：如建築物之混凝土鑽心試驗，不可能對每一寸混凝土都予以鑽心。
    """)
    st.divider()
    st.info("💡 **互動實驗：鑽心試驗模擬器 (感受破壞性觀測的成本)**")
    total_concrete = st.slider("設定預拌混凝土總圓柱試體數量 (普查需全部壓碎)", 100, 1000, 500)
    sample_to_crush = st.number_input("決定抽樣壓碎的數量", 1, total_concrete, 10)
    if st.button("執行抗壓試驗", key="btn_tab3"):
        cost_saved = (total_concrete - sample_to_crush) * 500
        st.success(f"💥 **碰！試驗完成。** 您破壞了 {sample_to_crush} 顆試體取得抗壓強度。")
        st.write(f"因為採用了統計抽樣，您成功保全了 **{total_concrete - sample_to_crush}** 顆試體用於實際工程，並為專案省下了大約 **{cost_saved:,} 元** 的破壞性試驗成本！")

# ------------------------------------------
# Tab 4: 1.5 樣本的選取
# ------------------------------------------
with tab4:
    if "secret_a_country" not in st.session_state:
        st.session_state.secret_a_country = random.sample(range(1, 101), 10)
        st.session_state.secret_a_country.sort()
    st.subheader("🎲 確保樣本的代表性：隨機抽樣")
    st.write("簡單隨機抽樣法係指母體中的任一樣本被抽出的機率均相同。 實務上，可利用「隨機數字表 (附錄表 F)」或電腦產生的「擬隨機數 (Pseudorandom number)」來抽樣。")
    st.divider()
    st.info("💡 **互動盲測：隨機抽樣大比拼 (電腦 vs 亂數表 vs 人腦)**")
    st.markdown("假設有 100 名諾貝爾物理得主 (編號 01-100)，我們要抽出 10 位進行訪談。")
    st.markdown("🤫 **【秘密任務】系統已經在背後偷偷隨機指定了 10 位作為「A 國得主」！**")
    st.markdown("但在揭曉之前，沒有人知道是哪 10 個號碼。理論上，隨機抽出 10 人時，中獎期望值是 1 人。請選擇一種方法進行抽樣，看看哪一種方法能最客觀地逮住他們！")
    
    if st.button("🔄 重新洗牌 (更換隱藏的 A 國得主名單)"):
        st.session_state.secret_a_country = random.sample(range(1, 101), 10)
        st.session_state.secret_a_country.sort()
        st.success("洗牌完成！A 國得主已經換人囉，名單依然是個秘密！")

    sample_method = st.radio("請選擇您想測試的抽樣方法：", ["A. 電腦擬隨機抽樣", "B. 查閱隨機數字表 (附錄表 F)", "C. 人腦直覺隨機挑選 (手動輸入)"])
    
    def reveal_and_check(sampled_list):
        secret_list = st.session_state.secret_a_country
        caught = [x for x in sampled_list if x in secret_list]
        st.success(f"✅ **您的抽樣名單為**：\n\n{sampled_list}")
        st.warning(f"🔓 **【系統揭曉】隱藏的 10 位 A 國得主是**：\n\n{secret_list}")
        if len(caught) > 0:
            st.error(f"🎯 **對獎結果：發現 {len(caught)} 位 A 國得主！** 中獎編號為：{caught}")
        else:
            st.info("🎯 **對獎結果：您這次的抽樣沒有抽中任何 A 國得主喔！**")

    if sample_method == "A. 電腦擬隨機抽樣":
        st.write("由電腦程式內部重複地進行隨機選取，產生 10 個不重複的擬隨機數。")
        if st.button("🤖 執行電腦抽樣並對獎", key="btn_tab4_a"):
            sampled = random.sample(range(1, 101), 10)
            sampled.sort()
            reveal_and_check(sampled)
            
    elif sample_method == "B. 查閱隨機數字表 (附錄表 F)":
        st.write("請從亂數表抄寫 10 組 5 位數。系統將自動擷取每組的 **前 2 碼** 作為得主編號（若為 00 則視為 100）。")
        table_input = st.text_input("輸入 10 組數字 (請以「逗號」分隔)：", value="", placeholder="例如: 12651, 61646, 81169, 74436...")
        if st.button("📖 解析亂數表並對獎", key="btn_tab4_b"):
            if not table_input.strip():
                st.warning("⚠️ 請先查閱附錄表 F 並輸入數字再進行對獎！")
            else:
                parts = table_input.split(",")
                sampled = []
                for p in parts:
                    p = p.strip()
                    if len(p) >= 2 and p[:2].isdigit():
                        num = int(p[:2])
                        if num == 0: num = 100
                        sampled.append(num)
                if len(sampled) > 0:
                    sampled.sort()
                    reveal_and_check(sampled)
                else:
                    st.error("無法解析數字，請確保輸入格式正確 (例如: 12651, 61646)。")
                
    elif sample_method == "C. 人腦直覺隨機挑選 (手動輸入)":
        st.write("請憑直覺，隨機輸入 10 個 1~100 的數字。看看人類大腦是否真的能做到「公平且無預期的隨機」？")
        human_input = st.text_input("輸入 10 個數字 (請以「逗號」分隔)：", value="", placeholder="例如: 7, 14, 25, 33, 42...")
        if st.button("🧠 提交人腦名單並對獎", key="btn_tab4_c"):
            if not human_input.strip():
                st.warning("⚠️ 請先憑直覺輸入 10 個數字再進行對獎！")
            else:
                parts = human_input.split(",")
                sampled = []
                for p in parts:
                    try:
                        num = int(p.strip())
                        if 1 <= num <= 100:
                            sampled.append(num)
                    except:
                        pass
                if len(sampled) > 0:
                    sampled.sort()
                    reveal_and_check(sampled)
                else:
                    st.error("無法解析數字，請確保輸入為 1~100 之間的整數並以逗號分隔。")

# ------------------------------------------
# Tab 5: 1.6 統計之工程應用
# ------------------------------------------
with tab5:
    st.subheader("📈 模式建立與預測 (Model Building)")
    st.write("由一個或二個以上之自變數去預測其相關之因變數的結果，是為工程統計方法中之一重要的應用。 此種由試驗資料中求出變數間之最適配的關係式，稱之為迴歸分析。")
    st.divider()
    st.info("💡 **互動實驗：物理模型預測**")
    st.write("Lapin 課本中的物理模型範例：圓形金屬棒的應力 $S$ 與應變 $E$ 之間的線性關係方程式為：$$ S = -5,000 + 10^7 E $$")
    e_input = st.slider("請調整預期應變量 (E)", min_value=0.0001, max_value=0.0010, value=0.0005, step=0.0001, format="%.4f")
    if st.button("計算預測應力", key="btn_tab5"):
        s_predict = -5000 + (10**7 * e_input)
        st.success("計算完成！請看下方儀表板結果：")
        st.metric(label="預測之應力承受值 S (載重/單位面積)", value=f"{s_predict:,.0f} 磅", delta="依據迴歸線性模型預測")

st.divider()

# ==========================================
# 模組二：實務工程案例 (折疊收納)
# ==========================================
st.header("2. 實務工程案例探討")
with st.expander("☎️ 案例 A：電話聲音傳輸 (普查的迷思與抽樣的奇蹟) - 點擊展開", expanded=False):
    st.markdown("**案例背景 (例題 1.1)**")
    st.write("舊有電話主要缺點為聲波太慢且每一次談話需佔一個線路。若將原有連續傳遞（如同普查）改以每 100 微秒為一間隔的電磁波進行傳遞區間（如同抽樣）。")
    st.success("**工程結論**：以部分間斷傳輸電磁波的方式，較連續性傳遞可省下可觀的時間與成本，將電磁波速及容量增快至 100 倍！")

with st.expander("👨‍👩‍👧‍👦 案例 B：美國 1950 年人口普查 (普查一定比抽樣準確嗎？) - 點擊展開", expanded=False):
    st.markdown("**案例背景 (例題 1.2)**")
    st.write("美國 1950 年人口普查報告指出，30歲以下的鰥夫（喪妻）人數比1940年增加了 10倍 (100%)。這是一個極度不合理的數值。")
    st.error("**工程結論**：普查資料雖然龐大，但因第一次嘗試以電腦表列化處理，讀卡位置發生誤打造成巨大錯誤。一個草率隨便的普查，其結果往往不如一個謹慎抽樣所得的結果來得正確！")

st.divider()

# ==========================================
# 模組三：整合性總測驗 (4 題制，防亂猜與防重複送出)
# ==========================================
st.header("📝 3. 本週整合性總測驗")
st.info("請完成以下 4 題測驗 (每題 25 分)。\n⚠️ **注意**：作答送出後即鎖定成績，請確實核對您的學號與驗證碼。")

# 【前端防呆】利用 session_state 記錄是否已經送出，用來將按鈕反灰
if "w1_locked" not in st.session_state:
    st.session_state.w1_locked = False

with st.form("week1_unified_quiz"):
    # UI 更改：拔除班別，加入驗證碼 (並設定為密碼不顯示明文)
    col_id, col_name, col_code = st.columns(3)
    with col_id: st_id = st.text_input("📝 學號")
    with col_name: st_name = st.text_input("📝 姓名")
    with col_code: st_vcode = st.text_input("🔑 驗證碼", type="password")
    
    st.markdown("---")
    
    st.markdown("**Q1 (1.2節)：請問「橋樑的承載重量 (噸)」屬於哪一種統計資料型態？**")
    q1 = st.radio("Q1 選項：", ["名目資料 (Nominal)", "順序資料 (Ordinal)", "區間資料 (Interval)", "比率資料 (Ratio)"], key="q1")
    
    st.markdown("**Q2 (1.4節)：進行建築物之混凝土鑽心試驗來決定強度，是基於下列哪一種必須採用「抽樣」而非「普查」的原因？**")
    q2 = st.radio("Q2 選項：", ["時間限制 (Timeliness)", "具有破壞性特質的觀測 (Destructive Nature)", "大母體 (Large Populations)", "無法取得的母體 (Inaccessible Populations)"], key="q2")
    
    st.markdown("**Q3 (1.6節)：利用數學方程式 (如 $S = -5000 + 10^7 E$)，由已知應變預測未知應力的統計程序，屬於哪一種工程應用？**")
    q3 = st.radio("Q3 選項：", ["統計製程管制 (SPC)", "模式建立與預測 (迴歸分析)", "評量設計的可靠度", "實驗設計 (DOE)"], key="q3")
    
    st.markdown("**Q4 (1.3節)：某品管工程師已知這批鋼材的「母體平均強度」，他據此計算出隨機抽取 5 支鋼材其平均強度大於某個數值的機率。這種「由充分已知的母體特性來探討樣本相關特性」的推理過程稱之為？**")
    q4 = st.radio("Q4 選項：", ["敘述統計 (Descriptive Statistics)", "歸納統計 (Inductive Statistics)", "演繹統計 (Deductive Statistics)", "探究性統計 (Exploratory Data Analysis)"], key="q4")
    
    st.markdown("---")
    
    # 按鈕狀態會跟隨 st.session_state.w1_locked 變化
    if st.form_submit_button("✅ 簽署並送出本週測驗", disabled=st.session_state.w1_locked):
        if st_id and st_name and st_vcode:
            with st.spinner("系統安全驗證與自動評分中..."):
                
                # 第一關：【防止亂猜】接收驗證結果，並順便把該生的「編號」抓出來
                is_valid_user, student_idx = verify_student(st_id, st_name, st_vcode)
                
                if not is_valid_user:
                    st.error("⛔ **身分驗證失敗**：您輸入的學號、姓名或驗證碼有誤，請重新確認！(為保護成績安全，不予顯示作答結果)")
                else:
                    # 第二關：【防止重複】檢查是否已經有成績
                    if check_has_submitted(st_id, "Week 01"):
                        st.error("⛔ **拒絕送出**：系統查詢到雲端資料庫中，您已經繳交過【Week 01】的測驗囉！請勿重複作答。")
                    else:
                        # 通過所有安全查核，開始計算成績
                        score = 0
                        if q1 == "比率資料 (Ratio)": score += 25
                        if q2 == "具有破壞性特質的觀測 (Destructive Nature)": score += 25
                        if q3 == "模式建立與預測 (迴歸分析)": score += 25
                        if q4 == "演繹統計 (Deductive Statistics)": score += 25
                        
                        ans_str = f"Q1:{q1[:2]}, Q2:{q2[:4]}, Q3:{q3[:4]}, Q4:{q4[:2]}"
                        
                        # 把學生的編號 (student_idx) 一起傳給寫入系統
                        success = save_score(student_idx, st_id, st_name, "Week 01", ans_str, score)
                        
                        if success:
                            st.session_state.w1_locked = True
                            st.success(f"🎊 **上傳成功！** {st_name} ({st_id}) 驗證通過，您獲得了 **{score} 分**。成績已鎖定寫入資料庫！")
                            if score == 100:
                                st.balloons()
        else:
            st.warning("⚠️ 請完整填寫學號、姓名與驗證碼再送出表單。")

# 如果已經被鎖定，在表單下方顯示溫馨提示
if st.session_state.w1_locked:
    st.info("🔒 您的測驗已送出並鎖定。系統已安全登錄您的成績。")