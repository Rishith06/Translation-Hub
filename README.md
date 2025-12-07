# 🌐 Translation Hub

A comprehensive, multi-language translation application built with Streamlit that provides real-time speech translation, text translation, and speaker diarization capabilities. Perfect for breaking down language barriers and enabling seamless communication across multiple languages.

## ✨ Features

### 🎤 Live Translator

- Real-time speech-to-text transcription using Vosk offline speech recognition
- Instant translation to multiple languages (Hindi, Telugu, Tamil, Kannada, Gujarati, Marathi)
- Live translation updates as you speak
- Support for pause/resume functionality

### 🎙️ Speech Translator

- Record audio directly in the browser
- Upload audio files in multiple formats (MP3, WAV, M4A, FLAC, OGG, AAC, WMA)
- Automatic audio format conversion for optimal transcription
- Multi-language translation with text-to-speech output
- Transliteration support for Indic languages

### 📝 Text-to-Text Translator

- Translate text between multiple languages
- Support for 100+ language pairs
- Batch translation capabilities
- Clean, intuitive interface

### 🎧 Speaker Diarization

- Identify and label multiple speakers in audio recordings
- Powered by Faster Whisper and SpeechBrain
- Automatic speaker segmentation
- Visual timeline of speaker changes

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio processing) 

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Rishith06/Translation-Hub.git
   cd Translation-Hub
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download Vosk Model** (for offline speech recognition)

   - Download the English-Indian model from [Vosk Models](https://alphacephei.com/vosk/models)
   - Extract it to `translator_app/vosk-model-en-in-0.5/`
   - Or use the model downloader script (if available)

5. **Set up FFmpeg** (if not in system PATH)
   - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract to `ffmpeg/bin/` directory in the project root
   - Or add FFmpeg to your system PATH

### Running the Application

```bash
streamlit run translator_app/Home.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📁 Project Structure

```
Translation-Hub/
├── translator_app/
│   ├── Home.py                 # Main entry point
│   ├── pages/
│   │   ├── Live_Translator.py  # Real-time speech translation
│   │   ├── Speech_Translator.py # Audio file translation
│   │   ├── Text_to_Text_Translator.py # Text translation
│   │   ├── Dirazation.py       # Speaker diarization
│   │   └── Credits.py          # Credits page
│   ├── utils/
│   │   ├── translation_utils.py
│   │   ├── audio_utils.py
│   │   ├── transcription_utils.py
│   │   └── tts_utils.py
│   └── vosk-model-en-in-0.5/   # Vosk speech recognition model
├── ffmpeg/                      # FFmpeg binaries (optional)
├── generated/                   # Generated audio outputs
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Technologies Used

- **Streamlit** - Web application framework
- **Vosk** - Offline speech recognition
- **Faster Whisper** - Fast speech recognition
- **SpeechBrain** - Speaker diarization
- **Deep Translator** - Online translation services
- **Argos Translate** - Offline translation
- **gTTS** - Google Text-to-Speech
- **Librosa** - Audio processing
- **PyDub** - Audio manipulation
- **NumPy & SciPy** - Scientific computing
- **scikit-learn** - Machine learning utilities

## 📝 Usage Examples

### Live Translation

1. Navigate to "Live Translator" from the home page
2. Click "Start Listening"
3. Speak in English
4. View real-time transcription and translations
5. Click "Stop" when finished

### Speech Translation

1. Go to "Speech Translator"
2. Record audio or upload an audio file
3. Wait for transcription
4. View translations in multiple languages
5. Listen to translated audio

### Text Translation

1. Open "Text Translator"
2. Enter or paste text
3. Select source and target languages
4. Get instant translation

## 🔧 Configuration

### Supported Languages

The application supports translation to:

- Hindi (hi)
- Telugu (te)
- Tamil (ta)
- Kannada (kn)
- Gujarati (gu)
- Marathi (mr)
- And 100+ more languages via Deep Translator

### Audio Format Support

- **Input**: MP3, WAV, M4A, FLAC, OGG, AAC, WMA
- **Processing**: Automatically converted to mono 16-bit WAV at 16kHz
- **Output**: MP3 audio files for translations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for offline speech recognition
- [Streamlit](https://streamlit.io/) for the web framework
- All the open-source libraries that made this project possible

## 📧 Contact

For questions, suggestions, or support, please open an issue on GitHub.

---

**Made with ❤️ for breaking down language barriers**
