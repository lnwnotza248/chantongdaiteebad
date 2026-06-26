from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ===================================================================
# 1. หน้าแรก (ยึดตามซอร์สโค้ดจริงที่คุณส่งมา 100%)
# ===================================================================
@app.route('/')
def index():
    return '''
    <!DOCTYPE html><html lang="th"><head>    <meta charset="UTF-8">    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <title>ระบบจองสนามมหาวิทยาลัยศิลปากรวิทยาเขตสนามจันทร์</title>    <style>        body {            font-family: Arial, sans-serif;            text-align: center;            margin: 50px;        }        h1 {            color: #2c3e50;        }        a {            display: inline-block;            margin: 20px;            padding: 10px 20px;            background-color: #3498db;            color: white;            text-decoration: none;            border-radius: 5px;        }        a:hover {            background-color: #2980b9;        }    </style></head><body>    <h1>ยินดีต้อนรับเข้าสู่ระบบจองเวลาเข้าใช้งานสนาม</h1>    <a href="booking.php">จองเวลาใช้งาน</a>    <a href="register.php">ลงทะเบียนเพื่อเข้าใช้งาน</a>    <a href="reservations.php">ตรวจสอบรายชื่อผู้จอง</a></body></html>
    '''

# ===================================================================
# 2. หน้าล็อกอินดักหน้า (จำลองพฤติกรรมเมื่อกดปุ่ม "จองเวลาใช้งาน")
# ===================================================================
@app.route('/booking.php', methods=['GET'])
def booking_gate():
    return '''
    <!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><title>เข้าสู่ระบบ</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; margin-top: 100px; }
        form { background: white; padding: 30px; border-radius: 8px; display: inline-block; max-width: 320px; margin: 0 auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"], input[type="password"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { width: 97%; padding: 10px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
    </head><body>
        <h2>กรุณาเข้าสู่ระบบก่อนจองสนาม</h2>
        <form action="/login_process" method="POST">
            <input type="text" name="username" placeholder="รหัสนักศึกษา" required><br>
            <input type="password" name="password" placeholder="รหัสผ่าน" required><br>
            <input type="submit" value="เข้าสู่ระบบ">
        </form>
    </body></html>
    '''

@app.route('/login_process', methods=['POST'])
def login_process():
    # เมื่อล็อกอินผ่าน ให้ดีดตัวไปที่หน้าจองสนามหลัก
    return '<script>window.location.href="/booking_main";</script>'

# ===================================================================
# 3. หน้าจองสนามหลัก (แก้ไขตัวสแลชหน้า URL ของ AJAX แล้ว เวลาจะแสดงปกติ)
# ===================================================================
@app.route('/booking_main')
def booking_main():
    return '''
    <!DOCTYPE html><html lang="th"><head>    <meta charset="UTF-8">    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <title>จองสนาม</title>    <style>        body {            font-family: Arial, sans-serif;            background-color: #f4f4f4;            margin: 0;            padding: 20px;        }        h2 {            text-align: center;            color: #333;        }        form {            background-color: white;            padding: 20px;            border-radius: 8px;            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);            max-width: 400px;            margin: 0 auto;        }        label {            display: block;            margin-bottom: 5px;            color: #555;        }        select {            width: 100%;            padding: 10px;            margin-bottom: 15px;            border: 1px solid #ccc;            border-radius: 4px;        }        input[type="submit"] {            width: 100%;            padding: 10px;            background-color: #3498db;            color: white;            border: none;            border-radius: 4px;            cursor: pointer;            font-size: 16px;        }        input[type="submit"]:hover {            background-color: #2980b9;        }        .logout-link {            display: block;            text-align: center;            margin-top: 20px;            color: #3498db;            text-decoration: none;        }        .cnote {            display: block;            text-align: center;            margin-top: 20px;            color: #5f0014;            text-decoration: none;        }
        .logout-link:hover {            text-decoration: underline;        }    </style>
        
    <script>
        function updateAvailableTimes() {
            const courtSelect = document.getElementById('court');
            const timeSelect = document.getElementById('time');
            const selectedCourt = courtSelect.value;

            // ส่งคำขอ AJAX ไปที่ /get_reserved_times.php (เติมสแลชนำหน้าเพื่อให้ Flask ค้นหาเจอ)
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/get_reserved_times.php', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const reservedTimes = JSON.parse(xhr.responseText);
                    timeSelect.innerHTML = ''; // ล้างตัวเลือกเวลาเก่าออก
                    
                    const availableTimes = [ '17:00_18:00','18:00_19:00', '19:00_20:00', '20:00_21:00', '21:00_22:00'];
                    availableTimes.forEach(time => {
                        if (!reservedTimes.includes(time)) {
                            const option = document.createElement('option');
                            option.value = time;
                            option.textContent = time;
                            timeSelect.appendChild(option);
                        }
                    });
                }
            };
            xhr.send('court_id=' + selectedCourt + '&date=2026-06-26');
        }
    </script>
    </head><body>
    <h2>จองสนาม</h2>
    <form action="/book_court.php" method="POST">
        <label for="court">เลือกสนาม:</label>
        <select id="court" name="court" required onchange="updateAvailableTimes()">
            <option value="">-- เลือกสนาม --</option>
            <option value="1">เทนนิส4</option>
            <option value="2">แบดมินตัน1</option>
            <option value="3">แบดมินตัน2</option>
            <option value="4">แบดมินตัน3</option>
            <option value="5">แบดมินตัน4</option>
            <option value="6">แบดมินตัน6</option>
        </select>
        <label for="time">เลือกเวลา:</label>
        <select id="time" name="time" required>
            <option value="">-- กรุณาเลือกสนามก่อน --</option>
        </select>
        <input type="submit" value="จอง">
    </form>
    <a href="logout.php" class="logout-link">ออกจากระบบ</a>
    <a href="reservations.php" class="logout-link">ดูเวลาที่มีการจอง</a>
    <a class="cnote">ระเบียบการจองสนามกีฬา </a>
    <a class="cnote">1.เริ่มการลงจองสนามได้ตั้งแต่เวลา 12:00 น. ของแต่ละวัน เป็นต้นไป และจะทำการล้างข้อมูลการจองทั้งหมดออกในเวลา 12:00 น.ในวันถัดไป</a>
    <a class="cnote">2.ผู้ที่ลงทะเบียนแต่ละคนสามารถจองได้ 1 ครั้งต่อวันเท่านั้น</a>
    <a class="cnote">3.หากพบปัญหาการจองซ้ำซ้อนในคอร์ดและเวลาเดียวกัน ระบบจะให้สิทธิ์ผู้ที่ยืนยันเวลาจองก่อน และจะลบข้อมูลของผู้จองที่ซ้ำซ้อนที่เหลือออก</a>
    <a class="cnote">4.หากพบปัญหาสามารถแจ้งได้ทาง Line OpenChat</a>
</body></html>
    '''

# ===================================================================
# 4. หลังบ้านจำลอง (ส่งค่าเวลาว่างกลับไปให้ AJAX)
# ===================================================================
@app.route('/get_reserved_times.php', methods=['POST'])
def get_reserved_times():
    # ดูว่าหน้าบ้านส่งคำขอเช็คของสนามรหัสอะไรมา
    court_id = request.form.get('court_id')
    
    # 🏸 รหัส "2" คือ แบดมินตัน1
    # ถ้าหน้าบ้านเลือกแบดมินตัน 1 ให้ส่งรอบเวลาไป "ครบทุกรอบ" เพื่อจำลองว่าสนามนี้โดนจองเต็มหมดแล้ว
    if court_id in ["2", "3", "4", "5", "6"]:
        return jsonify(['17:00_18:00', '18:00_19:00'])
        
    # ส่วนสนามอื่นๆ (เทนนิส และ แบด 2, 3, 4, 6) ปล่อยให้ว่างทุกรอบตามปกติ บอตจะได้เลือกได้
    return jsonify([])

# ===================================================================
# 5. หน้าตอบรับเมื่อทำรายการส่งฟอร์มสำเร็จ
# ===================================================================
@app.route('/book_court.php', methods=['POST'])
def book_court():
    court = request.form.get('court')
    time_slot = request.form.get('time')
    
    court_dict = {"1": "เทนนิส4", "2": "แบดมินตัน1", "3": "แบดมินตัน2", "4": "แบดมินตัน3", "5": "แบดมินตัน4", "6": "แบดมินตัน6"}
    court_name = court_dict.get(court, f"รหัส {court}")
    
    return f'''
    <html>
    <body style="text-align:center; font-family:Arial, sans-serif; margin-top:50px;">
        <h2 style="color: green;">🎉 ยินดีด้วย บอตของคุณทำรายการส่งฟอร์มสำเร็จ!</h2>
        <p><b>สนามที่จองได้:</b> {court_name}</p>
        <p><b>ช่วงเวลาที่ได้:</b> {time_slot}</p>
        <p style="color: gray; font-size: 13px;">(ข้อมูลถูกส่งเข้าสู่หน้าประมวลผล book_court.php เรียบร้อย)</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(port=5000, debug=True)