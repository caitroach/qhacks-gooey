import webview
import threading
import time

APP_TITLE = "Willow"

COMPACT = (420, 380)
FULL = (900, 650)

class Api:
    def __init__(self):
        self.window = None
        self.muted = True
        self.current_mode = "compact"

    def bind_window(self, window):
        self.window = window

    def set_mute(self, muted):
        self.muted = bool(muted)
        print(f"🎙️  Microphone {'muted' if self.muted else 'LIVE'}")
        return {"ok": True, "muted": self.muted}

    def set_window_mode(self, mode):
        if not self.window:
            return {"ok": False, "error": "Window not bound"}
        
        if self.current_mode == mode:
            return {"ok": True, "mode": mode}

        if mode == "full":
            w, h = FULL
        else:
            w, h = COMPACT

        try:
            print(f"🔄 Switching to {mode}: {w}x{h}")
            
            # On Windows, we need to resize in the main thread
            # Use evaluate_js to trigger a resize callback
            self.current_mode = mode
            
            # Pass the dimensions back to JavaScript to handle
            return {"ok": True, "mode": mode, "w": w, "h": h}
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"ok": False, "error": str(e)}

    def get_current_mode(self):
        return {"mode": self.current_mode}

def get_screen_size():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        return w, h
    except:
        return 1920, 1080  # fallback

def main():
    api = Api()
    
    # Start in compact mode
    w, h = COMPACT
    
    # Position in bottom-right
    screen_w, screen_h = get_screen_size()
    x = screen_w - w - 20
    y = screen_h - h - 100

    window = webview.create_window(
        APP_TITLE,
        "index.html",
        width=w,
        height=h,
        x=x,
        y=y,
        on_top=True,
        resizable=True,
        js_api=api
    )

    api.bind_window(window)

    def start():
        print("🌅 Willow started!")

    webview.start(start, debug=False)

if __name__ == "__main__":
    main()