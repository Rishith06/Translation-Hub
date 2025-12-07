import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import torch
import librosa
import numpy as np

import torchaudio  # <-- add this

# --- torchaudio / speechbrain compatibility patch ---
# Some newer torchaudio builds on Windows/Python 3.12 don't expose list_audio_backends(),
# but speechbrain expects it. We monkey-patch a minimal version.

if not hasattr(torchaudio, "list_audio_backends"):
    def _fake_list_audio_backends():
        # We just pretend that at least one backend is available.
        # speechbrain only checks that this list is non-empty.
        return ["soundfile"]

    torchaudio.list_audio_backends = _fake_list_audio_backends
# --- end patch ---


from speechbrain.pretrained import EncoderClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

st.set_page_config(page_title="Text Translator", layout="wide")

# Custom CSS to hide Streamlit elements including the deployment button and hamburger menu
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

# Inject custom CSS to hide Streamlit elements
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ===========================
# Inject Galaxy Theme CSS
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



st.title("🎤  Speaker Diarization")
st.caption("Auto Speaker Detection + Transcription")

# Upload audio
audio_file = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3"])

# Pause threshold slider
pause_threshold = st.slider("Pause threshold for sentence breaks (seconds)", 0.1, 2.0, 0.5, 0.1)

# Load pretrained speaker embedding model
@st.cache_resource
def load_embedder():
    return EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        run_opts={"device": "cpu"}  # change to "cuda" if you have GPU
    )
embedder = load_embedder()

def get_embedding(y, sr):
    """Extract speaker embedding using SpeechBrain ECAPA model"""
    signal = torch.tensor(y).unsqueeze(0)
    embedding = embedder.encode_batch(signal).detach().cpu().numpy()
    return embedding.flatten()

if audio_file is not None:
    # Save uploaded file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tfile.write(audio_file.read())
    audio_path = tfile.name

    st.audio(audio_path)

    if st.button("🚀 Run  Diarization"):
        with st.spinner("Transcribing with Whisper..."):
            # model = WhisperModel("small.en", compute_type="int8")
            model = WhisperModel("small.en", device="cpu", compute_type="int8")

            segments, _ = model.transcribe(audio_path, word_timestamps=True)

            # Collect sentence segments
            sentence_segments = []
            current_start = None
            current_text = ""
            prev_end = 0

            for segment in segments:
                for word in segment.words:
                    if current_start is None:
                        current_start = word.start
                    gap = word.start - prev_end
                    if gap > pause_threshold and current_text.strip():
                        sentence_segments.append((current_start, prev_end, current_text.strip()))
                        current_text = word.word
                        current_start = word.start
                    else:
                        current_text += " " + word.word
                    prev_end = word.end
            if current_text.strip():
                sentence_segments.append((current_start, prev_end, current_text.strip()))

        with st.spinner("Extracting embeddings & detecting speakers..."):
            features = []
            for start, end, text in sentence_segments:
                y, sr = librosa.load(audio_path, sr=16000, offset=start, duration=end - start)
                features.append(get_embedding(y, sr))

            # Auto-select optimal speaker count
            possible_k = range(3, min(len(features), 6))
            best_k = 3
            best_score = -1
            for k in possible_k:
                kmeans_temp = KMeans(n_clusters=k, random_state=0).fit(features)
                if len(set(kmeans_temp.labels_)) > 1:
                    score = silhouette_score(features, kmeans_temp.labels_)
                    if score > best_score:
                        best_score = score
                        best_k = k

            kmeans = KMeans(n_clusters=best_k, random_state=0).fit(features)
            labels = kmeans.labels_

            # Consistent speaker numbering
            speaker_map = {}
            speaker_counter = 1
            final_labels = []
            for label in labels:
                if label not in speaker_map:
                    speaker_map[label] = speaker_counter
                    speaker_counter += 1
                final_labels.append(speaker_map[label])

        # 🎨 Build WOW chat-style output
        st.subheader(f"✨ Diarization Result (Detected {best_k} speakers)")
        for (start, end, text), speaker in zip(sentence_segments, final_labels):
            st.markdown(
    f"""
    <div style='
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 12px 15px;
        margin: 8px 0;
        color: #f5f5f5;
        font-size: 16px;
        line-height: 1.5;
    '>
        <b style="color:#4CAF50;">Speaker {speaker}</b>
        <span style='color:#bbb; font-size:12px;'> [{start:.1f}s - {end:.1f}s]</span><br>
        {text}
    </div>
    """,
    unsafe_allow_html=True
)


        # Download button
        result_text = "\n".join(
            [f"Speaker {speaker}: {text}" for (_, _, text), speaker in zip(sentence_segments, final_labels)]
        )
        st.download_button("💾 Download Transcript", result_text, file_name="diarization.txt")