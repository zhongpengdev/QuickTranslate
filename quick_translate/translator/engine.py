import concurrent.futures
from typing import Optional
from .models import TranslationResult, PartOfSpeechMeaning, ExampleSentence
from .cache import TranslationCache
from .youdao import YoudaoTranslator
from .google import GoogleTranslator
from .audio import AudioPlayer

class TranslationEngine:
    """
    High-precision, high-speed translation engine aggregator.
    Leverages parallel fetching between Youdao Dict and Google Translate with local caching.
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
                error="请输入要翻译的内容"
            )

        # 1. Check cache for instant lookup
        if not force_refresh:
            cached = self.cache.get(query)
            if cached and cached.has_content():
                return cached

        # 2. Parallel fetch from free engines
        res_yd: Optional[TranslationResult] = None
        res_gg: Optional[TranslationResult] = None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_yd = executor.submit(self.youdao.query, query)
            future_gg = executor.submit(self.google.query, query)

            try:
                res_yd = future_yd.result(timeout=5)
            except Exception as e:
                print(f"[Engine] Youdao error: {e}")

            try:
                res_gg = future_gg.result(timeout=5)
            except Exception as e:
                print(f"[Engine] Google error: {e}")

        # 3. Aggregate results
        aggregated = self._merge_results(query, res_yd, res_gg)

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
                error="网络连接失败或未能找到释义，请稍后重试。"
            )

        if yd and not gg:
            return yd
        if gg and not yd:
            return gg

        # Both succeeded: combine the best of both!
        # Primary translation: prefer Youdao for single words / idioms, prefer Google for long sentences
        word_count = len(query.split())
        is_sentence = word_count > 4 or any(p in query for p in ["。", "！", "？", ".", "!", "?"])

        if is_sentence and gg.translation:
            primary_trans = gg.translation
        else:
            primary_trans = yd.translation or gg.translation

        # Phonetics: combine UK/US from Youdao and any from Google
        phonetics = dict(yd.phonetics)
        for k, v in gg.phonetics.items():
            if k not in phonetics and not phonetics:
                phonetics[k] = v

        # Audio URLs: combine Youdao audio and Google voice
        audio_urls = dict(yd.audio_urls)
        for k, v in gg.audio_urls.items():
            if k not in audio_urls:
                audio_urls[k] = v

        # POS Meanings & Common Meanings: prefer Youdao's rich dict, append Google's if missing
        pos_meanings = list(yd.pos_meanings)
        if not pos_meanings and gg.pos_meanings:
            pos_meanings = list(gg.pos_meanings)

        common_meanings = list(yd.common_meanings)
        if not common_meanings and gg.common_meanings:
            common_meanings = list(gg.common_meanings)

        # Examples: use Youdao's bilingual example sentences
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
            detected_lang=detected_lang,
            source_engine="Smart Hybrid (Youdao + Google)",
            from_cache=False
        )

    def play_audio(self, url: str):
        self.audio.play_url(url)

    def play_word(self, word: str, voice_type: int = 2):
        self.audio.play_word(word, voice_type)

    def play_tts(self, text: str, lang: str = "zh-CN"):
        self.audio.play_tts(text, lang)
