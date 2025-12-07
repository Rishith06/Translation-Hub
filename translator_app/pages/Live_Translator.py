import streamlit as st
import pyaudio
import queue
import vosk
import sys
import json
from deep_translator import GoogleTranslator
import time
import streamlit.components.v1 as components
from gtts import gTTS
import os
import tempfile
from playsound import playsound
import threading

# BACKGROUND + THEME
st.set_page_config(page_title="Text Translator", layout="wide")

# Custom CSS
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}  /* Hide hamburger menu */
footer {visibility: hidden;}  /* Hide footer */
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
# Galaxy Theme CSS
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
    padding: 0.8em 1.5em;
    box-shadow: 0px 0px 12px rgba(58,111,247,0.8);
    transition: 0.3s;
    min-height: 50px;
}
.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 18px rgba(58,111,247,1);
}

/* Disabled button style (for Pause and Stop) */
.stButton button:disabled {
    background: linear-gradient(135deg, #6c757d, #495057) !important;
    color: rgba(255,255,255,0.7) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Small button style for Hindi, Telugu, and Clear buttons */
.small-button {
    background: linear-gradient(135deg, #3a6ff7, #9b51e0) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.4em 0.8em !important;
    box-shadow: 0px 0px 8px rgba(58,111,247,0.6) !important;
    transition: 0.3s !important;
    min-height: 35px !important;
    font-size: 14px !important;
}
.small-button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0px 0px 12px rgba(58,111,247,0.8) !important;
}

/* Target specific buttons by their data-testid */
[data-testid="stButton"] button[key="play_hindi_final"],
[data-testid="stButton"] button[key="play_telugu_final"],
[data-testid="stButton"] button[key="clear_results"] {
    background: linear-gradient(135deg, #3a6ff7, #9b51e0) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.4em 0.8em !important;
    box-shadow: 0px 0px 8px rgba(58,111,247,0.6) !important;
    transition: 0.3s !important;
    min-height: 35px !important;
    font-size: 14px !important;
    width: auto !important;
    max-width: 200px !important;
}
[data-testid="stButton"] button[key="play_hindi_final"]:hover,
[data-testid="stButton"] button[key="play_telugu_final"]:hover,
[data-testid="stButton"] button[key="clear_results"]:hover {
    transform: scale(1.02) !important;
    box-shadow: 0px 0px 12px rgba(58,111,247,0.8) !important;
}

/* Alternative CSS targeting for button styling */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #3a6ff7, #9b51e0) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.6em 1.0em !important;
    box-shadow: 0px 0px 8px rgba(58,111,247,0.6) !important;
    transition: 0.3s !important;
    min-height: 40px !important;
    font-size: 14px !important;
}
div[data-testid="stButton"] button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0px 0px 12px rgba(58,111,247,0.8) !important;
}

/* Status indicators */
.status-listening {
    background: rgba(76,175,80,0.2);
    border-left: 4px solid #4CAF50;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.status-paused {
    background: rgba(255,193,7,0.2);
    border-left: 4px solid #FFC107;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

/* Language specific styling */
.hindi-box {
    background: rgba(76,175,80,0.2);
    border-left: 4px solid #4CAF50;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.telugu-box {
    background: rgba(33,150,243,0.2);
    border-left: 4px solid #2196F3;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

/* TTS Buttons */
.stButton button[kind="secondary"] {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
    color: white;
    border: none;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
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

# Initialize Google Translators
hindi_translator = GoogleTranslator(source='en', target='hi')
telugu_translator = GoogleTranslator(source='en', target='te')

# --- Robust Vosk Model Path Checking ---
def find_vosk_model():
    # Try common locations
    possible_paths = [
        "vosk-model-en-in-0.5",
        "translator_app/vosk-model-en-in-0.5",
        os.path.join(os.getcwd(), "vosk-model-en-in-0.5"),
        os.path.join(os.getcwd(), "translator_app", "vosk-model-en-in-0.5"),
    ]
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            contents = os.listdir(path)
            if contents:
                print(f"[INFO] Found Vosk model at: {path}")
                print(f"[INFO] Model directory contents: {contents}")
                return path
            else:
                print(f"[ERROR] Model directory is empty: {path}")
    print("[ERROR] Could not find a valid Vosk model directory. Please download and extract a model from https://alphacephei.com/vosk/models and place it in the project root or translator_app/ directory.")
    return None

MODEL_PATH = find_vosk_model()
if not MODEL_PATH:
    st.error("❌ Vosk model not found. Please download and extract a model from https://alphacephei.com/vosk/models and place it in the project root or translator_app/ directory.")
    st.stop()

try:
    vosk_model = vosk.Model(MODEL_PATH)
except Exception as e:
    st.error(f"❌ Failed to create a Vosk model from {MODEL_PATH}: {e}\n\nMake sure the folder is not empty, is not a zip file, and contains subfolders like 'am', 'conf', 'graph', etc.")
    st.stop()

# Audio settings
q = queue.Queue()
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize session state for toggles
if 'listening' not in st.session_state:
    st.session_state['listening'] = False
if 'paused' not in st.session_state:
    st.session_state['paused'] = False
if 'result_text' not in st.session_state:
    st.session_state['result_text'] = ""
if 'hindi_text' not in st.session_state:
    st.session_state['hindi_text'] = ""
if 'telugu_text' not in st.session_state:
    st.session_state['telugu_text'] = ""

def audio_callback(in_data, frame_count, time_info, status):
    q.put(in_data)
    return (None, pyaudio.paContinue)

def play_tts(text, lang_code, lang_name):
    """Play text-to-speech for given text and language"""
    try:
        if text and len(text.strip()) > 0:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                threading.Thread(target=lambda: [playsound(tmp_file.name), os.unlink(tmp_file.name)], daemon=True).start()
                return True
    except Exception as e:
        st.error(f"TTS Error for {lang_name}: {e}")
        return False

def continuous_recognition():
    st.session_state['listening'] = True
    rec = vosk.KaldiRecognizer(vosk_model, 16000)
    result_text = ""
    hindi_text = ""
    partial_placeholder = st.empty()
    final_placeholder = st.empty()
    hindi_placeholder = st.empty()
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK,
                   stream_callback=audio_callback)
    stream.start_stream()
    st.write("🎤 Listening... Click 'Stop' to end.")
    
    try:
        while st.session_state.get('listening', False):
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    result_text += text + " "
                    final_placeholder.success("✅ Transcribed Text (English):")
                    final_placeholder.write(result_text)
                    # Live translation
                    hindi_text = hindi_translator.translate(result_text)
                    hindi_placeholder.markdown(
        f"""
        <div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:10px; font-size:18px; color:#ffeb3b;">
            ✅ Live Translated Text (Hindi):<br><br>{hindi_text}
        </div>
        """,
        unsafe_allow_html=True
    )
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "")
                if partial:
                    partial_placeholder.info(f"Partial: {partial}")
            time.sleep(0.01)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    # Final result after stopping
    final_result = json.loads(rec.FinalResult())
    text = final_result.get("text", "")
    if text:
        result_text += text
        final_placeholder.success("✅ Final Transcribed Text (English):")
        final_placeholder.write(result_text)
        hindi_text = hindi_translator.translate(result_text)
        hindi_placeholder.success("✅ Final Translated Text (Hindi):")
        hindi_placeholder.write(hindi_text)
    return result_text.strip()

# Streamlit UI
st.markdown(
    "<h1 style='text-align: center; color: white;'>🎙 Live Translator </h1>",
    unsafe_allow_html=True,
)

# Control Buttons - Main controls in next line after title
st.markdown("---")
col1, col2, col3 = st.columns(3)
start_clicked = col1.button("► Start Listening", disabled=st.session_state['listening'], key="main_start")
pause_label = "II Pause" if not st.session_state['paused'] else "► Resume"
pause_clicked = col2.button(pause_label, disabled=not st.session_state['listening'], key="main_pause")
stop_clicked = col3.button("■ Stop", disabled=not st.session_state['listening'], key="main_stop")

# Handle button clicks
if start_clicked:
    st.session_state['listening'] = True
    st.session_state['paused'] = False
    st.session_state['result_text'] = ""
    st.session_state['hindi_text'] = ""
    st.session_state['telugu_text'] = ""
    st.rerun()

if pause_clicked:
    st.session_state['paused'] = not st.session_state['paused']
    st.rerun()

if stop_clicked:
    st.session_state['listening'] = False
    st.session_state['paused'] = False
    st.rerun()

# Paused Status Display
if st.session_state['paused'] and st.session_state['listening']:
    word_count = len(st.session_state.get('result_text', '').split()) if st.session_state.get('result_text') else 0
    st.markdown(
        f"""
        <div style="background:rgba(255,193,7,0.2); padding:15px; border-radius:10px; margin:10px 0; border-left:4px solid #FFC107;">
            <h4 style="color:#FFC107; margin:0; font-size:16px;">⏸ PAUSED - Words: {word_count}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

if not st.session_state['listening'] and st.session_state.get('result_text'):
    st.success("✔ Recording Complete!")

# Final Transcribed Text (English)
if not st.session_state['listening'] and st.session_state.get('result_text'):
    st.write("**Final Transcribed Text (English):**")
    st.write(st.session_state['result_text'])

# Final Translated Text (Hindi)
if not st.session_state['listening'] and st.session_state.get('hindi_text') and st.session_state.get('hindi_text') != 'Hindi translations will appear here...':
    st.markdown(
        f"""
        <div style="background:rgba(76,175,80,0.2); padding:20px; border-radius:15px; 
                   border:2px solid #4CAF50; margin:20px 0;">
            <h4 style="color:#4CAF50; margin:0 0 15px 0; font-size:18px;">✔ Final Translated Text (Hindi):</h4>
            <div style="font-size:20px; color:#81C784; line-height:1.6; background:rgba(0,0,0,0.3); padding:15px; border-radius:10px;">
                {st.session_state['hindi_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🔊 Play Hindi Audio", key="play_hindi_final"):
        play_tts(st.session_state['hindi_text'], 'hi', 'Hindi')

# Final Translated Text (Telugu)
if not st.session_state['listening'] and st.session_state.get('telugu_text') and st.session_state.get('telugu_text') != 'Telugu translations will appear here...':
    st.markdown(
        f"""
        <div style="background:rgba(33,150,243,0.2); padding:20px; border-radius:15px; 
                   border:2px solid #2196F3; margin:20px 0;">
            <h4 style="color:#2196F3; margin:0 0 15px 0; font-size:18px;">✔ Final Translated Text (Telugu):</h4>
            <div style="font-size:20px; color:#81C784; line-height:1.6; background:rgba(0,0,0,0.3); padding:15px; border-radius:10px;">
                {st.session_state['telugu_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🔊 Play Telugu Audio", key="play_telugu_final"):
        play_tts(st.session_state['telugu_text'], 'te', 'Telugu')

# Clear Results Button 
if not st.session_state['listening'] and (st.session_state.get('result_text') or st.session_state.get('hindi_text') or st.session_state.get('telugu_text')):
    st.markdown("---")
    if st.button("🗑 Clear Results", key="clear_results"):
        st.session_state['result_text'] = ""
        st.session_state['hindi_text'] = ""
        st.session_state['telugu_text'] = ""
        st.session_state['listening'] = False
        st.session_state['paused'] = False
        st.rerun()

# Main recording logic
if st.session_state['listening']:
    # Initialize result storage
    if 'result_text' not in st.session_state:
        st.session_state['result_text'] = ""
    

    word_count = len(st.session_state.get('result_text', '').split()) if st.session_state.get('result_text') else 0
    
    if st.session_state['paused']:
        st.warning(f"⏸ **PAUSED** - Click 'Resume' to continue | Words: {word_count}")
    else:
        st.success(f"🎤 **LISTENING** - Speak now... | Words: {word_count}")
        

        with st.spinner("🎤 Recording and translating..."):
            try:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=audio_callback
                )
                stream.start_stream()
                
                rec = vosk.KaldiRecognizer(vosk_model, 16000)

                partial_placeholder = st.empty()
                final_placeholder = st.empty()
                hindi_placeholder = st.empty()
                telugu_placeholder = st.empty()
                
                recording_time = 0
                while st.session_state['listening'] and recording_time < 30:  # Max 30 seconds
                    if st.session_state['paused']:
                        time.sleep(0.1)
                        continue
                        
                    try:
                        if not q.empty():
                            data = q.get_nowait()
                            
                            if rec.AcceptWaveform(data):
                                result = json.loads(rec.Result())
                                text = result.get("text", "")
                                if text:
                                    st.session_state['result_text'] += text + " "
                                    
                                    try:
                                        new_hindi = hindi_translator.translate(text)
                                        new_telugu = telugu_translator.translate(text)
                                        
                                        st.session_state['hindi_text'] += new_hindi + " "
                                        st.session_state['telugu_text'] += new_telugu + " "
                                        
                                        final_placeholder.success("✅ **English Text:**")
                                        final_placeholder.write(st.session_state['result_text'])
                                        
                                        hindi_placeholder.markdown(
                                            f"""
                                            <div style="background:rgba(76,175,80,0.2); padding:15px; border-radius:10px; 
                                                       border:2px solid #4CAF50; margin:10px 0;">
                                                <h4 style="color:#4CAF50; margin:0 0 10px 0; font-size:16px;">🔄 Live Hindi Translation:</h4>
                                                <div style="font-size:16px; color:#81C784; line-height:1.6;">
                                                    {st.session_state['hindi_text']}
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                        
                                        telugu_placeholder.markdown(
                                            f"""
                                            <div style="background:rgba(33,150,243,0.2); padding:15px; border-radius:10px; 
                                                       border:2px solid #2196F3; margin:10px 0;">
                                                <h4 style="color:#2196F3; margin:0 0 10px 0; font-size:16px;">🔄 Live Telugu Translation:</h4>
                                                <div style="font-size:16px; color:#81C784; line-height:1.6;">
                                                    {st.session_state['telugu_text']}
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                        
                                        # Force UI update to show real-time translations
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"Translation error: {e}")
                            else:
                                partial = json.loads(rec.PartialResult()).get("partial", "")
                                if partial and not st.session_state['paused']:
                                    partial_placeholder.info(f"🔄 Listening: {partial}")
                    except:
                        pass
                    
                    time.sleep(0.1)
                    recording_time += 0.1
                
                # Cleanup
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                # Auto-stop after recording
                st.session_state['listening'] = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Recording error: {e}")
                st.session_state['listening'] = False