import tkinter as tk
import webview

APP_TITLE = "Willow"

COMPACT = (420, 380)  # Increased height slightly for better fit
FULL = (900, 650)

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
        self.current_mode = "compact"

    def bind_window(self, window: webview.Window):
        self.window = window

    def set_mute(self, muted: bool):
        self.muted = bool(muted)
        # TODO: hook into your real mic logic
        return {"ok": True, "muted": self.muted}

    def set_window_mode(self, mode: str):
        if not self.window:
            return {"ok": False, "error": "Window not bound yet"}

        if mode == "full":
            w, h = FULL
        else:
            w, h = COMPACT

        x, y = bottom_right_pos(w, h)

        # Native resize/move (reliable)
        self.window.resize(w, h)
        self.window.move(x, y)
        self.current_mode = mode
        
        return {"ok": True, "mode": mode, "w": w, "h": h, "x": x, "y": y}

    def get_current_mode(self):
        return {"mode": self.current_mode}

def main():
    win_w, win_h = COMPACT
    x, y = bottom_right_pos(win_w, win_h)

    api = Api()

    window = webview.create_window(
        APP_TITLE,
        "web/index.html",
        width=win_w,
        height=win_h,
        x=x,
        y=y,
        on_top=True,
        resizable=True,
        js_api=api
    )

    api.bind_window(window)

    def on_start():
        api.set_window_mode("compact")

    webview.start(on_start, debug=False)

if __name__ == "__main__":
    main()
