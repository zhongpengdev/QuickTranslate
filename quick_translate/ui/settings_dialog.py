from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QFrame, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from ..config import ConfigManager

class SettingsDialog(QDialog):
    """Configuration dialog for custom hotkeys, auto system theme, and smart preferences."""
    hotkey_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setObjectName("SettingsDialog")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.initial_theme = self.config.get("theme", "auto")
        self.setWindowTitle("偏好设置 - QuickTranslate")
        self.setFixedWidth(450)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Hotkey Section
        hk_frame = QFrame()
        hk_frame.setProperty("class", "ResultCard")
        hk_layout = QVBoxLayout(hk_frame)
        hk_layout.setSpacing(8)

        hk_title = QLabel("唤醒快捷键")
        hk_title.setStyleSheet("font-weight: 600; font-size: 13.5px;")
        hk_layout.addWidget(hk_title)

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设组合:"))
        self.preset_combo = QComboBox()
        presets = ["Ctrl+Alt+T (默认)", "Alt+Space", "Ctrl+Shift+D", "F4", "Ctrl+F8", "自定义"]
        self.preset_combo.addItems(presets)
        preset_layout.addWidget(self.preset_combo, stretch=1)
        hk_layout.addLayout(preset_layout)

        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("自定义键:"))
        self.hotkey_input = QLineEdit(self.config.get("hotkey", "Ctrl+Alt+T"))
        self.hotkey_input.setPlaceholderText("例如: Ctrl+Alt+T 或 Alt+Space")
        custom_layout.addWidget(self.hotkey_input, stretch=1)
        hk_layout.addLayout(custom_layout)

        tip_label = QLabel("提示: 按下快捷键将自动从顶部菜单栏顺滑滑出翻译面板。")
        tip_label.setStyleSheet("color: #71717a; font-size: 11.5px;")
        hk_layout.addWidget(tip_label)

        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)

        current_hk = self.config.get("hotkey", "Ctrl+Alt+T")
        matched = False
        for i in range(self.preset_combo.count()):
            item_text = self.preset_combo.itemText(i)
            if current_hk.lower() in item_text.lower():
                self.preset_combo.setCurrentIndex(i)
                matched = True
                break
        if not matched:
            self.preset_combo.setCurrentText("自定义")

        layout.addWidget(hk_frame)

        # 2. Preferences & Theme Section
        pref_frame = QFrame()
        pref_frame.setProperty("class", "ResultCard")
        pref_layout = QVBoxLayout(pref_frame)
        pref_layout.setSpacing(10)

        # Theme Selector (Auto / Light / Dark)
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("外观主题:"))
        self.theme_combo = QComboBox()
        theme_options = [
            ("跟随系统 (Auto，推荐)", "auto"),
            ("明亮白色 (Light)", "light"),
            ("深色暗夜 (Dark)", "dark")
        ]
        for label, val in theme_options:
            self.theme_combo.addItem(label, val)

        saved_theme = self.config.get("theme", "auto")
        for idx in range(self.theme_combo.count()):
            if self.theme_combo.itemData(idx) == saved_theme:
                self.theme_combo.setCurrentIndex(idx)
                break

        self.theme_combo.currentIndexChanged.connect(self._on_theme_preview)
        theme_layout.addWidget(self.theme_combo, stretch=1)
        pref_layout.addLayout(theme_layout)

        # Smart features
        self.clipboard_cb = QCheckBox("唤醒时智能识别剪贴板内容")
        self.clipboard_cb.setChecked(self.config.get("smart_clipboard", True))
        pref_layout.addWidget(self.clipboard_cb)

        self.auto_pronounce_cb = QCheckBox("查词后自动朗读发音")
        self.auto_pronounce_cb.setChecked(self.config.get("auto_pronounce", False))
        pref_layout.addWidget(self.auto_pronounce_cb)

        self.auto_copy_cb = QCheckBox("翻译后自动复制结果到剪贴板")
        self.auto_copy_cb.setChecked(self.config.get("auto_copy", False))
        pref_layout.addWidget(self.auto_copy_cb)

        layout.addWidget(pref_frame)

        # 3. Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存设置")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_preset_changed(self, text: str):
        if "Ctrl+Alt+T" in text:
            self.hotkey_input.setText("Ctrl+Alt+T")
        elif "Alt+Space" in text:
            self.hotkey_input.setText("Alt+Space")
        elif "Ctrl+Shift+D" in text:
            self.hotkey_input.setText("Ctrl+Shift+D")
        elif "F4" in text:
            self.hotkey_input.setText("F4")
        elif "Ctrl+F8" in text:
            self.hotkey_input.setText("Ctrl+F8")

    def _on_theme_preview(self, index: int):
        theme_mode = self.theme_combo.itemData(index)
        eff_theme = self.config.get_effective_theme() if theme_mode == "auto" else theme_mode
        self.theme_changed.emit(eff_theme)
        self.style().unpolish(self)
        self.style().polish(self)
        for child in self.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
        self.update()

    def reject(self):
        eff = self.config.get_effective_theme()
        self.theme_changed.emit(eff)
        super().reject()

    def _save_settings(self):
        new_hk = self.hotkey_input.text().strip()
        if not new_hk:
            QMessageBox.warning(self, "错误", "快捷键不能为空！")
            return

        old_hk = self.config.get("hotkey")
        self.config.set("hotkey", new_hk)

        new_theme = self.theme_combo.currentData()
        self.config.set("theme", new_theme)
        self.initial_theme = new_theme

        self.config.set("smart_clipboard", self.clipboard_cb.isChecked())
        self.config.set("auto_pronounce", self.auto_pronounce_cb.isChecked())
        self.config.set("auto_copy", self.auto_copy_cb.isChecked())

        if new_hk != old_hk:
            self.hotkey_changed.emit(new_hk)

        eff = self.config.get_effective_theme()
        self.theme_changed.emit(eff)

        self.accept()
