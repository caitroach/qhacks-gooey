import sys
import time
import threading
from pathlib import Path

sys.setrecursionlimit(5000)

import webview  # pywebview

APP_TITLE = "Willow"

WINDOW_SIZE = (560, 740)

WINDOW_OFFSET = (20, 90)

TOPMOST_PULSE_SECONDS = 1.0 # she causes issues 


class AppState:
    def __init__(self):
        self.muted = True
        self.transcript = ""
        self.window: webview.Window | None = None


state = AppState()

def get_screen_size() -> tuple[int, int]:
    try:
        s = webview.screens[0]
        return int(s.width), int(s.height)
    except Exception:
        return 1920, 1080


def get_bottom_right_position(window_size: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
    w, h = map(int, window_size)
    off_x, off_y = map(int, offset)

    screen_w, screen_h = get_screen_size()
    x = max(0, screen_w - w - off_x)
    y = max(0, screen_h - h - off_y)
    return int(x), int(y)


def apply_window_geometry() -> dict:
    x, y = get_bottom_right_position(WINDOW_SIZE, WINDOW_OFFSET)

    ok = True
    if state.window is not None:
        try:
            state.window.resize(int(WINDOW_SIZE[0]), int(WINDOW_SIZE[1]))
            state.window.move(int(x), int(y))
        except Exception as e:
            ok = False
            print(f"⚠️ Failed to apply window geometry: {e}")

    return {"ok": ok, "size": list(WINDOW_SIZE), "pos": [x, y]}


def maintain_on_top():
    while True:
        time.sleep(TOPMOST_PULSE_SECONDS)
        w = state.window
        if not w:
            continue
        try:
            w.on_top = True
        except Exception:
            pass

class Api:
    def set_mute(self, muted: bool):
        state.muted = bool(muted)
        print(f"🎙️ Microphone {'muted' if state.muted else 'LIVE'}")
        return {"ok": True, "muted": state.muted}

    def update_transcript(self, text: str):
        state.transcript = text or ""
        return {"ok": True}

def ensure_web_folder() -> Path:
    root = Path(__file__).resolve().parent
    web_dir = root / "web"

    if not web_dir.exists():
        raise FileNotFoundError("Missing ./web/ folder. Put index.html and styles.css in ./web/")

    for name in ("index.html", "styles.css"):
        if not (web_dir / name).exists():
            raise FileNotFoundError(f"Missing {name} in ./web/")

    return web_dir


def on_loaded(window=None):
    if state.window is None:
        return

    try:
        state.window.on_top = True
    except Exception:
        pass

    apply_window_geometry()

    if sys.platform == "win32":
        threading.Thread(target=maintain_on_top, daemon=True).start()


def main():
    try:
        web_dir = ensure_web_folder()
    except Exception as e:
        print(f"❌ {e}")
        input("Press Enter to exit...")
        return

    x, y = get_bottom_right_position(WINDOW_SIZE, WINDOW_OFFSET)
    url = (web_dir / "index.html").resolve().as_uri()

    api = Api()

    window = webview.create_window(
        APP_TITLE,
        url=url,
        js_api=api,
        width=int(WINDOW_SIZE[0]),
        height=int(WINDOW_SIZE[1]),
        x=int(x),
        y=int(y),
        on_top=True,
        resizable=True,   
    )
    state.window = window

    webview.start(on_loaded, window, debug=False)


if __name__ == "__main__":
    main()
