import customtkinter as ctk
import json
import asyncio
import os
import edge_tts
import requests
from googletrans import Translator, LANGUAGES
import logging

# Setup logging configuration
logging.basicConfig(
    filename='text2speech.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# UI Theme setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Load language codes with error handling
try:
    with open("languages.json", "r", encoding="utf-8") as file:
        LANGUAGES = json.load(file)
except FileNotFoundError as e:
    logging.error("languages.json file not found!")
    LANGUAGES = {"English (US)": "en-US"}  # fallback default
except json.JSONDecodeError as e:
    logging.error("languages.json corrupted or invalid!")
    LANGUAGES = {"English (US)": "en-US"}  # fallback default

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title="Message", message="", box_type="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)
        self.grab_set()  # Modal behavior

        # Colors based on message type
        colors = {
            "info": "#2979FF",
            "error": "#FF5252",
            "success": "#4CAF50",
            "warning": "#FFA000"
        }
        self.color = colors.get(box_type, "#2979FF")

        # Configure window bg to dark mode default
        self.configure(fg_color="#121212")

        # Message Label
        self.label = ctk.CTkLabel(self, text=message, wraplength=300, font=ctk.CTkFont(size=14))
        self.label.pack(pady=(30, 20), padx=20)

        # Ok Button
        self.ok_button = ctk.CTkButton(self, text="OK", fg_color=self.color, command=self.destroy)
        self.ok_button.pack(pady=(0, 20), ipadx=10)

        # Center window on parent
        self.center_window(parent)

    def center_window(self, parent):
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        win_w = self.winfo_width()
        win_h = self.winfo_height()

        pos_x = parent_x + (parent_w - win_w) // 2
        pos_y = parent_y + (parent_h - win_h) // 2
        self.geometry(f"+{pos_x}+{pos_y}")

class Text2SpeechApp(ctk.CTk):
    """
    CustomTkinter GUI app for translating English text to a selected language
    and converting the translated text to speech using Edge TTS.

    Attributes:
        LANGUAGES (dict): Dictionary mapping language names to codes.
    """

    def __init__(self):
        super().__init__()

        
        self.title("Text2Speech - EdgeTTS")
        self.geometry("500x600")
        self.minsize(300, 550)
        self.configure(padx=30, pady=30)
        
        self.create_widgets()
        
        

    def chk_internet(self)->bool:
        try:
            r = requests.get('https://www.google.com')
            return True
        except:
            CustomMessageBox(self, "Error", "No Internet Connection", "Error")
            return False

    def create_widgets(self):
        self.header_label = ctk.CTkLabel(
            self,
            text="Text2Speech",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#00aaff"
        )
        self.header_label.pack(pady=(0, 30))

        self.lang_label = ctk.CTkLabel(
            self,
            text="Select Language:",
            font=ctk.CTkFont(size=16)
        )
        self.lang_label.pack(anchor="w", pady=(0, 8))

        self.language_var = ctk.StringVar()
        self.language_combobox = ctk.CTkComboBox(
            self,
            values=[f"{k} ({v})" for k, v in LANGUAGES.items()],
            variable=self.language_var,
            height=38,
            dropdown_hover_color="#007ACC",
            corner_radius=8
        )
        self.language_combobox.set(
            list(LANGUAGES.keys())[0] + f" ({list(LANGUAGES.values())[0]})"
        )
        self.language_combobox.pack(fill="x", pady=(0, 30))

        self.textbox = ctk.CTkTextbox(
            self,
            height=15 * 10,
            font=ctk.CTkFont(size=16),
            corner_radius=12
        )
        self.textbox.pack(fill="both", expand=True)
        self.textbox.insert("0.0", "Enter your text here...")
        self.textbox.bind("<FocusIn>", self.clear_placeholder)
        self.textbox.bind("<FocusOut>", self.add_placeholder)

        self.submit_button = ctk.CTkButton(
            self,
            text="Translate & Speak",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#00aaff",
            hover_color="#0077cc",
            command=self.on_submit
        )
        self.submit_button.pack(pady=(20, 20), fill="x")

    def clear_placeholder(self, event):
        """
        Clear placeholder text on focus in the textbox.
        """
        current_text = self.textbox.get("0.0", "end").strip()
        if current_text == "Enter your text here...":
            self.textbox.delete("0.0", "end")

    def add_placeholder(self, event):
        """
        Add placeholder text if textbox is empty on focus out.
        """
        current_text = self.textbox.get("0.0", "end").strip()
        if not current_text:
            self.textbox.insert("0.0", "Enter your text here...")

    def on_submit(self):
        """
        Triggered on button click: reads inputs and runs translation + TTS.
        Handles empty input gracefully.
        """
        if not self.chk_internet():
            return
        selected = self.language_var.get()
        lang_code = selected.split('(')[-1].strip(')') if "(" in selected else ""
        text = self.textbox.get("0.0", "end").strip()
        if text == "Enter your text here..." or not text:
            logging.warning("Empty input text. User pressed submit without input.")
            return
        try:
            asyncio.run(self.process(text, lang_code))
        except Exception as e:
            logging.error(f"Error in on_submit process: {e}")

    async def process(self, text: str, lang_code: str):
        """
        Translate the text and convert to speech asynchronously.

        Args:
            text (str): Input text in English.
            lang_code (str): Language code for translation and voice.

        """
        try:
            translated_text = await self.translate(text, lang_code)
            if not translated_text:
                logging.warning("Translation returned empty text.")
                return
            voice = await self.get_voice_by_lang_code(lang_code)
            if not voice:
                logging.warning(f"No voice found for locale '{lang_code}'. Using default 'en-US-JennyNeural'.")
                voice = "en-US-JennyNeural"  # fallback voice
            communicate = edge_tts.Communicate(text=translated_text, voice=voice)
            await communicate.save("audio.mp3")
            os.system("start audio.mp3")  # Windows only
            CustomMessageBox(self, "Success", "TTS Success", "Success")
            logging.info(f"Successfully played audio for language '{lang_code}'.")
        except Exception as e:
            logging.error(f"Error during process: {e}")

    async def translate(self, text: str, lang_code: str) -> str:
        """
        Use Google Translate to translate English text to desired language.

        Args:
            text (str): English text.
            lang_code (str): Target language code.

        Returns:
            str: Translated text.

        """
        translator = Translator()
        # Trim off the region part if present (en-US -> en)
        short_code = lang_code.split('-')[0] if '-' in lang_code else lang_code
        try:
            # run blocking translate in separate thread to avoid blocking event loop
            result = await translator.translate(text=text, src='en', dest=short_code)
            return result.text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return ""

    async def get_voice_by_lang_code(self, lang_code: str) -> str:
        """
        Get the first matching Edge TTS voice by language locale code.

        Args:
            lang_code (str): Language locale code (e.g., 'en-US').

        Returns:
            str: Edge TTS voice short name or None if not found.
        """
        try:
            voices = await edge_tts.list_voices()
            for voice in voices:
                if voice["Locale"].lower() == lang_code.lower():
                    return voice["ShortName"]
            return None
        except Exception as e:
            logging.error(f"Error fetching voices: {e}")
            return None


if __name__ == "__main__":
    try:
        app = Text2SpeechApp()
        app.mainloop()
    except Exception as main_e:
        logging.critical(f"Fatal error in main loop: {main_e}")
