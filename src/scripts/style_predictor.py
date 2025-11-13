from __future__ import annotationsfrom __future__ import annotations



from typing import List, Dictfrom typing import List, Dict

import torchimport torch

from PIL import Imagefrom PIL import Image

from transformers import CLIPProcessor, CLIPModelfrom transformers import CLIPProcessor, CLIPModel



import sysfrom data.styles import STYLES

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.styles import STYLESclass StylePredictor:

    def __init__(self):

        # FashionCLIP: CLIP tuned for fashion semantics

class StylePredictor:        self.model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")

    def __init__(self):        self.processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")

        # FashionCLIP: CLIP tuned for fashion semantics

        self.model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")        self.model.to(self.device)



        # Force CPU on Raspberry Pi (no CUDA available)        # Style prompts (your "vibes") - now loaded from central data file

        self.device = "cpu"        self.styles: Dict[str, str] = STYLES

        self.model.to(self.device)

    def _embed_image(self, image: Image.Image) -> torch.Tensor:

        # Style prompts - loaded from central data file        """

        self.styles: Dict[str, str] = STYLES        Return normalized image embedding for the ORIGINAL image.

        We do NOT mask the face before embedding, per your request.

    def _embed_image(self, image: Image.Image) -> torch.Tensor:        """

        """        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        Return normalized image embedding for the ORIGINAL image.        with torch.no_grad():

        We do NOT mask the face before embedding.            img_emb = self.model.get_image_features(**inputs)

        """        img_emb = img_emb / img_emb.norm(p=2, dim=-1, keepdim=True)

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)        return img_emb  # shape (1, D)

        with torch.no_grad():

            img_emb = self.model.get_image_features(**inputs)    def _embed_text_list(self, texts: List[str]) -> torch.Tensor:

        img_emb = img_emb / img_emb.norm(p=2, dim=-1, keepdim=True)        """

        return img_emb  # shape (1, D)        Return normalized text embeddings for style descriptions.

        """

    def _embed_text_list(self, texts: List[str]) -> torch.Tensor:        text_inputs = self.processor(

        """            text=texts, return_tensors="pt", padding=True

        Return normalized text embeddings for style descriptions.        ).to(self.device)

        """        with torch.no_grad():

        text_inputs = self.processor(            txt_emb = self.model.get_text_features(**text_inputs)

            text=texts, return_tensors="pt", padding=True        txt_emb = txt_emb / txt_emb.norm(p=2, dim=-1, keepdim=True)

        ).to(self.device)        return txt_emb  # shape (N, D)

        with torch.no_grad():

            txt_emb = self.model.get_text_features(**text_inputs)    def predict(self, original_image: Image.Image) -> List[Dict[str, float]]:

        txt_emb = txt_emb / txt_emb.norm(p=2, dim=-1, keepdim=True)        """

        return txt_emb  # shape (N, D)        Compare the ORIGINAL image with each style description.

        Return a ranked list of style candidates.

    def predict(self, original_image: Image.Image) -> List[Dict[str, float]]:

        """        Output format:

        Compare the ORIGINAL image with each style description.        [

        Return a ranked list of style candidates.          {"name": "Urban Streetwear", "score": 0.82, "desc": "Casual streetwear outfit ..."},

          {"name": "Casual Chic", "score": 0.77, "desc": "Clean modern casual outfit ..."},

        Output format:          ...

        [        ]

          {"name": "Urban Streetwear", "score": 0.82, "desc": "Casual streetwear outfit ..."},        """

          {"name": "Casual Chic", "score": 0.77, "desc": "Clean modern casual outfit ..."},        # 1. Embed the outfit photo (original, unmasked)

          ...        img_emb = self._embed_image(original_image)

        ]

        """        # 2. Embed each style description

        # 1. Embed the outfit photo (original, unmasked)        style_texts = list(self.styles.values())

        img_emb = self._embed_image(original_image)        style_names = list(self.styles.keys())

        text_emb = self._embed_text_list(style_texts)  # (N, D)

        # 2. Embed each style description

        style_texts = list(self.styles.values())        # 3. Cosine similarity = dot product because both are normalized

        style_names = list(self.styles.keys())        sims = (img_emb @ text_emb.T).squeeze(0).detach().cpu()  # shape (N,)

        text_emb = self._embed_text_list(style_texts)  # (N, D)

        # 4. Build ranked list

        # 3. Cosine similarity = dot product because both are normalized        ranked = []

        sims = (img_emb @ text_emb.T).squeeze(0).detach().cpu()  # shape (N,)        for i, name in enumerate(style_names):

            ranked.append({

        # 4. Build ranked list                "name": name,

        ranked = []                "score": float(sims[i]),      # similarity strength

        for i, name in enumerate(style_names):                "desc": self.styles[name],    # keep description for UI

            ranked.append({            })

                "name": name,

                "score": float(sims[i]),      # similarity strength        ranked.sort(key=lambda x: x["score"], reverse=True)

                "desc": self.styles[name],    # keep description for UI        return ranked

            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
