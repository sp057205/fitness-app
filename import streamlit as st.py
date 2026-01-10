import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 頁面設定 ---
st.set_page_config(page_title="30-Day Pull-up Pyramid V4.3", page_icon="🧗", layout="centered")

# ==========================================
# ☁️ Google Sheets 連線
# ==========================================
def get_google_sheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("fitness_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"連線錯誤: {e}")
        st.stop()

def load_data(sheet):
    try:
        data_str = sheet.cell(1, 1).value
        # 預設開始日期為「明天」
        tomorrow = (datetime.date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        if not data_str:
            return {"current_day": 1, "start_date": tomorrow, "weight": 70, "history": {}}
        return json.loads(data_str)
    except:
        tomorrow = (datetime.date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        return {"current_day": 1, "start_date": tomorrow, "weight": 70, "history": {}}

def save_data(sheet, data):
    sheet.update_cell(1, 1, json.dumps(data))

# ==========================================
# 🧗 金字塔訓練模組 (根據圖片重新編排)
# ==========================================
MODULES = {
    "A1": {
        "Name": "🔹 Week 1: 地基建立 (Foundation)",
        "Focus": "圖片底層：握力、懸吊、肩胛啟動",
        "Exercises": [
            {"name": "死垂懸吊 (Dead Hang)", "reps": "3組 x 30-45秒", "video": "https://www.youtube.com/results?search_query=dead+hang+pull+up+bar", "note": "放鬆背部，手臂打直，只練握力與適應體重"},
            {"name": "肩胛引體 (Scapular Pulls)", "reps": "3組 x 12次", "video": "https://www.youtube.com/results?search_query=scapular+pull+ups", "note": "手臂直，只動肩膀。這是引體向上的啟動開關"},
            {"name": "地面/椅子: 核心死蟲式", "reps": "3組 x 15次", "video": "https://www.youtube.com/results?search_query=dead+bug+core", "note": "圖片強調核心連結，避免身體擺盪"},
            {"name": "彈力帶: 面拉 (Face Pulls)", "reps": "4組 x 20次", "video": "https://www.youtube.com/results?search_query=band+face+pulls", "note": "強化旋轉肌袖，保護肩膀"}
        ]
    },
    "A2": {
        "Name": "🔹 Week 2: 水平拉力 (Rowing Strength)",
        "Focus": "圖片中層：澳洲式引體 (利用角度降低難度)",
        "Exercises": [
            {"name": "澳洲式引體 (Australian Pulls)", "reps": "4組 x 10-12次", "video": "https://www.youtube.com/results?search_query=australian+pull+ups", "note": "身體越平越難。專注將胸口拉向槓子，夾緊背部"},
            {"name": "單臂啞鈴/壺鈴划船", "reps": "4組 x 10次/邊", "video": "https://www.youtube.com/results?search_query=one+arm+dumbbell+row", "note": "增加單邊絕對力量"},
            {"name": "懸吊支撐 (Active Hang)", "reps": "3組 x 20秒", "video": "https://www.youtube.com/results?search_query=active+hang", "note": "比死垂進階，肩胛骨保持收縮狀態懸掛"},
            {"name": "核心: 棒式 (Plank)", "reps": "3組 x 45秒", "video": "https://www.youtube.com/results?search_query=plank", "note": "模擬引體向上時的身體剛性"}
        ]
    },
    "A3": {
        "Name": "🔹 Week 3: 離心突破 (Eccentric Power)",
        "Focus": "圖片上層：離心引體 (藉由下放對抗地心引力)",
        "Exercises": [
            {"name": "離心引體向上 (Negative)", "reps": "5組 x 5次 (下放5秒)", "video": "https://www.youtube.com/results?search_query=negative+pull+ups", "note": "跳上去，極慢下放。這是長肌肉最快的方法"},
            {"name": "彈力帶輔助引體", "reps": "3組 x 8-10次", "video": "https://www.youtube.com/results?search_query=band+assisted+pull+ups", "note": "感受完整的上拉行程"},
            {"name": "反手澳洲式引體 (Chin-up grip)", "reps": "3組 x 12次", "video": "https://www.youtube.com/results?search_query=underhand+australian+pull+ups", "note": "增加二頭肌參與，輔助拉力"},
            {"name": "核心: 懸吊抬腿", "reps": "3組 x 10次", "video": "https://www.youtube.com/results?search_query=hanging+knee+raise", "note": "進階核心訓練"}
        ]
    },
    "A4": {
        "Name": "🔹 Week 4: 巔峰驗收 (Peak Performance)",
        "Focus": "金字塔頂端：標準引體挑戰",
        "Exercises": [
            {"name": "🏆 標準引體向上 (嘗試)", "reps": "MAX 次數", "video": "https://www.youtube.com/results?search_query=pull+ups", "note": "第一組測驗最大次數，做不上去就改做離心"},
            {"name": "離心引體 (補強)", "reps": "3組 x 5次", "video": "", "note": "如果拉不上去，繼續用這招堆疊力量"},
            {"name": "跳繩: 500下 (慶祝)", "reps": "1組", "video": "", "note": "慶祝堅持一個月！"},
            {"name": "拍照記錄體態", "reps": "1張", "video": "", "note": "對比 Day 1 的變化"}
        ]
    },
    "B": {
        "Name": "🔹 Push & Shoulders (推力與肩膀)",
        "Focus": "平衡拮抗肌群，避免圓肩",
        "Exercises": [
            {"name": "啞鈴站姿肩推", "reps": "4組 x 10次", "video": "https://www.youtube.com/results?search_query=dumbbell+shoulder+press", "note": "核心收緊，重量適中"},
            {"name": "啞鈴側平舉", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=lateral+raise", "note": "打造寬肩視覺"},
            {"name": "伏地挺身", "reps": "4組 x 力竭", "video": "https://www.youtube.com/results?search_query=push+up", "note": "基礎推力"},
            {"name": "彈力帶擴胸", "reps": "3組 x 25次", "video": "https://www.youtube.com/results?search_query=band+pull+aparts", "note": "矯正圓肩"}
        ]
    },
    "C": {
        "Name": "🔹 Legs & Cardio (腿部與心肺)",
        "Focus": "保加利亞深蹲 + 壺鈴燃脂",
        "Exercises": [
            {"name": "🔥 保加利亞深蹲", "reps": "3組 x 10次/腳", "video": "https://www.youtube.com/results?search_query=bulgarian+split+squat", "note": "單腿之王，前腳發力"},
            {"name": "壺鈴擺盪 (Swings)", "reps": "5組 x 20次", "video": "https://www.youtube.com/results?search_query=kettlebell+swing", "note": "後鍊與有氧"},
            {"name": "負重臀橋", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=weighted+glute+bridge", "note": "啟動臀大肌"},
            {"name": "TABATA 跳繩", "reps": "4分鐘", "video": "https://www.youtube.com/results?search_query=tabata+jump+rope", "note": "VO2Max 衝刺"}
        ]
    },
    "Rest": {
        "Name": "🛌 休息與恢復 (Rest)",
        "Focus": "肌酸、鎂、睡眠",
        "Exercises": [
            {"name": "完全休息", "reps": "Relax", "note": "讓神經系統恢復"},
            {"name": "滾筒放鬆", "reps": "20 min", "note": "放鬆背部筋膜"},
            {"name": "補劑檢查", "reps": "Check", "note": "肌酸、D3、鎂"}
        ]
    }
}

# 30天日程表：根據週次自動切換 A1 -> A2 -> A3 -> A4
# 邏輯：週一(Pull), 週二(Rest), 週三(Push), 週四(Legs), 週五(Pull), 週六(Push), 週日(Legs)
SCHEDULE = (
    ["A1", "Rest", "B", "C", "A1", "B", "C"] +  # Week 1
    ["A2", "Rest", "B", "C", "A2", "B", "C"] +  # Week 2
    ["A3", "Rest", "B", "C", "A3", "B", "C"] +  # Week 3
    ["A4", "Rest", "B", "C", "A4", "B", "C"] +  # Week 4
    ["A4", "Final"] # Final Days
)

# ==========================================
# 🚀 APP 主程式
# ==========================================
def main():
    st.markdown("""<style>.stProgress > div > div > div > div { background-color: #00CC96; } .big-stat { font-size: 24px; font-weight: bold; color: #00CC96; } .supplement-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; }</style>""", unsafe_allow_html=True)
    st.title("🧗 30-Day Pull-up Pyramid V4.3")
    
    sheet = get_google_sheet_data()
    data = load_data(sheet)

    with st.sidebar:
        st.header("⚙️ 設定")
        # 自動處理日期格式
        try:
            saved_start = datetime.datetime.strptime(data.get('start_date'), "%Y-%m-%d").date()
        except:
            saved_start = datetime.date.today() + timedelta(days=1)
            
        start_date = st.date_input("開始日期", value=saved_start)
        data['start_date'] = str(start_date)
        
        weight = st.number_input("體重 (kg)", value=data.get('weight', 70))
        data['weight'] = weight
        target_protein = int(weight * 2.0)
        
        st.markdown(f"""<div class="supplement-box"><b>🥩 每日蛋白質目標</b><br><span class="big-stat">{target_protein} g</span></div>""", unsafe_allow_html=True)
        
        completed = len([k for k,v in data['history'].items() if v.get('completed')])
        st.progress(completed / 30)
        st.write(f"進度: {completed} / 30 天")
        
        if st.button("🔴 重置紀錄"):
            sheet.update_cell(1, 1, "")
            st.rerun()

    tab1, tab2 = st.tabs(["🚀 今日任務", "📅 完整日曆"])
    with tab1:
        # 計算今天是第幾天
        today_date = datetime.date.today()
        # 簡單計算天數差異
        delta = (today_date - start_date).days + 1
        
        # 讓使用者可以查看其他天，但預設顯示今天
        # 如果還沒開始，顯示 Day 1
        if delta < 1: delta = 1
        if delta > 30: delta = 30
        
        day = st.number_input("Day", 1, 30, delta)
        current_date = start_date + timedelta(days=day-1)
        st.markdown(f"### 📅 {current_date.strftime('%Y-%m-%d (%a)')}")
        
        if day > 29 and day <= 30:
            st.success("🏆 最終驗收週！")
            st.markdown("### 本週目標：你的第一下標準引體向上！")
            if st.button("挑戰完成！"): st.balloons()
        
        # 取得當日課表
        if day <= len(SCHEDULE):
            code = SCHEDULE[day-1]
        else:
            code = "Final"
            
        if code in MODULES:
            module = MODULES[code]
            if code == "Rest": st.success(f"🍃 {module['Name']}")
            else: st.error(f"🔥 {module['Name']}")
            st.caption(module['Focus'])

            with st.form(f"form_{day}"):
                for ex in module['Exercises']:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{ex['name']}**")
                        if ex.get('note'): st.caption(f"💡 {ex['note']}")
                        if ex.get('video'): st.link_button("📺 教學", ex['video'])
                    with c2: st.markdown(f"**{ex['reps']}**")
                    st.divider()
                
                st.markdown("#### 💊 補劑 & 營養")
                c_sup1, c_sup2 = st.columns(2)
                with c_sup1:
                    st.checkbox("肌酸 (5g)", key=f"creatine_{day}")
                    st.checkbox("K2 + D3", key=f"k2d3_{day}")
                with c_sup2:
                    st.checkbox("鎂 (睡前)", key=f"mag_{day}")
                    prot = st.number_input("蛋白質 (g)", 0, 300, key=f"prot_{day}")
                if prot >= target_protein: st.caption("✅ 蛋白質達標！")
                
                note = st.text_area("筆記", value=data['history'].get(str(day), {}).get('note', ''))
                if st.form_submit_button("✅ 完成並上傳"):
                    data['history'][str(day)] = {"completed": True, "date": str(datetime.date.today()), "note": note, "protein": prot}
                    # 只有當打卡的是今天或未來的進度才存檔
                    save_data(sheet, data)
                    st.success("紀錄已同步！")
                    st.rerun()
        else:
             st.info("休息日或計畫結束！")

    with tab2:
        schedule_data = []
        for i in range(1, 31):
            d = start_date + timedelta(days=i-1)
            c = SCHEDULE[i-1] if i-1 < len(SCHEDULE) else "FINAL"
            status = "✅" if data['history'].get(str(i), {}).get('completed') else "⬜"
            # 顯示模組名稱而非代號，讓使用者更清楚
            mod_name = MODULES[c]['Name'] if c in MODULES else c
            schedule_data.append({"日期": d.strftime("%m/%d"), "代號": c, "內容": mod_name, "狀態": status})
        st.dataframe(pd.DataFrame(schedule_data), height=500, use_container_width=True)

if __name__ == "__main__":
    main()
