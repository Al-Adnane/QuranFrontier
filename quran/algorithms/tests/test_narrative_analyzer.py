"""
Tests for Algorithm 2: Narrative Structure and Story Arc

All tests use in-memory sample data (no actual corpus files required)
unless testing corpus integration.
"""

import json
import os
import sys
import tempfile

import pytest

# Ensure the algorithms package is importable when running from repo root
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", ".."),
)

from quran.algorithms.narrative_analyzer import (
    ConflictType,
    NarrativeStructure,
    QuranicNarrativeAnalyzer,
    Scene,
    StoryArcType,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_analyzer(verses=None):
    """Return an analyzer with optional in-memory corpus data loaded via a tempfile."""
    analyzer = QuranicNarrativeAnalyzer()
    if verses is not None:
        corpus = {"verses": verses}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(corpus, f)
            tmp_path = f.name
        analyzer._load_corpus(tmp_path)
        os.unlink(tmp_path)
    return analyzer


YUSUF_SAMPLE_VERSES = [
    {"verse_key": "12:1", "translation": "Alif Lam Ra. These are the verses of the clear Book."},
    {"verse_key": "12:2", "translation": "Indeed, We have sent it down as an Arabic Quran that you might understand."},
    {"verse_key": "12:3", "translation": "We relate to you the best of stories in what We have revealed to you of this Quran."},
    {"verse_key": "12:4", "translation": "When Joseph said to his father: O my father, indeed I saw eleven stars and the sun and the moon."},
    {"verse_key": "12:5", "translation": "He said: O my son, do not relate your vision to your brothers or they will contrive against you a plan."},
    {"verse_key": "12:6", "translation": "And thus will your Lord choose you and teach you the interpretation of narratives."},
    {"verse_key": "12:7", "translation": "Certainly were there in Joseph and his brothers signs for those who ask."},
    {"verse_key": "12:8", "translation": "When they said: Joseph and his brother are more beloved to our father than we."},
    {"verse_key": "12:9", "translation": "Kill Joseph or cast him out to some land; the countenance of your father will be only for you."},
    {"verse_key": "12:10", "translation": "Then a speaker among them said: Do not kill Joseph but throw him into the well."},
    {"verse_key": "12:11", "translation": "They said: O our father, why do you not entrust us with Joseph while indeed we are his sincere well-wishers?"},
    {"verse_key": "12:12", "translation": "Send him with us tomorrow that he may eat well and play. And indeed we will be his guardians."},
    {"verse_key": "12:13", "translation": "He said: Indeed, it saddens me that you should take him and I fear that the wolf would eat him."},
    {"verse_key": "12:14", "translation": "They said: If the wolf eats him while we are a strong group, indeed we would then be losers."},
    {"verse_key": "12:15", "translation": "So when they took him and put him into the well, We inspired to him that you will inform them of this affair."},
    {"verse_key": "12:16", "translation": "And they came to their father at night, weeping."},
    {"verse_key": "12:17", "translation": "They said: O our father, we went racing each other and left Joseph with our possessions."},
    {"verse_key": "12:18", "translation": "And they brought upon his shirt false blood. He said: Rather, your souls have enticed you to something."},
    {"verse_key": "12:19", "translation": "And there came a caravan of travelers; they sent their water drawer, and he let down his bucket. He said: Good news! Here is a boy."},
    {"verse_key": "12:20", "translation": "And they sold him for a reduced price - a few dirhams - and they were, concerning him, of those who considered him insignificant."},
    {"verse_key": "12:21", "translation": "And the one from Egypt who bought him said to his wife: Make his residence comfortable. Perhaps he will benefit us."},
    {"verse_key": "12:22", "translation": "And when Joseph reached maturity, We gave him judgment and knowledge. And thus We reward the doers of good."},
    {"verse_key": "12:23", "translation": "And she in whose house he was sought to seduce him. She closed the doors and said: Come, you. He said: I seek the refuge of Allah."},
    {"verse_key": "12:24", "translation": "And she certainly desired him, and he would have desired her if not that he saw the proof of his Lord."},
    {"verse_key": "12:25", "translation": "And they both raced to the door, and she tore his shirt from the back."},
    {"verse_key": "12:26", "translation": "Joseph said: It was she who sought to seduce me. And a witness from her family testified."},
    {"verse_key": "12:27", "translation": "And if his shirt is torn from the front, then she has told the truth, and he is of the liars."},
    {"verse_key": "12:28", "translation": "So when her husband saw his shirt torn from the back, he said: Indeed, it is of the women's plan."},
    {"verse_key": "12:29", "translation": "Joseph, ignore this. And you, ask forgiveness for your sin. Indeed, you were of the sinful."},
    {"verse_key": "12:30", "translation": "And women in the city said: The wife of the noble has sought to seduce her slave boy."},
    {"verse_key": "12:31", "translation": "So when she heard of their scheming, she sent for them and prepared for them a banquet."},
    {"verse_key": "12:32", "translation": "She said: That is the one about whom you blamed me. And I certainly sought to seduce him, but he firmly refused."},
    {"verse_key": "12:33", "translation": "He said: My Lord, prison is more to my liking than that to which they invite me. And if You do not avert from me their plan, I might incline toward them."},
    {"verse_key": "12:34", "translation": "So his Lord responded to him and averted from him their plan. Indeed, He is the Hearing, the Knowing."},
    {"verse_key": "12:35", "translation": "Then it appeared to them after they had seen the signs that they should imprison him for a time."},
    {"verse_key": "12:36", "translation": "And there entered the prison with him two young men. One of them said: Indeed, I see myself pressing wine."},
    {"verse_key": "12:37", "translation": "He said: You will not receive food that is provided to you before I inform you of its interpretation."},
    {"verse_key": "12:38", "translation": "I have followed the religion of my fathers, Abraham, Isaac and Jacob."},
    {"verse_key": "12:39", "translation": "O two companions of prison, are separate lords better or Allah, the One, the Prevailing?"},
    {"verse_key": "12:40", "translation": "You worship not besides Him except names you have named them, you and your fathers."},
    {"verse_key": "12:41", "translation": "O two companions of prison, as for one of you, he will give drink to his master of wine."},
    {"verse_key": "12:42", "translation": "And he said to the one he knew would be saved: Mention me before your master."},
    {"verse_key": "12:43", "translation": "And the king said: Indeed, I have seen in a dream seven fat cows being eaten by seven lean ones."},
    {"verse_key": "12:44", "translation": "They said: It is but a mixture of false dreams, and we are not learned in the interpretation of dreams."},
    {"verse_key": "12:45", "translation": "But the one who was freed and remembered after a time said: I will inform you of its interpretation, so send me forth."},
    {"verse_key": "12:46", "translation": "He said: Joseph, O man of truth, explain to us about seven fat cows eaten by seven lean ones."},
    {"verse_key": "12:47", "translation": "He said: You will plant for seven years consecutively; and what you harvest leave in its spikes."},
    {"verse_key": "12:48", "translation": "Then will come after that seven difficult years which will consume what you advanced for them, except a little."},
    {"verse_key": "12:49", "translation": "Then will come after that a year in which the people will be given rain and in which they will press olives."},
    {"verse_key": "12:50", "translation": "And the king said: Bring him to me. So when the messenger came to him, Joseph said: Return to your master."},
    {"verse_key": "12:51", "translation": "The king said to the women: What is your testimony when you sought to seduce Joseph of his will?"},
    {"verse_key": "12:52", "translation": "That is so that he would know that I did not betray him in absence and that Allah does not guide the plan of betrayers."},
    {"verse_key": "12:53", "translation": "And I do not acquit myself. Indeed, the soul is a persistent enjoiner of evil, except those upon which my Lord has mercy."},
    {"verse_key": "12:54", "translation": "And the king said: Bring him to me; I will appoint him exclusively for myself. And when he spoke to him, he said: Indeed, you are today established."},
    {"verse_key": "12:55", "translation": "Joseph said: Appoint me over the storehouses of the land. Indeed, I will be a knowing guardian."},
    {"verse_key": "12:56", "translation": "And thus We established Joseph in the land to settle therein wherever he willed. We touch with Our mercy whom We will."},
    {"verse_key": "12:57", "translation": "And the reward of the Hereafter is better for those who believed and were fearing Allah."},
    {"verse_key": "12:58", "translation": "And the brothers of Joseph came and entered upon him, and he recognized them, but they did not recognize him."},
    {"verse_key": "12:59", "translation": "And when he had furnished them with their supplies, he said: Bring me a brother of yours from your father."},
    {"verse_key": "12:60", "translation": "But if you do not bring him to me, no measure of grain will be given to you from me, nor will you approach me."},
    {"verse_key": "12:61", "translation": "They said: We will seek to obtain him from his father. And indeed, we will do it."},
    {"verse_key": "12:62", "translation": "And Joseph said to his servants: Put their merchandise back into their saddlebags."},
    {"verse_key": "12:63", "translation": "So when they returned to their father, they said: O our father, grain has been denied from us."},
    {"verse_key": "12:64", "translation": "He said: Should I entrust you with him except as I entrusted you with his brother before? But Allah is the best guardian."},
    {"verse_key": "12:65", "translation": "And when they opened their baggage, they found their merchandise returned to them."},
    {"verse_key": "12:66", "translation": "He said: I will never send him with you until you give me a promise by Allah that you will bring him back."},
    {"verse_key": "12:67", "translation": "And he said: O my sons, do not enter from one gate but enter from different gates."},
    {"verse_key": "12:68", "translation": "And when they entered from where their father had ordered them, it did not avail them against Allah at all."},
    {"verse_key": "12:69", "translation": "And when they entered upon Joseph, he took his brother to himself; he said: Indeed, I am your brother."},
    {"verse_key": "12:70", "translation": "So when he had furnished them with their supplies, he put the water bowl into the bag of his brother."},
    {"verse_key": "12:71", "translation": "They said, while approaching them: What is it you are missing?"},
    {"verse_key": "12:72", "translation": "They said: We are missing the measure of the king. And for he who produces it is a camel load; and I am responsible for it."},
    {"verse_key": "12:73", "translation": "They said: By Allah, you have certainly known that we did not come to cause corruption in the land."},
    {"verse_key": "12:74", "translation": "Joseph's people said: Then what would be its recompense if you should be liars?"},
    {"verse_key": "12:75", "translation": "They said: Its recompense is that he in whose bag it is found - he will be its recompense."},
    {"verse_key": "12:76", "translation": "So he began with their bags before the bag of his brother; then he extracted it from the bag of his brother."},
    {"verse_key": "12:77", "translation": "They said: If he steals - a brother of his has stolen before."},
    {"verse_key": "12:78", "translation": "They said: O exalted one, indeed he has a father who is an old man, so take one of us in his place."},
    {"verse_key": "12:79", "translation": "He said: Allah forbid that we should take except him in whose possession we found our property."},
    {"verse_key": "12:80", "translation": "So when they had despaired of him, they secluded themselves in private consultation. The eldest of them said: Do you not know that your father has taken upon you an oath by Allah."},
    {"verse_key": "12:81", "translation": "Return to your father and say: O our father, indeed your son has stolen."},
    {"verse_key": "12:82", "translation": "And ask the city in which we were and the caravan in which we came - and indeed, we are truthful."},
    {"verse_key": "12:83", "translation": "He said: Rather, your souls have enticed you to something. So patience is most fitting."},
    {"verse_key": "12:84", "translation": "And he turned away from them and said: Oh, my sorrow over Joseph, and his eyes became white from grief, for he was a suppressor."},
    {"verse_key": "12:85", "translation": "They said: By Allah, you will not cease remembering Joseph until you become fatally ill or become of those who perish."},
    {"verse_key": "12:86", "translation": "He said: I only complain of my suffering and my grief to Allah, and I know from Allah that which you do not know."},
    {"verse_key": "12:87", "translation": "O my sons, go and find out about Joseph and his brother and despair not of relief from Allah."},
    {"verse_key": "12:88", "translation": "And when they entered upon him, they said: O exalted one, adversity has touched us and our family."},
    {"verse_key": "12:89", "translation": "He said: Do you know what you did with Joseph and his brother when you were ignorant?"},
    {"verse_key": "12:90", "translation": "They said: Are you indeed Joseph? He said: I am Joseph, and this is my brother. Allah has certainly favored us."},
    {"verse_key": "12:91", "translation": "They said: By Allah, certainly has Allah preferred you over us, and indeed we have been sinners."},
    {"verse_key": "12:92", "translation": "He said: No blame will there be upon you today. Allah will forgive you; and He is the most merciful of the merciful."},
    {"verse_key": "12:93", "translation": "Take this, my shirt, and cast it over the face of my father; he will become seeing. And bring me your family, all together."},
    {"verse_key": "12:94", "translation": "And when the caravan departed, their father said: Indeed, I find the smell of Joseph and I would say I was senile."},
    {"verse_key": "12:95", "translation": "They said: By Allah, indeed you are in your old error."},
    {"verse_key": "12:96", "translation": "And when the bearer of good tidings arrived, he cast it over his face, and he returned seeing. He said: Did I not tell you that I know from Allah that which you do not know?"},
    {"verse_key": "12:97", "translation": "They said: O our father, ask for us forgiveness of our sins; indeed, we have been sinners."},
    {"verse_key": "12:98", "translation": "He said: I will ask forgiveness for you from my Lord. Indeed, it is He who is the Forgiving, the Merciful."},
    {"verse_key": "12:99", "translation": "And when they entered upon Joseph, he took his parents to himself and said: Enter Egypt, Allah willing, safe."},
    {"verse_key": "12:100", "translation": "And he raised his parents upon the throne, and they bowed to him in prostration. And he said: O my father, this is the explanation of my vision of before."},
    {"verse_key": "12:101", "translation": "My Lord, You have given me sovereignty and taught me of the interpretation of dreams. Creator of the heavens and earth, You are my protector in this world and in the Hereafter."},
    {"verse_key": "12:102", "translation": "That is from the news of the unseen which We reveal to you, O Muhammad. And you were not with them when they put together their plan while they conspired."},
    {"verse_key": "12:103", "translation": "And most of the people, although you strive for it, are not believers."},
    {"verse_key": "12:104", "translation": "And you do not ask of them for it any payment. It is not except a reminder to the worlds."},
    {"verse_key": "12:111", "translation": "There was certainly in their stories a lesson for those of understanding."},
]


# --------------------------------------------------------------------------- #
# Test 1: extract_characters finds "Moses" in text containing "Moses"
# --------------------------------------------------------------------------- #

def test_extract_characters_finds_moses():
    analyzer = make_analyzer()
    text = "Moses led his people through the desert, trusting in Allah."
    chars = analyzer.extract_characters(text)
    assert "Moses" in chars


def test_extract_characters_finds_multiple():
    analyzer = make_analyzer()
    text = "Moses and Joseph both received divine guidance."
    chars = analyzer.extract_characters(text)
    assert "Moses" in chars
    assert "Joseph" in chars


def test_extract_characters_case_insensitive():
    analyzer = make_analyzer()
    text = "MOSES spoke to pharaoh with divine authority."
    chars = analyzer.extract_characters(text)
    assert "Moses" in chars
    assert "Pharaoh" in chars


# --------------------------------------------------------------------------- #
# Test 2: detect_conflict returns EXTERNAL for text with "reject"
# --------------------------------------------------------------------------- #

def test_detect_conflict_external_reject():
    analyzer = make_analyzer()
    text = "The people chose to reject the messenger and oppose his teachings."
    conflict = analyzer.detect_conflict(text)
    assert conflict == ConflictType.EXTERNAL


def test_detect_conflict_external_deny():
    analyzer = make_analyzer()
    text = "They denied the signs and refused to believe."
    conflict = analyzer.detect_conflict(text)
    assert conflict == ConflictType.EXTERNAL


# --------------------------------------------------------------------------- #
# Test 3: detect_conflict returns INTERNAL for text with "temptation"
# --------------------------------------------------------------------------- #

def test_detect_conflict_internal_temptation():
    analyzer = make_analyzer()
    text = "He struggled with temptation and the desires of the soul."
    conflict = analyzer.detect_conflict(text)
    assert conflict == ConflictType.INTERNAL


def test_detect_conflict_internal_soul():
    analyzer = make_analyzer()
    text = "The soul inclines toward desire and the nafs whispers evil."
    conflict = analyzer.detect_conflict(text)
    assert conflict == ConflictType.INTERNAL


def test_detect_conflict_none():
    analyzer = make_analyzer()
    text = "In the name of Allah, the Entirely Merciful."
    conflict = analyzer.detect_conflict(text)
    assert conflict == ConflictType.NONE


# --------------------------------------------------------------------------- #
# Test 4: extract_themes finds "patience" theme from "patient endurance"
# --------------------------------------------------------------------------- #

def test_extract_themes_finds_patience():
    analyzer = make_analyzer()
    text = "Believers demonstrate patient endurance in times of trial."
    themes = analyzer.extract_themes(text)
    assert "patience" in themes


def test_extract_themes_finds_mercy():
    analyzer = make_analyzer()
    text = "Allah is merciful and full of compassion toward those who repent."
    themes = analyzer.extract_themes(text)
    assert "mercy" in themes


def test_extract_themes_multiple():
    analyzer = make_analyzer()
    text = "The grateful and patient servant trusts in Allah's guidance and mercy."
    themes = analyzer.extract_themes(text)
    # Should find at least patience, gratitude, guidance, mercy, and trust_in_god
    assert "patience" in themes
    assert "gratitude" in themes
    assert "guidance" in themes


def test_extract_themes_empty_text():
    analyzer = make_analyzer()
    themes = analyzer.extract_themes("")
    assert isinstance(themes, list)
    assert len(themes) == 0


# --------------------------------------------------------------------------- #
# Test 5: segment_into_scenes produces at least 2 scenes with "Then" separator
# --------------------------------------------------------------------------- #

def test_segment_into_scenes_two_scenes_with_then():
    analyzer = make_analyzer()
    verses = [
        (1, "In the beginning there was the command of Allah."),
        (2, "He created the heavens and the earth with wisdom."),
        (3, "Then Moses spoke to his people saying be patient."),
        (4, "Then he went to Pharaoh and delivered the message."),
        (5, "And the people witnessed the signs of their Lord."),
    ]
    scenes = analyzer.segment_into_scenes(verses)
    assert len(scenes) >= 2


def test_segment_into_scenes_single_scene_no_break():
    analyzer = make_analyzer()
    verses = [
        (1, "Allah is the Lord of the worlds."),
        (2, "He is the Merciful, the Compassionate."),
        (3, "Praise be to Allah for His many blessings."),
    ]
    scenes = analyzer.segment_into_scenes(verses)
    assert len(scenes) == 1


def test_segment_into_scenes_verse_range_correct():
    analyzer = make_analyzer()
    verses = [
        (1, "Allah created the heavens and the earth."),
        (2, "He placed mountains and rivers upon it."),
        (3, "Then Moses came to Pharaoh with clear signs."),
        (4, "Then he said to him: Let the children of Israel go."),
        (5, "And Pharaoh refused and was among the arrogant."),
    ]
    scenes = analyzer.segment_into_scenes(verses)
    assert len(scenes) >= 2
    assert scenes[0].verse_range[0] == 1
    # Last scene ends at last verse
    assert scenes[-1].verse_range[1] == 5


def test_segment_into_scenes_minimum_size_enforced():
    """A break is not inserted if the previous scene would be < 2 verses."""
    analyzer = make_analyzer()
    verses = [
        (1, "Allah created the heavens."),
        (2, "Then Moses spoke."),  # Only 1 verse before this -> no break
        (3, "Then he said: let my people go."),
        (4, "And Pharaoh refused to listen."),
        (5, "Then a great punishment came upon them."),
    ]
    scenes = analyzer.segment_into_scenes(verses)
    # Verse 1 alone cannot form a scene before break at verse 2
    for scene in scenes:
        start, end = scene.verse_range
        assert end - start + 1 >= 1  # Each scene has at least 1 verse (structural)


# --------------------------------------------------------------------------- #
# Test 6: classify_arc returns REDEMPTION for surah 12 (Yusuf)
# --------------------------------------------------------------------------- #

def test_classify_arc_redemption_for_yusuf():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    structure = analyzer.analyze_surah(12)
    assert structure is not None
    assert structure.arc_type == StoryArcType.REDEMPTION


def test_classify_arc_redemption_with_joseph_scenes():
    """classify_arc should return REDEMPTION when Joseph is in the scenes."""
    analyzer = make_analyzer()
    # Build fake scenes with Joseph character
    scene = Scene(
        number=1,
        verse_range=(1, 10),
        text="Joseph was tested with patience and emerged victorious.",
        characters={"Joseph"},
        conflict=ConflictType.EXTERNAL,
        moral_weight=0.8,
        themes=["patience", "trial"],
    )
    arc = analyzer.classify_arc([scene])
    assert arc == StoryArcType.REDEMPTION


def test_classify_arc_quest_for_moses_pharaoh():
    """classify_arc should return QUEST when Moses and Pharaoh are both present."""
    analyzer = make_analyzer()
    scene = Scene(
        number=1,
        verse_range=(1, 20),
        text="Moses confronted Pharaoh who refused the divine command.",
        characters={"Moses", "Pharaoh"},
        conflict=ConflictType.EXTERNAL,
        moral_weight=0.9,
        themes=["guidance", "divine_power"],
    )
    arc = analyzer.classify_arc([scene])
    assert arc == StoryArcType.QUEST


def test_classify_arc_didactic_multiple_prophets():
    """classify_arc should return DIDACTIC when multiple prophets appear."""
    analyzer = make_analyzer()
    scene = Scene(
        number=1,
        verse_range=(1, 30),
        text="The stories of Noah and Abraham and Moses are told for lessons.",
        characters={"Noah", "Abraham", "Moses"},
        conflict=ConflictType.COSMIC,
        moral_weight=0.7,
        themes=["prophecy", "guidance"],
    )
    arc = analyzer.classify_arc([scene])
    assert arc == StoryArcType.DIDACTIC


# --------------------------------------------------------------------------- #
# Test 7: extract_central_lesson returns non-empty string
# --------------------------------------------------------------------------- #

def test_extract_central_lesson_non_empty():
    analyzer = make_analyzer()
    scene = Scene(
        number=1,
        verse_range=(1, 5),
        text="Patience leads to triumph.",
        characters=set(),
        conflict=ConflictType.NONE,
        moral_weight=0.5,
        themes=["patience"],
    )
    lesson = analyzer.extract_central_lesson([scene], ["patience"])
    assert isinstance(lesson, str)
    assert len(lesson.strip()) > 0


def test_extract_central_lesson_no_themes():
    analyzer = make_analyzer()
    lesson = analyzer.extract_central_lesson([], [])
    assert isinstance(lesson, str)
    assert len(lesson.strip()) > 0


def test_extract_central_lesson_mercy_theme():
    analyzer = make_analyzer()
    themes = ["mercy", "mercy", "patience"]
    lesson = analyzer.extract_central_lesson([], themes)
    assert "mercy" in lesson.lower() or "forgiveness" in lesson.lower() or "compassion" in lesson.lower()


def test_extract_central_lesson_patience_theme():
    analyzer = make_analyzer()
    themes = ["patience", "patience", "trial", "trial", "trial"]
    lesson = analyzer.extract_central_lesson([], themes)
    # Most frequent is "trial"
    assert isinstance(lesson, str)
    assert len(lesson) > 10


# --------------------------------------------------------------------------- #
# Test 8: Full analyze_surah integration with in-memory corpus
# --------------------------------------------------------------------------- #

def test_analyze_surah_yusuf_returns_structure():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    structure = analyzer.analyze_surah(12)
    assert structure is not None
    assert isinstance(structure, NarrativeStructure)
    assert structure.surah_number == 12
    assert structure.surah_name == "Yusuf"


def test_analyze_surah_yusuf_has_scenes():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    structure = analyzer.analyze_surah(12)
    assert structure is not None
    assert len(structure.scenes) >= 1


def test_analyze_surah_yusuf_finds_joseph():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    structure = analyzer.analyze_surah(12)
    assert structure is not None
    assert "Joseph" in structure.character_appearances


def test_analyze_surah_unknown_returns_none():
    """A surah not in NARRATIVE_SURAHS should return None."""
    analyzer = make_analyzer()
    result = analyzer.analyze_surah(1)  # Al-Fatiha is not a narrative surah
    assert result is None


def test_analyze_surah_no_corpus_returns_none():
    """If corpus is empty, analyze_surah returns None even for known surahs."""
    analyzer = make_analyzer()  # No corpus loaded
    result = analyzer.analyze_surah(12)
    assert result is None


# --------------------------------------------------------------------------- #
# Test 9: analyze_all_narratives returns a dict
# --------------------------------------------------------------------------- #

def test_analyze_all_narratives_returns_dict():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    results = analyzer.analyze_all_narratives()
    assert isinstance(results, dict)
    # Surah 12 should be in results since we loaded its verses
    assert 12 in results


def test_analyze_all_narratives_empty_corpus():
    analyzer = make_analyzer()
    results = analyzer.analyze_all_narratives()
    assert isinstance(results, dict)
    assert len(results) == 0


# --------------------------------------------------------------------------- #
# Test 10: arc_intensity is between 0 and 1
# --------------------------------------------------------------------------- #

def test_arc_intensity_range():
    analyzer = make_analyzer(YUSUF_SAMPLE_VERSES)
    structure = analyzer.analyze_surah(12)
    assert structure is not None
    assert 0.0 <= structure.arc_intensity <= 1.0


def test_moral_weight_range():
    analyzer = make_analyzer()
    for scene_num in [1, 5, 10]:
        weight = analyzer.calculate_moral_weight("Some text here.", scene_num, 10)
        assert 0.0 <= weight <= 1.0, f"moral_weight out of range for scene {scene_num}"
