import webview
import threading

APP_TITLE = "Willow"

COMPACT = (420, 380)
FULL = (900, 650)

class Api:
    def __init__(self):
        self.compact_window = None
        self.full_window = None
        self.muted = True
        self.current_mode = "compact"

    def bind_windows(self, compact_window, full_window):
        self.compact_window = compact_window
        self.full_window = full_window

    def set_mute(self, muted):
        self.muted = bool(muted)
        print(f"🎙️  Microphone {'muted' if self.muted else 'LIVE'}")
        return {"ok": True, "muted": self.muted}

    def switch_to_full(self):
        """Switch from compact to full window"""
        if self.current_mode == "full":
            return {"ok": True, "mode": "full"}
        
        try:
            print("🔄 Switching to full mode")
            self.current_mode = "full"
            
            # Show full window, hide compact
            if self.full_window:
                self.full_window.show()
            if self.compact_window:
                self.compact_window.hide()
            
            return {"ok": True, "mode": "full"}
        except Exception as e:
            print(f"❌ Error switching to full: {e}")
            return {"ok": False, "error": str(e)}

    def switch_to_compact(self):
        """Switch from full to compact window"""
        if self.current_mode == "compact":
            return {"ok": True, "mode": "compact"}
        
        try:
            print("🔄 Switching to compact mode")
            self.current_mode = "compact"
            
            # Show compact window, hide full
            if self.compact_window:
                self.compact_window.show()
            if self.full_window:
                self.full_window.hide()
            
            return {"ok": True, "mode": "compact"}
        except Exception as e:
            print(f"❌ Error switching to compact: {e}")
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
    
    # Get screen size for positioning
    screen_w, screen_h = get_screen_size()
    
    # Position compact window in bottom-right
    compact_x = screen_w - COMPACT[0] - 20
    compact_y = screen_h - COMPACT[1] - 100
    
    # Position full window in bottom-right
    full_x = screen_w - FULL[0] - 20
    full_y = screen_h - FULL[1] - 100

    # Create compact window (visible by default)
    compact_window = webview.create_window(
        APP_TITLE + " - Compact",
        "web/index.html",
        width=COMPACT[0],
        height=COMPACT[1],
        x=compact_x,
        y=compact_y,
        on_top=True,
        resizable=False,
        js_api=api
    )

    # Create full window (hidden by default)
    full_window = webview.create_window(
        APP_TITLE + " - Full",
        "web/index.html",
        width=FULL[0],
        height=FULL[1],
        x=full_x,
        y=full_y,
        on_top=True,
        resizable=True,
        js_api=api,
        hidden=True  # Start hidden
    )

    api.bind_windows(compact_window, full_window)

    def start():
        print("🌅 Willow started in compact mode!")
        print("💡 Click 'Expand' to switch to full mode")

    webview.start(start, debug=False)

if __name__ == "__main__":
    main()