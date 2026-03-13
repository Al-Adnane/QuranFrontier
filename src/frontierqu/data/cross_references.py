"""Cross-references and thematic groups for the Quran.

Provides intertextual links between verses (munasabat, naskh, thematic parallels)
and thematic groupings for algorithmic analysis.
"""

# Cross-references: ((surah1, verse1), (surah2, verse2), relation_type)
# relation_type values: basmala, sirat, tawhid, fasting, prayer, prophetic_narrative,
#                       naskh, munasabat, mercy, creation, covenant, guidance
CROSS_REFERENCES = [
    # Basmala connections
    ((1, 1), (27, 30), "basmala"),  # Fatihah basmala <-> Naml: Solomon's letter basmala
    ((1, 1), (11, 41), "basmala"),  # Fatihah basmala <-> Hud: Noah's ark "In the name of God"

    # Sirat al-Mustaqim (straight path)
    ((1, 6), (6, 153), "sirat"),    # Fatihah straight path <-> An'am: "this is My path"
    ((1, 6), (36, 61), "sirat"),    # Fatihah straight path <-> Ya-Sin: "this is a straight path"

    # Tawhid (monotheism)
    ((112, 1), (2, 255), "tawhid"),  # Ikhlas <-> Ayat al-Kursi
    ((112, 1), (59, 22), "tawhid"),  # Ikhlas <-> Hashr: divine names
    ((112, 1), (6, 102), "tawhid"),  # Ikhlas <-> An'am: "that is Allah your Lord"
    ((2, 255), (3, 2), "tawhid"),    # Ayat al-Kursi <-> Ali Imran: "Allah, no deity except Him"

    # Fasting
    ((2, 183), (2, 185), "fasting"),  # Baqarah fasting prescribed <-> Ramadan verse
    ((2, 183), (19, 26), "fasting"),  # Baqarah fasting <-> Maryam: Mary's fast of silence

    # Prayer
    ((2, 238), (17, 78), "prayer"),   # Baqarah: guard prayers <-> Isra: establish prayer
    ((2, 238), (11, 114), "prayer"),  # Baqarah: guard prayers <-> Hud: establish prayer at both ends
    ((1, 5), (20, 14), "prayer"),     # Fatihah worship <-> Ta-Ha: "worship Me and establish prayer"

    # Prophetic narratives - Moses
    ((2, 51), (7, 142), "prophetic_narrative"),  # Baqarah: Moses 40 nights <-> A'raf: Moses 40 nights
    ((20, 9), (28, 29), "prophetic_narrative"),  # Ta-Ha: Moses and fire <-> Qasas: Moses and fire

    # Prophetic narratives - Abraham
    ((2, 124), (14, 35), "prophetic_narrative"),  # Baqarah: Abraham tested <-> Ibrahim: Abraham's prayer
    ((6, 74), (21, 51), "prophetic_narrative"),   # An'am: Abraham and idols <-> Anbiya: Abraham and idols

    # Naskh (abrogation relationships)
    ((2, 142), (2, 144), "naskh"),   # Qibla change: Jerusalem -> Mecca
    ((2, 240), (2, 234), "naskh"),   # Widow waiting period: 1 year -> 4 months 10 days

    # Munasabat (thematic continuity between adjacent passages)
    ((2, 1), (2, 2), "munasabat"),   # Alif-Lam-Mim -> "This is the Book"
    ((55, 1), (55, 2), "munasabat"), # Ar-Rahman -> taught the Quran
    ((1, 7), (2, 1), "munasabat"),   # End of Fatihah guidance <-> Baqarah "guidance for the righteous"

    # Mercy
    ((1, 3), (6, 12), "mercy"),      # Fatihah: Ar-Rahman <-> An'am: "He has prescribed mercy"
    ((1, 3), (7, 156), "mercy"),     # Fatihah: Ar-Rahman <-> A'raf: "My mercy encompasses all"

    # Creation
    ((2, 30), (15, 28), "creation"),  # Baqarah: Adam creation <-> Hijr: Adam from clay
    ((96, 1), (96, 2), "creation"),   # Alaq: created man from a clot

    # Covenant
    ((2, 83), (5, 12), "covenant"),   # Baqarah: covenant of Israel <-> Ma'idah: covenant of Israel
]

# Thematic groups: theme -> list of (surah, verse) tuples
THEMATIC_GROUPS = {
    "tawhid": [
        (1, 1), (2, 255), (6, 102), (7, 54), (16, 1), (21, 22),
        (23, 91), (59, 22), (59, 23), (59, 24), (112, 1), (112, 2),
        (112, 3), (112, 4),
    ],
    "mercy": [
        (1, 1), (1, 3), (6, 12), (6, 54), (7, 156), (21, 107),
        (39, 53), (55, 1), (55, 2),
    ],
    "justice": [
        (4, 58), (4, 135), (5, 8), (5, 42), (6, 152), (16, 90),
        (49, 9), (57, 25),
    ],
    "patience": [
        (2, 45), (2, 153), (3, 200), (11, 115), (12, 18), (16, 127),
        (31, 17), (39, 10), (103, 3),
    ],
    "knowledge": [
        (2, 31), (2, 269), (20, 114), (35, 28), (39, 9), (58, 11),
        (96, 1), (96, 3), (96, 4), (96, 5),
    ],
    "creation": [
        (2, 30), (6, 1), (7, 54), (15, 28), (21, 30), (23, 12),
        (32, 7), (55, 3), (76, 1), (96, 1), (96, 2),
    ],
    "afterlife": [
        (2, 28), (3, 185), (6, 32), (23, 115), (29, 64), (56, 1),
        (75, 1), (78, 1), (99, 1), (101, 1),
    ],
    "prayer": [
        (1, 5), (2, 43), (2, 238), (4, 103), (11, 114), (17, 78),
        (20, 14), (29, 45), (62, 9), (73, 20),
    ],
    "fasting": [
        (2, 183), (2, 184), (2, 185), (2, 187), (19, 26),
    ],
    "charity": [
        (2, 177), (2, 261), (2, 267), (2, 274), (3, 92), (9, 60),
        (57, 18), (63, 10), (64, 16),
    ],
    "prophets": [
        (2, 136), (3, 33), (6, 83), (6, 84), (6, 85), (6, 86),
        (21, 25), (21, 69), (21, 78), (21, 85), (33, 40),
    ],
    "guidance": [
        (1, 6), (2, 2), (2, 185), (3, 138), (6, 153), (17, 9),
        (27, 2), (31, 3), (36, 61), (45, 20),
    ],
    "gratitude": [
        (2, 152), (14, 7), (16, 18), (27, 40), (31, 12), (34, 13),
        (39, 66), (54, 35), (76, 3),
    ],
}
