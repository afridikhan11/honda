# AI Voice Assistant (free)

Bol kar computer se kaam karwayein. Ye assistant aap ki baat samajh kar khud apps kholta hai, Chrome chalata hai,
Facebook aur TikTok par post karta hai, aur ads banane mein madad karta hai.
Isay chalane ka kharcha **0** hai. Sirf ads ka budget aap ka apna lagta hai.

| Hissa | Kya use hota hai | Kharcha |
|---|---|---|
| Awaaz sunna | Google speech (internet) | Free |
| Dimagh | Google Gemini (free tier) | Free, magar roz ki had hai |
| Chrome chalana | browser-use (open source) | Free |
| Jawab bolna | Microsoft Edge ki Urdu awaaz | Free |

8GB RAM wale PC par chal jata hai, kyunke bhaari kaam Google ke servers par hota hai. Internet zaroori hai.

## Setup (sirf pehli dafa)

1. **Python install karein:** https://www.python.org/downloads/ se Python 3.12 ya 3.13 lein.
   Install karte waqt **"Add python.exe to PATH"** par tick lagayein.
2. **Free Gemini key lein:** https://aistudio.google.com/apikey kholein, Google account se login karein, aur **Create API key** dabayein. Key copy kar lein.
3. Is folder mein **`SETUP.bat`** par double-click karein. Install hone ke baad `.env` file Notepad mein khulegi.
   Usme `GEMINI_API_KEY=` ke aage apni key paste kar ke save karein.
4. **`LOGIN-CHROME.bat`** chalayein. Ye assistant ka apna alag Chrome kholega. Isme ek dafa Facebook, TikTok Ads
   aur jo bhi site chahiye, login kar lein. Phir ye Chrome **band kar dein**.

## Roz ka istemal

**`START.bat`** chalayein. Phir **F9** dabayein aur bolein, ya us kaali window mein likh kar Enter karein.

Misalein:
- "notepad khol kar likho kal subah 10 baje meeting hai"
- "youtube par Junaid Jamshed ki naat chalao"
- "awaaz kam karo", "screenshot lo", "computer lock karo"
- "Facebook par Honda Islamabad page par post karo: CD70 2026 model aa gaya hai, aaj hi tashreef layein"
- "TikTok Ads mein naya campaign banao, roz ka budget 1000 rupay, Islamabad ke log, 18 se 35 saal"
- "Gmail kholo aur dekho aaj kis ki email aayi hai"

Band karne ke liye "khuda hafiz" likhein ya bolein, ya window band kar dein.

## Hifazat
- **Post, message, ad publish, payment ya delete** se pehle assistant poochega: "Kya kar doon?" Aap "haan" bolenge tabhi aage barhega.
- Shutdown aur restart 30 second baad hote hain. "shutdown cancel karo" bol kar rok sakte hain.
- Password aur OTP assistant khud nahi daalta. Ye aap Chrome mein khud daalein.
- Facebook aur TikTok par bohat zyada automatic kaam karne se account par pabandi lag sakti hai, is liye isay aam insaan ki
  raftaar se istemal karein.

## Masle aur hal
- **"free had khatam ho gayi":** Gemini ki free tier mein har minute aur har din ki had hai, aur browser wale kaam
  zyada requests lete hain. Thori der ruk jayein, ya `.env` mein `GEMINI_MODEL=gemini-2.5-flash-lite` kar dein.
- **Awaaz samajh nahi aati:** `.env` mein `LISTEN_LANGUAGE=en-IN` kar ke dekhein, jo Roman Urdu aur English mix ke liye behtar hai.
- **Chrome nahi khulta ya profile error aata hai:** `LOGIN-CHROME.bat` wala Chrome band karein. Ek waqt mein assistant ka
  Chrome sirf ek jagah khul sakta hai.
- **Note:** Google ki free tier mein aap ki commands Google apni AI behtar karne ke liye istemal kar sakta hai.
  Is liye passwords ya zaati maloomat bol kar na dein.

## Files
```
agent.py       dimagh: Gemini + tools, F9 loop
pc_tools.py    computer ke kaam (apps, keyboard, volume, power...)
voice.py       sunna / bolna
SETUP.bat      ek dafa install
START.bat      roz chalayein
LOGIN-CHROME.bat  assistant ke Chrome mein login
```
