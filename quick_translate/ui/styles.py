"""Modern stylesheets for QuickTranslate with complete Dark and Light theme support."""

DARK_THEME = """
QWidget {
    background-color: #18181b;
    color: #f4f4f5;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    font-size: 15px;
}

QWidget#MainWindow {
    background-color: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 14px;
}

QDialog, QDialog#SettingsDialog {
    background-color: #18181b;
    color: #f4f4f5;
    border: 1px solid #3f3f46;
    border-radius: 14px;
}

/* Search input */
QLineEdit#SearchInput {
    background-color: #27272a;
    border: 2px solid #3f3f46;
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 17px;
    color: #ffffff;
    selection-background-color: #3b82f6;
}

QLineEdit#SearchInput:focus {
    border: 2px solid #3b82f6;
    background-color: #202023;
}

/* Primary Action Button */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 9px 20px;
    font-weight: bold;
    font-size: 15px;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:pressed {
    background-color: #1e40af;
}

/* Secondary Button */
QPushButton#SecondaryButton {
    background-color: #27272a;
    color: #d4d4d8;
    border: 1px solid #3f3f46;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton#SecondaryButton:hover {
    background-color: #3f3f46;
    color: #ffffff;
}

/* Audio Pronunciation Button */
QPushButton.AudioBtn {
    background-color: #27272a;
    color: #60a5fa;
    border: 1px solid #3b82f6;
    border-radius: 16px;
    padding: 5px 14px;
    font-size: 13.5px;
    font-weight: 500;
}

QPushButton.AudioBtn:hover {
    background-color: #1e3a8a;
    color: #ffffff;
    border: 1px solid #60a5fa;
}

/* Cards */
QFrame[class="ResultCard"], QFrame.ResultCard {
    background-color: #202024;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 14px;
}

QFrame[class="ExampleCard"], QFrame.ExampleCard {
    background-color: #1e1e22;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

/* Labels */
QLabel#PrimaryTranslation {
    font-size: 22px;
    font-weight: bold;
    color: #60a5fa;
    line-height: 1.3;
}

QLabel#QueryLabel {
    font-size: 25px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#PhoneticLabel {
    font-size: 15px;
    color: #a1a1aa;
    font-family: "DejaVu Sans", "Lucida Sans Unicode", sans-serif;
}

QLabel#SectionHeader {
    font-size: 14px;
    font-weight: bold;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 10px;
}

QLabel#ExampleSource {
    font-size: 15px;
    color: #f4f4f5;
    line-height: 1.4;
}

QLabel#ExampleTarget {
    font-size: 14.5px;
    color: #a1a1aa;
    line-height: 1.4;
}

QLabel#WelcomeTips {
    color: #a1a1aa;
    line-height: 1.7;
    font-size: 14.5px;
    margin-top: 12px;
}

QLabel#BottomHint {
    color: #71717a;
    font-size: 13px;
    padding: 4px 6px;
}

QLabel#LoadingSub {
    color: #71717a;
    font-size: 13px;
    margin-top: 8px;
}

/* Badges */
QLabel.PosBadge, QLabel[class="PosBadge"] {
    background-color: #1e3a8a;
    color: #93c5fd;
    border-radius: 6px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 13px;
}

QLabel.TagBadge, QLabel[class="TagBadge"] {
    background-color: #27272a;
    color: #a1a1aa;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
}

/* ComboBox & CheckBox */
QComboBox {
    background-color: #27272a;
    color: #ffffff;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 24px;
}

QComboBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox QAbstractItemView {
    background-color: #202024;
    color: #ffffff;
    border: 1px solid #3f3f46;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    padding: 4px;
}

QCheckBox {
    color: #f4f4f5;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #3f3f46;
    background-color: #27272a;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* ScrollArea */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3f3f46;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #52525b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    font-size: 15px;
}

QWidget#MainWindow {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
}

QDialog, QDialog#SettingsDialog {
    background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
}

/* Search input */
QLineEdit#SearchInput {
    background-color: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 17px;
    color: #0f172a;
    selection-background-color: #3b82f6;
}

QLineEdit#SearchInput:focus {
    border: 2px solid #2563eb;
    background-color: #ffffff;
}

/* Primary Action Button */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 9px 20px;
    font-weight: bold;
    font-size: 15px;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:pressed {
    background-color: #1e40af;
}

/* Secondary Button */
QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton#SecondaryButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #94a3b8;
}

/* Audio Pronunciation Button */
QPushButton.AudioBtn {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    padding: 5px 14px;
    font-size: 13.5px;
    font-weight: 500;
}

QPushButton.AudioBtn:hover {
    background-color: #dbeafe;
    border: 1px solid #93c5fd;
}

/* Cards */
QFrame[class="ResultCard"], QFrame.ResultCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px;
}

QFrame[class="ExampleCard"], QFrame.ExampleCard {
    background-color: #f1f5f9;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

/* Labels */
QLabel#PrimaryTranslation {
    font-size: 22px;
    font-weight: bold;
    color: #1d4ed8;
    line-height: 1.3;
}

QLabel#QueryLabel {
    font-size: 25px;
    font-weight: bold;
    color: #0f172a;
}

QLabel#PhoneticLabel {
    font-size: 15px;
    color: #64748b;
    font-family: "DejaVu Sans", "Lucida Sans Unicode", sans-serif;
}

QLabel#SectionHeader {
    font-size: 14px;
    font-weight: bold;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 10px;
}

QLabel#ExampleSource {
    font-size: 15px;
    color: #0f172a;
    line-height: 1.4;
}

QLabel#ExampleTarget {
    font-size: 14.5px;
    color: #475569;
    line-height: 1.4;
}

QLabel#WelcomeTips {
    color: #475569;
    line-height: 1.7;
    font-size: 14.5px;
    margin-top: 12px;
}

QLabel#BottomHint {
    color: #64748b;
    font-size: 13px;
    padding: 4px 6px;
}

QLabel#LoadingSub {
    color: #64748b;
    font-size: 13px;
    margin-top: 8px;
}

/* Badges */
QLabel.PosBadge, QLabel[class="PosBadge"] {
    background-color: #dbeafe;
    color: #1e40af;
    border-radius: 6px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 13px;
}

QLabel.TagBadge, QLabel[class="TagBadge"] {
    background-color: #f1f5f9;
    color: #64748b;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
}

/* ComboBox & CheckBox */
QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 24px;
}

QComboBox:focus {
    border: 1px solid #2563eb;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    padding: 4px;
}

QCheckBox {
    color: #0f172a;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* ScrollArea */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
