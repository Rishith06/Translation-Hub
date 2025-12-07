import streamlit as st
from audio_recorder_streamlit import audio_recorder
import wave
import tempfile
import os
import json
import io
import numpy as np
import sys
from deep_translator import GoogleTranslator
from gtts import gTTS
import subprocess
from pathlib import Path
import streamlit.components.v1 as components

# Hide Streamlit UI (from new.py)
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
.block-container {padding: 0; margin: 0;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Galaxy Gradient and Stars Background (from Text_to_text.py) ---
st.markdown('''
<style>
.stApp {
    background: linear-gradient(180deg, #0b0c2a, #1a1c40, #1e2b6f);
    color: white !important;
    font-family: 'Segoe UI', sans-serif;
}
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
    z-index: 0;
}
.block-container {
    margin-left: 60px;
}
@keyframes animStar {
    from { transform: translateY(0px); }
    to { transform: translateY(600px); }
}
</style>
''', unsafe_allow_html=True)

# --- Runtime package ensure (for transliteration) ---
def _ensure_package(module_name: str, pip_name: str) -> None:
    try:
        __import__(module_name)
    except Exception:
        try:
            subprocess.check_call([Path(sys.executable).as_posix(), "-m", "pip", "install", pip_name])
        except Exception:
            pass

def ensure_transliteration_runtime():
    _ensure_package("indic_transliteration", "indic-transliteration")
    _ensure_package("langdetect", "langdetect")

# --- Transliteration helpers ---
def detect_source_lang_code(text: str) -> str | None:
    try:
        from langdetect import detect  # type: ignore
        return detect(text) if text and text.strip() else None
    except Exception:
        return None

def transliterate_to_input_script(text: str, target_lang_code: str, source_lang_code: str | None) -> str | None:
    if not text:
        return None
    try:
        from indic_transliteration import sanscript  # type: ignore
        from indic_transliteration.sanscript import transliterate  # type: ignore
    except Exception:
        return None

    code_to_script = {
        "hi": sanscript.DEVANAGARI,
        "mr": sanscript.DEVANAGARI,
        "te": sanscript.TELUGU,
        "ta": sanscript.TAMIL,
        "kn": sanscript.KANNADA,
        "gu": sanscript.GUJARATI,
        # add more if needed
    }

    # Always convert to English romanized (ITRANS) irrespective of input
    src_script = code_to_script.get(target_lang_code)
    if src_script:
        try:
            transliterated_text = transliterate(str(text), src_script, sanscript.ITRANS)
            # Clean up special characters and ensure lowercase
            import re
            # Remove Indic script special characters
            transliterated_text = re.sub(r'[्ंः]', '', transliterated_text)
            # Remove other special characters except spaces
            transliterated_text = re.sub(r'[^\w\s]', '', transliterated_text)
            # Convert to lowercase and clean up spacing
            transliterated_text = transliterated_text.lower().strip()
            # Remove extra spaces
            transliterated_text = re.sub(r'\s+', ' ', transliterated_text)
            return transliterated_text
        except Exception:
            return None
    return None

def english_to_devanagari(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    import re
    words = re.split(r"(\s+)", text)
    cons = {"b": "ब", "c": "क", "d": "ड", "f": "फ", "g": "ग", "h": "ह",
            "j": "ज", "k": "क", "l": "ल", "m": "म", "n": "न", "p": "प",
            "q": "क", "r": "र", "s": "स", "t": "ट", "v": "व", "w": "व",
            "x": "क्स", "y": "य", "z": "ज"}
    dig = {"sh": "श", "ch": "च", "th": "थ", "ph": "फ", "bh": "भ",
           "gh": "घ", "kh": "ख", "qu": "क्व"}
    mat = {"a": "", "e": "े", "i": "ि", "o": "ो", "u": "ु"}
    vow = {"a": "अ", "e": "ए", "i": "इ", "o": "ओ", "u": "उ"}
    
    def tr_word(w: str) -> str:
        if not w or re.fullmatch(r"\W+", w):
            return w
        lw = w.lower()
        if lw == "i":
            return "आई"
        i = 0
        out = []
        last_cons = False
        while i < len(lw):
            if lw[i:i+3] == "ing":
                out.append("िंग")
                i += 3
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                if last_cons:
                    out.append("ू" if lw[i] == "o" else "ी")
                else:
                    out.append("ऊ" if lw[i] == "o" else "ई")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] == "ea":
                out.append("ी" if last_cons else "ई")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in dig:
                out.append(dig[lw[i:i+2]])
                i += 2
                last_cons = True
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
        if last_cons:
            out.append("्")
        return "".join(out)
    
    return "".join(tr_word(w) for w in words)

def english_to_telugu(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    import re
    words = re.split(r"(\s+)", text)
    cons = {"b": "బ", "c": "క", "d": "డ", "f": "ఫ", "g": "గ", "h": "హ",
            "j": "జ", "k": "క", "l": "ల", "m": "మ", "n": "న", "p": "ప",
            "q": "క", "r": "ర", "s": "స", "t": "ట", "v": "వ", "w": "వ",
            "x": "క్స", "y": "య", "z": "జ"}
    dig = {"sh": "శ", "ch": "చ", "th": "థ", "ph": "ఫ", "bh": "భ",
           "gh": "ఘ", "kh": "ఖ", "qu": "క్వ"}
    # Use correct gunintalu (ఓత్తులు)
    mat = {"a": "", "e": "ె", "i": "ి", "o": "ొ", "u": "ు"}
    mat_long = {"ee": "ీ", "oo": "ూ"}
    diph_matra = {"ai": "ై", "au": "ౌ"}
    vow = {"a": "అ", "e": "ఎ", "i": "ఇ", "o": "ఒ", "u": "ఉ"}
    vow_long = {"ee": "ఈ", "oo": "ఊ"}
    diph_vowel = {"ai": "ఐ", "au": "ఔ"}
    
    def tr_word(w: str) -> str:
        if not w or re.fullmatch(r"\W+", w):
            return w
        lw = w.lower()
        if lw == "i":
            return "ఐ"
        i = 0
        out = []
        last_cons = False
        while i < len(lw):
            if lw[i:i+3] == "ing":
                out.append("ింగ్")
                i += 3
                last_cons = False
                continue
            # long vowels and diphthongs
            if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                if last_cons:
                    out.append(mat_long[lw[i:i+2]])
                else:
                    out.append(vow_long[lw[i:i+2]])
                i += 2
                last_cons = False
                continue
            # AA matra / vowel (గుణింతాలు: ఆ → ా)
            if i + 1 < len(lw) and lw[i:i+2] == "aa":
                if last_cons:
                    out.append("ా")
                else:
                    out.append("ఆ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in ("ai", "au"):
                if last_cons:
                    out.append(diph_matra[lw[i:i+2]])
                else:
                    out.append(diph_vowel[lw[i:i+2]])
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] == "ea":
                out.append("ీ" if last_cons else "ఈ")
                i += 2
                last_cons = False
                continue
            # RI matra / vowel (ఋ → ృ)
            if i + 1 < len(lw) and lw[i:i+2] == "ri":
                if last_cons:
                    out.append("ృ")
                else:
                    out.append("ఋ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in dig:
                if last_cons:
                    out.append("్")
                out.append(dig[lw[i:i+2]])
                i += 2
                last_cons = True
                continue
            # handle consonant + r + vowel as rakar (్ర)
            if lw[i] == "r" and last_cons:
                # look ahead for a vowel or long/diphthong
                if i + 2 <= len(lw) and lw[i+1:i+3] in mat_long:
                    out.append("్ర" + mat_long[lw[i+1:i+3]])
                    i += 3
                    last_cons = False
                    continue
                if i + 2 <= len(lw) and lw[i+1:i+3] in diph_matra:
                    out.append("్ర" + diph_matra[lw[i+1:i+3]])
                    i += 3
                    last_cons = False
                    continue
                if i + 1 < len(lw) and lw[i+1] in mat:
                    out.append("్ర" + mat[lw[i+1]])
                    i += 2
                    last_cons = False
                    continue
                # no following vowel, treat as standalone 'ర్'
                out.append("ర్")
                i += 1
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
        # terminal virama for ending consonant (e.g., 'read' -> 'రీడ్')
        if last_cons:
            out.append("్")
        return "".join(out)
    
    return "".join(tr_word(w) for w in words)

def english_to_tamil(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    import re
    words = re.split(r"(\s+)", text)
    cons = {"b": "ப", "c": "க", "d": "ட", "f": "ஃப", "g": "க", "h": "ஹ",
            "j": "ஜ", "k": "க", "l": "ல", "m": "ம", "n": "ந", "p": "ப",
            "q": "க", "r": "ர", "s": "ச", "t": "ட", "v": "வ", "w": "வ",
            "x": "க்ஸ்", "y": "ய", "z": "ஜ"}
    dig = {"sh": "ஷ", "ch": "ச்", "th": "த்", "ph": "ஃப", "bh": "ப்",
           "gh": "க்", "kh": "க்", "qu": "க்வ"}
    mat = {"a": "", "e": "ே", "i": "ி", "o": "ோ", "u": "ு"}
    vow = {"a": "அ", "e": "எ", "i": "இ", "o": "ஒ", "u": "உ"}
    
    def tr_word(w: str) -> str:
        if not w or re.fullmatch(r"\W+", w):
            return w
        lw = w.lower()
        if lw == "i":
            return "ஐ"
        i = 0
        out = []
        last_cons = False
        while i < len(lw):
            if lw[i:i+3] == "ing":
                out.append("ிங்")
                i += 3
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                if last_cons:
                    out.append("ூ" if lw[i] == "o" else "ீ")
                else:
                    out.append("ஊ" if lw[i] == "o" else "ஈ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] == "ea":
                out.append("ீ" if last_cons else "ஈ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in dig:
                out.append(dig[lw[i:i+2]])
                i += 2
                last_cons = True
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
    text = text.strip()
    if not text:
        return text
    import re
    words = re.split(r"(\s+)", text)
    cons = {"b": "ಬ", "c": "ಕ", "d": "ಡ", "f": "ಫ", "g": "ಗ", "h": "ಹ",
            "j": "ಜ", "k": "ಕ", "l": "ಲ", "m": "ಮ", "n": "ನ", "p": "ಪ",
            "q": "ಕ", "r": "ರ", "s": "ಸ", "t": "ಟ", "v": "ವ", "w": "ವ",
            "x": "ಕ್ಸ", "y": "ಯ", "z": "ಜ"}
    dig = {"sh": "ಶ", "ch": "ಚ", "th": "ಥ", "ph": "ಫ", "bh": "ಭ",
           "gh": "ಘ", "kh": "ಖ", "qu": "ಕ್ವ"}
    mat = {"a": "", "e": "ೇ", "i": "ಿ", "o": "ೋ", "u": "ು"}
    vow = {"a": "ಅ", "e": "ಎ", "i": "ಇ", "o": "ಒ", "u": "ಉ"}
    
    def tr_word(w: str) -> str:
        if not w or re.fullmatch(r"\W+", w):
            return w
        lw = w.lower()
        if lw == "i":
            return "ಐ"
        i = 0
        out = []
        last_cons = False
        while i < len(lw):
            if lw[i:i+3] == "ing":
                out.append("ಿಂಗ್")
                i += 3
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in ("oo", "ee"):
                if last_cons:
                    out.append("ೂ" if lw[i] == "o" else "ೀ")
                else:
                    out.append("ಊ" if lw[i] == "o" else "ಈ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] == "ea":
                out.append("ೀ" if last_cons else "ಈ")
                i += 2
                last_cons = False
                continue
            if i + 1 < len(lw) and lw[i:i+2] in dig:
                out.append(dig[lw[i:i+2]])
                i += 2
                last_cons = True
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

# --- Global Configuration and Setup ---
st.set_page_config(layout="wide", page_title="Final Speech Translation App")

st.title("Final Speech Translation App - Full Audio Format Support")

# Check for audioop availability for better WAV processing
try:
    import audioop
    AUDIOOP_AVAILABLE = True
    st.success("✅ Full audio processing available for WAV files.")
except ImportError:
    AUDIOOP_AVAILABLE = False
    st.warning("⚠ audioop not available. Using alternative audio processing for WAV files.")

# Check if Vosk model exists
MODEL_PATH = "translator_app/vosk-model-en-in-0.5"
if not os.path.exists(MODEL_PATH):
    st.error(f"❌ Vosk model not found at: {MODEL_PATH}")
    st.info("Please make sure the model folder vosk-model-en-in-0.5 exists in your project directory.")
    st.stop()

# Initialize Vosk model only when needed and cache it
@st.cache_resource
def load_vosk_model():
    """Load the Vosk speech recognition model."""
    try:
        from vosk import Model
        return Model(MODEL_PATH)
    except Exception as e:
        st.error(f"Error loading Vosk model: {e}")
        return None

# --- Ensure ffmpeg is in PATH automatically ---
ffmpeg_dir = Path(__file__).parent / 'ffmpeg'
ffmpeg_exe = ffmpeg_dir / 'ffmpeg.exe'
if ffmpeg_exe.exists():
    os.environ['PATH'] = str(ffmpeg_dir) + os.pathsep + os.environ.get('PATH', '')

# --- Helper Functions for Audio Processing ---

def find_ffmpeg():
    """Find ffmpeg executable in various common locations."""
    # Check if ffmpeg is in PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return 'ffmpeg' 
    except FileNotFoundError:
        pass
    
    # Check local ffmpeg directory (e.g., 'ffmpeg/bin/ffmpeg.exe' or 'ffmpeg/ffmpeg')
    local_ffmpeg_dir = Path("ffmpeg/bin")
    if local_ffmpeg_dir.exists():
        ffmpeg_exe = local_ffmpeg_dir / "ffmpeg.exe" if os.name == 'nt' else local_ffmpeg_dir / "ffmpeg"
        if ffmpeg_exe.exists():
            return str(ffmpeg_exe.absolute())
    
    # Check if ffmpeg is in the current directory
    current_ffmpeg = Path("ffmpeg.exe") if os.name == 'nt' else Path("ffmpeg")
    if current_ffmpeg.exists():
        return str(current_ffmpeg.absolute())
    
    return None

def check_ffmpeg_availability():
    """Check if ffmpeg is available and executable."""
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        try:
            result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False
    return False

def convert_wav_to_mono_16bit_basic(wav_bytes_or_path):
    """
    Basic WAV conversion using wave module and audioop or numpy.
    This is used as a fallback or for direct WAV processing.
    """
    try:
        # Open WAV file from bytes or path
        if isinstance(wav_bytes_or_path, bytes):
            wav_io = io.BytesIO(wav_bytes_or_path)
            wf = wave.open(wav_io, 'rb')
        else:
            wf = wave.open(wav_bytes_or_path, 'rb')
        
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        audio_data = wf.readframes(nframes)
        wf.close()

        # Check if audio is already in the target format
        if channels == 1 and sampwidth == 2 and framerate == 16000:
            st.info("Audio is already in the desired format (mono, 16-bit, 16kHz).")
            if isinstance(wav_bytes_or_path, bytes):
                # If input was bytes, save to a temp file to return a path
                temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_wav.write(wav_bytes_or_path)
                temp_wav.close()
                return temp_wav.name
            else:
                return wav_bytes_or_path # Already a path, no conversion needed

        # Perform conversions
        if AUDIOOP_AVAILABLE:
            if channels == 2:
                st.info("🔄 Converting stereo to mono with audioop...")
                audio_data = audioop.tomono(audio_data, sampwidth, 1, 1)
                channels = 1
            if sampwidth != 2:
                st.info("🔄 Converting to 16-bit with audioop...")
                audio_data = audioop.lin2lin(audio_data, sampwidth, 2)
                sampwidth = 2
            if framerate != 16000:
                st.info("🔄 Resampling to 16kHz with audioop.ratecv...")
                # Use audioop.ratecv to resample to 16kHz
                audio_data, _ = audioop.ratecv(audio_data, sampwidth, channels, framerate, 16000, None)
                framerate = 16000
        else:
            # Fallback for audio processing using numpy
            if channels == 2:
                st.info("🔄 Converting stereo to mono using numpy...")
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_array = audio_array.reshape(-1, 2)
                audio_array = np.mean(audio_array, axis=1, dtype=np.int16)
                audio_data = audio_array.tobytes()
                channels = 1
            
            if sampwidth != 2:
                st.info("🔄 Converting sample width to 16-bit using numpy...")
                if sampwidth == 1:  # 8-bit to 16-bit
                    audio_array = np.frombuffer(audio_data, dtype=np.uint8)
                    audio_array = (audio_array.astype(np.int16) - 128) * 256
                    audio_data = audio_array.tobytes()
                elif sampwidth == 4:  # 32-bit to 16-bit
                    audio_array = np.frombuffer(audio_data, dtype=np.int32)
                    audio_array = (audio_array >> 16).astype(np.int16)
                    audio_data = audio_array.tobytes()
                sampwidth = 2
            
            if framerate != 16000:
                st.info("🔄 Resampling to 16kHz using numpy (this can be slow)...")
                # This is a basic resampling, for high quality, librosa is better
                from scipy.signal import resample
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                num_samples = int(len(audio_array) * (16000 / framerate))
                audio_array = resample(audio_array, num_samples).astype(np.int16)
                audio_data = audio_array.tobytes()
                framerate = 16000

        # Write converted audio to a new temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(temp_wav, 'wb') as wf_out:
            wf_out.setnchannels(channels)
            wf_out.setsampwidth(sampwidth)
            wf_out.setframerate(framerate)
            wf_out.writeframes(audio_data)
        temp_wav.close() # Close the file handle immediately
        return temp_wav.name
        
    except Exception as e:
        st.error(f"Error in basic WAV conversion: {e}")
        return None

def convert_audio_to_mono_16bit_wav(audio_file_path, original_format=None):
    """
    Convert any audio format to mono 16-bit WAV using pydub (preferred) or librosa (fallback).
    """
    try:
        from pydub import AudioSegment
        
        ffmpeg_path = find_ffmpeg()
        if not ffmpeg_path:
            st.warning("⚠ ffmpeg not found. Using alternative conversion methods (may have limited format support)...")
            return convert_audio_without_ffmpeg(audio_file_path, original_format)
        
        # Set ffmpeg path for pydub if it's not in system PATH
        if ffmpeg_path != 'ffmpeg':
            os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
            
        # Load audio file with pydub
        try:
            if original_format:
                audio = AudioSegment.from_file(audio_file_path, format=original_format)
            else:
                audio = AudioSegment.from_file(audio_file_path)
        except Exception:
            st.warning(f"pydub failed to load file with format {original_format}. Retrying without specifying format.")
            audio = AudioSegment.from_file(audio_file_path)
        
        # Convert to target format (mono, 16-bit, 16kHz)
        if audio.channels > 1:
            st.info("🔄 Converting stereo to mono...")
            audio = audio.set_channels(1)
        
        if audio.sample_width != 2:
            st.info("🔄 Converting to 16-bit sample width...")
            audio = audio.set_sample_width(2)
        
        if audio.frame_rate != 16000:
            st.info("🔄 Resampling to 16kHz for optimal transcription...")
            audio = audio.set_frame_rate(16000)
        
        output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        audio.export(output_path, format="wav")
        
        st.success("✅ Audio converted successfully with pydub!")
        return output_path
            
    except ImportError:
        st.warning("⚠ pydub not available. Using basic conversion methods...")
        return convert_audio_without_ffmpeg(audio_file_path, original_format)
    except Exception as e:
        st.warning(f"⚠ pydub conversion failed: {e}. Using alternative method...")
        return convert_audio_without_ffmpeg(audio_file_path, original_format)

def convert_audio_without_ffmpeg(audio_file_path, original_format=None):
    """
    Fallback function to convert audio using librosa and soundfile
    if pydub/ffmpeg are not available.
    """
    try:
        # If it's a WAV file, try basic WAV conversion first
        if original_format and original_format.lower() == 'wav':
            return convert_wav_to_mono_16bit_basic(audio_file_path)
        
        # For other formats, try using librosa as fallback
        try:
            import librosa
            import soundfile as sf
            st.info("🔄 Using librosa for audio conversion...")
            
            # Load audio with librosa (automatically converts to mono and resamples)
            audio, sr = librosa.load(audio_file_path, sr=16000, mono=True)
            
            # Convert to 16-bit integer format
            audio = (audio * 32767).astype(np.int16)
            
            # Save as WAV using soundfile
            output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            sf.write(output_path, audio, 16000, subtype='PCM_16')
            
            st.success("✅ Audio converted successfully with librosa!")
            return output_path
            
        except ImportError:
            st.warning("⚠ librosa or soundfile not available. Cannot convert non-WAV files without ffmpeg.")
            st.error("Please install pydub and ffmpeg for full audio format support. For WAV files, basic conversion is attempted.")
            return None
        except Exception as e:
            st.warning(f"⚠ librosa conversion failed: {e}. Cannot convert this file.")
            return None
            
    except Exception as e:
        st.error(f"Error in alternative conversion: {e}")
        return None

def transcribe(wav_file_path, model):
    """Transcribe a WAV file using the Vosk model."""
    try:
        from vosk import KaldiRecognizer
        wf = wave.open(wav_file_path, "rb")
        
        # Vosk expects mono, 16-bit, 16kHz audio. Warn if not.
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            st.warning(f"Vosk expects mono, 16-bit, 16kHz audio. Current: Channels={wf.getnchannels()}, Sample Width={wf.getsampwidth()}, Frame Rate={wf.getframerate()}. Transcription quality may be affected.")
        
        rec = KaldiRecognizer(model, wf.getframerate())
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                results.append(res.get("text", ""))
        final_res = json.loads(rec.FinalResult())
        results.append(final_res.get("text", ""))
        return " ".join(results)
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return ""

def translate_and_speak(transcription, lang_name, lang_code, source_lang_code):
    """Translates text, adds transliteration, and generates speech for the translation."""
    try:
        with st.spinner(f"Translating to {lang_name}..."):
            translated = GoogleTranslator(source='auto', target=lang_code).translate(transcription)

        with st.expander(f"🔊 {lang_name}"):
            st.markdown(f"**{lang_name} Translation:**")
            st.write(translated)

            # Transliteration block - always show English romanized
            translit = transliterate_to_input_script(translated, lang_code, source_lang_code)
            if translit:
                st.markdown(f"**Transliteration (English romanized):**")
                st.write(translit)

            with st.spinner(f"Generating speech for {lang_name}..."):
                tts = gTTS(text=translated, lang=lang_code, slow=False)
                tts_fp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tts.save(tts_fp.name)
                tts_fp.close() # Ensure the file is closed before Streamlit tries to read it
                st.audio(tts_fp.name, format="audio/mp3")
                os.unlink(tts_fp.name) # Clean up TTS temp file immediately
                
    except Exception as e:
        st.error(f"Error translating/speaking {lang_name}: {e}")
        
# --- Main App Interface ---

# Record Audio Section
st.write("### 🎙️ Record Audio")
st.markdown("Click the microphone to record your message.")
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e8656a",  # Color while recording
    neutral_color="#a23b3b",    # Color when not recording
    icon_size="2x",
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Processing recorded audio..."):
        # Recorded audio is already WAV, so use the basic WAV converter
        wav_path = convert_wav_to_mono_16bit_basic(audio_bytes)
        
        if wav_path:
            model = load_vosk_model()
            if model is None:
                st.stop()
            
            st.write("### 📝 Transcription:")
            transcription = transcribe(wav_path, model)
            st.info(transcription)

            if transcription.strip() != "":
                st.write("### 🌐 Translations & Transliteration:")
                languages = {
                    "Hindi": "hi",
                    "Tamil": "ta",
                    "Gujarati": "gu",
                    "Marathi": "mr",
                    "Kannada": "kn",
                    "Telugu": "te"
                }
                
                # ensure transliteration deps
                ensure_transliteration_runtime()
                src_code = detect_source_lang_code(transcription)
                
                for lang_name, lang_code in languages.items():
                    translate_and_speak(transcription, lang_name, lang_code, src_code)
            else:
                st.warning("No speech detected in the recording.")

            try:
                os.unlink(wav_path) # Clean up recorded WAV temp file
            except Exception:
                pass

# Enhanced File Upload Section
st.write("---")
st.write("### 📂 Upload Audio File")
st.write("**Supported Formats:** MP3, M4A, FLAC, WAV, OGG, AAC, WMA")
st.write("**Auto-conversion:** All files are converted to mono 16-bit WAV for optimal speech recognition")

ffmpeg_available = check_ffmpeg_availability()
if ffmpeg_available:
    st.success(f"✅ ffmpeg is available. Full audio format support is enabled.")
else:
    st.warning("⚠ ffmpeg not found. Limited audio format support (WAV files recommended).")
    st.info("💡 To enable full format support, please install ffmpeg and ensure it's in your system's PATH, or place ffmpeg.exe (Windows) / ffmpeg (Linux/macOS) in an ffmpeg/bin folder in your project directory.")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac', 'wma'],
    help="Upload any audio file - it will be automatically converted for optimal speech recognition"
)

if uploaded_file is not None:
    st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name
    
    with st.spinner("Processing uploaded file..."):
        converted_path = convert_audio_to_mono_16bit_wav(temp_file_path, file_extension)
        
        if converted_path:
            model = load_vosk_model()
            if model is None:
                st.stop()
            
            st.write("### 📝 Transcription:")
            transcription = transcribe(converted_path, model)
            st.info(transcription)
            
            if transcription.strip() != "":
                st.write("### 🌐 Translations & Transliteration:")
                languages = {
                    "Hindi": "hi",
                    "Tamil": "ta",
                    "Gujarati": "gu",
                    "Marathi": "mr",
                    "Kannada": "kn",
                    "Telugu": "te"
                }
                
                # ensure transliteration deps
                ensure_transliteration_runtime()
                src_code = detect_source_lang_code(transcription)
                
                for lang_name, lang_code in languages.items():
                    translate_and_speak(transcription, lang_name, lang_code, src_code)
            else:
                st.warning("No transcription generated. Please try with a clearer audio file.")
                
            try:
                os.unlink(temp_file_path) # Clean up original uploaded temp file
                if converted_path != temp_file_path: # Only unlink if a new file was created
                    os.unlink(converted_path) # Clean up converted WAV temp file
            except Exception:
                pass
        else:
            st.error("Failed to convert audio file. Please try a different file.")

# Footer Section with Instructions
st.write("---")
st.markdown("""
### 📋 Supported Audio Formats:
- **WAV** (.wav) - Uncompressed format (always supported)
- **MP3** (.mp3) - Most common compressed format
- **M4A** (.m4a) - Apple's audio format
- **FLAC** (.flac) - Lossless compressed format
- **OGG** (.ogg) - Open source format
- **AAC** (.aac) - Advanced audio coding
- **WMA** (.wma) - Windows media audio

### 🎯 Audio Processing Features:
- **Automatic format conversion** to WAV
- **Stereo to mono conversion** for better speech recognition
- **16-bit audio processing** for optimal quality
- **16kHz sample rate** for speech recognition
- **Multiple conversion methods** for compatibility

### 📝 Instructions:
1. **Record Audio**: Click the microphone button to record your speech.
2. **Upload File**: Or upload any supported audio file.
3. **Get Results**: The app will transcribe and translate your speech.
4. **Listen**: Click the audio players to hear the translations.
""")

st.write("---")