import os
import shutil
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QShortcut, QApplication, QMessageBox, QFrame
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QPoint, QPropertyAnimation,
    QEasingCurve, QTimer, QEvent
)
from PyQt5.QtGui import QKeySequence

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
    Sleek Menubar Popover Window that smoothly slides down from the top menubar/status bar.
    - Lives in the menubar (no taskbar icon).
    - Slide-down animation on hotkey or menubar icon click.
    - Automatically focuses cursor.
    - Follows system dark/light theme automatically.
    - Rich dictionary info, clipboard auto-suggestion, recent history, and wordbook.
    """

    def __init__(self, config_manager: ConfigManager, engine: TranslationEngine, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.engine = engine
        self.current_worker = None
        self.is_animating = False
        self.settings_dialog_open = False
        self.last_clipboard_text = ""

        self._init_window_flags()
        self._init_ui()
        self._init_shortcuts()
        self._init_theme_monitor()

        # Initial theme application
        self.apply_theme(self.config.get_effective_theme())

    def _init_window_flags(self):
        self.setObjectName("FlyoutWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Qt.Tool ensures no taskbar or dock entry!
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        screen = QApplication.primaryScreen().availableGeometry()
        width = min(660, max(560, int(screen.width() * 0.42)))
        height = min(560, max(460, int(screen.height() * 0.52)))
        self.resize(width, height)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Search Header Frame
        search_header = QFrame(self)
        search_header.setObjectName("SearchHeader")
        h_layout = QHBoxLayout(search_header)
        h_layout.setContentsMargins(12, 6, 12, 6)
        h_layout.setSpacing(8)

        # Search Icon prefix
        search_icon = QLabel("🔍", search_header)
        search_icon.setStyleSheet("color: #71717a; font-size: 14px;")
        h_layout.addWidget(search_icon)

        # Search Input
        self.search_input = SearchInput(parent=search_header)
        self.search_input.search_requested.connect(self.perform_translation)
        self.search_input.escape_pressed.connect(self.slide_up_and_hide)
        h_layout.addWidget(self.search_input, stretch=1)

        # Quick Translate Button
        self.trans_btn = QPushButton("翻译", search_header)
        self.trans_btn.setObjectName("PrimaryButton")
        self.trans_btn.setCursor(Qt.PointingHandCursor)
        self.trans_btn.clicked.connect(lambda: self.perform_translation(self.search_input.text()))
        h_layout.addWidget(self.trans_btn)

        # Wordbook / Favorites Button
        self.wordbook_btn = QPushButton("★", search_header)
        self.wordbook_btn.setObjectName("IconButton")
        self.wordbook_btn.setToolTip("生词本 (Favorites)")
        self.wordbook_btn.setCursor(Qt.PointingHandCursor)
        self.wordbook_btn.clicked.connect(self._show_favorites)
        h_layout.addWidget(self.wordbook_btn)

        # Settings Button
        self.settings_btn = QPushButton("⚙", search_header)
        self.settings_btn.setObjectName("IconButton")
        self.settings_btn.setToolTip("偏好设置 (Ctrl+,)")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        h_layout.addWidget(self.settings_btn)

        # Dismiss Button
        self.close_btn = QPushButton("✕", search_header)
        self.close_btn.setObjectName("IconButton")
        self.close_btn.setToolTip("收起窗口 (ESC)")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.slide_up_and_hide)
        h_layout.addWidget(self.close_btn)

        main_layout.addWidget(search_header)

        # 2. Results Container View
        self.result_view = ResultView(self)
        self.result_view.play_audio_requested.connect(self.engine.play_audio)
        self.result_view.search_requested.connect(self._search_from_chip)
        self.result_view.toggle_favorite_requested.connect(self._on_toggle_favorite)
        main_layout.addWidget(self.result_view, stretch=1)

        # Load empty launchpad state
        self._refresh_empty_state()

    def _init_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.slide_up_and_hide)
        QShortcut(QKeySequence("Ctrl+L"), self, self._focus_search)
        QShortcut(QKeySequence("Ctrl+,"), self, self.open_settings)
        # Tab to paste clipboard text if empty
        QShortcut(QKeySequence(Qt.Key_Tab), self, self._paste_and_translate_clipboard)
        # Ctrl+1 / Ctrl+2 to play UK/US audio
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self._play_dialect_audio("UK"))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self._play_dialect_audio("US"))

    def _init_theme_monitor(self):
        # Auto-check system theme changes every 3 seconds if theme is set to 'auto'
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self._check_system_theme_update)
        self.theme_timer.start(3000)

    def _check_system_theme_update(self):
        if self.config.get("theme", "auto") == "auto":
            eff = self.config.get_effective_theme()
            current_is_dark = "18181c" in (self.styleSheet() or "")
            if (eff == "dark" and not current_is_dark) or (eff == "light" and current_is_dark):
                self.apply_theme(eff)

    def _focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _get_target_pos(self) -> (QPoint, QPoint):
        """Calculates start position (hidden above top bar) and target position (flush below top bar)."""
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2 + screen.x()
        target_y = screen.y()
        start_y = target_y - self.height()
        return QPoint(x, start_y), QPoint(x, target_y)

    def slide_down(self):
        """Smoothly slides the window down from the top menubar and focuses input."""
        if self.is_animating:
            return

        start_pos, target_pos = self._get_target_pos()
        self.move(start_pos)
        self.show()
        self.raise_()
        self.activateWindow()

        # Linux X11 focus guarantee
        if shutil.which("xdotool"):
            try:
                subprocess.Popen(
                    ["xdotool", "windowactivate", str(int(self.winId()))],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

        # Update empty state with latest clipboard / history if no current query
        if not self.search_input.text().strip():
            self._refresh_empty_state()

        self.is_animating = True
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(160)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(target_pos)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(self._on_slide_down_finished)
        self.anim.start()

    def _on_slide_down_finished(self):
        self.is_animating = False
        self._focus_search()

    def slide_up_and_hide(self):
        """Smoothly slides the window back up into the menubar and hides it."""
        if self.is_animating or not self.isVisible():
            return

        start_pos, target_pos = self._get_target_pos()
        self.is_animating = True
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(140)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(start_pos)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.finished.connect(self._on_slide_up_finished)
        self.anim.start()

    def _on_slide_up_finished(self):
        self.is_animating = False
        self.hide()

    def toggle_wake(self):
        """Toggles slide-down from menubar / slide-up to menubar."""
        if self.isVisible() and self.isActiveWindow():
            self.slide_up_and_hide()
        else:
            self.slide_down()

    def changeEvent(self, event):
        # Auto-dismiss on click outside (lost activation focus)
        if event.type() == QEvent.ActivationChange:
            if not self.isActiveWindow() and self.isVisible() and not self.settings_dialog_open:
                self.slide_up_and_hide()
        super().changeEvent(event)

    def _refresh_empty_state(self):
        hist = self.engine.get_recent_history(8)
        favs = self.engine.get_favorites()

        # Check clipboard text
        clip_text = ""
        if self.config.get("smart_clipboard", True):
            try:
                raw_clip = QApplication.clipboard().text()
                if raw_clip and len(raw_clip.strip()) > 1 and len(raw_clip.strip()) < 300:
                    clip_text = raw_clip.strip()
            except Exception:
                pass

        self.last_clipboard_text = clip_text
        self.result_view.show_empty_state(recent_history=hist, clipboard_text=clip_text, favorites=favs)

    def _paste_and_translate_clipboard(self):
        if not self.search_input.text().strip() and self.last_clipboard_text:
            self.search_input.setText(self.last_clipboard_text)
            self.perform_translation(self.last_clipboard_text)

    def _search_from_chip(self, query: str):
        self.search_input.setText(query)
        self.perform_translation(query)

    def _show_favorites(self):
        favs = self.engine.get_favorites()
        if not favs:
            QMessageBox.information(self, "生词本", "生词本目前为空，查询单词后点击右上角的 ☆ 即可收藏！")
            return
        self.search_input.clear()
        self.result_view.show_empty_state(recent_history=[], clipboard_text="", favorites=favs)

    def _on_toggle_favorite(self, query: str, translation: str):
        self.engine.toggle_favorite(query, translation)

    def _play_dialect_audio(self, dialect: str):
        if self.result_view and self.result_view.current_result:
            res = self.result_view.current_result
            url = res.audio_urls.get(dialect)
            if url:
                self.engine.play_audio(url)

    def perform_translation(self, text: str):
        query = text.strip()
        if not query:
            self._refresh_empty_state()
            return

        self.result_view.show_loading_state(query)

        self.current_worker = TranslationWorker(self.engine, query)
        self.current_worker.result_ready.connect(self._on_translation_finished)
        self.current_worker.start()

    def _on_translation_finished(self, res: TranslationResult):
        self.result_view.render_result(res)

        if self.config.get("auto_pronounce", False) and res.audio_urls:
            url = res.audio_urls.get("US") or res.audio_urls.get("UK") or list(res.audio_urls.values())[0]
            if url:
                self.engine.play_audio(url)

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
        self.settings_dialog_open = True
        dialog = SettingsDialog(self.config, self)
        dialog.hotkey_changed.connect(self._on_hotkey_changed)
        dialog.theme_changed.connect(self.apply_theme)
        dialog.exec_()
        self.settings_dialog_open = False
        self._focus_search()

    def _on_hotkey_changed(self, new_hotkey: str):
        if hasattr(self, "hotkey_manager") and self.hotkey_manager:
            ok = self.hotkey_manager.update_hotkey(new_hotkey)
            if ok:
                QMessageBox.information(self, "快捷键已生效", f"全局唤醒快捷键已更新为: {new_hotkey}")
            else:
                QMessageBox.warning(self, "错误", "快捷键注册失败，请检查格式！")
