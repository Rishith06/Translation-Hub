import streamlit as st
import sounddevice as sd
import queue
import vosk
import sys
import json
import argostranslate.package
import argostranslate.translate
import time
import streamlit.components.v1 as components

# ---------------- BACKGROUND + THEME ---------------- #
st.set_page_config(page_title="Text Translator", layout="wide")

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

# Galaxy Theme CSS
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

# Load Argos Translate
installed_languages = argostranslate.translate.get_installed_languages()
from_lang = list(filter(lambda x: x.code == "en", installed_languages))[0]
to_lang = list(filter(lambda x: x.code == "hi", installed_languages))[0]
translation = from_lang.get_translation(to_lang)

# Load Vosk Model
MODEL_PATH = "translator_app/vosk-model-en-in-0.5"
vosk_model = vosk.Model(MODEL_PATH)

# Audio settings
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def continuous_recognition():
    st.session_state['listening'] = True
    rec = vosk.KaldiRecognizer(vosk_model, 16000)
    result_text = ""
    hindi_text = ""
    partial_placeholder = st.empty()
    final_placeholder = st.empty()
    hindi_placeholder = st.empty()
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        st.write("🎤 Listening... Click 'Stop' to end.")
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
                    hindi_text = translation.translate(result_text)
                    # hindi_placeholder.success("✅ Live Translated Text (Hindi):")
                    # hindi_placeholder.write(hindi_text)
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
                    # Optionally, show live translation of partial
                    # hindi_partial = translation.translate(partial)
                    # hindi_placeholder.info(f"Partial Hindi: {hindi_partial}")
            time.sleep(0.01)
    # Final result after stopping
    final_result = json.loads(rec.FinalResult())
    text = final_result.get("text", "")
    if text:
        result_text += text
        final_placeholder.success("✅ Final Transcribed Text (English):")
        final_placeholder.write(result_text)
        hindi_text = translation.translate(result_text)
        hindi_placeholder.success("✅ Final Translated Text (Hindi):")
        hindi_placeholder.write(hindi_text)
    return result_text.strip()

# Streamlit UI
st.markdown(
    "<h1 style='text-align: center; color: #90caf9;'>🎙️ English to Hindi Voice Translator</h1>",
    unsafe_allow_html=True,
)

if 'listening' not in st.session_state:
    st.session_state['listening'] = False
if 'paused' not in st.session_state:
    st.session_state['paused'] = False

col1, col2 = st.columns(2)
start_clicked = col1.button("▶️ Start Listening", disabled=st.session_state['listening'])
pause_label = "⏸️ Pause" if not st.session_state['paused'] else "▶️ Resume"
pause_clicked = col2.button(pause_label, disabled=not st.session_state['listening'])

if start_clicked:
    st.session_state['listening'] = True
    st.session_state['paused'] = False
    with st.spinner("Recording and transcribing..."):
        eng_text = ""
        rec = vosk.KaldiRecognizer(vosk_model, 16000)
        result_text = ""
        hindi_text = ""
        partial_placeholder = st.empty()
        final_placeholder = st.empty()
        hindi_placeholder = st.empty()
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
            st.write("🎤 Listening... Click 'Pause' to pause.")
            while st.session_state.get('listening', False):
                if st.session_state.get('paused', False):
                    st.write("⏸️ Paused. Click 'Resume' to continue.")
                    time.sleep(0.1)
                    continue
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        result_text += text + " "
                        final_placeholder.success("✅ Transcribed Text (English):")
                        final_placeholder.write(result_text)
                        # Live translation
                        hindi_text = translation.translate(result_text)
                        hindi_placeholder.success("✅ Live Translated Text (Hindi):")
                        hindi_placeholder.write(hindi_text)
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        partial_placeholder.info(f"Partial: {partial}")
                time.sleep(0.01)
        # Final result after stopping
        final_result = json.loads(rec.FinalResult())
        text = final_result.get("text", "")
        if text:
            result_text += text
            final_placeholder.success("✅ Final Transcribed Text (English):")
            final_placeholder.write(result_text)
            hindi_text = translation.translate(result_text)
            hindi_placeholder.success("✅ Final Translated Text (Hindi):")
            hindi_placeholder.write(hindi_text)
        eng_text = result_text.strip()
        if not eng_text:
            st.warning("Could not detect any speech.")

if pause_clicked:
    st.session_state['paused'] = not st.session_state['paused']
