import os
import json
import sqlite3
from typing import Optional
from .models import TranslationResult, ExampleSentence, PartOfSpeechMeaning

class TranslationCache:
    """SQLite backed cache for translation results."""

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
                conn.execute("CREATE INDEX IF NOT EXISTS idx_query ON translations (query)")
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
                    return TranslationResult(
                        query=data["query"],
                        translation=data["translation"],
                        phonetics=data.get("phonetics", {}),
                        audio_urls=data.get("audio_urls", {}),
                        pos_meanings=pos_meanings,
                        common_meanings=data.get("common_meanings", []),
                        examples=examples,
                        detected_lang=data.get("detected_lang", "auto"),
                        source_engine=data.get("source_engine", "Cache"),
                        from_cache=True
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
                "detected_lang": result.detected_lang,
                "source_engine": result.source_engine
            }
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO translations (query, data_json) VALUES (?, ?)",
                    (query_key, json.dumps(payload, ensure_ascii=False))
                )
        except Exception as e:
            print(f"[Cache] Set error: {e}")

    def clear(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM translations")
        except Exception as e:
            print(f"[Cache] Clear error: {e}")
