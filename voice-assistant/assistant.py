"""
Voice Assistant — laptop/PC ko awaaz se chalayein (Windows).

Bolein:  "notepad kholo", "chrome open karo", "youtube par naat chalao",
         "google par honda cd70 price search karo", "awaaz barhao",
         "screenshot lo", "time kya hai", "likho assalam o alaikum",
         "computer band karo" (pehle tasdeeq poochega), "band karna cancel".
Band karne ke liye:  "assistant band karo"  ya  "exit".
"""

import datetime
import os
import re
import subprocess
import sys
import urllib.parse
import webbrowser

# ---------- Settings ----------
LANGUAGE = "en-IN"          # Roman Urdu/English ke liye best. Urdu script ke liye "ur-PK".
WAKE_WORD = None            # misal "computer" — tab sirf "computer notepad kholo" par amal hoga
HONDA_URL = "https://honda.nextgenaidevelopers.com"

# Bolay gaye naam -> Windows command
APPS = {
    "notepad": "notepad",
    "calculator": "calc", "calc": "calc",
    "paint": "mspaint",
    "chrome": "start chrome", "browser": "start chrome",
    "edge": "start msedge",
    "explorer": "explorer", "file": "explorer", "files": "explorer", "my computer": "explorer",
    "cmd": "start cmd", "command prompt": "start cmd",
    "settings": "start ms-settings:",
    "task manager": "taskmgr",
    "control panel": "control",
    "word": "start winword", "excel": "start excel", "powerpoint": "start powerpnt",
    "whatsapp": "start whatsapp:",
    "camera": "start microsoft.windows.camera:",
    "vs code": "code", "vscode": "code",
}

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "gmail": "https://mail.google.com",
    "whatsapp web": "https://web.whatsapp.com",
    "github": "https://github.com",
    "honda": HONDA_URL,
}

# Roman Urdu / English / Urdu alfaaz jo "kholo" ka matlab dete hain
OPEN_WORDS = r"(kholo|khol do|khol|open karo|open kar do|open|chalao|chala do|start karo|start|launch|کھولو|چلاؤ)"
CLOSE_WORDS = r"(band karo|band kar do|close karo|close|بند کرو)"


def _norm(text):
    text = text.lower().strip()
    text = re.sub(r"(?<!\w)\.|\.(?!\w)|[,!?؟।]", " ", text)   # "daraz.pk" ka dot rehne do
    return re.sub(r"\s+", " ", text).strip()


def parse(text):
    """Bola gaya jumla -> (action, argument). Pure function, test ho sakta hai."""
    t = _norm(text)
    if not t:
        return ("none", None)

    if WAKE_WORD:
        if not t.startswith(WAKE_WORD):
            return ("none", None)
        t = t[len(WAKE_WORD):].strip()

    # --- assistant khud band ---
    if re.search(r"\b(exit|quit|stop listening)\b", t) or re.search(r"assistant (band|close|stop)", t):
        return ("exit", None)

    # --- shutdown / restart / sleep / lock ---
    if re.search(r"(shutdown|shut down).*(cancel|ruko|mat)|(cancel|ruko).*(shutdown|band)|band karna cancel", t):
        return ("cancel_shutdown", None)
    if re.search(r"(computer|laptop|pc|system) (band|shutdown|shut down)|^shutdown|^shut down", t):
        return ("shutdown", None)
    if re.search(r"(restart|reboot|dobara chalu)", t):
        return ("restart", None)
    if re.search(r"\b(sleep|sula do|so jao)\b", t):
        return ("sleep", None)
    if re.search(r"\block\b|lock karo|taala", t):
        return ("lock", None)

    # --- volume ---
    if re.search(r"(mute|awaaz band|awaz band|chup)", t) and not re.search(r"unmute", t):
        return ("mute", None)
    if re.search(r"unmute|awaaz kholo|awaz kholo", t):
        return ("mute", None)  # mute key toggle karti hai
    if re.search(r"(volume|awaaz|awaz|آواز).*(up|barhao|badhao|zyada|ziada|tez|increase|بڑھاؤ)", t):
        return ("volume_up", None)
    if re.search(r"(volume|awaaz|awaz|آواز).*(down|kam|ahista|halki|decrease|کم)", t):
        return ("volume_down", None)

    # --- media ---
    if re.search(r"\b(pause|play|ruko|roko)\b", t) and not re.search(r"(chalao|par|pe|on) ", t):
        return ("play_pause", None)
    if re.search(r"(next song|agla gana|agla|next)", t):
        return ("next_track", None)

    # --- screenshot ---
    if re.search(r"screen ?shot|screen ki tasveer", t):
        return ("screenshot", None)

    # --- time / date ---
    if re.search(r"(time|waqt|ٹائم|وقت).*(kya|kitna|batao|hai)|what.*time|^time$", t):
        return ("time", None)
    if re.search(r"(date|tareekh|tarikh|aaj).*(kya|batao|hai)|what.*date", t):
        return ("date", None)

    # --- youtube par kuch chalao ---
    m = re.search(r"youtube (par|pe|on) (.+?) (chalao|chala do|lagao|play karo|play|search karo|search|dikhao)$", t)
    if m:
        return ("youtube", m.group(2))
    m = re.search(r"^play (.+?) on youtube$", t)
    if m:
        return ("youtube", m.group(1))

    # --- google search ---
    m = re.search(r"(?:google (?:par|pe|on) )?(.+?) (search karo|search kar do|search|dhoondo|talash karo|تلاش کرو)$", t)
    if m:
        return ("search", m.group(1).replace("google par ", "").strip())
    m = re.search(r"^(?:search|google) (?:for )?(.+)$", t)
    if m:
        return ("search", m.group(1))

    # --- type karo ---
    m = re.search(r"^(likho|type karo|type|لکھو) (.+)$", t)
    if m:
        return ("type", m.group(2))
    m = re.search(r"^(.+) (likho|type karo|لکھو)$", t)
    if m:
        return ("type", m.group(1))

    # --- keyboard ---
    if re.search(r"(enter dabao|press enter|^enter$)", t):
        return ("key", "enter")
    if re.search(r"(save karo|^save$)", t):
        return ("hotkey", "ctrl+s")
    if re.search(r"(copy karo|^copy$)", t):
        return ("hotkey", "ctrl+c")
    if re.search(r"(paste karo|^paste$)", t):
        return ("hotkey", "ctrl+v")
    if re.search(r"(undo|wapis karo)", t):
        return ("hotkey", "ctrl+z")
    if re.search(r"(select all|sab select)", t):
        return ("hotkey", "ctrl+a")
    if re.search(r"(window band|tab band|close window|close tab)", t):
        return ("hotkey", "ctrl+w" if "tab" in t else "alt+f4")
    if re.search(r"(desktop dikhao|show desktop|sab minimize)", t):
        return ("hotkey", "win+d")
    if re.search(r"(scroll down|neeche|niche)", t):
        return ("scroll", -500)
    if re.search(r"(scroll up|upar|oopar)", t):
        return ("scroll", 500)

    # --- close app ---
    m = re.search(rf"^(.+?) {CLOSE_WORDS}$", t)
    if m and m.group(1) in APPS:
        return ("close_app", m.group(1))

    # --- open app / site ---
    m = re.search(rf"^(?:{OPEN_WORDS} )?(.+?)(?: {OPEN_WORDS})?$", t)
    if m:
        name = m.group(2).replace(" app", "").replace(" software", "").strip()
        has_open_word = bool(m.group(1) or m.group(3))
        for key in sorted(SITES, key=len, reverse=True):   # "whatsapp web" pehle
            if name == key and (has_open_word or key in ("youtube", "gmail")):
                return ("open_site", key)
        if name in APPS and has_open_word:
            return ("open_app", name)
        if has_open_word and name.endswith((".com", ".pk", ".org", ".net")):
            return ("open_url", name)

    return ("unknown", t)


# ================= Executors (Windows) =================

def speak(msg):
    print(">>", msg)
    try:
        import pyttsx3
        eng = pyttsx3.init()
        eng.say(msg)
        eng.runAndWait()
    except Exception:
        pass


def _run(cmd):
    subprocess.Popen(cmd, shell=True)


def _process_name(app):
    exe = APPS[app].replace("start ", "").split(":")[0]
    return {"calc": "CalculatorApp.exe", "msedge": "msedge.exe"}.get(exe, exe + ".exe")


def confirm(listen):
    speak("Pakka? Haan ya nahi bolein.")
    ans = _norm(listen() or "")
    return bool(re.search(r"\b(haan|han|ha|yes|ji|jee|ok|okay|ہاں|جی)\b", ans))


def execute(action, arg, listen):
    import pyautogui  # sirf Windows/desktop par chahiye
    if action == "open_app":
        _run(APPS[arg]); speak(f"{arg} khol raha hoon")
    elif action == "close_app":
        _run(f"taskkill /im {_process_name(arg)} /f"); speak(f"{arg} band kar diya")
    elif action == "open_site":
        webbrowser.open(SITES[arg]); speak(f"{arg} khol raha hoon")
    elif action == "open_url":
        webbrowser.open("https://" + arg); speak(f"{arg} khol raha hoon")
    elif action == "search":
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(arg))
        speak(f"{arg} search kar raha hoon")
    elif action == "youtube":
        webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(arg))
        speak(f"YouTube par {arg}")
    elif action == "type":
        pyautogui.write(arg, interval=0.02)
    elif action == "key":
        pyautogui.press(arg)
    elif action == "hotkey":
        pyautogui.hotkey(*arg.split("+"))
    elif action == "scroll":
        pyautogui.scroll(arg)
    elif action == "volume_up":
        pyautogui.press("volumeup", presses=5)
    elif action == "volume_down":
        pyautogui.press("volumedown", presses=5)
    elif action == "mute":
        pyautogui.press("volumemute")
    elif action == "play_pause":
        pyautogui.press("playpause")
    elif action == "next_track":
        pyautogui.press("nexttrack")
    elif action == "screenshot":
        folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, datetime.datetime.now().strftime("voice_%Y%m%d_%H%M%S.png"))
        pyautogui.screenshot(path); speak("Screenshot save ho gaya")
    elif action == "time":
        speak("Abhi " + datetime.datetime.now().strftime("%I:%M %p") + " hain")
    elif action == "date":
        speak("Aaj " + datetime.datetime.now().strftime("%d %B %Y") + " hai")
    elif action == "lock":
        _run("rundll32.exe user32.dll,LockWorkStation")
    elif action == "sleep":
        if confirm(listen):
            _run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif action == "shutdown":
        if confirm(listen):
            _run("shutdown /s /t 30"); speak("30 second mein band hoga. Rokne ke liye bolein: band karna cancel")
    elif action == "restart":
        if confirm(listen):
            _run("shutdown /r /t 30"); speak("30 second mein restart hoga")
    elif action == "cancel_shutdown":
        _run("shutdown /a"); speak("Cancel kar diya")
    elif action == "unknown":
        print("   (samajh nahi aaya:", arg, ")")


def main():
    import speech_recognition as sr
    rec = sr.Recognizer()
    rec.pause_threshold = 0.8
    mic = sr.Microphone()
    with mic as source:
        print("Shor naap raha hoon... 1 second khamosh rahein")
        rec.adjust_for_ambient_noise(source, duration=1)

    def listen():
        with mic as source:
            try:
                audio = rec.listen(source, timeout=6, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                return None
        try:
            return rec.recognize_google(audio, language=LANGUAGE)
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("!! Internet check karein (Google speech ko internet chahiye)")
            return None

    speak("Assistant tayyar hai. Bolein.")
    while True:
        print("\n🎤 Sun raha hoon...")
        heard = listen()
        if not heard:
            continue
        print("Suna:", heard)
        action, arg = parse(heard)
        if action == "exit":
            speak("Khuda Hafiz"); break
        try:
            execute(action, arg, listen)
        except Exception as e:
            print("!! Error:", e)


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Note: yeh assistant Windows ke liye bana hai; kuch commands doosre OS par nahi chalenge.")
    main()
