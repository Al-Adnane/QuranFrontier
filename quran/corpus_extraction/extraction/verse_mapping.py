"""
Verse Mapping for Phase 3 Parallel Extraction.

Maps global verse numbers (1-6,236) to (surah, ayah) pairs.
The Quran has 114 surahs with varying numbers of verses.

This module provides bidirectional mapping:
- Global verse number → (surah, ayah)
- (surah, ayah) → global verse number
"""

from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VerseMapper:
    """Maps between global verse numbers and (surah, ayah) pairs."""

    # Quran structure: surahs[i] = number of ayahs in surah i+1
    # Total: 114 surahs, 6,236 verses (quran.com standard)
    # Note: Some editions count differently due to bismillah placement
    SURAH_AYAH_COUNTS = [
        7,      # Surah 1: Al-Fatiha (7 ayahs)
        286,    # Surah 2: Al-Baqarah (286 ayahs)
        200,    # Surah 3: Al-Imran (200 ayahs)
        176,    # Surah 4: An-Nisa (176 ayahs)
        120,    # Surah 5: Al-Maidah (120 ayahs)
        165,    # Surah 6: Al-An'am (165 ayahs)
        206,    # Surah 7: Al-A'raf (206 ayahs)
        75,     # Surah 8: Al-Anfal (75 ayahs)
        129,    # Surah 9: At-Tawbah (129 ayahs)
        109,    # Surah 10: Yunus (109 ayahs)
        123,    # Surah 11: Hud (123 ayahs)
        111,    # Surah 12: Yusuf (111 ayahs)
        43,     # Surah 13: Ar-Ra'd (43 ayahs)
        52,     # Surah 14: Ibrahim (52 ayahs)
        99,     # Surah 15: Al-Hijr (99 ayahs)
        128,    # Surah 16: An-Nahl (128 ayahs)
        111,    # Surah 17: Al-Isra (111 ayahs)
        110,    # Surah 18: Al-Kahf (110 ayahs)
        98,     # Surah 19: Maryam (98 ayahs)
        135,    # Surah 20: Ta-Ha (135 ayahs)
        112,    # Surah 21: Al-Anbiya (112 ayahs)
        78,     # Surah 22: Al-Hajj (78 ayahs)
        118,    # Surah 23: Al-Mu'minun (118 ayahs)
        64,     # Surah 24: An-Nur (64 ayahs)
        77,     # Surah 25: Al-Furqan (77 ayahs)
        227,    # Surah 26: Ash-Shu'ara (227 ayahs)
        93,     # Surah 27: An-Naml (93 ayahs)
        88,     # Surah 28: Al-Qasas (88 ayahs)
        69,     # Surah 29: Al-Ankabut (69 ayahs)
        60,     # Surah 30: Ar-Rum (60 ayahs)
        34,     # Surah 31: Luqman (34 ayahs)
        30,     # Surah 32: As-Sajdah (30 ayahs)
        73,     # Surah 33: Al-Ahzab (73 ayahs)
        54,     # Surah 34: Saba (54 ayahs)
        45,     # Surah 35: Fatir (45 ayahs)
        83,     # Surah 36: Ya-Sin (83 ayahs)
        182,    # Surah 37: As-Saffat (182 ayahs)
        88,     # Surah 38: Sad (88 ayahs)
        75,     # Surah 39: Az-Zumar (75 ayahs)
        85,     # Surah 40: Ghafir (85 ayahs)
        54,     # Surah 41: Fussilat (54 ayahs)
        53,     # Surah 42: Ash-Shura (53 ayahs)
        89,     # Surah 43: Az-Zukhruf (89 ayahs)
        59,     # Surah 44: Ad-Dukhan (59 ayahs)
        37,     # Surah 45: Al-Jathiyah (37 ayahs)
        35,     # Surah 46: Al-Ahqaf (35 ayahs)
        38,     # Surah 47: Muhammad (38 ayahs)
        29,     # Surah 48: Al-Fath (29 ayahs)
        18,     # Surah 49: Al-Hujurat (18 ayahs)
        45,     # Surah 50: Qaf (45 ayahs)
        60,     # Surah 51: Adh-Dhariyat (60 ayahs)
        49,     # Surah 52: At-Tur (49 ayahs)
        62,     # Surah 53: An-Najm (62 ayahs)
        55,     # Surah 54: Al-Qamar (55 ayahs)
        78,     # Surah 55: Ar-Rahman (78 ayahs)
        96,     # Surah 56: Al-Waqi'ah (96 ayahs)
        50,     # Surah 57: Al-Hadid (50 ayahs)
        40,     # Surah 58: Al-Mujadilah (40 ayahs)
        34,     # Surah 59: Al-Hashr (34 ayahs)
        37,     # Surah 60: Al-Mumtahanah (37 ayahs)
        14,     # Surah 61: As-Saff (14 ayahs)
        11,     # Surah 62: Al-Jumu'ah (11 ayahs)
        11,     # Surah 63: Al-Munafiqun (11 ayahs)
        18,     # Surah 64: At-Taghabun (18 ayahs)
        12,     # Surah 65: At-Talaq (12 ayahs)
        12,     # Surah 66: At-Tahrim (12 ayahs)
        30,     # Surah 67: Al-Mulk (30 ayahs)
        52,     # Surah 68: Al-Qalam (52 ayahs)
        52,     # Surah 69: Al-Haqqah (52 ayahs)
        44,     # Surah 70: Al-Ma'arij (44 ayahs)
        28,     # Surah 71: Nuh (28 ayahs)
        28,     # Surah 72: Al-Jinn (28 ayahs)
        20,     # Surah 73: Al-Muzzammil (20 ayahs)
        56,     # Surah 74: Al-Muddaththir (56 ayahs)
        40,     # Surah 75: Al-Qiyamah (40 ayahs)
        31,     # Surah 76: Al-Insan (31 ayahs)
        50,     # Surah 77: Al-Mursalat (50 ayahs)
        40,     # Surah 78: An-Naba (40 ayahs)
        46,     # Surah 79: An-Naziat (46 ayahs)
        42,     # Surah 80: Abasa (42 ayahs)
        29,     # Surah 81: At-Takwir (29 ayahs)
        19,     # Surah 82: Al-Infitar (19 ayahs)
        36,     # Surah 83: Al-Mutaffifin (36 ayahs)
        25,     # Surah 84: Al-Inshiqaq (25 ayahs)
        22,     # Surah 85: Al-Buruj (22 ayahs)
        17,     # Surah 86: At-Tariq (17 ayahs)
        19,     # Surah 87: Al-A'la (19 ayahs)
        26,     # Surah 88: Al-Ghashiyah (26 ayahs)
        30,     # Surah 89: Al-Fajr (30 ayahs)
        20,     # Surah 90: Al-Balad (20 ayahs)
        15,     # Surah 91: Ash-Shams (15 ayahs)
        21,     # Surah 92: Al-Lail (21 ayahs)
        11,     # Surah 93: Ad-Duha (11 ayahs)
        8,      # Surah 94: Ash-Sharh (8 ayahs)
        5,      # Surah 95: At-Tin (5 ayahs)
        19,     # Surah 96: Al-Alaq (19 ayahs)
        5,      # Surah 97: Al-Qadr (5 ayahs)
        8,      # Surah 98: Al-Bayyinah (8 ayahs)
        6,      # Surah 99: Az-Zalzalah (6 ayahs)
        11,     # Surah 100: Al-Adiyat (11 ayahs)
        3,      # Surah 101: Al-Qari'ah (3 ayahs)
        8,      # Surah 102: At-Takathur (8 ayahs)
        4,      # Surah 103: Al-Asr (4 ayahs)
        9,      # Surah 104: Al-Humazah (9 ayahs)
        5,      # Surah 105: Al-Fil (5 ayahs)
        4,      # Surah 106: Quraysh (4 ayahs)
        7,      # Surah 107: Al-Ma'un (7 ayahs)
        8,      # Surah 108: Al-Kawthar (8 ayahs)
        6,      # Surah 109: Al-Kafirun (6 ayahs)
        3,      # Surah 110: An-Nasr (3 ayahs)
        5,      # Surah 111: Al-Masad (5 ayahs)
        4,      # Surah 112: Al-Ikhlas (4 ayahs)
        5,      # Surah 113: Al-Falaq (5 ayahs)
        6,      # Surah 114: An-Nas (6 ayahs)
    ]

    def __init__(self):
        """Initialize verse mapper with precomputed cumulative verse counts."""
        # Build cumulative verse counts for O(1) lookup
        self.cumulative_verses = [0]  # Starting point
        for count in self.SURAH_AYAH_COUNTS:
            self.cumulative_verses.append(self.cumulative_verses[-1] + count)

        # Validate total
        total_verses = self.cumulative_verses[-1]
        if total_verses != 6236:
            logger.warning(f"Total verses: {total_verses}, expected 6236")

    def get_surah_ayah(self, global_verse: int) -> Tuple[int, int]:
        """
        Convert global verse number to (surah, ayah) pair.

        Args:
            global_verse: Global verse number (1 to total_verses)

        Returns:
            Tuple of (surah, ayah) where surah is 1-114 and ayah is 1-based

        Raises:
            ValueError: If global_verse is out of range
        """
        total = self.get_total_verses()
        if not (1 <= global_verse <= total):
            raise ValueError(f"Global verse must be 1-{total}, got {global_verse}")

        # Binary search to find surah
        left, right = 0, len(self.SURAH_AYAH_COUNTS)
        while left < right:
            mid = (left + right) // 2
            if self.cumulative_verses[mid] < global_verse:
                left = mid + 1
            else:
                right = mid

        surah = left
        ayah = global_verse - self.cumulative_verses[surah - 1]

        return (surah, ayah)

    def get_global_verse(self, surah: int, ayah: int) -> int:
        """
        Convert (surah, ayah) pair to global verse number.

        Args:
            surah: Surah number (1-114)
            ayah: Ayah number within the surah (1-based)

        Returns:
            Global verse number (1-6236)

        Raises:
            ValueError: If surah/ayah are invalid
        """
        if not (1 <= surah <= 114):
            raise ValueError(f"Surah must be 1-114, got {surah}")

        max_ayah = self.SURAH_AYAH_COUNTS[surah - 1]
        if not (1 <= ayah <= max_ayah):
            raise ValueError(
                f"Ayah {ayah} invalid for surah {surah} "
                f"(max: {max_ayah})"
            )

        return self.cumulative_verses[surah - 1] + ayah

    def get_surah_ayah_count(self, surah: int) -> int:
        """
        Get the number of ayahs in a surah.

        Args:
            surah: Surah number (1-114)

        Returns:
            Number of ayahs in the surah

        Raises:
            ValueError: If surah is out of range
        """
        if not (1 <= surah <= 114):
            raise ValueError(f"Surah must be 1-114, got {surah}")

        return self.SURAH_AYAH_COUNTS[surah - 1]

    def is_valid_verse(self, surah: int, ayah: int) -> bool:
        """
        Check if (surah, ayah) pair is valid.

        Args:
            surah: Surah number
            ayah: Ayah number

        Returns:
            True if valid, False otherwise
        """
        if not (1 <= surah <= 114):
            return False
        if not (1 <= ayah <= self.SURAH_AYAH_COUNTS[surah - 1]):
            return False
        return True

    def get_total_verses(self) -> int:
        """Get total number of verses in the Quran (6236)."""
        return self.cumulative_verses[-1]

    def get_total_surahs(self) -> int:
        """Get total number of surahs (114)."""
        return len(self.SURAH_AYAH_COUNTS)
