from flask import Flask, jsonify, send_from_directory
import threading
import time
import os
import ctypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

scan_data = {
    "name": "—",
    "wear": "—",
    "offered_price": "—",
    "market_price": "—",
    "status": "waiting"
}

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "ui.html")

@app.route("/data")
def data():
    return jsonify(scan_data)

def update(name=None, wear=None, offered_price=None, market_price=None, status=None):
    if name is not None:          scan_data["name"] = name
    if wear is not None:          scan_data["wear"] = wear
    if offered_price is not None: scan_data["offered_price"] = offered_price
    if market_price is not None:  scan_data["market_price"] = market_price
    if status is not None:        scan_data["status"] = status

def _run_flask(port):
    app.run(port=port, debug=False, use_reloader=False)

# Win32 helpers to set window opacity
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
LWA_ALPHA         = 0x00000002

def _set_opacity(hwnd, opacity):
    """opacity: 0-255"""
    user32 = ctypes.windll.user32
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
    user32.SetLayeredWindowAttributes(hwnd, 0, opacity, LWA_ALPHA)

def _find_hwnd(title):
    return ctypes.windll.user32.FindWindowW(None, title)

def _fade_loop(title, fade_in, steps=12, delay=0.02):
    hwnd = _find_hwnd(title)
    if not hwnd:
        return
    start, end = (30, 255) if fade_in else (255, 30)
    for i in range(steps + 1):
        val = int(start + (end - start) * (i / steps))
        _set_opacity(hwnd, val)
        time.sleep(delay)

def start(port=5050):
    t = threading.Thread(target=_run_flask, args=(port,), daemon=True)
    t.start()
    time.sleep(0.8)

    import webview

    WIN_TITLE = "CS2 Terminal"

    def on_loaded():
        # Start faded out
        hwnd = _find_hwnd(WIN_TITLE)
        if hwnd:
            _set_opacity(hwnd, 30)

    # Expose fade functions to JavaScript
    class Api:
        def fade_in(self):
            threading.Thread(target=_fade_loop, args=(WIN_TITLE, True), daemon=True).start()

        def fade_out(self):
            threading.Thread(target=_fade_loop, args=(WIN_TITLE, False), daemon=True).start()

    api = Api()

    window = webview.create_window(
        title=WIN_TITLE,
        url=f"http://localhost:{port}",
        width=400,
        height=220,
        resizable=False,
        frameless=True,
        on_top=True,
        js_api=api,
    )
    window.events.loaded += on_loaded
    webview.start()