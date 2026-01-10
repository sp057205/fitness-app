import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 頁面設定 ---
st.set_page_config(page_title="30-Day Pro V5.2 (Final)", page_icon="🦍", layout="centered")

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
        # 預設邏輯：若無資料，將「本週一」設為開始日
        today = datetime.date.today()
        start_of_week = today - timedelta(days=today.weekday()) 
        
        if not data_str:
            return {"start_date": str(start_of_week), "weight": 70, "history": {}}
        return json.loads(data_str)
    except:
        today = datetime.date.today()
        start_of_week = today - timedelta(days=today.weekday())
        return {"start_date": str(start_of_week), "weight": 70, "history": {}}

def save_data(sheet, data):
    sheet.update_cell(1, 1, json.dumps(data))

# ==========================================
# 🏋️ 訓練模組 (V5.2 補強版)
# ==========================================

# 通用動作：每日必做
DAILY_HANG = {"name": "🔥 每日儀式: 單槓懸吊 (Dead Hang)", "reps": "3組 x 30-60秒", "video": "https://www.youtube.com/results?search_query=dead+hang", "note": "每日必做！手臂打直，放鬆脊椎，預防肩膀受傷"}

MODULES = {
    # --- 背部 (Back) ---
    "Back": {
        "Name": "🔹 Back (練背)",
        "Focus": "週日/週三：引體地基與後肩強化",
        "Exercises": [
            DAILY_HANG,
            {"name": "肩胛引體 (Scapular Pulls)", "reps": "3組 x 12-15次", "video": "https://www.youtube.com/results?search_query=scapular+pull+ups", "note": "手臂伸直，只動肩膀，啟動背闊肌"},
            {"name": "負向引體 (Negative Pull-ups)", "reps": "4組 x 6-8次", "video": "https://www.youtube.com/results?search_query=negative+pull+ups", "note": "跳上，5秒極慢下放 (肌肥大關鍵)"},
            {"name": "澳式引體 (Australian Pulls)", "reps": "4組 x 10-12次", "video": "https://www.youtube.com/results?search_query=australian+pull+ups", "note": "水平拉，身體越平越難"},
            {"name": "TRX/彈力帶: Y-T-W 伸展", "reps": "3組 x 10次/方向", "video": "https://www.youtube.com/results?search_query=trx+ytw+exercise", "note": "Y字(下斜方)、T字(後三角)、W字(旋轉肌袖)"},
            {"name": "臉拉 (Face Pulls)", "reps": "4組 x 20次", "video": "https://www.youtube.com/results?search_query=face+pull", "note": "矯正圓肩，大拇指後旋"}
        ]
    },
    
    # --- 胸部 (Chest) + 核心補強 ---
    "Chest": {
        "Name": "🔹 Chest (練胸 + 核心)",
        "Focus": "週一/週四：推力、肩膀與腹肌",
        "Exercises": [
            DAILY_HANG,
            {"name": "標準伏地挺身", "reps": "4組 x 力竭", "video": "https://www.youtube.com/results?search_query=perfect+push+up", "note": "胸肌充血"},
            {"name": "啞鈴站姿肩推", "reps": "4組 x 10次", "video": "https://www.youtube.com/results?search_query=dumbbell+shoulder+press", "note": "不拱腰，核心收緊 (若肩痛改地板臥推)"},
            {"name": "啞鈴側平舉", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=lateral+raise", "note": "寬肩關鍵"},
            {"name": "彈力帶擴胸", "reps": "3組 x 25次", "video": "https://www.youtube.com/results?search_query=band+pull+aparts", "note": "挺胸矯正"},
            {"name": "🔥 核心: 死蟲式 (Dead Bug)", "reps": "3組 x 15次", "video": "https://www.youtube.com/results?search_query=dead+bug+core", "note": "V5.2新增: 對抗骨盆前傾，增強前側核心"}
        ]
    },
    
    # --- 腿部 (Legs) ---
    "Legs": {
        "Name": "🔹 Legs & VO2 (練腿)",
        "Focus": "週五：側蹲與高強度心肺",
        "Exercises": [
            DAILY_HANG,
            {"name": "側蹲 (Cossack Squat)", "reps": "3組 x 10次/邊", "video": "https://www.youtube.com/results?search_query=cossack+squat", "note": "強化內收肌與活動度"},
            {"name": "保加利亞深蹲", "reps": "3組 x 10次/腳", "video": "https://www.youtube.com/results?search_query=bulgarian+split+squat", "note": "單腿之王，前腳發力"},
            {"name": "負重臀橋", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=weighted+glute+bridge", "note": "夾緊屁股"},
            {"name": "⚡ TABATA 跳繩", "reps": "4分鐘 (20秒衝/10秒休)", "video": "https://www.youtube.com/results?search_query=tabata+jump+rope", "note": "VO2Max 衝刺"}
        ]
    },
    
    # --- 休息/有氧 (Active Rest) + 腿部熱身 ---
    "Cardio": {
        "Name": "🛌 Active Rest (恢復 + 腿熱身)",
        "Focus": "週二/週六：跳繩與主動恢復",
        "Exercises": [
            DAILY_HANG,
            {"name": "🔥 熱身: 徒手深蹲", "reps": "2組 x 20次", "video": "https://www.youtube.com/results?search_query=air+squats", "note": "V5.2新增: 增加腿部頻率，喚醒神經"},
            {"name": "間歇跳繩 (Intervals)", "reps": "10組 (跳1分 / 休30秒)", "video": "https://www.youtube.com/results?search_query=jump+rope+workout", "note": "共15分鐘，保持心率"},
            {"name": "滾筒放鬆", "reps": "20 min", "video": "https://www.youtube.com/results?search_query=full+body+foam+rolling", "note": "放鬆背部與腿"},
            {"name": "補鎂 & 睡眠", "reps": "Check", "video": "", "note": "修復神經"}
        ]
    }
}

# ==========================================
# 🚀 APP 主程式
# ==========================================
def main():
    st.markdown("""<style>.stProgress > div > div > div > div { background-color: #00CC96; } .big-stat { font-size: 24px; font-weight: bold; color: #00CC96; } .supplement-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; } .day-header { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)
    st.title("🦍 30-Day Pro V5.2 (Final)")
    
    sheet = get_google_sheet_data()
    data = load_data(sheet)

    with st.sidebar:
        st.header("⚙️ 週設定")
        try:
            saved_start = datetime.datetime.strptime(data.get('start_date'), "%Y-%m-%d").date()
        except:
            saved_start = datetime.date.today() - timedelta(days=datetime.date.today().weekday())
            
        start_date = st.date_input("計畫開始週 (請選週一)", value=saved_start)
        data['start_date'] = str(start_date)
        
        weight = st.number_input("體重 (kg)", value=data.get('weight', 70))
        data['weight'] = weight
        target_protein = int(weight * 2.0)
        
        st.markdown(f"""<div class="supplement-box"><b>🥩 每日蛋白質目標</b><br><span class="big-stat">{target_protein} g</span></div>""", unsafe_allow_html=True)
        
        completed = len([k for k,v in data['history'].items() if v.get('completed')])
        st.progress(completed / 30)
        st.write(f"打卡天數: {completed} 天")
        
        if st.button("🔴 重置紀錄"):
            sheet.update_cell(1, 1, "")
            st.rerun()

    tab1, tab2 = st.tabs(["🚀 今日任務", "📅 完整週表"])
    with tab1:
        today = datetime.date.today()
        days_diff = (today - start_date).days
        current_week = (days_diff // 7) + 1
        weekday_idx = today.weekday() # 0=Mon, ... 6=Sun
        
        weekdays_map = ["Monday (週一)", "Tuesday (週二)", "Wednesday (週三)", "Thursday (週四)", "Friday (週五)", "Saturday (週六)", "Sunday (週日)"]
        day_name = weekdays_map[weekday_idx]
        
        st.markdown(f"### 🗓️ Week {current_week} | {day_name}")
        
        # --- 課表邏輯 ---
        target_code = ""
        if weekday_idx == 0 or weekday_idx == 3: target_code = "Chest"  # Mon, Thu
        elif weekday_idx == 1 or weekday_idx == 5: target_code = "Cardio" # Tue, Sat
        elif weekday_idx == 4: target_code = "Legs"   # Fri
        elif weekday_idx == 2 or weekday_idx == 6: target_code = "Back"   # Wed, Sun
        
        if target_code in MODULES:
            module = MODULES[target_code]
            if target_code == "Cardio": st.success(f"🧘 {module['Name']}")
            else: st.error(f"🦍 {module['Name']}")
            st.caption(module['Focus'])

            day_key = f"W{current_week}-{day_name[:3]}"

            with st.form(f"form_{day_key}"):
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
                    st.checkbox("肌酸 (5g)", key=f"creatine_{day_key}")
                    st.checkbox("K2 + D3", key=f"k2d3_{day_key}")
                with c_sup2:
                    st.checkbox("鎂 (睡前)", key=f"mag_{day_key}")
                    prot = st.number_input("蛋白質 (g)", 0, 300, key=f"prot_{day_key}")
                if prot >= target_protein: st.caption("✅ 蛋白質達標！")
                
                # 優化筆記提示：強調漸進式負荷
                note = st.text_area("訓練筆記 (請記錄重量與次數，例如: 划船 15kg)", value=data['history'].get(day_key, {}).get('note', ''))
                
                if st.form_submit_button("✅ 完成並打卡"):
                    data['history'][day_key] = {"completed": True, "date": str(today), "note": note, "protein": prot}
                    save_data(sheet, data)
                    st.success(f"{day_name} 訓練完成！")
                    st.rerun()
        else:
            st.info("非訓練日")

    with tab2:
        st.markdown("### 📋 本月課表總覽")
        schedule_list = []
        days_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for w in range(1, 5):
            for d_idx, d_name in enumerate(days_short):
                key = f"W{w}-{d_name}"
                
                code = ""
                if d_idx == 0 or d_idx == 3: code = "Chest"
                elif d_idx == 1 or d_idx == 5: code = "Cardio"
                elif d_idx == 4: code = "Legs"
                elif d_idx == 2 or d_idx == 6: code = "Back"
                
                mod_name = MODULES[code]['Name']
                status = "✅" if data['history'].get(key, {}).get('completed') else "⬜"
                
                schedule_list.append({
                    "週次": f"Week {w}", 
                    "星期": d_name, 
                    "內容": mod_name.split(": ")[-1] if ": " in mod_name else mod_name,
                    "狀態": status
                })
        
        st.dataframe(pd.DataFrame(schedule_list), height=600, use_container_width=True)

if __name__ == "__main__":
    main()
