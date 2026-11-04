import os
import re
import uuid
import time
import wave
import hashlib
from typing import Dict, Any, Optional
import riva.client
from app.core.config import settings

class AudioService:
    """
    Multimodal Audio Service:
    - Text-to-Speech (TTS) via NVIDIA Resemble.AI Chatterbox Multilingual TTS
    - Automatic text normalization (strips markdown formatting for smooth speech)
    - MD5 audio caching for instantaneous playback on repeated sentences
    - Optimized 22.05kHz audio packaging for low latency transfer
    """
    def __init__(self):
        self.api_key = settings.NVIDIA_TTS_API_KEY
        self.server = settings.NVIDIA_TTS_SERVER
        self.function_id = settings.NVIDIA_TTS_FUNCTION_ID
        self.default_voice = settings.NVIDIA_TTS_VOICE or "Chatterbox-Multilingual.en-US.Male"

        self.generated_dir = os.path.join(settings.GENERATED_DIR, "audio")
        os.makedirs(self.generated_dir, exist_ok=True)
        self._tts_client: Optional[riva.client.SpeechSynthesisService] = None

    def _get_client(self) -> riva.client.SpeechSynthesisService:
        if self._tts_client is None:
            auth = riva.client.Auth(
                ssl_root_cert=None,
                use_ssl=True,
                uri=self.server,
                metadata_args=[
                    ["function-id", self.function_id],
                    ["authorization", f"Bearer {self.api_key}"]
                ]
            )
            self._tts_client = riva.client.SpeechSynthesisService(auth)
        return self._tts_client

    def _clean_text_for_speech(self, text: str) -> str:
        """
        Removes Markdown symbols, links, code fences, and bullet characters
        so the synthesized speech sounds natural.
        """
        # Remove URLs
        cleaned = re.sub(r'https?://\S+', '', text)
        # Remove code blocks and inline code
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'`[^`]*`', '', cleaned)
        # Remove markdown bold/italic/headers
        cleaned = re.sub(r'[*_#~>]', '', cleaned)
        # Remove bullet points and extra dashes
        cleaned = re.sub(r'^[•\-\*]\s+', '', cleaned, flags=re.MULTILINE)
        # Collapse whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def synthesize_speech(
        self,
        text: str,
        voice_name: Optional[str] = None,
        language_code: str = "en-US",
        sample_rate_hz: int = 22050,
        retries: int = 2
    ) -> Dict[str, Any]:
        """
        Synthesizes text into speech WAV audio via NVIDIA Resemble AI Chatterbox.
        Uses MD5 content hashing to return cached audio instantly.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for speech synthesis.")

        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            clean_text = text.strip()

        # Limit spoken text to first 600 characters for high responsiveness
        if len(clean_text) > 600:
            clean_text = clean_text[:600] + "..."

        chosen_voice = voice_name or self.default_voice

        # ── Check Audio Cache ──
        cache_key = hashlib.md5(f"{clean_text}_{chosen_voice}_{sample_rate_hz}".encode("utf-8")).hexdigest()
        cached_filename = f"tts_{cache_key}.wav"
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
                "model": "resembleai/chatterbox-multilingual-tts",
                "cached": True,
                "status": "success"
            }

        last_error = None
        for attempt in range(retries):
            try:
                client = self._get_client()
                response = client.synthesize(
                    text=clean_text,
                    voice_name=chosen_voice,
                    language_code=language_code,
                    sample_rate_hz=sample_rate_hz
                )

                audio_data = response.audio
                if not audio_data:
                    raise RuntimeError("NVIDIA Chatterbox returned empty audio bytes.")

                # Write raw PCM data into a valid RIFF/WAV audio container
                with wave.open(cached_path, "wb") as wf:
                    wf.setnchannels(1)                # Mono
                    wf.setsampwidth(2)                # 16-bit PCM (2 bytes per sample)
                    wf.setframerate(sample_rate_hz)   # 22050 Hz
                    wf.writeframes(audio_data)

                size_bytes = os.path.getsize(cached_path)

                return {
                    "filename": cached_filename,
                    "file_path": cached_path,
                    "url": f"/generated/audio/{cached_filename}",
                    "text": clean_text,
                    "voice": chosen_voice,
                    "language_code": language_code,
                    "size_bytes": size_bytes,
                    "model": "resembleai/chatterbox-multilingual-tts",
                    "cached": False,
                    "status": "success"
                }

            except Exception as e:
                last_error = str(e)
                # Reset client cache in case gRPC channel dropped
                self._tts_client = None
                if attempt < retries - 1:
                    time.sleep(0.5)

        raise RuntimeError(f"NVIDIA Chatterbox TTS failed after {retries} attempts: {last_error}")

audio_service = AudioService()
