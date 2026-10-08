@echo off
rem Assistant wale Chrome mein ek dafa Facebook / TikTok / Gmail login kar lein.
cd /d %~dp0
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%~dp0chrome-profile" https://facebook.com https://ads.tiktok.com
