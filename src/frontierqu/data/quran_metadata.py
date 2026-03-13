"""Quran metadata for the FrontierQu framework.

Provides structural metadata about the Quran including surah information,
verse counts, revelation order, and cross-reference data.
Complete coverage: 114 surahs, 6236 verses.
"""

# Canonical verse counts for all 114 surahs (sum = 6236)
VERSE_COUNTS = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75,
    9: 129, 10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128,
    17: 111, 18: 110, 19: 98, 20: 135, 21: 112, 22: 78, 23: 118, 24: 64,
    25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60, 31: 34, 32: 30,
    33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29,
    49: 18, 50: 45, 51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96,
    57: 29, 58: 22, 59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18,
    65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44, 71: 28, 72: 28,
    73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26,
    89: 30, 90: 20, 91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19,
    97: 5, 98: 8, 99: 8, 100: 11, 101: 11, 102: 8, 103: 3, 104: 9,
    105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3, 111: 5, 112: 4,
    113: 5, 114: 6,
}

assert len(VERSE_COUNTS) == 114, f"Expected 114 surahs, got {len(VERSE_COUNTS)}"
assert sum(VERSE_COUNTS.values()) == 6236, f"Expected 6236 verses, got {sum(VERSE_COUNTS.values())}"

SURAH_METADATA = {
    1: {"name_ar": "\u0627\u0644\u0641\u0627\u062a\u062d\u0629", "name_en": "Al-Fatihah", "verses": 7, "revelation": "MECCAN_EARLY", "type": "foundational", "themes": ["praise", "guidance", "worship"]},
    2: {"name_ar": "\u0627\u0644\u0628\u0642\u0631\u0629", "name_en": "Al-Baqarah", "verses": 286, "revelation": "MEDINAN", "type": "legislative", "themes": ["law", "faith", "stories", "fasting", "pilgrimage"]},
    3: {"name_ar": "\u0622\u0644 \u0639\u0645\u0631\u0627\u0646", "name_en": "Ali 'Imran", "verses": 200, "revelation": "MEDINAN", "type": "legislative", "themes": ["family", "faith", "battle_of_uhud"]},
    4: {"name_ar": "\u0627\u0644\u0646\u0633\u0627\u0621", "name_en": "An-Nisa", "verses": 176, "revelation": "MEDINAN", "type": "legislative", "themes": ["women", "justice", "inheritance"]},
    5: {"name_ar": "\u0627\u0644\u0645\u0627\u0626\u062f\u0629", "name_en": "Al-Ma'idah", "verses": 120, "revelation": "MEDINAN", "type": "legislative", "themes": ["contracts", "food_laws", "justice"]},
    6: {"name_ar": "\u0627\u0644\u0623\u0646\u0639\u0627\u0645", "name_en": "Al-An'am", "verses": 165, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["tawhid", "creation", "prophets"]},
    7: {"name_ar": "\u0627\u0644\u0623\u0639\u0631\u0627\u0641", "name_en": "Al-A'raf", "verses": 206, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["prophets", "adam", "afterlife"]},
    8: {"name_ar": "\u0627\u0644\u0623\u0646\u0641\u0627\u0644", "name_en": "Al-Anfal", "verses": 75, "revelation": "MEDINAN", "type": "legislative", "themes": ["battle_of_badr", "war_ethics", "spoils"]},
    9: {"name_ar": "\u0627\u0644\u062a\u0648\u0628\u0629", "name_en": "At-Tawbah", "verses": 129, "revelation": "MEDINAN", "type": "legislative", "themes": ["repentance", "treaties", "jihad"]},
    10: {"name_ar": "\u064a\u0648\u0646\u0633", "name_en": "Yunus", "verses": 109, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["prophets", "faith", "divine_mercy"]},
    11: {"name_ar": "\u0647\u0648\u062f", "name_en": "Hud", "verses": 123, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["prophets", "patience", "divine_justice"]},
    12: {"name_ar": "\u064a\u0648\u0633\u0641", "name_en": "Yusuf", "verses": 111, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["joseph", "patience", "dreams"]},
    13: {"name_ar": "\u0627\u0644\u0631\u0639\u062f", "name_en": "Ar-Ra'd", "verses": 43, "revelation": "MEDINAN", "type": "theological", "themes": ["thunder", "creation", "guidance"]},
    14: {"name_ar": "\u0625\u0628\u0631\u0627\u0647\u064a\u0645", "name_en": "Ibrahim", "verses": 52, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["abraham", "gratitude", "prayer"]},
    15: {"name_ar": "\u0627\u0644\u062d\u062c\u0631", "name_en": "Al-Hijr", "verses": 99, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["quran_preservation", "prophets", "creation"]},
    16: {"name_ar": "\u0627\u0644\u0646\u062d\u0644", "name_en": "An-Nahl", "verses": 128, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["blessings", "creation", "gratitude"]},
    17: {"name_ar": "\u0627\u0644\u0625\u0633\u0631\u0627\u0621", "name_en": "Al-Isra", "verses": 111, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["night_journey", "ethics", "quran"]},
    18: {"name_ar": "\u0627\u0644\u0643\u0647\u0641", "name_en": "Al-Kahf", "verses": 110, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["cave_sleepers", "knowledge", "trials"]},
    19: {"name_ar": "\u0645\u0631\u064a\u0645", "name_en": "Maryam", "verses": 98, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["mary", "jesus", "prophets"]},
    20: {"name_ar": "\u0637\u0647", "name_en": "Ta-Ha", "verses": 135, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["moses", "quran", "guidance"]},
    21: {"name_ar": "\u0627\u0644\u0623\u0646\u0628\u064a\u0627\u0621", "name_en": "Al-Anbiya", "verses": 112, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["prophets", "tawhid", "judgment"]},
    22: {"name_ar": "\u0627\u0644\u062d\u062c", "name_en": "Al-Hajj", "verses": 78, "revelation": "MEDINAN", "type": "legislative", "themes": ["pilgrimage", "sacrifice", "worship"]},
    23: {"name_ar": "\u0627\u0644\u0645\u0624\u0645\u0646\u0648\u0646", "name_en": "Al-Mu'minun", "verses": 118, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["believers", "faith", "creation"]},
    24: {"name_ar": "\u0627\u0644\u0646\u0648\u0631", "name_en": "An-Nur", "verses": 64, "revelation": "MEDINAN", "type": "legislative", "themes": ["light", "modesty", "social_ethics"]},
    25: {"name_ar": "\u0627\u0644\u0641\u0631\u0642\u0627\u0646", "name_en": "Al-Furqan", "verses": 77, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["criterion", "quran", "servants_of_god"]},
    26: {"name_ar": "\u0627\u0644\u0634\u0639\u0631\u0627\u0621", "name_en": "Ash-Shu'ara", "verses": 227, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["poets", "prophets", "rejection"]},
    27: {"name_ar": "\u0627\u0644\u0646\u0645\u0644", "name_en": "An-Naml", "verses": 93, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["ants", "solomon", "knowledge"]},
    28: {"name_ar": "\u0627\u0644\u0642\u0635\u0635", "name_en": "Al-Qasas", "verses": 88, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["moses", "stories", "divine_plan"]},
    29: {"name_ar": "\u0627\u0644\u0639\u0646\u0643\u0628\u0648\u062a", "name_en": "Al-Ankabut", "verses": 69, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["spider", "trials", "faith"]},
    30: {"name_ar": "\u0627\u0644\u0631\u0648\u0645", "name_en": "Ar-Rum", "verses": 60, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["romans", "prophecy", "signs"]},
    31: {"name_ar": "\u0644\u0642\u0645\u0627\u0646", "name_en": "Luqman", "verses": 34, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["wisdom", "parenting", "gratitude"]},
    32: {"name_ar": "\u0627\u0644\u0633\u062c\u062f\u0629", "name_en": "As-Sajdah", "verses": 30, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["prostration", "creation", "resurrection"]},
    33: {"name_ar": "\u0627\u0644\u0623\u062d\u0632\u0627\u0628", "name_en": "Al-Ahzab", "verses": 73, "revelation": "MEDINAN", "type": "legislative", "themes": ["confederates", "prophet_household", "social_law"]},
    34: {"name_ar": "\u0633\u0628\u0623", "name_en": "Saba", "verses": 54, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["sheba", "gratitude", "judgment"]},
    35: {"name_ar": "\u0641\u0627\u0637\u0631", "name_en": "Fatir", "verses": 45, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["originator", "creation", "angels"]},
    36: {"name_ar": "\u064a\u0633", "name_en": "Ya-Sin", "verses": 83, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["heart_of_quran", "resurrection", "signs"]},
    37: {"name_ar": "\u0627\u0644\u0635\u0627\u0641\u0627\u062a", "name_en": "As-Saffat", "verses": 182, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["angels", "tawhid", "prophets"]},
    38: {"name_ar": "\u0635", "name_en": "Sad", "verses": 88, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["david", "solomon", "patience"]},
    39: {"name_ar": "\u0627\u0644\u0632\u0645\u0631", "name_en": "Az-Zumar", "verses": 75, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["groups", "sincerity", "mercy"]},
    40: {"name_ar": "\u063a\u0627\u0641\u0631", "name_en": "Ghafir", "verses": 85, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["forgiver", "faith", "pharaoh"]},
    41: {"name_ar": "\u0641\u0635\u0644\u062a", "name_en": "Fussilat", "verses": 54, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["explained", "quran", "creation"]},
    42: {"name_ar": "\u0627\u0644\u0634\u0648\u0631\u0649", "name_en": "Ash-Shura", "verses": 53, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["consultation", "revelation", "unity"]},
    43: {"name_ar": "\u0627\u0644\u0632\u062e\u0631\u0641", "name_en": "Az-Zukhruf", "verses": 89, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["ornaments", "tawhid", "prophets"]},
    44: {"name_ar": "\u0627\u0644\u062f\u062e\u0627\u0646", "name_en": "Ad-Dukhan", "verses": 59, "revelation": "MECCAN_LATE", "type": "eschatological", "themes": ["smoke", "judgment", "pharaoh"]},
    45: {"name_ar": "\u0627\u0644\u062c\u0627\u062b\u064a\u0629", "name_en": "Al-Jathiyah", "verses": 37, "revelation": "MECCAN_LATE", "type": "eschatological", "themes": ["kneeling", "signs", "judgment"]},
    46: {"name_ar": "\u0627\u0644\u0623\u062d\u0642\u0627\u0641", "name_en": "Al-Ahqaf", "verses": 35, "revelation": "MECCAN_LATE", "type": "narrative", "themes": ["sand_dunes", "hud", "quran"]},
    47: {"name_ar": "\u0645\u062d\u0645\u062f", "name_en": "Muhammad", "verses": 38, "revelation": "MEDINAN", "type": "legislative", "themes": ["prophet", "fighting", "faith"]},
    48: {"name_ar": "\u0627\u0644\u0641\u062a\u062d", "name_en": "Al-Fath", "verses": 29, "revelation": "MEDINAN", "type": "legislative", "themes": ["victory", "hudaybiyyah", "faith"]},
    49: {"name_ar": "\u0627\u0644\u062d\u062c\u0631\u0627\u062a", "name_en": "Al-Hujurat", "verses": 18, "revelation": "MEDINAN", "type": "legislative", "themes": ["manners", "brotherhood", "social_ethics"]},
    50: {"name_ar": "\u0642", "name_en": "Qaf", "verses": 45, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["resurrection", "creation", "quran"]},
    51: {"name_ar": "\u0627\u0644\u0630\u0627\u0631\u064a\u0627\u062a", "name_en": "Adh-Dhariyat", "verses": 60, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["winds", "judgment", "prophets"]},
    52: {"name_ar": "\u0627\u0644\u0637\u0648\u0631", "name_en": "At-Tur", "verses": 49, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["mount_sinai", "judgment", "paradise"]},
    53: {"name_ar": "\u0627\u0644\u0646\u062c\u0645", "name_en": "An-Najm", "verses": 62, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["star", "revelation", "ascension"]},
    54: {"name_ar": "\u0627\u0644\u0642\u0645\u0631", "name_en": "Al-Qamar", "verses": 55, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["moon", "prophets", "judgment"]},
    55: {"name_ar": "\u0627\u0644\u0631\u062d\u0645\u0646", "name_en": "Ar-Rahman", "verses": 78, "revelation": "MEDINAN", "type": "theological", "themes": ["mercy", "blessings", "creation"]},
    56: {"name_ar": "\u0627\u0644\u0648\u0627\u0642\u0639\u0629", "name_en": "Al-Waqi'ah", "verses": 96, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["event", "judgment", "three_groups"]},
    57: {"name_ar": "\u0627\u0644\u062d\u062f\u064a\u062f", "name_en": "Al-Hadid", "verses": 29, "revelation": "MEDINAN", "type": "theological", "themes": ["iron", "faith", "charity"]},
    58: {"name_ar": "\u0627\u0644\u0645\u062c\u0627\u062f\u0644\u0629", "name_en": "Al-Mujadilah", "verses": 22, "revelation": "MEDINAN", "type": "legislative", "themes": ["pleading_woman", "justice", "divine_knowledge"]},
    59: {"name_ar": "\u0627\u0644\u062d\u0634\u0631", "name_en": "Al-Hashr", "verses": 24, "revelation": "MEDINAN", "type": "legislative", "themes": ["exile", "divine_names", "community"]},
    60: {"name_ar": "\u0627\u0644\u0645\u0645\u062a\u062d\u0646\u0629", "name_en": "Al-Mumtahanah", "verses": 13, "revelation": "MEDINAN", "type": "legislative", "themes": ["examined_woman", "allegiance", "interfaith"]},
    61: {"name_ar": "\u0627\u0644\u0635\u0641", "name_en": "As-Saff", "verses": 14, "revelation": "MEDINAN", "type": "theological", "themes": ["ranks", "faith", "struggle"]},
    62: {"name_ar": "\u0627\u0644\u062c\u0645\u0639\u0629", "name_en": "Al-Jumu'ah", "verses": 11, "revelation": "MEDINAN", "type": "legislative", "themes": ["friday_prayer", "knowledge", "commerce"]},
    63: {"name_ar": "\u0627\u0644\u0645\u0646\u0627\u0641\u0642\u0648\u0646", "name_en": "Al-Munafiqun", "verses": 11, "revelation": "MEDINAN", "type": "legislative", "themes": ["hypocrites", "sincerity", "charity"]},
    64: {"name_ar": "\u0627\u0644\u062a\u063a\u0627\u0628\u0646", "name_en": "At-Taghabun", "verses": 18, "revelation": "MEDINAN", "type": "theological", "themes": ["mutual_loss", "faith", "obedience"]},
    65: {"name_ar": "\u0627\u0644\u0637\u0644\u0627\u0642", "name_en": "At-Talaq", "verses": 12, "revelation": "MEDINAN", "type": "legislative", "themes": ["divorce", "family_law", "taqwa"]},
    66: {"name_ar": "\u0627\u0644\u062a\u062d\u0631\u064a\u0645", "name_en": "At-Tahrim", "verses": 12, "revelation": "MEDINAN", "type": "legislative", "themes": ["prohibition", "prophet_household", "repentance"]},
    67: {"name_ar": "\u0627\u0644\u0645\u0644\u0643", "name_en": "Al-Mulk", "verses": 30, "revelation": "MECCAN_LATE", "type": "theological", "themes": ["sovereignty", "creation", "afterlife"]},
    68: {"name_ar": "\u0627\u0644\u0642\u0644\u0645", "name_en": "Al-Qalam", "verses": 52, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["pen", "character", "judgment"]},
    69: {"name_ar": "\u0627\u0644\u062d\u0627\u0642\u0629", "name_en": "Al-Haqqah", "verses": 52, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["reality", "judgment", "quran"]},
    70: {"name_ar": "\u0627\u0644\u0645\u0639\u0627\u0631\u062c", "name_en": "Al-Ma'arij", "verses": 44, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["ascending_ways", "judgment", "patience"]},
    71: {"name_ar": "\u0646\u0648\u062d", "name_en": "Nuh", "verses": 28, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["noah", "dawah", "persistence"]},
    72: {"name_ar": "\u0627\u0644\u062c\u0646", "name_en": "Al-Jinn", "verses": 28, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["jinn", "tawhid", "revelation"]},
    73: {"name_ar": "\u0627\u0644\u0645\u0632\u0645\u0644", "name_en": "Al-Muzzammil", "verses": 20, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["night_prayer", "quran_recitation", "patience"]},
    74: {"name_ar": "\u0627\u0644\u0645\u062f\u062b\u0631", "name_en": "Al-Muddaththir", "verses": 56, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["cloaked_one", "warning", "judgment"]},
    75: {"name_ar": "\u0627\u0644\u0642\u064a\u0627\u0645\u0629", "name_en": "Al-Qiyamah", "verses": 40, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["resurrection", "judgment", "soul"]},
    76: {"name_ar": "\u0627\u0644\u0625\u0646\u0633\u0627\u0646", "name_en": "Al-Insan", "verses": 31, "revelation": "MEDINAN", "type": "theological", "themes": ["human", "gratitude", "paradise"]},
    77: {"name_ar": "\u0627\u0644\u0645\u0631\u0633\u0644\u0627\u062a", "name_en": "Al-Mursalat", "verses": 50, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["emissaries", "judgment", "denial"]},
    78: {"name_ar": "\u0627\u0644\u0646\u0628\u0623", "name_en": "An-Naba", "verses": 40, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["tidings", "resurrection", "creation"]},
    79: {"name_ar": "\u0627\u0644\u0646\u0627\u0632\u0639\u0627\u062a", "name_en": "An-Nazi'at", "verses": 46, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["extractors", "resurrection", "moses"]},
    80: {"name_ar": "\u0639\u0628\u0633", "name_en": "Abasa", "verses": 42, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["frowning", "equality", "judgment"]},
    81: {"name_ar": "\u0627\u0644\u062a\u0643\u0648\u064a\u0631", "name_en": "At-Takwir", "verses": 29, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["folding_up", "judgment", "revelation"]},
    82: {"name_ar": "\u0627\u0644\u0627\u0646\u0641\u0637\u0627\u0631", "name_en": "Al-Infitar", "verses": 19, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["cleaving", "judgment", "angels"]},
    83: {"name_ar": "\u0627\u0644\u0645\u0637\u0641\u0641\u064a\u0646", "name_en": "Al-Mutaffifin", "verses": 36, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["defrauding", "judgment", "record"]},
    84: {"name_ar": "\u0627\u0644\u0627\u0646\u0634\u0642\u0627\u0642", "name_en": "Al-Inshiqaq", "verses": 25, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["splitting", "judgment", "record"]},
    85: {"name_ar": "\u0627\u0644\u0628\u0631\u0648\u062c", "name_en": "Al-Buruj", "verses": 22, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["constellations", "persecution", "faith"]},
    86: {"name_ar": "\u0627\u0644\u0637\u0627\u0631\u0642", "name_en": "At-Tariq", "verses": 17, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["night_star", "creation", "quran"]},
    87: {"name_ar": "\u0627\u0644\u0623\u0639\u0644\u0649", "name_en": "Al-A'la", "verses": 19, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["most_high", "purification", "reminder"]},
    88: {"name_ar": "\u0627\u0644\u063a\u0627\u0634\u064a\u0629", "name_en": "Al-Ghashiyah", "verses": 26, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["overwhelming", "judgment", "creation"]},
    89: {"name_ar": "\u0627\u0644\u0641\u062c\u0631", "name_en": "Al-Fajr", "verses": 30, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["dawn", "past_nations", "judgment"]},
    90: {"name_ar": "\u0627\u0644\u0628\u0644\u062f", "name_en": "Al-Balad", "verses": 20, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["city", "struggle", "compassion"]},
    91: {"name_ar": "\u0627\u0644\u0634\u0645\u0633", "name_en": "Ash-Shams", "verses": 15, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["sun", "soul", "purification"]},
    92: {"name_ar": "\u0627\u0644\u0644\u064a\u0644", "name_en": "Al-Layl", "verses": 21, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["night", "charity", "guidance"]},
    93: {"name_ar": "\u0627\u0644\u0636\u062d\u0649", "name_en": "Ad-Duha", "verses": 11, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["morning_light", "consolation", "gratitude"]},
    94: {"name_ar": "\u0627\u0644\u0634\u0631\u062d", "name_en": "Ash-Sharh", "verses": 8, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["expansion", "ease", "consolation"]},
    95: {"name_ar": "\u0627\u0644\u062a\u064a\u0646", "name_en": "At-Tin", "verses": 8, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["fig", "human_nature", "judgment"]},
    96: {"name_ar": "\u0627\u0644\u0639\u0644\u0642", "name_en": "Al-Alaq", "verses": 19, "revelation": "MECCAN_EARLY", "type": "foundational", "themes": ["clot", "first_revelation", "knowledge"]},
    97: {"name_ar": "\u0627\u0644\u0642\u062f\u0631", "name_en": "Al-Qadr", "verses": 5, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["power", "laylat_al_qadr", "angels"]},
    98: {"name_ar": "\u0627\u0644\u0628\u064a\u0646\u0629", "name_en": "Al-Bayyinah", "verses": 8, "revelation": "MEDINAN", "type": "theological", "themes": ["clear_evidence", "faith", "judgment"]},
    99: {"name_ar": "\u0627\u0644\u0632\u0644\u0632\u0644\u0629", "name_en": "Az-Zalzalah", "verses": 8, "revelation": "MEDINAN", "type": "eschatological", "themes": ["earthquake", "judgment", "deeds"]},
    100: {"name_ar": "\u0627\u0644\u0639\u0627\u062f\u064a\u0627\u062a", "name_en": "Al-Adiyat", "verses": 11, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["chargers", "ingratitude", "judgment"]},
    101: {"name_ar": "\u0627\u0644\u0642\u0627\u0631\u0639\u0629", "name_en": "Al-Qari'ah", "verses": 11, "revelation": "MECCAN_EARLY", "type": "eschatological", "themes": ["calamity", "judgment", "scales"]},
    102: {"name_ar": "\u0627\u0644\u062a\u0643\u0627\u062b\u0631", "name_en": "At-Takathur", "verses": 8, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["rivalry", "heedlessness", "afterlife"]},
    103: {"name_ar": "\u0627\u0644\u0639\u0635\u0631", "name_en": "Al-Asr", "verses": 3, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["time", "faith", "patience"]},
    104: {"name_ar": "\u0627\u0644\u0647\u0645\u0632\u0629", "name_en": "Al-Humazah", "verses": 9, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["backbiter", "wealth", "hellfire"]},
    105: {"name_ar": "\u0627\u0644\u0641\u064a\u0644", "name_en": "Al-Fil", "verses": 5, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["elephant", "divine_protection", "kaaba"]},
    106: {"name_ar": "\u0642\u0631\u064a\u0634", "name_en": "Quraysh", "verses": 4, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["quraysh", "trade", "worship"]},
    107: {"name_ar": "\u0627\u0644\u0645\u0627\u0639\u0648\u0646", "name_en": "Al-Ma'un", "verses": 7, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["small_kindness", "hypocrisy", "prayer"]},
    108: {"name_ar": "\u0627\u0644\u0643\u0648\u062b\u0631", "name_en": "Al-Kawthar", "verses": 3, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["abundance", "prayer", "sacrifice"]},
    109: {"name_ar": "\u0627\u0644\u0643\u0627\u0641\u0631\u0648\u0646", "name_en": "Al-Kafirun", "verses": 6, "revelation": "MECCAN_EARLY", "type": "theological", "themes": ["disbelievers", "tolerance", "tawhid"]},
    110: {"name_ar": "\u0627\u0644\u0646\u0635\u0631", "name_en": "An-Nasr", "verses": 3, "revelation": "MEDINAN", "type": "devotional", "themes": ["victory", "praise", "forgiveness"]},
    111: {"name_ar": "\u0627\u0644\u0645\u0633\u062f", "name_en": "Al-Masad", "verses": 5, "revelation": "MECCAN_EARLY", "type": "narrative", "themes": ["palm_fiber", "abu_lahab", "judgment"]},
    112: {"name_ar": "\u0627\u0644\u0625\u062e\u0644\u0627\u0635", "name_en": "Al-Ikhlas", "verses": 4, "revelation": "MECCAN_EARLY", "type": "foundational", "themes": ["sincerity", "tawhid", "divine_nature"]},
    113: {"name_ar": "\u0627\u0644\u0641\u0644\u0642", "name_en": "Al-Falaq", "verses": 5, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["daybreak", "protection", "refuge"]},
    114: {"name_ar": "\u0627\u0644\u0646\u0627\u0633", "name_en": "An-Nas", "verses": 6, "revelation": "MECCAN_EARLY", "type": "devotional", "themes": ["mankind", "protection", "refuge"]},
}

TOTAL_SURAHS = 114
TOTAL_VERSES = 6236
TOTAL_WORDS = 77430
TOTAL_LETTERS = 323671


def get_surah_metadata(surah_number: int) -> dict:
    """Get metadata for a specific surah by number (1-114)."""
    return SURAH_METADATA.get(surah_number, {})


def get_total_surahs() -> int:
    """Return the total number of surahs in the Quran."""
    return TOTAL_SURAHS


def get_total_verses() -> int:
    """Return the total number of verses in the Quran."""
    return TOTAL_VERSES


def get_verse_count(surah_number: int) -> int:
    """Return the verse count for a specific surah."""
    return VERSE_COUNTS.get(surah_number, 0)
