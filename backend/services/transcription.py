import os
import whisper

# Global cache dictionary for different local whisper models
_local_models = {}


def load_model(model_name: str = "base"):
    """Load and cache the whisper model in memory."""
    global _local_models
    if model_name not in _local_models:
        print(f"Loading local Whisper model '{model_name}' (this may take a moment on first run)...")
        # Cache the loaded model
        _local_models[model_name] = whisper.load_model(model_name)
        print(f"Whisper model '{model_name}' loaded successfully.")
    return _local_models[model_name]


def transcribe_audio(file_path: str, model_name: str = "local-whisper-base") -> str:
    """
    Transcribes the audio file at file_path using either local Whisper or Groq Whisper API.
    Returns the transcript as a string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    try:
        # Determine whether to use local Whisper or Groq API
        if model_name.startswith("local-whisper-"):
            local_name = model_name.replace("local-whisper-", "")
            # Default to base if empty or not standard
            if not local_name:
                local_name = "base"
            
            model = load_model(local_name)
            print(f"Transcribing audio file locally with Whisper '{local_name}': {file_path}")
            result = model.transcribe(file_path, fp16=False)  # fp16=False avoids CPU warning
            transcript_text = result.get("text", "").strip()
            print("Local transcription complete.")
            return transcript_text
        else:
            # Use Groq API Whisper (e.g. whisper-large-v3, whisper-large-v3-turbo)
            print(f"Transcribing audio file via Groq API using model '{model_name}': {file_path}")
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_groq_api_key_here":
                raise ValueError("GROQ_API_KEY environment variable is not set. Please update the .env file.")
                
            client = Groq(api_key=api_key)
            with open(file_path, "rb") as file:
                translation = client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), file.read()),
                    model=model_name,
                )
                transcript_text = translation.text.strip()
                print("Groq API transcription complete.")
                return transcript_text
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        raise e
