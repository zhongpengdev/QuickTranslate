from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ..config import ConfigManager

class SettingsDialog(QDialog):
    """Configuration dialog for custom hotkeys, theme, and app behavior."""
    hotkey_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setObjectName("SettingsDialog")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.initial_theme = self.config.get("theme", "dark")
        self.setWindowTitle("QuickTranslate - 设置")
        self.setFixedWidth(460)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 1. Title
        title = QLabel("⚙️ 偏好设置")
        title.setObjectName("QueryLabel")
        layout.addWidget(title)

        # 2. Hotkey Section
        hk_frame = QFrame()
        hk_frame.setProperty("class", "ResultCard")
        hk_layout = QVBoxLayout(hk_frame)
        hk_layout.setSpacing(10)

        hk_title = QLabel("唤醒全局快捷键 (点击/按下即可唤醒窗口)")
        hk_title.setStyleSheet("font-weight: bold;")
        hk_layout.addWidget(hk_title)

        # Preset Dropdown
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设快捷键:"))
        self.preset_combo = QComboBox()
        presets = ["Ctrl+Alt+T (默认)", "Alt+Space", "Ctrl+Shift+D", "F4", "Ctrl+F8", "自定义"]
        self.preset_combo.addItems(presets)
        preset_layout.addWidget(self.preset_combo, stretch=1)
        hk_layout.addLayout(preset_layout)

        # Custom Input
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("快捷键组合:"))
        self.hotkey_input = QLineEdit(self.config.get("hotkey", "Ctrl+Alt+T"))
        self.hotkey_input.setPlaceholderText("例如: Ctrl+Alt+T 或 Alt+Space")
        custom_layout.addWidget(self.hotkey_input, stretch=1)
        hk_layout.addLayout(custom_layout)

        tip_label = QLabel("提示: 支持组合键如 Ctrl+Alt+T, Alt+Space, Ctrl+Shift+D, F4 等。")
        tip_label.setStyleSheet("color: #71717a; font-size: 12px;")
        hk_layout.addWidget(tip_label)

        # Connect preset change
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)

        # Select initial preset if matches
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

        # 3. Preferences Section
        pref_frame = QFrame()
        pref_frame.setProperty("class", "ResultCard")
        pref_layout = QVBoxLayout(pref_frame)
        pref_layout.setSpacing(10)

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("界面主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色暗夜 (Dark)", "明亮白色 (Light)"])
        if self.config.get("theme") == "light":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_preview)
        theme_layout.addWidget(self.theme_combo, stretch=1)
        pref_layout.addLayout(theme_layout)

        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("界面缩放:"))
        self.scale_combo = QComboBox()
        scale_options = [
            ("自动高分屏缩放 (推荐)", "auto"),
            ("125% (稍微放大)", "1.25"),
            ("150% (舒适放大)", "1.5"),
            ("175% (清晰大字)", "1.75"),
            ("200% (超大高分)", "2.0"),
            ("100% (原始未缩放)", "1.0")
        ]
        for label, val in scale_options:
            self.scale_combo.addItem(label, val)

        current_scale = str(self.config.get("scale_factor", "auto"))
        for idx in range(self.scale_combo.count()):
            if self.scale_combo.itemData(idx) == current_scale:
                self.scale_combo.setCurrentIndex(idx)
                break
        scale_layout.addWidget(self.scale_combo, stretch=1)
        pref_layout.addLayout(scale_layout)

        self.auto_pronounce_cb = QCheckBox("查词后自动朗读发音")
        self.auto_pronounce_cb.setChecked(self.config.get("auto_pronounce", False))
        pref_layout.addWidget(self.auto_pronounce_cb)

        self.auto_copy_cb = QCheckBox("翻译后自动复制结果到剪贴板")
        self.auto_copy_cb.setChecked(self.config.get("auto_copy", False))
        pref_layout.addWidget(self.auto_copy_cb)

        layout.addWidget(pref_frame)

        # 4. Action Buttons
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
        theme = "light" if index == 1 else "dark"
        self.theme_changed.emit(theme)

    def reject(self):
        # Revert theme if user cancels without saving
        saved_theme = self.config.get("theme", "dark")
        self.theme_changed.emit(saved_theme)
        super().reject()

    def _save_settings(self):
        new_hk = self.hotkey_input.text().strip()
        if not new_hk:
            QMessageBox.warning(self, "错误", "快捷键不能为空！")
            return

        # Save to config
        old_hk = self.config.get("hotkey")
        self.config.set("hotkey", new_hk)

        new_theme = "light" if self.theme_combo.currentIndex() == 1 else "dark"
        old_theme = self.config.get("theme")
        self.config.set("theme", new_theme)

        new_scale = self.scale_combo.currentData()
        old_scale = self.config.get("scale_factor", "auto")
        self.config.set("scale_factor", new_scale)

        self.config.set("auto_pronounce", self.auto_pronounce_cb.isChecked())
        self.config.set("auto_copy", self.auto_copy_cb.isChecked())

        if new_hk != old_hk:
            self.hotkey_changed.emit(new_hk)

        if new_theme != old_theme:
            self.theme_changed.emit(new_theme)

        if new_scale != old_scale:
            QMessageBox.information(
                self,
                "缩放已设置",
                "界面缩放比例已更新，将在重启程序后完全生效。"
            )

        self.accept()
