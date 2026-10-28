from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class SystemTrayManager(QSystemTrayIcon):
    """Menubar / system tray icon manager for toggling slide-down flyout."""

    def __init__(self, icon_path: str, parent=None):
        super().__init__(QIcon(icon_path), parent)
        self.setToolTip("QuickTranslate (点击或快捷键唤出)")
        self._init_menu()
        self.activated.connect(self._on_activated)

    def _init_menu(self):
        menu = QMenu()

        self.action_toggle = QAction("🔍 唤出 / 收起翻译", self)
        menu.addAction(self.action_toggle)

        self.action_settings = QAction("⚙️ 偏好设置...", self)
        menu.addAction(self.action_settings)

        menu.addSeparator()

        self.action_quit = QAction("❌ 退出", self)
        menu.addAction(self.action_quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        # Left-click or double-click triggers flyout toggle
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.action_toggle.trigger()
