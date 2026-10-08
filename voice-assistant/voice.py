"""Awaaz sunna (Google free speech) aur bolna (Microsoft Edge ki free Urdu awaaz)."""

import asyncio
import ctypes
import os
import re
import tempfile

import speech_recognition as sr

LISTEN_LANGUAGE = os.getenv("LISTEN_LANGUAGE", "ur-PK")      # English ke liye "en-IN"
SPEAK_VOICE = os.getenv("SPEAK_VOICE", "ur-PK-AsadNeural")   # aurat ki awaaz: ur-PK-UzmaNeural

_rec = sr.Recognizer()
_rec.pause_threshold = 1.0
_mic = None


def _microphone():
    global _mic
    if _mic is None:
        _mic = sr.Microphone()
        with _mic as source:
            _rec.adjust_for_ambient_noise(source, duration=1)
    return _mic


def listen(timeout=7, phrase_limit=20):
    """Mic se ek jumla sun kar text wapis karta hai (ya None)."""
    with _microphone() as source:
        print("🎤 Bolein...")
        try:
            audio = _rec.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return None
    try:
        text = _rec.recognize_google(audio, language=LISTEN_LANGUAGE)
        print("🗣  Aap:", text)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("!! Internet check karein — awaaz pehchanne ke liye internet chahiye.")
        return None


def _play_mp3(path):
    """Windows ka built-in player (winmm) — koi extra library nahi."""
    mci = ctypes.windll.winmm.mciSendStringW
    mci(f'open "{path}" type mpegvideo alias tts', None, 0, None)
    mci("play tts wait", None, 0, None)
    mci("close tts", None, 0, None)


def speak(text):
    print("🤖 Assistant:", text)
    if not text:
        return
    try:
        import edge_tts
        path = os.path.join(tempfile.gettempdir(), "assistant_tts.mp3")
        asyncio.run(edge_tts.Communicate(text, SPEAK_VOICE).save(path))
        _play_mp3(path)
    except Exception:
        try:  # internet na ho to Windows ki apni (English) awaaz
            import pyttsx3
            eng = pyttsx3.init()
            eng.say(text)
            eng.runAndWait()
        except Exception:
            pass


def ask_yes_no(question):
    """Sawal bol kar haan/nahi suno. Awaaz samajh na aaye to keyboard se poochho."""
    speak(question)
    for _ in range(2):
        words = set(re.findall(r"\w+", (listen(timeout=8, phrase_limit=5) or "").lower()))
        if words & {"nahi", "nahin", "no", "mat", "ruko", "نہیں", "نہ", "مت", "رکو"}:
            return False
        if words & {"haan", "han", "ha", "yes", "ji", "jee", "ok", "okay", "theek", "ہاں", "جی", "ٹھیک", "اوکے"}:
            return True
        speak("Haan ya nahi bolein.")
    return input("Keyboard se jawab dein (haan/nahi): ").strip().lower() in ("haan", "han", "h", "yes", "y")
