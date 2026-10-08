"""Computer ke kaam jo AI khud kar sakta hai. Har function ka docstring Gemini ko batata hai ke yeh kya karta hai."""

import datetime
import os
import subprocess
import urllib.parse
import webbrowser

from voice import ask_yes_no

APPS = {
    "notepad": "notepad", "calculator": "calc", "paint": "mspaint",
    "chrome": "start chrome", "edge": "start msedge", "file explorer": "explorer",
    "cmd": "start cmd", "settings": "start ms-settings:", "task manager": "taskmgr",
    "control panel": "control", "word": "start winword", "excel": "start excel",
    "powerpoint": "start powerpnt", "whatsapp": "start whatsapp:",
    "camera": "start microsoft.windows.camera:", "vs code": "code",
}


def open_app(name: str) -> str:
    """Computer par koi app kholta hai. name in mein se ho: notepad, calculator, paint, chrome, edge,
    file explorer, cmd, settings, task manager, control panel, word, excel, powerpoint, whatsapp, camera, vs code.
    List se bahar ki app ke liye uska Windows naam (misal 'spotify') dein."""
    cmd = APPS.get(name.lower().strip(), f'start "" "{name}"')
    subprocess.Popen(cmd, shell=True)
    return f"{name} khol di"


def close_app(process_name: str) -> str:
    """Chalti hui app band karta hai. process_name misal: 'notepad.exe', 'chrome.exe', 'WINWORD.EXE'."""
    if not process_name.lower().endswith(".exe"):
        process_name += ".exe"
    r = subprocess.run(f"taskkill /im {process_name} /f", shell=True, capture_output=True, text=True)
    return "band kar di" if r.returncode == 0 else f"band nahi hui: {r.stderr.strip()}"


def open_website(url: str) -> str:
    """Aam browser mein website ya link kholta hai (sirf dekhne ke liye). Website par kaam karna ho to browser_task use karein."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"{url} khol di"


def google_search(query: str) -> str:
    """Google par search kholta hai."""
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(query))
    return "search khol di"


def youtube_search(query: str) -> str:
    """YouTube par video/gana dhoondta hai."""
    webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
    return "YouTube khol diya"


def type_text(text: str) -> str:
    """Jo window abhi khuli hai usme text type karta hai (jaise Notepad mein likhna)."""
    import pyautogui
    import pyperclip
    pyperclip.copy(text)          # Urdu text bhi sahi type ho
    pyautogui.hotkey("ctrl", "v")
    return "likh diya"


def press_keys(keys: str) -> str:
    """Keyboard shortcut dabata hai. Misal: 'enter', 'ctrl+s', 'ctrl+c', 'alt+f4', 'win+d', 'ctrl+w', 'ctrl+t'."""
    import pyautogui
    parts = [k.strip().lower() for k in keys.split("+")]
    pyautogui.hotkey(*parts) if len(parts) > 1 else pyautogui.press(parts[0])
    return f"{keys} daba diya"


def media_control(action: str) -> str:
    """Awaaz aur gaane control. action: 'volume_up', 'volume_down', 'mute', 'play_pause', 'next', 'previous'."""
    import pyautogui
    key = {"volume_up": "volumeup", "volume_down": "volumedown", "mute": "volumemute",
           "play_pause": "playpause", "next": "nexttrack", "previous": "prevtrack"}[action]
    pyautogui.press(key, presses=5 if "volume" in action else 1)
    return "ho gaya"


def take_screenshot() -> str:
    """Screen ki tasveer Pictures\\Screenshots mein save karta hai."""
    import pyautogui
    folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, datetime.datetime.now().strftime("assistant_%Y%m%d_%H%M%S.png"))
    pyautogui.screenshot(path)
    return f"save ho gaya: {path}"


def current_datetime() -> str:
    """Abhi ka waqt aur tareekh."""
    return datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")


def power(action: str) -> str:
    """Computer ki power. action: 'lock', 'sleep', 'shutdown', 'restart', 'cancel_shutdown'.
    Shutdown/restart/sleep se pehle user se khud tasdeeq li jaati hai."""
    if action == "lock":
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "lock kar diya"
    if action == "cancel_shutdown":
        subprocess.Popen("shutdown /a", shell=True)
        return "shutdown cancel"
    cmds = {"shutdown": "shutdown /s /t 30", "restart": "shutdown /r /t 30",
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"}
    if action not in cmds:
        return "ghalat action"
    if not ask_yes_no(f"Kya computer {action} kar doon?"):
        return "user ne mana kar diya"
    subprocess.Popen(cmds[action], shell=True)
    return f"{action} 30 second mein (rokna ho to 'cancel_shutdown')"


TOOLS = [open_app, close_app, open_website, google_search, youtube_search, type_text,
         press_keys, media_control, take_screenshot, current_datetime, power]
