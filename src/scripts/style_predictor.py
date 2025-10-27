from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

class StylePredictor:
    def __init__(self):
        self.model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
        self.processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Predefined style prompts
        self.styles = {
            "Urban Streetwear": "A casual streetwear outfit with sneakers and hoodies.",
            "Formal Business": "A formal outfit with suits, ties, and dress shoes.",
            "Vintage": "A retro, vintage outfit with classic cuts and faded tones.",
            "Bohemian": "A boho-style outfit with loose, patterned fabrics and earthy colors.",
            "Casual Chic": "A simple, modern outfit that's stylish yet relaxed.",
            "Sporty": "An athletic outfit with sportswear and sneakers.",
            "Elegant Evening": "A sophisticated evening outfit with dresses or tuxedos.",
            "Punk Rock": "An edgy outfit with leather jackets, band tees, and bold accessories.",
            "Preppy": "A polished, neat, and traditional style inspired by American East Coast college-prep schools.",
            "Gothic": "A dark, mysterious outfit with black clothing and dramatic accessories.",
            "Artsy": "A creative outfit with bold colors, patterns, and artistic influences."
        }

    def predict(self, image: Image.Image):
        """Return predicted style name, score, and top description."""
        # Encode the image
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_emb = self.model.get_image_features(**inputs)
        image_emb /= image_emb.norm(p=2)

        # Encode style text prompts
        text_inputs = self.processor(
            text=list(self.styles.values()), return_tensors="pt", padding=True
        ).to(self.device)
        with torch.no_grad():
            text_emb = self.model.get_text_features(**text_inputs)
        text_emb /= text_emb.norm(p=2)

        # Compute cosine similarity
        sims = (image_emb @ text_emb.T).squeeze(0)
        best_idx = int(torch.argmax(sims))
        best_style = list(self.styles.keys())[best_idx]
        best_score = float(sims[best_idx].cpu())

        return best_style, best_score, list(self.styles.values())[best_idx]
