import concurrent.futures
from typing import Optional, List, Dict
from .models import TranslationResult, PartOfSpeechMeaning, ExampleSentence
from .cache import TranslationCache
from .youdao import YoudaoTranslator
from .google import GoogleTranslator
from .audio import AudioPlayer

class TranslationEngine:
    """
    High-precision, high-speed translation engine aggregator.
    Combines Youdao Dict and Google Translate with rich dictionary data and caching.
    """

    def __init__(self, cache_db=None):
        self.cache = TranslationCache(cache_db)
        self.youdao = YoudaoTranslator(timeout=4)
        self.google = GoogleTranslator(timeout=4)
        self.audio = AudioPlayer()

    def translate(self, text: str, force_refresh: bool = False) -> TranslationResult:
        query = text.strip()
        if not query:
            return TranslationResult(
                query="",
                translation="",
                error="请输入要查询的词汇或句子"
            )

        # 1. Check cache for instant lookup
        if not force_refresh:
            cached = self.cache.get(query)
            if cached and cached.has_content():
                cached.is_favorite = self.cache.is_favorite(query)
                return cached

        # 2. Parallel fetch from free engines
        res_yd: Optional[TranslationResult] = None
        res_gg: Optional[TranslationResult] = None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_yd = executor.submit(self.youdao.query, query)
            future_gg = executor.submit(self.google.query, query)

            try:
                res_yd = future_yd.result(timeout=4.5)
            except Exception as e:
                print(f"[Engine] Youdao error: {e}")

            try:
                res_gg = future_gg.result(timeout=4.5)
            except Exception as e:
                print(f"[Engine] Google error: {e}")

        # 3. Aggregate results
        aggregated = self._merge_results(query, res_yd, res_gg)
        aggregated.is_favorite = self.cache.is_favorite(query)

        # 4. Save to cache if valid
        if aggregated and aggregated.has_content() and not aggregated.error:
            self.cache.set(aggregated)

        return aggregated

    def _merge_results(
        self,
        query: str,
        yd: Optional[TranslationResult],
        gg: Optional[TranslationResult]
    ) -> TranslationResult:
        if not yd and not gg:
            return TranslationResult(
                query=query,
                translation="",
                error="未能获取翻译结果，请检查网络或输入。"
            )

        if yd and not gg:
            return yd
        if gg and not yd:
            return gg

        # Both succeeded: combine best of both
        word_count = len(query.split())
        is_sentence = word_count > 4 or any(p in query for p in ["。", "！", "？", ".", "!", "?"])

        if is_sentence and gg.translation:
            primary_trans = gg.translation
        else:
            primary_trans = yd.translation or gg.translation

        # Phonetics
        phonetics = dict(yd.phonetics)
        for k, v in gg.phonetics.items():
            if k not in phonetics and not phonetics:
                phonetics[k] = v

        # Audio URLs
        audio_urls = dict(yd.audio_urls)
        for k, v in gg.audio_urls.items():
            if k not in audio_urls:
                audio_urls[k] = v

        # POS Meanings
        pos_meanings = list(yd.pos_meanings)
        if not pos_meanings and gg.pos_meanings:
            pos_meanings = list(gg.pos_meanings)

        common_meanings = list(yd.common_meanings)
        if not common_meanings and gg.common_meanings:
            common_meanings = list(gg.common_meanings)

        # Examples
        examples = list(yd.examples)

        detected_lang = yd.detected_lang or gg.detected_lang or "auto"

        return TranslationResult(
            query=query,
            translation=primary_trans,
            phonetics=phonetics,
            audio_urls=audio_urls,
            pos_meanings=pos_meanings,
            common_meanings=common_meanings,
            examples=examples,
            word_forms=list(yd.word_forms),
            phrases=list(yd.phrases),
            synonyms=list(yd.synonyms),
            exam_tags=list(yd.exam_tags),
            collins_star=yd.collins_star,
            detected_lang=detected_lang,
            source_engine="Smart Hybrid",
            from_cache=False
        )

    def play_audio(self, url: str):
        self.audio.play_url(url)

    def play_word(self, word: str, voice_type: int = 2):
        self.audio.play_word(word, voice_type)

    def play_tts(self, text: str, lang: str = "zh-CN"):
        self.audio.play_tts(text, lang)

    def get_recent_history(self, limit: int = 8) -> List[Dict[str, str]]:
        return self.cache.get_recent_history(limit)

    def clear_history(self):
        self.cache.clear_history()

    def toggle_favorite(self, query: str, translation: str = "") -> bool:
        return self.cache.toggle_favorite(query, translation)

    def get_favorites(self) -> List[Dict[str, str]]:
        return self.cache.get_favorites()
