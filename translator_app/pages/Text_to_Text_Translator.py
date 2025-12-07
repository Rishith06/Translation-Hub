import streamlit as st
import os
import sys
import io
import time
import json
import importlib
from datetime import datetime


st.set_page_config(page_title="Text Translator", layout="wide")

# Custom CSS to hide Streamlit elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;} 
footer {visibility: hidden;}  
.block-container {
    padding-top: 0;
    padding-bottom: 0;
}
header {visibility: hidden;}  /* Hide header */
div[data-testid="stDecoration"] {visibility: hidden;} /* Hide Streamlit deployment button */
body {
    background-color: #1E3A8A; /* Blue background */
    color: white; /* White text */
}
.scrollable {
    height: 500px;
    overflow-y: scroll;
}
</style>
"""

# Custom CSS
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ===========================
# Galaxy Theme
# ===========================
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(180deg, #0b0c2a, #1a1c40, #1e2b6f);
    color: white !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1, h2, h3 {
    color: #fff !important;
    text-shadow: 0px 0px 8px rgba(255,255,255,0.3);
}

/* Input box */
.stTextArea textarea {
    background: rgba(255,255,255,0.1);
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 10px;
}

/* Button */
.stButton button {
    background: linear-gradient(135deg, #3a6ff7, #9b51e0);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    border: none;
    padding: 0.6em 1.2em;
    box-shadow: 0px 0px 12px rgba(155,81,224,0.8);
    transition: 0.3s;
}
.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 18px rgba(155,81,224,1);
}

/* Table */
.dataframe {
    background: rgba(255,255,255,0.15);
    color: white !important;
    border-radius: 20px;
    backdrop-filter: blur(20px);
    border: 3px solid rgba(255,255,255,0.2);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    overflow: hidden;
    margin: 20px 0;
}
.dataframe th, .dataframe td {
    color: white !important;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    text-align: left;
    font-size: 15px;
    line-height: 1.5;
    font-weight: 500;
}
.dataframe th {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 13px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    padding: 25px 20px;
    border-bottom: 3px solid rgba(255,255,255,0.2);
}
.dataframe tr:nth-child(even) {
    background: rgba(255,255,255,0.08);
}
.dataframe tr:nth-child(odd) {
    background: rgba(255,255,255,0.03);
}
.dataframe tr:hover {
    background: rgba(255,255,255,0.15);
    transform: scale(1.01);
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.dataframe td:first-child {
    font-weight: bold;
    color: #4CAF50 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

/* Audio sections */
.audio-section {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}

/* Speaker button */
.speaker-btn {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    border: none;
    border-radius: 50%;
    width: 35px;
    height: 35px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(76,175,80,0.3);
}
.speaker-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(76,175,80,0.5);
}

/* Audio player styling */
.stAudio {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px;
    margin: 5px 0;
}

/* Output text styling */
.output-text {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.output-text strong {
    color: #4CAF50;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.translation-result {
    background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(69,160,73,0.1));
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 2px solid rgba(76,175,80,0.3);
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.audio-section {
    background: linear-gradient(135deg, rgba(155,81,224,0.1), rgba(58,111,247,0.1));
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 2px solid rgba(155,81,224,0.3);
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.input-section {
    background: linear-gradient(135deg, rgba(255,193,7,0.1), rgba(255,152,0,0.1));
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 2px solid rgba(255,193,7,0.3);
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* Stars */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 2px;
    height: 2px;
    background: white;
    box-shadow: 
        50px 100px white, 120px 230px white, 250px 400px white,
        500px 50px white, 700px 300px white, 900px 200px white,
        1100px 400px white, 1300px 150px white, 1500px 500px white,
        1700px 350px white, 1900px 250px white;
    animation: animStar 20s linear infinite;
}
@keyframes animStar {
    from { transform: translateY(0px); }
    to { transform: translateY(600px); }
}
</style>
""", unsafe_allow_html=True)



os.makedirs("utils", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

os.makedirs("generated", exist_ok=True)
os.makedirs(os.path.join("generated", "outputs"), exist_ok=True)

os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

try:
    from pathlib import Path
    CURRENT_FILE = Path(__file__).resolve()
    PROJECT_ROOT = CURRENT_FILE.parents[2]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
except Exception:
    pass

def _pip_install(package_name: str) -> None:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def _try_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


import streamlit as st 


# Utilities that may require packages; import lazily after ensuring
def ensure_runtime_packages():
    from translator_app.utils.package_utils import ensure_packages
    ensure_packages([
        {"module": "numpy", "pip": "numpy"},
        {"module": "scipy", "pip": "scipy"},
        {"module": "soundfile", "pip": "soundfile"},
        {"module": "librosa", "pip": "librosa"},
        {"module": "matplotlib", "pip": "matplotlib"},
        {"module": "pydub", "pip": "pydub"},
        {"module": "mutagen", "pip": "mutagen"},
        {"module": "ffmpeg", "pip": "ffmpeg-python"},
        {"module": "pyttsx3", "pip": "pyttsx3"},
        {"module": "gtts", "pip": "gTTS"},
        {"module": "langdetect", "pip": "langdetect"},
        {"module": "deep_translator", "pip": "deep-translator"},
        {"module": "argostranslate", "pip": "argostranslate"},
        {"module": "TTS", "pip": "TTS"},
        {"module": "whisper", "pip": "openai-whisper"},
        {"module": "indic_transliteration", "pip": "indic-transliteration"},
        {"module": "tabulate", "pip": "tabulate"},

    ])


@st.cache_resource(show_spinner=False)
def setup_runtime_packages_once() -> bool:
    """Ensure runtime packages exactly once per process to prevent reload loops."""
    try:
        ensure_runtime_packages()
    except Exception:
        pass
    return True


def safe_import_utils():
    from translator_app.utils.package_utils import write_requirements_file, get_installed_versions
    from translator_app.utils.audio_utils import plot_waveform, ensure_wav_sample_rate
    from translator_app.utils.tts_utils import TTSManager
    from translator_app.utils.transcription_utils import transcribe_with_whisper
    from translator_app.utils.translation_utils import translate_with_fallback_strict, translate_to_all_targets
    return {
        "write_requirements_file": write_requirements_file,
        "get_installed_versions": get_installed_versions,
        "plot_waveform": plot_waveform,
        "ensure_wav_sample_rate": ensure_wav_sample_rate,
        "TTSManager": TTSManager,
        "transcribe_with_whisper": transcribe_with_whisper,
        "translate_with_fallback_strict": translate_with_fallback_strict,
        "translate_to_all_targets": translate_to_all_targets,
    }


def translate_all_deep(text: str, source_lang_code: str | None, targets: list[str]):
    """Use deep_translator GoogleTranslator for all targets. Returns (translations, errors)."""
    translations = {}
    errors = {}
    try:
        from deep_translator import GoogleTranslator  
    except Exception as e:
        for t in targets:
            translations[t] = None
            errors[t] = f"deep_translator unavailable: {e}"
        return translations, errors

    for t in targets:
        try:
            translator = GoogleTranslator(source=source_lang_code or 'auto', target=t)
            translations[t] = translator.translate(text)
            errors[t] = None
        except Exception as e:
            translations[t] = None
            errors[t] = str(e)
        if t == 'te' and (translations.get(t) is None or str(translations.get(t)).strip() == ''):
            try:
                translator_te = GoogleTranslator(source='auto', target='te')
                translations[t] = translator_te.translate(text)
                errors[t] = None
            except Exception:
                translations[t] = "<Telugu translation unavailable>"
                if not errors.get(t):
                    errors[t] = "Fallback Telugu translation failed"
    return translations, errors


def synthesize_all_gtts(translations: dict[str, str | None]):
    """Synthesize MP3 via gTTS for each translation. Returns (paths, errors)."""
    paths = {}
    errors = {}
    try:
        from gtts import gTTS  
    except Exception as e:
        for lang in translations.keys():
            paths[lang] = None
            errors[lang] = f"gTTS unavailable: {e}"
        return paths, errors

    ts = int(time.time())
    base_dir = os.path.join("generated", "outputs")
    os.makedirs(base_dir, exist_ok=True)
    for lang, text in translations.items():
        if not text:
            paths[lang] = None
            errors[lang] = "No translation"
            continue
        try:
            out_path = os.path.join(base_dir, f"translated_{lang}_{ts}.mp3")
            tts = gTTS(text=text, lang=lang)
            tts.save(out_path)
            paths[lang] = out_path
            errors[lang] = None
        except Exception as e:
            paths[lang] = None
            errors[lang] = str(e)
    return paths, errors


# Transliteration helpers
def compute_transliterations(
    translations: dict[str, str | None],
    source_lang_code: str | None = None,
    source_text: str | None = None,
) -> dict[str, str]:
    """Return transliterations of the input text into each target language's script.
    For example: English input "hello" -> Hindi script "हेलो", Telugu script "హెలో", etc.
    """
    romanized: dict[str, str] = {}
    
    if not source_text:
        return romanized
    
    try:
        from indic_transliteration import sanscript 
        from indic_transliteration.sanscript import transliterate  
    except Exception:
        return romanized

    code_to_script = {
        "hi": sanscript.DEVANAGARI,
        "te": sanscript.TELUGU,
        "ta": sanscript.TAMIL,
        "kn": sanscript.KANNADA,
        "bn": sanscript.BENGALI,
    }

    def english_to_devanagari(text: str) -> str:
        """Convert English text to Devanagari script"""
        text = text.strip().lower()
        if not text:
            return text

        import re
        words = re.split(r"(\s+)", text)

        consonant_map = {
            "b": "ब", "c": "क", "d": "ड", "f": "फ", "g": "ग", "h": "ह",
            "j": "ज", "k": "क", "l": "ल", "m": "म", "n": "न", "p": "प",
            "q": "क", "r": "र", "s": "स", "t": "ट", "v": "व", "w": "व",
            "x": "क्स", "y": "य", "z": "ज",
        }
        vowel_matra = {"a": "", "e": "े", "i": "ि", "o": "ो", "u": "ु"}
        vowel_indep = {"a": "अ", "e": "ए", "i": "इ", "o": "ओ", "u": "उ"}

        def translit_word(w: str) -> str:
            if not w or re.fullmatch(r"\W+", w):
                return w
            lw = w.lower()
            i = 0
            out = []
            last_is_consonant = False
            while i < len(lw):
                if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                    if last_is_consonant:
                        out.append("ू" if lw[i] == "o" else "ी")
                    else:
                        out.append("ऊ" if lw[i] == "o" else "ई")
                    i += 2
                    last_is_consonant = False
                    continue
                ch = lw[i]
                if ch in consonant_map:
                    out.append(consonant_map[ch])
                    last_is_consonant = True
                    i += 1
                    continue
                if ch in vowel_matra:
                    if last_is_consonant:
                        out.append(vowel_matra[ch])
                        last_is_consonant = False
                    else:
                        out.append(vowel_indep[ch])
                        last_is_consonant = False
                    i += 1
                    continue
                out.append(w[i])
                last_is_consonant = False
                i += 1
            return "".join(out)

        return "".join(translit_word(w) for w in words)

    def english_to_telugu(text: str) -> str:
        """Convert English text to Telugu script"""
        text = text.strip().lower()
        if not text:
            return text
        import re
        words = re.split(r"(\s+)", text)
        cons = {
            "b": "బ", "c": "క", "d": "డ", "f": "ఫ", "g": "గ", "h": "హ",
            "j": "జ", "k": "క", "l": "ల", "m": "మ", "n": "న", "p": "ప",
            "q": "క", "r": "ర", "s": "స", "t": "ట", "v": "వ", "w": "వ",
            "x": "క్స", "y": "య", "z": "జ",
        }
        mat = {"a": "", "e": "ె", "i": "ి", "o": "ొ", "u": "ు"}
        vow = {"a": "అ", "e": "ఎ", "i": "ఇ", "o": "ఒ", "u": "ఉ"}

        def tr_word(w: str) -> str:
            if not w or re.fullmatch(r"\W+", w):
                return w
            lw = w.lower()
            i = 0
            out = []
            last_cons = False
            while i < len(lw):
                if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                    if last_cons:
                        out.append("ూ" if lw[i] == "o" else "ీ")
                    else:
                        out.append("ఊ" if lw[i] == "o" else "ఈ")
                    i += 2
                    last_cons = False
                    continue
                ch = lw[i]
                if ch in cons:
                    if last_cons:
                        out.append("్")
                    out.append(cons[ch])
                    last_cons = True
                    i += 1
                    continue
                if ch in mat:
                    out.append(mat[ch] if last_cons else vow[ch])
                    last_cons = False
                    i += 1
                    continue
                out.append(w[i])
                last_cons = False
                i += 1
            if last_cons:
                out.append("్")
            return "".join(out)

        return "".join(tr_word(w) for w in words)

    def english_to_tamil(text: str) -> str:
        """Convert English text to Tamil script"""
        text = text.strip().lower()
        if not text:
            return text
        import re
        words = re.split(r"(\s+)", text)
        cons = {
            "b": "ப", "c": "க", "d": "ட", "f": "ஃப", "g": "க", "h": "ஹ",
            "j": "ஜ", "k": "க", "l": "ல", "m": "ம", "n": "ந", "p": "ப",
            "q": "க", "r": "ர", "s": "ச", "t": "ட", "v": "வ", "w": "வ",
            "x": "க்ஸ்", "y": "ய", "z": "ஜ",
        }
        mat = {"a": "", "e": "ே", "i": "ி", "o": "ோ", "u": "ு"}
        vow = {"a": "அ", "e": "எ", "i": "இ", "o": "ஒ", "u": "உ"}

        def tr_word(w: str) -> str:
            if not w or re.fullmatch(r"\W+", w):
                return w
            lw = w.lower()
            i = 0
            out = []
            last_cons = False
            while i < len(lw):
                if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                    if last_cons:
                        out.append("ூ" if lw[i] == "o" else "ீ")
                    else:
                        out.append("ஊ" if lw[i] == "o" else "ஈ")
                    i += 2
                    last_cons = False
                    continue
                ch = lw[i]
                if ch in cons:
                    out.append(cons[ch])
                    last_cons = True
                    i += 1
                    continue
                if ch in mat:
                    out.append(mat[ch] if last_cons else vow[ch])
                    last_cons = False
                    i += 1
                    continue
                out.append(w[i])
                last_cons = False
                i += 1
            return "".join(out)

        return "".join(tr_word(w) for w in words)

    def english_to_kannada(text: str) -> str:
        """Convert English text to Kannada script"""
        text = text.strip().lower()
        if not text:
            return text
        import re
        words = re.split(r"(\s+)", text)
        cons = {
            "b": "ಬ", "c": "ಕ", "d": "ಡ", "f": "ಫ", "g": "ಗ", "h": "ಹ",
            "j": "ಜ", "k": "ಕ", "l": "ಲ", "m": "ಮ", "n": "ನ", "p": "ಪ",
            "q": "ಕ", "r": "ರ", "s": "ಸ", "t": "ಟ", "v": "ವ", "w": "ವ",
            "x": "ಕ್ಸ", "y": "ಯ", "z": "ಜ",
        }
        mat = {"a": "", "e": "ೇ", "i": "ಿ", "o": "ೋ", "u": "ು"}
        vow = {"a": "ಅ", "e": "ಎ", "i": "ಇ", "o": "ಒ", "u": "ಉ"}

        def tr_word(w: str) -> str:
            if not w or re.fullmatch(r"\W+", w):
                return w
            lw = w.lower()
            i = 0
            out = []
            last_cons = False
            while i < len(lw):
                if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                    if last_cons:
                        out.append("ೂ" if lw[i] == "o" else "ೀ")
                    else:
                        out.append("ಊ" if lw[i] == "o" else "ಈ")
                    i += 2
                    last_cons = False
                    continue
                ch = lw[i]
                if ch in cons:
                    out.append(cons[ch])
                    last_cons = True
                    i += 1
                    continue
                if ch in mat:
                    out.append(mat[ch] if last_cons else vow[ch])
                    last_cons = False
                    i += 1
                    continue
                out.append(w[i])
                last_cons = False
                i += 1
            return "".join(out)

        return "".join(tr_word(w) for w in words)

    # Generate transliterations for each target language
    for code, translation_text in translations.items():
        if not translation_text:
            romanized[code] = ""
            continue
            
        try:
            if source_lang_code == "en":
                # English input -> convert translations to English script (romanize)
                if code in code_to_script:
                    # For Indic languages, transliterate the translation back to Roman
                    result = transliterate(str(translation_text), code_to_script[code], sanscript.ITRANS)
                    if result:
                        import re
                        clean_result = re.sub(r'[^a-zA-Z0-9\s]', '', result).lower().strip()
                        romanized[code] = clean_result if clean_result else str(translation_text).lower()
                    else:
                        romanized[code] = str(translation_text).lower()
                elif code == "en":
                    romanized[code] = str(translation_text).lower()
                else:
                    romanized[code] = str(translation_text).lower()
                    
            elif source_lang_code in code_to_script:
                # Indic input -> convert translations to input language script
                if code == "en":
                    # English translation -> convert to input language script
                    if source_lang_code == "hi":
                        romanized[code] = english_to_devanagari(str(translation_text))
                    elif source_lang_code == "te":
                        romanized[code] = english_to_telugu(str(translation_text))
                    elif source_lang_code == "ta":
                        romanized[code] = english_to_tamil(str(translation_text))
                    elif source_lang_code == "kn":
                        romanized[code] = english_to_kannada(str(translation_text))
                    else:
                        romanized[code] = str(translation_text).lower()
                elif code in code_to_script:
                    # Other Indic translation -> convert to input language script
                    result = transliterate(str(translation_text), code_to_script[code], code_to_script[source_lang_code])
                    romanized[code] = result if result else str(translation_text)
                else:
                    romanized[code] = str(translation_text).lower()
            else:
                # Fallback for other languages
                romanized[code] = str(translation_text).lower()
                
        except Exception:
            romanized[code] = str(translation_text).lower() if translation_text else ""

    return romanized


# Try to import external hooks; keep None if missing
def import_external_hooks():
    external = {"transcribe_audio": None, "translate_text": None}
    try:
        from external_audio import transcribe_audio as _transcribe_audio  # type: ignore
        external["transcribe_audio"] = _transcribe_audio
    except Exception:
        pass
    try:
        from external_translate import translate_text as _translate_text  # type: ignore
        external["translate_text"] = _translate_text
    except Exception:
        pass
    return external


APP_TITLE = "Text-to-Text Translator"


LANG_OPTIONS = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Bengali": "bn",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh",
}


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    # st.caption("This app does not clone your voice. It always uses TTS with generic voices to synthesize translated text.")

    # Ensure packages at runtime
    with st.spinner("Preparing environment (first run may take a moment)..."):
        setup_ok = setup_runtime_packages_once()
        if not setup_ok:
            st.warning("Some optional packages could not be installed at runtime.")

    # Import utils after ensuring packages
    utils = safe_import_utils()
    write_requirements_file = utils["write_requirements_file"]
    get_installed_versions = utils["get_installed_versions"]
    plot_waveform = utils["plot_waveform"]
    ensure_wav_sample_rate = utils["ensure_wav_sample_rate"]
    TTSManager = utils["TTSManager"]
    transcribe_with_whisper = utils["transcribe_with_whisper"]
    translate_with_fallback_strict = utils["translate_with_fallback_strict"]
    translate_to_all_targets = utils["translate_to_all_targets"]

    external = import_external_hooks()

    # Auto-generate requirements.txt on first run
    try:
        if not os.path.exists("requirements.txt"):
            versions = get_installed_versions([
                "streamlit",
                "numpy",
                "scipy",
                "soundfile",
                "librosa",
                "matplotlib",
                "pydub",
                "mutagen",
                "ffmpeg-python",
                "pyttsx3",
                "gtts",
                "deep-translator",
                "argostranslate",
                "TTS",
                "whisper",
                "torch",
            ])
            write_requirements_file("requirements.txt", versions)
    except Exception:
        pass

    # Controls
    st.markdown("---")
    
    # Main section
    st.subheader("📝 Input")
    
    # Initialize session state for input text
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""
    
    input_text = st.text_area(
        "Enter text to translate and synthesize (language will be detected automatically):", 
        value=st.session_state.input_text,
        height=200,
        key="input_text_area"
    )
    
    # Update session state when input changes
    if input_text != st.session_state.input_text:
        st.session_state.input_text = input_text
        # Reset processing state when input changes
        st.session_state.should_process = False
    
    # Add clear button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Clear", key="clear_button"):
            st.session_state.input_text = ""
            st.rerun()
    
    # Initialize session state for processing
    if 'should_process' not in st.session_state:
        st.session_state.should_process = False
    
    # Process button logic
    if st.button("Process Text"):
        if input_text.strip():
            st.session_state.should_process = True
        else:
            st.error("Please enter some text.")
    
    # Process text if button was clicked or if we're in a session that should process
    if st.session_state.should_process and input_text.strip():
        # Parse input into lines and detect language automatically
        input_lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
        language_inputs = []
        
        for line in input_lines:
            if line.strip():
                # Detect language automatically with improved logic for individual characters and scripts
                try:
                    from langdetect import detect, DetectorFactory
                    import random
                    import re
                    
                    # Set seed for consistent detection
                    DetectorFactory.seed = 0
                    
                    # Script detection patterns for individual characters and words
                    script_patterns = {
                        'hi': r'[\u0900-\u097F]',  # Devanagari
                        'te': r'[\u0C00-\u0C7F]',  # Telugu
                        'ta': r'[\u0B80-\u0BFF]',  # Tamil
                        'kn': r'[\u0C80-\u0CFF]',  # Kannada
                        'bn': r'[\u0980-\u09FF]',  # Bengali
                        'gu': r'[\u0A80-\u0AFF]',  # Gujarati
                        'ml': r'[\u0D00-\u0D7F]',  # Malayalam
                        'pa': r'[\u0A00-\u0A7F]',  # Gurmukhi
                        'or': r'[\u0B00-\u0B7F]',  # Odia
                        'si': r'[\u0D80-\u0DFF]',  # Sinhala
                        'th': r'[\u0E00-\u0E7F]',  # Thai
                        'ar': r'[\u0600-\u06FF]',  # Arabic
                        'he': r'[\u0590-\u05FF]',  # Hebrew
                        'ko': r'[\uAC00-\uD7AF]',  # Korean
                        'ja': r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]',  # Japanese
                        'zh': r'[\u4E00-\u9FFF]',  # Chinese
                        'ru': r'[\u0400-\u04FF]',  # Cyrillic
                        'el': r'[\u0370-\u03FF]',  # Greek
                    }
                    
                    # Check for script-specific characters first
                    detected_script = None
                    for lang_code, pattern in script_patterns.items():
                        if re.search(pattern, line):
                            detected_script = lang_code
                            break
                    
                    if detected_script:
                        detected_lang_code = detected_script
                    else:
                        # Check for common English patterns
                        english_patterns = [
                            r'\b(I|you|he|she|it|we|they)\b',
                            r'\b(am|is|are|was|were|be|been|being)\b',
                            r'\b(learning|studying|working|reading|writing|speaking)\b',
                            r'\b(programming|coding|development|software|computer)\b',
                            r'\b(hello|hi|good|bad|nice|great|wonderful)\b'
                        ]
                        
                        line_lower = line.lower()
                        english_score = 0
                        for pattern in english_patterns:
                            if re.search(pattern, line_lower):
                                english_score += 1
                        
                        # If strong English indicators, classify as English
                        if english_score >= 2:
                            detected_lang_code = 'en'
                        else:
                            # Use langdetect for other cases
                            detected_lang_code = detect(line)
                    
                    # Map language code to name
                    lang_code_to_name = {
                        'en': 'English', 'hi': 'Hindi', 'te': 'Telugu', 'ta': 'Tamil', 
                        'kn': 'Kannada', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                        'it': 'Italian', 'pt': 'Portuguese', 'ar': 'Arabic', 'bn': 'Bengali',
                        'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese',
                        'gu': 'Gujarati', 'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia',
                        'th': 'Thai', 'he': 'Hebrew', 'el': 'Greek', 'si': 'Sinhala'
                    }
                    detected_lang_name = lang_code_to_name.get(detected_lang_code, f'Language ({detected_lang_code})')
                    language_inputs.append((detected_lang_name, line))
                except Exception:
                    # Fallback to English if detection fails
                    language_inputs.append(('English', line))
        
        if not language_inputs:
            st.error("Please enter some text to translate")
            return
        
        st.subheader("📥 Input Sentences")
        for lang_name, text_content in language_inputs:
            st.markdown(f'<div class="output-text"><strong>{lang_name}:</strong> {text_content}</div>', unsafe_allow_html=True)
        
        st.subheader("📤 Output")
        
        # Target languages
        TARGET_LANGS = ["en", "hi", "te", "ta", "kn"]
        LANG_NAMES = {"en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada"}
        LANG_CODES = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Kannada": "kn"}
        
        # Process all inputs and organize by target language
        all_results = {}
        
        # Initialize results structure for each target language
        for target_code in TARGET_LANGS:
            all_results[target_code] = []
        
        # Process each input and collect translations
        for input_idx, (input_lang_name, input_text_content) in enumerate(language_inputs):
            # Detect source language code
            detected_source = None
            try:
                from langdetect import detect
                detected_source = detect(input_text_content)
            except Exception:
                detected_source = LANG_CODES.get(input_lang_name)
            
            if not detected_source:
                detected_source = LANG_CODES.get(input_lang_name, "auto")
            
            # Process each target language
            for target_code in TARGET_LANGS:
                target_name = LANG_NAMES[target_code]
                
                # Skip if same as input language
                if target_code == detected_source:
                    translation = input_text_content
                else:
                    # Translate
                    try:
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source=detected_source or 'auto', target=target_code)
                        translation = translator.translate(input_text_content)
                        
                        # Telugu-specific fix
                        if target_code == 'te' and (not translation or str(translation).strip() == ''):
                            translator_te = GoogleTranslator(source='auto', target='te')
                            translation = translator_te.translate(input_text_content)
                            
                    except Exception as e:
                        translation = f"Translation failed: {str(e)}"
                
                # Generate transliteration
                try:
                    temp_translations = {target_code: translation}
                    temp_romanized = compute_transliterations(
                        temp_translations,
                        source_lang_code=detected_source,
                        source_text=input_text_content,
                    )
                    transliteration = temp_romanized.get(target_code, "")
                except Exception:
                    transliteration = translation  # Fallback
                
                # Store result
                all_results[target_code].append({
                    'input_lang': input_lang_name,
                    'input_text': input_text_content,
                    'translation': translation,
                    'transliteration': transliteration,
                    'input_idx': input_idx
                })
        
        # Display results organized by target language
        for target_code in TARGET_LANGS:
            target_name = LANG_NAMES[target_code]
            results = all_results[target_code]
            
            st.markdown(f"### {target_name} Translation")
            
            for idx, result in enumerate(results):
                input_lang = result['input_lang']
                translation = result['translation']
                transliteration = result['transliteration']
                
                # Display translation
                st.markdown(f"**{input_lang} → {translation}**")
                if transliteration and transliteration != translation:
                    st.markdown(f"({transliteration})")
                
                # Generate and display audio
                try:
                    from gtts import gTTS
                    import time
                    ts = int(time.time())
                    base_dir = os.path.join("generated", "outputs")
                    os.makedirs(base_dir, exist_ok=True)
                    
                    if translation and translation.strip() and target_code != LANG_CODES.get(input_lang):
                        out_path = os.path.join(base_dir, f"translated_{target_code}_{idx}_{ts}.mp3")
                        tts = gTTS(text=translation, lang=target_code)
                        tts.save(out_path)
                        
                        st.markdown(f"🔊 Audio {idx + 1} ({target_name})")
                        st.audio(out_path)
                        

                except Exception as e:
                    st.error(f"Audio generation failed: {str(e)}")
                
                st.markdown("")
            
            st.markdown("---")
        
        # Show summary table only for single language input
        if len(language_inputs) == 1:
            st.subheader("📊 Summary Table")
            import pandas as pd
            
            # Create summary table for single input
            summary_rows = []
            input_lang_name, input_text_content = language_inputs[0]
            detected_source = LANG_CODES.get(input_lang_name, "auto")
            
            for target_code in TARGET_LANGS:
                target_name = LANG_NAMES[target_code]
                
                # Get translation and transliteration for this combination
                temp_translations = {target_code: ""}
                temp_romanized = {}
                
                try:
                    if target_code == detected_source:
                        translation = input_text_content
                    else:
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source=detected_source or 'auto', target=target_code)
                        translation = translator.translate(input_text_content)
                        
                        if target_code == 'te' and (not translation or str(translation).strip() == ''):
                            translator_te = GoogleTranslator(source='auto', target='te')
                            translation = translator_te.translate(input_text_content)
                    
                    temp_translations[target_code] = translation
                    temp_romanized = compute_transliterations(
                        temp_translations,
                        source_lang_code=detected_source,
                        source_text=input_text_content,
                    )
                    transliteration = temp_romanized.get(target_code, "")
                except Exception:
                    translation = "Translation failed"
                    transliteration = ""
                
                summary_rows.append({
                    "Input Language": input_lang_name,
                    "Input Text": input_text_content,
                    "Target Language": target_name,
                    "Translation": translation,
                    "Transliteration": transliteration
                })
            
            df = pd.DataFrame(summary_rows)
            st.dataframe(df, use_container_width=True)




if __name__ == "__main__":
    main()