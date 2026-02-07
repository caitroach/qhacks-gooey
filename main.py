import tkinter as tk
import webview

APP_TITLE = "Willow"

# Start at compact size, but user can resize manually
INITIAL_WIDTH = 420
INITIAL_HEIGHT = 380

def screen_size():
    root = tk.Tk()
    root.withdraw()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.destroy()
    return w, h

def bottom_right_pos(win_w: int, win_h: int, margin: int = 16, taskbar_fudge: int = 80):
    sw, sh = screen_size()
    x = max(0, sw - win_w - margin)
    y = max(0, sh - win_h - margin - taskbar_fudge)
    return x, y

class Api:
    def __init__(self):
        self.window = None
        self.muted = True

    def bind_window(self, window: webview.Window):
        self.window = window

    def set_mute(self, muted: bool):
        self.muted = bool(muted)
        print(f"🎙️  Microphone {'muted' if self.muted else 'LIVE'}")
        return {"ok": True, "muted": self.muted}

def main():
    x, y = bottom_right_pos(INITIAL_WIDTH, INITIAL_HEIGHT)

    api = Api()

    window = webview.create_window(
        APP_TITLE,
        "web/index.html",
        width=INITIAL_WIDTH,
        height=INITIAL_HEIGHT,
        x=x,
        y=y,
        on_top=True,
        resizable=True,  # User can resize manually
        js_api=api
    )

    api.bind_window(window)

    def on_start():
        print("🌅 Willow started! (Resize window manually)")

    webview.start(on_start, debug=False)

if __name__ == "__main__":
    main()