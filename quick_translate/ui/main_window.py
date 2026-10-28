import os
import shutil
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QShortcut, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QKeySequence, QIcon

from ..config import ConfigManager
from ..translator.engine import TranslationEngine
from ..translator.models import TranslationResult
from .widgets import SearchInput
from .result_view import ResultView
from .settings_dialog import SettingsDialog
from .styles import DARK_THEME, LIGHT_THEME

class TranslationWorker(QThread):
    """Background worker thread so translation requests never block the UI."""
    result_ready = pyqtSignal(object)

    def __init__(self, engine: TranslationEngine, text: str, force_refresh: bool = False):
        super().__init__()
        self.engine = engine
        self.text = text
        self.force_refresh = force_refresh

    def run(self):
        res = self.engine.translate(self.text, self.force_refresh)
        self.result_ready.emit(res)

class MainWindow(QWidget):
    """
    Spotlight/Raycast inspired sleek translation window.
    Supports auto-focus, Enter-to-translate, hotkey wake-up, and audio playback.
    """

    def __init__(self, config_manager: ConfigManager, engine: TranslationEngine, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.engine = engine
        self.current_worker = None
        self._drag_pos = QPoint()

        self._init_window_flags()
        self._init_ui()
        self._init_shortcuts()
        self.apply_theme(self.config.get("theme", "dark"))
        self._center_window()

    def _init_window_flags(self):
        self.setObjectName("MainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # Frameless floating spotlight window
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        width = self.config.get("window_width", 760)
        height = self.config.get("window_height", 600)
        self.resize(width, height)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # 1. Top Search Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Search Bar
        self.search_input = SearchInput(parent=self)
        self.search_input.search_requested.connect(self.perform_translation)
        self.search_input.escape_pressed.connect(self.hide_window)
        header_layout.addWidget(self.search_input, stretch=1)

        # Translate Button
        self.trans_btn = QPushButton("翻译", self)
        self.trans_btn.setObjectName("PrimaryButton")
        self.trans_btn.setCursor(Qt.PointingHandCursor)
        self.trans_btn.setToolTip("点击翻译或在输入框按回车 (Enter)")
        self.trans_btn.clicked.connect(lambda: self.perform_translation(self.search_input.text()))
        header_layout.addWidget(self.trans_btn)

        # Settings Button
        self.settings_btn = QPushButton("⚙️", self)
        self.settings_btn.setObjectName("SecondaryButton")
        self.settings_btn.setToolTip("偏好设置 (Ctrl+,)")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)

        # Hide / Minimize Button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("SecondaryButton")
        self.close_btn.setToolTip("隐藏窗口 (ESC)")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide_window)
        header_layout.addWidget(self.close_btn)

        main_layout.addLayout(header_layout)

        # 2. Results Container
        self.result_view = ResultView(self)
        self.result_view.play_audio_requested.connect(self.engine.play_audio)
        main_layout.addWidget(self.result_view, stretch=1)

        # 3. Bottom Status Hint
        self.hint_label = QLabel(self._get_hint_text(), self)
        self.hint_label.setObjectName("BottomHint")
        self.hint_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(self.hint_label)

    def _get_hint_text(self) -> str:
        hk = self.config.get("hotkey", "Ctrl+Alt+T")
        return f"快捷键: [{hk}] 快速唤醒  |  [Enter] 立即翻译  |  [ESC] 隐藏窗口  |  [Ctrl+L] 聚焦输入"

    def _init_shortcuts(self):
        # ESC -> hide
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.hide_window)
        # Ctrl+L -> focus search
        QShortcut(QKeySequence("Ctrl+L"), self, self._focus_search)
        # Ctrl+, -> settings
        QShortcut(QKeySequence("Ctrl+,"), self, self.open_settings)

    def _focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2 + screen.x()
        # Position slightly above center (top 20% of screen) for Raycast/Spotlight look
        y = max(screen.y() + 60, int(screen.height() * 0.18) + screen.y())
        self.move(x, y)

    def wake_up(self):
        """
        Brings the window to the absolute front and automatically focuses the cursor.
        """
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

        # On Linux X11, invoke xdotool windowactivate to bypass window manager focus stealing prevention
        if shutil.which("xdotool"):
            try:
                win_id = int(self.winId())
                subprocess.Popen(
                    ["xdotool", "windowactivate", str(win_id)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

        self._focus_search()

    def toggle_wake(self):
        """Toggle hide/show behavior like Spotlight/Alfred/Raycast."""
        if self.isVisible() and self.isActiveWindow():
            self.hide_window()
        else:
            self.wake_up()

    def hide_window(self):
        self.hide()

    def perform_translation(self, text: str):
        query = text.strip()
        if not query:
            return

        self.result_view.show_loading_state(query)

        # Run on background thread
        self.current_worker = TranslationWorker(self.engine, query)
        self.current_worker.result_ready.connect(self._on_translation_finished)
        self.current_worker.start()

    def _on_translation_finished(self, res: TranslationResult):
        self.result_view.render_result(res)

        # Auto-pronounce if configured
        if self.config.get("auto_pronounce", False) and res.audio_urls:
            # Prefer US or UK or first available
            audio_url = res.audio_urls.get("US") or res.audio_urls.get("UK") or list(res.audio_urls.values())[0]
            if audio_url:
                self.engine.play_audio(audio_url)

        # Auto-copy if configured
        if self.config.get("auto_copy", False) and res.translation:
            QApplication.clipboard().setText(res.translation)

    def apply_theme(self, theme_name: str):
        stylesheet = LIGHT_THEME if theme_name == "light" else DARK_THEME
        qapp = QApplication.instance()
        if qapp:
            qapp.setStyleSheet(stylesheet)
        self.setStyleSheet(stylesheet)
        self._repolish_widget(self)
        if hasattr(self, "result_view") and self.result_view:
            self._repolish_widget(self.result_view)
        self.update()

    def _repolish_widget(self, w):
        if not w:
            return
        try:
            w.style().unpolish(w)
            w.style().polish(w)
            for child in w.findChildren(QWidget):
                child.style().unpolish(child)
                child.style().polish(child)
        except Exception:
            pass

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.hotkey_changed.connect(self._on_hotkey_changed)
        dialog.theme_changed.connect(self.apply_theme)
        dialog.exec_()

    def _on_hotkey_changed(self, new_hotkey: str):
        self.hint_label.setText(self._get_hint_text())
        # Emit or notify parent to update global hotkey listener
        if hasattr(self, "hotkey_manager") and self.hotkey_manager:
            ok = self.hotkey_manager.update_hotkey(new_hotkey)
            if ok:
                QMessageBox.information(self, "快捷键已生效", f"全局唤醒快捷键已更新为: {new_hotkey}")
            else:
                QMessageBox.warning(self, "错误", f"快捷键注册失败，请检查格式！")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
