import serial
import json
import threading
import time
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

#  KONFIGURASI PORT 
SERIAL_PORT = 'COM2' 
BAUD_RATE = 9600

sensor_data = {
    "suhu": 0.0,
    "kelembapan": 0.0,
    "kekeruhan": 0,
    "status_air": "-",
    "mode": "STANDBY",
    "alarm": False
}

def read_serial():
    global sensor_data
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Berhasil buka port {SERIAL_PORT}")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        sensor_data = json.loads(line)
                    except json.JSONDecodeError:
                        pass
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ Gagal: {e}")

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    return jsonify(sensor_data)


# HTML & CSS 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>P2HMBG - Mobile Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary: #2196F3;
            --primary-dark: #1e88e5;
            --bg-outer: #cbd5e1;
            --bg-app: #f4f7fc;
            --text: #1e293b;
            --muted: #64748b;
            --success: #10b981;
            --danger: #ef4444;
            --lcd-bg: #0d1e0d;
            --lcd-txt: #5af85a;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body { background-color: var(--bg-outer); display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; }

        /* BUNGKUSAN LAYAR HP LEBIH COMPACT (400px) */
        .mobile-container {
            width: 100%;
            max-width: 400px;
            background-color: var(--bg-app);
            min-height: 100vh;
            position: relative;
            box-shadow: 0 0 40px rgba(0,0,0,0.2); /* Efek bingkai HP di layar laptop */
            overflow-x: hidden;
            overflow-y: auto;
            padding-bottom: 60px; /* Jarak untuk bottom nav */
        }

        /* --- LOGIN SCREEN (Kini di dalam ukuran HP) --- */
        #login-screen { position: absolute; top: 0; left: 0; width: 100%; min-height: 100vh; background-color: #ffffff; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
        .login-logo { width: 110px; height: 110px; margin: 0 auto 15px auto; border-radius: 50%; overflow: hidden; border: 3px solid #e3f2fd; box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3); background-color: #ffffff; }
        .login-logo img { width: 100%; height: 100%; object-fit: cover; }
        .login-title { color: var(--primary); font-weight: 700; font-size: 18px; text-align: center; }
        .login-subtitle { color: var(--muted); font-weight: 500; font-size: 12px; margin-bottom: 25px; text-align: center; }
        .login-input { width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 13px; background-color: #f8fafc; margin-bottom: 15px; outline: none; }
        .btn-login { width: 100%; padding: 12px; background-color: var(--primary); color: white; border: none; border-radius: 15px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3); }

        /* --- HEADER APLIKASI (Di-press ukurannya) --- */
        .app-header { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 15px 20px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; position: sticky; top: 0; z-index: 50; box-shadow: 0 2px 10px rgba(0,0,0,0.1);}
        .app-header h1 { font-size: 16px; font-weight: 700; }
        .app-header p { font-size: 11px; opacity: 0.9; margin-top: 2px; }
        .mode-badge-top { display: inline-block; background: rgba(0,0,0,0.2); padding: 4px 10px; border-radius: 10px; font-size: 10px; font-weight: 700; margin-top: 8px; border: 1px solid rgba(255,255,255,0.1); }
        .clock-display { position: absolute; right: 15px; top: 15px; font-size: 10px; text-align: right; opacity: 0.8; }

        /* --- TAMPILAN VIEW --- */
        .view-section { display: none; padding: 12px; animation: fadeIn 0.2s; }
        .view-section.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* --- GRID KOTAK 2x2 (Makin Rapat) --- */
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
        .metric-card { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); text-align: center; border: 1px solid #f1f5f9; }
        .metric-card i { font-size: 16px; margin-bottom: 5px; color: var(--primary); }
        .metric-card.danger-card i { color: var(--danger); }
        .card-label { font-size: 10px; color: var(--muted); font-weight: 600; margin-bottom: 2px; }
        .card-value { font-size: 16px; font-weight: 700; color: var(--text); }
        .card-status { font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 8px; display: inline-block; margin-top: 3px; }
        .status-ok { background: #d1fae5; color: #065f46; }
        .status-bad { background: #fee2e2; color: #991b1b; }

        /* --- HARDWARE PANELS --- */
        .panel-box { background: white; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }
        .panel-title { font-size: 11px; font-weight: 700; color: var(--text); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
        
        /* LCD (Dikecilkan) */
        .lcd-screen { background-color: var(--lcd-bg); border: 3px solid #334155; border-radius: 6px; padding: 6px; width: 100%; overflow: hidden; }
        .lcd-line { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: var(--lcd-txt); letter-spacing: 1px; height: 14px; white-space: pre; text-shadow: 0 0 2px rgba(90, 248, 90, 0.8); }
        
        /* Aktuator LED */
        .actuator-item { display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 6px 10px; border-radius: 6px; margin-bottom: 5px; border: 1px solid #e2e8f0; }
        .actuator-info { display: flex; align-items: center; gap: 6px; font-size: 10px; font-weight: 600; }
        .pin-badge { background: #cbd5e1; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 9px; }
        .led-indicator { width: 10px; height: 10px; border-radius: 50%; background: #94a3b8; border: 2px solid #cbd5e1; }
        .led-indicator.active-blue { background: #3b82f6; border-color: #93c5fd; box-shadow: 0 0 6px #3b82f6; }
        .led-indicator.active-red { background: #ef4444; border-color: #fca5a5; box-shadow: 0 0 6px #ef4444; animation: blink 0.5s infinite; }

        @keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

        /* --- TABEL LOG --- */
        .table-wrapper { width: 100%; overflow-x: auto; }
        table { width: 100%; min-width: 350px; border-collapse: collapse; text-align: left; font-size: 10px; }
        th, td { padding: 6px 8px; border-bottom: 1px solid #f1f5f9; }
        th { background: #f8fafc; color: var(--muted); font-weight: 600; }
        
        /* --- BOTTOM NAVIGATION MENU --- */
        .bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 8px 0 10px 0; border-top: 1px solid #e2e8f0; border-top-left-radius: 15px; border-top-right-radius: 15px; box-shadow: 0 -4px 10px rgba(0,0,0,0.03); z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 2px; color: var(--muted); font-size: 9px; font-weight: 700; cursor: pointer; text-decoration: none; width: 20%; }
        .nav-item.active { color: var(--primary); }
        .nav-item i { font-size: 16px; }

        /* Gauges */
        .gauge-container { background: #e2e8f0; height: 10px; border-radius: 5px; width: 100%; margin-top: 8px; overflow: hidden; }
        .gauge-fill { height: 100%; transition: width 0.3s; }
        .g-limit { display: flex; justify-content: space-between; font-size: 8px; color: var(--muted); margin-top: 3px; }
    </style>
</head>
<body>

    <div class="mobile-container">

        <div id="login-screen">
            <div class="login-logo">
                <img src="/static/logo.png" alt="Logo P2HMBG" onerror="this.src='https://via.placeholder.com/150?text=LOGO';">
            </div>
            <div class="login-title">P2HMBG MOBILE</div>
            <div class="login-subtitle">Storage Safety Hub</div>
            <input type="text" id="username-input" class="login-input" placeholder="Masukkan Nama / Admin" autocomplete="off">
            <button class="btn-login" onclick="doLogin()">Masuk Aplikasi</button>
        </div>

        <div id="main-app" style="display: none;">
            <header class="app-header">
                <div class="clock-display" id="live-clock">00:00<br>2026</div>
                <p>Halo, <span id="header-name">Admin</span> 👋</p>
                <h1>P2HMBG Hub</h1>
                <div class="mode-badge-top" id="top-mode-badge">🔴 MENGHUBUNGKAN...</div>
            </header>

            <div id="dashboard-view" class="view-section active">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <i class="fa-solid fa-temperature-half"></i>
                        <p class="card-label">Suhu Aktif</p>
                        <div class="card-value" id="val-suhu">-- °C</div>
                        <div class="card-status status-ok" id="stat-suhu">Normal</div>
                    </div>
                    <div class="metric-card">
                        <i class="fa-solid fa-droplet"></i>
                        <p class="card-label">Kelembapan</p>
                        <div class="card-value" id="val-humid">-- %</div>
                        <div class="card-status status-ok">Normal</div>
                    </div>
                    <div class="metric-card">
                        <i class="fa-solid fa-faucet-drip"></i>
                        <p class="card-label">Kondisi Air</p>
                        <div class="card-value" id="val-air">--</div>
                        <div class="card-status status-ok" id="stat-air">Normal</div>
                    </div>
                    <div class="metric-card danger-card">
                        <i class="fa-solid fa-bullhorn"></i>
                        <p class="card-label">Alarm Fisik</p>
                        <div class="card-value" id="val-alarm">0</div>
                        <div class="card-status status-ok" id="stat-alarm">Aman</div>
                    </div>
                </div>

                <div class="panel-box">
                    <div class="panel-title"><i class="fa-solid fa-microchip"></i> LCD Output (Sinkron Wokwi)</div>
                    <div class="lcd-screen">
                        <div class="lcd-line" id="lcd-0">  SISTEM KONTROL  </div>
                        <div class="lcd-line" id="lcd-1">      P2HMBG      </div>
                        <div class="lcd-line" id="lcd-2">                  </div>
                        <div class="lcd-line" id="lcd-3">Menunggu Data...  </div>
                    </div>
                </div>

                <div class="panel-box">
                    <div class="panel-title"><i class="fa-solid fa-gears"></i> Hardware Aktuator</div>
                    <div class="actuator-item">
                        <div class="actuator-info"><span class="pin-badge">P-11</span> Kompresor</div>
                        <div class="led-indicator" id="led-kompresor"></div>
                    </div>
                    <div class="actuator-item">
                        <div class="actuator-info"><span class="pin-badge">P-06</span> Buzzer Alarm</div>
                        <div class="led-indicator" id="led-buzzer"></div>
                    </div>
                </div>
            </div>

            <div id="chiller-view" class="view-section">
                <div class="panel-box" style="border-top: 3px solid #2196F3;">
                    <div class="panel-title" style="color: #1e40af;"><i class="fa-solid fa-snowflake"></i> Chiller (Sayur)</div>
                    <p style="font-size: 10px; color: var(--muted); margin-bottom: 12px;">Target batas aman: 2.0°C - 8.0°C.</p>
                    
                    <div class="metrics-grid">
                        <div class="metric-card"><p class="card-label">Suhu</p><div class="card-value" style="color:#2196F3;" id="ch-suhu">-- °C</div></div>
                        <div class="metric-card"><p class="card-label">Humid</p><div class="card-value" id="ch-humid">-- %</div></div>
                    </div>
                    
                    <p style="font-size: 10px; font-weight: 600;">Level Suhu (0°C - 15°C)</p>
                    <div class="gauge-container"><div class="gauge-fill" id="ch-gauge" style="background:#2196F3; width:0%;"></div></div>
                    <div class="g-limit"><span>0°C</span><span>Batas Aman</span><span>15°C</span></div>
                </div>
            </div>

            <div id="freezer-view" class="view-section">
                <div class="panel-box" style="border-top: 3px solid #86198f;">
                    <div class="panel-title" style="color: #86198f;"><i class="fa-solid fa-temperature-empty"></i> Freezer Utama</div>
                    <p style="font-size: 10px; color: var(--muted); margin-bottom: 12px;">Target batas aman: -25.0°C s/d -15.0°C.</p>
                    
                    <div class="metrics-grid">
                        <div class="metric-card"><p class="card-label">Suhu</p><div class="card-value" style="color:#86198f;" id="fz-suhu">-- °C</div></div>
                        <div class="metric-card"><p class="card-label">Humid</p><div class="card-value" id="fz-humid">-- %</div></div>
                    </div>
                    
                    <p style="font-size: 10px; font-weight: 600;">Level Suhu (-30°C s/d 0°C)</p>
                    <div class="gauge-container"><div class="gauge-fill" id="fz-gauge" style="background:#86198f; width:0%;"></div></div>
                    <div class="g-limit"><span>-30°C</span><span>Batas Aman</span><span>0°C</span></div>
                </div>
            </div>

            <div id="history-view" class="view-section">
                <div class="panel-box">
                    <div class="panel-title"><i class="fa-solid fa-list-check"></i> Log Data (Realtime)</div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>Waktu</th><th>Mode</th><th>Suhu</th><th>Air</th><th>Stat</th></tr></thead>
                            <tbody id="log-table-body"></tbody>
                        </table>
                    </div>
                </div>
                
                <div class="panel-box" style="border-top: 3px solid var(--danger);">
                    <div class="panel-title" style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Log Peringatan</div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>Waktu</th><th>Masalah</th></tr></thead>
                            <tbody id="alert-table-body">
                                <tr><td colspan="2" style="text-align:center;">Sistem Terpantau Aman</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <nav class="bottom-nav">
                <a class="nav-item active" data-target="dashboard"><i class="fa-solid fa-house"></i>Home</a>
                <a class="nav-item" data-target="chiller"><i class="fa-solid fa-snowflake"></i>Chiller</a>
                <a class="nav-item" data-target="freezer"><i class="fa-solid fa-temperature-empty"></i>Freezer</a>
                <a class="nav-item" data-target="history"><i class="fa-solid fa-clock-rotate-left"></i>Riwayat</a>
                <a class="nav-item" onclick="doLogout()"><i class="fa-solid fa-right-from-bracket"></i>Keluar</a>
            </nav>
        </div>
    </div>

    <script>
        let isFirstData = true;

        function doLogin() {
            const uname = document.getElementById("username-input").value.trim() || "Admin";
            document.getElementById("header-name").innerText = uname;
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-app").style.display = "block";
        }

        function doLogout() {
            document.getElementById("main-app").style.display = "none";
            document.getElementById("login-screen").style.display = "flex";
            document.getElementById("username-input").value = "";
            document.querySelector('.nav-item[data-target="dashboard"]').click();
        }

        document.querySelectorAll('.nav-item[data-target]').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
                document.getElementById(this.getAttribute('data-target') + '-view').classList.add('active');
            });
        });

        setInterval(() => {
            const now = new Date();
            document.getElementById("live-clock").innerHTML = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + "<br>" + now.toLocaleDateString('id-ID', {day:'numeric', month:'short'});
        }, 1000);

        setInterval(() => {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    let mode = data.mode;
                    let suhu = data.suhu;
                    let humid = data.kelembapan;
                    let ldr = data.kekeruhan;
                    let air = data.status_air;
                    let alarmTotal = data.alarm;

                    let alarmSuhu = false;
                    let kompresor = false;
                    let alarmAir = (air === "KOTOR" && mode !== "STANDBY");

                    if (mode === "CHILLER") {
                        if (suhu > 2.0) kompresor = true;
                        if (suhu < 2.0 || suhu > 8.0) alarmSuhu = true;
                    } else if (mode === "FREEZER") {
                        if (suhu > -25.0) kompresor = true;
                        if (suhu < -25.0 || suhu > -15.0) alarmSuhu = true;
                    }

                    const topBadge = document.getElementById("top-mode-badge");
                    if (mode === "CHILLER") { topBadge.innerHTML = "🟢 CHILLER AKTIF"; topBadge.style.background = "#059669"; }
                    else if (mode === "FREEZER") { topBadge.innerHTML = "🔵 FREEZER AKTIF"; topBadge.style.background = "#2563EB"; }
                    else { topBadge.innerHTML = "⚫ STANDBY"; topBadge.style.background = "rgba(0,0,0,0.3)"; }

                    document.getElementById("val-suhu").innerText = suhu.toFixed(1) + " °C";
                    document.getElementById("val-humid").innerText = humid.toFixed(1) + " %";
                    document.getElementById("val-air").innerText = air;
                    document.getElementById("val-alarm").innerText = alarmTotal ? "1" : "0";

                    const bSuhu = document.getElementById("stat-suhu");
                    bSuhu.innerText = (alarmSuhu && mode !== "STANDBY") ? "Bahaya" : "Normal";
                    bSuhu.className = (alarmSuhu && mode !== "STANDBY") ? "card-status status-bad" : "card-status status-ok";

                    const bAir = document.getElementById("stat-air");
                    bAir.innerText = alarmAir ? "Kotor!" : "Normal";
                    bAir.className = alarmAir ? "card-status status-bad" : "card-status status-ok";

                    const bAlarm = document.getElementById("stat-alarm");
                    bAlarm.innerText = alarmTotal ? "Cek Alat!" : "Aman";
                    bAlarm.className = alarmTotal ? "card-status status-bad" : "card-status status-ok";

                    let l0 = `Suhu : ${suhu.toFixed(1)} C   `;
                    let l1 = `Humid: ${humid.toFixed(1)} %   `;
                    let l2 = `Air:${ldr} ${air.padEnd(7, ' ')}`;
                    let l3 = mode === "CHILLER" ? (alarmSuhu ? "CHILLER: OUT RNG" : (alarmAir ? "CHIL: AIR KERUH!" : "CHILLER: AMAN   ")) : 
                             (mode === "FREEZER" ? (alarmSuhu ? "FREEZER: OUT RNG" : (alarmAir ? "FREZ: AIR KERUH!" : "FREEZER: AMAN   ")) : "Mode : STANDBY  ");

                    document.getElementById("lcd-0").innerText = l0.substring(0,16);
                    document.getElementById("lcd-1").innerText = l1.substring(0,16);
                    document.getElementById("lcd-2").innerText = l2.substring(0,16);
                    document.getElementById("lcd-3").innerText = l3.substring(0,16);

                    document.getElementById("led-kompresor").className = kompresor ? "led-indicator active-blue" : "led-indicator";
                    document.getElementById("led-buzzer").className = alarmTotal ? "led-indicator active-red" : "led-indicator";

                    document.getElementById("ch-suhu").innerText = mode === "CHILLER" ? suhu.toFixed(1) + " °C" : "-- °C";
                    document.getElementById("ch-humid").innerText = mode === "CHILLER" ? humid.toFixed(1) + " %" : "-- %";
                    document.getElementById("ch-gauge").style.width = mode === "CHILLER" ? Math.min(Math.max((suhu / 15)*100, 0), 100) + "%" : "0%";

                    document.getElementById("fz-suhu").innerText = mode === "FREEZER" ? suhu.toFixed(1) + " °C" : "-- °C";
                    document.getElementById("fz-humid").innerText = mode === "FREEZER" ? humid.toFixed(1) + " %" : "-- %";
                    document.getElementById("fz-gauge").style.width = mode === "FREEZER" ? Math.min(Math.max(((suhu+30)/30)*100, 0), 100) + "%" : "0%";

                    if (mode !== "STANDBY" || isFirstData) {
                        const timeStr = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
                        const tbody = document.getElementById("log-table-body");
                        const tr = document.createElement("tr");
                        let stIcon = alarmTotal ? "❌" : "✅";
                        tr.innerHTML = `<td>${timeStr}</td><td>${mode.substring(0,4)}</td><td>${suhu.toFixed(1)}</td><td>${air.substring(0,3)}</td><td>${stIcon}</td>`;
                        tbody.insertBefore(tr, tbody.firstChild);
                        if(tbody.children.length > 8) tbody.removeChild(tbody.lastChild);
                        
                        if(alarmTotal) {
                            const abody = document.getElementById("alert-table-body");
                            if(abody.innerHTML.includes("Aman")) abody.innerHTML = "";
                            const trA = document.createElement("tr");
                            trA.innerHTML = `<td>${timeStr}</td><td style="color:var(--danger); font-weight:bold;">${alarmSuhu ? "Suhu Out Range" : "Air Kotor"}</td>`;
                            abody.insertBefore(trA, abody.firstChild);
                            if(abody.children.length > 4) abody.removeChild(abody.lastChild);
                        }
                        isFirstData = false;
                    }
                }).catch(e => console.log("Menunggu Arduino/Wokwi..."));
        }, 1000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    threading.Thread(target=read_serial, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
