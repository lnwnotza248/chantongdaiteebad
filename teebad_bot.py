import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

print("==========================================================")
print("          SU Sport Badminton Bot (Terminal v2.1)          ")
print("==========================================================")

print("กรุณาเลือกโหมดการทำงานของบอต:")
print("1. [Test Mode] สำหรับทดสอบระบบตอนนี้ (ข้ามลูปเวลารอเที่ยงวัน)")
print("2. [Live Mode] สำหรับใช้ลงสนามจองจริง (ล็อกเวลารันที่ 12:00:00 น.)")

while True:
    mode_choice = input("👉 เลือกโหมด (พิมพ์เลข 1 หรือ 2): ").strip()
    if mode_choice in ["1", "2"]:
        break
    print("❌ พิมพ์ผิด! กรุณาพิมพ์เลข 1 หรือ 2 เท่านั้น")

IS_TEST_MODE = True if mode_choice == "1" else False
RUN_TIME = "ทำงานทันที (Test Mode)" if IS_TEST_MODE else "12:00:00"
t_hour, t_min, t_sec = 12, 0, 0

print("----------------------------------------------------------")
SU_USERNAME = input("👤 กรุณากรอกรหัสนักศึกษา: ").strip()
SU_PASSWORD = input("🔑 กรุณากรอกรหัสผ่าน: ").strip()

COURT_MAP = {"1": "แบดมินตัน1", "2": "แบดมินตัน2", "3": "แบดมินตัน3", "4": "แบดมินตัน4", "6": "แบดมินตัน6"}
TIME_MAP = {"1": "17:00_18:00", "2": "18:00_19:00", "3": "19:00_20:00", "4": "20:00_21:00", "5": "21:00_22:00"}
ALL_TIME_TEXTS = list(TIME_MAP.values())
BACKEND_COURT_ID_MAP = {
    "แบดมินตัน1": "2",
    "แบดมินตัน2": "3",
    "แบดมินตัน3": "4",
    "แบดมินตัน4": "5",
    "แบดมินตัน6": "6"
}
ALL_COURTS = ["แบดมินตัน1", "แบดมินตัน2", "แบดมินตัน3", "แบดมินตัน4", "แบดมินตัน6"]

# --- เมนูเลือกสนาม ---
print("\n--- ตั้งค่าสนามเจาะจง (พิมพ์เลขสนามตรงตัว) ---")
print("1. แบดมินตัน1\n2. แบดมินตัน2\n3. แบดมินตัน3\n4. แบดมินตัน4\n6. แบดมินตัน6")
print("** หากต้องการให้เลือกอัตโนมัติ ให้กด [Enter] ข้ามไปได้เลย **")

while True:
    court_choice = input("🎯 เลือกสนาม (พิมพ์เลข 1, 2, 3, 4, 6 หรือกด Enter ข้าม): ").strip()
    if court_choice == "":
        TARGET_COURT_NAME = ""
        break
    elif court_choice in COURT_MAP:
        TARGET_COURT_NAME = COURT_MAP[court_choice]
        break
    print("❌ ไม่มีสนามนี้ในระบบ! กรุณาพิมพ์เลข 1, 2, 3, 4 หรือ 6 เท่านั้น")

# --- เมนูเลือกเวลา ---
print("\n--- ตั้งค่าช่วงเวลาเจาะจง (พิมพ์ตัวเลขรอบเวลา) ---")
print("1. รอบเวลา 17:00_18:00\n2. รอบเวลา 18:00_19:00\n3. รอบเวลา 19:00_20:00\n4. รอบเวลา 20:00_21:00\n5. รอบเวลา 21:00_22:00")
print("** หากต้องการให้เลือกอัตโนมัติ ให้กด [Enter] ข้ามไปได้เลย **")

while True:
    time_choice = input("⏳ เลือกช่วงเวลา (พิมพ์เลข 1-5 หรือกด Enter ข้าม): ").strip()
    if time_choice == "":
        TARGET_TIME_TEXT = ""
        break
    elif time_choice in TIME_MAP:
        TARGET_TIME_TEXT = TIME_MAP[time_choice]
        break
    print("❌ ช่วงเวลาไม่ถูกต้อง! กรุณาพิมพ์เลข 1 ถึง 5 หรือกด Enter เท่านั้น")

# ===================================================================
# 🧠 ระบบตรวจสอบเงื่อนไขล่วงหน้า + เรียงคิวสำรองแบบกำหนดเอง
# ===================================================================
USER_ALLOW_BACKUP = "no"
CUSTOM_COURT_QUEUE = []
CUSTOM_TIME_QUEUE = []
CUSTOM_PAIR_QUEUE = []

if TARGET_COURT_NAME == "" and TARGET_TIME_TEXT == "":
    CURRENT_CASE = "CASE_1"
elif TARGET_COURT_NAME != "" and TARGET_TIME_TEXT == "":
    CURRENT_CASE = "CASE_2"
    while True:
        choice = input("\n❓ ถ้าสนามที่เลือกเต็ม จะยอมให้บอทสลับไปเลือกสนามอื่นที่ว่างไหม? (y/n): ").strip().lower()
        if choice in ["y", "n"]:
            USER_ALLOW_BACKUP = "yes" if choice == "y" else "no"
            break
        print("❌ กรุณาตอบ y หรือ n เท่านั้น")
    
    if USER_ALLOW_BACKUP == "yes":
        print("\n📝 กรุณาระบุลำดับสนามสำรองที่ต้องการให้บอทไปหา (พิมพ์เลขสนาม 4 ตัวติดกันโดยห้ามซ้ำกับสนามหลัก)")
        print("ดัชนีสนามที่ป้อนได้คือเลข: 1, 2, 3, 4, 6 (ตัวอย่างเช่น พิมพ์ '6432')")
        while True:
            q_input = input("👉 ระบุลำดับสนามสำรอง (เลข 4 ตัว): ").strip()
            if len(q_input) == 4 and q_input.isdigit():
                valid = True
                temp_queue = []
                for ch in q_input:
                    if ch in COURT_MAP and COURT_MAP[ch] != TARGET_COURT_NAME and COURT_MAP[ch] not in temp_queue:
                        temp_queue.append(COURT_MAP[ch])
                    else:
                        valid = False
                if valid:
                    CUSTOM_COURT_QUEUE = temp_queue
                    break
            print("❌ พิมพ์ไม่ถูกต้อง! ต้องมีเลขสนาม 4 ตัวจากกลุ่ม (1,2,3,4,6) ไม่ซ้ำกัน และไม่ซ้ำกับสนามหลัก")

elif TARGET_COURT_NAME == "" and TARGET_TIME_TEXT != "":
    CURRENT_CASE = "CASE_3"
    while True:
        choice = input("\n❓ ถ้าเวลาที่เลือกในทุกสนามเต็ม จะยอมให้บอทสลับไปเลือกเวลาอื่นไหม? (y/n): ").strip().lower()
        if choice in ["y", "n"]:
            USER_ALLOW_BACKUP = "yes" if choice == "y" else "no"
            break
        print("❌ กรุณาตอบ y หรือ n เท่านั้น")
        
    if USER_ALLOW_BACKUP == "yes":
        print("\n📝 กรุณาระบุลำดับเวลาสำรองที่ต้องการให้บอทไปหา (พิมพ์เลขช่วงเวลา 4 ตัวติดกันโดยห้ามซ้ำกับเวลาหลัก)")
        while True:
            q_input = input("👉 ระบุลำดับเวลาสำรอง (เลข 4 ตัว เช่น 2345): ").strip()
            if len(q_input) == 4 and q_input.isdigit():
                valid = True
                temp_queue = []
                for ch in q_input:
                    if ch in TIME_MAP and TIME_MAP[ch] != TARGET_TIME_TEXT and TIME_MAP[ch] not in temp_queue:
                        temp_queue.append(TIME_MAP[ch])
                    else:
                        valid = False
                if valid:
                    CUSTOM_TIME_QUEUE = temp_queue
                    break
            print("❌ พิมพ์ไม่ถูกต้อง! ต้องมีเลขช่วงเวลา 4 ตัว ไม่ซ้ำกัน และไม่ซ้ำกับเวลาหลัก")

else:
    CURRENT_CASE = "CASE_4"
    while True:
        choice = input("\n❓ ถ้าสนามและเวลาที่เลือกเต็ม จะยอมให้บอทสลับไปเลือกอันอื่นที่ว่างไหม? (y/n): ").strip().lower()
        if choice in ["y", "n"]:
            USER_ALLOW_BACKUP = "yes" if choice == "y" else "no"
            break
        print("❌ กรุณาตอบ y หรือ n เท่านั้น")
        
    if USER_ALLOW_BACKUP == "yes":
        print("\n📝 กรุณาระบุโอกาสสำรองแบบจับคู่ (พิมพ์เลขสนามคู่กับเลขเวลา เช่น '62' = สนาม6 เวลา2)")
        print("พิมพ์ป้อนทีละคู่แล้วกด [Enter] และเมื่อต้องการหยุดลิสต์ ให้พิมพ์เลข '0' แล้วกด Enter")
        while True:
            pair_input = input(f"👉 ระบุโอกาสสำรองคู่ที่ {len(CUSTOM_PAIR_QUEUE) + 1} (หรือพิมพ์ 0 เพื่อหยุด): ").strip()
            if pair_input == "0":
                if len(CUSTOM_PAIR_QUEUE) == 0:
                    print("⚠️ ต้องระบุโอกาสสำรองอย่างน้อย 1 คู่ หรือถ้าไม่ต้องการแผนอื่น ให้ตอบ 'n' ตั้งแต่แรก")
                    continue
                break
            if len(pair_input) == 2 and pair_input.isdigit():
                c_ch, t_ch = pair_input[0], pair_input[1]
                if c_ch in COURT_MAP and t_ch in TIME_MAP:
                    c_name = COURT_MAP[c_ch]
                    t_text = TIME_MAP[t_ch]
                    if (c_name == TARGET_COURT_NAME and t_text == TARGET_TIME_TEXT):
                        print("❌ คู่สำรองนี้ซ้ำกับคู่หลักที่คุณเลือกไปตอนแรกแล้ว!")
                        continue
                    if (c_name, t_text) not in CUSTOM_PAIR_QUEUE:
                        CUSTOM_PAIR_QUEUE.append((c_name, t_text))
                        print(f"   [บันทึกแผนสำรอง]: {c_name} รอบ {t_text}")
                        continue
            print("❌ รูปแบบผิด! ต้องพิมพ์เลข 2 ตัว (เลขสนาม 1,2,3,4,6 ตามด้วยเลขเวลา 1-5) เช่น 62")

print("==========================================================")
print(f"บันทึกสถานะ: โหมด [{CURRENT_CASE}]")
print(f"สนามหลัก: {TARGET_COURT_NAME if TARGET_COURT_NAME else 'อัตโนมัติ'}")
print(f"รอบเวลาหลัก: {TARGET_TIME_TEXT if TARGET_TIME_TEXT else 'อัตโนมัติ'}")
print("==========================================================")

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_experimental_option("detach", False)

URL_TARGET = "http://127.0.0.1:5000/" if IS_TEST_MODE else "https://susport.sc.su.ac.th/"
driver = webdriver.Chrome(options=options)
log(f"เปิด Chrome Browser สำเร็จ -> {URL_TARGET}")

try:
    driver.get(URL_TARGET)
    wait = WebDriverWait(driver, 15)
    
    # 1. ล็อกอิน
    login_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'จองเวลาใช้งาน') or contains(text(), 'เข้าสู่ระบบ')]")))
    login_nav.click()
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(SU_USERNAME)
    password_field.send_keys(SU_PASSWORD)
    login_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='เข้าสู่ระบบ']")))
    driver.execute_script("arguments[0].click();", login_btn)
    log("ล็อกอินเสสิ้น")
    
    # 2. ระบบหน่วงเวลานาฬิกาเวอร์ชันกิน CPU ต่ำ
    if not IS_TEST_MODE:
        log(f"⏰ [Live Mode] กำลังรอนาฬิกาแตะเวลาเที่ยงวัน: {RUN_TIME} น. ...")
        while True:
            now = datetime.now()
            if now.hour == t_hour and now.minute == t_min and now.second == t_sec:
                log("[!!!] ถึงเวลาเที่ยงวันแล้ว! รีเฟรชหน้าเว็บทันที")
                driver.refresh()
                break
            time.sleep(0.02) # เร่งความถี่การตรวจเพื่อรีเฟรชให้ใกล้เคียงเวลาเที่ยงวันที่สุด
    else:
        log("🚀 [Test Mode] ข้ามระบบเวลารอ เริ่มต้นหาคอร์ททันที...")

    final_court = None
    final_time = None
    stop_reason = ""

    # 🔒 ฟังก์ชันเช็คตารางเวลาเวอร์ชันสยบ AJAX Race Condition และขจัดค่า Placeholder บั๊ก
    def get_time_dropdown(timeout=0.75):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                dropdown = Select(driver.find_element(By.ID, "time"))
                if len(dropdown.options) >= 1:
                    return dropdown
            except Exception:
                pass
            time.sleep(0.02)
        return None

    def check_and_get_time(target_time_str=None):
        t_dropdown = get_time_dropdown(timeout=0.75)
        if not t_dropdown:
            return None

        # ถ้ารอบเวลามีตัวเลือกเดียว และตัวเลือกนั้นไม่มีค่า value (เช่น ป้ายเตือนว่าเต็ม หรือข้อความกรุณาเลือกสนาม)
        if len(t_dropdown.options) == 1 and t_dropdown.options[0].get_attribute('value') == "":
            return None
            
        # วนลูปสแกนหาเวลาจริงที่เปิดให้กดจอง
        if target_time_str:
            for opt in t_dropdown.options:
                if opt.text == target_time_str and opt.get_attribute('value') != "":
                    return opt.text
            return None
        else:
            for opt in t_dropdown.options:
                if opt.get_attribute('value') != "":
                    return opt.text
            return None

    def fetch_reserved_times(court_id, date_text=None):
        if not date_text:
            date_text = datetime.now().strftime("%Y-%m-%d")
        try:
            result = driver.execute_async_script(
                "const courtId = arguments[0]; const date = arguments[1]; const callback = arguments[arguments.length - 1];"
                "fetch('/get_reserved_times.php', {"
                "method: 'POST',"
                "headers: {'Content-Type': 'application/x-www-form-urlencoded'},"
                "body: 'court_id=' + encodeURIComponent(courtId) + '&date=' + encodeURIComponent(date)"
                "})"
                ".then(resp => resp.json())"
                ".then(data => callback({status: 'ok', data: data}))"
                ".catch(err => callback({status: 'error', message: err.toString()}));",
                court_id, date_text
            )
            if isinstance(result, dict) and result.get('status') == 'ok' and isinstance(result.get('data'), list):
                return result['data']
        except Exception:
            pass
        return None

    def is_available(court_name, time_text):
        court_id = BACKEND_COURT_ID_MAP.get(court_name)
        if not court_id:
            return None
        reserved = fetch_reserved_times(court_id)
        if reserved is None:
            return None
        return time_text not in reserved

    def find_first_available(courts=None, target_time_str=None):
        if courts is None:
            courts = ALL_COURTS
        for court in courts:
            court_id = BACKEND_COURT_ID_MAP.get(court)
            if not court_id:
                continue
            reserved = fetch_reserved_times(court_id)
            if reserved is None:
                continue
            if target_time_str:
                if target_time_str not in reserved:
                    return court, target_time_str
            else:
                for time_text in ALL_TIME_TEXTS:
                    if time_text not in reserved:
                        return court, time_text
        return None, None

    # --- ลูปประมวลผลการจอง (CASE 1 - 4) ---
    if CURRENT_CASE == "CASE_1":
        for court in ALL_COURTS:
            Select(driver.find_element(By.ID, "court")).select_by_visible_text(court)
            try:
                found_time = check_and_get_time()
            except:
                found_time = None
            if found_time:
                final_court = court
                final_time = found_time
                break
            log(f"❌ {court} เต็มแล้ว... ข้ามไปเช็คสนามถัดไป")
        if not final_court:
            stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"

    elif CURRENT_CASE == "CASE_2":
        try:
            Select(driver.find_element(By.ID, "court")).select_by_visible_text(TARGET_COURT_NAME)
            found_time = check_and_get_time()
        except:
            found_time = None

        if found_time:
            final_court = TARGET_COURT_NAME
            final_time = found_time
        else:
            if USER_ALLOW_BACKUP == "yes":
                log(f"⚠️ {TARGET_COURT_NAME} เต็ม! ตรวจสอบตามคิวสำรอง: {CUSTOM_COURT_QUEUE}")
                for court in CUSTOM_COURT_QUEUE:
                    Select(driver.find_element(By.ID, "court")).select_by_visible_text(court)
                    try: found_time = check_and_get_time()
                    except: found_time = None
                    if found_time:
                        final_court = court
                        final_time = found_time
                        break
                    log(f"❌ {court} เต็มแล้ว...")
                if not final_court:
                    stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"
            else:
                stop_reason = "🚨 สนามที่เลือกเต็มหมดแล้ว วันหน้าค่อยตี"

    elif CURRENT_CASE == "CASE_3":
        for court in ALL_COURTS:
            Select(driver.find_element(By.ID, "court")).select_by_visible_text(court)
            try: found_time = check_and_get_time(TARGET_TIME_TEXT)
            except: found_time = None
            if found_time:
                final_court = court
                final_time = found_time
                break
        if not final_court:
            if USER_ALLOW_BACKUP == "yes":
                log(f"⚠️ เวลา {TARGET_TIME_TEXT} เต็มหมดทุกสนาม! ค้นหาตามคิวเวลาสำรอง")
                for time_text in CUSTOM_TIME_QUEUE:
                    for court in ALL_COURTS:
                        Select(driver.find_element(By.ID, "court")).select_by_visible_text(court)
                        try: found_time = check_and_get_time(time_text)
                        except: found_time = None
                        if found_time:
                            final_court = court
                            final_time = found_time
                            break
                    if final_court: break
                if not final_court:
                    stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"
            else:
                stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"

    elif CURRENT_CASE == "CASE_4":
        try:
            Select(driver.find_element(By.ID, "court")).select_by_visible_text(TARGET_COURT_NAME)
            found_time = check_and_get_time(TARGET_TIME_TEXT)
        except:
            found_time = None

        if found_time:
            final_court = TARGET_COURT_NAME
            final_time = found_time
        else:
            if USER_ALLOW_BACKUP == "yes":
                log("⚠️ สนามและเวลาหลักเต็ม! ไล่ตรวจตามลิสต์คู่อันดับสำรอง...")
                for b_court, b_time in CUSTOM_PAIR_QUEUE:
                    Select(driver.find_element(By.ID, "court")).select_by_visible_text(b_court)
                    try: found_time = check_and_get_time(b_time)
                    except: found_time = None
                    if found_time:
                        final_court = b_court
                        final_time = b_time
                        break
                    log(f"❌ คู่สำรอง [{b_court} | {b_time}] เต็มแล้ว...")
                if not final_court:
                    stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"
            else:
                stop_reason = "🚨 เต็มหมดแล้ว วันหน้าค่อยตี"

    # --- ส่งยืนยันปลายทางหากไม่ติดธงขัดข้อง ---
    if stop_reason != "":
        print(f"\n{stop_reason}")
    else:
        Select(driver.find_element(By.ID, "court")).select_by_visible_text(final_court)
        Select(driver.find_element(By.ID, "time")).select_by_visible_text(final_time)
        submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='จอง']")))
        driver.execute_script("arguments[0].click();", submit_btn)
        log(f"🎉 [SUCCESS] บอตส่งคำขอจองสำเร็จ! ล็อกคอร์ท: {final_court} | รอบเวลา: {final_time}")

except Exception as e:
    log(f"❌ บอตทำงานขัดข้องระหว่างประมวลผล: {e}")

# 🔒 บล็อกคำสั่งนิรภัยการันตีการปิดตัว 100% ป้องกันหน้าจอเบราว์เซอร์ลอยค้าง
finally:
    print("\n----------------------------------------------------------")
    print("[INFO] บอตสิ้นสุดขั้นตอนการรันคำสั่งทั้งหมดเรียบร้อยแล้ว")
    try:
        input("👉 กดปุ่ม [Enter] ในจอดำนี้เพื่อปิดหน้าต่าง Chrome และปิดโปรแกรม...")
    except:
        pass  # ป้องกันกรณีโดนตัดสัญญาณอินพุตกลางคัน (EOFError)
        
    try:
        driver.quit()
    except:
        pass
    print("ปิดระบบบอตเรียบร้อย")