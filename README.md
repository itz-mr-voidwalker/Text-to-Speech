## 🗣️ Text2Speech - EdgeTTS GUI App
A beautiful, dark-themed CustomTkinter GUI application that translates English text to your chosen language and converts it into realistic AI speech using Microsoft EdgeTTS.
Built with love, async power, and sarcastic logging!

## 🚀 Features
- 🌍 Translate text using Google Translate
- 🗣️ Speak text in selected language using Microsoft Edge TTS
- 🎧 Playback generated audio with one click
- 📁 Save logs with status messages (errors, warnings, info)
- 📦 Language selection from JSON config (languages.json)
- 🎛️ Custom-designed GUI using CustomTkinter
- 📲 Works offline for GUI, but translation & TTS need internet

## 📦 Requirements
Install dependencies using pip:
```
pip install -r requirements.txt
```

## 🧠 How It Works
User enters English text.

Chooses a target language from the dropdown.

App translates it using Google Translate API.

Finds a compatible Edge TTS voice for the language.

Converts translated text to .mp3 using Edge TTS.

Plays audio using system default player.


## 📁 File Structure
```
text2speech/
├── main.py              # App main script
├── languages.json       # Language names to locale code mapping
├── text2speech.log      # Runtime logs (generated)
├── audio.mp3            # Output audio (generated)
└── README.md            # You’re reading it now 😉

```

## ⚠️ Error Handling
- 📴 No Internet? ➜ Shows custom error message box.

- 🗣️ Language has no voice? ➜ Uses default en-US-JennyNeural.

- ❌ Translate failed? ➜ Gracefully logs the error and skips.


## 📌 Notes
- Only languages supported by Edge TTS will produce speech.

- Works only on Windows (uses os.system("start audio.mp3"))

- Needs valid languages.json in the root directory.

- Logging info saved in text2speech.log.

## 👑 Author
Made by 𝓜я. ᴠᴇɴɢᴇᴀɴᴄᴇ aka Sai Vignesh
