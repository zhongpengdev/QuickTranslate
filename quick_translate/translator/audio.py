import os
import shutil
import hashlib
import requests
import subprocess
import threading

class AudioPlayer:
    """Handles downloading and playing pronunciation audio clips asynchronously."""

    def __init__(self, cache_dir=None):
        if not cache_dir:
            cache_dir = os.path.expanduser("~/.cache/quicktranslate/audio")
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.current_proc = None

    def play_url(self, url: str):
        if not url:
            return
        threading.Thread(target=self._download_and_play, args=(url,), daemon=True).start()

    def play_word(self, word: str, voice_type: int = 2):
        """
        voice_type: 1 for UK, 2 for US
        """
        if not word:
            return
        url = f"https://dict.youdao.com/dictvoice?audio={word}&type={voice_type}"
        self.play_url(url)

    def play_tts(self, text: str, lang: str = "zh-CN"):
        if not text:
            return
        # Google TTS fallback for arbitrary sentences
        import urllib.parse
        encoded = urllib.parse.quote(text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={lang}&q={encoded}"
        self.play_url(url)

    def _download_and_play(self, url: str):
        try:
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
            local_path = os.path.join(self.cache_dir, f"{url_hash}.mp3")

            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200 and len(resp.content) > 100:
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                else:
                    print(f"[Audio] Failed to download audio from {url}: status {resp.status_code}")
                    return

            self._play_file(local_path)
        except Exception as e:
            print(f"[Audio] Error playing audio: {e}")

    def _play_file(self, file_path: str):
        # Stop any currently playing audio
        if self.current_proc and self.current_proc.poll() is None:
            try:
                self.current_proc.terminate()
            except Exception:
                pass

        # Try available players
        if shutil.which("ffplay"):
            self.current_proc = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif shutil.which("mpv"):
            self.current_proc = subprocess.Popen(
                ["mpv", "--no-video", "--really-quiet", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif shutil.which("paplay"):
            self.current_proc = subprocess.Popen(
                ["paplay", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif shutil.which("aplay"):
            self.current_proc = subprocess.Popen(
                ["aplay", "-q", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            print("[Audio] No supported audio player found on system (ffplay, mpv, paplay, aplay).")
