import threading
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard
from .config import ConfigManager

class GlobalHotkeyManager(QObject):
    """
    Manages global keyboard hotkeys using pynput and delivers events to Qt main thread.
    """
    hotkey_triggered = pyqtSignal()
    hotkey_error = pyqtSignal(str)

    def __init__(self, hotkey_str: str = "Ctrl+Alt+T", parent=None):
        super().__init__(parent)
        self.current_human_hotkey = hotkey_str
        self.listener = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            self._start_listener(self.current_human_hotkey)

    def stop(self):
        with self._lock:
            self._stop_listener()

    def update_hotkey(self, new_human_hotkey: str) -> bool:
        """
        Updates the global hotkey to a new combination.
        Returns True if successful, False if invalid.
        """
        with self._lock:
            try:
                pynput_format = ConfigManager.human_to_pynput_hotkey(new_human_hotkey)
                # Test creating hotkey object
                dummy = keyboard.GlobalHotKeys({pynput_format: lambda: None})
                self._stop_listener()
                self.current_human_hotkey = new_human_hotkey
                self._start_listener(new_human_hotkey)
                return True
            except Exception as e:
                err_msg = f"快捷键格式无效: {new_human_hotkey} ({e})"
                print(f"[Hotkey] {err_msg}")
                self.hotkey_error.emit(err_msg)
                return False

    def _start_listener(self, human_hotkey: str):
        self._stop_listener()
        try:
            pynput_str = ConfigManager.human_to_pynput_hotkey(human_hotkey)
            self.listener = keyboard.GlobalHotKeys({
                pynput_str: self._on_triggered
            })
            self.listener.daemon = True
            self.listener.start()
            print(f"[Hotkey] Listening for global hotkey: {human_hotkey} ({pynput_str})")
        except Exception as e:
            print(f"[Hotkey] Failed to register hotkey {human_hotkey}: {e}")
            self.hotkey_error.emit(f"快捷键注册失败: {e}")

    def _stop_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

    def _on_triggered(self):
        # Emitted from pynput thread, Qt queues it to main thread
        self.hotkey_triggered.emit()
