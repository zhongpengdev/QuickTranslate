import os
import json
import sqlite3
from typing import Optional, List, Dict
from .models import (
    TranslationResult, ExampleSentence, PartOfSpeechMeaning,
    WordForm, PhraseItem, SynonymItem
)

class TranslationCache:
    """SQLite backed cache for translation results, search history, and favorite words."""

    def __init__(self, db_path=None):
        if not db_path:
            cache_dir = os.path.expanduser("~/.cache/quicktranslate")
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.path.join(cache_dir, "cache.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS translations (
                        query TEXT PRIMARY KEY,
                        data_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT UNIQUE NOT NULL,
                        translation TEXT,
                        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS favorites (
                        query TEXT PRIMARY KEY,
                        translation TEXT,
                        starred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_query ON translations (query)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_history ON search_history (searched_at DESC)")
        except Exception as e:
            print(f"[Cache] Init error: {e}")

    def get(self, query: str) -> Optional[TranslationResult]:
        query_key = query.strip().lower()
        if not query_key:
            return None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM translations WHERE query = ?", (query_key,))
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    pos_meanings = [
                        PartOfSpeechMeaning(pos=item["pos"], definitions=item["definitions"])
                        for item in data.get("pos_meanings", [])
                    ]
                    examples = [
                        ExampleSentence(source=item["source"], target=item["target"])
                        for item in data.get("examples", [])
                    ]
                    word_forms = [
                        WordForm(name=item["name"], value=item["value"])
                        for item in data.get("word_forms", [])
                    ]
                    phrases = [
                        PhraseItem(phrase=item["phrase"], meaning=item["meaning"])
                        for item in data.get("phrases", [])
                    ]
                    synonyms = [
                        SynonymItem(pos=item["pos"], words=item["words"])
                        for item in data.get("synonyms", [])
                    ]
                    is_fav = self.is_favorite(query_key)
                    return TranslationResult(
                        query=data["query"],
                        translation=data["translation"],
                        phonetics=data.get("phonetics", {}),
                        audio_urls=data.get("audio_urls", {}),
                        pos_meanings=pos_meanings,
                        common_meanings=data.get("common_meanings", []),
                        examples=examples,
                        word_forms=word_forms,
                        phrases=phrases,
                        synonyms=synonyms,
                        exam_tags=data.get("exam_tags", []),
                        collins_star=data.get("collins_star"),
                        detected_lang=data.get("detected_lang", "auto"),
                        source_engine=data.get("source_engine", "Cache"),
                        from_cache=True,
                        is_favorite=is_fav
                    )
        except Exception as e:
            print(f"[Cache] Get error: {e}")
        return None

    def set(self, result: TranslationResult):
        if not result or not result.query or result.error:
            return
        query_key = result.query.strip().lower()
        try:
            payload = {
                "query": result.query,
                "translation": result.translation,
                "phonetics": result.phonetics,
                "audio_urls": result.audio_urls,
                "pos_meanings": [{"pos": p.pos, "definitions": p.definitions} for p in result.pos_meanings],
                "common_meanings": result.common_meanings,
                "examples": [{"source": e.source, "target": e.target} for e in result.examples],
                "word_forms": [{"name": wf.name, "value": wf.value} for wf in result.word_forms],
                "phrases": [{"phrase": ph.phrase, "meaning": ph.meaning} for ph in result.phrases],
                "synonyms": [{"pos": s.pos, "words": s.words} for s in result.synonyms],
                "exam_tags": result.exam_tags,
                "collins_star": result.collins_star,
                "detected_lang": result.detected_lang,
                "source_engine": result.source_engine
            }
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO translations (query, data_json) VALUES (?, ?)",
                    (query_key, json.dumps(payload, ensure_ascii=False))
                )
                # Also log to search history
                conn.execute(
                    "INSERT OR REPLACE INTO search_history (query, translation, searched_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (result.query.strip(), result.translation)
                )
        except Exception as e:
            print(f"[Cache] Set error: {e}")

    def get_recent_history(self, limit: int = 8) -> List[Dict[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT query, translation FROM search_history ORDER BY searched_at DESC LIMIT ?",
                    (limit,)
                )
                return [{"query": r[0], "translation": r[1] or ""} for r in cursor.fetchall()]
        except Exception as e:
            print(f"[Cache] Get history error: {e}")
            return []

    def clear_history(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM search_history")
        except Exception as e:
            print(f"[Cache] Clear history error: {e}")

    def toggle_favorite(self, query: str, translation: str = "") -> bool:
        """Toggles favorite state. Returns True if now favorite, False if removed."""
        query_clean = query.strip()
        if not query_clean:
            return False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM favorites WHERE query = ?", (query_clean,))
                exists = cursor.fetchone()
                if exists:
                    conn.execute("DELETE FROM favorites WHERE query = ?", (query_clean,))
                    return False
                else:
                    conn.execute(
                        "INSERT INTO favorites (query, translation) VALUES (?, ?)",
                        (query_clean, translation)
                    )
                    return True
        except Exception as e:
            print(f"[Cache] Toggle favorite error: {e}")
            return False

    def is_favorite(self, query: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM favorites WHERE query = ?", (query.strip(),))
                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_favorites(self) -> List[Dict[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT query, translation FROM favorites ORDER BY starred_at DESC")
                return [{"query": r[0], "translation": r[1] or ""} for r in cursor.fetchall()]
        except Exception as e:
            print(f"[Cache] Get favorites error: {e}")
            return []
