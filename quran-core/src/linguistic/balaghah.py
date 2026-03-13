"""Arabic Rhetoric (Balaghah) as Information Theory.

Three branches:
    Ma'ani (meanings) -> information content per sentence structure
    Bayan (clarity) -> semantic distance between literal and intended meaning
    Badi' (embellishment) -> phonological pattern entropy

Rhetorical density = total rhetorical bits / number of morphemes
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math
import re


@dataclass
class RhetoricalDevice:
    device_type: str     # e.g., "jinas", "tashbih", "istiarah"
    category: str        # "maani", "bayan", or "badi"
    description: str
    score: float         # 0.0-1.0 strength/confidence


@dataclass
class MaaniAnalysis:
    sentence_type: str   # khabariy (declarative), inshaiy (performative)
    emphasis_level: float  # 0.0 = neutral, 1.0 = maximum emphasis
    word_order: str      # "standard", "fronted", "delayed"
    devices: List[RhetoricalDevice] = field(default_factory=list)


@dataclass
class RhetoricalAnalysis:
    text: str
    maani: Optional[MaaniAnalysis]
    bayan: List[RhetoricalDevice]
    badi: List[RhetoricalDevice]
    density: float

    @classmethod
    def analyze(cls, text: str) -> 'RhetoricalAnalysis':
        maani = detect_maani(text)
        bayan = detect_bayan(text)
        badi = detect_badi(text)
        density = rhetorical_density(text)
        return cls(text=text, maani=maani, bayan=bayan, badi=badi, density=density)


# -- Ma'ani (Meanings) --

# Emphasis markers
EMPHASIS_PARTICLES = {"إن", "أن", "لقد", "قد", "إنما", "لا", "والله"}
# Fronting patterns (taqdim): object before verb, predicate before subject
FRONTING_MARKERS = {"إياك", "إيَّاكَ"}  # Exclusive object fronting


def detect_maani(text: str) -> MaaniAnalysis:
    """Analyze sentence-level rhetoric (ma'ani)."""
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    words = stripped.split()

    # Determine sentence type
    interrogative_particles = {"أ", "هل", "ما", "من", "أين", "كيف", "متى", "لماذا"}
    imperative_prefixes = {"اِ", "قل", "قم", "كن"}

    sentence_type = "khabariy"  # default: declarative
    if words and words[0] in interrogative_particles:
        sentence_type = "inshaiy_istifham"  # interrogative
    elif words and any(words[0].startswith(p) for p in imperative_prefixes):
        sentence_type = "inshaiy_amr"  # imperative

    # Compute emphasis level
    emphasis = 0.0
    for word in words:
        if word in EMPHASIS_PARTICLES:
            emphasis += 0.3
    # Fronting = emphasis (taqdim)
    for marker in FRONTING_MARKERS:
        if marker in text:
            emphasis += 0.4
    emphasis = min(emphasis, 1.0)

    # Word order
    word_order = "standard"
    for marker in FRONTING_MARKERS:
        if marker in text:
            word_order = "fronted"
            break

    devices = []
    if emphasis > 0:
        devices.append(RhetoricalDevice(
            device_type="tawkid", category="maani",
            description="Emphasis", score=emphasis
        ))
    if word_order == "fronted":
        devices.append(RhetoricalDevice(
            device_type="taqdim", category="maani",
            description="Fronting for emphasis/exclusivity", score=0.8
        ))

    return MaaniAnalysis(
        sentence_type=sentence_type,
        emphasis_level=emphasis,
        word_order=word_order,
        devices=devices
    )


# -- Bayan (Clarity) --

# Known metaphorical terms in Quran
METAPHOR_TERMS = {
    "نور": "light_metaphor",       # Allah is the light
    "ظلمات": "darkness_metaphor",  # Disbelief as darkness
    "صراط": "path_metaphor",       # Guidance as straight path
    "ميزان": "scale_metaphor",     # Justice as scales
    "ماء": "water_metaphor",       # Revelation as water/rain
}


def detect_bayan(text: str) -> List[RhetoricalDevice]:
    """Detect figures of speech (bayan): metaphor, simile, metonymy."""
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    devices = []

    # Detect tashbih (simile) -- contains ka or mithl
    if "كَ" in text or "مثل" in stripped or "ك" in stripped.split():
        devices.append(RhetoricalDevice(
            device_type="tashbih", category="bayan",
            description="Simile (explicit comparison)", score=0.7
        ))

    # Detect isti'arah (metaphor) -- known metaphorical terms
    for term, metaphor_type in METAPHOR_TERMS.items():
        if term in stripped:
            devices.append(RhetoricalDevice(
                device_type="istiarah", category="bayan",
                description=f"Metaphor: {metaphor_type}", score=0.8
            ))

    # Detect kinayah (metonymy/allusion)
    if "يد" in stripped.split():  # "hand" often metonymic
        devices.append(RhetoricalDevice(
            device_type="kinayah", category="bayan",
            description="Metonymy", score=0.6
        ))

    return devices


# -- Badi' (Embellishment) --

def _extract_consonant_skeleton(word: str) -> str:
    """Extract consonant skeleton for pattern matching."""
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    vowels = set("اوي")
    return "".join(c for c in stripped if c not in vowels)


def detect_badi(text: str) -> List[RhetoricalDevice]:
    """Detect embellishment devices (badi'): alliteration, antithesis, rhyme."""
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    words = stripped.split()
    devices = []

    # Detect jinas (paronomasia / wordplay from shared roots)
    skeletons = [_extract_consonant_skeleton(w) for w in words]
    for i in range(len(skeletons)):
        for j in range(i + 1, len(skeletons)):
            if len(skeletons[i]) >= 2 and len(skeletons[j]) >= 2:
                # Share first 2 consonants = partial jinas
                if skeletons[i][:2] == skeletons[j][:2] and words[i] != words[j]:
                    devices.append(RhetoricalDevice(
                        device_type="jinas", category="badi",
                        description=f"Paronomasia between '{words[i]}' and '{words[j]}'",
                        score=0.7
                    ))

    # Detect tikrar (repetition)
    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1
    for w, count in word_counts.items():
        if count > 1 and len(w) > 1:
            devices.append(RhetoricalDevice(
                device_type="tikrar", category="badi",
                description=f"Repetition of '{w}' ({count}x)", score=0.5 * min(count, 3)
            ))

    # Detect tibaq (antithesis) -- known antonym pairs
    antonym_pairs = [
        ("الليل", "النهار"), ("السماء", "الأرض"), ("الحياة", "الموت"),
        ("النور", "الظلمات"), ("الجنة", "النار"), ("الخير", "الشر"),
    ]
    for a, b in antonym_pairs:
        if a in stripped and b in stripped:
            devices.append(RhetoricalDevice(
                device_type="tibaq", category="badi",
                description=f"Antithesis: {a} vs {b}", score=0.9
            ))

    # Detect saj' (prose rhyme) -- ending similarity
    if len(words) >= 2:
        if words[-1][-1:] == words[-2][-1:] and len(words[-1]) > 1:
            devices.append(RhetoricalDevice(
                device_type="saj", category="badi",
                description="Prose rhyme (matching endings)", score=0.6
            ))

    return devices


# -- Rhetorical Density --

def rhetorical_density(text: str) -> float:
    """Compute rhetorical bits per morpheme.

    density = (sum of device scores) * log2(1 + num_devices) / num_morphemes
    """
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    morphemes = stripped.split()
    if not morphemes:
        return 0.0

    maani = detect_maani(text)
    bayan = detect_bayan(text)
    badi = detect_badi(text)

    all_devices = maani.devices + bayan + badi
    if not all_devices:
        # Even plain text has base rhetorical content from word choice
        return 0.1 * len(morphemes) / max(len(morphemes), 1)

    total_score = sum(d.score for d in all_devices)
    device_bits = math.log2(1 + len(all_devices))

    return (total_score * device_bits) / len(morphemes)
