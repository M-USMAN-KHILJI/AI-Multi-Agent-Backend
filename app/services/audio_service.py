import os
import re
import uuid
import time
import wave
import hashlib
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

class AudioService:
    """
    Multimodal Audio Service:
    - Primary: ElevenLabs high-fidelity Neural TTS (default: Rachel / multilingual v2)
    - Fallback: NVIDIA Resemble.AI Chatterbox Multilingual TTS
    - Automatic text normalization (strips markdown formatting for smooth speech)
    - MD5 audio caching for instantaneous playback on repeated sentences
    """
    def __init__(self):
        # ElevenLabs Settings
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        self.elevenlabs_model_id = settings.ELEVENLABS_MODEL_ID or "eleven_multilingual_v2"

        # NVIDIA Riva Settings (Fallback)
        self.nvidia_api_key = settings.NVIDIA_TTS_API_KEY
        self.nvidia_server = settings.NVIDIA_TTS_SERVER
        self.nvidia_function_id = settings.NVIDIA_TTS_FUNCTION_ID
        self.nvidia_voice = settings.NVIDIA_TTS_VOICE or "Chatterbox-Multilingual.en-US.Male"

        self.generated_dir = os.path.join(settings.GENERATED_DIR, "audio")
        os.makedirs(self.generated_dir, exist_ok=True)
        self._riva_client = None

    def _get_riva_client(self):
        if self._riva_client is None:
            import riva.client
            auth = riva.client.Auth(
                ssl_root_cert=None,
                use_ssl=True,
                uri=self.nvidia_server,
                metadata_args=[
                    ["function-id", self.nvidia_function_id],
                    ["authorization", f"Bearer {self.nvidia_api_key}"]
                ]
            )
            self._riva_client = riva.client.SpeechSynthesisService(auth)
        return self._riva_client

    def _clean_text_for_speech(self, text: str) -> str:
        """
        Removes Markdown symbols, links, code fences, and bullet characters
        so the synthesized speech sounds natural.
        """
        cleaned = re.sub(r'https?://\S+', '', text)
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'`[^`]*`', '', cleaned)
        cleaned = re.sub(r'[*_#~>]', '', cleaned)
        cleaned = re.sub(r'^[•\-\*]\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _synthesize_elevenlabs(self, text: str, voice_id: str, output_path: str) -> None:
        """
        Calls ElevenLabs REST API to generate realistic speech in MP3.
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self.elevenlabs_model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.05,
                "use_speaker_boost": True
            }
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"ElevenLabs API Error [{resp.status_code}]: {resp.text}")
            with open(output_path, "wb") as f:
                f.write(resp.content)

    def synthesize_speech(
        self,
        text: str,
        voice_name: Optional[str] = None,
        language_code: str = "en-US",
        sample_rate_hz: int = 22050,
        retries: int = 2
    ) -> Dict[str, Any]:
        """
        Synthesizes text into speech audio via ElevenLabs (or falls back to NVIDIA Riva).
        Uses MD5 content hashing for instant cached responses.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for speech synthesis.")

        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            clean_text = text.strip()

        # Limit spoken text to first 1000 characters for optimal latency
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "..."

        # Check if ElevenLabs is configured
        use_elevenlabs = bool(self.elevenlabs_api_key)
        # If the frontend passes the legacy NVIDIA voice or empty string, default to ElevenLabs voice
        if not voice_name or "Chatterbox" in voice_name:
            chosen_voice = self.elevenlabs_voice_id if use_elevenlabs else self.nvidia_voice
        else:
            chosen_voice = voice_name
        ext = "mp3" if use_elevenlabs else "wav"

        # ── Check Audio Cache ──
        cache_key = hashlib.md5(f"{clean_text}_{chosen_voice}_{use_elevenlabs}".encode("utf-8")).hexdigest()
        cached_filename = f"tts_{cache_key}.{ext}"
        cached_path = os.path.join(self.generated_dir, cached_filename)

        if os.path.exists(cached_path) and os.path.getsize(cached_path) > 1000:
            return {
                "filename": cached_filename,
                "file_path": cached_path,
                "url": f"/generated/audio/{cached_filename}",
                "text": clean_text,
                "voice": chosen_voice,
                "language_code": language_code,
                "size_bytes": os.path.getsize(cached_path),
                "model": "elevenlabs/eleven_multilingual_v2" if use_elevenlabs else "resembleai/chatterbox-multilingual-tts",
                "cached": True,
                "status": "success"
            }

        # ── Try ElevenLabs ──
        if use_elevenlabs:
            try:
                self._synthesize_elevenlabs(clean_text, chosen_voice, cached_path)
                return {
                    "filename": cached_filename,
                    "file_path": cached_path,
                    "url": f"/generated/audio/{cached_filename}",
                    "text": clean_text,
                    "voice": chosen_voice,
                    "language_code": language_code,
                    "size_bytes": os.path.getsize(cached_path),
                    "model": "elevenlabs/eleven_multilingual_v2",
                    "cached": False,
                    "status": "success"
                }
            except Exception as e:
                # If ElevenLabs fails and NVIDIA is configured, fall back
                if not self.nvidia_api_key:
                    raise RuntimeError(f"ElevenLabs TTS failed: {str(e)}")

        # ── Fallback: NVIDIA Chatterbox TTS ──
        last_error = None
        cached_filename_wav = f"tts_{cache_key}.wav"
        cached_path_wav = os.path.join(self.generated_dir, cached_filename_wav)

        for attempt in range(retries):
            try:
                client = self._get_riva_client()
                response = client.synthesize(
                    text=clean_text,
                    voice_name=self.nvidia_voice,
                    language_code=language_code,
                    sample_rate_hz=sample_rate_hz
                )
                audio_data = response.audio
                if not audio_data:
                    raise RuntimeError("NVIDIA Chatterbox returned empty audio bytes.")

                with wave.open(cached_path_wav, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate_hz)
                    wf.writeframes(audio_data)

                return {
                    "filename": cached_filename_wav,
                    "file_path": cached_path_wav,
                    "url": f"/generated/audio/{cached_filename_wav}",
                    "text": clean_text,
                    "voice": self.nvidia_voice,
                    "language_code": language_code,
                    "size_bytes": os.path.getsize(cached_path_wav),
                    "model": "resembleai/chatterbox-multilingual-tts",
                    "cached": False,
                    "status": "success"
                }
            except Exception as e:
                last_error = str(e)
                self._riva_client = None
                if attempt < retries - 1:
                    time.sleep(0.5)

        raise RuntimeError(f"Audio TTS synthesis failed: {last_error}")

audio_service = AudioService()
