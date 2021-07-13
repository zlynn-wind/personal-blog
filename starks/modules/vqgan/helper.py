from random import choice


STYLES = (
    "UKIYO-E",
    "Rococo",
    "Pop art",
    "Color Field Painting",
    "Vintage",
    "Unreal Engine",
    "Cartoon",
    "Cubism",
    "Ghibli",
    "Traditonal Chinese Painting",
    "Pixel art",
    "Vintage vaporwave",
    "Peking Opera",
    "Edvard Munch",
    "Pierre Auguste Cot"
    "Salvador dali",
    "Thomas Kinkade",
    "Monet",
    "Henri Matisse",
    "Camille Deschiens",
    "Alex Andreyev",
    "Leica Camera",
    "Nan Goldin",
    "Eric Rohmer",
    "Jia Zhangke director style",
)


def get_random_style():
    return choice(STYLES)
