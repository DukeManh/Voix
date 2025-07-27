import streamlit as st
import torch
from TTS.api import TTS
import tempfile
import os
import io
import base64
import torch.serialization
import atexit
import glob
import time

# Page configuration
st.set_page_config(
    page_title="Coqui TTS Voice Generator",
    page_icon="🎤",
    layout="wide"
)

# Global cleanup registry
if 'temp_files_to_cleanup' not in st.session_state:
    st.session_state.temp_files_to_cleanup = set()

def cleanup_temp_files():
    """Clean up any remaining temporary files"""
    for file_path in list(st.session_state.temp_files_to_cleanup):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
            st.session_state.temp_files_to_cleanup.discard(file_path)
        except:
            pass  # Ignore cleanup errors

def cleanup_orphaned_files():
    """Clean up any orphaned TTS files in temp directory"""
    try:
        temp_dir = tempfile.gettempdir()
        # Find all temporary wav files that might be from our app
        pattern = os.path.join(temp_dir, "tmp*.wav")
        for file_path in glob.glob(pattern):
            try:
                # Only delete files older than 1 hour to be safe
                if os.path.getmtime(file_path) < (time.time() - 3600):
                    os.unlink(file_path)
            except:
                pass
    except:
        pass

# Register cleanup function to run on app exit
atexit.register(cleanup_temp_files)

# Initialize session state
if 'tts_model' not in st.session_state:
    st.session_state.tts_model = None
if 'available_voices' not in st.session_state:
    st.session_state.available_voices = {}
if 'last_model_path' not in st.session_state:
    st.session_state.last_model_path = None

@st.cache_resource
def load_tts_model(model_name):
    """Load and cache the TTS model"""
    try:
        # Allowlist custom optimizer for Coqui TTS checkpoints
        torch.serialization.add_safe_globals(["TTS.utils.radam.RAdam"])
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize TTS model
        tts = TTS(model_name=model_name, progress_bar=False).to(device)
        return tts
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

def generate_audio(text, model, speaker=None, language=None, speed=1.0):
    """Generate audio from text using the TTS model"""
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            temp_file_path = tmp_file.name
            
            # Handle multilingual models (YourTTS)
            if hasattr(model, 'languages') and model.languages:
                # For multilingual models, both speaker and language are required
                if speaker and language:
                    model.tts_to_file(text=text, speaker=speaker, language=language, file_path=temp_file_path, speed=speed)
                elif language:
                    model.tts_to_file(text=text, language=language, file_path=temp_file_path, speed=speed)
                else:
                    # Default to French for multilingual models
                    model.tts_to_file(text=text, language="fr-fr", file_path=temp_file_path, speed=speed)
            # Handle single-language models with speakers
            elif speaker and hasattr(model, "speakers") and model.speakers:
                model.tts_to_file(text=text, speaker=speaker, file_path=temp_file_path, speed=speed)
            # Handle simple single-language, single-speaker models
            else:
                model.tts_to_file(text=text, file_path=temp_file_path, speed=speed)
            
            # Register temp file for cleanup
            st.session_state.temp_files_to_cleanup.add(temp_file_path)
            
            return temp_file_path
            
    except Exception as e:
        # Clean up temp file if there was an error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore cleanup errors
        st.error(f"Error generating audio: {str(e)}")
        return None

def test_voice_loading():
    """Test if voices can be loaded successfully"""
    test_results = {}
    
    # Only test truly working French voice models
    french_voices = [
        ("tts_models/fr/css10/vits", None),  # Single French speaker
        ("tts_models/multilingual/multi-dataset/your_tts", "fr-fr"),  # Multilingual with 6 speakers
    ]
    
    for model_path, language in french_voices:
        try:
            # Test loading the model
            tts = TTS(model_name=model_path, progress_bar=False)
            test_results[f"{model_path}_{language}"] = "✅ Available"
            
            # For YourTTS, also note the speakers available
            if "your_tts" in model_path and hasattr(tts, 'speakers'):
                test_results[f"{model_path}_speakers"] = f"✅ {len(tts.speakers)} speakers available"
            
            # Clean up the model from memory
            del tts
            
        except Exception as e:
            test_results[f"{model_path}_{language}"] = f"❌ Error: {str(e)[:50]}..."
    
    return test_results

@st.cache_resource
def load_all_models():
    """Load all available TTS models for the user"""
    with st.spinner("Loading available TTS models..."):
        # Test and load each voice model
        voice_status = test_voice_loading()
        
        # Display model availability
        for voice, status in voice_status.items():
            st.session_state.available_voices[voice] = status
            if "Error" not in status:
                model_path, speaker = voice.split("_")
                st.session_state.tts_model = load_tts_model(model_path)
                st.session_state.last_model_path = model_path
                st.success(f"✅ Loaded: {voice}")
            else:
                st.warning(f"⚠️ {status}")
    
    # Final status message
    if st.session_state.tts_model:
        st.success("All available models have been loaded.")
    else:
        st.error("No models could be loaded. Please check the logs.")

def main():
    st.title("🎤 Coqui TTS Voice Generator")
    st.markdown("Generate natural-sounding speech from text using Coqui TTS")
    
    # Sidebar for model and voice selection
    with st.sidebar:
        st.header("🗣️ Choisir une Voix Française")
        
        # Add voice testing button
        if st.button("🧪 Test Voice Loading", help="Test which French voices are available"):
            with st.spinner("Testing French voice models..."):
                test_results = test_voice_loading()
                st.write("**Voice Availability:**")
                for voice_key, status in test_results.items():
                    if "Available" in status:
                        st.success(f"✅ {voice_key}")
                    else:
                        st.error(f"❌ {voice_key}: {status}")
        
        # French voice options with friendly names
        voice_options = [
            ("👨 Pierre (Voix Masculine Claire)", "tts_models/fr/css10/vits", None),
            ("👩 Marie (Voix Féminine Douce)", "tts_models/multilingual/multi-dataset/your_tts", "female-en-5"),
            ("👩 Sophie (Voix Féminine Naturelle)", "tts_models/multilingual/multi-dataset/your_tts", "female-pt-4\n"),
            ("👨 Antoine (Voix Masculine Grave)", "tts_models/multilingual/multi-dataset/your_tts", "male-en-2"),
            ("👨 Laurent (Voix Masculine Expressive)", "tts_models/multilingual/multi-dataset/your_tts", "male-pt-3\n"),
        ]
        voice_labels = [v[0] for v in voice_options]
        selected_voice_idx = st.selectbox("Voice:", options=range(len(voice_labels)), format_func=lambda i: voice_labels[i])
        selected_voice = voice_options[selected_voice_idx]
        model_path, speaker = selected_voice[1], selected_voice[2]

        # Automatically load model when selection changes
        if (not st.session_state.tts_model) or (st.session_state.get('last_model_path') != model_path):
            with st.spinner("Loading TTS model... This may take a few minutes on first run."):
                st.session_state.tts_model = load_tts_model(model_path)
                st.session_state.last_model_path = model_path
            if st.session_state.tts_model:
                st.success("✅ Model loaded successfully!")
            else:
                st.error("❌ Failed to load model")

        # Show model status
        if st.session_state.tts_model:
            st.success("✅ Model Ready")
        else:
            st.warning("⚠️ Please load a model first")

        # Device info
        device = "CUDA (GPU)" if torch.cuda.is_available() else "CPU"
        st.info(f"🖥️ Using: {device}")
        
        # Voice speed control
        st.header("⚡ Contrôle de Vitesse")
        voice_speed = st.slider(
            "Vitesse de la voix:",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="0.5 = Très lent, 1.0 = Normal, 2.0 = Très rapide"
        )
        speed_labels = {
            0.5: "🐌 Très lent",
            0.7: "🚶 Lent", 
            1.0: "👍 Normal",
            1.3: "🏃 Rapide",
            1.5: "⚡ Très rapide",
            2.0: "🚀 Ultra rapide"
        }
        # Find closest label
        closest_speed = min(speed_labels.keys(), key=lambda x: abs(x - voice_speed))
        if abs(closest_speed - voice_speed) <= 0.1:
            st.caption(f"📊 {speed_labels[closest_speed]}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Text Input")
        text_input = st.text_area(
            "Enter the text you want to read aloud:",
            height=200,
            placeholder="Type your text here... For example: 'Bonjour, ceci est une démonstration de la technologie Coqui TTS!'"
        )
        # Character count
        char_count = len(text_input)
        st.caption(f"Characters: {char_count}")
        if char_count > 1000:
            st.warning("⚠️ Long texts may take more time to process")

    with col2:
        st.header("🔊 Text Reader")
        # Automatically generate and play audio when text is entered and model is loaded
        if st.session_state.tts_model and text_input.strip():
            with st.spinner("Reading aloud..."):
                # For YourTTS multilingual models, pass both speaker and language
                if "your_tts" in model_path and speaker:
                    audio_file = generate_audio(text_input, st.session_state.tts_model, speaker, "fr-fr", voice_speed)
                # For CSS10 and other single-language models
                elif speaker:
                    audio_file = generate_audio(text_input, st.session_state.tts_model, speaker, None, voice_speed)
                else:
                    audio_file = generate_audio(text_input, st.session_state.tts_model, None, None, voice_speed)
                    
                if audio_file:
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav", start_time=0)
                    st.download_button(
                        label="💾 Download Audio",
                        data=audio_bytes,
                        file_name="read_text.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                    os.unlink(audio_file)
                    st.success("✅ Reading complete!")
    
    # Instructions and tips
    with st.expander("📖 Comment Utiliser"):
        st.markdown("""
        ### Pour Commencer:
        1. **Tester les Voix**: Cliquez sur "🧪 Test Voice Loading" pour vérifier quelles voix françaises sont disponibles
        2. **Choisir une Voix**: Sélectionnez une voix française dans le menu déroulant
        3. **Saisir le Texte**: Tapez ou collez le texte français que vous voulez convertir en parole
        4. **Écouter**: L'audio se génère automatiquement et vous pouvez l'écouter directement
        5. **Télécharger**: Cliquez sur "💾 Download Audio" pour sauvegarder le fichier
        
        ### Voix Françaises Disponibles:
        - 🇫🇷 **CSS10**: Voix française masculine naturelle et claire
        - 🇫🇷 **YourTTS**: 4 voix françaises distinctes (2 femmes, 2 hommes) avec différentes caractéristiques vocales
        
        ### Toutes les Voix Parlent Français:
        - ✅ Toutes les options génèrent une parole française naturelle
        - 🎭 Chaque voix offre un timbre et une personnalité différents
        - 🔄 Testez différentes voix pour trouver celle qui convient le mieux à votre texte
        
        ### À Noter:
        - ✅ CSS10: Une seule voix masculine française de qualité
        - 🎭 YourTTS: 6 voix distinctes (3 hommes, 3 femmes) entraînées multilingues
        - 🔄 Changez entre CSS10 et YourTTS pour des voix complètement différentes
        
        ### Conseils:
        - 💡 Les textes plus courts se génèrent plus rapidement
        - 🖥️ L'accélération GPU est utilisée automatiquement si disponible
        - 🧪 Utilisez le test de voix pour vérifier la compatibilité avant utilisation
        - 📝 Essayez différents textes pour comparer les voix
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("Construit avec ❤️ en utilisant [Coqui TTS](https://github.com/coqui-ai/TTS) et Streamlit | Spécialisé pour le Français")

if __name__ == "__main__":
    main()