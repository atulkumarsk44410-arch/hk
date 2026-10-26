# MarketAI Studio — हिंदी MVP

## फीचर्स
- AI Meta ad copy, creative concepts, landing-page copy और campaign planning
- SQLite आधारित लीड मैनेजर और status updates
- हिंदी/अंग्रेज़ी कंटेंट
- Responsive dashboard

## लोकल कंप्यूटर पर चलाएँ (Windows)
1. Python 3.10+ इंस्टॉल करें।
2. इस फोल्डर में Command Prompt/PowerShell खोलें।
3. वर्चुअल एनवायरनमेंट बनाएँ:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. `.env.example` की कॉपी बनाकर उसका नाम `.env` रखें।
5. `.env` में अपनी OpenAI API key डालें। API key को HTML/JavaScript में कभी न डालें।
6. चलाएँ:
   ```powershell
   python app.py
   ```
7. ब्राउज़र में `http://127.0.0.1:5000` खोलें।

## API खर्च
OpenAI API का बिल ChatGPT सदस्यता से अलग हो सकता है। API billing/usage limits पहले सेट करें।

## डिप्लॉयमेंट
किसी Python web host पर GitHub repository से deploy करें:
- Build/install command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables: `OPENAI_API_KEY`, `OPENAI_MODEL`
- Persistent disk/storage जोड़ें और `DATABASE_PATH` को उसी persistent location पर सेट करें, नहीं तो redeploy पर SQLite डेटा खो सकता है।
- HTTPS, authentication, rate limiting और backups जोड़ने के बाद ही वास्तविक ग्राहक डेटा रखें।

## अभी क्या production-ready नहीं है?
- Login, roles और account-level isolation नहीं
- Google Sheets sync नहीं
- Live Meta Ads account connection या ad publishing नहीं
- Image/video file generation नहीं; creative tab ideas और prompts देता है
- SQLite MVP है; multi-user production के लिए PostgreSQL बेहतर है

## Meta API को बाद में जोड़ना
Meta Developer App बनाएँ, Marketing API access/permissions और OAuth flow कॉन्फ़िगर करें। Tokens server-side सुरक्षित रखें। App review/Business verification जैसी शर्तें लागू हो सकती हैं। पहले read-only campaign insights जोड़ें, फिर draft creation, और केवल स्पष्ट user approval के बाद publishing. API access उपलब्ध होने तक यह dashboard लाइव Meta data होने का दावा नहीं करता।
