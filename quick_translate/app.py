import os
import sys
import signal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt

from .config import ConfigManager
from .translator.engine import TranslationEngine
from .hotkey import GlobalHotkeyManager
from .ui.main_window import MainWindow
from .ui.tray_icon import SystemTrayManager

def get_asset_path(filename: str) -> str:
    """Gets absolute path to asset file, compatible with source and PyInstaller bundle."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, "assets", filename)
    if os.path.exists(path):
        return path
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename)

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 1. Enable High-DPI Scaling before creating QApplication
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    config_mgr = ConfigManager()
    scale_factor = config_mgr.get("scale_factor", "auto")
    if scale_factor and scale_factor != "auto":
        os.environ["QT_SCALE_FACTOR"] = str(scale_factor)

    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("QuickTranslate")
    app.setApplicationDisplayName("QuickTranslate")
    app.setQuitOnLastWindowClosed(False)

    icon_path = get_asset_path("icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialize components
    engine = TranslationEngine()
    window = MainWindow(config_mgr, engine)

    # Global Hotkey Manager
    initial_hotkey = config_mgr.get("hotkey", "Ctrl+Alt+T")
    hotkey_mgr = GlobalHotkeyManager(initial_hotkey)
    # Pressing hotkey toggles smooth slide-down from menubar / slide-up to menubar
    hotkey_mgr.hotkey_triggered.connect(window.toggle_wake)
    window.hotkey_manager = hotkey_mgr
    hotkey_mgr.start()

    # Menubar System Tray Icon
    tray_mgr = SystemTrayManager(icon_path)
    tray_mgr.action_toggle.triggered.connect(window.toggle_wake)
    tray_mgr.action_settings.triggered.connect(window.open_settings)
    tray_mgr.action_quit.triggered.connect(app.quit)
    tray_mgr.show()

    # Slide down on initial launch so the user immediately sees it
    window.slide_down()

    def cleanup():
        hotkey_mgr.stop()

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
