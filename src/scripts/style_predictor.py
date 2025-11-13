from __future__ import annotations
from typing import List, Dict
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from ..data.styles import STYLES

class StylePredictor:
    _model: CLIPModel | None = None
    _processor: CLIPProcessor | None = None
    
    def __init__(self) -> None:
        self._ensure_loaded()
    
    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._model is None or cls._processor is None:
            cls._model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
            cls._processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")
            cls._model = cls._model.to("cpu")
            cls._model.eval()
    
    def _embed_image(self, image: Image.Image) -> torch.Tensor:
        inputs = self._processor(images=image, return_tensors="pt").to("cpu")
        with torch.no_grad():
            image_features = self._model.get_image_features(**inputs)
        return image_features / image_features.norm(dim=-1, keepdim=True)
    
    def _embed_text_list(self, text_list: List[str]) -> torch.Tensor:
        inputs = self._processor(text=text_list, return_tensors="pt", padding=True).to("cpu")
        with torch.no_grad():
            text_features = self._model.get_text_features(**inputs)
        return text_features / text_features.norm(dim=-1, keepdim=True)
    
    def predict(self, image: Image.Image) -> List[Dict]:
        image_embed = self._embed_image(image)
        style_names = list(STYLES.keys())
        style_prompts = [STYLES[name]["description"] for name in style_names]
        text_embeds = self._embed_text_list(style_prompts)
        similarities = (image_embed @ text_embeds.T).squeeze(0)
        scores = torch.softmax(similarities * 100, dim=0).cpu().numpy()
        results = [
            {"name": style_names[i], "score": float(scores[i]), "description": STYLES[style_names[i]]["description"]}
            for i in range(len(style_names))
        ]
        return sorted(results, key=lambda x: x["score"], reverse=True)
