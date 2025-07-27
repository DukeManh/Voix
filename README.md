# Coqui TTS French Learning App

A web application designed for French learners to practice listening and comprehension. Enter French text, listen to natural-sounding French speech, and instantly see the English translation. Optimized for mobile use.

## Purpose

- Help French learners improve listening skills and pronunciation
- Instantly translate French text to English for comprehension
- Provide multiple French voices for varied listening practice

## Features

- 📝 **French Text Input**: Type or paste French text to convert to speech
- 🎤 **Voice Selection**: Choose from several French voices (male/female)
- 🎵 **Audio Playback**: Listen to generated French audio directly in the browser
- 💾 **Download**: Save generated audio files as WAV
- 🇬🇧 **French to English Translation**: See English translation below the audio player
- 📱 **Mobile Friendly**: Layout optimized for mobile devices

## Installation

1. Clone or download this repository
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```
2. Open your browser and go to the URL shown in the terminal (usually `http://localhost:8501`)
3. Select a French voice and enter your French text
4. Listen to the audio and view the English translation below the player

## System Requirements

- Python 3.8 or higher
- macOS, Windows, or Linux
- 4GB+ RAM (8GB+ recommended for larger models)
- GPU (optional, for faster generation)

## Tips

- First model load will download the model files (can take several minutes)
- Shorter texts generate faster
- GPU acceleration is automatically used if available
- Translation is for French to English only and is intended for French learners

## License

This project uses Coqui TTS which is licensed under MPL 2.0.