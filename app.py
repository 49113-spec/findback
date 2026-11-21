import base64
import json
import os
import secrets
import socket
import sqlite3
import string
import uuid
from datetime import datetime
from flask import Flask, Response, jsonify, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "findback-host-49113-honor-secret")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "lost_found.db")

HOST_USER = "49113"
HOST_PASS = "HONOR"

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
      --cursor-glow: radial-gradient(circle, rgba(99,102,241,0.28) 0%, rgba(56,189,248,0.14) 45%, transparent 72%);
      --cursor-ring: rgba(79, 70, 229, 0.45);
      --sparkle-bg: radial-gradient(circle, rgba(255,255,255,0.95), rgba(129,140,248,0.65));
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
      --cursor-glow: radial-gradient(circle, rgba(56,189,248,0.32) 0%, rgba(168,85,247,0.18) 45%, transparent 72%);
      --cursor-ring: rgba(125, 211, 252, 0.55);
      --sparkle-bg: radial-gradient(circle, rgba(255,255,255,0.95), rgba(56,189,248,0.75));
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
    .badge-open { background: var(--b-open-bg); color: var(--b-open-t); border: 1px solid var(--border); padding: 6px 13px; border-radius: 999px; }
    .badge-done { background: var(--b-done-bg); color: var(--b-done-t); border: 1px solid var(--border); padding: 6px 13px; border-radius: 999px; }
    .badge-host { background: linear-gradient(135deg, rgba(245,158,11,0.25), rgba(217,119,6,0.22)); color: #b45309; border: 1px solid rgba(245,158,11,0.45); padding: 6px 13px; border-radius: 999px; }
    .badge-cohost { background: linear-gradient(135deg, rgba(14,165,233,0.22), rgba(99,102,241,0.22)); color: #0369a1; border: 1px solid rgba(14,165,233,0.45); padding: 6px 13px; border-radius: 999px; }
    body.dark-mode .badge-host { color: #fcd34d; }
    body.dark-mode .badge-cohost { color: #7dd3fc; }
    .pill-btn {
      background: var(--glass); color: var(--text); border: 1px solid var(--border);
      padding: 6px 13px; border-radius: 999px; font-size: 12px; font-weight: bold;
      cursor: pointer; font-family: inherit; transition: 0.2s;
    }
    .pill-btn:hover { transform: scale(1.04); }
    .feed-btn {
      background: linear-gradient(135deg, rgba(251,191,36,0.28), rgba(249,115,22,0.25));
      color: #b45309; border: 1px solid rgba(245,158,11,0.55);
    }
    body.dark-mode .feed-btn { color: #fde047; }
    .nav { padding: 14px 16px 0; }
    .nav-pill-wrap { display: inline-flex; flex-wrap: wrap; gap: 6px; padding: 6px; border-radius: 16px; }
    .tab-btn { border: 1px solid transparent; padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; background: transparent; color: var(--sub); transition: 0.2s; }
    .tab-btn:hover { background: rgba(255, 255, 255, 0.2); color: var(--text); }
    .tab-btn.active { background: linear-gradient(135deg, rgba(79,70,229,0.92), rgba(59,130,246,0.92)); color: #fff; border-color: rgba(255,255,255,0.5); box-shadow: 0 4px 16px rgba(79,70,229,0.35); }
    .main { padding: 20px 16px 44px; }
    .hidden { display: none !important; }
    .toast-banner {
      background: rgba(16, 185, 129, 0.2); color: var(--done);
      border: 1px solid rgba(16, 185, 129, 0.45);
      border-radius: 14px; padding: 11px 16px; margin-bottom: 16px;
      font-size: 13px; font-weight: bold; text-align: center;
    }
    .toast-banner.warn {
      background: rgba(245, 158, 11, 0.22); color: var(--alert-h);
      border-color: rgba(245, 158, 11, 0.5);
    }
    .alert-box { background: var(--alert-bg); backdrop-filter: blur(22px); border: 1px solid var(--alert-bd); border-radius: 18px; padding: 16px 18px; margin-bottom: 20px; }
    .alert-box h2 { font-size: 14px; color: var(--alert-h); margin-bottom: 8px; }
    .alert-item { font-size: 13px; color: var(--alert-t); margin-bottom: 4px; }
    .filter-bar { border-radius: 18px; padding: 14px; display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; }
    .input, .select, .textarea { background: var(--input-bg); border: 1px solid var(--input-bd); border-radius: 12px; padding: 9px 13px; font-size: 14px; font-family: inherit; color: var(--text); outline: none; }
    .input::placeholder, .textarea::placeholder { color: var(--muted); }
    .input:focus, .select:focus, .textarea:focus { border-color: #818cf8; box-shadow: 0 0 0 3px rgba(99,102,241,0.22); }
    .filter-bar .input { flex: 1; min-width: 180px; }
    .btn { border: 1px solid rgba(255,255,255,0.45); border-radius: 12px; padding: 9px 18px; font-size: 14px; font-weight: bold; cursor: pointer; color: #fff; font-family: inherit; transition: 0.2s; }
    .btn:hover { transform: translateY(-1px); filter: brightness(1.06); }
    .btn-indigo { background: linear-gradient(135deg, #4f46e5, #2563eb); }
    .btn-rose { background: linear-gradient(135deg, #f43f5e, #e11d48); width: 100%; padding: 12px; }
    .btn-emerald { background: linear-gradient(135deg, #10b981, #059669); font-size: 12px; padding: 8px 11px; white-space: nowrap; }
    .btn-slate { background: linear-gradient(135deg, #64748b, #475569); font-size: 12px; padding: 8px 12px; width: 100%; }
    .btn-amber { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .btn-full { width: 100%; padding: 12px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 18px; }
    .card { border-radius: 20px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; transition: 0.25s; }
    .card:hover { transform: translateY(-3px); }
    .card.resolved { opacity: 0.76; }

    /* แกลเลอรีรูปภาพในการ์ด */
    .card-gallery { margin-bottom: 12px; }
    .card-img-wrap { width: 100%; height: 180px; border-radius: 14px; overflow: hidden; border: 1px solid var(--border); cursor: zoom-in; position: relative; }
    .card-img-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .img-count-badge {
      position: absolute; bottom: 8px; right: 8px;
      background: rgba(15, 23, 42, 0.75); color: #fff;
      font-size: 11px; font-weight: bold; padding: 3px 9px;
      border-radius: 999px; backdrop-filter: blur(6px);
    }
    .thumb-strip {
      display: flex; gap: 6px; margin-top: 7px; overflow-x: auto; padding-bottom: 2px;
    }
    .thumb-strip img {
      width: 44px; height: 44px; object-fit: cover; border-radius: 8px;
      border: 2px solid transparent; cursor: pointer; opacity: 0.72; transition: 0.15s;
    }
    .thumb-strip img.active, .thumb-strip img:hover {
      border-color: #6366f1; opacity: 1; transform: scale(1.04);
    }

    .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; gap: 6px; }
    .card-top-right { display: flex; align-items: center; gap: 8px; }
    .del-btn {
      background: rgba(244, 63, 94, 0.14); color: var(--h-lost);
      border: 1px solid var(--border); width: 24px; height: 24px;
      border-radius: 999px; font-size: 11px; font-weight: bold;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: 0.2s;
    }
    .del-btn:hover { background: #e11d48; color: #ffffff; transform: scale(1.08); }
    .tag-found { background: var(--t-found-bg); color: var(--t-found-t); border: 1px solid var(--border); font-size: 12px; font-weight: bold; padding: 4px 11px; border-radius: 999px; }
    .tag-lost { background: var(--t-lost-bg); color: var(--t-lost-t); border: 1px solid var(--border); font-size: 12px; font-weight: bold; padding: 4px 11px; border-radius: 999px; }
    .date-txt { font-size: 12px; color: var(--muted); }
    .card h3 { font-size: 17px; margin-bottom: 2px; }
    .cat-txt { font-size: 12px; color: var(--cat); font-weight: bold; margin-bottom: 8px; }
    .desc-txt { font-size: 13px; color: var(--sub); margin-bottom: 12px; }
    .meta { border-top: 1px solid var(--div); padding-top: 10px; font-size: 12px; color: var(--muted); }
    .meta div { margin-bottom: 3px; }
    .meta strong { color: var(--sub); }

    /* ป้ายแสดงรหัสคอนเฟิร์ม 5 หลักเฉพาะเจ้าของโพสต์ / HOST / Co-Host */
    .pin-owner-badge {
      display: inline-block;
      margin-top: 6px;
      background: rgba(245, 158, 11, 0.16);
      color: var(--alert-h);
      border: 1px dashed rgba(245, 158, 11, 0.55);
      border-radius: 8px;
      padding: 4px 9px;
      font-size: 12px;
      font-weight: bold;
      letter-spacing: 0.5px;
    }

    /* คอมเมนต์ / แจ้งเบาะแสใต้การ์ด */
    .clue-box {
      border-top: 1px solid var(--div);
      margin-top: 10px;
      padding-top: 8px;
      font-size: 12px;
    }
    .clue-list {
      max-height: 92px;
      overflow-y: auto;
      margin-bottom: 6px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .clue-item {
      background: var(--input-bg);
      border: 1px solid var(--div);
      border-radius: 8px;
      padding: 4px 8px;
      color: var(--sub);
      word-break: break-word;
    }
    .clue-item strong { color: var(--cat); }
    .clue-form { display: flex; gap: 5px; }
    .clue-form .input { flex: 1; min-width: 0; font-size: 11px; padding: 5px 8px; border-radius: 8px; }
    .clue-btn {
      background: var(--b-open-bg); color: var(--b-open-t);
      border: 1px solid var(--border); border-radius: 8px;
      padding: 5px 9px; font-size: 11px; font-weight: bold; cursor: pointer;
    }
    .clue-btn:hover { filter: brightness(1.08); }

    .card-footer { border-top: 1px solid var(--div); padding-top: 12px; margin-top: 10px; }
    .resolve-stack { display: flex; flex-direction: column; gap: 6px; }
    .resolve-row { display: flex; gap: 6px; }
    .resolve-stack .input { flex: 1; min-width: 0; font-size: 12px; padding: 7px 10px; }
    .pin-input { max-width: 118px; text-align: center; font-weight: bold; letter-spacing: 2px; }
    .done-txt { font-size: 13px; font-weight: bold; color: var(--done); }

    .form-box { max-width: 540px; margin: 0 auto; border-radius: 22px; padding: 26px; }
    .form-box h2 { font-size: 19px; margin-bottom: 4px; }
    .form-box p { font-size: 12px; color: var(--muted); margin-bottom: 18px; }
    .field { margin-bottom: 14px; }
    .field label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: var(--sub); }
    .field .input, .field .select, .field .textarea { width: 100%; }
    .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .pin-setup-box {
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.35);
      border-radius: 14px;
      padding: 12px;
      margin-bottom: 14px;
    }
    .pin-setup-box label { color: var(--cat); }
    .pin-hint { font-size: 11px; color: var(--muted); margin-top: 4px; }

    /* อัปโหลดหลายรูป + ปุ่มลบรูปก่อนโพสต์ */
    .upload-box { border: 1.5px dashed var(--border); background: var(--input-bg); border-radius: 14px; padding: 12px; text-align: center; }
    .upload-box input[type="file"] { width: 100%; font-size: 13px; color: var(--sub); cursor: pointer; }
    .preview-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(105px, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    .preview-grid:empty { display: none; }
    .preview-item {
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--border);
      aspect-ratio: 1 / 1;
      background: rgba(0, 0, 0, 0.08);
    }
    .preview-item img {
      width: 100%; height: 100%; object-fit: cover; display: block;
    }
    .remove-img-btn {
      position: absolute; top: 5px; right: 5px;
      background: rgba(225, 29, 72, 0.92); color: #ffffff;
      border: 1px solid rgba(255,255,255,0.7);
      border-radius: 999px; padding: 3px 8px;
      font-size: 11px; font-weight: bold; cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      transition: 0.15s;
    }
    .remove-img-btn:hover { background: #be123c; transform: scale(1.06); }

    .empty { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted); font-size: 14px; border-radius: 20px; }

    /* Modals */
    .modal-backdrop { position: fixed; inset: 0; z-index: 50; background: rgba(3,7,18,0.75); backdrop-filter: blur(14px); display: flex; align-items: center; justify-content: center; padding: 20px; }
    .zoom-wrap { position: relative; display: flex; flex-direction: column; align-items: center; gap: 10px; }
    .zoom-wrap img.zoomed { max-width: 90vw; max-height: 80vh; border-radius: 18px; border: 1px solid rgba(255,255,255,0.25); }
    .zoom-controls { display: flex; align-items: center; gap: 12px; }
    .auth-card { max-width: 420px; width: 100%; border-radius: 24px; padding: 26px; position: relative; }
    .auth-card h2 { font-size: 21px; margin-bottom: 4px; text-align: center; background: var(--title); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .auth-sub { font-size: 12px; color: var(--sub); text-align: center; margin-bottom: 14px; }
    .auth-tabs {
      display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
      background: var(--input-bg); padding: 5px; border-radius: 12px; margin-bottom: 14px;
    }
    .auth-tab {
      border: none; background: transparent; color: var(--sub);
      padding: 7px; border-radius: 9px; font-size: 13px; font-weight: bold;
      cursor: pointer; font-family: inherit; transition: 0.2s;
    }
    .auth-tab.active {
      background: linear-gradient(135deg, #4f46e5, #2563eb); color: #ffffff;
    }
    .err-msg { background: rgba(225, 29, 72, 0.16); color: var(--h-lost); border: 1px solid rgba(225, 29, 72, 0.35); border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: bold; margin-bottom: 12px; text-align: center; }
    .ok-msg { background: rgba(16, 185, 129, 0.18); color: var(--done); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: bold; margin-bottom: 12px; text-align: center; }
    .divider-txt { text-align: center; font-size: 12px; color: var(--muted); margin: 14px 0; position: relative; }
    .divider-txt::before, .divider-txt::after { content: ""; position: absolute; top: 50%; width: 38%; height: 1px; background: var(--border); }
    .divider-txt::before { left: 0; }
    .divider-txt::after { right: 0; }
    .friend-list { max-height: 200px; overflow-y: auto; margin-top: 14px; border-top: 1px solid var(--div); padding-top: 10px; }
    .friend-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 10px; border-radius: 10px; background: var(--input-bg); margin-bottom: 6px; font-size: 13px; gap: 8px; }
    .role-pill { font-size: 10px; font-weight: bold; padding: 2px 7px; border-radius: 999px; margin-left: 5px; }
    .role-cohost { background: rgba(14,165,233,0.2); color: #0284c7; border: 1px solid rgba(14,165,233,0.4); }
    .role-user { background: rgba(100,116,139,0.18); color: var(--sub); border: 1px solid var(--border); }
    .lock-pill { font-size: 11px; color: var(--muted); font-weight: bold; }
    body.dark-mode .role-cohost { color: #7dd3fc; }

    .qr-card { max-width: 410px; width: 100%; border-radius: 24px; padding: 24px; text-align: center; position: relative; }
    .qr-card h2 { font-size: 19px; margin-bottom: 6px; }
    .qr-card p { font-size: 12px; color: var(--sub); margin-bottom: 14px; }
    .qr-frame { background: #ffffff; padding: 14px; border-radius: 18px; display: inline-block; box-shadow: 0 8px 24px rgba(0,0,0,0.18); margin-bottom: 12px; }
    .qr-frame img { display: block; width: 210px; height: 210px; }
    .qr-url-row { display: flex; gap: 6px; margin-bottom: 12px; }
    .qr-url-row .input { flex: 1; font-size: 12px; padding: 8px 10px; }
    .qr-actions { display: flex; gap: 8px; }
    .qr-actions .btn { flex: 1; font-size: 13px; padding: 10px; }
    .btn-ghost { background: var(--glass); color: var(--text); border: 1px solid var(--border); }

    /* Liquid Glass Cursor & Sparkles */
    .cursor-aura {
      position: fixed; top: 0; left: 0; width: 130px; height: 130px;
      margin-left: -65px; margin-top: -65px; border-radius: 50%;
      background: var(--cursor-glow); pointer-events: none; z-index: 60;
      opacity: 0; transition: opacity 0.25s ease;
    }
    .cursor-ring {
      position: fixed; top: 0; left: 0; width: 28px; height: 28px;
      margin-left: -14px; margin-top: -14px; border-radius: 50%;
      border: 1.5px solid var(--cursor-ring);
      background: rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(4px);
      box-shadow: inset 0 1px 2px rgba(255,255,255,0.65), 0 4px 12px rgba(79,70,229,0.18);
      pointer-events: none; z-index: 61; opacity: 0;
      transition: width 0.2s, height 0.2s, margin 0.2s, opacity 0.25s;
    }
    .cursor-ring.hovering {
      width: 46px; height: 46px; margin-left: -23px; margin-top: -23px;
      background: rgba(255, 255, 255, 0.22);
    }
    .glass-sparkle {
      position: fixed; width: 8px; height: 8px; border-radius: 50%;
      background: var(--sparkle-bg);
      box-shadow: 0 0 8px rgba(129, 140, 248, 0.6);
      pointer-events: none; z-index: 59;
      animation: sparkleFade 0.65s ease-out forwards;
    }
    @keyframes sparkleFade {
      0% { transform: translate(-50%, -50%) scale(1); opacity: 0.9; }
      100% { transform: translate(-50%, -18px) scale(0.15); opacity: 0; }
    }

    /* น้องแมวดำวิ่งหนี + หลับ + กินอาหาร */
    .black-cat-wrap {
      position: fixed; top: 0; left: 0; width: 78px; height: 66px;
      margin-left: -39px; margin-top: -33px;
      pointer-events: none; z-index: 62;
      filter: drop-shadow(0 6px 10px rgba(0, 0, 0, 0.28));
      will-change: transform;
    }
    .cat-svg {
      width: 100%; height: 100%; overflow: visible;
      transition: transform 0.22s ease-out;
    }
    .cat-body-group {
      transform-origin: 55px 72px;
      transition: transform 0.35s ease;
    }
    .cat-alert {
      position: absolute; top: -15px; left: 14px;
      background: #fde047; color: #0f172a; font-weight: bold; font-size: 11px;
      width: 18px; height: 18px; line-height: 18px; text-align: center;
      border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      opacity: 0; transform: scale(0.5); transition: 0.15s ease;
    }
    .black-cat-wrap.fleeing .cat-alert { opacity: 1; transform: scale(1.1); }
    .black-cat-wrap.eating .cat-alert {
      opacity: 1; transform: scale(1.15);
      background: #fb7185; color: #ffffff;
    }
    .black-cat-wrap.fleeing .cat-body-group,
    .black-cat-wrap.eating .cat-body-group { animation: catBounce 0.16s ease-in-out infinite alternate; }
    .black-cat-wrap.fleeing .leg-f1,
    .black-cat-wrap.fleeing .leg-b2 { animation: legSwingA 0.14s ease-in-out infinite alternate; }
    .black-cat-wrap.fleeing .leg-f2,
    .black-cat-wrap.fleeing .leg-b1 { animation: legSwingB 0.14s ease-in-out infinite alternate; }
    .cat-tail { transform-origin: 84px 54px; animation: tailSway 1.6s ease-in-out infinite alternate; }
    .black-cat-wrap.fleeing .cat-tail { animation: tailPuff 0.18s ease-in-out infinite alternate; }

    /* สถานะแมวหลับ */
    .cat-zzz {
      position: absolute; top: -18px; left: 8px;
      font-size: 12px; font-weight: bold; color: #818cf8;
      text-shadow: 0 1px 4px rgba(0,0,0,0.35);
      opacity: 0; pointer-events: none;
    }
    .black-cat-wrap.sleeping .cat-zzz {
      opacity: 1;
      animation: zzzFloat 1.8s ease-in-out infinite;
    }
    .black-cat-wrap.sleeping .cat-body-group {
      transform: translateY(11px) scaleY(0.84);
    }
    .black-cat-wrap.sleeping .cat-tail {
      animation: tailSleep 2.8s ease-in-out infinite alternate;
    }
    .eyes-sleeping { display: none; }
    .black-cat-wrap.sleeping .eyes-awake { display: none; }
    .black-cat-wrap.sleeping .eyes-sleeping { display: inline; }

    .fish-bowl {
      position: fixed; z-index: 61; pointer-events: none;
      font-size: 28px; transform: translate(-50%, -50%) scale(0.4);
      filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
      animation: bowlPop 0.35s ease-out forwards;
    }
    .floating-heart {
      position: fixed; z-index: 63; pointer-events: none;
      font-size: 16px; color: #fb7185;
      animation: heartRise 1.1s ease-out forwards;
    }
    @keyframes bowlPop {
      0% { transform: translate(-50%, -50%) scale(0.3); opacity: 0; }
      100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }
    @keyframes heartRise {
      0% { transform: translate(-50%, 0) scale(0.7); opacity: 1; }
      100% { transform: translate(-50%, -36px) scale(1.25); opacity: 0; }
    }
    @keyframes zzzFloat {
      0% { transform: translate(0, 4px) scale(0.85); opacity: 0.35; }
      50% { transform: translate(-6px, -6px) scale(1.05); opacity: 1; }
      100% { transform: translate(-12px, -16px) scale(0.95); opacity: 0; }
    }
    @keyframes tailSleep {
      0% { transform: rotate(8deg); }
      100% { transform: rotate(14deg); }
    }
    @keyframes catBounce {
      0% { transform: translateY(0px); }
      100% { transform: translateY(-4px); }
    }
    @keyframes legSwingA {
      0% { transform: rotate(-22deg); }
      100% { transform: rotate(22deg); }
    }
    @keyframes legSwingB {
      0% { transform: rotate(22deg); }
      100% { transform: rotate(-22deg); }
    }
    @keyframes tailSway {
      0% { transform: rotate(-4deg); }
      100% { transform: rotate(6deg); }
    }
    @keyframes tailPuff {
      0% { transform: rotate(-8deg) scale(1.04); }
      100% { transform: rotate(10deg) scale(1.08); }
    }
    @media (hover: none) and (pointer: coarse) {
      .cursor-aura, .cursor-ring { display: none; }
    }
  </style>
</head>
<body>
  <div class="liquid-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>

  <!-- Liquid Glass Cursor -->
  <div id="cursorAura" class="cursor-aura"></div>
  <div id="cursorRing" class="cursor-ring"></div>

  <!-- น้องแมวดำตัวเล็ก -->
  <div id="blackCat" class="black-cat-wrap" aria-hidden="true">
    <div id="catAlert" class="cat-alert">!</div>
    <div class="cat-zzz">Z z z</div>
    <svg id="catSvg" class="cat-svg" viewBox="0 0 120 100">
      <g class="cat-body-group" stroke="rgba(255,255,255,0.38)" stroke-width="1.4" stroke-linejoin="round">
        <path class="cat-tail" fill="#0b0f19" d="M84,56 C91,48 93,36 92,26 L96,29 L98,19 L102,22 L104,11 L109,16 L112,8 C115,18 114,32 110,43 L113,43 C109,52 101,60 88,63 Z"/>
        <path class="leg-b1" style="transform-origin:78px 64px" fill="#0b0f19" d="M74,60 L82,62 L92,89 C93,93 87,95 85,91 L73,68 Z"/>
        <path class="leg-b2" style="transform-origin:66px 64px" fill="#0b0f19" d="M63,60 L71,61 L76,90 C77,94 70,95 69,91 L62,67 Z"/>
        <path class="leg-f1" style="transform-origin:46px 62px" fill="#0b0f19" d="M43,58 L51,60 L47,89 C46,93 40,92 40,88 L42,63 Z"/>
        <path class="leg-f2" style="transform-origin:35px 59px" fill="#0b0f19" d="M32,55 L40,58 L32,87 C31,91 25,89 26,85 L31,60 Z"/>
        <path fill="#0b0f19" d="M33,52 C43,32 72,30 86,52 C89,58 86,65 78,65 C65,61 52,61 42,64 C35,65 31,58 33,52 Z"/>
        <path fill="#0b0f19" d="M13,43 C11,36 13,29 18,26 L17,15 L26,22 C30,21 34,21 38,23 L46,16 L45,28 C49,33 49,41 44,47 C38,54 22,55 16,48 C14,46 13,45 13,43 Z"/>
        <!-- ตาตอนตื่น -->
        <g class="eyes-awake">
          <ellipse cx="23" cy="37" rx="5.5" ry="6.8" fill="#fde047" stroke="none"/>
          <ellipse cx="37" cy="38" rx="5.5" ry="6.8" fill="#fde047" stroke="none"/>
          <ellipse id="pupilL" cx="22.5" cy="37" rx="2.1" ry="4.2" fill="#0b0f19" stroke="none"/>
          <ellipse id="pupilR" cx="36.5" cy="38" rx="2.1" ry="4.2" fill="#0b0f19" stroke="none"/>
        </g>
        <!-- ตาตอนหลับ -->
        <g class="eyes-sleeping" fill="none" stroke="#fde047" stroke-width="2.2" stroke-linecap="round">
          <path d="M18,38 Q23,42 28,38"/>
          <path d="M32,39 Q37,43 42,39"/>
        </g>
      </g>
    </svg>
  </div>

  <header class="header">
    <div class="container header-flex">
      <h1>FindBack</h1>
      <div class="badges">
        <span class="badge-open">รอรับคืน/ตามหา: {{ stat_open }}</span>
        <span class="badge-done">ส่งคืนแล้ว: {{ stat_resolved }}</span>
        <button type="button" onclick="feedCat()" id="feedCatBtn" class="pill-btn feed-btn" title="ช่วยส่งคืนของหายให้คนอื่นสำเร็จเพื่อสุ่มอาหารแมว: 1 ชิ้น (49%), 2 ชิ้น (25%), 3 ชิ้น (15%), 4 ชิ้น (10%), 5 ชิ้น (1%)">
          🐟 ให้อาหารแมว (<span id="foodCountDisplay">{{ food_count }}</span>)
        </button>

        {% if is_host %}
          <span class="badge-host">👑 HOST ({{ current_user }})</span>
          <button type="button" onclick="openFriendsModal()" class="pill-btn">👥 จัดการบัญชี & รหัส</button>
          <a href="/logout" class="pill-btn" style="text-decoration:none;">ออกจากระบบ</a>
        {% elif is_cohost %}
          <span class="badge-cohost">🛡️ CO-HOST ({{ display_name or current_user }})</span>
          <button type="button" onclick="openFriendsModal()" class="pill-btn">👥 จัดการบัญชี & รหัส</button>
          <a href="/logout" class="pill-btn" style="text-decoration:none;">ออกจากระบบ</a>
        {% elif current_user %}
          <span class="badge-open">👤 {{ display_name or current_user }}</span>
          <a href="/logout" class="pill-btn" style="text-decoration:none;">ออกจากระบบ</a>
        {% else %}
          <span class="badge-open">🚶 Guest Mode</span>
          <button type="button" onclick="openLoginModal('signin')" class="pill-btn">🔑 Sign In / Sign Up</button>
        {% endif %}

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
    <div id="liveToast" class="toast-banner {% if flash_warn %}warn{% endif %} {% if not flash_msg %}hidden{% endif %}">{{ flash_msg or '' }}</div>

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

    <section id="view-feed">
      <form method="GET" action="/" class="filter-bar glass">
        <input type="text" name="q" value="{{ keyword }}" placeholder="ค้นหาชื่อสิ่งของ, สถานที่, รายละเอียด..." class="input">
        <select name="type" onchange="this.form.submit()" class="select">
          <option value="all" {% if filter_type == 'all' %}selected{% endif %}>ทุกประเภท</option>
          <option value="found" {% if filter_type == 'found' %}selected{% endif %}>เก็บได้ / รอเจ้าของ</option>
          <option value="lost" {% if filter_type == 'lost' %}selected{% endif %}>แจ้งของหาย / ตามหา</option>
        </select>
        <select name="category" onchange="this.form.submit()" class="select">
          <option value="all" {% if filter_category == 'all' %}selected{% endif %}>ทุกหมวดหมู่</option>
          <option value="อุปกรณ์ไอที / มือถือ" {% if filter_category == 'อุปกรณ์ไอที / มือถือ' %}selected{% endif %}>อุปกรณ์ไอที / มือถือ</option>
          <option value="กระเป๋า / เงิน / บัตร" {% if filter_category == 'กระเป๋า / เงิน / บัตร' %}selected{% endif %}>กระเป๋า / เงิน / บัตร</option>
          <option value="อุปกรณ์การเรียน / หนังสือ" {% if filter_category == 'อุปกรณ์การเรียน / หนังสือ' %}selected{% endif %}>อุปกรณ์การเรียน / หนังสือ</option>
          <option value="กุญแจ / ของใช้ส่วนตัว" {% if filter_category == 'กุญแจ / ของใช้ส่วนตัว' %}selected{% endif %}>กุญแจ / ของใช้ส่วนตัว</option>
          <option value="อื่นๆ" {% if filter_category == 'อื่นๆ' %}selected{% endif %}>อื่นๆ</option>
        </select>
        <select name="status" onchange="this.form.submit()" class="select">
          <option value="open" {% if filter_status == 'open' %}selected{% endif %}>กำลังดำเนินการ</option>
          <option value="resolved" {% if filter_status == 'resolved' %}selected{% endif %}>ส่งคืน/ปิดแล้ว</option>
          <option value="all" {% if filter_status == 'all' %}selected{% endif %}>ทุกสถานะ</option>
        </select>
        <button type="submit" class="btn btn-indigo">ค้นหา</button>
      </form>

      <div class="grid">
        {% if not items %}
        <div class="empty glass">ยังไม่มีรายการแจ้งของหายหรือของที่เก็บได้ในระบบ</div>
        {% endif %}

        {% for item in items %}
        <div class="card glass {% if item.status == 'resolved' %}resolved{% endif %}" id="card-{{ item.id }}">
          <div>
            {% if item.images %}
            <div class="card-gallery">
              <div class="card-img-wrap" onclick="openCardGallery({{ item.id }})" title="คลิกเพื่อขยายรูป">
                <img id="main-img-{{ item.id }}" src="{{ item.images[0] }}" data-idx="0" alt="{{ item.item_name }}">
                {% if item.images|length > 1 %}
                <span id="img-badge-{{ item.id }}" class="img-count-badge">📷 1 / {{ item.images|length }}</span>
                {% endif %}
              </div>
              {% if item.images|length > 1 %}
              <div class="thumb-strip">
                {% for img_src in item.images %}
                <img src="{{ img_src }}" class="{% if loop.index0 == 0 %}active{% endif %}" onclick="switchCardThumb({{ item.id }}, {{ loop.index0 }}, this)" alt="รูปที่ {{ loop.index }}">
                {% endfor %}
              </div>
              {% endif %}
            </div>
            {% endif %}

            <div class="card-top">
              {% if item.type == 'found' %}
              <span class="tag-found">เก็บได้ (รอเจ้าของ)</span>
              {% else %}
              <span class="tag-lost">แจ้งของหาย (ตามหา)</span>
              {% endif %}
              <div class="card-top-right">
                <span class="date-txt">{{ item.item_date }}</span>
                {% if item.can_delete %}
                <form method="POST" action="/delete/{{ item.id }}" onsubmit="return confirm('ต้องการลบรายการนี้ใช่หรือไม่? (อาหารแมวที่สะสมไว้จะไม่หาย)');" style="margin:0;">
                  <button type="submit" class="del-btn" title="ลบรายการนี้">✕</button>
                </form>
                {% endif %}
              </div>
            </div>
            <h3>{{ item.item_name }}</h3>
            <div class="cat-txt">{{ item.category }}</div>
            <div class="desc-txt">{{ item.description or 'ไม่มีรายละเอียดเพิ่มเติม' }}</div>
            <div class="meta">
              <div><strong>สถานที่:</strong> {{ item.location }}</div>
              <div><strong>ผู้แจ้ง/ผู้บันทึก:</strong> {{ item.reporter_name }}</div>
              <div><strong>ติดต่อ/จุดรับคืน:</strong> {{ item.contact_or_pickup }}</div>
              {% if item.can_see_code and item.confirm_code %}
              <div class="pin-owner-badge">
                🔑 รหัสคอนเฟิร์มส่งคืน: {{ item.confirm_code }}
              </div>
              {% endif %}
            </div>

            <!-- ช่องคอมเมนต์ / แจ้งเบาะแสใต้โพสต์ -->
            <div class="clue-box">
              {% if item.comments %}
              <div class="clue-list">
                {% for c in item.comments %}
                <div class="clue-item">
                  <strong>{{ c.author_name }}:</strong> {{ c.message }}
                </div>
                {% endfor %}
              </div>
              {% endif %}
              <form method="POST" action="/comment/{{ item.id }}" class="clue-form">
                <input type="text" name="message" required placeholder="💬 แจ้งเบาะแส / สอบถามใต้โพสต์..." class="input">
                <button type="submit" class="clue-btn">ส่ง</button>
              </form>
            </div>
          </div>

          <div class="card-footer">
            {% if item.status == 'resolved' %}
              <span class="done-txt">✔ ปิดรายการแล้ว ({{ item.claimed_by }})</span>
            {% elif item.type == 'lost' and item.is_owner %}
              <form method="POST" action="/resolve/{{ item.id }}" style="margin:0;">
                <input type="hidden" name="self_found" value="1">
                <button type="submit" class="btn btn-slate" title="เจ้าของพบของด้วยตัวเอง ปิดประกาศโดยไม่ได้รับอาหารแมว">
                  ✓ เจอของแล้ว (ปิดประกาศของฉัน)
                </button>
              </form>
            {% else %}
              <form method="POST" action="/resolve/{{ item.id }}" class="resolve-stack">
                <input type="text" name="claimed_by" required placeholder="{% if item.type == 'lost' %}ระบุชื่อผู้เก็บได้ / ผู้ส่งคืน...{% else %}ระบุชื่อเจ้าของตัวจริงที่มารับ...{% endif %}" class="input">
                <div class="resolve-row">
                  <input type="text" name="confirm_code" required maxlength="5" pattern="\d{5}" inputmode="numeric" placeholder="รหัส 5 หลัก" title="กรอกรหัสคอนเฟิร์มตัวเลข 5 หลักที่ผู้โพสต์ตั้งไว้" class="input pin-input">
                  <button type="submit" class="btn btn-emerald" style="flex:1;" title="ยืนยันรหัส 5 หลักเพื่อส่งคืนและสุ่มรับอาหารแมว 1–5 ชิ้น">ยืนยันส่งคืน (สุ่ม 1–5 🐟)</button>
                </div>
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
        <p>กรอกข้อมูลทรัพย์สินที่สูญหาย พร้อมตั้งรหัสคอนเฟิร์ม 5 หลักสำหรับยืนยันตอนรับของคืน</p>
        <form method="POST" action="/add" enctype="multipart/form-data">
          <input type="hidden" name="type" value="lost">
          <input type="hidden" name="images_json" id="lostImagesJson" value="[]">
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

          <div class="pin-setup-box">
            <label>🔑 ตั้งรหัสคอนเฟิร์มตอนรับของคืน (ตัวเลข 5 หลัก) *</label>
            <input type="text" name="confirm_code" required maxlength="5" pattern="\d{5}" inputmode="numeric" placeholder="เช่น 12345 (ตั้งซ้ำกับโพสต์อื่นได้)" class="input" style="margin-top:6px;letter-spacing:3px;font-weight:bold;">
            <div class="pin-hint">เก็บตัวเลข 5 หลักนี้ไว้บอกผู้ที่เก็บของมาคืน เพื่อใช้กดยืนยันส่งมอบและรับรางวัลอาหารแมว</div>
          </div>

          <div class="field">
            <label>รูปภาพสิ่งของ (เพิ่มได้หลายรูป สูงสุด 5 รูป)</label>
            <div class="upload-box">
              <input type="file" id="lostFileInput" accept="image/*" multiple onchange="handleMultiImageSelect(this, 'lostPreviewGrid', 'lostImagesJson')">
              <div id="lostPreviewGrid" class="preview-grid"></div>
            </div>
          </div>
          <div class="field">
            <label>ลักษณะเด่น / รายละเอียดเพิ่มเติม</label>
            <textarea name="description" rows="2" class="textarea"></textarea>
          </div>
          <div class="row-2">
            <div class="field">
              <label>ชื่อผู้แจ้ง *</label>
              <input type="text" name="reporter_name" required value="{{ display_name or current_user or '' }}" class="input">
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
        <p>บันทึกสิ่งของเข้าคลัง พร้อมตั้งรหัสคอนเฟิร์ม 5 หลักสำหรับยืนยันเมื่อเจ้าของตัวจริงมารับคืน</p>
        <form method="POST" action="/add" enctype="multipart/form-data">
          <input type="hidden" name="type" value="found">
          <input type="hidden" name="images_json" id="foundImagesJson" value="[]">
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

          <div class="pin-setup-box">
            <label>🔑 ตั้งรหัสคอนเฟิร์มส่งคืนเจ้าของ (ตัวเลข 5 หลัก) *</label>
            <input type="text" name="confirm_code" required maxlength="5" pattern="\d{5}" inputmode="numeric" placeholder="เช่น 55555 (ตั้งซ้ำกับโพสต์อื่นได้)" class="input" style="margin-top:6px;letter-spacing:3px;font-weight:bold;">
            <div class="pin-hint">ใช้กรอกยืนยันตอนตรวจสอบแล้วว่าเจ้าของตัวจริงมารับของคืน</div>
          </div>

          <div class="field">
            <label>รูปภาพสิ่งของที่พบ (เพิ่มได้หลายรูป สูงสุด 5 รูป)</label>
            <div class="upload-box">
              <input type="file" id="foundFileInput" accept="image/*" multiple onchange="handleMultiImageSelect(this, 'foundPreviewGrid', 'foundImagesJson')">
              <div id="foundPreviewGrid" class="preview-grid"></div>
            </div>
          </div>
          <div class="field">
            <label>รายละเอียดสิ่งของ</label>
            <textarea name="description" rows="2" class="textarea"></textarea>
          </div>
          <div class="row-2">
            <div class="field">
              <label>ผู้บันทึก / ผู้เก็บได้ *</label>
              <input type="text" name="reporter_name" required value="{{ display_name or current_user or '' }}" class="input">
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

  <!-- หน้าต่าง Sign In / Sign Up / Guest Mode -->
  <div id="loginModal" class="modal-backdrop {% if not show_login %}hidden{% endif %}" onclick="if(event.target===this) closeLoginModal()">
    <div class="auth-card glass">
      <h2>FindBack</h2>
      <p class="auth-sub">เข้าสู่ระบบ สมัครสมาชิกใหม่ หรือเข้าใช้งานแบบ Guest</p>

      <div class="auth-tabs">
        <button type="button" id="tabBtnSignIn" class="auth-tab {% if auth_tab != 'signup' %}active{% endif %}" onclick="switchAuthTab('signin')">🔑 Sign In (เข้าสู่ระบบ)</button>
        <button type="button" id="tabBtnSignUp" class="auth-tab {% if auth_tab == 'signup' %}active{% endif %}" onclick="switchAuthTab('signup')">✨ Sign Up (สมัครสมาชิก)</button>
      </div>

      {% if login_error %}
      <div class="err-msg">{{ login_error }}</div>
      {% endif %}
      {% if signup_ok %}
      <div class="ok-msg">{{ signup_ok }}</div>
      {% endif %}

      <!-- ฟอร์ม Sign In -->
      <form id="signInForm" method="POST" action="/login" class="{% if auth_tab == 'signup' %}hidden{% endif %}">
        <div class="field">
          <label>ชื่อผู้ใช้ (Username)</label>
          <input type="text" name="username" required placeholder="กรอกชื่อผู้ใช้..." class="input">
        </div>
        <div class="field">
          <label>รหัสผ่าน (Password)</label>
          <input type="password" name="password" required placeholder="กรอกรหัสผ่าน..." class="input">
        </div>
        <button type="submit" class="btn btn-indigo btn-full">เข้าสู่ระบบ (Sign In)</button>
      </form>

      <!-- ฟอร์ม Sign Up (สมัครเองได้เฉพาะบัญชีธรรมดา) -->
      <form id="signUpForm" method="POST" action="/signup" class="{% if auth_tab != 'signup' %}hidden{% endif %}">
        <div class="field">
          <label>ตั้งชื่อผู้ใช้ (Username) *</label>
          <input type="text" name="username" required placeholder="เช่น somchai99 (ห้ามซ้ำกับคนอื่น)" class="input">
        </div>
        <div class="field">
          <label>ตั้งรหัสผ่าน (Password) *</label>
          <input type="password" name="password" required placeholder="ตั้งรหัสผ่านสำหรับเข้าสู่ระบบ..." class="input">
        </div>
        <div class="field">
          <label>ชื่อแสดงผล / ชื่อเล่น (ไม่บังคับ)</label>
          <input type="text" name="display_name" placeholder="เช่น สมชาย ม.2" class="input">
        </div>
        <button type="submit" class="btn btn-emerald btn-full" style="font-size:14px;padding:12px;">สมัครสมาชิก (Sign Up)</button>
      </form>

      <div class="divider-txt">หรือ</div>
      <form method="POST" action="/guest">
        <button type="submit" class="btn btn-ghost btn-full">🚶 เข้าใช้งานแบบ Guest (ไม่ต้องล็อกอิน)</button>
      </form>
    </div>
  </div>

  <!-- หน้าต่างจัดการบัญชี & สร้าง/ลบรหัส (HOST และ CO-HOST) -->
  {% if is_host or is_cohost %}
  <div id="friendsModal" class="modal-backdrop {% if not show_friends %}hidden{% endif %}" onclick="if(event.target===this) closeFriendsModal()">
    <div class="auth-card glass" style="max-width:460px;">
      {% if is_host %}
        <h2>👑 จัดการบัญชี & รหัส (HOST)</h2>
        <p class="auth-sub">สร้างบัญชีได้ 2 แบบคือ <b>Co-Host</b> และ <b>ธรรมดา</b> พร้อมลบบัญชีได้ทั้งหมด</p>
      {% else %}
        <h2>🛡️ จัดการบัญชี & รหัส (CO-HOST)</h2>
        <p class="auth-sub">สามารถ <b>สร้าง</b> และ <b>ลบ</b> บัญชีแบบ <b>ธรรมดา (User)</b> ได้</p>
      {% endif %}

      {% if friend_msg %}
      <div class="ok-msg">{{ friend_msg }}</div>
      {% endif %}
      {% if friend_err %}
      <div class="err-msg">{{ friend_err }}</div>
      {% endif %}

      <form method="POST" action="/manage/create_user">
        <div class="row-2">
          <div class="field">
            <label>ชื่อผู้ใช้ (Username) *</label>
            <input type="text" name="new_username" required placeholder="เช่น student_01" class="input">
          </div>
          <div class="field">
            <label>รหัสผ่าน (Password) *</label>
            <input type="text" name="new_password" required placeholder="ตั้งรหัสผ่าน..." class="input">
          </div>
        </div>
        <div class="row-2">
          <div class="field">
            <label>ประเภทสิทธิ์บัญชี *</label>
            <select name="role" class="select">
              <option value="user">👤 ธรรมดา (User)</option>
              {% if is_host %}
              <option value="cohost">🛡️ Co-Host (ผู้ช่วยดูแล)</option>
              {% endif %}
            </select>
          </div>
          <div class="field">
            <label>ชื่อแสดงผล (ไม่บังคับ)</label>
            <input type="text" name="display_name" placeholder="เช่น พี่สภานักเรียน" class="input">
          </div>
        </div>
        <button type="submit" class="btn btn-amber btn-full">+ สร้างบัญชี / อัปเดตรหัส</button>
      </form>

      <div class="friend-list">
        <div style="font-size:12px;font-weight:bold;color:var(--sub);margin-bottom:6px;">รายชื่อบัญชีทั้งหมดในระบบ ({{ friends|length }} บัญชี)</div>
        {% if not friends %}
        <div style="font-size:12px;color:var(--muted);text-align:center;padding:10px;">ยังไม่มีบัญชีอื่นในระบบ</div>
        {% endif %}
        {% for f in friends %}
        <div class="friend-row">
          <div>
            <strong>{{ f.username }}</strong>
            {% if f.role == 'cohost' %}
              <span class="role-pill role-cohost">🛡️ Co-Host</span>
            {% else %}
              <span class="role-pill role-user">👤 ธรรมดา</span>
            {% endif %}
            {% if f.display_name %}<div style="color:var(--muted);font-size:11px;">ชื่อแสดงผล: {{ f.display_name }}</div>{% endif %}
          </div>
          {% if is_host or (is_cohost and f.role == 'user') %}
          <form method="POST" action="/manage/delete_user/{{ f.username }}" onsubmit="return confirm('ยืนยันลบบัญชีและรหัสของ {{ f.username }} ใช่หรือไม่?');" style="margin:0;">
            <button type="submit" class="del-btn" title="ลบบัญชีและรหัสนี้">✕</button>
          </form>
          {% else %}
          <span class="lock-pill" title="เฉพาะ HOST เท่านั้นที่ลบบัญชี Co-Host ได้">🔒 Co-Host</span>
          {% endif %}
        </div>
        {% endfor %}
      </div>

      <button type="button" onclick="closeFriendsModal()" class="btn btn-ghost btn-full" style="margin-top:12px;">ปิดหน้าต่าง</button>
    </div>
  </div>
  {% endif %}

  <!-- Modal ขยายรูปภาพ (รองรับเลื่อนดูหลายรูป) -->
  <div id="imgModal" class="modal-backdrop hidden" onclick="if(event.target===this) closeImageModal()">
    <div class="zoom-wrap">
      <img id="modalImg" class="zoomed" src="" alt="ขยายรูปภาพ">
      <div class="zoom-controls">
        <button type="button" id="zoomPrevBtn" onclick="stepZoomGallery(-1)" class="btn btn-ghost" style="padding:7px 14px;font-size:13px;">◀ ก่อนหน้า</button>
        <span id="zoomCounter" style="color:#fff;font-size:13px;font-weight:bold;">1 / 1</span>
        <button type="button" id="zoomNextBtn" onclick="stepZoomGallery(1)" class="btn btn-ghost" style="padding:7px 14px;font-size:13px;">ถัดไป ▶</button>
        <button type="button" onclick="closeImageModal()" class="btn btn-rose" style="width:auto;padding:7px 16px;font-size:13px;">ปิด</button>
      </div>
    </div>
  </div>

  <div id="qrModal" class="modal-backdrop hidden" onclick="if(event.target===this) closeQrModal()">
    <div class="qr-card glass">
      <h2>สแกน QR Code เพื่อเปิด FindBack</h2>
      <p>ระบบแรนด้อมลิงก์ใหม่ให้อัตโนมัติทุกรอบเพื่อความปลอดภัยในการแชร์</p>
      <div class="qr-frame">
        <img id="qrCodeImg" src="/qr?url={{ mobile_url | urlencode }}" alt="FindBack QR Code">
      </div>
      <div class="qr-url-row">
        <input type="text" id="qrUrlInput" value="{{ mobile_url }}" class="input" placeholder="ระบุลิงก์ URL...">
        <button type="button" onclick="randomizeQrLink()" class="btn btn-indigo" style="padding:8px 12px;font-size:12px;">🎲 สุ่มลิงก์ใหม่</button>
      </div>
      <div class="qr-actions">
        <button type="button" onclick="downloadQrPng()" class="btn btn-emerald" style="font-size:13px;padding:10px;">บันทึกรูป PNG</button>
        <button type="button" onclick="closeQrModal()" class="btn btn-ghost">ปิดหน้าต่าง</button>
      </div>
    </div>
  </div>

  <script>
    var BASE_PUBLIC_URL = {{ base_public_url | tojson }};
    var CARD_GALLERIES = {{ card_galleries_json | safe }};
    var activeZoomList = [];
    var activeZoomIdx = 0;

    function showToast(msg, isWarn) {
      var el = document.getElementById('liveToast');
      if (!el) return;
      el.textContent = msg;
      if (isWarn) el.classList.add('warn');
      else el.classList.remove('warn');
      el.classList.remove('hidden');
      clearTimeout(el._timer);
      el._timer = setTimeout(function() { el.classList.add('hidden'); }, 5000);
    }

    function switchTab(tabName, btn) {
      ['feed', 'reportLost', 'recordFound'].forEach(function(t) {
        document.getElementById('view-' + t).classList.add('hidden');
      });
      document.getElementById('view-' + tabName).classList.remove('hidden');
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
    }

    function switchAuthTab(mode) {
      var signInForm = document.getElementById('signInForm');
      var signUpForm = document.getElementById('signUpForm');
      var btnIn = document.getElementById('tabBtnSignIn');
      var btnUp = document.getElementById('tabBtnSignUp');
      if (mode === 'signup') {
        signInForm.classList.add('hidden');
        signUpForm.classList.remove('hidden');
        btnIn.classList.remove('active');
        btnUp.classList.add('active');
      } else {
        signUpForm.classList.add('hidden');
        signInForm.classList.remove('hidden');
        btnUp.classList.remove('active');
        btnIn.classList.add('active');
      }
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

    function openLoginModal(tab) {
      if (tab) switchAuthTab(tab);
      document.getElementById('loginModal').classList.remove('hidden');
    }
    function closeLoginModal() {
      document.getElementById('loginModal').classList.add('hidden');
    }
    function openFriendsModal() {
      var m = document.getElementById('friendsModal');
      if (m) m.classList.remove('hidden');
    }
    function closeFriendsModal() {
      var m = document.getElementById('friendsModal');
      if (m) m.classList.add('hidden');
    }

    /* ระบบเพิ่มรูปได้หลายรูป + ปุ่มลบรูปก่อนโพสต์ */
    var formImageStore = {
      lostImagesJson: [],
      foundImagesJson: []
    };

    function renderFormPreviews(gridId, hiddenId) {
      var list = formImageStore[hiddenId] || [];
      var grid = document.getElementById(gridId);
      var hidden = document.getElementById(hiddenId);
      hidden.value = JSON.stringify(list);
      grid.innerHTML = '';

      list.forEach(function(dataUrl, idx) {
        var wrap = document.createElement('div');
        wrap.className = 'preview-item';

        var img = document.createElement('img');
        img.src = dataUrl;
        img.alt = 'รูปที่ ' + (idx + 1);

        var delBtn = document.createElement('button');
        delBtn.type = 'button';
        delBtn.className = 'remove-img-btn';
        delBtn.textContent = '✕ ลบรูป';
        delBtn.title = 'ลบรูปนี้เพื่อเลือกหรือถ่ายใหม่';
        delBtn.onclick = function() {
          formImageStore[hiddenId].splice(idx, 1);
          renderFormPreviews(gridId, hiddenId);
        };

        wrap.appendChild(img);
        wrap.appendChild(delBtn);
        grid.appendChild(wrap);
      });
    }

    function handleMultiImageSelect(input, gridId, hiddenId) {
      var files = Array.from(input.files || []);
      if (!files.length) return;
      var maxPhotos = 5;
      var currentList = formImageStore[hiddenId] || [];
      var remaining = maxPhotos - currentList.length;

      if (remaining <= 0) {
        showToast('เพิ่มรูปได้สูงสุด ' + maxPhotos + ' รูปต่อรายการ (กดปุ่ม ✕ ลบรูป เพื่อเปลี่ยนรูปได้)', true);
        input.value = '';
        return;
      }

      var toProcess = files.slice(0, remaining);
      if (files.length > remaining) {
        showToast('เลือกได้สูงสุด ' + maxPhotos + ' รูป ระบบนำเข้า ' + remaining + ' รูปแรกให้แล้ว', true);
      }

      toProcess.forEach(function(file) {
        var reader = new FileReader();
        reader.onload = function(e) {
          var img = new Image();
          img.onload = function() {
            var canvas = document.createElement('canvas');
            var maxW = 640, w = img.width, h = img.height;
            if (w > maxW) { h = Math.round(h * (maxW / w)); w = maxW; }
            canvas.width = w; canvas.height = h;
            canvas.getContext('2d').drawImage(img, 0, 0, w, h);
            var dataUrl = canvas.toDataURL('image/jpeg', 0.75);
            formImageStore[hiddenId].push(dataUrl);
            renderFormPreviews(gridId, hiddenId);
          };
          img.src = e.target.result;
        };
        reader.readAsDataURL(file);
      });

      input.value = '';
    }

    /* สลับรูปย่อยบนการ์ด & เปิดแกลเลอรีขยายเต็มจอ */
    function switchCardThumb(itemId, idx, thumbEl) {
      var imgs = CARD_GALLERIES[itemId] || [];
      if (!imgs[idx]) return;
      var mainImg = document.getElementById('main-img-' + itemId);
      if (mainImg) {
        mainImg.src = imgs[idx];
        mainImg.setAttribute('data-idx', idx);
      }
      var badge = document.getElementById('img-badge-' + itemId);
      if (badge) {
        badge.textContent = '📷 ' + (idx + 1) + ' / ' + imgs.length;
      }
      if (thumbEl && thumbEl.parentElement) {
        thumbEl.parentElement.querySelectorAll('img').forEach(function(el) {
          el.classList.remove('active');
        });
        thumbEl.classList.add('active');
      }
    }

    function openCardGallery(itemId) {
      var imgs = CARD_GALLERIES[itemId] || [];
      if (!imgs.length) return;
      var mainImg = document.getElementById('main-img-' + itemId);
      var startIdx = mainImg ? parseInt(mainImg.getAttribute('data-idx') || '0', 10) : 0;
      activeZoomList = imgs;
      activeZoomIdx = startIdx;
      updateZoomModal();
      document.getElementById('imgModal').classList.remove('hidden');
    }

    function updateZoomModal() {
      if (!activeZoomList.length) return;
      document.getElementById('modalImg').src = activeZoomList[activeZoomIdx];
      document.getElementById('zoomCounter').textContent = (activeZoomIdx + 1) + ' / ' + activeZoomList.length;
      var multi = activeZoomList.length > 1;
      document.getElementById('zoomPrevBtn').style.display = multi ? 'inline-block' : 'none';
      document.getElementById('zoomNextBtn').style.display = multi ? 'inline-block' : 'none';
    }

    function stepZoomGallery(delta) {
      if (!activeZoomList.length) return;
      activeZoomIdx = (activeZoomIdx + delta + activeZoomList.length) % activeZoomList.length;
      updateZoomModal();
    }

    function closeImageModal() {
      document.getElementById('imgModal').classList.add('hidden');
      document.getElementById('modalImg').src = '';
    }

    function generateRandomCode(len) {
      var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
      var out = '';
      for (var i = 0; i < len; i++) {
        out += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return out;
    }

    function randomizeQrLink() {
      var newUrl = BASE_PUBLIC_URL + '/go/' + generateRandomCode(6);
      document.getElementById('qrUrlInput').value = newUrl;
      document.getElementById('qrCodeImg').src = '/qr?url=' + encodeURIComponent(newUrl);
    }

    function openQrModal() {
      randomizeQrLink();
      document.getElementById('qrModal').classList.remove('hidden');
    }
    function closeQrModal() {
      document.getElementById('qrModal').classList.add('hidden');
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

    /* Liquid Glass Cursor + Black Cat (Sleep 4s / Wake / Flee / Eat Food) */
    (function() {
      var aura = document.getElementById('cursorAura');
      var ring = document.getElementById('cursorRing');
      var catWrap = document.getElementById('blackCat');
      var catAlert = document.getElementById('catAlert');
      var catSvg = document.getElementById('catSvg');
      var pupilL = document.getElementById('pupilL');
      var pupilR = document.getElementById('pupilR');

      var mouseX = -999, mouseY = -999;
      var auraX = -999, auraY = -999;
      var ringX = -999, ringY = -999;
      var lastSparkleTime = 0;

      var catX = Math.max(90, window.innerWidth - 95);
      var catY = Math.max(90, window.innerHeight - 85);
      var catVx = 0, catVy = 0;
      var facingRight = false;

      var lastNearTime = Date.now();
      var foodTarget = null;
      var eatingUntil = 0;

      function spawnHeart(x, y) {
        var h = document.createElement('div');
        h.className = 'floating-heart';
        h.textContent = '♥';
        h.style.left = (x + (Math.random() - 0.5) * 26) + 'px';
        h.style.top = (y - 20) + 'px';
        document.body.appendChild(h);
        setTimeout(function() { h.remove(); }, 1100);
      }

      window.feedCat = function() {
        fetch('/feed_cat', { method: 'POST' })
          .then(function(r) { return r.json(); })
          .then(function(data) {
            if (!data.ok) {
              showToast('ยังไม่มีอาหารแมว — ช่วยส่งคืนของหายให้คนอื่นเพื่อสุ่มรับอาหารแมว 1–5 ชิ้น 🐟', true);
              return;
            }
            document.getElementById('foodCountDisplay').textContent = data.food_count;
            lastNearTime = Date.now();
            catWrap.classList.remove('sleeping');

            if (foodTarget && foodTarget.el) {
              foodTarget.el.remove();
            }
            var tx = Math.min(window.innerWidth - 90, Math.max(90, catX + (catX > window.innerWidth / 2 ? -110 : 110)));
            var ty = Math.min(window.innerHeight - 80, Math.max(110, catY + (Math.random() - 0.5) * 50));
            var bowl = document.createElement('div');
            bowl.className = 'fish-bowl';
            bowl.textContent = '🐟';
            bowl.style.left = tx + 'px';
            bowl.style.top = ty + 'px';
            document.body.appendChild(bowl);

            foodTarget = { x: tx, y: ty, el: bowl };
            eatingUntil = 0;
            showToast('วางปลาให้น้องแมวแล้ว! เหลืออาหารแมว ' + data.food_count + ' ชิ้น 🐟', false);
          });
      };

      document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (auraX < -500) {
          auraX = ringX = mouseX;
          auraY = ringY = mouseY;
        }
        aura.style.opacity = '1';
        ring.style.opacity = '1';

        var isInteractive = e.target && e.target.closest('button, a, input, select, textarea, .card-img-wrap');
        if (isInteractive) {
          ring.classList.add('hovering');
        } else {
          ring.classList.remove('hovering');
        }

        var now = Date.now();
        if (now - lastSparkleTime > 42) {
          lastSparkleTime = now;
          var sp = document.createElement('div');
          sp.className = 'glass-sparkle';
          sp.style.left = (mouseX + (Math.random() - 0.5) * 14) + 'px';
          sp.style.top = (mouseY + (Math.random() - 0.5) * 14) + 'px';
          document.body.appendChild(sp);
          setTimeout(function() { sp.remove(); }, 650);
        }
      });

      document.addEventListener('touchstart', function(e) {
        if (e.touches && e.touches[0]) {
          mouseX = e.touches[0].clientX;
          mouseY = e.touches[0].clientY;
        }
      }, { passive: true });

      function animateLoop() {
        var now = Date.now();

        if (mouseX > -500) {
          auraX += (mouseX - auraX) * 0.14;
          auraY += (mouseY - auraY) * 0.14;
          ringX += (mouseX - ringX) * 0.32;
          ringY += (mouseY - ringY) * 0.32;
          aura.style.transform = 'translate3d(' + auraX + 'px,' + auraY + 'px,0)';
          ring.style.transform = 'translate3d(' + ringX + 'px,' + ringY + 'px,0)';
        }

        var dx = catX - mouseX;
        var dy = catY - mouseY;
        var dist = Math.hypot(dx, dy);
        var wakeRadius = 220;
        var fleeRadius = 165;

        if (mouseX > -500 && dist < wakeRadius) {
          lastNearTime = now;
        }

        if (foodTarget) {
          lastNearTime = now;
          catWrap.classList.remove('sleeping');
          var fdx = foodTarget.x - catX;
          var fdy = foodTarget.y - catY;
          var fdist = Math.hypot(fdx, fdy);

          if (fdist > 28 && eatingUntil === 0) {
            catVx += (fdx / fdist) * 1.15;
            catVy += (fdy / fdist) * 1.15;
            catWrap.classList.add('fleeing');
            catWrap.classList.remove('eating');
            catAlert.textContent = '♥';
            facingRight = fdx > 0;
          } else {
            if (eatingUntil === 0) {
              eatingUntil = now + 2200;
            }
            catVx *= 0.6;
            catVy *= 0.6;
            catWrap.classList.remove('fleeing');
            catWrap.classList.add('eating');
            catAlert.textContent = '♥';
            if (Math.random() < 0.08) {
              spawnHeart(catX, catY);
            }
            if (now >= eatingUntil) {
              if (foodTarget.el) foodTarget.el.remove();
              foodTarget = null;
              eatingUntil = 0;
              catWrap.classList.remove('eating');
              catAlert.textContent = '!';
              lastNearTime = now;
            }
          }
        } else {
          catWrap.classList.remove('eating');
          catAlert.textContent = '!';

          if (dist < fleeRadius && mouseX > -500) {
            catWrap.classList.remove('sleeping');
            var strength = (fleeRadius - dist) / fleeRadius;
            var nx = dist > 0.1 ? dx / dist : (Math.random() - 0.5);
            var ny = dist > 0.1 ? dy / dist : (Math.random() - 0.5);

            var pad = 65;
            var w = window.innerWidth;
            var h = window.innerHeight;
            if (catX < pad || catX > w - pad || catY < pad + 50 || catY > h - pad) {
              var perpX = -ny;
              var perpY = nx;
              nx = nx * 0.55 + perpX * 0.85;
              ny = ny * 0.55 + perpY * 0.85;
            }

            catVx += nx * (1.8 + strength * 3.4);
            catVy += ny * (1.8 + strength * 3.4);
          }
        }

        catVx *= 0.88;
        catVy *= 0.88;
        catX += catVx;
        catY += catVy;

        var margin = 46;
        var maxW = window.innerWidth - margin;
        var maxH = window.innerHeight - margin;
        if (catX < margin) { catX = margin; catVx = Math.abs(catVx) * 0.5; }
        if (catX > maxW) { catX = maxW; catVx = -Math.abs(catVx) * 0.5; }
        if (catY < margin + 45) { catY = margin + 45; catVy = Math.abs(catVy) * 0.5; }
        if (catY > maxH) { catY = maxH; catVy = -Math.abs(catVy) * 0.5; }

        var speed = Math.hypot(catVx, catVy);
        if (!foodTarget) {
          if (speed > 0.65) {
            catWrap.classList.add('fleeing');
            catWrap.classList.remove('sleeping');
            if (catVx > 0.25) facingRight = true;
            else if (catVx < -0.25) facingRight = false;
          } else {
            catWrap.classList.remove('fleeing');
            if (now - lastNearTime >= 4000) {
              catWrap.classList.add('sleeping');
            } else {
              catWrap.classList.remove('sleeping');
              if (mouseX > -500) {
                facingRight = mouseX > catX;
              }
            }
          }
        }

        if (mouseX > -500 && !catWrap.classList.contains('sleeping')) {
          var targetX = foodTarget ? foodTarget.x : mouseX;
          var targetY = foodTarget ? foodTarget.y : mouseY;
          var lookAngle = Math.atan2(targetY - catY, targetX - catX);
          var lx = Math.cos(lookAngle) * 1.8 * (facingRight ? -1 : 1);
          var ly = Math.sin(lookAngle) * 1.8;
          pupilL.setAttribute('cx', (22.5 + lx).toFixed(1));
          pupilL.setAttribute('cy', (37 + ly).toFixed(1));
          pupilR.setAttribute('cx', (36.5 + lx).toFixed(1));
          pupilR.setAttribute('cy', (38 + ly).toFixed(1));
        }

        catWrap.style.transform = 'translate3d(' + catX.toFixed(1) + 'px,' + catY.toFixed(1) + 'px,0)';
        catSvg.style.transform = facingRight ? 'scaleX(-1)' : 'scaleX(1)';

        requestAnimationFrame(animateLoop);
      }

      requestAnimationFrame(animateLoop);
    })();
  </script>
</body>
</html>
"""


def roll_cat_food():
    """สุ่มจำนวนอาหารแมว 1-5 ชิ้น ตามโอกาส 49%, 25%, 15%, 10%, 1%"""
    roll = secrets.randbelow(100)
    if roll < 49:
        return 1
    elif roll < 74:
        return 2
    elif roll < 89:
        return 3
    elif roll < 99:
        return 4
    else:
        return 5


def parse_images(raw_val):
    if not raw_val:
        return []
    raw_val = raw_val.strip()
    if raw_val.startswith("["):
        try:
            arr = json.loads(raw_val)
            return [x for x in arr if isinstance(x, str) and x.startswith("data:image/")]
        except Exception:
            return []
    if raw_val.startswith("data:image/"):
        return [raw_val]
    return []


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


def get_base_public_url():
    host = request.host
    if host.startswith("127.0.0.1") or host.startswith("localhost"):
        return f"http://{get_local_ip()}:5050"
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    return f"{proto}://{host}"


def generate_random_code(length=6):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


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
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                display_name TEXT DEFAULT '',
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            )
        """)
        u_cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "role" not in u_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS cat_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                food_count INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("INSERT OR IGNORE INTO cat_state (id, food_count) VALUES (1, 0)")

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
                image_data TEXT DEFAULT '',
                owner_user TEXT DEFAULT '',
                confirm_code TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(items)").fetchall()]
        if "image_data" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN image_data TEXT DEFAULT ''")
        if "owner_user" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN owner_user TEXT DEFAULT ''")
        if "confirm_code" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN confirm_code TEXT DEFAULT ''")

        host_row = conn.execute("SELECT username FROM users WHERE username = ?", (HOST_USER,)).fetchone()
        if not host_row:
            conn.execute(
                "INSERT INTO users (username, password_hash, display_name, role, created_at) VALUES (?, ?, ?, 'host', ?)",
                (HOST_USER, generate_password_hash(HOST_PASS), "HOST", datetime.now().isoformat())
            )
        else:
            conn.execute("UPDATE users SET role = 'host' WHERE username = ?", (HOST_USER,))


def ensure_guest_id():
    if "guest_id" not in session:
        session["guest_id"] = uuid.uuid4().hex
    return session["guest_id"]


def get_current_actor_id():
    current_user = session.get("user")
    if current_user:
        return current_user
    return f"guest:{ensure_guest_id()}"


def get_current_role():
    current_user = session.get("user")
    if not current_user:
        return "guest"
    if current_user == HOST_USER:
        return "host"
    return session.get("role", "user")


def is_post_owner(owner_user):
    if not owner_user:
        return False
    return owner_user == get_current_actor_id()


def can_user_delete(owner_user):
    role = get_current_role()
    if role in ("host", "cohost"):
        return True
    return is_post_owner(owner_user)


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


@app.route("/go/<random_code>")
def random_redirect(random_code):
    return redirect(url_for("index"))


@app.route("/qr")
def qr_svg():
    target = request.args.get("url", "").strip()
    if not target:
        target = f"{get_base_public_url()}/go/{generate_random_code(6)}"
    svg = make_qr_svg(target)
    return Response(svg, mimetype="image/svg+xml")


@app.route("/feed_cat", methods=["POST"])
def feed_cat():
    with get_db() as conn:
        row = conn.execute("SELECT food_count FROM cat_state WHERE id = 1").fetchone()
        current_food = row["food_count"] if row else 0
        if current_food <= 0:
            return jsonify({"ok": False, "food_count": 0})
        new_food = current_food - 1
        conn.execute("UPDATE cat_state SET food_count = ? WHERE id = 1", (new_food,))
    return jsonify({"ok": True, "food_count": new_food})


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    with get_db() as conn:
        user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user_row and check_password_hash(user_row["password_hash"], password):
        session["user"] = user_row["username"]
        session["display_name"] = user_row["display_name"] or user_row["username"]
        session["role"] = "host" if user_row["username"] == HOST_USER else (user_row["role"] or "user")
        session["mode_chosen"] = True
        session.pop("login_error", None)
    else:
        session["login_error"] = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
        session["auth_tab"] = "signin"
    return redirect(url_for("index"))


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    display_name = request.form.get("display_name", "").strip()

    if not username or not password:
        session["login_error"] = "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน"
        session["auth_tab"] = "signup"
        return redirect(url_for("index"))

    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if exists:
            session["login_error"] = f"ชื่อผู้ใช้ '{username}' มีคนใช้แล้ว กรุณาตั้งชื่ออื่น"
            session["auth_tab"] = "signup"
            return redirect(url_for("index"))

        # สมัครสมาชิกเองจะได้สิทธิ์ 'user' (ธรรมดา) เท่านั้น ไม่สามารถสร้าง Co-Host ได้
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role, created_at) VALUES (?, ?, ?, 'user', ?)",
            (username, generate_password_hash(password), display_name, datetime.now().isoformat())
        )

    session["user"] = username
    session["display_name"] = display_name or username
    session["role"] = "user"
    session["mode_chosen"] = True
    session.pop("login_error", None)
    session["flash_msg"] = f"สมัครสมาชิกและเข้าสู่ระบบสำเร็จ ยินดีต้อนรับคุณ {display_name or username}!"
    session["flash_warn"] = False
    return redirect(url_for("index"))


@app.route("/guest", methods=["POST"])
def enter_guest():
    ensure_guest_id()
    session.pop("user", None)
    session.pop("display_name", None)
    session.pop("role", None)
    session.pop("login_error", None)
    session["mode_chosen"] = True
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("display_name", None)
    session.pop("role", None)
    session.pop("mode_chosen", None)
    session.pop("login_error", None)
    return redirect(url_for("index"))


@app.route("/manage/create_user", methods=["POST"])
def manage_create_user():
    actor_role = get_current_role()
    if actor_role not in ("host", "cohost"):
        return redirect(url_for("index"))

    new_user = request.form.get("new_username", "").strip()
    new_pass = request.form.get("new_password", "").strip()
    disp = request.form.get("display_name", "").strip()
    requested_role = request.form.get("role", "user").strip()

    # เฉพาะ HOST เท่านั้นที่สร้าง Co-Host ได้ ส่วน Co-Host สร้างได้เฉพาะ 'user' (ธรรมดา)
    if actor_role == "host":
        target_role = requested_role if requested_role in ("user", "cohost") else "user"
    else:
        target_role = "user"

    if new_user and new_pass and new_user != HOST_USER:
        role_label = "Co-Host" if target_role == "cohost" else "ธรรมดา"
        with get_db() as conn:
            existing = conn.execute("SELECT role FROM users WHERE username = ?", (new_user,)).fetchone()
            if existing:
                # ป้องกัน Co-Host แก้ไขบัญชีระดับ HOST หรือ Co-Host คนอื่น
                if actor_role == "cohost" and existing["role"] != "user":
                    session["friend_err"] = "Co-Host ไม่สามารถแก้ไขรหัสของบัญชีระดับ HOST หรือ Co-Host ได้"
                else:
                    conn.execute(
                        "UPDATE users SET password_hash = ?, display_name = ?, role = ? WHERE username = ?",
                        (generate_password_hash(new_pass), disp, target_role, new_user)
                    )
                    session["friend_msg"] = f"อัปเดตบัญชี '{new_user}' ({role_label}) เรียบร้อยแล้ว"
            else:
                conn.execute(
                    "INSERT INTO users (username, password_hash, display_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                    (new_user, generate_password_hash(new_pass), disp, target_role, datetime.now().isoformat())
                )
                session["friend_msg"] = f"สร้างบัญชี '{new_user}' ({role_label}) เรียบร้อยแล้ว"
    session["show_friends"] = True
    return redirect(url_for("index"))


@app.route("/manage/delete_user/<username>", methods=["POST"])
def manage_delete_user(username):
    actor_role = get_current_role()
    if actor_role not in ("host", "cohost") or username == HOST_USER:
        return redirect(url_for("index"))

    with get_db() as conn:
        target = conn.execute("SELECT role FROM users WHERE username = ?", (username,)).fetchone()
        if not target:
            session["show_friends"] = True
            return redirect(url_for("index"))

        if actor_role == "cohost" and target["role"] != "user":
            session["friend_err"] = "Co-Host สามารถลบบัญชีแบบธรรมดาได้เท่านั้น"
        else:
            conn.execute("DELETE FROM users WHERE username = ?", (username,))
            session["friend_msg"] = f"ลบบัญชีและรหัสของ '{username}' เรียบร้อยแล้ว"

    session["show_friends"] = True
    return redirect(url_for("index"))


@app.route("/")
def index():
    ensure_guest_id()
    keyword = request.args.get("q", "").strip().lower()
    filter_type = request.args.get("type", "all")
    filter_category = request.args.get("category", "all")
    filter_status = request.args.get("status", "open")

    current_user = session.get("user")
    display_name = session.get("display_name")
    role = get_current_role()
    is_host = (role == "host")
    is_cohost = (role == "cohost")

    login_error = session.pop("login_error", None)
    signup_ok = session.pop("signup_ok", None)
    auth_tab = session.pop("auth_tab", "signin")
    friend_msg = session.pop("friend_msg", None)
    friend_err = session.pop("friend_err", None)
    flash_msg = session.pop("flash_msg", None)
    flash_warn = session.pop("flash_warn", False)
    show_friends = session.pop("show_friends", False)
    show_login = (not session.get("mode_chosen")) or bool(login_error)

    with get_db() as conn:
        all_items = [dict(row) for row in conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()]
        all_comments = [dict(row) for row in conn.execute("SELECT * FROM comments ORDER BY id ASC").fetchall()]
        food_row = conn.execute("SELECT food_count FROM cat_state WHERE id = 1").fetchone()
        food_count = food_row["food_count"] if food_row else 0
        friends = []
        if is_host or is_cohost:
            friends = [dict(row) for row in conn.execute(
                "SELECT username, display_name, role FROM users WHERE username != ? ORDER BY created_at DESC",
                (HOST_USER,)
            ).fetchall()]

    comments_by_item = {}
    for c in all_comments:
        comments_by_item.setdefault(c["item_id"], []).append(c)

    smart_matches = find_smart_matches(all_items)
    stat_open = sum(1 for i in all_items if i["status"] == "open")
    stat_resolved = sum(1 for i in all_items if i["status"] == "resolved")

    filtered_items = []
    card_galleries = {}
    for item in all_items:
        search_blob = f"{item['item_name']} {item['location']} {item['description']} {item['reporter_name']}".lower()
        if keyword and keyword not in search_blob:
            continue
        if filter_type != "all" and item["type"] != filter_type:
            continue
        if filter_category != "all" and item["category"] != filter_category:
            continue
        if filter_status != "all" and item["status"] != filter_status:
            continue
        owner_u = item.get("owner_user", "")
        owner_flag = is_post_owner(owner_u)
        item["is_owner"] = owner_flag
        item["can_delete"] = can_user_delete(owner_u)
        item["can_see_code"] = owner_flag or is_host or is_cohost
        item["comments"] = comments_by_item.get(item["id"], [])
        imgs = parse_images(item.get("image_data", ""))
        item["images"] = imgs
        if imgs:
            card_galleries[str(item["id"])] = imgs
        filtered_items.append(item)

    base_public_url = get_base_public_url()
    mobile_url = f"{base_public_url}/go/{generate_random_code(6)}"

    return render_template_string(
        HTML_PAGE,
        items=filtered_items,
        card_galleries_json=json.dumps(card_galleries),
        smart_matches=smart_matches,
        stat_open=stat_open,
        stat_resolved=stat_resolved,
        food_count=food_count,
        keyword=keyword,
        filter_type=filter_type,
        filter_category=filter_category,
        filter_status=filter_status,
        base_public_url=base_public_url,
        mobile_url=mobile_url,
        current_user=current_user,
        display_name=display_name,
        is_host=is_host,
        is_cohost=is_cohost,
        friends=friends,
        show_login=show_login,
        login_error=login_error,
        signup_ok=signup_ok,
        auth_tab=auth_tab,
        show_friends=show_friends,
        friend_msg=friend_msg,
        friend_err=friend_err,
        flash_msg=flash_msg,
        flash_warn=flash_warn
    )


@app.route("/add", methods=["POST"])
def add_item():
    ensure_guest_id()
    session["mode_chosen"] = True
    owner_user = get_current_actor_id()

    confirm_code = request.form.get("confirm_code", "").strip()
    if len(confirm_code) != 5 or not confirm_code.isdigit():
        session["flash_msg"] = "กรุณาตั้งรหัสคอนเฟิร์มส่งคืนเป็นตัวเลข 5 หลักให้ถูกต้อง (เช่น 12345)"
        session["flash_warn"] = True
        return redirect(url_for("index"))

    # รองรับหลายรูปภาพ (JSON array สูงสุด 5 รูป)
    imgs = parse_images(request.form.get("images_json", "[]"))
    if not imgs and "image_file" in request.files:
        for f in request.files.getlist("image_file"):
            if f and f.filename and len(imgs) < 5:
                raw = f.read()
                if len(raw) <= 2 * 1024 * 1024:
                    mime = f.mimetype or "image/jpeg"
                    imgs.append(f"data:{mime};base64," + base64.b64encode(raw).decode("utf-8"))

    images_stored = json.dumps(imgs[:5]) if imgs else ""

    with get_db() as conn:
        conn.execute("""
            INSERT INTO items (type, item_name, category, location, item_date,
                               description, reporter_name, contact_or_pickup, status, created_at, image_data, owner_user, confirm_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?)
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
            images_stored,
            owner_user,
            confirm_code
        ))
    session["flash_msg"] = f"บันทึกรายการสำเร็จ! (รหัสคอนเฟิร์ม 5 หลักของคุณคือ {confirm_code})"
    session["flash_warn"] = False
    return redirect(url_for("index"))


@app.route("/comment/<int:item_id>", methods=["POST"])
def add_comment(item_id):
    msg = request.form.get("message", "").strip()
    if msg:
        author = session.get("display_name") or session.get("user") or "ผู้ใช้งานทั่วไป"
        with get_db() as conn:
            exists = conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone()
            if exists:
                conn.execute(
                    "INSERT INTO comments (item_id, author_name, message, created_at) VALUES (?, ?, ?, ?)",
                    (item_id, author, msg[:250], datetime.now().isoformat())
                )
    return redirect(url_for("index"))


@app.route("/resolve/<int:item_id>", methods=["POST"])
def resolve_item(item_id):
    self_found = request.form.get("self_found") == "1"
    claimed_by = request.form.get("claimed_by", "").strip()
    entered_code = request.form.get("confirm_code", "").strip()

    with get_db() as conn:
        row = conn.execute(
            "SELECT type, status, reporter_name, owner_user, confirm_code FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()
        if not row or row["status"] != "open":
            return redirect(url_for("index"))

        owner_flag = is_post_owner(row["owner_user"] or "")

        # กรณีเจ้าของโพสต์ "แจ้งของหาย" กดปิดประกาศของตัวเอง -> ไม่แจกอาหารแมว
        if row["type"] == "lost" and (owner_flag or self_found):
            conn.execute(
                "UPDATE items SET status = 'resolved', claimed_by = ? WHERE id = ?",
                ("เจ้าของพบของเองแล้ว", item_id)
            )
            session["flash_msg"] = "ปิดประกาศเรียบร้อยแล้ว (เจ้าของพบของด้วยตัวเอง จึงไม่ได้รับรางวัลอาหารแมว)"
            session["flash_warn"] = True
            return redirect(url_for("index"))

        if not claimed_by:
            return redirect(url_for("index"))

        # ตรวจสอบรหัสคอนเฟิร์ม 5 หลักก่อนปิดเคสส่งคืน
        saved_code = (row["confirm_code"] or "").strip()
        if saved_code and entered_code != saved_code:
            session["flash_msg"] = "❌ รหัสคอนเฟิร์ม 5 หลักไม่ถูกต้อง! กรุณาตรวจสอบรหัสกับผู้โพสต์ก่อนกดยืนยันส่งคืน"
            session["flash_warn"] = True
            return redirect(url_for("index"))

        # ป้องกันพิมพ์ชื่อซ้ำกับชื่อผู้โพสต์เพื่อปั๊มรางวัล
        if claimed_by.lower() == (row["reporter_name"] or "").strip().lower():
            session["flash_msg"] = "ชื่อผู้ส่งคืน/ผู้รับคืนต้องไม่ซ้ำกับชื่อผู้โพสต์รายการ"
            session["flash_warn"] = True
            return redirect(url_for("index"))

        reward_food = roll_cat_food()
        label_prefix = "ผู้เก็บได้: " if row["type"] == "lost" else "ผู้รับคืน: "
        conn.execute(
            "UPDATE items SET status = 'resolved', claimed_by = ? WHERE id = ?",
            (f"{label_prefix}{claimed_by} • รหัสยืนยันผ่าน ✔", item_id)
        )
        conn.execute(
            "UPDATE cat_state SET food_count = food_count + ? WHERE id = 1",
            (reward_food,)
        )
        fish_icons = "🐟" * reward_food
        session["flash_warn"] = False
        if reward_food == 5:
            session["flash_msg"] = f"🎉 แจ็กพอต (1%)! ยืนยันรหัส 5 หลักผ่านและส่งคืนสำเร็จ สุ่มได้รับอาหารแมว +{reward_food} ชิ้น {fish_icons}"
        else:
            session["flash_msg"] = f"ยืนยันรหัส 5 หลักผ่านและส่งคืนสำเร็จ! สุ่มได้รับอาหารแมว +{reward_food} ชิ้น {fish_icons}"

    return redirect(url_for("index"))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    with get_db() as conn:
        row = conn.execute("SELECT owner_user FROM items WHERE id = ?", (item_id,)).fetchone()
        if row and can_user_delete(row["owner_user"] or ""):
            conn.execute("DELETE FROM comments WHERE item_id = ?", (item_id,))
            conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port)
