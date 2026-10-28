from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class SystemTrayManager(QSystemTrayIcon):
    """System tray icon manager for background operation and quick access."""

    def __init__(self, icon_path: str, parent=None):
        super().__init__(QIcon(icon_path), parent)
        self.setToolTip("QuickTranslate 极速桌面翻译")
        self._init_menu()
        self.activated.connect(self._on_activated)

    def _init_menu(self):
        menu = QMenu()

        self.action_show = QAction("🔍 唤醒翻译窗口", self)
        menu.addAction(self.action_show)

        self.action_settings = QAction("⚙️ 偏好设置...", self)
        menu.addAction(self.action_settings)

        menu.addSeparator()

        self.action_quit = QAction("❌ 退出程序", self)
        menu.addAction(self.action_quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.action_show.trigger()
