import re
import requests
from typing import Optional
from .models import TranslationResult, ExampleSentence, PartOfSpeechMeaning

def clean_html(text: str) -> str:
    if not text:
        return ""
    # Replace HTML entities and tags
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"<[^>]+>", "", text).strip()

class YoudaoTranslator:
    """Free Youdao Dictionary API client with phonetic, audio, POS, and bilingual examples."""

    BASE_URL = "https://dict.youdao.com/jsonapi"

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def query(self, text: str) -> Optional[TranslationResult]:
        clean_text = text.strip()
        if not clean_text:
            return None

        try:
            resp = self.session.get(self.BASE_URL, params={"q": clean_text}, timeout=self.timeout)
            if resp.status_code != 200:
                return None
            data = resp.json()
            return self._parse_response(clean_text, data)
        except Exception as e:
            print(f"[Youdao] Query error: {e}")
            return None

    def _parse_response(self, query: str, data: dict) -> TranslationResult:
        phonetics = {}
        audio_urls = {}
        pos_meanings = []
        common_meanings = []
        examples = []
        primary_translation = ""
        detected_lang = "en"

        # 1. English to Chinese (ec)
        if "ec" in data:
            detected_lang = "en"
            w = data["ec"].get("word", [{}])[0]
            
            # Phonetics
            uk_phone = w.get("ukphone")
            us_phone = w.get("usphone")
            phone = w.get("phone")

            if uk_phone:
                phonetics["UK"] = f"/{uk_phone}/"
                audio_urls["UK"] = f"https://dict.youdao.com/dictvoice?audio={query}&type=1"
            if us_phone:
                phonetics["US"] = f"/{us_phone}/"
                audio_urls["US"] = f"https://dict.youdao.com/dictvoice?audio={query}&type=2"
            if not phonetics and phone:
                phonetics["Phonetic"] = f"/{phone}/"
                audio_urls["Audio"] = f"https://dict.youdao.com/dictvoice?audio={query}&type=2"

            # Definitions & POS
            trs = w.get("trs", [])
            for tr_item in trs:
                tr = tr_item.get("tr", [{}])[0]
                pos_text_arr = tr.get("l", {}).get("i", [])
                if pos_text_arr:
                    full_def = " ".join(str(x) for x in pos_text_arr).strip()
                    common_meanings.append(full_def)
                    
                    # Split into POS and definition if matches "pos. definition"
                    match = re.match(r"^([a-zA-Z]+\.)\s*(.*)$", full_def)
                    if match:
                        pos = match.group(1)
                        definition = match.group(2)
                        pos_meanings.append(PartOfSpeechMeaning(pos=pos, definitions=[definition]))
                    else:
                        pos_meanings.append(PartOfSpeechMeaning(pos="释义", definitions=[full_def]))

        # 2. Chinese to English (ce)
        elif "ce" in data:
            detected_lang = "zh"
            w = data["ce"].get("word", [{}])[0]
            phone = w.get("phone")
            if phone:
                phonetics["Pinyin"] = f"[{phone}]"
                audio_urls["Audio"] = f"https://dict.youdao.com/dictvoice?audio={query}&le=zh"

            trs = w.get("trs", [])
            for tr_item in trs:
                tr = tr_item.get("tr", [{}])[0]
                pos_text_arr = tr.get("l", {}).get("i", [])
                tokens = []
                for item in pos_text_arr:
                    if isinstance(item, dict) and "#text" in item:
                        tokens.append(item["#text"])
                    elif isinstance(item, str):
                        tokens.append(item.strip())
                joined = " ".join(t for t in tokens if t).strip()
                if joined:
                    common_meanings.append(joined)
                    pos_meanings.append(PartOfSpeechMeaning(pos="英译", definitions=[joined]))

        # 3. Web Translation if ec/ce empty
        if not common_meanings and "web_trans" in data:
            web_data = data["web_trans"].get("web-translation", [])
            for item in web_data[:3]:
                key = item.get("key", "")
                trans_list = [t.get("value", "") for t in item.get("trans", [])]
                if trans_list:
                    common_meanings.append(f"{key}: " + ", ".join(trans_list))

        # 4. Translation (fanyi)
        if "fanyi" in data:
            primary_translation = data["fanyi"].get("tran", "")
        elif common_meanings:
            # First meaning as primary translation
            first = common_meanings[0]
            # Strip POS prefix like "n. " if present
            primary_translation = re.sub(r"^[a-zA-Z]+\.\s*", "", first).split("；")[0].split(";")[0]

        # 5. Bilingual Example Sentences (blng_sents_part)
        if "blng_sents_part" in data:
            sents = data["blng_sents_part"].get("sentence-pair", [])
            for s in sents[:6]:
                eng = clean_html(s.get("sentence-eng") or s.get("sentence", ""))
                cn = clean_html(s.get("sentence-translation", ""))
                if eng and cn:
                    examples.append(ExampleSentence(source=eng, target=cn))

        # 6. Fallback to authentic sentences (auth_sents_part)
        if not examples and "auth_sents_part" in data:
            auth_sents = data["auth_sents_part"].get("sent", [])
            for s in auth_sents[:5]:
                foreign = clean_html(s.get("foreign", ""))
                speech = clean_html(s.get("speech", ""))
                source = clean_html(s.get("source", ""))
                target = f"来源: {source}" if source else ""
                if foreign:
                    examples.append(ExampleSentence(source=foreign, target=target))

        return TranslationResult(
            query=query,
            translation=primary_translation,
            phonetics=phonetics,
            audio_urls=audio_urls,
            pos_meanings=pos_meanings,
            common_meanings=common_meanings,
            examples=examples,
            detected_lang=detected_lang,
            source_engine="Youdao Dict"
        )
