import asyncio
import requests
import hashlib
import os
from pathlib import Path

try:
    import edge_tts
except ImportError:
    edge_tts = None

AUDIO_DIR = Path(__file__).parent.parent.parent / "audio_cache"
AUDIO_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"
VOICE = "en-US-JennyNeural"  # Natural female voice


def _generate_explanation(question, answer):
    """Ask Ollama to generate a teacher-style spoken explanation (not just read the answer)."""
    prompt = f"""You are a friendly college professor explaining a concept to a student verbally.

The student asked: "{question}"

The textbook answer is:
{answer}

Now explain this concept step by step as if you're talking to the student face to face. 
Rules:
- Use simple, conversational language
- Say "So basically..." or "Think of it this way..." to make it natural
- Explain HOW it works, don't just repeat the answer
- Keep it under 150 words
- Do NOT use bullet points, code, or special formatting - just flowing speech"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 300, "temperature": 0.8}
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"Let me explain this simply. {answer[:300]}"


async def _text_to_speech(text, output_path):
    """Convert text to MP3 using edge-tts."""
    if edge_tts is None:
        raise RuntimeError("edge-tts is not installed. Run: pip install edge-tts")
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(str(output_path))


def generate_voice_explanation(question, answer):
    """Generate a voice explanation and return the audio file path."""
    cache_key = hashlib.md5(f"{question}:{answer[:100]}".encode()).hexdigest()
    audio_path = AUDIO_DIR / f"{cache_key}.mp3"

    if audio_path.exists():
        return str(audio_path), None

    explanation = _generate_explanation(question, answer)
    asyncio.run(_text_to_speech(explanation, audio_path))

    return str(audio_path), explanation


def cleanup_old_audio(max_files=100):
    """Remove oldest audio files if cache exceeds limit."""
    files = sorted(AUDIO_DIR.glob("*.mp3"), key=os.path.getmtime)
    while len(files) > max_files:
        files.pop(0).unlink()
