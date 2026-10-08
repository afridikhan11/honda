"""Mic ke baghair commands ki pehchaan check karein:  python test_parse.py"""
from assistant import parse

CASES = {
    "notepad kholo": ("open_app", "notepad"),
    "Chrome open karo": ("open_app", "chrome"),
    "open calculator": ("open_app", "calculator"),
    "notepad band karo": ("close_app", "notepad"),
    "youtube kholo": ("open_site", "youtube"),
    "whatsapp web open karo": ("open_site", "whatsapp web"),
    "honda kholo": ("open_site", "honda"),
    "daraz.pk kholo": ("open_url", "daraz.pk"),
    "google par honda cd70 price search karo": ("search", "honda cd70 price"),
    "weather islamabad search karo": ("search", "weather islamabad"),
    "youtube par naat chalao": ("youtube", "naat"),
    "play cricket highlights on youtube": ("youtube", "cricket highlights"),
    "awaaz barhao": ("volume_up", None),
    "volume kam karo": ("volume_down", None),
    "mute karo": ("mute", None),
    "screenshot lo": ("screenshot", None),
    "time kya hai": ("time", None),
    "aaj date kya hai": ("date", None),
    "likho assalam o alaikum": ("type", "assalam o alaikum"),
    "enter dabao": ("key", "enter"),
    "save karo": ("hotkey", "ctrl+s"),
    "tab band karo": ("hotkey", "ctrl+w"),
    "desktop dikhao": ("hotkey", "win+d"),
    "computer band karo": ("shutdown", None),
    "band karna cancel": ("cancel_shutdown", None),
    "laptop restart karo": ("restart", None),
    "lock karo": ("lock", None),
    "assistant band karo": ("exit", None),
    "kuch bhi random baat": ("unknown", "kuch bhi random baat"),
}

fails = 0
for said, want in CASES.items():
    got = parse(said)
    if got != want:
        fails += 1
        print(f"FAIL  {said!r}: {got} (chahiye {want})")
print(f"{len(CASES) - fails}/{len(CASES)} pass")
raise SystemExit(1 if fails else 0)
