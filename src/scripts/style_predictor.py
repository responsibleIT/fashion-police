from __future__ import annotations

from typing import List, Dict
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

from data.styles import STYLES


class StylePredictor:
    def __init__(self):
        # FashionCLIP: CLIP tuned for fashion semantics
        self.model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
        self.processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Style prompts (your "vibes") - now loaded from central data file
        self.styles: Dict[str, str] = STYLES

    def _embed_image(self, image: Image.Image) -> torch.Tensor:
        """
        Return normalized image embedding for the ORIGINAL image.
        We do NOT mask the face before embedding, per your request.
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            img_emb = self.model.get_image_features(**inputs)
        img_emb = img_emb / img_emb.norm(p=2, dim=-1, keepdim=True)
        return img_emb  # shape (1, D)

    def _embed_text_list(self, texts: List[str]) -> torch.Tensor:
        """
        Return normalized text embeddings for style descriptions.
        """
        text_inputs = self.processor(
            text=texts, return_tensors="pt", padding=True
        ).to(self.device)
        with torch.no_grad():
            txt_emb = self.model.get_text_features(**text_inputs)
        txt_emb = txt_emb / txt_emb.norm(p=2, dim=-1, keepdim=True)
        return txt_emb  # shape (N, D)

    def predict(self, original_image: Image.Image) -> List[Dict[str, float]]:
        """
        Compare the ORIGINAL image with each style description.
        Return a ranked list of style candidates.

        Output format:
        [
          {"name": "Urban Streetwear", "score": 0.82, "desc": "Casual streetwear outfit ..."},
          {"name": "Casual Chic", "score": 0.77, "desc": "Clean modern casual outfit ..."},
          ...
        ]
        """
        # 1. Embed the outfit photo (original, unmasked)
        img_emb = self._embed_image(original_image)

        # 2. Embed each style description
        style_texts = list(self.styles.values())
        style_names = list(self.styles.keys())
        text_emb = self._embed_text_list(style_texts)  # (N, D)

        # 3. Cosine similarity = dot product because both are normalized
        sims = (img_emb @ text_emb.T).squeeze(0).detach().cpu()  # shape (N,)

        # 4. Build ranked list
        ranked = []
        for i, name in enumerate(style_names):
            ranked.append({
                "name": name,
                "score": float(sims[i]),      # similarity strength
                "desc": self.styles[name],    # keep description for UI
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
