#!/usr/bin/env python3
"""Observer for Zeruel synthetic probe execution on Brave / Desktop browser.
Captures browser window via Win32 PrintWindow (PW_RENDERFULLCONTENT) and desktop GDI,
detects probe completion (synthetic_success), account picker, or pause/restart states.
Brings Brave tab to foreground before reading.
Writes results to log file. Never handles credentials or secrets.
"""

import os
import sys
import time
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
import ctypes
import win32service, win32gui, win32con, win32ui, win32api
import pytesseract
from PIL import Image

LOG_DEFAULT = r"D:\SystemHope\renewal\log.txt"
PW_RENDERFULLCONTENT = 2

def attach_desktop():
    try:
        hwinsta = win32service.OpenWindowStation("WinSta0", False, win32con.MAXIMUM_ALLOWED)
        hwinsta.SetProcessWindowStation()
        hdesk = win32service.OpenDesktop("Default", 0, False, win32con.MAXIMUM_ALLOWED)
        hdesk.SetThreadDesktop()
        return True
    except Exception:
        return False

def find_browser_window():
    res = []
    def cb(h, _):
        try:
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h)
                cls = win32gui.GetClassName(h)
                if "Chrome_WidgetWin_1" in cls:
                    if any(k in t.lower() for k in ["zeruel", "brave", "google"]):
                        res.append((h, t))
        except Exception:
            pass
        return True
    try:
        win32gui.EnumWindows(cb, None)
    except Exception:
        pass
    # Prefer window with Zeruel in title if already present
    zeruel_wins = [w for w in res if "zeruel" in w[1].lower()]
    if zeruel_wins:
        return zeruel_wins[0]
    return res[0] if res else (None, "")

def bring_tab_to_front(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd):
        return ""
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(win32con.VK_MENU, 0, 0, 0)
        user32.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        return win32gui.GetWindowText(hwnd)
    except Exception:
        return win32gui.GetWindowText(hwnd) if win32gui.IsWindow(hwnd) else ""

def capture_window_or_desktop(hwnd):
    # 1. Try PrintWindow on the browser window
    if hwnd and win32gui.IsWindow(hwnd):
        try:
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            w, h = r - l, b - t
            if w > 100 and h > 100:
                hdc = win32gui.GetDC(hwnd)
                srcdc = win32ui.CreateDCFromHandle(hdc)
                memdc = srcdc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(srcdc, w, h)
                memdc.SelectObject(bmp)
                res = ctypes.windll.user32.PrintWindow(hwnd, memdc.GetSafeHdc(), PW_RENDERFULLCONTENT)
                info = bmp.GetInfo()
                bits = bmp.GetBitmapBits(True)
                win32gui.ReleaseDC(hwnd, hdc)
                if res:
                    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bits, "raw", "BGRX", 0, 1)
                    ext = img.getextrema()
                    if ext != ((0, 0), (0, 0), (0, 0)):
                        return img
        except Exception:
            pass

    # 2. Fallback to desktop GDI capture / ImageGrab
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        if img:
            return img
    except Exception:
        pass

    try:
        hdesk_win = win32gui.GetDesktopWindow()
        l, t, r, b = win32gui.GetWindowRect(hdesk_win)
        w, h = r - l, b - t
        hwindc = win32gui.GetWindowDC(hdesk_win)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, w, h)
        memdc.SelectObject(bmp)
        memdc.BitBlt((0, 0), (w, h), srcdc, (0, 0), win32con.SRCCOPY)
        info = bmp.GetInfo()
        bits = bmp.GetBitmapBits(True)
        return Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bits, "raw", "BGRX", 0, 1)
    except Exception:
        return None

# Cuenta del propietario: solo desde el archivo privado local, nunca en el repositorio.
_HINT = Path.home() / ".zeruel-private" / "renewal_hint.txt"
OWNER_LOCAL = _HINT.read_text(encoding="utf-8").strip().split("@")[0].lower() if _HINT.is_file() else ""


def observe(task_id, timeout=180, log_file=LOG_DEFAULT):
    start_time = time.time()
    last_text = ""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    print(f"Observando probe para task_id={task_id} (timeout={timeout}s)...", file=sys.stderr)
    
    while time.time() - start_time < timeout:
        state_bundle = []
        def worker():
            attach_desktop()
            hwnd, title = find_browser_window()
            if hwnd:
                title = bring_tab_to_front(hwnd)
            img = capture_window_or_desktop(hwnd)
            state_bundle.append((hwnd, title, img))
            
        t = threading.Thread(target=worker)
        t.start()
        t.join()
        
        if not state_bundle or not state_bundle[0][2]:
            time.sleep(3)
            continue
            
        hwnd, title, img = state_bundle[0]
        
        # Se recorta la barra del navegador: con login_hint el correo aparece en la URL de Google
        # y el OCR lo confundía con el selector de cuentas (falso positivo y clic en la barra).
        top = min(110, img.height // 8)
        img = img.crop((0, top, img.width, img.height))
        text = pytesseract.image_to_string(img)
        last_text = text
        
        # 1. Check if Google Account Picker is showing and select owner account if present
        if ("Elige una cuenta" in text or "Choose an account" in text) and "synthetic_success" not in text:
            try:
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                clicked = False
                for i in range(len(data['text'])):
                    w = data['text'][i]
                    if OWNER_LOCAL and OWNER_LOCAL in w.lower():
                        cx = data['left'][i] + data['width'][i] // 2
                        cy = top + data['top'][i] + data['height'][i] // 2
                        attach_desktop()
                        user32 = ctypes.windll.user32
                        user32.SetCursorPos(cx, cy)
                        time.sleep(0.1)
                        user32.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, cx, cy, 0, 0)
                        time.sleep(0.05)
                        user32.mouse_event(win32con.MOUSEEVENTF_LEFTUP, cx, cy, 0, 0)
                        print(f"Cuenta de propietario seleccionada automaticamente en ({cx}, {cy})", file=sys.stderr)
                        clicked = True
                        time.sleep(3)
                        break
                if not clicked and (time.time() - start_time > 30):
                    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    record = f"{now_iso} | ID={task_id} | STATE=google_account_picker_required | ERROR=Google solicito elegir cuenta\n"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(record)
                    try: img.save(r"D:\SystemHope\renewal\latest_probe.png")
                    except Exception: pass
                    return {"status": "error", "state": "account_picker", "detail": "Google pidio elegir cuenta"}
            except Exception as e:
                print(f"Error en seleccion de cuenta: {e}", file=sys.stderr)
            
        # 2. Check for synthetic_success
        has_id = (task_id[:8] in text) or (task_id[:6].lower() in text.lower().replace('o', '0').replace('l', '1'))
        if ("synthetic_success" in text or "Completado" in text) and (has_id or (time.time() - start_time > 10 and "synthetic_success" in text)):
            elapsed = round(time.time() - start_time, 2)
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Extract summary details if visible
            match_elapsed = re.search(r"(\d+[,.]\d+)\s*s", text)
            match_rss = re.search(r"(\d+)\s*KiB", text)
            summary_str = f"completado en {elapsed}s"
            if match_elapsed: summary_str += f", probe_runtime={match_elapsed.group(0)}"
            if match_rss: summary_str += f", rss={match_rss.group(0)}"
            
            record = f"{now_iso} | ID={task_id} | STATE=synthetic_success | {summary_str}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(record)
            try: img.save(r"D:\SystemHope\renewal\latest_probe.png")
            except Exception: pass
                
            return {"status": "success", "state": "synthetic_success", "elapsed": elapsed, "detail": summary_str}
            
        # 3. Check paused
        # «Pausado · paused» es también el estado inicial al cargar: solo es fallo si persiste.
        if ("Pausado" in text or '"state": "paused"' in text) and time.time() - start_time > 120:
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            record = f"{now_iso} | ID={task_id} | STATE=paused | ERROR=Servidor en estado paused (reinicio detectado)\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(record)
            try: img.save(r"D:\SystemHope\renewal\latest_probe.png")
            except Exception: pass
            return {"status": "error", "state": "paused", "detail": "Servidor reiniciado en estado paused"}

        time.sleep(3)
        
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    record = f"{now_iso} | ID={task_id} | STATE=timeout | ERROR=Timeout tras {timeout}s\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(record)
    if 'img' in locals() and img:
        try: img.save(r"D:\SystemHope\renewal\latest_probe.png")
        except Exception: pass
    return {"status": "timeout", "state": "timeout", "detail": f"Timeout tras {timeout}s"}

if __name__ == "__main__":
    tid = sys.argv[1] if len(sys.argv) > 1 else "test0000000000000000000000000000"
    tout = int(sys.argv[2]) if len(sys.argv) > 2 else 180
    logfile = sys.argv[3] if len(sys.argv) > 3 else LOG_DEFAULT
    res = observe(tid, timeout=tout, log_file=logfile)
    print(json.dumps(res, ensure_ascii=False))
