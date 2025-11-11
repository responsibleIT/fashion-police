"""
Style categories and descriptions for fashion classification.
This file serves as a single source of truth for all style definitions.
"""

from typing import Dict

# Style definitions with their descriptions
STYLES: Dict[str, str] = {
    "Urban Streetwear": (
        "Casual streetwear outfit with hoodies, relaxed fit, sneakers, sporty energy."
    ),
    "Formal Business": (
        "Formal business outfit with tailored blazer, collared shirt, suit trousers and dress shoes."
    ),
    "Casual Chic": (
        "Clean modern casual outfit: simple basics styled in a polished way, effortless but intentional."
    ),
    "Sporty / Athleisure": (
        "Athletic activewear look: sportswear, gym-ready vibe, performance fabrics, sneakers."
    ),
    "Vintage / Retro": (
        "Retro vintage outfit using classic cuts, muted or faded colors, thrift-store aesthetic."
    ),
    "Bohemian": (
        "Boho outfit with loose patterned fabrics, flowy layers and earthy tones."
    ),
    "Elegant Evening": (
        "Refined night-out look with sleek silhouettes, dressy pieces, going-out energy."
    ),
    "Preppy": (
        "Polished collegiate style: neat, coordinated layers, structured and tidy."
    ),
    "Punk / Alt": (
        "Alternative edgy outfit with darker tones, maybe leather or band tee energy."
    ),
    "Gothic": (
        "Dark aesthetic with mostly black clothing and dramatic mood."
    ),
    "Artsy / Expressive": (
        "Creative expressive outfit with bold colors, interesting textures, standout shapes."
    ),
}

# List of style names for easy iteration
STYLE_NAMES = list(STYLES.keys())
