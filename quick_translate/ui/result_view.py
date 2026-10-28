import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from .widgets import (
    AudioButton, PosBadge, ExamTag, WordFormChip,
    QuickChip, ClipboardBar, CopyButton
)
from ..translator.models import TranslationResult

class ResultView(QWidget):
    """
    Renders structured, rich, professional dictionary results:
    - Primary translation, phonetics, and audio
    - Word forms, exam tags, and Collins stars
    - Common meanings and POS breakdown
    - Collocations / phrases and synonyms
    - Real-world bilingual example sentences
    - Recent search history and clipboard quick actions
    """
    play_audio_requested = pyqtSignal(str)
    search_requested = pyqtSignal(str)
    toggle_favorite_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_result = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.viewport().setAutoFillBackground(False)

        self.container = QWidget()
        self.container.setObjectName("ResultContainer")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(14, 10, 14, 14)
        self.container_layout.setSpacing(10)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def clear_content(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_empty_state(self, recent_history: list = None, clipboard_text: str = None, favorites: list = None):
        """Displays a clean launchpad state with clipboard suggestion, history, and favorites."""
        self.clear_content()

        # 1. Smart Clipboard Suggestion (if valid word/sentence and not empty)
        if clipboard_text and len(clipboard_text.strip()) > 1 and len(clipboard_text.strip()) < 300:
            clip_btn = ClipboardBar(clipboard_text.strip(), self)
            clip_btn.clipboard_clicked.connect(self.search_requested.emit)
            self.container_layout.addWidget(clip_btn)

        # 2. Recent Searches
        if recent_history:
            hist_frame = QFrame()
            hist_frame.setProperty("class", "ResultCard")
            h_layout = QVBoxLayout(hist_frame)
            h_layout.setSpacing(8)

            sec_title = QLabel("最近查询")
            sec_title.setObjectName("SectionHeader")
            h_layout.addWidget(sec_title)

            chips_layout = QHBoxLayout()
            chips_layout.setSpacing(6)
            for item in recent_history[:6]:
                chip = QuickChip(item["query"], self)
                chip.chip_clicked.connect(self.search_requested.emit)
                chips_layout.addWidget(chip)
            chips_layout.addStretch()
            h_layout.addLayout(chips_layout)

            self.container_layout.addWidget(hist_frame)

        # 3. Favorites / Starred Words (if any)
        if favorites:
            fav_frame = QFrame()
            fav_frame.setProperty("class", "ResultCard")
            f_layout = QVBoxLayout(fav_frame)
            f_layout.setSpacing(8)

            fav_title = QLabel("★ 我的生词本")
            fav_title.setObjectName("SectionHeader")
            f_layout.addWidget(fav_title)

            fav_chips = QHBoxLayout()
            fav_chips.setSpacing(6)
            for item in favorites[:6]:
                chip = QuickChip(item["query"], self)
                chip.chip_clicked.connect(self.search_requested.emit)
                fav_chips.addWidget(chip)
            fav_chips.addStretch()
            f_layout.addLayout(fav_chips)

            self.container_layout.addWidget(fav_frame)

        # 4. Clean Keyboard Shortcut Hint
        tips_label = QLabel("↵ 翻译  •  ESC 收起  •  Tab 贴板  •  Ctrl+1/2 朗读")
        tips_label.setObjectName("BottomHint")
        tips_label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(tips_label)

        self.container_layout.addStretch()

    def show_loading_state(self, query: str):
        self.clear_content()
        card = QFrame()
        card.setProperty("class", "ResultCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 36, 20, 36)
        l.setAlignment(Qt.AlignCenter)

        title = QLabel(f"正在查询: \"{query}\"")
        title.setObjectName("PrimaryTranslation")
        title.setAlignment(Qt.AlignCenter)
        l.addWidget(title)

        sub = QLabel("双引擎实时获取释义、发音与双语例句...")
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
        l.setContentsMargins(20, 24, 20, 24)
        l.setAlignment(Qt.AlignCenter)

        desc = QLabel(error_msg)
        desc.setObjectName("ExampleTarget")
        desc.setAlignment(Qt.AlignCenter)
        l.addWidget(desc)

        self.container_layout.addWidget(card)
        self.container_layout.addStretch()

    def render_result(self, res: TranslationResult):
        self.clear_content()
        self.current_result = res
        if res.error:
            self.show_error_state(res.error)
            return

        # 1. Header Card: Query, Exam Tags, Collins Stars, Phonetics, Translation
        header_card = QFrame()
        header_card.setProperty("class", "ResultCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(8)

        # Top row: Word + Collins Star + Favorite Star + Copy Button
        top_row = QHBoxLayout()
        q_label = QLabel(res.query)
        q_label.setObjectName("QueryLabel")
        q_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        top_row.addWidget(q_label)

        # Collins Stars
        if res.collins_star:
            star_text = "★" * res.collins_star + "☆" * (5 - res.collins_star)
            star_label = QLabel(star_text)
            star_label.setStyleSheet("color: #f59e0b; font-size: 13px; margin-left: 6px;")
            top_row.addWidget(star_label)

        top_row.addStretch()

        # Favorite Star Toggle
        self.fav_btn = QPushButton("★ 已收藏" if res.is_favorite else "☆ 收藏", self)
        self.fav_btn.setObjectName("IconButton")
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.clicked.connect(self._on_favorite_clicked)
        top_row.addWidget(self.fav_btn)

        copy_btn = CopyButton(res.translation or res.query, "复制")
        top_row.addWidget(copy_btn)
        h_layout.addLayout(top_row)

        # Exam Tags Row (CET4, CET6, IELTS, etc.)
        if res.exam_tags:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(6)
            for tag in res.exam_tags[:6]:
                tag_row.addWidget(ExamTag(tag))
            tag_row.addStretch()
            h_layout.addLayout(tag_row)

        # Phonetics & Audio Row
        if res.phonetics or res.audio_urls:
            ph_row = QHBoxLayout()
            ph_row.setSpacing(8)

            for dialect in ["UK", "US", "Pinyin", "Phonetic"]:
                text_val = res.phonetics.get(dialect)
                audio_val = res.audio_urls.get(dialect) or res.audio_urls.get("Audio")
                if text_val or audio_val:
                    label_name = "英" if dialect == "UK" else "美" if dialect == "US" else "拼" if dialect == "Pinyin" else "音标"
                    btn = AudioButton(f"{label_name} {text_val or ''}".strip(), audio_val or "")
                    btn.play_requested.connect(self.play_audio_requested.emit)
                    ph_row.addWidget(btn)

            # Sentence TTS fallback
            if not res.phonetics and res.audio_urls.get("Voice"):
                tts_btn = AudioButton("朗读整句", res.audio_urls.get("Voice"))
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

        # 2. Word Forms Card (词形变化: 过去式, 现在分词, 复数)
        if res.word_forms:
            wf_frame = QFrame()
            wf_frame.setProperty("class", "ResultCard")
            wf_layout = QVBoxLayout(wf_frame)
            wf_layout.setSpacing(6)

            wf_title = QLabel("词形变化")
            wf_title.setObjectName("SectionHeader")
            wf_layout.addWidget(wf_title)

            chips_layout = QHBoxLayout()
            chips_layout.setSpacing(6)
            for wf in res.word_forms:
                chips_layout.addWidget(WordFormChip(wf.name, wf.value))
            chips_layout.addStretch()
            wf_layout.addLayout(chips_layout)

            self.container_layout.addWidget(wf_frame)

        # 3. Section: 常见意思与释义 (Common Meanings & POS Breakdown)
        if res.pos_meanings or res.common_meanings:
            meanings_frame = QFrame()
            meanings_frame.setProperty("class", "ResultCard")
            m_layout = QVBoxLayout(meanings_frame)
            m_layout.setSpacing(8)

            sec_title = QLabel("详细释义")
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

        # 4. Section: 常用短语 (Phrases & Collocations)
        if res.phrases:
            phr_frame = QFrame()
            phr_frame.setProperty("class", "ResultCard")
            p_layout = QVBoxLayout(phr_frame)
            p_layout.setSpacing(6)

            p_title = QLabel("常用短语")
            p_title.setObjectName("SectionHeader")
            p_layout.addWidget(p_title)

            for phr in res.phrases[:4]:
                r = QHBoxLayout()
                hw = QLabel(phr.phrase)
                hw.setStyleSheet("font-weight: 600; color: #3b82f6;")
                tr = QLabel(phr.meaning)
                tr.setObjectName("ExampleTarget")
                r.addWidget(hw)
                r.addWidget(tr, stretch=1)
                p_layout.addLayout(r)

            self.container_layout.addWidget(phr_frame)

        # 5. Section: 近义词 (Synonyms)
        if res.synonyms:
            syn_frame = QFrame()
            syn_frame.setProperty("class", "ResultCard")
            s_layout = QVBoxLayout(syn_frame)
            s_layout.setSpacing(6)

            s_title = QLabel("近义词")
            s_title.setObjectName("SectionHeader")
            s_layout.addWidget(s_title)

            for syn in res.synonyms:
                r = QHBoxLayout()
                if syn.pos:
                    r.addWidget(PosBadge(syn.pos))
                w_label = QLabel(", ".join(syn.words))
                w_label.setObjectName("ExampleTarget")
                r.addWidget(w_label, stretch=1)
                s_layout.addLayout(r)

            self.container_layout.addWidget(syn_frame)

        # 6. Section: 经典例句 (Example Sentences)
        if res.examples:
            examples_frame = QFrame()
            examples_frame.setProperty("class", "ResultCard")
            ex_layout = QVBoxLayout(examples_frame)
            ex_layout.setSpacing(8)

            ex_sec_title = QLabel("双语例句")
            ex_sec_title.setObjectName("SectionHeader")
            ex_layout.addWidget(ex_sec_title)

            for ex in res.examples[:4]:
                card = QFrame()
                card.setProperty("class", "ExampleCard")
                c_layout = QVBoxLayout(card)
                c_layout.setSpacing(3)

                src_label = QLabel(self._highlight_keyword(ex.source, res.query))
                src_label.setObjectName("ExampleSource")
                src_label.setTextFormat(Qt.RichText)
                src_label.setWordWrap(True)
                src_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                c_layout.addWidget(src_label)

                tgt_label = QLabel(ex.target)
                tgt_label.setObjectName("ExampleTarget")
                tgt_label.setWordWrap(True)
                tgt_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                c_layout.addWidget(tgt_label)

                ex_layout.addWidget(card)

            self.container_layout.addWidget(examples_frame)

        # Bottom stretch to keep cards compact
        self.container_layout.addStretch()

    def _highlight_keyword(self, sentence: str, query: str) -> str:
        if not query or len(query) < 2:
            return sentence
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f'<b style="color: #3b82f6;">{m.group(0)}</b>', sentence)

    def _on_favorite_clicked(self):
        if not self.current_result:
            return
        is_fav = not self.current_result.is_favorite
        self.current_result.is_favorite = is_fav
        self.fav_btn.setText("★ 已收藏" if is_fav else "☆ 收藏")
        self.toggle_favorite_requested.emit(self.current_result.query, self.current_result.translation)
