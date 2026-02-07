import eel
import sys
import os
import threading
import time

# ==========================================
# Configuration
# ==========================================
APP_TITLE = "Willow"
COMPACT_SIZE = (420, 380)
FULL_SIZE = (900, 650)

class AppState:
    def __init__(self):
        self.muted = True
        self.current_mode = "compact"
        self.transcript = ""
        self.window_handle = None

state = AppState()

# ==========================================
# Windows helpers (Win10)
# ==========================================
HAS_WIN32 = False
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        import win32api

        HAS_WIN32 = True

        def _enum_visible_windows():
            wins = []
            def cb(hwnd, acc):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        acc.append((hwnd, win32gui.GetWindowText(hwnd)))
                except Exception:
                    pass
                return True
            win32gui.EnumWindows(cb, wins)
            return wins

        def find_window_handle():
            """
            Eel/Chrome windows can have titles like:
              "Willow" or "Willow - Google Chrome" or "localhost:8080 - Google Chrome"
            So we match a couple substrings.
            """
            needles = [APP_TITLE.lower(), "localhost", "127.0.0.1"]
            candidates = []
            for hwnd, title in _enum_visible_windows():
                t = (title or "").lower()
                if any(n in t for n in needles):
                    candidates.append((hwnd, title))
            return candidates[0][0] if candidates else None

        def set_always_on_top(hwnd: int) -> bool:
            if not hwnd:
                return False
            try:
                flags = (
                    win32con.SWP_NOMOVE
                    | win32con.SWP_NOSIZE
                    | win32con.SWP_NOACTIVATE
                    | win32con.SWP_SHOWWINDOW
                )
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
                return True
            except Exception:
                return False

        def get_screen_size():
            return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)

        def reposition_window(hwnd: int, size: tuple[int, int]) -> bool:
            if not hwnd:
                return False
            try:
                screen_w, screen_h = get_screen_size()
                w, h = int(size[0]), int(size[1])
                x = int(screen_w - w - 20)
                y = int(screen_h - h - 100)
                flags = win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, w, h, flags)
                return True
            except Exception as e:
                print(f"⚠️  Error repositioning: {e}")
                return False

        def maintain_on_top():
            # Keep it pinned. Windows can drop TOPMOST when focus changes sometimes.
            while True:
                time.sleep(1.0)
                if not state.window_handle:
                    continue
                try:
                    set_always_on_top(state.window_handle)
                except Exception:
                    pass

        def start_window_thread():
            # Wait for the Chrome window to exist
            time.sleep(1.5)
            state.window_handle = find_window_handle()
            if not state.window_handle:
                print("⚠️  Could not find window handle (always-on-top/resize may not work)")
                return

            print(f"✓ Found window handle: {state.window_handle}")
            set_always_on_top(state.window_handle)

            # Put it in the right place/size immediately
            target = COMPACT_SIZE if state.current_mode == "compact" else FULL_SIZE
            reposition_window(state.window_handle, target)

            t = threading.Thread(target=maintain_on_top, daemon=True)
            t.start()

    except ImportError:
        HAS_WIN32 = False


# ==========================================
# Exposed API functions (called from JS)
# ==========================================
@eel.expose
def set_mute(muted):
    state.muted = bool(muted)
    print(f"🎙️  Microphone {'muted' if state.muted else 'LIVE'}")
    return {"ok": True, "muted": state.muted}

@eel.expose
def get_current_mode():
    return {"mode": state.current_mode}

def _apply_mode(mode: str):
    mode = "full" if mode == "full" else "compact"
    state.current_mode = mode
    size = FULL_SIZE if mode == "full" else COMPACT_SIZE

    resized = False
    if HAS_WIN32 and state.window_handle:
        resized = reposition_window(state.window_handle, size)

    # Tell the frontend to refresh its CSS mode without guessing based on innerWidth
    try:
        eel.window_resize(size[0], size[1])
    except Exception:
        pass

    return {"ok": True, "mode": mode, "resized": bool(resized)}

@eel.expose
def switch_to_full():
    if state.current_mode == "full":
        return {"ok": True, "mode": "full", "resized": False}
    print("🔄 Switching to full mode")
    return _apply_mode("full")

@eel.expose
def switch_to_compact():
    if state.current_mode == "compact":
        return {"ok": True, "mode": "compact", "resized": False}
    print("🔄 Switching to compact mode")
    return _apply_mode("compact")

@eel.expose
def update_transcript(text):
    state.transcript = text or ""
    return {"ok": True}


# ==========================================
# App bootstrap
# ==========================================
def get_screen_position(window_size):
    # Bottom-right
    try:
        if sys.platform == "win32" and HAS_WIN32:
            screen_w = win32api.GetSystemMetrics(0)
            screen_h = win32api.GetSystemMetrics(1)
        else:
            screen_w, screen_h = 1920, 1080
        x = int(screen_w - window_size[0] - 20)
        y = int(screen_h - window_size[1] - 100)
        return x, y
    except Exception:
        return 100, 100

def on_close(page, sockets):
    print("\\n👋 Willow closed")

def main():
    web_folder = "web"
    if not os.path.exists(web_folder):
        os.makedirs(web_folder, exist_ok=True)
        print("❌ Missing 'web' folder. Put index.html and styles.css in ./web/")
        input("Press Enter to exit...")
        return

    for req in ["index.html", "styles.css"]:
        if not os.path.exists(os.path.join(web_folder, req)):
            print(f"❌ Missing {req} in ./web/")
            input("Press Enter to exit...")
            return

    eel.init(web_folder)

    initial_size = COMPACT_SIZE if state.current_mode == "compact" else FULL_SIZE
    x, y = get_screen_position(initial_size)

    if sys.platform == "win32" and HAS_WIN32:
        threading.Thread(target=start_window_thread, daemon=True).start()
    elif sys.platform == "win32" and not HAS_WIN32:
        print("⚠️  Install pywin32 for always-on-top + auto-resize: pip install pywin32")

    chrome_args = ["--disable-gpu", "--no-sandbox"]
    eel.start(
        "index.html",
        size=initial_size,
        position=(x, y),
        mode="chrome",
        close_callback=on_close,
        cmdline_args=chrome_args,
        suppress_error=False,
        port=8080,
    )

if __name__ == "__main__":
    main()
