""""""

Style categories and descriptions for fashion classification.Style categories and descriptions for fashion classification.

This file serves as a single source of truth for all style definitions.This file serves as a single source of truth for all style definitions.

""""""



from typing import Dictfrom typing import Dict



# Style definitions with their descriptions# Style definitions with their descriptions

STYLES: Dict[str, str] = {STYLES: Dict[str, str] = {

    "Urban Streetwear": (    "Urban Streetwear": (

        "Casual streetwear outfit with hoodies, relaxed fit, sneakers, sporty energy."        "Casual streetwear outfit with hoodies, relaxed fit, sneakers, sporty energy."

    ),    ),

    "Formal Business": (    "Formal Business": (

        "Formal business outfit with tailored blazer, collared shirt, suit trousers and dress shoes."        "Formal business outfit with tailored blazer, collared shirt, suit trousers and dress shoes."

    ),    ),

    "Casual Chic": (    "Casual Chic": (

        "Clean modern casual outfit: simple basics styled in a polished way, effortless but intentional."        "Clean modern casual outfit: simple basics styled in a polished way, effortless but intentional."

    ),    ),

    "Sporty / Athleisure": (    "Sporty / Athleisure": (

        "Athletic activewear look: sportswear, gym-ready vibe, performance fabrics, sneakers."        "Athletic activewear look: sportswear, gym-ready vibe, performance fabrics, sneakers."

    ),    ),

    "Vintage / Retro": (    "Vintage / Retro": (

        "Retro vintage outfit using classic cuts, muted or faded colors, thrift-store aesthetic."        "Retro vintage outfit using classic cuts, muted or faded colors, thrift-store aesthetic."

    ),    ),

    "Bohemian": (    "Bohemian": (

        "Boho outfit with loose patterned fabrics, flowy layers and earthy tones."        "Boho outfit with loose patterned fabrics, flowy layers and earthy tones."

    ),    ),

    "Elegant Evening": (    "Elegant Evening": (

        "Refined night-out look with sleek silhouettes, dressy pieces, going-out energy."        "Refined night-out look with sleek silhouettes, dressy pieces, going-out energy."

    ),    ),

    "Preppy": (    "Preppy": (

        "Polished collegiate style: neat, coordinated layers, structured and tidy."        "Polished collegiate style: neat, coordinated layers, structured and tidy."

    ),    ),

    "Punk / Alt": (    "Punk / Alt": (

        "Alternative edgy outfit with darker tones, maybe leather or band tee energy."        "Alternative edgy outfit with darker tones, maybe leather or band tee energy."

    ),    ),

    "Gothic": (    "Gothic": (

        "Dark aesthetic with mostly black clothing and dramatic mood."        "Dark aesthetic with mostly black clothing and dramatic mood."

    ),    ),

    "Artsy / Expressive": (    "Artsy / Expressive": (

        "Creative expressive outfit with bold colors, interesting textures, standout shapes."        "Creative expressive outfit with bold colors, interesting textures, standout shapes."

    ),    ),

}}



# List of style names for easy iteration# List of style names for easy iteration

STYLE_NAMES = list(STYLES.keys())STYLE_NAMES = list(STYLES.keys())

