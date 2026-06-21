"""Pictogram helper functions and mappings for Météo-Grenoble.com."""

PICTO_TO_CONDITION = {
    1: "sunny",             # Ciel clair - quasiment pas de nuages et un soleil omniprésent
    2: "partlycloudy",      # Ciel peu nuageux - le soleil domine largement
    3: "partlycloudy",      # Ciel nuageux - les éclaircies et les nuages se partagent le ciel - pas de pluie
    4: "cloudy",            # Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie
    5: "rainy",             # Risque de quelques averses de pluie, faibles à modérées
    6: "pouring",           # Fréquentes averses de pluie, souvent fortes
    7: "snowy-rainy",       # Risque d'averses de pluie et neige ou neige fondue ou neige et grésil ne tenant généralement pas au sol...
    8: "snowy",             # Risque de quelques averses de neige, faibles ou modérées
    9: "snowy",             # Fréquentes averses de neige, souvent fortes...
    11: "lightning-rainy",  # Orage ponctuel éclatant...
    12: "lightning-rainy",  # Temps très instable avec de fortes et fréquentes averses orageuses
    13: "sunny",            # Temps sec mais risque de plaques de verglas se formant sur les chaussées
    14: "cloudy",           # Ciel couvert - le soleil est totalement absent mais le temps est sec ou le risque de pluies est limité
    15: "rainy",            # Pluies faibles ou bruines - intermittentes ou persistantes - le parapluie est généralement nécessaire
    16: "pouring",          # Pluies fortes et persistantes - les vêtements de pluie sont absolument nécessaires...
    17: "rainy",            # Pluies verglaçantes : la pluie gèle au contact de tous les objets...
    18: "snowy-rainy",      # Pluies et neige mêlées...
    19: "snowy",            # Neige faible - intermittente ou persistante...
    20: "snowy",            # Neige forte et persistante - elle tient au sol...
    21: "fog",              # Nuages bas ou brouillard - visibilité généralement réduite à moins de 1 km...
    22: "lightning-rainy",  # Fortes pluies orageuses dans un ciel totalement couvert
    23: "clear-night",      # Ciel dégagé - quasiment pas de nuages (nuit)
    24: "partlycloudy",     # Ciel peu nuageux - les éclaircies dominent largement (nuit)
    25: "partlycloudy",     # Ciel nuageux - les éclaircies et les nuages se partagent le ciel - pas de pluie (nuit)
    26: "cloudy",           # Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie (nuit)
    27: "rainy",            # Risque de quelques averses de pluie, faibles à modérées (nuit)
    28: "pouring",          # Fréquentes averses de pluie, souvent fortes (nuit)
    29: "snowy-rainy",      # Risque d'averses de pluie et neige ou neige fondue ou neige et grésil... (nuit)
    30: "snowy",            # Risque de quelques averses de neige, faibles ou modérées (nuit)
    31: "snowy",            # Fréquentes averses de neige, souvent fortes... (nuit)
    33: "lightning-rainy",  # Orage ponctuel éclatant... (nuit)
    34: "lightning-rainy",  # Temps très instable avec de fortes et fréquentes averses orageuses (nuit)
    40: "partlycloudy",     # Ciel voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil
    41: "partlycloudy",     # Ciel assez nuageux - les nuages l'emportent, mais quelques belles éclaircies sont possibles
    42: "partlycloudy",     # Ciel voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil (nuit)
    43: "partlycloudy",     # Ciel assez nuageux - les nuages l'emportent, mais quelques belles éclaircies sont possibles (nuit)
    44: "partlycloudy",     # Ciel légèrement voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil
    45: "partlycloudy",     # Ciel légèrement voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil (nuit)
}

PICTO_TO_DESCRIPTION = {
    1: "Ciel clair - quasiment pas de nuages et un soleil omniprésent",
    2: "Ciel peu nuageux - le soleil domine largement",
    3: "Ciel nuageux - les éclaircies et les nuages se partagent le ciel - pas de pluie",
    4: "Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie",
    5: "Risque de quelques averses de pluie, faibles à modérées",
    6: "Fréquentes averses de pluie, souvent fortes",
    7: "Risque d'averses de pluie et neige ou neige fondue ou neige et grésil ne tenant généralement pas au sol ou très temporairement",
    8: "Risque de quelques averses de neige, faibles ou modérées",
    9: "Fréquentes averses de neige, souvent fortes et tenant au moins temporairement au sol si la température descend en dessous de +1°C",
    11: "Orage ponctuel éclatant alors que le ciel est seulement nuageux (parsemé d'éclaircies) - le risque est modéré",
    12: "Temps très instable avec de fortes et fréquentes averses orageuses - le risque est important",
    13: "Temps sec mais risque de plaques de verglas se formant sur les chaussées",
    14: "Ciel couvert - le soleil est totalement absent mais le temps est sec ou le risque de pluies est limité",
    15: "Pluies faibles ou bruines - intermittentes ou persistantes - le parapluie est généralement nécessaire",
    16: "Pluies fortes et persistantes - les vêtements de pluie sont absolument nécessaires - conditions météo difficiles - la visibilité peut être réduite",
    17: "Pluies verglaçantes : la pluie gèle au contact de tous les objets - ATTENTION car les chaussées peuvent se transformer en patinoire !",
    18: "Pluies et neige mêlées ou pluie suivie de neige ou neige suivie de pluie",
    19: "Neige faible - intermittente ou persistante - cette neige peut tenir au sol si la température est suffisamment basse",
    20: "Neige forte et persistante - elle tient au sol - conditions météo difficiles - la visibilité peut être réduite",
    21: "Nuages bas ou brouillard - visibilité généralement réduite à moins de 1 km et rendant la circulation dangereuse",
    22: "Fortes pluies orageuses dans un ciel totalement couvert - le risque est maximum",
    23: "Ciel dégagé - quasiment pas de nuages",
    24: "Ciel peu nuageux - les éclaircies dominent largement",
    25: "Ciel nuageux - les éclaircies et les nuages se partagent le ciel - pas de pluie",
    26: "Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie",
    27: "Risque de quelques averses de pluie, faibles à modérées",
    28: "Fréquentes averses de pluie, souvent fortes",
    29: "Risque d'averses de pluie et neige ou neige fondue ou neige et grésil ne tenant généralement pas au sol ou très temporairement",
    30: "Risque de quelques averses de neige, faibles ou modérées",
    31: "Fréquentes averses de neige, souvent fortes et tenant au moins temporairement au sol si la température descend en dessous de +1°C",
    33: "Orage ponctuel éclatant alors que le ciel est seulement nuageux (parsemé d'éclaircies) - le risque est modéré",
    34: "Temps très instable avec de fortes et fréquentes averses orageuses - le risque est important",
    40: "Ciel voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil",
    41: "Ciel assez nuageux - les nuages l'emportent, mais quelques belles éclaircies sont possibles",
    42: "Ciel voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil",
    43: "Ciel assez nuageux - les nuages l'emportent, mais quelques belles éclaircies sont possibles",
    44: "Ciel légèrement voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil",
    45: "Ciel légèrement voilé par des nuages d'altitude, ternissant plus ou moins l'éclat du soleil",
}


def map_picto_to_condition(picto: int | None) -> str:
    """Map the website's picto code to a standard Home Assistant weather condition."""
    if picto is None:
        return "cloudy"
    return PICTO_TO_CONDITION.get(picto, "cloudy")


def map_picto_to_description(picto: int | None) -> str | None:
    """Map the website's picto code to its descriptive meaning."""
    if picto is None:
        return None
    return PICTO_TO_DESCRIPTION.get(picto)
