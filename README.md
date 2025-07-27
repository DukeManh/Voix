# Coqui TTS Voice Generator

A simple web application for text-to-speech generation using Coqui TTS and Streamlit.

## Features

- 📝 **Text Input**: Paste any text you want to convert to speech
- 🎤 **Voice Selection**: Choose from multiple TTS models and speakers
- 🎵 **Audio Playback**: Listen to generated audio directly in the browser
- 💾 **Download**: Save generated audio files as WAV
- 🚀 **GPU Support**: Automatic GPU acceleration when available

## Available Models

- **English (Fast)**: Quick generation using Tacotron2
- **English (High Quality)**: Better quality with multiple speaker voices
- **Multilingual**: Support for multiple languages (slower but versatile)

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and go to the URL shown in the terminal (usually `http://localhost:8501`)

3. Load a TTS model by clicking "Load Model" in the sidebar

4. Enter your text and click "Generate Speech"

5. Listen to the audio or download the WAV file

## System Requirements

- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended for larger models)
- GPU (optional but recommended for faster generation)

## Tips

- First model load will download the model files (can take several minutes)
- Shorter texts generate faster
- GPU acceleration is automatically used if available
- The multilingual model supports languages like English, Spanish, French, German, and more

## Troubleshooting

If you encounter issues:
1. Make sure all dependencies are installed correctly
2. Try using a different model if one fails to load
3. Check that you have sufficient disk space for model downloads
4. For GPU issues, ensure PyTorch is installed with CUDA support

## License

This project uses Coqui TTS which is licensed under MPL 2.0.