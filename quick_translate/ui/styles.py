"""Modern, minimalist stylesheets for QuickTranslate menubar flyout."""

DARK_THEME = """
QWidget {
    background-color: #1a1a1e;
    color: #e4e4e7;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* Menubar Flyout Dropdown Window */
QWidget#FlyoutWindow {
    background-color: #18181c;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-top: none;
    border-bottom-left-radius: 14px;
    border-bottom-right-radius: 14px;
}

QDialog, QDialog#SettingsDialog {
    background-color: #18181c;
    color: #e4e4e7;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
}

/* Minimalist Search Bar Header */
QFrame#SearchHeader {
    background-color: #202025;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-top: none;
    padding: 2px 4px;
}

QLineEdit#SearchInput {
    background-color: transparent;
    border: none;
    padding: 10px 12px;
    font-size: 16px;
    font-weight: 500;
    color: #ffffff;
    selection-background-color: #3b82f6;
}

QLineEdit#SearchInput:focus {
    border: none;
}

/* Top Action Buttons (Settings, Favorite, Close) */
QPushButton#IconButton {
    background-color: transparent;
    color: #a1a1aa;
    border: none;
    border-radius: 6px;
    padding: 6px;
    font-size: 14px;
}

QPushButton#IconButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

/* Primary Action Button */
QPushButton#PrimaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#PrimaryButton:hover {
    background-color: #2563eb;
}

QPushButton#SecondaryButton {
    background-color: #27272a;
    color: #d4d4d8;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
}

QPushButton#SecondaryButton:hover {
    background-color: #3f3f46;
    color: #ffffff;
}

/* Sound Wave Audio Pill Button */
QPushButton.AudioBtn {
    background-color: rgba(59, 130, 246, 0.12);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.AudioBtn:hover {
    background-color: rgba(59, 130, 246, 0.22);
    color: #ffffff;
}

/* Cards & Sections */
QFrame.ResultCard {
    background-color: #1f1f24;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px;
}

QFrame.ExampleCard {
    background-color: rgba(255, 255, 255, 0.02);
    border-left: 3px solid #3b82f6;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}

/* Labels */
QLabel#QueryLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#PrimaryTranslation {
    font-size: 20px;
    font-weight: 600;
    color: #60a5fa;
    line-height: 1.3;
}

QLabel#SectionHeader {
    font-size: 12px;
    font-weight: 600;
    color: #71717a;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 6px;
}

QLabel#ExampleSource {
    font-size: 14px;
    color: #f4f4f5;
    line-height: 1.4;
}

QLabel#ExampleTarget {
    font-size: 13.5px;
    color: #a1a1aa;
    line-height: 1.4;
}

QLabel#BottomHint {
    color: #71717a;
    font-size: 12px;
    padding: 2px 4px;
}

/* Badges & Chips */
QLabel.PosBadge {
    background-color: rgba(59, 130, 246, 0.15);
    color: #93c5fd;
    border-radius: 4px;
    padding: 2px 6px;
    font-weight: 600;
    font-size: 12px;
}

QLabel.ExamTag {
    background-color: rgba(168, 85, 247, 0.15);
    color: #c084fc;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
    font-weight: 500;
}

QLabel.WordFormChip {
    background-color: rgba(255, 255, 255, 0.06);
    color: #a1a1aa;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 11.5px;
}

QLabel.TagBadge {
    background-color: rgba(255, 255, 255, 0.05);
    color: #a1a1aa;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
}

/* History / Clipboard Quick Chips */
QPushButton.QuickChip {
    background-color: #27272a;
    color: #d4d4d8;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
}

QPushButton.QuickChip:hover {
    background-color: #3f3f46;
    color: #ffffff;
}

QPushButton.ClipboardBar {
    background-color: rgba(59, 130, 246, 0.1);
    color: #60a5fa;
    border: 1px dashed rgba(59, 130, 246, 0.35);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    text-align: left;
}

QPushButton.ClipboardBar:hover {
    background-color: rgba(59, 130, 246, 0.18);
    color: #93c5fd;
}

/* ComboBox & CheckBox */
QComboBox {
    background-color: #27272a;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 22px;
}

QComboBox QAbstractItemView {
    background-color: #202025;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.1);
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QCheckBox {
    color: #e4e4e7;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background-color: #27272a;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* ScrollArea */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3f3f46;
    border-radius: 3px;
    min-height: 20px;
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
    background-color: #ffffff;
    color: #1e293b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* Menubar Flyout Dropdown Window */
QWidget#FlyoutWindow {
    background-color: #f8fafc;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-top: none;
    border-bottom-left-radius: 14px;
    border-bottom-right-radius: 14px;
}

QDialog, QDialog#SettingsDialog {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px;
}

/* Minimalist Search Bar Header */
QFrame#SearchHeader {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    border-top: none;
    padding: 2px 4px;
}

QLineEdit#SearchInput {
    background-color: transparent;
    border: none;
    padding: 10px 12px;
    font-size: 16px;
    font-weight: 500;
    color: #0f172a;
    selection-background-color: #3b82f6;
}

QLineEdit#SearchInput:focus {
    border: none;
}

/* Top Action Buttons (Settings, Favorite, Close) */
QPushButton#IconButton {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-radius: 6px;
    padding: 6px;
    font-size: 14px;
}

QPushButton#IconButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

/* Primary Action Button */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
}

QPushButton#SecondaryButton:hover {
    background-color: #f8fafc;
    color: #0f172a;
    border-color: #94a3b8;
}

/* Sound Wave Audio Pill Button */
QPushButton.AudioBtn {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.AudioBtn:hover {
    background-color: #dbeafe;
    border-color: #93c5fd;
}

/* Cards & Sections */
QFrame.ResultCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px;
}

QFrame.ExampleCard {
    background-color: #f8fafc;
    border-left: 3px solid #2563eb;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}

/* Labels */
QLabel#QueryLabel {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#PrimaryTranslation {
    font-size: 20px;
    font-weight: 600;
    color: #1d4ed8;
    line-height: 1.3;
}

QLabel#SectionHeader {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 6px;
}

QLabel#ExampleSource {
    font-size: 14px;
    color: #0f172a;
    line-height: 1.4;
}

QLabel#ExampleTarget {
    font-size: 13.5px;
    color: #475569;
    line-height: 1.4;
}

QLabel#BottomHint {
    color: #94a3b8;
    font-size: 12px;
    padding: 2px 4px;
}

/* Badges & Chips */
QLabel.PosBadge {
    background-color: #dbeafe;
    color: #1e40af;
    border-radius: 4px;
    padding: 2px 6px;
    font-weight: 600;
    font-size: 12px;
}

QLabel.ExamTag {
    background-color: #f3e8ff;
    color: #7e22ce;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
    font-weight: 500;
}

QLabel.WordFormChip {
    background-color: #f1f5f9;
    color: #475569;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 11.5px;
}

QLabel.TagBadge {
    background-color: #f1f5f9;
    color: #64748b;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
}

/* History / Clipboard Quick Chips */
QPushButton.QuickChip {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
}

QPushButton.QuickChip:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}

QPushButton.ClipboardBar {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px dashed #93c5fd;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    text-align: left;
}

QPushButton.ClipboardBar:hover {
    background-color: #dbeafe;
}

/* ComboBox & CheckBox */
QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 22px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
}

QCheckBox {
    color: #1e293b;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
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
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
