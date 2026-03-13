"""Comprehensive Quranic Arabic Morphological Lexicon."""
from dataclasses import dataclass
from typing import Dict, List, Optional
import re


@dataclass
class MorphEntry:
    word: str
    root: str
    pattern: str
    pos: str          # noun, verb, particle, adjective, pronoun
    form: Optional[int] = None   # verb form 1-10
    gloss: str = ""


# Full morphological database: root -> list of derived words
MORPHOLOGY_LEXICON: Dict[str, List[MorphEntry]] = {

    "رحم": [
        MorphEntry("رحمن", "رحم", "فَعْلَان", "adjective", gloss="Most Merciful"),
        MorphEntry("رحيم", "رحم", "فَعِيل", "adjective", gloss="Especially Merciful"),
        MorphEntry("رحمة", "رحم", "فَعْلَة", "noun", gloss="mercy"),
        MorphEntry("رحم", "رحم", "فَعَلَ", "verb", 1, "to have mercy"),
        MorphEntry("مرحوم", "رحم", "مَفْعُول", "adjective", gloss="shown mercy"),
        MorphEntry("يرحم", "رحم", "يَفْعَل", "verb", 1, "he has mercy"),
        MorphEntry("الرحمن", "رحم", "الفَعْلَان", "adjective", gloss="the Most Merciful"),
    ],

    "حمد": [
        MorphEntry("حمد", "حمد", "فَعَلَ", "verb", 1, "to praise"),
        MorphEntry("محمد", "حمد", "مُفَعَّل", "noun", gloss="praised one"),
        MorphEntry("أحمد", "حمد", "أَفْعَل", "adjective", gloss="most praiseworthy"),
        MorphEntry("حامد", "حمد", "فَاعِل", "noun", gloss="one who praises"),
        MorphEntry("محمود", "حمد", "مَفْعُول", "adjective", gloss="praised"),
        MorphEntry("حمدا", "حمد", "فَعْلاً", "noun", gloss="praise (acc)"),
        MorphEntry("يحمد", "حمد", "يَفْعَل", "verb", 1, "he praises"),
    ],

    "ربب": [
        MorphEntry("رب", "ربب", "فَعْل", "noun", gloss="Lord"),
        MorphEntry("رباني", "ربب", "فَعَّالِي", "adjective", gloss="lordly, rabbinical"),
        MorphEntry("ربوبية", "ربب", "فَعُولِيَّة", "noun", gloss="lordship"),
        MorphEntry("ربيون", "ربب", "فَعِيُّون", "noun", gloss="lords (plural)"),
        MorphEntry("المربي", "ربب", "المُفَعِّل", "noun", gloss="the nurturer"),
    ],

    "علم": [
        MorphEntry("عالم", "علم", "فَاعِل", "noun", gloss="scholar, world"),
        MorphEntry("عليم", "علم", "فَعِيل", "adjective", gloss="all-knowing"),
        MorphEntry("معلوم", "علم", "مَفْعُول", "adjective", gloss="known"),
        MorphEntry("علم", "علم", "فَعَلَ", "verb", 1, "to know"),
        MorphEntry("تعليم", "علم", "تَفْعِيل", "noun", gloss="education"),
        MorphEntry("عالمين", "علم", "فَاعِلِين", "noun", gloss="worlds, all beings"),
        MorphEntry("معلم", "علم", "مُفَعِّل", "noun", gloss="teacher"),
        MorphEntry("علوم", "علم", "فُعُول", "noun", gloss="sciences"),
    ],

    "ملك": [
        MorphEntry("ملك", "ملك", "فَعَلَ", "verb", 1, "to own, possess"),
        MorphEntry("مالك", "ملك", "فَاعِل", "noun", gloss="owner, possessor"),
        MorphEntry("مملكة", "ملك", "مَفْعَلَة", "noun", gloss="kingdom"),
        MorphEntry("ملكوت", "ملك", "فَعَلُوت", "noun", gloss="dominion"),
        MorphEntry("ملوك", "ملك", "فُعُول", "noun", gloss="kings"),
        MorphEntry("مملوك", "ملك", "مَفْعُول", "noun", gloss="owned, slave"),
        MorphEntry("ملائكة", "ملك", "فَعَائِلَة", "noun", gloss="angels"),
        MorphEntry("ملك", "ملك", "فَعْل", "noun", gloss="king"),
    ],

    "دين": [
        MorphEntry("دين", "دين", "فَعْل", "noun", gloss="religion, way of life"),
        MorphEntry("ديان", "دين", "فَيْعَال", "adjective", gloss="one who judges"),
        MorphEntry("مدين", "دين", "مَفْعُول", "adjective", gloss="indebted"),
        MorphEntry("دان", "دين", "فَعَلَ", "verb", 1, "to judge, to be indebted"),
        MorphEntry("يدين", "دين", "يَفْعَل", "verb", 1, "he judges"),
    ],

    "عبد": [
        MorphEntry("عبد", "عبد", "فَعَلَ", "verb", 1, "to worship"),
        MorphEntry("عبادة", "عبد", "فَعَالَة", "noun", gloss="worship"),
        MorphEntry("عابد", "عبد", "فَاعِل", "noun", gloss="worshipper"),
        MorphEntry("معبود", "عبد", "مَفْعُول", "noun", gloss="the worshipped"),
        MorphEntry("عبيد", "عبد", "فَعِيل", "noun", gloss="slaves (plural)"),
        MorphEntry("عباد", "عبد", "فِعَال", "noun", gloss="servants of God"),
        MorphEntry("تعبد", "عبد", "تَفَعُّل", "noun", gloss="devotion"),
    ],

    "صلو": [
        MorphEntry("صلاة", "صلو", "فَعَالَة", "noun", gloss="prayer"),
        MorphEntry("صلى", "صلو", "فَعَّلَ", "verb", 2, "to pray"),
        MorphEntry("مصلى", "صلو", "مُفَعَّل", "noun", gloss="prayer place"),
        MorphEntry("مصلون", "صلو", "مُفَعِّلُون", "noun", gloss="those who pray"),
        MorphEntry("يصلون", "صلو", "يُفَعُّون", "verb", 2, "they pray"),
        MorphEntry("صلوات", "صلو", "فَعَلَات", "noun", gloss="prayers (plural)"),
    ],

    "سجد": [
        MorphEntry("سجود", "سجد", "فُعُول", "noun", gloss="prostration"),
        MorphEntry("ساجد", "سجد", "فَاعِل", "noun", gloss="one prostrating"),
        MorphEntry("مسجد", "سجد", "مَفْعَل", "noun", gloss="mosque"),
        MorphEntry("سجدة", "سجد", "فَعْلَة", "noun", gloss="a single prostration"),
        MorphEntry("يسجد", "سجد", "يَفْعَل", "verb", 1, "he prostrates"),
        MorphEntry("اسجد", "سجد", "اُفْعُل", "verb", 1, "prostrate!"),
    ],

    "زكو": [
        MorphEntry("زكاة", "زكو", "فَعَالَة", "noun", gloss="purifying alms"),
        MorphEntry("زكي", "زكو", "فَعِيل", "adjective", gloss="pure, righteous"),
        MorphEntry("يزكو", "زكو", "يَفْعُل", "verb", 1, "he purifies"),
        MorphEntry("تزكية", "زكو", "تَفْعِيل", "noun", gloss="purification"),
        MorphEntry("مزكي", "زكو", "مُفَعِّل", "noun", gloss="one who purifies"),
    ],

    "هدي": [
        MorphEntry("هداية", "هدي", "فَعَالَة", "noun", gloss="guidance"),
        MorphEntry("هادي", "هدي", "فَاعِل", "adjective", gloss="guide"),
        MorphEntry("مهدي", "هدي", "مَفْعُول", "adjective", gloss="guided one"),
        MorphEntry("هدى", "هدي", "فَعَلَ", "verb", 1, "to guide"),
        MorphEntry("يهدي", "هدي", "يَفْعِل", "verb", 1, "he guides"),
        MorphEntry("اهتداء", "هدي", "اِفْتِعَال", "noun", gloss="being guided"),
    ],

    "صرط": [
        MorphEntry("صراط", "صرط", "فِعَال", "noun", gloss="path, way"),
        MorphEntry("المستقيم", "صرط", "المُسْتَفْعِل", "adjective", gloss="the straight"),
    ],

    "قوم": [
        MorphEntry("قوم", "قوم", "فَعْل", "noun", gloss="people, nation"),
        MorphEntry("قيام", "قوم", "فِعَال", "noun", gloss="standing, rising"),
        MorphEntry("قائم", "قوم", "فَاعِل", "noun", gloss="standing one"),
        MorphEntry("مقيم", "قوم", "مُفِيل", "adjective", gloss="residing"),
        MorphEntry("أقام", "قوم", "أَفْعَلَ", "verb", 4, "to establish"),
        MorphEntry("استقام", "قوم", "اِسْتَفْعَلَ", "verb", 10, "to be upright"),
        MorphEntry("قيامة", "قوم", "فِعَالَة", "noun", gloss="resurrection"),
        MorphEntry("قام", "قوم", "فَعَلَ", "verb", 1, "to stand up"),
    ],

    "أمن": [
        MorphEntry("أمن", "أمن", "فَعَلَ", "verb", 1, "to be safe, to believe"),
        MorphEntry("مؤمن", "أمن", "مُفْعِل", "noun", gloss="believer"),
        MorphEntry("مؤمنون", "أمن", "مُفْعِلُون", "noun", gloss="believers (plural)"),
        MorphEntry("إيمان", "أمن", "إِفْعَال", "noun", gloss="faith, belief"),
        MorphEntry("أمانة", "أمن", "فَعَالَة", "noun", gloss="trustworthiness"),
        MorphEntry("آمن", "أمن", "فَاعَلَ", "verb", 3, "to believe"),
        MorphEntry("أمين", "أمن", "فَعِيل", "adjective", gloss="trustworthy"),
        MorphEntry("أمان", "أمن", "فَعَال", "noun", gloss="safety, peace"),
    ],

    "كفر": [
        MorphEntry("كفر", "كفر", "فَعَلَ", "verb", 1, "to disbelieve, cover"),
        MorphEntry("كافر", "كفر", "فَاعِل", "noun", gloss="disbeliever"),
        MorphEntry("كفران", "كفر", "فَعْلَان", "noun", gloss="ingratitude"),
        MorphEntry("كفور", "كفر", "فَعُول", "adjective", gloss="very ungrateful"),
        MorphEntry("كافرون", "كفر", "فَاعِلُون", "noun", gloss="disbelievers"),
        MorphEntry("كفارة", "كفر", "فَعَالَة", "noun", gloss="expiation, atonement"),
    ],

    "نفق": [
        MorphEntry("منافق", "نفق", "مُفَاعِل", "noun", gloss="hypocrite"),
        MorphEntry("نفاق", "نفق", "فِعَال", "noun", gloss="hypocrisy"),
        MorphEntry("منافقون", "نفق", "مُفَاعِلُون", "noun", gloss="hypocrites"),
        MorphEntry("نافق", "نفق", "فَاعَلَ", "verb", 3, "to be hypocritical"),
    ],

    "قرأ": [
        MorphEntry("قرآن", "قرأ", "فُعْلَان", "noun", gloss="the Quran, recitation"),
        MorphEntry("قارئ", "قرأ", "فَاعِل", "noun", gloss="reciter, reader"),
        MorphEntry("مقروء", "قرأ", "مَفْعُول", "adjective", gloss="read, recited"),
        MorphEntry("قراءة", "قرأ", "فِعَالَة", "noun", gloss="reading, recitation"),
        MorphEntry("قرأ", "قرأ", "فَعَلَ", "verb", 1, "to read, recite"),
        MorphEntry("اقرأ", "قرأ", "اِفْعَل", "verb", 1, "read! recite!"),
    ],

    "كتب": [
        MorphEntry("كتاب", "كتب", "فِعَال", "noun", gloss="book"),
        MorphEntry("كاتب", "كتب", "فَاعِل", "noun", gloss="writer"),
        MorphEntry("مكتوب", "كتب", "مَفْعُول", "adjective", gloss="written"),
        MorphEntry("كتابة", "كتب", "فِعَالَة", "noun", gloss="writing"),
        MorphEntry("مكتبة", "كتب", "مَفْعَلَة", "noun", gloss="library"),
        MorphEntry("كتب", "كتب", "فَعَلَ", "verb", 1, "to write"),
        MorphEntry("كتب", "كتب", "فُعُل", "noun", gloss="books (plural)"),
        MorphEntry("كتيبة", "كتب", "فَعِيلَة", "noun", gloss="regiment, battalion"),
    ],

    "خلق": [
        MorphEntry("خلق", "خلق", "فَعَلَ", "verb", 1, "to create"),
        MorphEntry("خالق", "خلق", "فَاعِل", "noun", gloss="creator"),
        MorphEntry("مخلوق", "خلق", "مَفْعُول", "noun", gloss="created being"),
        MorphEntry("خلق", "خلق", "فَعْل", "noun", gloss="character, creation"),
        MorphEntry("خلقة", "خلق", "فَعْلَة", "noun", gloss="nature, constitution"),
        MorphEntry("خلائق", "خلق", "فَعَائِل", "noun", gloss="creatures (plural)"),
    ],

    "سمو": [
        MorphEntry("اسم", "سمو", "اِفْعَل", "noun", gloss="name"),
        MorphEntry("سماء", "سمو", "فَعَاء", "noun", gloss="sky, heaven"),
        MorphEntry("سمي", "سمو", "فَعِيل", "adjective", gloss="namesake"),
        MorphEntry("تسمية", "سمو", "تَفْعِيل", "noun", gloss="naming"),
        MorphEntry("بسم", "سمو", "بِفَعْل", "particle", gloss="in the name of"),
        MorphEntry("أسماء", "سمو", "أَفْعَال", "noun", gloss="names (plural)"),
    ],

    "أرض": [
        MorphEntry("أرض", "أرض", "فَعْل", "noun", gloss="earth, land"),
        MorphEntry("أراضي", "أرض", "أَفَاعِل", "noun", gloss="lands (plural)"),
        MorphEntry("أرضي", "أرض", "فَعْلِي", "adjective", gloss="earthly"),
    ],

    "حيي": [
        MorphEntry("حياة", "حيي", "فَعَالَة", "noun", gloss="life"),
        MorphEntry("حي", "حيي", "فَعِيل", "adjective", gloss="alive"),
        MorphEntry("أحيا", "حيي", "أَفْعَلَ", "verb", 4, "to give life"),
        MorphEntry("يحيى", "حيي", "يَفْعَل", "verb", 1, "he lives"),
        MorphEntry("محيي", "حيي", "مُفْعِل", "noun", gloss="giver of life"),
        MorphEntry("حيوان", "حيي", "فَيْعَلَان", "noun", gloss="animal, creature"),
    ],

    "موت": [
        MorphEntry("موت", "موت", "فَعْل", "noun", gloss="death"),
        MorphEntry("ميت", "موت", "فَيْعِل", "adjective", gloss="dead"),
        MorphEntry("مات", "موت", "فَعَلَ", "verb", 1, "to die"),
        MorphEntry("يموت", "موت", "يَفْعُل", "verb", 1, "he dies"),
        MorphEntry("إماتة", "موت", "إِفْعَالَة", "noun", gloss="causing death"),
        MorphEntry("مميت", "موت", "مُفِيل", "noun", gloss="giver of death"),
    ],

    "آخر": [
        MorphEntry("آخر", "آخر", "فَاعِل", "adjective", gloss="other, last"),
        MorphEntry("آخرة", "آخر", "فَاعِلَة", "noun", gloss="the hereafter"),
        MorphEntry("أخير", "آخر", "فَعِيل", "adjective", gloss="last, final"),
        MorphEntry("تأخير", "آخر", "تَفْعِيل", "noun", gloss="delay"),
        MorphEntry("أخر", "آخر", "فُعَل", "adjective", gloss="others (plural)"),
    ],

    "عدل": [
        MorphEntry("عدل", "عدل", "فَعَلَ", "verb", 1, "to be just"),
        MorphEntry("عادل", "عدل", "فَاعِل", "adjective", gloss="just"),
        MorphEntry("عدالة", "عدل", "فَعَالَة", "noun", gloss="justice"),
        MorphEntry("معدل", "عدل", "مُفَعِّل", "noun", gloss="rate, adjuster"),
        MorphEntry("عدل", "عدل", "فَعْل", "noun", gloss="justice"),
        MorphEntry("يعدل", "عدل", "يَفْعِل", "verb", 1, "he is just"),
    ],

    "ظلم": [
        MorphEntry("ظلم", "ظلم", "فَعَلَ", "verb", 1, "to wrong, oppress"),
        MorphEntry("ظالم", "ظلم", "فَاعِل", "noun", gloss="wrongdoer"),
        MorphEntry("ظلام", "ظلم", "فَعَال", "noun", gloss="darkness"),
        MorphEntry("ظلمات", "ظلم", "فَعَلَات", "noun", gloss="darknesses"),
        MorphEntry("مظلوم", "ظلم", "مَفْعُول", "noun", gloss="the oppressed"),
        MorphEntry("ظلم", "ظلم", "فَعْل", "noun", gloss="injustice, wrongdoing"),
        MorphEntry("ظالمون", "ظلم", "فَاعِلُون", "noun", gloss="wrongdoers (plural)"),
    ],

    "نبأ": [
        MorphEntry("نبأ", "نبأ", "فَعَلَ", "verb", 1, "to inform"),
        MorphEntry("نبي", "نبأ", "فَعِيل", "noun", gloss="prophet"),
        MorphEntry("أنبياء", "نبأ", "أَفْعِيَاء", "noun", gloss="prophets"),
        MorphEntry("نبأ", "نبأ", "فَعَل", "noun", gloss="news, information"),
        MorphEntry("أنبأ", "نبأ", "أَفْعَلَ", "verb", 4, "to inform"),
    ],

    "رسل": [
        MorphEntry("رسول", "رسل", "فَعُول", "noun", gloss="messenger"),
        MorphEntry("رسالة", "رسل", "فَعَالَة", "noun", gloss="message, mission"),
        MorphEntry("رسل", "رسل", "فُعُل", "noun", gloss="messengers (plural)"),
        MorphEntry("مرسل", "رسل", "مُفْعَل", "noun", gloss="sent, one sent"),
        MorphEntry("أرسل", "رسل", "أَفْعَلَ", "verb", 4, "to send"),
        MorphEntry("مرسلون", "رسل", "مُفْعَلُون", "noun", gloss="those sent"),
    ],

    "حرم": [
        MorphEntry("حرام", "حرم", "فَعَال", "adjective", gloss="forbidden"),
        MorphEntry("محرم", "حرم", "مُفَعَّل", "noun", gloss="forbidden month, mahram"),
        MorphEntry("حرم", "حرم", "فَعَلَ", "verb", 1, "to forbid, deprive"),
        MorphEntry("حريم", "حرم", "فَعِيل", "noun", gloss="sanctuary"),
        MorphEntry("تحريم", "حرم", "تَفْعِيل", "noun", gloss="prohibition"),
        MorphEntry("محرمات", "حرم", "مُفَعَّلَات", "noun", gloss="forbidden things"),
    ],

    "حلل": [
        MorphEntry("حلال", "حلل", "فَعَال", "adjective", gloss="permitted, lawful"),
        MorphEntry("حل", "حلل", "فَعَلَ", "verb", 1, "to permit, untie"),
        MorphEntry("تحليل", "حلل", "تَفْعِيل", "noun", gloss="analysis, making lawful"),
        MorphEntry("محلل", "حلل", "مُفَعِّل", "noun", gloss="analyst, one who permits"),
        MorphEntry("حلول", "حلل", "فُعُول", "noun", gloss="solutions"),
    ],

    "غفر": [
        MorphEntry("غفر", "غفر", "فَعَلَ", "verb", 1, "to forgive"),
        MorphEntry("غفور", "غفر", "فَعُول", "adjective", gloss="most forgiving"),
        MorphEntry("مغفرة", "غفر", "مَفْعِلَة", "noun", gloss="forgiveness"),
        MorphEntry("غافر", "غفر", "فَاعِل", "noun", gloss="forgiver"),
        MorphEntry("استغفر", "غفر", "اِسْتَفْعَلَ", "verb", 10, "to seek forgiveness"),
        MorphEntry("غفران", "غفر", "فَعْلَان", "noun", gloss="forgiveness"),
    ],

    "توب": [
        MorphEntry("توبة", "توب", "فَعْلَة", "noun", gloss="repentance"),
        MorphEntry("تائب", "توب", "فَاعِل", "noun", gloss="repentant"),
        MorphEntry("تواب", "توب", "فَعَّال", "adjective", gloss="acceptor of repentance"),
        MorphEntry("تاب", "توب", "فَعَلَ", "verb", 1, "to repent"),
        MorphEntry("يتوب", "توب", "يَفْعُل", "verb", 1, "he repents"),
    ],

    "جنن": [
        MorphEntry("جنة", "جنن", "فَعْلَة", "noun", gloss="paradise, garden"),
        MorphEntry("جنات", "جنن", "فَعَلَات", "noun", gloss="gardens (plural)"),
        MorphEntry("جن", "جنن", "فَعَلَ", "noun", gloss="jinn"),
        MorphEntry("جنون", "جنن", "فُعُول", "noun", gloss="madness"),
        MorphEntry("مجنون", "جنن", "مَفْعُول", "adjective", gloss="insane"),
        MorphEntry("جنين", "جنن", "فَعِيل", "noun", gloss="embryo, fetus"),
    ],

    "نار": [
        MorphEntry("نار", "نار", "فَعَل", "noun", gloss="fire, hell"),
        MorphEntry("نور", "نار", "فَعْل", "noun", gloss="light"),
        MorphEntry("أنار", "نار", "أَفْعَلَ", "verb", 4, "to illuminate"),
        MorphEntry("منير", "نار", "مُفِيل", "adjective", gloss="illuminating"),
        MorphEntry("استنار", "نار", "اِسْتَفْعَلَ", "verb", 10, "to be illuminated"),
    ],

    "قلب": [
        MorphEntry("قلب", "قلب", "فَعْل", "noun", gloss="heart"),
        MorphEntry("قلوب", "قلب", "فُعُول", "noun", gloss="hearts (plural)"),
        MorphEntry("قلب", "قلب", "فَعَلَ", "verb", 1, "to turn over, flip"),
        MorphEntry("تقلب", "قلب", "تَفَعُّل", "noun", gloss="fluctuation"),
        MorphEntry("مقلب", "قلب", "مُفَعِّل", "noun", gloss="one who turns"),
    ],

    "نفس": [
        MorphEntry("نفس", "نفس", "فَعْل", "noun", gloss="soul, self"),
        MorphEntry("أنفس", "نفس", "أَفْعَل", "noun", gloss="souls (plural)"),
        MorphEntry("نفيس", "نفس", "فَعِيل", "adjective", gloss="precious, valuable"),
        MorphEntry("تنفس", "نفس", "تَفَعُّل", "noun", gloss="breathing"),
        MorphEntry("نفاس", "نفس", "فَعَال", "noun", gloss="postpartum"),
    ],

    "عقل": [
        MorphEntry("عقل", "عقل", "فَعَلَ", "verb", 1, "to reason, understand"),
        MorphEntry("عقل", "عقل", "فَعْل", "noun", gloss="reason, intellect"),
        MorphEntry("عاقل", "عقل", "فَاعِل", "adjective", gloss="rational, sane"),
        MorphEntry("معقول", "عقل", "مَفْعُول", "adjective", gloss="reasonable"),
        MorphEntry("تعقل", "عقل", "تَفَعُّل", "noun", gloss="reasoning"),
        MorphEntry("عقلاء", "عقل", "فُعَلَاء", "noun", gloss="the rational ones"),
    ],

    "يوم": [
        MorphEntry("يوم", "يوم", "فَعْل", "noun", gloss="day"),
        MorphEntry("أيام", "يوم", "أَفْعَال", "noun", gloss="days (plural)"),
        MorphEntry("يومي", "يوم", "فَعْلِي", "adjective", gloss="daily"),
    ],

    "زمن": [
        MorphEntry("زمن", "زمن", "فَعَل", "noun", gloss="time, era"),
        MorphEntry("أزمان", "زمن", "أَفْعَال", "noun", gloss="times, ages"),
        MorphEntry("زمني", "زمن", "فَعَلِي", "adjective", gloss="temporal"),
        MorphEntry("زمان", "زمن", "فَعَال", "noun", gloss="time, epoch"),
    ],

    "عدد": [
        MorphEntry("عدد", "عدد", "فَعَلَ", "verb", 1, "to count"),
        MorphEntry("عدد", "عدد", "فَعَل", "noun", gloss="number, quantity"),
        MorphEntry("أعداد", "عدد", "أَفْعَال", "noun", gloss="numbers (plural)"),
        MorphEntry("معدود", "عدد", "مَفْعُول", "adjective", gloss="counted, numbered"),
        MorphEntry("إحصاء", "عدد", "إِفْعَال", "noun", gloss="census, counting"),
    ],

    "مطر": [
        MorphEntry("مطر", "مطر", "فَعَلَ", "verb", 1, "to rain"),
        MorphEntry("مطر", "مطر", "فَعَل", "noun", gloss="rain"),
        MorphEntry("أمطار", "مطر", "أَفْعَال", "noun", gloss="rains (plural)"),
        MorphEntry("ممطر", "مطر", "مُفْعِل", "adjective", gloss="rainy"),
    ],

    "ماء": [
        MorphEntry("ماء", "ماء", "فَعَل", "noun", gloss="water"),
        MorphEntry("مياه", "ماء", "فِيَاه", "noun", gloss="waters (plural)"),
        MorphEntry("مائي", "ماء", "فَعَلِي", "adjective", gloss="aquatic"),
    ],

    "سلم": [
        MorphEntry("سلام", "سلم", "فَعَال", "noun", gloss="peace, greeting"),
        MorphEntry("مسلم", "سلم", "مُفْعِل", "noun", gloss="Muslim, one who submits"),
        MorphEntry("إسلام", "سلم", "إِفْعَال", "noun", gloss="Islam, submission"),
        MorphEntry("سليم", "سلم", "فَعِيل", "adjective", gloss="sound, safe"),
        MorphEntry("استسلام", "سلم", "اِسْتِفْعَال", "noun", gloss="surrender"),
        MorphEntry("سلم", "سلم", "فَعَلَ", "verb", 1, "to be safe, to submit"),
        MorphEntry("مسلمون", "سلم", "مُفْعِلُون", "noun", gloss="Muslims"),
    ],

    "صبر": [
        MorphEntry("صبر", "صبر", "فَعَلَ", "verb", 1, "to be patient"),
        MorphEntry("صابر", "صبر", "فَاعِل", "noun", gloss="patient one"),
        MorphEntry("صبور", "صبر", "فَعُول", "adjective", gloss="very patient"),
        MorphEntry("صبر", "صبر", "فَعْل", "noun", gloss="patience"),
        MorphEntry("اصطبر", "صبر", "اِفْتَعَلَ", "verb", 8, "to persevere"),
    ],

    "شكر": [
        MorphEntry("شكر", "شكر", "فَعَلَ", "verb", 1, "to be grateful"),
        MorphEntry("شاكر", "شكر", "فَاعِل", "noun", gloss="grateful one"),
        MorphEntry("شكور", "شكر", "فَعُول", "adjective", gloss="very grateful"),
        MorphEntry("شكر", "شكر", "فَعْل", "noun", gloss="gratitude"),
        MorphEntry("شكران", "شكر", "فَعْلَان", "noun", gloss="gratitude"),
    ],

    "نصر": [
        MorphEntry("نصر", "نصر", "فَعَلَ", "verb", 1, "to help, support"),
        MorphEntry("ناصر", "نصر", "فَاعِل", "noun", gloss="helper, supporter"),
        MorphEntry("منصور", "نصر", "مَفْعُول", "adjective", gloss="aided, victorious"),
        MorphEntry("أنصار", "نصر", "أَفْعَال", "noun", gloss="helpers, Ansar"),
        MorphEntry("نصير", "نصر", "فَعِيل", "noun", gloss="helper, ally"),
        MorphEntry("نصر", "نصر", "فَعْل", "noun", gloss="victory, help"),
    ],

    "صلح": [
        MorphEntry("صالح", "صلح", "فَاعِل", "adjective", gloss="righteous"),
        MorphEntry("إصلاح", "صلح", "إِفْعَال", "noun", gloss="reform, correction"),
        MorphEntry("مصلح", "صلح", "مُفْعِل", "noun", gloss="reformer"),
        MorphEntry("صلاح", "صلح", "فَعَال", "noun", gloss="righteousness"),
        MorphEntry("صلح", "صلح", "فَعَلَ", "verb", 1, "to be righteous"),
        MorphEntry("مصالحة", "صلح", "مُفَاعَلَة", "noun", gloss="reconciliation"),
    ],

    "أمر": [
        MorphEntry("أمر", "أمر", "فَعَلَ", "verb", 1, "to command"),
        MorphEntry("أمر", "أمر", "فَعْل", "noun", gloss="command, matter"),
        MorphEntry("آمر", "أمر", "فَاعِل", "noun", gloss="commander"),
        MorphEntry("مأمور", "أمر", "مَفْعُول", "noun", gloss="one commanded"),
        MorphEntry("أوامر", "أمر", "أَفَاعِل", "noun", gloss="commands (plural)"),
        MorphEntry("إمارة", "أمر", "إِفَالَة", "noun", gloss="emirate, command"),
    ],

    "نهي": [
        MorphEntry("نهي", "نهي", "فَعَلَ", "verb", 1, "to forbid, prohibit"),
        MorphEntry("نهي", "نهي", "فَعْل", "noun", gloss="prohibition"),
        MorphEntry("ناهي", "نهي", "فَاعِل", "noun", gloss="one who forbids"),
        MorphEntry("منهي", "نهي", "مَفْعُول", "noun", gloss="the forbidden"),
    ],

    "فتح": [
        MorphEntry("فتح", "فتح", "فَعَلَ", "verb", 1, "to open, conquer"),
        MorphEntry("فتح", "فتح", "فَعْل", "noun", gloss="opening, conquest"),
        MorphEntry("فاتح", "فتح", "فَاعِل", "noun", gloss="opener, conqueror"),
        MorphEntry("مفتوح", "فتح", "مَفْعُول", "adjective", gloss="opened"),
        MorphEntry("فتوح", "فتح", "فُعُول", "noun", gloss="conquests"),
        MorphEntry("مفتاح", "فتح", "مِفْعَال", "noun", gloss="key"),
    ],

    "وحد": [
        MorphEntry("واحد", "وحد", "فَاعِل", "adjective", gloss="one, single"),
        MorphEntry("وحيد", "وحد", "فَعِيل", "adjective", gloss="alone, unique"),
        MorphEntry("توحيد", "وحد", "تَفْعِيل", "noun", gloss="monotheism, unification"),
        MorphEntry("أحد", "وحد", "فَعَل", "adjective", gloss="one (in negation)"),
        MorphEntry("وحدة", "وحد", "فَعْلَة", "noun", gloss="unity"),
    ],

    "صمد": [
        MorphEntry("صمد", "صمد", "فَعَلَ", "verb", 1, "to be eternal, self-sufficient"),
        MorphEntry("صمد", "صمد", "فَعَل", "adjective", gloss="the Eternal Absolute"),
        MorphEntry("صمود", "صمد", "فُعُول", "noun", gloss="steadfastness"),
    ],

    "ولد": [
        MorphEntry("ولد", "ولد", "فَعَلَ", "verb", 1, "to give birth"),
        MorphEntry("ولد", "ولد", "فَعَل", "noun", gloss="child, son"),
        MorphEntry("والد", "ولد", "فَاعِل", "noun", gloss="father"),
        MorphEntry("والدة", "ولد", "فَاعِلَة", "noun", gloss="mother"),
        MorphEntry("أولاد", "ولد", "أَفْعَال", "noun", gloss="children"),
        MorphEntry("مولود", "ولد", "مَفْعُول", "noun", gloss="newborn"),
    ],

    "كفو": [
        MorphEntry("كفو", "كفو", "فَعَل", "noun", gloss="equal, match"),
        MorphEntry("كافأ", "كفو", "فَاعَلَ", "verb", 3, "to reward, match"),
        MorphEntry("مكافأة", "كفو", "مُفَاعَلَة", "noun", gloss="reward, equivalence"),
        MorphEntry("تكافؤ", "كفو", "تَفَاعُل", "noun", gloss="equality"),
    ],

    "حكم": [
        MorphEntry("حكم", "حكم", "فَعَلَ", "verb", 1, "to judge, rule"),
        MorphEntry("حاكم", "حكم", "فَاعِل", "noun", gloss="ruler, judge"),
        MorphEntry("محكوم", "حكم", "مَفْعُول", "noun", gloss="the judged"),
        MorphEntry("حكمة", "حكم", "فَعْلَة", "noun", gloss="wisdom"),
        MorphEntry("حكيم", "حكم", "فَعِيل", "adjective", gloss="wise"),
        MorphEntry("حكم", "حكم", "فَعْل", "noun", gloss="judgment, ruling"),
        MorphEntry("محكمة", "حكم", "مَفْعَلَة", "noun", gloss="court of justice"),
    ],

    "فقه": [
        MorphEntry("فقه", "فقه", "فَعَلَ", "verb", 1, "to understand deeply"),
        MorphEntry("فقيه", "فقه", "فَعِيل", "noun", gloss="jurist, scholar"),
        MorphEntry("فقه", "فقه", "فَعْل", "noun", gloss="jurisprudence, deep understanding"),
        MorphEntry("فقهاء", "فقه", "فُعَلَاء", "noun", gloss="jurists (plural)"),
    ],

    "ذكر": [
        MorphEntry("ذكر", "ذكر", "فَعَلَ", "verb", 1, "to remember, mention"),
        MorphEntry("ذكر", "ذكر", "فَعْل", "noun", gloss="remembrance, mention"),
        MorphEntry("ذاكر", "ذكر", "فَاعِل", "noun", gloss="one who remembers"),
        MorphEntry("مذكور", "ذكر", "مَفْعُول", "adjective", gloss="mentioned"),
        MorphEntry("ذكرى", "ذكر", "فَعْلَى", "noun", gloss="reminder, memory"),
        MorphEntry("تذكر", "ذكر", "تَفَعُّل", "noun", gloss="remembering"),
    ],

    "فكر": [
        MorphEntry("فكر", "فكر", "فَعَلَ", "verb", 1, "to think, reflect"),
        MorphEntry("فكر", "فكر", "فَعْل", "noun", gloss="thought, thinking"),
        MorphEntry("تفكر", "فكر", "تَفَعُّل", "noun", gloss="contemplation"),
        MorphEntry("مفكر", "فكر", "مُفَعِّر", "noun", gloss="thinker"),
        MorphEntry("أفكار", "فكر", "أَفْعَال", "noun", gloss="thoughts (plural)"),
    ],

    "نظر": [
        MorphEntry("نظر", "نظر", "فَعَلَ", "verb", 1, "to look, consider"),
        MorphEntry("ناظر", "نظر", "فَاعِل", "noun", gloss="observer"),
        MorphEntry("منظور", "نظر", "مَفْعُول", "adjective", gloss="visible, perspective"),
        MorphEntry("نظرة", "نظر", "فَعْلَة", "noun", gloss="glance, viewpoint"),
        MorphEntry("نظرية", "نظر", "فَعْلِيَّة", "noun", gloss="theory"),
    ],

    "سمع": [
        MorphEntry("سمع", "سمع", "فَعَلَ", "verb", 1, "to hear"),
        MorphEntry("سامع", "سمع", "فَاعِل", "noun", gloss="hearer, listener"),
        MorphEntry("سميع", "سمع", "فَعِيل", "adjective", gloss="all-hearing"),
        MorphEntry("مسموع", "سمع", "مَفْعُول", "adjective", gloss="heard"),
        MorphEntry("سمع", "سمع", "فَعْل", "noun", gloss="hearing"),
        MorphEntry("استمع", "سمع", "اِسْتَفْعَلَ", "verb", 10, "to listen attentively"),
    ],

    "بصر": [
        MorphEntry("بصر", "بصر", "فَعَلَ", "verb", 1, "to see"),
        MorphEntry("بصير", "بصر", "فَعِيل", "adjective", gloss="all-seeing"),
        MorphEntry("بصيرة", "بصر", "فَعِيلَة", "noun", gloss="insight"),
        MorphEntry("أبصار", "بصر", "أَفْعَال", "noun", gloss="sights, eyes"),
        MorphEntry("تبصر", "بصر", "تَفَعُّل", "noun", gloss="insight, vision"),
    ],

    "كلم": [
        MorphEntry("كلم", "كلم", "فَعَلَ", "verb", 1, "to speak to"),
        MorphEntry("كلام", "كلم", "فَعَال", "noun", gloss="speech, words"),
        MorphEntry("كلمة", "كلم", "فَعْلَة", "noun", gloss="word"),
        MorphEntry("كلمات", "كلم", "فَعَلَات", "noun", gloss="words (plural)"),
        MorphEntry("تكلم", "كلم", "تَفَعَّلَ", "verb", 5, "to speak"),
        MorphEntry("متكلم", "كلم", "مُتَفَعِّل", "noun", gloss="speaker"),
    ],

    "قول": [
        MorphEntry("قول", "قول", "فَعْل", "noun", gloss="speech, saying"),
        MorphEntry("قال", "قول", "فَعَلَ", "verb", 1, "to say"),
        MorphEntry("يقول", "قول", "يَفْعُل", "verb", 1, "he says"),
        MorphEntry("أقوال", "قول", "أَفْعَال", "noun", gloss="sayings"),
        MorphEntry("قائل", "قول", "فَاعِل", "noun", gloss="one who says"),
    ],

    "فعل": [
        MorphEntry("فعل", "فعل", "فَعَلَ", "verb", 1, "to do, act"),
        MorphEntry("فعل", "فعل", "فَعْل", "noun", gloss="act, deed"),
        MorphEntry("فاعل", "فعل", "فَاعِل", "noun", gloss="doer, subject"),
        MorphEntry("مفعول", "فعل", "مَفْعُول", "noun", gloss="done, object"),
        MorphEntry("أفعال", "فعل", "أَفْعَال", "noun", gloss="acts, deeds"),
    ],

    "جعل": [
        MorphEntry("جعل", "جعل", "فَعَلَ", "verb", 1, "to make, cause"),
        MorphEntry("جاعل", "جعل", "فَاعِل", "noun", gloss="maker, one who makes"),
        MorphEntry("مجعول", "جعل", "مَفْعُول", "adjective", gloss="made"),
    ],

    "أخذ": [
        MorphEntry("أخذ", "أخذ", "فَعَلَ", "verb", 1, "to take"),
        MorphEntry("آخذ", "أخذ", "فَاعِل", "noun", gloss="one who takes"),
        MorphEntry("مأخوذ", "أخذ", "مَفْعُول", "adjective", gloss="taken"),
        MorphEntry("مؤاخذة", "أخذ", "مُفَاعَلَة", "noun", gloss="accountability"),
    ],

    "ذهب": [
        MorphEntry("ذهب", "ذهب", "فَعَلَ", "verb", 1, "to go"),
        MorphEntry("ذاهب", "ذهب", "فَاعِل", "noun", gloss="one going"),
        MorphEntry("ذهاب", "ذهب", "فَعَال", "noun", gloss="departure"),
        MorphEntry("مذهب", "ذهب", "مَفْعَل", "noun", gloss="school of thought"),
    ],

    "جاء": [
        MorphEntry("جاء", "جاء", "فَعَلَ", "verb", 1, "to come"),
        MorphEntry("جائي", "جاء", "فَاعِل", "noun", gloss="one who comes"),
        MorphEntry("مجيء", "جاء", "مَفْعِيل", "noun", gloss="coming, arrival"),
    ],

    "أتى": [
        MorphEntry("أتى", "أتى", "فَعَلَ", "verb", 1, "to come, bring"),
        MorphEntry("آتي", "أتى", "فَاعِل", "adjective", gloss="coming, forthcoming"),
        MorphEntry("إيتاء", "أتى", "إِفْعَال", "noun", gloss="giving, bringing"),
    ],

    "كان": [
        MorphEntry("كان", "كان", "فَعَلَ", "verb", 1, "to be, was"),
        MorphEntry("يكون", "كان", "يَفْعُل", "verb", 1, "to be, becomes"),
        MorphEntry("كينونة", "كان", "فَيْعَلَة", "noun", gloss="existence, being"),
    ],

    "صار": [
        MorphEntry("صار", "صار", "فَعَلَ", "verb", 1, "to become"),
        MorphEntry("يصير", "صار", "يَفْعِل", "verb", 1, "to become"),
        MorphEntry("مصير", "صار", "مَفْعِل", "noun", gloss="destiny, fate"),
    ],

    "وجد": [
        MorphEntry("وجد", "وجد", "فَعَلَ", "verb", 1, "to find"),
        MorphEntry("وجود", "وجد", "فُعُول", "noun", gloss="existence"),
        MorphEntry("موجود", "وجد", "مَفْعُول", "adjective", gloss="existing, found"),
        MorphEntry("واجد", "وجد", "فَاعِل", "noun", gloss="one who finds"),
    ],

    "رأى": [
        MorphEntry("رأى", "رأى", "فَعَلَ", "verb", 1, "to see"),
        MorphEntry("رؤية", "رأى", "فُعْلَة", "noun", gloss="vision, sight"),
        MorphEntry("رأي", "رأى", "فَعْل", "noun", gloss="opinion, view"),
        MorphEntry("مرئي", "رأى", "مَفْعُول", "adjective", gloss="visible, seen"),
    ],

    "قدر": [
        MorphEntry("قدر", "قدر", "فَعَلَ", "verb", 1, "to decree, be able"),
        MorphEntry("قدير", "قدر", "فَعِيل", "adjective", gloss="all-powerful"),
        MorphEntry("قدرة", "قدر", "فَعْلَة", "noun", gloss="power, ability"),
        MorphEntry("مقدر", "قدر", "مُفَعَّل", "adjective", gloss="decreed"),
        MorphEntry("تقدير", "قدر", "تَفْعِيل", "noun", gloss="estimation, appreciation"),
        MorphEntry("قدر", "قدر", "فَعَل", "noun", gloss="decree, fate"),
    ],

    "شاء": [
        MorphEntry("شاء", "شاء", "فَعَلَ", "verb", 1, "to will, want"),
        MorphEntry("مشيئة", "شاء", "مَفْعِلَة", "noun", gloss="will, divine will"),
        MorphEntry("شاء", "شاء", "فَاعِل", "noun", gloss="one who wills"),
    ],

    "أراد": [
        MorphEntry("أراد", "أراد", "أَفْعَلَ", "verb", 4, "to want, intend"),
        MorphEntry("إرادة", "أراد", "إِفَالَة", "noun", gloss="will, intention"),
        MorphEntry("مريد", "أراد", "مُفِيل", "noun", gloss="one who wills"),
    ],

    "عمل": [
        MorphEntry("عمل", "عمل", "فَعَلَ", "verb", 1, "to work, do"),
        MorphEntry("عمل", "عمل", "فَعَل", "noun", gloss="work, deed"),
        MorphEntry("عامل", "عمل", "فَاعِل", "noun", gloss="worker, factor"),
        MorphEntry("أعمال", "عمل", "أَفْعَال", "noun", gloss="works, deeds"),
        MorphEntry("عمال", "عمل", "فَعَّال", "noun", gloss="workers"),
    ],

    "حمل": [
        MorphEntry("حمل", "حمل", "فَعَلَ", "verb", 1, "to carry, bear"),
        MorphEntry("حامل", "حمل", "فَاعِل", "noun", gloss="carrier, pregnant"),
        MorphEntry("محمول", "حمل", "مَفْعُول", "adjective", gloss="carried, borne"),
        MorphEntry("حمل", "حمل", "فَعْل", "noun", gloss="burden, pregnancy"),
    ],

    "وضع": [
        MorphEntry("وضع", "وضع", "فَعَلَ", "verb", 1, "to place, put down"),
        MorphEntry("واضع", "وضع", "فَاعِل", "noun", gloss="one who places"),
        MorphEntry("موضوع", "وضع", "مَفْعُول", "noun", gloss="topic, placed"),
        MorphEntry("وضع", "وضع", "فَعْل", "noun", gloss="position, status"),
    ],

    "ترك": [
        MorphEntry("ترك", "ترك", "فَعَلَ", "verb", 1, "to leave, abandon"),
        MorphEntry("تارك", "ترك", "فَاعِل", "noun", gloss="one who leaves"),
        MorphEntry("متروك", "ترك", "مَفْعُول", "adjective", gloss="abandoned"),
        MorphEntry("تركة", "ترك", "فَعْلَة", "noun", gloss="inheritance"),
    ],

    "أكل": [
        MorphEntry("أكل", "أكل", "فَعَلَ", "verb", 1, "to eat"),
        MorphEntry("آكل", "أكل", "فَاعِل", "noun", gloss="eater"),
        MorphEntry("مأكول", "أكل", "مَفْعُول", "adjective", gloss="eaten, food"),
        MorphEntry("أكل", "أكل", "فَعْل", "noun", gloss="eating, food"),
        MorphEntry("أكلة", "أكل", "فَعْلَة", "noun", gloss="a meal, morsel"),
    ],

    "شرب": [
        MorphEntry("شرب", "شرب", "فَعَلَ", "verb", 1, "to drink"),
        MorphEntry("شارب", "شرب", "فَاعِل", "noun", gloss="one who drinks"),
        MorphEntry("مشروب", "شرب", "مَفْعُول", "noun", gloss="drink, beverage"),
        MorphEntry("شراب", "شرب", "فَعَال", "noun", gloss="drink, beverage"),
    ],

    "لبس": [
        MorphEntry("لبس", "لبس", "فَعَلَ", "verb", 1, "to wear, dress"),
        MorphEntry("لباس", "لبس", "فَعَال", "noun", gloss="clothing"),
        MorphEntry("لابس", "لبس", "فَاعِل", "noun", gloss="one who wears"),
        MorphEntry("ملبوس", "لبس", "مَفْعُول", "adjective", gloss="worn"),
    ],

    "دخل": [
        MorphEntry("دخل", "دخل", "فَعَلَ", "verb", 1, "to enter"),
        MorphEntry("داخل", "دخل", "فَاعِل", "noun", gloss="one entering, inside"),
        MorphEntry("مدخل", "دخل", "مَفْعَل", "noun", gloss="entrance"),
        MorphEntry("دخول", "دخل", "فُعُول", "noun", gloss="entry"),
    ],

    "خرج": [
        MorphEntry("خرج", "خرج", "فَعَلَ", "verb", 1, "to exit, go out"),
        MorphEntry("خارج", "خرج", "فَاعِل", "noun", gloss="one exiting, outside"),
        MorphEntry("مخرج", "خرج", "مَفْعَل", "noun", gloss="exit, way out"),
        MorphEntry("خروج", "خرج", "فُعُول", "noun", gloss="exit, going out"),
        MorphEntry("إخراج", "خرج", "إِفْعَال", "noun", gloss="bringing out, expulsion"),
    ],

    "وسع": [
        MorphEntry("وسع", "وسع", "فَعَلَ", "verb", 1, "to be wide, encompass"),
        MorphEntry("واسع", "وسع", "فَاعِل", "adjective", gloss="vast, wide"),
        MorphEntry("وسيع", "وسع", "فَعِيل", "adjective", gloss="spacious"),
        MorphEntry("سعة", "وسع", "فَعَة", "noun", gloss="capacity, abundance"),
    ],

    "ضاق": [
        MorphEntry("ضاق", "ضاق", "فَعَلَ", "verb", 1, "to be narrow, distressed"),
        MorphEntry("ضيق", "ضاق", "فَعْل", "noun", gloss="narrowness, distress"),
        MorphEntry("ضائق", "ضاق", "فَاعِل", "adjective", gloss="distressed"),
    ],

    "كثر": [
        MorphEntry("كثر", "كثر", "فَعَلَ", "verb", 1, "to be many, increase"),
        MorphEntry("كثير", "كثر", "فَعِيل", "adjective", gloss="many, much"),
        MorphEntry("أكثر", "كثر", "أَفْعَل", "adjective", gloss="more, most"),
        MorphEntry("كثرة", "كثر", "فَعْلَة", "noun", gloss="multitude, abundance"),
    ],

    "قلل": [
        MorphEntry("قليل", "قلل", "فَعِيل", "adjective", gloss="few, little"),
        MorphEntry("أقل", "قلل", "أَفْعَل", "adjective", gloss="fewer, less"),
        MorphEntry("قل", "قلل", "فَعَلَ", "verb", 1, "to be few"),
        MorphEntry("قلة", "قلل", "فَعْلَة", "noun", gloss="scarcity"),
    ],

    "عظم": [
        MorphEntry("عظيم", "عظم", "فَعِيل", "adjective", gloss="great, magnificent"),
        MorphEntry("عظمة", "عظم", "فَعْلَة", "noun", gloss="greatness, majesty"),
        MorphEntry("عظم", "عظم", "فَعَلَ", "verb", 1, "to be great"),
        MorphEntry("أعظم", "عظم", "أَفْعَل", "adjective", gloss="greatest"),
        MorphEntry("تعظيم", "عظم", "تَفْعِيل", "noun", gloss="glorification"),
    ],

    "صغر": [
        MorphEntry("صغير", "صغر", "فَعِيل", "adjective", gloss="small, young"),
        MorphEntry("أصغر", "صغر", "أَفْعَل", "adjective", gloss="smaller, youngest"),
        MorphEntry("صغر", "صغر", "فَعَلَ", "verb", 1, "to be small"),
        MorphEntry("صغار", "صغر", "فِعَال", "noun", gloss="small ones"),
    ],

    "جمل": [
        MorphEntry("جميل", "جمل", "فَعِيل", "adjective", gloss="beautiful"),
        MorphEntry("جمال", "جمل", "فَعَال", "noun", gloss="beauty"),
        MorphEntry("أجمل", "جمل", "أَفْعَل", "verb", 4, "to do beautifully"),
        MorphEntry("جملة", "جمل", "فَعْلَة", "noun", gloss="sentence, group"),
    ],

    "حسن": [
        MorphEntry("حسن", "حسن", "فَعَلَ", "verb", 1, "to be good, beautiful"),
        MorphEntry("حسن", "حسن", "فَعْل", "adjective", gloss="good, beautiful"),
        MorphEntry("إحسان", "حسن", "إِفْعَال", "noun", gloss="excellence, benevolence"),
        MorphEntry("حسنة", "حسن", "فَعْلَة", "noun", gloss="good deed"),
        MorphEntry("أحسن", "حسن", "أَفْعَلَ", "verb", 4, "to do well"),
        MorphEntry("محسن", "حسن", "مُفْعِل", "noun", gloss="one who does good"),
    ],

    "قبح": [
        MorphEntry("قبيح", "قبح", "فَعِيل", "adjective", gloss="ugly, reprehensible"),
        MorphEntry("قبح", "قبح", "فَعَلَ", "verb", 1, "to be ugly"),
        MorphEntry("قبح", "قبح", "فَعْل", "noun", gloss="ugliness"),
    ],

    "جهل": [
        MorphEntry("جهل", "جهل", "فَعَلَ", "verb", 1, "to be ignorant"),
        MorphEntry("جاهل", "جهل", "فَاعِل", "noun", gloss="ignorant one"),
        MorphEntry("جهل", "جهل", "فَعْل", "noun", gloss="ignorance"),
        MorphEntry("جهلاء", "جهل", "فُعَلَاء", "noun", gloss="ignorant ones"),
        MorphEntry("جاهلية", "جهل", "فَاعِلِيَّة", "noun", gloss="period of ignorance"),
    ],

    "عرف": [
        MorphEntry("عرف", "عرف", "فَعَلَ", "verb", 1, "to know, recognize"),
        MorphEntry("عارف", "عرف", "فَاعِل", "noun", gloss="one who knows"),
        MorphEntry("معروف", "عرف", "مَفْعُول", "noun", gloss="known, good deed"),
        MorphEntry("عرفان", "عرف", "فَعْلَان", "noun", gloss="gnosis, gratitude"),
        MorphEntry("تعريف", "عرف", "تَفْعِيل", "noun", gloss="definition, introduction"),
    ],

    "فهم": [
        MorphEntry("فهم", "فهم", "فَعَلَ", "verb", 1, "to understand"),
        MorphEntry("فاهم", "فهم", "فَاعِل", "noun", gloss="one who understands"),
        MorphEntry("مفهوم", "فهم", "مَفْعُول", "noun", gloss="understood, concept"),
        MorphEntry("فهم", "فهم", "فَعْل", "noun", gloss="understanding"),
    ],

    "حفظ": [
        MorphEntry("حفظ", "حفظ", "فَعَلَ", "verb", 1, "to memorize, preserve"),
        MorphEntry("حافظ", "حفظ", "فَاعِل", "noun", gloss="one who memorizes"),
        MorphEntry("محفوظ", "حفظ", "مَفْعُول", "adjective", gloss="memorized, preserved"),
        MorphEntry("حفيظ", "حفظ", "فَعِيل", "adjective", gloss="all-preserving"),
        MorphEntry("حفظة", "حفظ", "فَعَلَة", "noun", gloss="guards, memorizers"),
    ],

    "نسي": [
        MorphEntry("نسي", "نسي", "فَعَلَ", "verb", 1, "to forget"),
        MorphEntry("ناسي", "نسي", "فَاعِل", "noun", gloss="one who forgets"),
        MorphEntry("منسي", "نسي", "مَفْعُول", "adjective", gloss="forgotten"),
        MorphEntry("نسيان", "نسي", "فَعَلَان", "noun", gloss="forgetfulness"),
    ],

    "أكرم": [
        MorphEntry("أكرم", "أكرم", "أَفْعَلَ", "verb", 4, "to honor"),
        MorphEntry("كريم", "أكرم", "فَعِيل", "adjective", gloss="generous, noble"),
        MorphEntry("كرامة", "أكرم", "فَعَالَة", "noun", gloss="dignity, honor"),
        MorphEntry("إكرام", "أكرم", "إِفْعَال", "noun", gloss="honoring"),
        MorphEntry("أكارم", "أكرم", "أَفَاعِل", "noun", gloss="noble ones"),
    ],

    "هان": [
        MorphEntry("هان", "هان", "فَعَلَ", "verb", 1, "to be easy, to humiliate"),
        MorphEntry("هون", "هان", "فَعْل", "noun", gloss="ease, humiliation"),
        MorphEntry("هوان", "هان", "فَعَلَان", "noun", gloss="humiliation"),
        MorphEntry("مهين", "هان", "مُفِيل", "adjective", gloss="humiliating"),
    ],

    "ظهر": [
        MorphEntry("ظهر", "ظهر", "فَعَلَ", "verb", 1, "to appear, manifest"),
        MorphEntry("ظاهر", "ظهر", "فَاعِل", "adjective", gloss="apparent, manifest"),
        MorphEntry("ظهور", "ظهر", "فُعُول", "noun", gloss="appearance"),
        MorphEntry("ظهر", "ظهر", "فَعْل", "noun", gloss="back, afternoon"),
        MorphEntry("مظهر", "ظهر", "مَفْعَل", "noun", gloss="appearance, look"),
    ],

    "بطن": [
        MorphEntry("باطن", "بطن", "فَاعِل", "adjective", gloss="hidden, inner"),
        MorphEntry("بطن", "بطن", "فَعَلَ", "verb", 1, "to be hidden inside"),
        MorphEntry("بطن", "بطن", "فَعْل", "noun", gloss="belly, interior"),
        MorphEntry("بواطن", "بطن", "فَوَاعِل", "noun", gloss="inner aspects"),
    ],
}


# Build reverse lookup
_WORD_LOOKUP: Dict[str, MorphEntry] = {}
for root_group, entries in MORPHOLOGY_LEXICON.items():
    for entry in entries:
        _WORD_LOOKUP[entry.word] = entry


def get_root_family(root: str) -> List[str]:
    if root in MORPHOLOGY_LEXICON:
        return [e.word for e in MORPHOLOGY_LEXICON[root]]
    return []


def lookup_word(word: str) -> Optional[MorphEntry]:
    if word in _WORD_LOOKUP:
        return _WORD_LOOKUP[word]
    stripped = re.sub(r'[\u064B-\u065F\u0670]', '', word)
    if stripped in _WORD_LOOKUP:
        return _WORD_LOOKUP[stripped]
    if stripped.startswith("ال") and len(stripped) > 2:
        bare = stripped[2:]
        if bare in _WORD_LOOKUP:
            return _WORD_LOOKUP[bare]
    return None


def get_all_roots() -> List[str]:
    return list(MORPHOLOGY_LEXICON.keys())
