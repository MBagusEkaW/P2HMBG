import serial
import json
import threading
import time
from flask import Flask, render_template_string, jsonify, url_for

app = Flask(__name__)

# KONFIGURASI PORT 
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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Central-Kitchen Storage Safety Hub - P2HMBG</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary: #2196F3;
            --primary-light: #e3f2fd;
            --primary-dark: #1e88e5;
            --bg: #f4f7fc;
            --card: #ffffff;
            --text: #2c3e50;
            --muted: #7f8c8d;
            --success: #2ecc71;
            --warning: #f1c40f;
            --danger: #e74c3c;
            --sidebar-w: 260px;
            --lcd-bg: #0d1e0d;
            --lcd-txt: #5af85a;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg); color: var(--text); overflow-x: hidden; min-height: 100vh; }

        /* --- LOGIN SCREEN --- */
        #login-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background-color: #ffffff; z-index: 1000; display: flex; align-items: center; justify-content: center; }
        .login-card { width: 100%; max-width: 400px; padding: 40px; text-align: center; }
        
        /* Modifikasi Logo */
        .login-logo-container { width: 140px; height: 140px; margin: 0 auto 30px auto; position: relative; display: flex; align-items: center; justify-content: center; }
        .login-logo-img { width: 100%; height: 100%; object-fit: contain; border-radius: 50%; z-index: 2; position: relative; background-color: white;}
        .login-logo-container::before { content: ''; position: absolute; width: 170px; height: 170px; border: 3px solid var(--primary-light); border-radius: 50%; z-index: 1; }
        
        .login-title { color: var(--primary); font-weight: 700; font-size: 22px; margin-bottom: 5px; letter-spacing: 0.5px; }
        .login-subtitle { color: var(--primary); font-weight: 500; font-size: 14px; margin-bottom: 40px; }
        .input-group { width: 100%; margin-bottom: 20px; text-align: left; }
        .login-input { width: 100%; padding: 16px 20px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 15px; background-color: #f8fafc; outline: none; transition: border 0.3s; }
        .login-input:focus { border-color: var(--primary); background-color: #ffffff; }
        .btn-login { width: 100%; padding: 16px; background-color: var(--primary); color: white; border: none; border-radius: 30px; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3); margin-bottom: 20px; transition: transform 0.1s; }
        .btn-login:active { transform: scale(0.98); }

        /* --- APP CONTAINER --- */
        .app-container { display: none; min-height: 100vh; width: 100%; }
        .sidebar { width: var(--sidebar-w); background-color: #ffffff; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100; }
        .sidebar-brand { padding: 24px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #f1f5f9; }
        .brand-icon { font-size: 28px; color: var(--primary); }
        .brand-text h1 { font-size: 18px; font-weight: 700; color: var(--text); letter-spacing: 0.5px; }
        .brand-text span { font-size: 11px; color: var(--muted); text-transform: uppercase; }
        .sidebar-menu { padding: 24px 16px; display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }
        .menu-item { display: flex; align-items: center; gap: 14px; padding: 12px 16px; color: #64748b; text-decoration: none; font-weight: 500; font-size: 14px; border-radius: 8px; transition: all 0.2s ease; cursor: pointer; border: none; background: transparent; width: 100%; text-align: left; }
        .menu-item:hover, .menu-item.active { background-color: var(--primary-light); color: var(--primary-dark); }
        .menu-item i { font-size: 18px; width: 20px; }
        .badge-count { margin-left: auto; background-color: var(--danger); color: white; font-size: 11px; padding: 2px 6px; border-radius: 10px; font-weight: 700; }
        .sidebar-footer { padding: 16px; border-top: 1px solid #f1f5f9; }
        .admin-profile-sm { display: flex; align-items: center; gap: 12px; background-color: #f8fafc; padding: 10px; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
        .admin-profile-sm:hover { background-color: #e2e8f0; }
        .admin-profile-sm .avatar { width: 36px; height: 36px; background-color: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; }
        .admin-profile-sm .info h4 { font-size: 13px; font-weight: 600; }
        .admin-profile-sm .info p { font-size: 11px; color: var(--muted); }

        .main-content { margin-left: var(--sidebar-w); flex-grow: 1; padding: 32px; max-width: 1400px; }
        .main-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
        .header-title h2 { font-size: 22px; font-weight: 700; color: #1e293b; }
        .header-title .subtitle { font-size: 13px; color: var(--muted); margin-top: 4px; }
        .header-meta { display: flex; align-items: center; gap: 24px; }
        .greeting-box { display: flex; align-items: center; gap: 10px; background-color: #f8fafc; padding: 8px 16px; border-radius: 30px; }
        .greeting-text h3 { font-size: 13px; font-weight: 600; }
        .greeting-text p { font-size: 11px; color: var(--success); font-weight: 500; }
        .system-time { font-size: 13px; font-weight: 600; color: #64748b; background-color: #e2e8f0; padding: 8px 16px; border-radius: 30px; }

        .view-section { display: none; animation: fadeIn 0.3s ease-in-out; }
        .view-section.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        .mode-control-bar { background-color: #fff; border-radius: 12px; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 24px; border-left: 5px solid var(--primary); }
        .mode-info .label { font-size: 14px; color: var(--muted); font-weight: 500; }
        .mode-badge { margin-left: 8px; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; }
        .status-standby { background-color: #e2e8f0; color: #475569; }
        .status-chiller { background-color: #dbeafe; color: #1e40af; }
        .status-freezer { background-color: #fae8ff; color: #86198f; }

        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 28px; }
        .metric-card { background-color: #fff; border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .card-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .blue-bg { background-color: #e3f2fd; color: #2196F3; }
        .cyan-bg { background-color: #e0f7fa; color: #00bcd4; }
        .water-bg { background-color: #e8f5e9; color: #4caf50; }
        .alert-bg { background-color: #ffebee; color: #f44336; }
        .card-details { flex-grow: 1; }
        .card-label { font-size: 13px; color: var(--muted); font-weight: 500; }
        .card-value { font-size: 22px; font-weight: 700; margin: 4px 0; color: #1e293b; }
        .card-value .sub-val { font-size: 14px; font-weight: 600; color: #4caf50; }
        .status-indicator { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; display: inline-block; }
        .status-indicator.normal { background-color: #e8f5e9; color: #2e7d32; }
        .status-indicator.danger { background-color: #ffebee; color: #c62828; animation: pulse 1s infinite alternate; }
        @keyframes pulse { 0% { opacity: 0.6; } 100% { opacity: 1; } }

        .hardware-monitor-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
        .lcd-wrapper, .hardware-status-card, .dedicated-dashboard-panel { background-color: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .panel-header { font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        .lcd-screen { background-color: var(--lcd-bg); border: 6px solid #334155; border-radius: 6px; padding: 16px; }
        .lcd-line { font-family: 'Share Tech Mono', monospace; font-size: 20px; color: var(--lcd-txt); letter-spacing: 2px; height: 26px; white-space: pre; text-shadow: 0 0 4px rgba(90, 248, 90, 0.6); }
        .lcd-footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); margin-top: 8px; }

        .actuator-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
        .actuator-item { display: flex; justify-content: space-between; align-items: center; background-color: #f8fafc; padding: 10px 14px; border-radius: 8px; }
        .pin-number { font-family: 'Share Tech Mono', monospace; background-color: #cbd5e1; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-right: 8px; }
        .pin-name { font-size: 13px; font-weight: 500; }
        .led-indicator { width: 14px; height: 14px; border-radius: 50%; background-color: #cbd5e1; border: 2px solid #94a3b8; }
        .led-indicator.active-kompresor { background-color: #2196F3; border-color: #64b5f6; box-shadow: 0 0 8px #2196F3; }
        .led-indicator.active-alarm { background-color: #ef4444; border-color: #f87171; box-shadow: 0 0 8px #ef4444; animation: blink 0.5s infinite; }
        @keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

        .table-container { background-color: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .table-header h3 { font-size: 15px; color: #1e293b; }
        .refresh-rate { font-size: 12px; color: var(--muted); }
        .data-table { width: 100%; border-collapse: collapse; text-align: left; }
        .data-table th, .data-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
        .data-table th { background-color: #f8fafc; color: #64748b; font-weight: 600; }

        .gauge-bar-container { background-color: #e2e8f0; border-radius: 8px; height: 16px; width: 100%; margin-top: 10px; overflow: hidden; position: relative; }
        .gauge-fill { height: 100%; background-color: var(--primary); transition: width 0.5s ease; width: 0%; }
        .gauge-limits { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); margin-top: 4px; }
        .btn-export { background-color: #2ecc71; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            
            <div class="login-logo-container">
                <img src="/static/logo.png" alt="P2HMBG Logo" class="login-logo-img">
            </div>

            <div class="login-title">CENTRAL-KITCHEN</div>
            <div class="login-subtitle">STORAGE SAFETY HUB</div>
            <div class="input-group"><input type="text" id="username-input" class="login-input" placeholder="Email / Username" autocomplete="off"></div>
            <button class="btn-login" onclick="doLogin()">Log In</button>
            <p style="font-size: 13px; color: var(--primary); margin-top: 10px; cursor:pointer; font-weight: 500;">Forgot your password?</p>
        </div>
    </div>

    <div class="app-container" id="main-app">
        <aside class="sidebar">
            <div class="sidebar-brand">
                <i class="fa-solid fa-shield-halved brand-icon"></i>
                <div class="brand-text"><h1>P2HMBG</h1><span>Storage Hub</span></div>
            </div>
            <nav class="sidebar-menu">
                <button class="menu-item active" data-target="dashboard"><i class="fa-solid fa-chart-pie"></i> Dashboard</button>
                <button class="menu-item" data-target="chiller"><i class="fa-solid fa-snowflake"></i> Gudang Chiller</button>
                <button class="menu-item" data-target="freezer"><i class="fa-solid fa-temperature-empty"></i> Gudang Freezer</button>
                <button class="menu-item" data-target="alerts"><i class="fa-solid fa-bell"></i> Peringatan <span class="badge-count" id="alert-badge">0</span></button>
                <button class="menu-item" data-target="history"><i class="fa-solid fa-clock-rotate-left"></i> Riwayat</button>
            </nav>
            <div class="sidebar-footer">
                <div class="admin-profile-sm" onclick="doLogout()">
                    <div class="avatar" id="sidebar-avatar">A</div>
                    <div class="info"><h4 id="sidebar-name">Admin</h4><p>Pusat Dapur MBG</p></div>
                </div>
                <div style="font-size: 10px; color: var(--muted); text-align: center; margin-top: 10px;">Klik profil untuk Log Out</div>
            </div>
        </aside>

        <main class="main-content">
            <header class="main-header">
                <div class="header-title">
                    <h2>CENTRAL-KITCHEN STORAGE SAFETY HUB</h2>
                    <p class="subtitle">Pusat Dapur MBG • Sistem Kontrol IoT Terintegrasi</p>
                </div>
                <div class="header-meta">
                    <div class="greeting-box">
                        <span class="wave">👋</span>
                        <div class="greeting-text">
                            <h3>Halo, <span id="header-name">Admin</span>!</h3>
                            <p>Sistem terhubung ke Wokwi</p>
                        </div>
                    </div>
                    <div class="system-time" id="live-clock">00:00:00</div>
                </div>
            </header>

            <div id="dashboard-view" class="view-section active">
                <div class="mode-control-bar">
                    <div class="mode-info">
                        <span class="label">Mode Sistem di Alat (Saklar Wokwi):</span>
                        <span class="mode-badge status-standby" id="current-mode-badge">STANDBY</span>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="card-icon blue-bg"><i class="fa-solid fa-temperature-half"></i></div>
                        <div class="card-details">
                            <p class="card-label">Suhu Aktif</p>
                            <h3 class="card-value" id="txt-suhu">--.- °C</h3>
                            <span class="status-indicator normal" id="lbl-suhu-status">Normal</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="card-icon cyan-bg"><i class="fa-solid fa-droplet"></i></div>
                        <div class="card-details">
                            <p class="card-label">Kelembapan</p>
                            <h3 class="card-value" id="txt-humid">--.- %</h3>
                            <span class="status-indicator normal" id="lbl-humid-status">Normal</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="card-icon water-bg"><i class="fa-solid fa-faucet-drip"></i></div>
                        <div class="card-details">
                            <p class="card-label">Kondisi Air (LDR)</p>
                            <h3 class="card-value" id="txt-air">--- <span class="sub-val" id="txt-status-air">JERNIH</span></h3>
                            <span class="status-indicator normal" id="lbl-air-status">Normal</span>
                        </div>
                    </div>
                    <div class="metric-card" id="alert-summary-card">
                        <div class="card-icon alert-bg"><i class="fa-solid fa-bullhorn"></i></div>
                        <div class="card-details">
                            <p class="card-label">Peringatan Aktif</p>
                            <h3 class="card-value" id="txt-alarm-count">0</h3>
                            <span class="status-indicator normal" id="lbl-alarm-status">Aman</span>
                        </div>
                    </div>
                </div>

                <div class="hardware-monitor-section">
                    <div class="lcd-wrapper">
                        <div class="panel-header"><i class="fa-solid fa-microchip"></i> LCD I2C Live View (Physical Output)</div>
                        <div class="lcd-screen">
                            <div class="lcd-line" id="lcd-row-0">  SISTEM KONTROL  </div>
                            <div class="lcd-line" id="lcd-row-1">      P2HMBG      </div>
                            <div class="lcd-line" id="lcd-row-2">                  </div>
                            <div class="lcd-line" id="lcd-row-3">Mode : STANDBY  </div>
                        </div>
                        <div class="lcd-footer"><span>Alamat I2C: 0x27</span><span>Data sinkron Wokwi</span></div>
                    </div>

                    <div class="hardware-status-card">
                        <div class="panel-header"><i class="fa-solid fa-gears"></i> Status Output Akutator (Relay & Pin)</div>
                        <div class="actuator-list">
                            <div class="actuator-item">
                                <div class="actuator-info"><span class="pin-number">PIN 11</span><span class="pin-name">Kompresor Pendingin (LED)</span></div>
                                <div class="led-indicator" id="led-kompresor"></div>
                            </div>
                            <div class="actuator-item">
                                <div class="actuator-info"><span class="pin-number">PIN 6</span><span class="pin-name">Buzzer Alarm Fisik</span></div>
                                <div class="led-indicator alarm-led" id="led-buzzer"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3><i class="fa-solid fa-list-check"></i> Log Data Sensor Terkini</h3>
                        <span class="refresh-rate">Diperbarui realtime dari Serial Port Wokwi</span>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr><th>Waktu</th><th>Mode Aktif</th><th>Suhu (°C)</th><th>Kelembapan (%)</th><th>Nilai LDR</th><th>Status Air</th><th>Sistem</th></tr>
                        </thead>
                        <tbody id="log-table-body"></tbody>
                    </table>
                </div>
            </div>

            <div id="chiller-view" class="view-section">
                <div class="dedicated-dashboard-panel" style="border-top: 4px solid #2196F3;">
                    <div class="panel-header" style="font-size: 18px; color:#1e293b;"><i class="fa-solid fa-snowflake"></i> Panel Khusus Gudang Chiller</div>
                    <p style="font-size:14px; color:var(--muted); margin-bottom:20px;">Target batas aman: 2.0°C sampai 8.0°C.</p>
                    <div class="metrics-grid">
                        <div class="metric-card" style="background:#f8fafc;"><div class="card-details"><p class="card-label">Suhu Chiller Saat Ini</p><h2 class="card-value" id="chiller-val-suhu" style="font-size: 32px; color:#1e40af;">--.- °C</h2></div></div>
                        <div class="metric-card" style="background:#f8fafc;"><div class="card-details"><p class="card-label">Kelembapan Chiller</p><h2 class="card-value" id="chiller-val-humid" style="font-size: 32px; color:#00bcd4;">--.- %</h2></div></div>
                    </div>
                    <div style="margin-top: 15px;">
                        <span class="card-label">Visualisasi Batas Suhu Chiller (2°C - 8°C):</span>
                        <div class="gauge-bar-container"><div class="gauge-fill" id="chiller-gauge" style="background:#2196F3;"></div></div>
                        <div class="gauge-limits"><span>0°C</span><span>Batas Aman (2°C - 8°C)</span><span>15°C</span></div>
                    </div>
                </div>
            </div>

            <div id="freezer-view" class="view-section">
                <div class="dedicated-dashboard-panel" style="border-top: 4px solid #86198f;">
                    <div class="panel-header" style="font-size: 18px; color:#1e293b;"><i class="fa-solid fa-temperature-empty"></i> Panel Khusus Gudang Freezer</div>
                    <p style="font-size:14px; color:var(--muted); margin-bottom:20px;">Target batas aman: -25.0°C sampai -15.0°C.</p>
                    <div class="metrics-grid">
                        <div class="metric-card" style="background:#f8fafc;"><div class="card-details"><p class="card-label">Suhu Freezer Saat Ini</p><h2 class="card-value" id="freezer-val-suhu" style="font-size: 32px; color:#86198f;">--.- °C</h2></div></div>
                        <div class="metric-card" style="background:#f8fafc;"><div class="card-details"><p class="card-label">Kelembapan Freezer</p><h2 class="card-value" id="freezer-val-humid" style="font-size: 32px; color:#00bcd4;">--.- %</h2></div></div>
                    </div>
                    <div style="margin-top: 15px;">
                        <span class="card-label">Visualisasi Batas Suhu Freezer (-25°C s/d -15°C):</span>
                        <div class="gauge-bar-container"><div class="gauge-fill" id="freezer-gauge" style="background:#86198f;"></div></div>
                        <div class="gauge-limits"><span>-30°C</span><span>Batas Aman (-25°C - -15°C)</span><span>0°C</span></div>
                    </div>
                </div>
            </div>

            <div id="alerts-view" class="view-section">
                <div class="table-container" style="border-top: 4px solid var(--danger);">
                    <div class="table-header"><h3><i class="fa-solid fa-triangle-exclamation"></i> Log Riwayat Peringatan Sistem</h3></div>
                    <table class="data-table">
                        <thead><tr><th>Timestamp</th><th>Kategori Peringatan</th><th>Deskripsi Kejadian</th><th>Status Masalah</th></tr></thead>
                        <tbody id="alerts-table-body"><tr><td colspan="4" style="text-align:center; color:var(--muted);">Tidak ada alarm aktif saat ini.</td></tr></tbody>
                    </table>
                </div>
            </div>

            <div id="history-view" class="view-section">
                <div class="table-container">
                    <div class="table-header">
                        <h3><i class="fa-solid fa-clock-rotate-left"></i> Basis Data Jangka Panjang</h3>
                        <button class="btn-export" onclick="alert('Berhasil mengunduh data sensor format .CSV!')"><i class="fa-solid fa-file-csv"></i> Ekspor ke CSV</button>
                    </div>
                    <table class="data-table">
                        <thead><tr><th>Waktu</th><th>Mode Alat</th><th>Suhu (°C)</th><th>Kelembapan (%)</th><th>Nilai Air</th><th>Kondisi Air</th></tr></thead>
                        <tbody id="history-full-table-body"></tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script>
        let alarmHistoryCount = 0; 
        
        function doLogin() {
            const inputName = document.getElementById("username-input").value.trim();
            const displayName = inputName === "" ? "Admin" : inputName;
            document.getElementById("header-name").innerText = displayName;
            document.getElementById("sidebar-name").innerText = displayName;
            document.getElementById("sidebar-avatar").innerText = displayName.charAt(0).toUpperCase();
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("main-app").style.display = "flex";
        }

        function doLogout() {
            document.getElementById("main-app").style.display = "none";
            document.getElementById("login-screen").style.display = "flex";
            document.getElementById("username-input").value = "";
            document.querySelector('.menu-item[data-target="dashboard"]').click();
        }

        document.querySelectorAll('.menu-item').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.menu-item').forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                document.querySelectorAll('.view-section').forEach(view => view.classList.remove('active'));
                const targetViewId = this.getAttribute('data-target') + '-view';
                const currentView = document.getElementById(targetViewId);
                if (currentView) currentView.classList.add('active');
            });
        });

        document.addEventListener("DOMContentLoaded", () => {
            setInterval(() => {
                const now = new Date();
                document.getElementById("live-clock").innerText = now.toLocaleTimeString() + " • " + now.toLocaleDateString('id-ID', {day:'numeric', month:'long', year:'numeric'});
            }, 1000);
        });

        setInterval(() => {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    let modeAktif = data.mode;
                    let suhu = data.suhu;
                    let kelembapan = data.kelembapan;
                    let nilaiKekeruhan = data.kekeruhan;
                    let statusAir = data.status_air;
                    let alarmTotal = data.alarm;

                    let alarmAir = (statusAir === "KOTOR" && modeAktif !== "STANDBY");
                    let alarmSuhu = false;
                    let kompresor = false;

                    if (modeAktif === "CHILLER") {
                        if (suhu > 2.0) kompresor = true;
                        if (suhu < 2.0 || suhu > 8.0) alarmSuhu = true;
                    } else if (modeAktif === "FREEZER") {
                        if (suhu > -25.0) kompresor = true;
                        if (suhu < -25.0 || suhu > -15.0) alarmSuhu = true;
                    }

                    const badge = document.getElementById("current-mode-badge");
                    badge.innerText = modeAktif;
                    badge.className = `mode-badge status-${modeAktif.toLowerCase()}`;

                    document.getElementById("txt-suhu").innerText = `${suhu.toFixed(1)} °C`;
                    document.getElementById("txt-humid").innerText = `${kelembapan.toFixed(1)} %`;
                    document.getElementById("txt-air").innerHTML = `${nilaiKekeruhan} <span class="sub-val">${statusAir}</span>`;

                    document.getElementById("chiller-val-suhu").innerText = modeAktif === "CHILLER" ? `${suhu.toFixed(1)} °C` : "--.- °C";
                    document.getElementById("chiller-val-humid").innerText = modeAktif === "CHILLER" ? `${kelembapan.toFixed(1)} %` : "--.- %";
                    document.getElementById("freezer-val-suhu").innerText = modeAktif === "FREEZER" ? `${suhu.toFixed(1)} °C` : "--.- °C";
                    document.getElementById("freezer-val-humid").innerText = modeAktif === "FREEZER" ? `${kelembapan.toFixed(1)} %` : "--.- %";

                    if(modeAktif === "CHILLER") {
                        let pct = Math.min(Math.max((suhu / 15) * 100, 0), 100);
                        document.getElementById("chiller-gauge").style.width = `${pct}%`;
                        document.getElementById("freezer-gauge").style.width = `0%`;
                    } else if(modeAktif === "FREEZER") {
                        let pct = Math.min(Math.max(((suhu + 30) / 30) * 100, 0), 100);
                        document.getElementById("freezer-gauge").style.width = `${pct}%`;
                        document.getElementById("chiller-gauge").style.width = `0%`;
                    }

                    const txtAirSpan = document.querySelector("#txt-air .sub-val");
                    if(statusAir === "KOTOR") txtAirSpan.style.color = "var(--danger)";
                    else if(statusAir === "STANDAR") txtAirSpan.style.color = "var(--warning)";
                    else txtAirSpan.style.color = "var(--success)";

                    updateBadge("lbl-suhu-status", alarmSuhu && modeAktif !== "STANDBY" ? "Bahaya" : "Normal", alarmSuhu && modeAktif !== "STANDBY");
                    updateBadge("lbl-air-status", alarmAir ? "Kotor!" : "Normal", alarmAir);
                    
                    document.getElementById("txt-alarm-count").innerText = alarmTotal ? "1" : "0";
                    document.getElementById("alert-badge").innerText = alarmTotal ? "1" : "0";
                    updateBadge("lbl-alarm-status", alarmTotal ? "⚠️ Bahaya" : "Aman", alarmTotal);

                    let line0 = `Suhu : ${suhu.toFixed(1)} C   `;
                    let line1 = `Humid: ${kelembapan.toFixed(1)} %   `;
                    let line2 = `Air:${nilaiKekeruhan} ${statusAir.padEnd(7, ' ')}`;
                    let line3 = "";

                    if (modeAktif === "CHILLER") {
                        if (alarmSuhu) line3 = "CHILLER: OUT RNG";
                        else if (alarmAir) line3 = "CHIL: AIR KERUH!";
                        else line3 = "CHILLER: AMAN   ";
                    } else if (modeAktif === "FREEZER") {
                        if (alarmSuhu) line3 = "FREEZER: OUT RNG";
                        else if (alarmAir) line3 = "FREZ: AIR KERUH!";
                        else line3 = "FREEZER: AMAN   ";
                    } else {
                        line3 = "Mode : STANDBY  ";
                    }

                    document.getElementById("lcd-row-0").innerText = line0.substring(0, 16);
                    document.getElementById("lcd-row-1").innerText = line1.substring(0, 16);
                    document.getElementById("lcd-row-2").innerText = line2.substring(0, 16);
                    document.getElementById("lcd-row-3").innerText = line3.substring(0, 16);

                    const ledKomp = document.getElementById("led-kompresor");
                    if(kompresor) ledKomp.classList.add("active-kompresor");
                    else ledKomp.classList.remove("active-kompresor");

                    const ledBuzz = document.getElementById("led-buzzer");
                    if(alarmTotal) ledBuzz.classList.add("active-alarm");
                    else ledBuzz.classList.remove("active-alarm");

                    logToTables(modeAktif, suhu, kelembapan, nilaiKekeruhan, statusAir, alarmTotal, alarmSuhu);
                })
                .catch(err => console.error("Koneksi ke Wokwi terputus!"));
        }, 1000); 

        function updateBadge(id, text, isDanger) {
            const element = document.getElementById(id);
            element.innerText = text;
            element.className = isDanger ? "status-indicator danger" : "status-indicator normal";
        }

        function logToTables(modeAktif, suhu, kelembapan, nilaiKekeruhan, statusAir, alarmTotal, alarmSuhu) {
            const timeStr = new Date().toLocaleTimeString();
            
            const tbody = document.getElementById("log-table-body");
            const tr = document.createElement("tr");
            let stateBadge = alarmTotal ? `<span style="color:var(--danger); font-weight:600;"><i class="fa-solid fa-circle-exclamation"></i> ALARM</span>` : `<span style="color:var(--success); font-weight:600;"><i class="fa-solid fa-circle-check"></i> OK</span>`;
            tr.innerHTML = `<td>${timeStr}</td><td><strong>${modeAktif}</strong></td><td>${suhu.toFixed(1)} °C</td><td>${kelembapan.toFixed(1)} %</td><td>${nilaiKekeruhan}</td><td>${statusAir}</td><td>${stateBadge}</td>`;
            tbody.insertBefore(tr, tbody.firstChild);
            if(tbody.children.length > 5) tbody.removeChild(tbody.lastChild);

            const historyBody = document.getElementById("history-full-table-body");
            const trHist = document.createElement("tr");
            trHist.innerHTML = `<td>${timeStr}</td><td>${modeAktif}</td><td>${suhu.toFixed(1)} °C</td><td>${kelembapan.toFixed(1)} %</td><td>${nilaiKekeruhan}</td><td>${statusAir}</td>`;
            historyBody.insertBefore(trHist, historyBody.firstChild);
            if(historyBody.children.length > 20) historyBody.removeChild(historyBody.lastChild);

            if(alarmTotal) {
                alarmHistoryCount++;
                if (alarmHistoryCount % 5 === 0) { 
                    const alertBody = document.getElementById("alerts-table-body");
                    if(alertBody.innerHTML.includes("Tidak ada alarm")) alertBody.innerHTML = "";
                    const trAlert = document.createElement("tr");
                    let kategori = alarmSuhu ? "Suhu Diluar Range" : "Air Kotor";
                    let deskripsi = alarmSuhu ? `Suhu unit ${modeAktif} menyentuh ${suhu.toFixed(1)}°C` : `Nilai LDR: ${nilaiKekeruhan} (${statusAir})`;
                    trAlert.innerHTML = `<td>${timeStr}</td><td><span style="background:#fff1f2; color:var(--danger); padding:2px 8px; border-radius:4px; font-weight:600;">${kategori}</span></td><td>${deskripsi}</td><td><b style="color:var(--danger);"><i class="fa-solid fa-bell"></i> ACTIVE</b></td>`;
                    alertBody.insertBefore(trAlert, alertBody.firstChild);
                    if(alertBody.children.length > 8) alertBody.removeChild(alertBody.lastChild);
                }
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    threading.Thread(target=read_serial, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
