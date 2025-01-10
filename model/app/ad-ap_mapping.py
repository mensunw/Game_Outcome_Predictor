champion_ad_ap_mapping = {
    1: (0.05, 0.95),  # Annie - Pure AP mage
    2: (0.1, 0.9),    # Olaf - Primarily AD with physical-damage-based kit
    3: (0.1, 0.9),    # Galio - AP tank with strong magic-damage focus
    4: (0.3, 0.7),    # Twisted Fate - Magic damage with strong AP scaling
    5: (0.9, 0.1),    # Xin Zhao - Primarily AD bruiser
    6: (0.8, 0.2),    # Urgot - AD bruiser with some AP flexibility
    7: (0.1, 0.9),    # LeBlanc - AP mage/assassin
    8: (0.05, 0.95),    # Vladimir - Pure AP mage
    9: (0.1, 0.9),    # Fiddlesticks - AP mage/jungle
    10: (0.4, 0.6),   # Kayle - Hybrid scaling, strong late-game AP focus
    11: (0.9, 0.1),   # Master Yi - AD assassin/duelist
    12: (0.2, 0.8),   # Alistar - AP-heavy due to abilities scaling with magic damage
    13: (0.1, 0.9),   # Ryze - AP mage with scaling damage
    14: (0.8, 0.2),   # Sion - Primarily AD tank
    15: (0.9, 0.1), # Sivir - Physical-damage ADC
    16: (0.1, 0.9),   # Soraka - Utility/AP support
    17: (0.2, 0.8),   # Teemo - Magic-damage focused
    18: (0.9, 0.1),   # Tristana - Primarily AD with some AP flexibility
    19: (0.3, 0.7),   # Warwick - AP-focused jungle/tank
    20: (0.1, 0.9),   # Nunu - AP tank with magic-damage scaling
    21: (0.85, 0.15), # Miss Fortune - Physical-damage ADC
    22: (0.9, 0.1), # Ashe - Pure AD carry with physical-damage focus
    23: (0.9, 0.1),   # Tryndamere - Primarily AD duelist
    24: (0.7, 0.3),   # Jax - Hybrid bruiser, leans AD
    25: (0.05, 0.95),   # Morgana - AP mage/support
    26: (0.05, 0.95),   # Zilean - AP utility/support
    27: (0.05, 0.95),   # Singed - AP tank
    28: (0.1, 0.9),   # Evelynn - AP assassin
    29: (0.8, 0.2),   # Twitch - Physical-damage ADC
    30: (0.05, 0.95),   # Karthus - Pure AP mage
    31: (0.1, 0.9),   # Cho'Gath - Mostly magic damage with AP scaling
    32: (0.1, 0.9),   # Amumu - Mostly magic damage, tank with AP scaling
    33: (0.1, 0.9),   # Rammus - AP tank with magic damage
    34: (0.05, 0.95),   # Anivia - AP mage
    35: (0.65, 0.35),   # Shaco - AD assassin, AP possible
    36: (0.7, 0.3),   # Dr. Mundo - Primarily AD-based tank
    37: (0.05, 0.95),   # Sona - AP utility support
    38: (0.4, 0.6),   # Kassadin - Hybrid scaling, leans AP
    39: (0.85, 0.15), # Irelia - Primarily AD but can itemize for AP flexibility
    40: (0.05, 0.95),   # Janna - Pure utility with magic damage
    41: (0.9, 0.1),   # Gangplank - Primarily AD bruiser
    42: (0.65, 0.35),   # Corki - Hybrid ADC with mixed damage
    43: (0.05, 0.95),   # Karma - Support mage, mostly magic damage
    44: (0.1, 0.9),   # Taric - AP support/tank
    45: (0.05, 0.95),   # Veigar - Pure AP mage
    48: (0.85, 0.15), # Trundle - AD bruiser with physical damage focus
    50: (0.1, 0.9),   # Swain - AP bruiser/mage
    51: (0.95, 0.05), # Caitlyn - Physical-damage-focused ADC
    53: (0.1, 0.9),   # Blitzcrank - AP tank/support
    54: (0.3, 0.7),   # Malphite - Primarily AP tank
    55: (0.35, 0.65),   # Katarina - AP assassin
    56: (0.9, 0.1),   # Nocturne - AD assassin
    57: (0.1, 0.9),   # Maokai - AP tank
    58: (0.9, 0.1),   # Renekton - AD bruiser
    59: (0.8, 0.2),   # Jarvan IV - AD bruiser/tank
    60: (0.05, 0.95),   # Elise - Hybrid AP bruiser
    61: (0.15, 0.85),   # Orianna - AP mage
    62: (0.9, 0.1),   # Wukong - AD bruiser
    63: (0.05, 0.95),   # Brand - Pure magic damage dealer with strong AP scaling
    64: (0.85, 0.15),   # Lee Sin - Primarily AD-focused
    67: (0.95, 0.05), # Vayne - Pure AD carry with true damage scaling (ignored here)
    68: (0.05, 0.95),   # Rumble - AP bruiser
    69: (0.05, 0.95),   # Cassiopeia - AP-focused mage with all magic damage
    72: (0.7, 0.3),   # Skarner - Hybrid tank, leans AP
    74: (0.05, 0.95),   # Heimerdinger - Pure AP mage
    75: (0.8, 0.2),   # Nasus - Primarily AD bruiser
    76: (0.1, 0.9),   # Nidalee - Hybrid assassin/mage, leans AP
    77: (0.6, 0.4),   # Udyr - Hybrid bruiser; depends on stance, leans AD
    78: (0.8, 0.2),   # Poppy - AD tank
    79: (0.05, 0.95),   # Gragas - AP bruiser
    80: (0.95, 0.05),   # Pantheon - Primarily AD
    81: (0.6, 0.4),   # Ezreal - Flexible ADC, leans slightly AD but AP is viable
    82: (0.1, 0.9),   # Mordekaiser - AP bruiser
    83: (0.9, 0.1),   # Yorick - AD bruiser
    84: (0.1, 0.9),   # Akali - Hybrid assassin, leans slightly AP due to her abilities
    85: (0.05, 0.95),   # Kennen - AP mage/utility
    86: (0.9, 0.1),   # Garen - AD tank/duelist
    89: (0.1, 0.9),   # Leona - AP tank/support
    90: (0.05, 0.95),   # Malzahar - AP mage
    91: (0.95, 0.05), # Talon
    92: (0.9, 0.1), # Riven
    96: (0.7, 0.3),   # Kog'Maw - Primarily AD, some AP flexibility
    98: (0.8, 0.2),   # Shen - AP tank with scaling
    99: (0.05, 0.95),   # Lux - AP mage/support
    101: (0.05, 0.95),  # Xerath - Pure AP mage
    102: (0.3, 0.7),  # Shyvana - Hybrid bruiser, leans AD
    103: (0.1, 0.9),  # Ahri - AP mage/assassin
    104: (0.9, 0.1),  # Graves - AD bruiser
    105: (0.15, 0.85),  # Fizz - AP assassin
    106: (0.4, 0.6),  # Volibear - Primarily AD bruiser
    107: (0.9, 0.1),  # Rengar - AD assassin
    110: (0.70, 0.3),  # Varus - Primarily AD, some AP flexibility
    111: (0.1, 0.9),  # Nautilus - AP tank
    112: (0.05, 0.95),  # Viktor - Pure AP mage
    113: (0.2, 0.8),  # Sejuani - AP tank with scaling
    114: (0.9, 0.1),  # Fiora - AD duelist
    115: (0.05, 0.95),  # Ziggs - Pure AP mage
    117: (0.1, 0.9),  # Lulu - AP utility/support
    119: (0.95, 0.05),# Draven - Pure AD carry
    120: (0.8, 0.2),  # Hecarim - Primarily AD bruiser
    121: (0.9, 0.1),  # Kha'Zix - AD assassin
    122: (0.9, 0.1),  # Darius - AD bruiser
    126: (0.85, 0.15),  # Jayce - Hybrid bruiser, leans AD
    127: (0.05, 0.95),  # Lissandra - AP mage
    131: (0.1, 0.9),  # Diana - AP bruiser
    133: (0.9, 0.1),  # Quinn - AD duelist
    134: (0.05, 0.95),  # Syndra - Pure AP mage
    136: (0.05, 0.95),  # Aurelion Sol - AP mage
    141: (0.9, 0.1),  # Kayn - AD assassin/duelist
    142: (0.05, 0.95),  # Zoe - Pure AP mage
    143: (0.05, 0.95),  # Zyra - AP mage/support
    145: (0.6, 0.4),  # Kai'Sa - Primarily AD, some AP flexibility
    147: (0.05, 0.95),  # Seraphine - AP mage/support
    150: (0.85, 0.15),  # Gnar - Primarily AD bruiser
    154: (0.1, 0.9),  # Zac - AP tank
    157: (0.9, 0.1),  # Yasuo - AD duelist
    161: (0.05, 0.95),  # Vel'Koz - Pure AP mage
    163: (0.05, 0.95),  # Taliyah - AP mage
    164: (0.85, 0.15),  # Camille - AD bruiser
    166: (0.9, 0.1),  # Akshan - AD assassin
    200: (0.9, 0.1),  # Bel'Veth - AD bruiser
    201: (0.1, 0.9),  # Braum - AP tank/support
    202: (0.95, 0.05),# Jhin - Physical-damage ADC
    203: (0.9, 0.1),  # Kindred - AD marksman/jungle
    221: (0.8, 0.2), # Zeri
    222: (0.95, 0.05),# Jinx - Physical-damage ADC
    223: (0.1, 0.9),  # Tahm Kench - AP tank
    233: (0.8, 0.2),  # Briar
    234: (0.8, 0.2),  # Viego - AD assassin/duelist
    235: (0.9, 0.1),  # Senna - AD marksman/support
    236: (0.95, 0.05),# Lucian - Physical-damage ADC
    238: (0.9, 0.1),  # Zed - AD assassin
    240: (0.9, 0.1),  # Kled - AD bruiser
    245: (0.1, 0.9),  # Ekko - AP assassin
    246: (0.9, 0.1),  # Qiyana - Hybrid assassin, leans AD
    254: (0.9, 0.1),  # Vi - AD bruiser
    266: (0.85, 0.15),  # Aatrox - AD bruiser
    267: (0.05, 0.95),  # Nami - AP support
    268: (0.2, 0.8),  # Azir - AP mage
    350: (0.05, 0.95),  # Yuumi - AP support
    360: (0.95, 0.05),# Samira - Physical-damage ADC
    412: (0.2, 0.8),  # Thresh - AP tank/support
    420: (0.9, 0.1),  # Illaoi - AD bruiser
    421: (0.9, 0.1),  # Rek'Sai - AD bruiser
    427: (0.1, 0.9),  # Ivern - AP utility/support
    429: (0.9, 0.1),  # Kalista - AD marksman
    432: (0.1, 0.9),  # Bard - AP support
    497: (0.1, 0.9),  # Rakan - AP support
    498: (0.95, 0.05),# Xayah - Physical-damage ADC
    516: (0.4, 0.6),  # Ornn - AP tank
    517: (0.25, 0.75),  # Sylas - AP bruiser
    518: (0.1, 0.9),  # Neeko - AP mage
    523: (0.95, 0.05),# Aphelios - Physical-damage ADC
    526: (0.1, 0.9), # Rell
    555: (0.9, 0.1),  # Pyke - AD assassin
    711: (0.1, 0.9),  # Vex - AP mage
    777: (0.8, 0.2),  # Yone - AD duelist
    799: (0.9, 0.1),  # Ambessa
    875: (0.9, 0.1),  # Sett - AD bruiser
    876: (0.1, 0.9),  # Lillia - AP bruiser
    887: (0.1, 0.9),  # Gwen - AP bruiser
    888: (0.1, 0.9), # Renata
    893: (0.1, 0.9),  # Aurora
    895: (0.95, 0.05),# Nilah - Physical-damage ADC
    897: (0.9, 0.1),  # K'Sante - AD bruiser
    901: (0.9, 0.1),  # Smolder
    902: (0.1, 0.9), # Milio
    910: (0.1, 0.9), # Hwei
    950: (0.95, 0.05), # Naafiri
}