from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent

class SearchInput(QLineEdit):
    """Search input box supporting auto-focus, enter-to-translate, and escape-to-dismiss."""
    search_requested = pyqtSignal(str)
    escape_pressed = pyqtSignal()

    def __init__(self, placeholder="输入词汇、短语或句子，按 Enter 翻译...", parent=None):
        super().__init__(parent)
        self.setObjectName("SearchInput")
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            text = self.text().strip()
            if text:
                self.search_requested.emit(text)
        elif event.key() == Qt.Key_Escape:
            self.escape_pressed.emit()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()

class AudioButton(QPushButton):
    """Pill button to play audio pronunciation."""
    play_requested = pyqtSignal(str)

    def __init__(self, label: str, audio_url: str = "", parent=None):
        super().__init__(f"🔊 {label}", parent)
        self.setProperty("class", "AudioBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.audio_url = audio_url
        self.clicked.connect(self._on_clicked)

    def set_audio_url(self, url: str):
        self.audio_url = url

    def _on_clicked(self):
        if self.audio_url:
            self.play_requested.emit(self.audio_url)

class PosBadge(QLabel):
    """Part-of-speech badge tag."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "PosBadge")
        self.setAlignment(Qt.AlignCenter)

class ExamTag(QLabel):
    """Exam tag chip like CET4, IELTS, etc."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "ExamTag")
        self.setAlignment(Qt.AlignCenter)

class WordFormChip(QLabel):
    """Word form chip like '过去式 ran'."""
    def __init__(self, name: str, value: str, parent=None):
        super().__init__(f"{name}: {value}", parent)
        self.setProperty("class", "WordFormChip")
        self.setAlignment(Qt.AlignCenter)

class QuickChip(QPushButton):
    """Clickable chip for recent search history."""
    chip_clicked = pyqtSignal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "QuickChip")
        self.setCursor(Qt.PointingHandCursor)
        self.query_text = text
        self.clicked.connect(lambda: self.chip_clicked.emit(self.query_text))

class ClipboardBar(QPushButton):
    """Smart clipboard action button."""
    clipboard_clicked = pyqtSignal(str)

    def __init__(self, clip_text: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "ClipboardBar")
        self.setCursor(Qt.PointingHandCursor)
        self.clip_text = clip_text
        display = clip_text.replace("\n", " ").strip()
        if len(display) > 35:
            display = display[:35] + "..."
        self.setText(f"📋 查询剪贴板内容: \"{display}\"  (按 Tab 快速填入)")
        self.clicked.connect(lambda: self.clipboard_clicked.emit(self.clip_text))

class CopyButton(QPushButton):
    """Quick button to copy text to clipboard."""
    def __init__(self, text_to_copy: str = "", label: str = "复制", parent=None):
        super().__init__(f"📋 {label}", parent)
        self.setObjectName("SecondaryButton")
        self.setCursor(Qt.PointingHandCursor)
        self.text_to_copy = text_to_copy
        self.clicked.connect(self._copy)

    def set_text(self, text: str):
        self.text_to_copy = text

    def _copy(self):
        if self.text_to_copy:
            QApplication.clipboard().setText(self.text_to_copy)
            original = self.text()
            self.setText("✓ 已复制")
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.setText(original))
