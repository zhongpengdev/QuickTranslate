import os
import json

DEFAULT_CONFIG = {
    "hotkey": "Ctrl+Alt+T",
    "theme": "dark",
    "scale_factor": "auto",  # "auto", "1.25", "1.5", "1.75", "2.0"
    "target_lang": "zh-CN",
    "auto_pronounce": False,
    "auto_copy": False,
    "window_width": 760,
    "window_height": 600,
    "history_max": 100,
    "window_position": "center"  # "center" or "remember"
}

class ConfigManager:
    """Manages application configuration, persisting to JSON."""

    def __init__(self, config_path=None):
        if not config_path:
            config_dir = os.path.expanduser("~/.config/quicktranslate")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.json")
        self.config_path = config_path
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

    @staticmethod
    def human_to_pynput_hotkey(human_str: str) -> str:
        """
        Converts human readable hotkey like 'Ctrl+Alt+T' to pynput format '<ctrl>+<alt>+t'.
        """
        if not human_str:
            return "<ctrl>+<alt>+t"
        
        parts = [p.strip() for p in human_str.split("+") if p.strip()]
        pynput_parts = []
        for p in parts:
            p_lower = p.lower()
            if p_lower in ("ctrl", "control"):
                pynput_parts.append("<ctrl>")
            elif p_lower in ("alt", "menu"):
                pynput_parts.append("<alt>")
            elif p_lower in ("shift",):
                pynput_parts.append("<shift>")
            elif p_lower in ("cmd", "super", "win", "windows", "meta"):
                pynput_parts.append("<cmd>")
            elif p_lower == "space":
                pynput_parts.append("<space>")
            elif p_lower.startswith("f") and p_lower[1:].isdigit():
                pynput_parts.append(f"<{p_lower}>")
            elif len(p_lower) == 1:
                pynput_parts.append(p_lower)
            else:
                pynput_parts.append(f"<{p_lower}>")
        return "+".join(pynput_parts)

    @staticmethod
    def pynput_to_human_hotkey(pynput_str: str) -> str:
        """
        Converts pynput format '<ctrl>+<alt>+t' to 'Ctrl+Alt+T'.
        """
        if not pynput_str:
            return "Ctrl+Alt+T"
        parts = [p.strip() for p in pynput_str.split("+") if p.strip()]
        human_parts = []
        for p in parts:
            raw = p.strip("<>").capitalize()
            if raw.lower() == "ctrl":
                human_parts.append("Ctrl")
            elif raw.lower() == "alt":
                human_parts.append("Alt")
            elif raw.lower() == "shift":
                human_parts.append("Shift")
            elif raw.lower() == "cmd":
                human_parts.append("Super")
            elif raw.lower() == "space":
                human_parts.append("Space")
            else:
                human_parts.append(raw.upper() if len(raw) == 1 else raw)
        return "+".join(human_parts)
