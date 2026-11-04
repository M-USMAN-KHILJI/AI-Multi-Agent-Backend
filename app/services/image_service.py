import os
import base64
import uuid
import time
import requests
from typing import Dict, Any, Optional
from app.core.config import settings

class ImageService:
    """
    Multimodal Image Service:
    1. Visual Understanding & Q&A: NVIDIA Multimodal Vision (Google PaliGemma)
    2. Image Generation & Visual Editing: NVIDIA FLUX 3 Image Klein
    """
    def __init__(self):
        # NVIDIA FLUX 3 (Generation & Synthesis)
        self.nvidia_key = settings.NVIDIA_API_KEY
        self.nvidia_url = settings.NVIDIA_FLUX_URL
        
        # NVIDIA Vision (Image-to-Text / Multimodal VQA)
        self.vision_key = settings.NVIDIA_VISION_API_KEY
        self.vision_url = settings.NVIDIA_VISION_URL
        self.vision_model = settings.NVIDIA_VISION_MODEL

        self.generated_dir = os.path.join(settings.GENERATED_DIR, "images")
        os.makedirs(self.generated_dir, exist_ok=True)

    def analyze_image(self, prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg", retries: int = 2) -> str:
        """
        Analyzes an uploaded image, describes what it is, and answers questions using Google PaliGemma VLM.
        """
        if not image_bytes:
            raise ValueError("No image provided for visual analysis.")

        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64_image}"

        headers = {
            "Authorization": f"Bearer {self.vision_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        user_text = prompt.strip() if prompt and prompt.strip() else ""

        # Google PaliGemma format (HTML <img> tag + task prefix)
        if "paligemma" in self.vision_url.lower() or "paligemma" in self.vision_model.lower():
            lower_text = user_text.lower()
            if lower_text and any(lower_text.startswith(w) for w in ["is ", "are ", "what ", "who ", "where ", "how ", "can ", "does "]) or lower_text.endswith("?"):
                vlm_prompt = f"answer en {user_text} <img src=\"{data_uri}\" />"
            elif user_text and user_text not in ["describe what is in this image in detail.", "identify and describe what is in this image in detail.", "inspect this image in detail and describe what you see."]:
                vlm_prompt = f"caption en\n{user_text} <img src=\"{data_uri}\" />"
            else:
                vlm_prompt = f"caption en\nDescribe all objects and their positions <img src=\"{data_uri}\" />"

            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": vlm_prompt
                    }
                ],
                "max_tokens": 512,
                "temperature": 0.2
            }
        else:
            # Standard OpenAI chat completions vision format (fallback)
            fallback_text = user_text or "Identify and describe what is in this image in detail."
            payload = {
                "model": self.vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": fallback_text},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ],
                "max_tokens": 512,
                "temperature": 0.2
            }

        last_error = None
        for attempt in range(retries):
            try:
                response = requests.post(self.vision_url, headers=headers, json=payload, timeout=45)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        msg = choices[0]["message"]
                        text = msg.get("content") or msg.get("reasoning_content") or ""
                        if text.strip():
                            return text.strip()
                    return "Visual inspection completed, but no text output was generated."
                elif response.status_code in (429, 503, 504):
                    last_error = f"NVIDIA Vision busy/rate-limited ({response.status_code}): {response.text[:150]}"
                else:
                    last_error = f"NVIDIA Vision error ({response.status_code}): {response.text[:200]}"
            except Exception as e:
                last_error = str(e)

            if attempt < retries - 1:
                time.sleep(2)

        raise RuntimeError(f"Visual analysis failed after {retries} attempts: {last_error}")

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024, retries: int = 2) -> Dict[str, Any]:
        """
        Generates or modifies a photorealistic image from a text prompt using NVIDIA FLUX 3 Image Klein.
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
                raise
            except Exception as e:
                last_error = str(e)

            if attempt < retries - 1:
                time.sleep(3)

        raise RuntimeError(f"NVIDIA FLUX 3 image generation failed after {retries} attempts: {last_error}")

    def edit_image_with_prompt(self, user_instruction: str, original_image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Multimodal Editing Pipeline:
        1. Analyzes the original image via NVIDIA Vision to understand all subjects, colors, layout, and context.
        2. Merges user edit instructions into a comprehensive generation prompt preserving original context.
        3. Synthesizes the modified/edited image via NVIDIA FLUX 3 Image Klein.
        """
        # Step 1: Understand the original image
        description = self.analyze_image(
            prompt="Describe all visual elements, main subject, colors, lighting, and composition of this image concisely in 2 sentences.",
            image_bytes=original_image_bytes,
            mime_type=mime_type
        )

        # Step 2: Formulate the coherent edit prompt
        combined_edit_prompt = (
            f"Based on an original image depicting: {description}. "
            f"Apply the following modifications and changes requested by the user: {user_instruction}. "
            f"Maintain cohesive style, realistic lighting, and high visual quality."
        )

        # Step 3: Generate the modified image via FLUX 3 Klein
        gen_result = self.generate_image(prompt=combined_edit_prompt)
        gen_result["original_image_description"] = description
        gen_result["edit_instruction"] = user_instruction
        return gen_result

image_service = ImageService()
