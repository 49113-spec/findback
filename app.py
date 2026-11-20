import base64
import os
import socket
import sqlite3
from datetime import datetime
from flask import Flask, Response, render_template_string, request, redirect, url_for

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "lost_found.db")

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FindBack</title>
  <style>
    :root {
      --bg: linear-gradient(135deg, #dbeafe 0%, #ede9fe 48%, #fce7f3 100%);
      --glass: rgba(255, 255, 255, 0.58);
      --header: rgba(255, 255, 255, 0.68);
      --border: rgba(255, 255, 255, 0.85);
      --highlight: rgba(255, 255, 255, 0.95);
      --shadow: 0 10px 30px rgba(30, 41, 59, 0.08);
      --text: #0f172a;
      --sub: #334155;
      --muted: #64748b;
      --input-bg: rgba(255, 255, 255, 0.78);
      --input-bd: rgba(255, 255, 255, 0.92);
      --div: rgba(255, 255, 255, 0.75);
      --title: linear-gradient(135deg, #312e81, #4f46e5, #0284c7);
      --alert-bg: rgba(254, 243, 199, 0.72);
      --alert-bd: rgba(255, 255, 255, 0.88);
      --alert-h: #92400e;
      --alert-t: #78350f;
      --b-open-bg: rgba(67, 56, 202, 0.14);
      --b-open-t: #312e81;
      --b-done-bg: rgba(5, 150, 105, 0.16);
      --b-done-t: #065f46;
      --t-found-bg: rgba(79, 70, 229, 0.14);
      --t-found-t: #3730a3;
      --t-lost-bg: rgba(225, 29, 72, 0.14);
      --t-lost-t: #be123c;
      --h-lost: #be123c;
      --h-found: #3730a3;
      --cat: #4338ca;
      --done: #059669;
      --orb1: radial-gradient(circle, #818cf8, #4f46e5);
      --orb2: radial-gradient(circle, #38bdf8, #0284c7);
      --orb3: radial-gradient(circle, #f472b6, #db2777);
      --orb-op: 0.72;
    }
    body.dark-mode {
      --bg: linear-gradient(135deg, #060913 0%, #0f172a 50%, #160d26 100%);
      --glass: rgba(17, 25, 40, 0.62);
      --header: rgba(11, 17, 30, 0.72);
      --border: rgba(255, 255, 255, 0.16);
      --highlight: rgba(255, 255, 255, 0.24);
      --shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
      --text: #f8fafc;
      --sub: #cbd5e1;
      --muted: #94a3b8;
      --input-bg: rgba(15, 23, 42, 0.75);
      --input-bd: rgba(255, 255, 255, 0.18);
      --div: rgba(255, 255, 255, 0.12);
      --title: linear-gradient(135deg, #e0e7ff, #818cf8, #38bdf8);
      --alert-bg: rgba(120, 53, 15, 0.35);
      --alert-bd: rgba(251, 191, 36, 0.38);
      --alert-h: #fcd34d;
      --alert-t: #fef3c7;
      --b-open-bg: rgba(99, 102, 241, 0.22);
      --b-open-t: #c7d2fe;
      --b-done-bg: rgba(16, 185, 129, 0.22);
      --b-done-t: #6ee7b7;
      --t-found-bg: rgba(99, 102, 241, 0.25);
      --t-found-t: #c7d2fe;
      --t-lost-bg: rgba(244, 63, 94, 0.25);
      --t-lost-t: #fecdd3;
      --h-lost: #fb7185;
      --h-found: #818cf8;
      --cat: #93c5fd;
      --done: #34d399;
      --orb1: radial-gradient(circle, #6366f1, #312e81);
      --orb2: radial-gradient(circle, #0ea5e9, #0369a1);
      --orb3: radial-gradient(circle, #ec4899, #831843);
      --orb-op: 0.55;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: Tahoma, 'Segoe UI', sans-serif;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      color-scheme: light;
      line-height: 1.5;
      overflow-x: hidden;
      transition: background 0.3s, color 0.3s;
    }
    body.dark-mode { color-scheme: dark; }
    .liquid-bg { position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }
    .orb { position: absolute; border-radius: 50%; filter: blur(70px); opacity: var(--orb-op); animation: floatOrb 14s ease-in-out infinite alternate; }
    .orb-1 { width: 400px; height: 400px; background: var(--orb1); top: -90px; left: -70px; }
    .orb-2 { width: 440px; height: 440px; background: var(--orb2); bottom: -110px; right: -80px; animation-delay: -5s; }
    .orb-3 { width: 320px; height: 320px; background: var(--orb3); top: 40%; left: 46%; animation-delay: -9s; }
    @keyframes floatOrb { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(35px,-30px) scale(1.08); } }
    .glass {
      background: var(--glass);
      backdrop-filter: blur(24px) saturate(180%);
      -webkit-backdrop-filter: blur(24px) saturate(180%);
      border: 1px solid var(--border);
      box-shadow: var(--shadow), inset 0 1px 1px var(--highlight);
    }
    .container { max-width: 980px; margin: 0 auto; }
    .header {
      position: sticky; top: 0; z-index: 20; padding: 15px 16px;
      background: var(--header);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border-bottom: 1px solid var(--border);
      box-shadow: 0 4px 24px rgba(30, 41, 59, 0.08);
    }
    .header-flex { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; }
    .header h1 { font-size: 25px; font-weight: bold; background: var(--title); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .badges { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 12px; font-weight: bold; }
    .badge-open { background: var(--b-open-bg); color: var(--b-open-t); border: 1px solid var(--border); padding: 6px 14px; border-radius: 999px; }
    .badge-done { background: var(--b-done-bg); color: var(--b-done-t); border: 1px solid var(--border); padding: 6px 14px; border-radius: 999px; }
    .pill-btn {
      background: var(--glass); color: var(--text); border: 1px solid var(--border);
      padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: bold;
      cursor: pointer; font-family: inherit; transition: 0.2s;
    }
    .pill-btn:hover { transform: scale(1.04); }
    .nav { padding: 14px 16px 0; }
    .nav-pill-wrap { display: inline-flex; flex-wrap: wrap; gap: 6px; padding: 6px; border-radius: 16px; }
    .tab-btn { border: 1px solid transparent; padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; background: transparent; color: var(--sub); transition: 0.2s; }
    .tab-btn:hover { background: rgba(255, 255, 255, 0.2); color: var(--text); }
    .tab-btn.active { background: linear-gradient(135deg, rgba(79,70,229,0.92), rgba(59,130,246,0.92)); color: #fff; border-color: rgba(255,255,255,0.5); box-shadow: 0 4px 16px rgba(79,70,229,0.35); }
    .main { padding: 20px 16px 44px; }
    .hidden { display: none !important; }
    .alert-box { background: var(--alert-bg); backdrop-filter: blur(22px); border: 1px solid var(--alert-bd); border-radius: 18px; padding: 16px 18px; margin-bottom: 20px; }
    .alert-box h2 { font-size: 14px; color: var(--alert-h); margin-bottom: 8px; }
    .alert-item { font-size: 13px; color: var(--alert-t); margin-bottom: 4px; }
    .filter-bar { border-radius: 18px; padding: 14px; display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; }
    .input, .select, .textarea { background: var(--input-bg); border: 1px solid var(--input-bd); border-radius: 12px; padding: 9px 13px; font-size: 14px; font-family: inherit; color: var(--text); outline: none; }
    .input::placeholder, .textarea::placeholder { color: var(--muted); }
    .input:focus, .select:focus, .textarea:focus { border-color: #818cf8; box-shadow: 0 0 0 3px rgba(99,102,241,0.22); }
    .filter-bar .input { flex: 1; min-width: 200px; }
    .btn { border: 1px solid rgba(255,255,255,0.45); border-radius: 12px; padding: 9px 18px; font-size: 14px; font-weight: bold; cursor: pointer; color: #fff; font-family: inherit; transition: 0.2s; }
    .btn:hover { transform: translateY(-1px); filter: brightness(1.06); }
    .btn-indigo { background: linear-gradient(135deg, #4f46e5, #2563eb); }
    .btn-rose { background: linear-gradient(135deg, #f43f5e, #e11d48); width: 100%; padding: 12px; }
    .btn-emerald { background: linear-gradient(135deg, #10b981, #059669); font-size: 12px; padding: 7px 13px; }
    .btn-full { width: 100%; padding: 12px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }
    .card { border-radius: 20px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; transition: 0.25s; }
    .card:hover { transform: translateY(-3px); }
    .card.resolved { opacity: 0.72; }
    .card-img-wrap { width: 100%; height: 175px; border-radius: 14px; overflow: hidden; margin-bottom: 12px; border: 1px solid var(--border); cursor: zoom-in; }
    .card-img-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .tag-found { background: var(--t-found-bg); color: var(--t-found-t); border: 1px solid var(--border); font-size: 12px; font-weight: bold; padding: 4px 11px; border-radius: 999px; }
    .tag-lost { background: var(--t-lost-bg); color: var(--t-lost-t); border: 1px solid var(--border); font-size: 12px; font-weight: bold; padding: 4px 11px; border-radius: 999px; }
    .date-txt { font-size: 12px; color: var(--muted); }
    .card h3 { font-size: 17px; margin-bottom: 2px; }
    .cat-txt { font-size: 12px; color: var(--cat); font-weight: bold; margin-bottom: 8px; }
    .desc-txt { font-size: 13px; color: var(--sub); margin-bottom: 12px; }
    .meta { border-top: 1px solid var(--div); padding-top: 10px; font-size: 12px; color: var(--muted); }
    .meta div { margin-bottom: 3px; }
    .meta strong { color: var(--sub); }
    .card-footer { border-top: 1px solid var(--div); padding-top: 12px; margin-top: 12px; }
    .resolve-form { display: flex; gap: 6px; }
    .resolve-form .input { flex: 1; font-size: 12px; padding: 7px 10px; }
    .done-txt { font-size: 13px; font-weight: bold; color: var(--done); }
    .form-box { max-width: 540px; margin: 0 auto; border-radius: 22px; padding: 26px; }
    .form-box h2 { font-size: 19px; margin-bottom: 4px; }
    .form-box p { font-size: 12px; color: var(--muted); margin-bottom: 18px; }
    .field { margin-bottom: 14px; }
    .field label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: var(--sub); }
    .field .input, .field .select, .field .textarea { width: 100%; }
    .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .upload-box { border: 1.5px dashed var(--border); background: var(--input-bg); border-radius: 14px; padding: 12px; text-align: center; }
    .upload-box input[type="file"] { width: 100%; font-size: 13px; color: var(--sub); cursor: pointer; }
    .preview-img { display: none; max-height: 180px; max-width: 100%; margin: 10px auto 0; border-radius: 12px; object-fit: contain; }
    .empty { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted); font-size: 14px; border-radius: 20px; }

    .modal-backdrop { position: fixed; inset: 0; z-index: 50; background: rgba(3,7,18,0.78); backdrop-filter: blur(14px); display: flex; align-items: center; justify-content: center; padding: 20px; }
    .modal-backdrop img.zoomed { max-width: 92vw; max-height: 86vh; border-radius: 18px; border: 1px solid rgba(255,255,255,0.25); cursor: zoom-out; }
    .qr-card { max-width: 390px; width: 100%; border-radius: 24px; padding: 24px; text-align: center; position: relative; }
    .qr-card h2 { font-size: 19px; margin-bottom: 6px; }
    .qr-card p { font-size: 12px; color: var(--sub); margin-bottom: 14px; }
    .qr-frame { background: #ffffff; padding: 14px; border-radius: 18px; display: inline-block; box-shadow: 0 8px 24px rgba(0,0,0,0.18); margin-bottom: 12px; }
    .qr-frame img { display: block; width: 210px; height: 210px; }
    .qr-url-row { display: flex; gap: 6px; margin-bottom: 12px; }
    .qr-url-row .input { flex: 1; font-size: 12px; padding: 8px 10px; }
    .qr-actions { display: flex; gap: 8px; }
    .qr-actions .btn { flex: 1; font-size: 13px; padding: 10px; }
    .btn-ghost { background: var(--glass); color: var(--text); border: 1px solid var(--border); }
  </style>
</head>
<body>
  <div class="liquid-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>

  <header class="header">
    <div class="container header-flex">
      <h1>FindBack</h1>
      <div class="badges">
        <span class="badge-open">รอรับคืน/ตามหา: {{ stat_open }}</span>
        <span class="badge-done">ส่งคืนแล้ว: {{ stat_resolved }}</span>
        <button type="button" onclick="openQrModal()" class="pill-btn">📱 QR Code</button>
        <button type="button" onclick="toggleTheme()" id="themeToggleBtn" class="pill-btn">🌙 Dark Mode</button>
      </div>
    </div>
  </header>

  <nav class="nav">
    <div class="container">
      <div class="nav-pill-wrap glass">
        <button onclick="switchTab('feed', this)" class="tab-btn active">รายการทั้งหมด & จับคู่อัตโนมัติ</button>
        <button onclick="switchTab('reportLost', this)" class="tab-btn">+ แจ้งทำของหาย (ผู้ใช้งาน)</button>
        <button onclick="switchTab('recordFound', this)" class="tab-btn">+ บันทึกของที่เก็บได้ (เจ้าหน้าที่)</button>
      </div>
    </div>
  </nav>

  <main class="container main">
    <section id="view-feed">
      {% if smart_matches %}
      <div class="alert-box">
        <h2>พบรายการที่น่าจะตรงกัน (Smart Match)</h2>
        {% for m in smart_matches %}
        <div class="alert-item">
          - รายการแจ้งหาย <b>"{{ m.lost_name }}"</b> ({{ m.lost_by }}) ตรงกับของที่เก็บได้ <b>"{{ m.found_name }}"</b> ที่ {{ m.found_loc }} ({{ m.pickup }})
        </div>
        {% endfor %}
      </div>
      {% endif %}

      <form method="GET" action="/" class="filter-bar glass">
        <input type="text" name="q" value="{{ keyword }}" placeholder="ค้นหาชื่อสิ่งของ, สถานที่, รายละเอียด..." class="input">
        <select name="type" onchange="this.form.submit()" class="select">
          <option value="all" {% if filter_type == 'all' %}selected{% endif %}>ทุกประเภท (แจ้งหาย + เก็บได้)</option>
          <option value="found" {% if filter_type == 'found' %}selected{% endif %}>เก็บได้ / รอเจ้าของมารับ</option>
          <option value="lost" {% if filter_type == 'lost' %}selected{% endif %}>แจ้งทำของหาย / กำลังตามหา</option>
        </select>
        <select name="status" onchange="this.form.submit()" class="select">
          <option value="open" {% if filter_status == 'open' %}selected{% endif %}>สถานะ: กำลังดำเนินการ</option>
          <option value="resolved" {% if filter_status == 'resolved' %}selected{% endif %}>สถานะ: ส่งคืนเรียบร้อยแล้ว</option>
          <option value="all" {% if filter_status == 'all' %}selected{% endif %}>ทุกสถานะ</option>
        </select>
        <button type="submit" class="btn btn-indigo">ค้นหา</button>
      </form>

      <div class="grid">
        {% if not items %}
        <div class="empty glass">ไม่พบข้อมูลรายการที่ค้นหา</div>
        {% endif %}

        {% for item in items %}
        <div class="card glass {% if item.status == 'resolved' %}resolved{% endif %}">
          <div>
            {% if item.image_data %}
            <div class="card-img-wrap" onclick="openImageModal(this.querySelector('img').src)" title="คลิกเพื่อขยายรูป">
              <img src="{{ item.image_data }}" alt="{{ item.item_name }}">
            </div>
            {% endif %}
            <div class="card-top">
              {% if item.type == 'found' %}
              <span class="tag-found">เก็บได้ (รอเจ้าของ)</span>
              {% else %}
              <span class="tag-lost">แจ้งของหาย (ตามหา)</span>
              {% endif %}
              <span class="date-txt">{{ item.item_date }}</span>
            </div>
            <h3>{{ item.item_name }}</h3>
            <div class="cat-txt">{{ item.category }}</div>
            <div class="desc-txt">{{ item.description or 'ไม่มีรายละเอียดเพิ่มเติม' }}</div>
            <div class="meta">
              <div><strong>สถานที่:</strong> {{ item.location }}</div>
              <div><strong>ผู้แจ้ง/ผู้บันทึก:</strong> {{ item.reporter_name }}</div>
              <div><strong>ติดต่อ/จุดรับคืน:</strong> {{ item.contact_or_pickup }}</div>
            </div>
          </div>

          <div class="card-footer">
            {% if item.status == 'resolved' %}
            <span class="done-txt">ส่งคืนแล้ว (ผู้รับ: {{ item.claimed_by }})</span>
            {% else %}
            <form method="POST" action="/resolve/{{ item.id }}" class="resolve-form">
              <input type="text" name="claimed_by" required placeholder="ระบุชื่อผู้รับคืน..." class="input">
              <button type="submit" class="btn btn-emerald">บันทึกส่งคืน</button>
            </form>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </section>

    <section id="view-reportLost" class="hidden">
      <div class="form-box glass">
        <h2 style="color:var(--h-lost);">แบบฟอร์มแจ้งทำของหาย</h2>
        <p>กรอกข้อมูลทรัพย์สินที่สูญหาย เพื่อให้ระบบช่วยจับคู่กับของที่จุดรับแจ้งบันทึกไว้</p>
        <form method="POST" action="/add" enctype="multipart/form-data">
          <input type="hidden" name="type" value="lost">
          <input type="hidden" name="image_data" id="lostImageData">
          <div class="field">
            <label>ชื่อสิ่งของที่หาย *</label>
            <input type="text" name="item_name" required placeholder="เช่น หูฟังไร้สาย สีขาว, บัตรนักเรียน" class="input">
          </div>
          <div class="row-2">
            <div class="field">
              <label>หมวดหมู่</label>
              <select name="category" class="select">
                <option>อุปกรณ์ไอที / มือถือ</option>
                <option>กระเป๋า / เงิน / บัตร</option>
                <option>อุปกรณ์การเรียน / หนังสือ</option>
                <option>กุญแจ / ของใช้ส่วนตัว</option>
                <option>อื่นๆ</option>
              </select>
            </div>
            <div class="field">
              <label>วันที่ทำหาย *</label>
              <input type="date" name="item_date" required class="input">
            </div>
          </div>
          <div class="field">
            <label>สถานที่คาดว่าทำหาย *</label>
            <input type="text" name="location" required placeholder="เช่น อาคาร 2 ห้อง 204" class="input">
          </div>
          <div class="field">
            <label>รูปภาพสิ่งของ (ถ้ามี)</label>
            <div class="upload-box">
              <input type="file" name="image_file" accept="image/*" onchange="handleImageSelect(this, 'lostPreview', 'lostImageData')">
              <img id="lostPreview" class="preview-img" alt="ตัวอย่างรูปภาพ">
            </div>
          </div>
          <div class="field">
            <label>ลักษณะเด่น / รายละเอียดเพิ่มเติม</label>
            <textarea name="description" rows="2" class="textarea"></textarea>
          </div>
          <div class="row-2">
            <div class="field">
              <label>ชื่อผู้แจ้ง *</label>
              <input type="text" name="reporter_name" required class="input">
            </div>
            <div class="field">
              <label>ช่องทางติดต่อกลับ *</label>
              <input type="text" name="contact_or_pickup" required placeholder="เบอร์โทร / Line ID" class="input">
            </div>
          </div>
          <button type="submit" class="btn btn-rose">บันทึกข้อมูลแจ้งของหาย</button>
        </form>
      </div>
    </section>

    <section id="view-recordFound" class="hidden">
      <div class="form-box glass">
        <h2 style="color:var(--h-found);">บันทึกข้อมูลของที่เก็บได้ (จุดรับแจ้ง)</h2>
        <p>สำหรับเจ้าหน้าที่/ผู้เก็บได้ บันทึกสิ่งของเข้าคลังเพื่อรอเจ้าของมาติดต่อรับคืน</p>
        <form method="POST" action="/add" enctype="multipart/form-data">
          <input type="hidden" name="type" value="found">
          <input type="hidden" name="image_data" id="foundImageData">
          <div class="field">
            <label>ชื่อสิ่งของที่พบ *</label>
            <input type="text" name="item_name" required placeholder="เช่น กระเป๋าสตางค์สีดำ, กุญแจรถ" class="input">
          </div>
          <div class="row-2">
            <div class="field">
              <label>หมวดหมู่</label>
              <select name="category" class="select">
                <option>อุปกรณ์ไอที / มือถือ</option>
                <option>กระเป๋า / เงิน / บัตร</option>
                <option>อุปกรณ์การเรียน / หนังสือ</option>
                <option>กุญแจ / ของใช้ส่วนตัว</option>
                <option>อื่นๆ</option>
              </select>
            </div>
            <div class="field">
              <label>วันที่พบ *</label>
              <input type="date" name="item_date" required class="input">
            </div>
          </div>
          <div class="field">
            <label>จุดที่พบสิ่งของ *</label>
            <input type="text" name="location" required placeholder="เช่น โรงอาหาร โต๊ะที่ 5" class="input">
          </div>
          <div class="field">
            <label>รูปภาพสิ่งของที่พบ (ถ้ามี)</label>
            <div class="upload-box">
              <input type="file" name="image_file" accept="image/*" onchange="handleImageSelect(this, 'foundPreview', 'foundImageData')">
              <img id="foundPreview" class="preview-img" alt="ตัวอย่างรูปภาพ">
            </div>
          </div>
          <div class="field">
            <label>รายละเอียดสิ่งของ</label>
            <textarea name="description" rows="2" class="textarea"></textarea>
          </div>
          <div class="row-2">
            <div class="field">
              <label>ผู้บันทึก / ผู้เก็บได้ *</label>
              <input type="text" name="reporter_name" required class="input">
            </div>
            <div class="field">
              <label>จุดติดต่อรับคืน *</label>
              <input type="text" name="contact_or_pickup" required value="ห้องปกครอง / จุดประชาสัมพันธ์" class="input">
            </div>
          </div>
          <button type="submit" class="btn btn-indigo btn-full">บันทึกเข้าคลังของหาย</button>
        </form>
      </div>
    </section>
  </main>

  <div id="imgModal" class="modal-backdrop hidden" onclick="closeImageModal()">
    <img id="modalImg" class="zoomed" src="" alt="ขยายรูปภาพ">
  </div>

  <div id="qrModal" class="modal-backdrop hidden" onclick="if(event.target===this) closeQrModal()">
    <div class="qr-card glass">
      <h2>สแกน QR Code เพื่อเปิด FindBack</h2>
      <p>ใช้กล้องมือถือสแกนเพื่อเข้าใช้งานระบบแจ้งของหายและส่งคืนได้ทันที</p>
      <div class="qr-frame">
        <img id="qrCodeImg" src="/qr" alt="FindBack QR Code">
      </div>
      <div class="qr-url-row">
        <input type="text" id="qrUrlInput" value="{{ mobile_url }}" class="input" placeholder="ระบุลิงก์ URL...">
        <button type="button" onclick="updateQrCode()" class="btn btn-indigo" style="padding:8px 12px;font-size:12px;">สร้างใหม่</button>
      </div>
      <div class="qr-actions">
        <button type="button" onclick="downloadQrPng()" class="btn btn-emerald" style="font-size:13px;padding:10px;">บันทึกรูป PNG</button>
        <button type="button" onclick="closeQrModal()" class="btn btn-ghost">ปิดหน้าต่าง</button>
      </div>
    </div>
  </div>

  <script>
    function switchTab(tabName, btn) {
      ['feed', 'reportLost', 'recordFound'].forEach(function(t) {
        document.getElementById('view-' + t).classList.add('hidden');
      });
      document.getElementById('view-' + tabName).classList.remove('hidden');
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
    }

    function toggleTheme() {
      var isDark = document.body.classList.toggle('dark-mode');
      var btn = document.getElementById('themeToggleBtn');
      btn.textContent = isDark ? '✨ Default Mode' : '🌙 Dark Mode';
      localStorage.setItem('findback_mode', isDark ? 'dark' : 'default');
    }

    if (localStorage.getItem('findback_mode') === 'dark') {
      document.body.classList.add('dark-mode');
      document.getElementById('themeToggleBtn').textContent = '✨ Default Mode';
    }

    function handleImageSelect(input, previewId, hiddenId) {
      var file = input.files[0];
      var preview = document.getElementById(previewId);
      var hidden = document.getElementById(hiddenId);
      if (!file) { preview.style.display = 'none'; hidden.value = ''; return; }
      var reader = new FileReader();
      reader.onload = function(e) {
        var img = new Image();
        img.onload = function() {
          var canvas = document.createElement('canvas');
          var maxW = 640, w = img.width, h = img.height;
          if (w > maxW) { h = Math.round(h * (maxW / w)); w = maxW; }
          canvas.width = w; canvas.height = h;
          canvas.getContext('2d').drawImage(img, 0, 0, w, h);
          var dataUrl = canvas.toDataURL('image/jpeg', 0.78);
          hidden.value = dataUrl;
          preview.src = dataUrl;
          preview.style.display = 'block';
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }

    function openImageModal(src) {
      document.getElementById('modalImg').src = src;
      document.getElementById('imgModal').classList.remove('hidden');
    }
    function closeImageModal() {
      document.getElementById('imgModal').classList.add('hidden');
      document.getElementById('modalImg').src = '';
    }

    function openQrModal() {
      document.getElementById('qrModal').classList.remove('hidden');
    }
    function closeQrModal() {
      document.getElementById('qrModal').classList.add('hidden');
    }
    function updateQrCode() {
      var url = document.getElementById('qrUrlInput').value.trim();
      if (url) {
        document.getElementById('qrCodeImg').src = '/qr?url=' + encodeURIComponent(url);
      }
    }
    function downloadQrPng() {
      var img = document.getElementById('qrCodeImg');
      var canvas = document.createElement('canvas');
      canvas.width = 480;
      canvas.height = 480;
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, 480, 480);
      ctx.drawImage(img, 30, 30, 420, 420);
      var a = document.createElement('a');
      a.download = 'FindBack_QR.png';
      a.href = canvas.toDataURL('image/png');
      a.click();
    }
  </script>
</body>
</html>
"""


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_public_url():
    host = request.host
    if host.startswith("127.0.0.1") or host.startswith("localhost"):
        return f"http://{get_local_ip()}:5050"
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    return f"{proto}://{host}"


def make_qr_svg(text):
    data = text.encode("utf-8")
    versions = [
        (1, 21, 19, 7, [], 0),
        (2, 25, 34, 10, [6, 18], 7),
        (3, 29, 55, 15, [6, 22], 7),
        (4, 33, 80, 20, [6, 26], 7),
        (5, 37, 108, 26, [6, 30], 7),
    ]
    ver_info = None
    for v, size, data_cw, ecc_cw, align, rem_bits in versions:
        if len(data) <= data_cw - 2:
            ver_info = (v, size, data_cw, ecc_cw, align, rem_bits)
            break
    if not ver_info:
        return ""
    ver, size, data_cw, ecc_cw, align, rem_bits = ver_info

    bits = [0, 1, 0, 0]
    for i in range(7, -1, -1):
        bits.append((len(data) >> i) & 1)
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    for _ in range(min(4, data_cw * 8 - len(bits))):
        bits.append(0)
    while len(bits) % 8 != 0:
        bits.append(0)

    cw = []
    for i in range(0, len(bits), 8):
        val = 0
        for b in bits[i:i+8]:
            val = (val << 1) | b
        cw.append(val)
    pad_bytes = [0xEC, 0x11]
    idx = 0
    while len(cw) < data_cw:
        cw.append(pad_bytes[idx % 2])
        idx += 1

    exp = [0] * 512
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D
    for i in range(255, 512):
        exp[i] = exp[i - 255]

    def gf_mul(a, b):
        return 0 if (a == 0 or b == 0) else exp[log[a] + log[b]]

    gen = [1]
    for i in range(ecc_cw):
        new_gen = [0] * (len(gen) + 1)
        for j in range(len(gen)):
            new_gen[j] ^= gen[j]
            new_gen[j + 1] ^= gf_mul(gen[j], exp[i])
        gen = new_gen

    rem = [0] * ecc_cw
    for b in cw:
        factor = b ^ rem[0]
        rem = rem[1:] + [0]
        for j in range(ecc_cw):
            rem[j] ^= gf_mul(gen[j + 1], factor)

    all_cw = cw + rem
    all_bits = []
    for b in all_cw:
        for i in range(7, -1, -1):
            all_bits.append((b >> i) & 1)
    all_bits.extend([0] * rem_bits)

    grid = [[0] * size for _ in range(size)]
    func = [[False] * size for _ in range(size)]

    def set_mod(r, c, val, is_func=True):
        if 0 <= r < size and 0 <= c < size:
            grid[r][c] = 1 if val else 0
            if is_func:
                func[r][c] = True

    for fr, fc in [(0, 0), (0, size - 7), (size - 7, 0)]:
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                r, c = fr + dr, fc + dc
                if 0 <= r < size and 0 <= c < size:
                    in_outer = (0 <= dr <= 6 and (dc in (0, 6))) or (0 <= dc <= 6 and (dr in (0, 6)))
                    in_inner = (2 <= dr <= 4 and 2 <= dc <= 4)
                    set_mod(r, c, in_outer or in_inner)

    for ar in align:
        for ac in align:
            if (ar == 6 and ac == 6) or (ar == 6 and ac == size - 7) or (ar == size - 7 and ac == 6):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    set_mod(ar + dr, ac + dc, max(abs(dr), abs(dc)) != 1)

    for i in range(8, size - 8):
        set_mod(6, i, i % 2 == 0)
        set_mod(i, 6, i % 2 == 0)

    for i in range(9):
        if i != 6:
            set_mod(8, i, 0)
            set_mod(i, 8, 0)
    for i in range(8):
        set_mod(8, size - 1 - i, 0)
        set_mod(size - 1 - i, 8, 0)
    set_mod(size - 8, 8, 1)

    bit_idx = 0
    upward = True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for r in rows:
            for dc in (0, -1):
                c = col + dc
                if not func[r][c]:
                    b = all_bits[bit_idx] if bit_idx < len(all_bits) else 0
                    bit_idx += 1
                    if (r + c) % 2 == 0:
                        b ^= 1
                    grid[r][c] = b
        upward = not upward
        col -= 2

    fmt = [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0]
    for i in range(6):
        grid[8][i] = fmt[i]
    grid[8][7] = fmt[6]
    grid[8][8] = fmt[7]
    grid[7][8] = fmt[8]
    for i in range(6):
        grid[5 - i][8] = fmt[9 + i]
    for i in range(7):
        grid[size - 1 - i][8] = fmt[i]
    for i in range(8):
        grid[8][size - 8 + i] = fmt[7 + i]

    rects = []
    for r in range(size):
        for c in range(size):
            if grid[r][c] == 1:
                rects.append(f'<rect x="{c+2}" y="{r+2}" width="1" height="1"/>')
    total = size + 4
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" width="220" height="220" shape-rendering="crispEdges"><rect width="{total}" height="{total}" fill="#ffffff"/><g fill="#0f172a">{"".join(rects)}</g></svg>'


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                item_date TEXT NOT NULL,
                description TEXT,
                reporter_name TEXT NOT NULL,
                contact_or_pickup TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                claimed_by TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                image_data TEXT DEFAULT ''
            )
        """)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(items)").fetchall()]
        if "image_data" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN image_data TEXT DEFAULT ''")

        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat()
            sample_data = [
                ("found", "กระเป๋าสตางค์หนังสีดำ", "กระเป๋า / เงิน / บัตร", "โรงอาหาร ชั้น 1",
                 "2026-11-20", "พบวางอยู่บนโต๊ะ ภายในมีบัตรนักเรียน", "เจ้าหน้าที่ธุรการ",
                 "ติดต่อรับได้ที่ห้องปกครอง", "open", "", now, ""),
                ("lost", "กระเป๋าสตางค์สีดำ", "กระเป๋า / เงิน / บัตร", "แถวโรงอาหาร",
                 "2026-11-20", "ทำหล่นช่วงพักเที่ยง มีบัตรนักเรียนอยู่ข้างใน", "ด.ช. กิตติพงศ์ ม.3/2",
                 "โทร 089-xxx-xxxx", "open", "", now, ""),
            ]
            conn.executemany("""
                INSERT INTO items (type, item_name, category, location, item_date,
                                   description, reporter_name, contact_or_pickup, status, claimed_by, created_at, image_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_data)


def find_smart_matches(items):
    open_lost = [i for i in items if i["type"] == "lost" and i["status"] == "open"]
    open_found = [i for i in items if i["type"] == "found" and i["status"] == "open"]
    matches = []
    for lost in open_lost:
        for found in open_found:
            same_category = lost["category"] == found["category"]
            lost_kw = lost["item_name"][:5].lower()
            found_kw = found["item_name"][:5].lower()
            if same_category and (lost_kw in found["item_name"].lower() or found_kw in lost["item_name"].lower()):
                matches.append({
                    "lost_name": lost["item_name"],
                    "lost_by": lost["reporter_name"],
                    "found_name": found["item_name"],
                    "found_loc": found["location"],
                    "pickup": found["contact_or_pickup"]
                })
    return matches


@app.route("/qr")
def qr_svg():
    target = request.args.get("url", "").strip()
    if not target:
        target = get_public_url()
    svg = make_qr_svg(target)
    return Response(svg, mimetype="image/svg+xml")


@app.route("/")
def index():
    keyword = request.args.get("q", "").strip().lower()
    filter_type = request.args.get("type", "all")
    filter_status = request.args.get("status", "open")

    with get_db() as conn:
        all_items = [dict(row) for row in conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()]

    smart_matches = find_smart_matches(all_items)
    stat_open = sum(1 for i in all_items if i["status"] == "open")
    stat_resolved = sum(1 for i in all_items if i["status"] == "resolved")

    filtered_items = []
    for item in all_items:
        search_blob = f"{item['item_name']} {item['location']} {item['description']} {item['reporter_name']}".lower()
        if keyword and keyword not in search_blob:
            continue
        if filter_type != "all" and item["type"] != filter_type:
            continue
        if filter_status != "all" and item["status"] != filter_status:
            continue
        filtered_items.append(item)

    mobile_url = get_public_url()

    return render_template_string(
        HTML_PAGE,
        items=filtered_items,
        smart_matches=smart_matches,
        stat_open=stat_open,
        stat_resolved=stat_resolved,
        keyword=keyword,
        filter_type=filter_type,
        filter_status=filter_status,
        mobile_url=mobile_url
    )


@app.route("/add", methods=["POST"])
def add_item():
    image_data = request.form.get("image_data", "").strip()
    if not image_data and "image_file" in request.files:
        f = request.files["image_file"]
        if f and f.filename:
            raw = f.read()
            if len(raw) <= 2 * 1024 * 1024:
                mime = f.mimetype or "image/jpeg"
                image_data = f"data:{mime};base64," + base64.b64encode(raw).decode("utf-8")

    with get_db() as conn:
        conn.execute("""
            INSERT INTO items (type, item_name, category, location, item_date,
                               description, reporter_name, contact_or_pickup, status, created_at, image_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
        """, (
            request.form["type"],
            request.form["item_name"],
            request.form["category"],
            request.form["location"],
            request.form["item_date"],
            request.form.get("description", ""),
            request.form["reporter_name"],
            request.form["contact_or_pickup"],
            datetime.now().isoformat(),
            image_data
        ))
    return redirect(url_for("index"))


@app.route("/resolve/<int:item_id>", methods=["POST"])
def resolve_item(item_id):
    claimed_by = request.form.get("claimed_by", "").strip()
    if claimed_by:
        with get_db() as conn:
            conn.execute(
                "UPDATE items SET status = 'resolved', claimed_by = ? WHERE id = ?",
                (claimed_by, item_id)
            )
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port)