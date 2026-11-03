import os
import base64
import uuid
import time
import requests
from typing import Dict, Any, Optional
from app.core.config import settings

class ImageService:
    """
    Dedicated Service for Image Generation using NVIDIA FLUX 3 Image Klein.
    Does not use Gemini for generation — purely powered by NVIDIA FLUX 3.
    """
    def __init__(self):
        self.nvidia_key = settings.NVIDIA_API_KEY
        self.nvidia_url = settings.NVIDIA_FLUX_URL
        self.generated_dir = os.path.join(settings.GENERATED_DIR, "images")
        os.makedirs(self.generated_dir, exist_ok=True)

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024, retries: int = 2) -> Dict[str, Any]:
        """
        Generates a photorealistic image directly from a text prompt using NVIDIA FLUX 3 Image Klein.
        Saves the resulting image locally in generated/images/ and returns metadata.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty for image generation.")

        headers = {
            "Authorization": f"Bearer {self.nvidia_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt.strip(),
            "mode": "t2i"
        }

        last_error = None
        for attempt in range(retries):
            try:
                response = requests.post(self.nvidia_url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    artifacts = data.get("artifacts", [])
                    if artifacts:
                        first_art = artifacts[0]
                        finish_reason = first_art.get("finishReason")

                        if finish_reason == "CONTENT_FILTERED":
                            raise ValueError("Prompt or output was filtered by NVIDIA safety guardrails. Please adjust your prompt.")

                        b64_content = first_art.get("base64")
                        if b64_content:
                            image_data = base64.b64decode(b64_content)

                            # Save generated image locally
                            filename = f"gen_{uuid.uuid4().hex[:12]}.jpg"
                            file_path = os.path.join(self.generated_dir, filename)
                            with open(file_path, "wb") as f:
                                f.write(image_data)

                            return {
                                "filename": filename,
                                "file_path": file_path,
                                "url": f"/generated/images/{filename}",
                                "original_prompt": prompt,
                                "enhanced_prompt": prompt,
                                "width": width,
                                "height": height,
                                "size_bytes": len(image_data),
                                "finish_reason": finish_reason
                            }
                    last_error = f"NVIDIA returned no valid artifacts: {data}"
                elif response.status_code in (429, 503, 504):
                    last_error = f"NVIDIA busy/rate-limited ({response.status_code}): {response.text[:150]}"
                else:
                    last_error = f"NVIDIA error ({response.status_code}): {response.text[:200]}"
            except ValueError:
                # Content filter errors should raise directly without retrying
                raise
            except Exception as e:
                last_error = str(e)

            if attempt < retries - 1:
                time.sleep(3)

        raise RuntimeError(f"NVIDIA FLUX 3 image generation failed after {retries} attempts: {last_error}")

image_service = ImageService()
