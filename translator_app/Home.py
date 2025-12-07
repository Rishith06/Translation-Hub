import streamlit as st

st.set_page_config(
    page_title="Translation Hub",
    page_icon="🌐",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd, #fce4ec);
        color: #2c3e50;
    }
    .big-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .description {
        font-size: 1.1rem;
        text-align: center;
        color: #424242;
        margin-bottom: 2rem;
    }
    .card-btn {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        text-align: center;
        text-decoration: none;
        display: block;
        min-width: 300px;
    }
    .card-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
    }
    .card-btn h3 {
        color: #0d47a1;
        margin-bottom: 0.5rem;
    }
    .card-btn p {
        color: #424242;
        margin-bottom: 0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🌐 Translation Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='description'>Your one-stop solution for real-time and recorded speech translation.</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


row1_cols = st.columns(2)
with row1_cols[0]:
    st.markdown(
        """
        <a href="/Live_Translator" target="_self" class="card-btn">
            <h3>🎤 Live Translator</h3>
            <p>Translate English speech to Hindi in real-time using Vosk + Argos Translate.</p>
        </a>
        """,
        unsafe_allow_html=True
    )
with row1_cols[1]:
    st.markdown(
        """
        <a href="/Speech_Translator" target="_self" class="card-btn">
            <h3>🎙 Speech_Translator</h3>
            <p>Record your audio, translate instantly, and hear the output in Hindi.</p>
        </a>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

row2_cols = st.columns(2)
with row2_cols[0]:
    st.markdown(
        """
        <a href="/Text_to_Text_Translator" target="_self" class="card-btn">
            <h3>📝 Text Translator</h3>
            <p>Type any text and translate it into multiple languages instantly.</p>
        </a>
        """,
        unsafe_allow_html=True
    )
with row2_cols[1]:
    st.markdown(
        """
        <a href="/Dirazation" target="_self" class="card-btn">
            <h3>🎧 Diarization</h3>
            <p>Detect and label multiple speakers in any audio recording.</p>
        </a>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center; color:#555;'>📌 Click a tool above to get started.</p>",
    unsafe_allow_html=True
)