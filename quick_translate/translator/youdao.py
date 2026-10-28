import re
import requests
from typing import Optional
from .models import (
    TranslationResult, ExampleSentence, PartOfSpeechMeaning,
    WordForm, PhraseItem, SynonymItem
)

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = str(text).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"<[^>]+>", "", text).strip()

class YoudaoTranslator:
    """Free Youdao Dictionary API client with phonetics, audio, POS, bilingual examples, word forms, and phrases."""

    BASE_URL = "https://dict.youdao.com/jsonapi"

    def __init__(self, timeout=4):
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
        word_forms = []
        phrases = []
        synonyms = []
        exam_tags = []
        collins_star = None
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
                    
                    match = re.match(r"^([a-zA-Z]+\.)\s*(.*)$", full_def)
                    if match:
                        pos = match.group(1)
                        definition = match.group(2)
                        pos_meanings.append(PartOfSpeechMeaning(pos=pos, definitions=[definition]))
                    else:
                        pos_meanings.append(PartOfSpeechMeaning(pos="释义", definitions=[full_def]))

            # Word forms
            for wf_item in w.get("wfs", []):
                wf = wf_item.get("wf", {})
                name = wf.get("name")
                val = wf.get("value")
                if name and val:
                    word_forms.append(WordForm(name=name, value=val))

            # Exam types
            for e in data["ec"].get("exam_type", []):
                if isinstance(e, str) and e.strip():
                    exam_tags.append(e.strip())

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

        # 3. Collins star
        if "collins" in data:
            entries = data["collins"].get("collins_entries", [])
            if entries and isinstance(entries, list):
                s = entries[0].get("star")
                if s and str(s).isdigit():
                    collins_star = int(s)

        # 4. Common Phrases
        if "phrs" in data:
            for p in data["phrs"].get("phrs", [])[:5]:
                phr_data = p.get("phr", {})
                hw = phr_data.get("headword", {}).get("l", {}).get("i")
                trs = phr_data.get("trs", [])
                tr_text = trs[0].get("tr", {}).get("l", {}).get("i") if trs else ""
                if hw and tr_text:
                    phrases.append(PhraseItem(phrase=clean_html(hw), meaning=clean_html(tr_text)))

        # 5. Synonyms
        if "syno" in data:
            for s in data["syno"].get("synos", [])[:3]:
                syno_item = s.get("syno", {})
                pos = syno_item.get("pos") or ""
                words = [w_item.get("w") for w_item in syno_item.get("ws", []) if w_item.get("w")]
                if words:
                    synonyms.append(SynonymItem(pos=pos, words=words[:5]))

        # 6. Web Translation fallback
        if not common_meanings and "web_trans" in data:
            web_data = data["web_trans"].get("web-translation", [])
            for item in web_data[:3]:
                key = item.get("key", "")
                trans_list = [t.get("value", "") for t in item.get("trans", [])]
                if trans_list:
                    common_meanings.append(f"{key}: " + ", ".join(trans_list))

        # 7. Translation (fanyi)
        if "fanyi" in data:
            primary_translation = data["fanyi"].get("tran", "")
        elif common_meanings:
            first = common_meanings[0]
            primary_translation = re.sub(r"^[a-zA-Z]+\.\s*", "", first).split("；")[0].split(";")[0]

        # 8. Bilingual Example Sentences (blng_sents_part)
        if "blng_sents_part" in data:
            sents = data["blng_sents_part"].get("sentence-pair", [])
            for s in sents[:6]:
                eng = clean_html(s.get("sentence-eng") or s.get("sentence", ""))
                cn = clean_html(s.get("sentence-translation", ""))
                if eng and cn:
                    examples.append(ExampleSentence(source=eng, target=cn))

        # Fallback to authentic sentences (auth_sents_part)
        if not examples and "auth_sents_part" in data:
            auth_sents = data["auth_sents_part"].get("sent", [])
            for s in auth_sents[:4]:
                foreign = clean_html(s.get("foreign", ""))
                source = clean_html(s.get("source", ""))
                if foreign:
                    examples.append(ExampleSentence(source=foreign, target=f"来源: {source}" if source else ""))

        return TranslationResult(
            query=query,
            translation=primary_translation,
            phonetics=phonetics,
            audio_urls=audio_urls,
            pos_meanings=pos_meanings,
            common_meanings=common_meanings,
            examples=examples,
            word_forms=word_forms,
            phrases=phrases,
            synonyms=synonyms,
            exam_tags=exam_tags,
            collins_star=collins_star,
            detected_lang=detected_lang,
            source_engine="Youdao Dict"
        )
