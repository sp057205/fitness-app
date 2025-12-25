import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 頁面設定 ---
st.set_page_config(page_title="30-Day Elite Cloud App", page_icon="☁️", layout="centered")

# ==========================================
# ☁️ Google Sheets 連線設定 (雲端版核心)
# ==========================================
def get_google_sheet_data():
    # 定義範圍
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 從 Streamlit Secrets 讀取憑證 (這是雲端安全的關鍵)
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # 開啟試算表 (名稱必須與你建立的一模一樣)
    try:
        sheet = client.open("fitness_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"找不到試算表！請確認：\n1. Google Sheet 名稱是否為 'fitness_db'\n2. 是否已共用給機器人 Email\n錯誤訊息: {e}")
        st.stop()

# --- 讀取與儲存邏輯 (改為讀寫雲端) ---
def load_data(sheet):
    try:
        # 嘗試讀取第一格，如果是空的代表是新表
        data_str = sheet.cell(1, 1).value
        if not data_str:
            # 初始化數據
            return {"current_day": 1, "start_date": "2025-12-29", "weight": 70, "history": {}}
        return json.loads(data_str)
    except:
        return {"current_day": 1, "start_date": "2025-12-29", "weight": 70, "history": {}}

def save_data(sheet, data):
    # 將整包數據轉為 JSON 字串存入 A1 格子 (簡單粗暴但有效)
    sheet.update_cell(1, 1, json.dumps(data))

# ==========================================
# 💀 訓練課表 (維持 V3.0)
# ==========================================
MODULES = {
    "A": {
        "Name": "🔹 Module A: 背部毀滅 (Back & Pull)",
        "Focus": "絕對力量與背部寬度",
        "Exercises": [
            {"name": "單槓: 離心引體向上", "reps": "4組 x 6-8次", "video": "https://www.youtube.com/results?search_query=negative+pull+ups", "note": "下放6秒，抵抗地心引力"},
            {"name": "壺鈴/啞鈴: 單臂划船", "reps": "4組 x 10次/邊", "video": "https://www.youtube.com/results?search_query=kettlebell+single+arm+row", "note": "重量重一點"},
            {"name": "彈力帶/單槓: 澳洲式引體", "reps": "3組 x 力竭", "video": "https://www.youtube.com/results?search_query=australian+pull+ups", "note": "身體平行地面"},
            {"name": "彈力帶: 面拉 (Face Pulls)", "reps": "4組 x 20次", "video": "https://www.youtube.com/results?search_query=band+face+pulls", "note": "改善圓肩必做"},
            {"name": "跳繩: 快速燃燒", "reps": "連續 500 下", "video": "https://www.youtube.com/results?search_query=jump+rope+basic", "note": "小腿肌耐力"}
        ]
    },
    "B": {
        "Name": "🔹 Module B: 3D肩膀 (Shoulders & Push)",
        "Focus": "打造倒三角",
        "Exercises": [
            {"name": "啞鈴/壺鈴: 站姿肩推", "reps": "4組 x 8-12次", "video": "https://www.youtube.com/results?search_query=dumbbell+standing+shoulder+press", "note": "核心收緊"},
            {"name": "啞鈴: 側平舉", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=dumbbell+lateral+raise+form", "note": "倒水姿勢，勿聳肩"},
            {"name": "標準/負重伏地挺身", "reps": "4組 x 力竭", "video": "https://www.youtube.com/results?search_query=perfect+push+up", "note": "胸大肌充血"},
            {"name": "彈力帶: 擴胸拉開", "reps": "3組 x 25次", "video": "https://www.youtube.com/results?search_query=band+pull+aparts", "note": "強化後肩"},
            {"name": "核心: 死蟲式", "reps": "3組", "video": "https://www.youtube.com/results?search_query=dead+bug+core", "note": "骨盆回正"}
        ]
    },
    "C": {
        "Name": "🔹 Module C: 腿部 & VO2 Max",
        "Focus": "臀橋啟動 + 心肺地獄",
        "Exercises": [
            {"name": "壺鈴: 擺盪 (Swings)", "reps": "5組 x 20次", "video": "https://www.youtube.com/results?search_query=russian+kettlebell+swing", "note": "屁股發力，燃脂"},
            {"name": "啞鈴/壺鈴: 酒杯深蹲", "reps": "4組 x 15次", "video": "https://www.youtube.com/results?search_query=goblet+squat", "note": "蹲深"},
            {"name": "🔥 負重臀橋", "reps": "4組 x 15-20次", "video": "https://www.youtube.com/results?search_query=dumbbell+glute+bridge", "note": "頂峰停1秒，夾爆屁股"},
            {"name": "啞鈴: 弓箭步走", "reps": "3組 x 20步", "video": "https://www.youtube.com/results?search_query=dumbbell+walking+lunges", "note": "練腿也練握力"},
            {"name": "⚡ TABATA 跳繩", "reps": "4分鐘 (20秒衝/10秒休)", "video": "https://www.youtube.com/results?search_query=tabata+jump+rope", "note": "全力衝刺"}
        ]
    },
    "Rest": {
        "Name": "🛌 週二固定休息日",
        "Focus": "恢復 & 補劑",
        "Exercises": [
            {"name": "完全休息", "reps": "Relax", "video": "", "note": "放鬆神經"},
            {"name": "滾筒放鬆", "reps": "20 min", "video": "https://www.youtube.com/results?search_query=full+body+foam+rolling", "note": "針對緊繃處"},
            {"name": "補鎂 & 睡眠", "reps": "8 hrs", "video": "", "note": "睡前鎂"}
        ]
    }
}

SCHEDULE = ["A", "Rest", "B", "C", "A", "B", "C"] * 4 + ["A", "Final"]

# ==========================================
# 🚀 APP 主程式
# ==========================================
def main():
    st.markdown("""<style>.stProgress > div > div > div > div { background-color: #00CC96; } .big-stat { font-size: 24px; font-weight: bold; color: #00CC96; } .supplement-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; }</style>""", unsafe_allow_html=True)
    st.title("🔥 30-Day Elite Cloud App")
    
    # 連線雲端
    sheet = get_google_sheet_data()
    data = load_data(sheet)

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ 個人設定")
        try: saved_start = datetime.datetime.strptime(data.get('start_date', '2025-12-29'), "%Y-%m-%d").date()
        except: saved_start = datetime.date(2025, 12, 29)
        start_date = st.date_input("開始日期", value=saved_start)
        data['start_date'] = str(start_date)
        
        weight = st.number_input("體重 (kg)", value=data.get('weight', 70))
        data['weight'] = weight
        target_protein = int(weight * 2.0)
        
        st.markdown(f"""<div class="supplement-box"><b>🥩 每日蛋白質目標</b><br><span class="big-stat">{target_protein} g</span></div>""", unsafe_allow_html=True)
        
        completed = len([k for k,v in data['history'].items() if v.get('completed')])
        st.progress(completed / 30)
        st.write(f"進度: {completed} / 30 天")
        
        if st.button("🔴 重置紀錄 (慎點)"):
            sheet.update_cell(1, 1, "") # 清空格子
            st.rerun()

    # --- Main ---
    tab1, tab2 = st.tabs(["🚀 今日任務", "📅 完整日曆"])
    with tab1:
        day = st.number_input("Day", 1, 30, data['current_day'])
        current_date = start_date + timedelta(days=day-1)
        st.markdown(f"### 📅 {current_date.strftime('%Y-%m-%d (%a)')}")
        
        if day == 30:
            st.success("🏆 最終驗收日！")
            if st.button("挑戰完成！"): st.balloons()
        else:
            code = SCHEDULE[day-1] if day <= 29 else "Final"
            module = MODULES[code]
            if code == "Rest": st.success(f"🍃 {module['Name']}")
            else: st.error(f"🔥 {module['Name']}")

            with st.form(f"form_{day}"):
                for ex in module['Exercises']:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{ex['name']}**")
                        if ex['note']: st.caption(f"💡 {ex['note']}")
                        if ex['video']: st.link_button("📺 教學", ex['video'])
                    with c2: st.markdown(f"**{ex['reps']}**")
                    st.divider()
                
                st.markdown("#### 💊 補劑打卡")
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
                    if day == data['current_day'] and day < 30: data['current_day'] += 1
                    save_data(sheet, data) # 存回雲端
                    st.success("已同步至 Google Sheets！")
                    st.rerun()

    with tab2:
        schedule_data = []
        for i in range(1, 31):
            d = start_date + timedelta(days=i-1)
            c = SCHEDULE[i-1] if i <= 29 else "FINAL"
            status = "✅ 完成" if data['history'].get(str(i), {}).get('completed') else "未完成"
            schedule_data.append({"Day": f"Day {i}", "Date": d.strftime("%m/%d"), "Module": c, "Status": status})
        st.dataframe(pd.DataFrame(schedule_data), height=500, use_container_width=True)

if __name__ == "__main__":
    main()