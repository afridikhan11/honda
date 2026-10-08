"""
AI Voice Assistant — free (Google Gemini free tier).

F9 dabayein -> bolein -> assistant khud kaam karega:
  "notepad khol kar likho aaj ki meeting 5 baje"
  "chrome mein facebook khol kar meri page par yeh post karo: ..."
  "youtube par naat chalao", "awaaz kam karo", "computer band kar do"
Post, payment, ad ya message bhejne se pehle hamesha aap se "haan" lega.
"""

import asyncio
import os
import sys
import threading
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

from google import genai                      # noqa: E402  (.env pehle load hona zaroori)
from google.genai import types                # noqa: E402

import pc_tools                               # noqa: E402
from voice import ask_yes_no, listen, speak   # noqa: E402

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BROWSER_MODEL = os.getenv("BROWSER_MODEL", MODEL)
HOTKEY = os.getenv("HOTKEY", "f9")
CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CHROME_PROFILE = HERE / "chrome-profile"       # assistant ka alag Chrome — yahan ek dafa FB/TikTok login karein

SYSTEM = """Tum user ke computer ka AI assistant ho. User Pakistani hai aur Urdu / Roman Urdu / English mein bolta hai.
- Jawab hamesha chhota (1-2 jumle) aur Roman Urdu mein do, kyunke jawab bol kar sunaya jata hai.
- Computer ke kaam ke liye diye gaye tools use karo. Ek kaam ke liye kayi tools baari baari chala sakte ho.
- Kisi website PAR kaam (login wali sites, Facebook/Instagram/TikTok post, form bharna, ads, messages, kuch dhoondna
  aur parhna) ke liye browser_task tool use karo, aur usko poori tafseel se kaam likh kar do (post ka poora text, page ka naam waghera).
- Awaaz se suna gaya text kabhi ghalat bhi hota hai. Agar baat wazeh na ho to pehle user se poochho.
- Kabhi andaza laga kar paisa kharch, post ya message mat karo."""

BROWSER_RULES = """
ZAROORI QAWAID:
- Koi bhi aakhri qadam — Post/Publish/Share, message Send, ad campaign Submit/Publish, payment, kuch Delete karna,
  account settings badalna — us button ko dabane se PEHLE ask_user_permission action se user se poochho
  (kya ho raha hai aur kitne paise lagenge, sab batao). "Nahi" mile to ruk jao aur done karo.
- Password ya OTP maange to ask_user_permission se user ko kaho ke khud browser mein daal de, phir aage chalo.
- Captcha aaye to user se hal karwao."""


# ---------- Browser (Chrome) — apne event loop par background mein ----------

_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True).start()
_browser = None


async def _run_browser_task(task):
    global _browser
    from browser_use import Agent, Browser, ChatGoogle, Tools, ActionResult

    if _browser is None:
        _browser = Browser(
            executable_path=CHROME_PATH if Path(CHROME_PATH).exists() else None,
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            keep_alive=True,
        )

    tools = Tools()

    @tools.action("User se ijazat/madad maango (post, payment, ad, message, delete se pehle, ya password/OTP/captcha ke liye).")
    def ask_user_permission(question: str) -> ActionResult:
        ok = ask_yes_no(question)
        return ActionResult(extracted_content="User ne HAAN kaha, aage chalo." if ok
                            else "User ne NAHI kaha. Yeh qadam mat uthao, kaam rok kar done karo.")

    agent = Agent(
        task=task + "\n" + BROWSER_RULES,
        llm=ChatGoogle(model=BROWSER_MODEL, api_key=API_KEY),
        browser=_browser,
        tools=tools,
    )
    history = await agent.run(max_steps=40)
    return history.final_result() or ("kaam mukammal" if history.is_done() else "kaam poora nahi hua")


def browser_task(task: str) -> str:
    """Chrome browser khud chala kar website par kaam karta hai — jaise Facebook/Instagram/TikTok par post,
    Facebook/TikTok ads banana, Gmail, WhatsApp Web, online form bharna, kisi site se maloomat nikalna.
    task: poora kaam tafseel se (kaun si site, kya karna hai, post ka poora text, budget waghera)."""
    speak("Theek hai, browser mein kar raha hoon.")
    try:
        return asyncio.run_coroutine_threadsafe(_run_browser_task(task), _loop).result(timeout=900)
    except Exception as e:
        return f"browser mein masla: {e}"


# ---------- Dimagh (Gemini) ----------

def make_chat():
    client = genai.Client(api_key=API_KEY)
    return client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            tools=pc_tools.TOOLS + [browser_task],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=15),
        ),
    )


def handle(chat, text):
    try:
        reply = chat.send_message(text).text
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            reply = "Aaj ki free had khatam ho gayi ya bohat tez requests hain. Thori der baad try karein."
        else:
            reply = "Maazrat, koi masla aa gaya."
            print("!!", msg)
    speak(reply or "Ho gaya.")


def main():
    if not API_KEY:
        print("GEMINI_API_KEY nahi mili. README dekhein: .env file mein key daalein.")
        sys.exit(1)
    import keyboard

    chat = make_chat()
    speak(f"Assistant tayyar hai. {HOTKEY.upper()} daba kar bolein.")
    print(f"\n[{HOTKEY.upper()}] = bolein   |   [Ctrl+C] = band   |   ya yahan likh kar Enter bhi kar sakte hain\n")

    pressed = threading.Event()
    keyboard.add_hotkey(HOTKEY, pressed.set)

    typed = []
    def read_console():
        while True:
            line = sys.stdin.readline()
            if line.strip():
                typed.append(line.strip())
                pressed.set()
    threading.Thread(target=read_console, daemon=True).start()

    while True:
        pressed.wait()
        pressed.clear()
        text = typed.pop(0) if typed else listen()
        if not text:
            speak("Samajh nahi aaya, dobara bolein.")
            continue
        if text.strip().lower() in ("exit", "band", "khuda hafiz", "خدا حافظ"):
            speak("Khuda Hafiz.")
            break
        handle(chat, text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKhuda Hafiz.")
