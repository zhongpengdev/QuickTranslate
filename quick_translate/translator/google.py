import urllib.parse
import requests
from typing import Optional
from .models import TranslationResult, PartOfSpeechMeaning

class GoogleTranslator:
    """Free Google Translate web API client."""

    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def query(self, text: str, target_lang: str = "zh-CN") -> Optional[TranslationResult]:
        clean_text = text.strip()
        if not clean_text:
            return None

        # Determine target language: if text is Chinese, translate to English, else to target_lang
        # First quick pass
        is_mainly_chinese = any('\u4e00' <= char <= '\u9fff' for char in clean_text)
        actual_target = "en" if is_mainly_chinese else target_lang

        try:
            params = {
                "client": "gtx",
                "sl": "auto",
                "tl": actual_target,
                "hl": "zh-CN",
                "dt": ["t", "bd", "ex", "md", "rw", "rm", "ss"],
                "q": clean_text
            }
            resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            if resp.status_code != 200:
                return None
            data = resp.json()
            return self._parse_response(clean_text, data, actual_target)
        except Exception as e:
            print(f"[Google] Query error: {e}")
            return None

    def _parse_response(self, query: str, data: list, target_lang: str) -> TranslationResult:
        translation_parts = []
        pronunciation = None
        phonetics = {}
        audio_urls = {}

        # 1. Extracted translation and romanization
        if data and len(data) > 0 and data[0]:
            for item in data[0]:
                if item and item[0]:
                    translation_parts.append(item[0])
            # Last element often has pronunciation
            last_item = data[0][-1]
            if isinstance(last_item, list) and len(last_item) > 3:
                # [None, None, target_pronunciation, src_pronunciation]
                src_pron = last_item[3]
                target_pron = last_item[2]
                if src_pron:
                    pronunciation = src_pron
                elif target_pron:
                    pronunciation = target_pron

        primary_translation = "".join(translation_parts).strip()
        detected_lang = data[2] if len(data) > 2 else "auto"

        if pronunciation:
            phonetics["Phonetic"] = f"/{pronunciation}/"
        
        # Audio TTS link
        encoded = urllib.parse.quote(query)
        audio_urls["Voice"] = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={detected_lang}&q={encoded}"

        # 2. Part of Speech & Meanings
        pos_meanings = []
        common_meanings = []
        if len(data) > 1 and data[1]:
            for entry in data[1]:
                if isinstance(entry, list) and len(entry) >= 2:
                    pos = entry[0]
                    words = entry[1]
                    definitions = [", ".join(words[:8])]
                    pos_meanings.append(PartOfSpeechMeaning(pos=pos, definitions=definitions))
                    common_meanings.append(f"{pos}: {', '.join(words[:6])}")

        return TranslationResult(
            query=query,
            translation=primary_translation,
            phonetics=phonetics,
            audio_urls=audio_urls,
            pos_meanings=pos_meanings,
            common_meanings=common_meanings,
            examples=[],
            detected_lang=detected_lang,
            source_engine="Google Translate"
        )
