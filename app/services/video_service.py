import os
import shutil
import uuid
import time
from typing import Dict, Any, Optional
from gradio_client import Client
from app.core.config import settings

class VideoService:
    """
    Video AI Service powered by Lightricks LTX-Video:
    - Text-to-Video generation (704x512 resolution, 2-second clips)
    - Output saved locally to generated/videos/
    """
    def __init__(self):
        self.hf_token = settings.HUGGINGFACE_API_KEY
        self.model_id = settings.HF_VIDEO_MODEL or "Lightricks/ltx-video-distilled"
        self.generated_dir = os.path.join(settings.GENERATED_DIR, "videos")
        os.makedirs(self.generated_dir, exist_ok=True)
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        if self._client is None:
            self._client = Client(self.model_id, token=self.hf_token)
        return self._client

    def generate_video(self, prompt: str, seed: int = -1, retries: int = 2) -> Dict[str, Any]:
        """
        Generates a video clip from a text prompt using LTX-Video (or fallback Drishya-Tiny).
        """
        clean_prompt = prompt.strip() if prompt else ""
        if not clean_prompt:
            raise ValueError("Prompt cannot be empty for video generation.")

        last_error = None
        for attempt in range(retries):
            try:
                client = self._get_client()

                # Check if model is LTX-Video
                if "ltx-video" in self.model_id.lower():
                    # LTX-Video Distilled endpoint
                    res = client.predict(
                        prompt=clean_prompt,
                        negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted",
                        input_image_filepath=None,
                        input_video_filepath=None,
                        height_ui=512,
                        width_ui=704,
                        mode="text-to-video",
                        duration_ui=2,
                        ui_frames_to_use=9,
                        seed_ui=seed if seed >= 0 else 42,
                        randomize_seed=(seed < 0),
                        ui_guidance_scale=1,
                        improve_texture_flag=True,
                        api_name="/text_to_video"
                    )

                    # Extract video file path from result tuple
                    if isinstance(res, (tuple, list)):
                        video_obj = res[0]
                        temp_video_path = video_obj.get("video") if isinstance(video_obj, dict) else str(video_obj)
                    elif isinstance(res, dict):
                        temp_video_path = res.get("video")
                    else:
                        temp_video_path = str(res)

                else:
                    # Generic Drishya-Tiny endpoint
                    temp_video_path = client.predict(
                        prompt=clean_prompt,
                        seed=seed,
                        api_name="/generate_video"
                    )

                if not temp_video_path or not os.path.exists(temp_video_path):
                    raise RuntimeError(f"Video file not found at returned path: {temp_video_path}")

                # Copy generated mp4 to project generated/videos directory
                filename = f"vid_{uuid.uuid4().hex[:12]}.mp4"
                dest_path = os.path.join(self.generated_dir, filename)
                shutil.copyfile(temp_video_path, dest_path)

                size_bytes = os.path.getsize(dest_path)

                return {
                    "filename": filename,
                    "file_path": dest_path,
                    "url": f"/generated/videos/{filename}",
                    "prompt": clean_prompt,
                    "model": "Lightricks/LTX-Video-0.9.1",
                    "width": 704,
                    "height": 512,
                    "size_bytes": size_bytes,
                    "duration_seconds": 2.0,
                    "status": "success"
                }

            except Exception as e:
                last_error = str(e)
                # Reset client cache on connection drop
                self._client = None
                if attempt < retries - 1:
                    time.sleep(2)

        raise RuntimeError(f"Video generation failed after {retries} attempts: {last_error}")

video_service = VideoService()
