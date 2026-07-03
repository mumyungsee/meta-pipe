"""
Step 4: 섬네일 이미지 생성
- 1차 시도: HuggingFace Inference API (서버 사이드 — 다운로드 불필요)
- 2차 fallback: 로컬 diffusers (모델 다운로드 필요)
"""

import os
import json
from pathlib import Path

STEP_DIR = Path(__file__).parent
PROMPT_FILE = STEP_DIR.parent / "step-3" / "prompt.json"
OUTPUT_FILE = STEP_DIR / "raw_image.png"
TARGET_WIDTH, TARGET_HEIGHT = 1280, 720

def load_prompt():
    with open(PROMPT_FILE) as f:
        return json.load(f)

def try_hf_inference_api(prompt_data):
    """HuggingFace Inference API 시도 (토큰 없이도 public 모델 가능)"""
    from huggingface_hub import InferenceClient

    token = os.environ.get("HF_TOKEN")
    client = InferenceClient(
        model="stabilityai/stable-diffusion-xl-base-1.0",
        token=token
    )

    print("HF Inference API로 이미지 생성 중...")
    image = client.text_to_image(
        prompt=prompt_data["positive_prompt"],
        negative_prompt=prompt_data["negative_prompt"],
        width=1024,
        height=576,
    )
    return image

def resize_to_target(image):
    """1280x720으로 리사이즈"""
    from PIL import Image
    return image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

def main():
    prompt_data = load_prompt()

    # 1차: HF Inference API
    try:
        image = try_hf_inference_api(prompt_data)
        image = resize_to_target(image)
        image.save(OUTPUT_FILE, "PNG")
        print(f"완료 (HF Inference API): {OUTPUT_FILE}")
        print(f"해상도: {image.size}")
        return True
    except Exception as e:
        print(f"HF Inference API 실패: {e}")

    # 2차 fallback: 로컬 diffusers
    print("로컬 diffusers fallback 시도 중... (시간 소요)")
    try:
        import torch
        from diffusers import AutoPipelineForText2Image

        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float32,
        )
        pipe.load_lora_weights(
            "itzzdeep/youtube-thumbnails-sdxl-lora-v3",
            weight_name="youtube-thumbnails-sdxl-lora-v3.safetensors"
        )

        generator = torch.Generator().manual_seed(prompt_data.get("seed", 42))
        result = pipe(
            prompt=prompt_data["positive_prompt"],
            negative_prompt=prompt_data["negative_prompt"],
            cross_attention_kwargs={"scale": prompt_data.get("lora_scale", 0.8)},
            generator=generator,
            width=1024,
            height=576,
            num_inference_steps=20,
        )
        image = result.images[0]
        image = resize_to_target(image)
        image.save(OUTPUT_FILE, "PNG")
        print(f"완료 (로컬 diffusers): {OUTPUT_FILE}")
        print(f"해상도: {image.size}")
        return True
    except Exception as e:
        print(f"로컬 diffusers 실패: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
