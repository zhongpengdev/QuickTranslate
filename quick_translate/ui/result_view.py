import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from .widgets import AudioButton, PosBadge, TagBadge, CopyButton
from ..translator.models import TranslationResult

class ResultView(QWidget):
    """
    Renders structured translation results:
    - Pronunciations (UK/US phonetics + audio playback)
    - Primary translation & explanations
    - Common meanings broken down by part of speech
    - Corresponding bilingual example sentences with audio
    """
    play_audio_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for long results
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.container.setObjectName("ResultContainer")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 12, 12, 12)
        self.container_layout.setSpacing(12)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

        self.show_welcome_state()

    def clear_content(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_welcome_state(self):
        self.clear_content()
        welcome_frame = QFrame()
        welcome_frame.setProperty("class", "ResultCard")
        w_layout = QVBoxLayout(welcome_frame)
        w_layout.setContentsMargins(20, 30, 20, 30)
        w_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("💡 极速词典 & 划词翻译")
        title.setObjectName("QueryLabel")
        title.setAlignment(Qt.AlignCenter)
        w_layout.addWidget(title)

        tips = QLabel(
            "• 输入单词、短语或长句，直接回车 (Enter) 翻译\n"
            "• 自动提供标准英/美音标发音、词性拆解、常见释义与双语例句\n"
            "• 全局快捷键随时一键唤醒并自动聚焦光标 (默认 Ctrl+Alt+T)\n"
            "• 按 ESC 键可一键极速隐藏窗口"
        )
        tips.setObjectName("WelcomeTips")
        tips.setAlignment(Qt.AlignCenter)
        w_layout.addWidget(tips)

        self.container_layout.addWidget(welcome_frame)
        self.container_layout.addStretch()

    def show_loading_state(self, query: str):
        self.clear_content()
        card = QFrame()
        card.setProperty("class", "ResultCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 40, 20, 40)
        l.setAlignment(Qt.AlignCenter)

        spinner = QLabel(f"⚡ 正在查询: \"{query}\" ...")
        spinner.setObjectName("PrimaryTranslation")
        spinner.setAlignment(Qt.AlignCenter)
        l.addWidget(spinner)

        sub = QLabel("正在从免费极速引擎并行获取释义、发音与例句...")
        sub.setObjectName("LoadingSub")
        sub.setAlignment(Qt.AlignCenter)
        l.addWidget(sub)

        self.container_layout.addWidget(card)
        self.container_layout.addStretch()

    def show_error_state(self, error_msg: str):
        self.clear_content()
        card = QFrame()
        card.setProperty("class", "ResultCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 30, 20, 30)
        l.setAlignment(Qt.AlignCenter)

        title = QLabel("⚠️ 翻译提示")
        title.setObjectName("QueryLabel")
        title.setAlignment(Qt.AlignCenter)
        l.addWidget(title)

        desc = QLabel(error_msg)
        desc.setStyleSheet("color: #f87171; margin-top: 10px; font-size: 14px;")
        desc.setAlignment(Qt.AlignCenter)
        l.addWidget(desc)

        self.container_layout.addWidget(card)
        self.container_layout.addStretch()

    def render_result(self, res: TranslationResult):
        self.clear_content()
        if res.error:
            self.show_error_state(res.error)
            return

        # 1. Header Card: Query, Phonetics, Audio Buttons, Primary Translation
        header_card = QFrame()
        header_card.setProperty("class", "ResultCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(10)

        # Top row: Query text + Copy button
        top_row = QHBoxLayout()
        q_label = QLabel(res.query)
        q_label.setObjectName("QueryLabel")
        top_row.addWidget(q_label)
        top_row.addStretch()

        copy_btn = CopyButton(res.translation or res.query, "复制翻译")
        top_row.addWidget(copy_btn)
        h_layout.addLayout(top_row)

        # Phonetics & Audio Row
        if res.phonetics or res.audio_urls:
            ph_row = QHBoxLayout()
            ph_row.setSpacing(10)

            # Display phonetics and play buttons
            for dialect in ["UK", "US", "Pinyin", "Phonetic"]:
                text_val = res.phonetics.get(dialect)
                audio_val = res.audio_urls.get(dialect) or res.audio_urls.get("Audio")
                if text_val or audio_val:
                    label_name = "英" if dialect == "UK" else "美" if dialect == "US" else "拼" if dialect == "Pinyin" else "音标"
                    display_text = f"{label_name} {text_val or ''}"
                    audio_btn = AudioButton(display_text.strip(), audio_val or "")
                    audio_btn.play_requested.connect(self.play_audio_requested.emit)
                    ph_row.addWidget(audio_btn)

            # Sentence TTS fallback if no word phonetics
            if not res.phonetics and res.audio_urls.get("Voice"):
                tts_btn = AudioButton("整句朗读", res.audio_urls.get("Voice"))
                tts_btn.play_requested.connect(self.play_audio_requested.emit)
                ph_row.addWidget(tts_btn)

            ph_row.addStretch()
            h_layout.addLayout(ph_row)

        # Primary Translation
        if res.translation:
            trans_label = QLabel(res.translation)
            trans_label.setObjectName("PrimaryTranslation")
            trans_label.setWordWrap(True)
            trans_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            h_layout.addWidget(trans_label)

        self.container_layout.addWidget(header_card)

        # 2. Section: 常见意思 (Common Meanings & POS Breakdown)
        if res.pos_meanings or res.common_meanings:
            meanings_frame = QFrame()
            meanings_frame.setProperty("class", "ResultCard")
            m_layout = QVBoxLayout(meanings_frame)
            m_layout.setSpacing(8)

            sec_title = QLabel("📖 常见意思与释义")
            sec_title.setObjectName("SectionHeader")
            m_layout.addWidget(sec_title)

            if res.pos_meanings:
                for pm in res.pos_meanings:
                    item_layout = QHBoxLayout()
                    item_layout.setSpacing(8)
                    item_layout.setAlignment(Qt.AlignTop)

                    badge = PosBadge(pm.pos)
                    item_layout.addWidget(badge)

                    defs_text = "；".join(pm.definitions)
                    def_label = QLabel(defs_text)
                    def_label.setWordWrap(True)
                    def_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    item_layout.addWidget(def_label, stretch=1)

                    m_layout.addLayout(item_layout)
            else:
                for cm in res.common_meanings[:6]:
                    lbl = QLabel(f"• {cm}")
                    lbl.setWordWrap(True)
                    lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    m_layout.addWidget(lbl)

            self.container_layout.addWidget(meanings_frame)

        # 3. Section: 对应例句 (Example Sentences)
        if res.examples:
            examples_frame = QFrame()
            examples_frame.setProperty("class", "ResultCard")
            ex_layout = QVBoxLayout(examples_frame)
            ex_layout.setSpacing(10)

            ex_sec_title = QLabel("📝 经典双语例句")
            ex_sec_title.setObjectName("SectionHeader")
            ex_layout.addWidget(ex_sec_title)

            for ex in res.examples[:5]:
                card = QFrame()
                card.setProperty("class", "ExampleCard")
                c_layout = QVBoxLayout(card)
                c_layout.setSpacing(4)

                # English sentence with target word highlight
                src_label = QLabel(self._highlight_keyword(ex.source, res.query))
                src_label.setObjectName("ExampleSource")
                src_label.setTextFormat(Qt.RichText)
                src_label.setWordWrap(True)
                src_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                c_layout.addWidget(src_label)

                # Chinese translation sentence
                tgt_label = QLabel(ex.target)
                tgt_label.setObjectName("ExampleTarget")
                tgt_label.setWordWrap(True)
                tgt_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                c_layout.addWidget(tgt_label)

                ex_layout.addWidget(card)

            self.container_layout.addWidget(examples_frame)

        # 4. Footer Metadata (Engine & Cache Status)
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(6)
        engine_badge = TagBadge(f"服务: {res.source_engine}")
        meta_layout.addWidget(engine_badge)

        if res.from_cache:
            cache_badge = TagBadge("⚡ 极速缓存 (0ms)")
            meta_layout.addWidget(cache_badge)

        meta_layout.addStretch()
        self.container_layout.addLayout(meta_layout)

        # Bottom stretch to push content to top
        self.container_layout.addStretch()

    def _highlight_keyword(self, sentence: str, query: str) -> str:
        """Highlights the query keyword in the example sentence."""
        if not query or len(query) < 2:
            return sentence
        # Case insensitive replacement wrapping with <b style="color: #60a5fa;">
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f'<b style="color: #60a5fa;">{m.group(0)}</b>', sentence)
