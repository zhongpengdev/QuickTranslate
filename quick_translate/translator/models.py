from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ExampleSentence:
    source: str
    target: str

@dataclass
class PartOfSpeechMeaning:
    pos: str
    definitions: List[str]

@dataclass
class WordForm:
    name: str    # e.g. "过去式", "复数", "现在分词"
    value: str   # e.g. "ran", "runs", "running"

@dataclass
class PhraseItem:
    phrase: str
    meaning: str

@dataclass
class SynonymItem:
    pos: str
    words: List[str]

@dataclass
class TranslationResult:
    query: str
    translation: str
    phonetics: Dict[str, str] = field(default_factory=dict)     # e.g. {"UK": "/.../", "US": "/.../"}
    audio_urls: Dict[str, str] = field(default_factory=dict)    # e.g. {"UK": "http...", "US": "http..."}
    pos_meanings: List[PartOfSpeechMeaning] = field(default_factory=list)
    common_meanings: List[str] = field(default_factory=list)
    examples: List[ExampleSentence] = field(default_factory=list)
    word_forms: List[WordForm] = field(default_factory=list)
    phrases: List[PhraseItem] = field(default_factory=list)
    synonyms: List[SynonymItem] = field(default_factory=list)
    exam_tags: List[str] = field(default_factory=list)
    collins_star: Optional[int] = None
    detected_lang: str = "auto"
    source_engine: str = "Aggregated"
    from_cache: bool = False
    is_favorite: bool = False
    error: Optional[str] = None

    def has_content(self) -> bool:
        return bool(self.translation or self.pos_meanings or self.common_meanings or self.examples)
