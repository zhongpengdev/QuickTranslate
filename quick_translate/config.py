import os
import json
import subprocess

DEFAULT_CONFIG = {
    "hotkey": "Ctrl+Alt+T",
    "theme": "auto",            # "auto" (follows system), "light", "dark"
    "scale_factor": "auto",     # "auto", "1.25", "1.5", "1.75", "2.0"
    "smart_clipboard": True,    # Detect and offer clipboard text on dropdown
    "auto_pronounce": False,
    "auto_copy": False,
    "window_width": 640,
    "window_height": 540,
    "history_max": 100
}

def detect_system_theme() -> str:
    """
    Detects whether the system is currently using dark or light theme.
    Supports GNOME, KDE, and GTK environments.
    """
    # 1. Check org.gnome.desktop.interface color-scheme
    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        val = res.stdout.strip().lower()
        if "dark" in val:
            return "dark"
    except Exception:
        pass

    # 2. Check org.gnome.desktop.interface gtk-theme
    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=1
        )
        val = res.stdout.strip().lower()
        if "dark" in val:
            return "dark"
    except Exception:
        pass

    return "light"

class ConfigManager:
    """Manages application configuration, persisting to JSON with system theme detection."""

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

    def get_effective_theme(self) -> str:
        """Returns the actual active theme ('dark' or 'light') based on config or system."""
        cfg_theme = self.get("theme", "auto")
        if cfg_theme in ("dark", "light"):
            return cfg_theme
        return detect_system_theme()

    @staticmethod
    def human_to_pynput_hotkey(human_str: str) -> str:
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
