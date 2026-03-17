# Pre-Quranic Sacred Texts - Original Script Rendering Guide

**Version:** 1.0.0  
**Last Updated:** 2026-03-14

---

## Overview

This document provides information on rendering the original scripts used in the pre-Quranic sacred texts collection. All texts are provided in their authentic original writing systems with Unicode encoding.

---

## Script Summary

| Tradition | Language | Script | Unicode Block | Status |
|-----------|----------|--------|---------------|--------|
| Judaism | Hebrew | Hebrew | U+0590-U+05FF | ✅ Full Support |
| Christianity | Koine Greek | Greek | U+0370-U+03FF | ✅ Full Support |
| Hinduism | Sanskrit | Devanagari | U+0900-U+097F | ✅ Full Support |
| Zoroastrianism | Avestan | Avestan | U+10B00-U+10B3F | ⚠️ Limited Support |
| Buddhism | Pali | Devanagari | U+0900-U+097F | ✅ Full Support |
| Taoism/Confucianism | Classical Chinese | Han Ideographs | U+4E00-U+9FFF | ✅ Full Support |
| Ancient Egypt | Ancient Egyptian | Egyptian Hieroglyphs | U+13000-U+1342F | ⚠️ Limited Support |
| Mesopotamia | Akkadian/Sumerian | Cuneiform | U+12000-U+123FF | ⚠️ Limited Support |

---

## Font Requirements

### ✅ Widely Supported Scripts

#### Hebrew
- **System Fonts:** Arial, Times New Roman, David, Frank Ruehl
- **Web Fonts:** Google Fonts (Frank Ruhl Libre, Heebo)
- **Unicode Range:** U+0590-U+05FF
- **Sample:** בְּרֵאשִׁית בָּרָא אֱלֹהִים

#### Greek
- **System Fonts:** Times New Roman, Arial, Gentium
- **Web Fonts:** Google Fonts (Gentium Plus, Cardo)
- **Unicode Range:** U+0370-U+03FF (including polytonic)
- **Sample:** Ἐν ἀρχῇ ἦν ὁ λόγος

#### Devanagari (Sanskrit/Pali)
- **System Fonts:** Mangal, Nirmala UI, Arial Unicode MS
- **Web Fonts:** Google Fonts (Noto Sans Devanagari, Tiro Devanagari)
- **Unicode Range:** U+0900-U+097F
- **Sample (Sanskrit):** अग्निमीळे पुरोहितं
- **Sample (Pali):** मनोपुब्बङ्गमा धम्मा

#### Chinese
- **System Fonts:** SimSun, Microsoft YaHei, Kaiti
- **Web Fonts:** Google Fonts (Noto Sans SC, Ma Shan Zheng)
- **Unicode Range:** U+4E00-U+9FFF
- **Sample:** 道可道，非常道

---

### ⚠️ Scripts Requiring Special Fonts

#### Avestan
- **Unicode Range:** U+10B00-U+10B3F
- **Required Fonts:**
  - Noto Sans Avestan (Google Fonts - Free)
  - Ahura Mazda Font (Specialized)
  - Jisihard Avestan Font
- **Sample:** 𐬀𐬴𐬆𐬨 𐬬𐬊𐬵𐬏 𐬬𐬀𐬵𐬌𐬯𐬙𐬆𐬨 𐬀𐬯𐬙𐬌
- **Download:** https://www.google.com/get/noto/#sans-lgc-avst
- **Notes:** Avestan script was specifically encoded for Zoroastrian texts. Requires Unicode 6.0+ support.

#### Egyptian Hieroglyphs
- **Unicode Range:** U+13000-U+1342F
- **Required Fonts:**
  - Noto Sans Egyptian Hieroglyphs (Google Fonts - Free)
  - NewGardiner (Specialized Egyptology font)
  - JSesh Font (Egyptology software)
- **Sample:** 𓀾 𓏏 𓏛 (Words to be spoken)
- **Download:** https://www.google.com/get/noto/#sans-lgc-egyp
- **Notes:** 
  - Unicode 6.0+ required
  - 1,071 hieroglyphic characters available
  - Direction can be left-to-right or right-to-left

#### Cuneiform (Akkadian/Sumerian)
- **Unicode Range:** U+12000-U+123FF (Sumero-Akkadian)
- **Required Fonts:**
  - Noto Sans Cuneiform (Google Fonts - Free)
  - Santakku (Free for academic use)
  - CuneiformFont (Specialized)
- **Sample:** 𒋗 𒀝 𒉪 𒁍 𒊏 𒅗 (He who saw the Deep)
- **Download:** https://www.google.com/get/noto/#sans-lgc-cune
- **Notes:**
  - Unicode 5.0+ required
  - 922 cuneiform signs + 103 numerals
  - Complex rendering may require specialized software

---

## Installation Instructions

### Windows 10/11

1. **Download Noto Fonts:**
   - Visit: https://www.google.com/get/noto/
   - Search for: Avestan, Egyptian Hieroglyphs, Cuneiform
   - Download and install

2. **Install Fonts:**
   - Right-click downloaded .ttf/.otf files
   - Select "Install for all users"

3. **Verify Installation:**
   - Open Character Map (charmap.exe)
   - Select the installed font
   - Verify characters display correctly

### macOS

1. **Download Noto Fonts:**
   - Visit: https://www.google.com/get/noto/
   - Download required scripts

2. **Install Fonts:**
   - Double-click font files
   - Click "Install Font"
   - Fonts will be added to Font Book

3. **Verify Installation:**
   - Open Font Book
   - Search for installed fonts
   - Preview characters

### Linux (Ubuntu/Debian)

```bash
# Install Noto fonts
sudo apt-get install fonts-noto fonts-noto-cjk

# Download specialized fonts
wget https://github.com/google/fonts/raw/main/ofl/notosansavestan/NotoSansAvestan-Regular.ttf
wget https://github.com/google/fonts/raw/main/ofl/notosanscuneiform/NotoSansCuneiform-Regular.ttf
wget https://github.com/google/fonts/raw/main/ofl/notosansegypthieroglyphs/NotoSansEgyptianHieroglyphs-Regular.ttf

# Install to user font directory
mkdir -p ~/.local/share/fonts
cp *.ttf ~/.local/share/fonts/
fc-cache -fv
```

---

## Web Rendering

### CSS Font Stack

```css
@font-face {
  font-family: 'Noto Sans Avestan';
  src: url('/fonts/NotoSansAvestan-Regular.ttf') format('truetype');
  unicode-range: U+10B00-10B3F;
}

@font-face {
  font-family: 'Noto Sans Egyptian Hieroglyphs';
  src: url('/fonts/NotoSansEgyptianHieroglyphs-Regular.ttf') format('truetype');
  unicode-range: U+13000-1342F;
}

@font-face {
  font-family: 'Noto Sans Cuneiform';
  src: url('/fonts/NotoSansCuneiform-Regular.ttf') format('truetype');
  unicode-range: U+12000-123FF;
}

.avestan {
  font-family: 'Noto Sans Avestan', 'Ahura Mazda', sans-serif;
}

.egyptian {
  font-family: 'Noto Sans Egyptian Hieroglyphs', 'NewGardiner', sans-serif;
}

.cuneiform {
  font-family: 'Noto Sans Cuneiform', 'Santakku', sans-serif;
}

.hebrew {
  font-family: 'Frank Ruhl Libre', 'David', serif;
}

.greek {
  font-family: 'Gentium Plus', 'Cardo', serif;
}

.sanskrit, .pali {
  font-family: 'Noto Sans Devanagari', 'Mangal', sans-serif;
}

.chinese {
  font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}
```

### HTML Usage

```html
<!-- Avestan -->
<p class="avestan">𐬀𐬴𐬆𐬨 𐬬𐬊𐬵𐬏</p>

<!-- Egyptian Hieroglyphs -->
<p class="egyptian">𓀾 𓏏 𓏛</p>

<!-- Cuneiform -->
<p class="cuneiform">𒋗 𒀝 𒉪 𒁍</p>

<!-- Hebrew -->
<p class="hebrew">בְּרֵאשִׁית בָּרָא</p>

<!-- Greek -->
<p class="greek">Ἐν ἀρχῇ ἦν</p>

<!-- Sanskrit -->
<p class="sanskrit">अग्निमीळे पुरोहितं</p>

<!-- Chinese -->
<p class="chinese">道可道，非常道</p>
```

---

## Browser Support

| Browser | Avestan | Egyptian | Cuneiform | Hebrew | Greek | Devanagari | Chinese |
|---------|---------|----------|-----------|--------|-------|------------|---------|
| Chrome 60+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Firefox 55+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Safari 12+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edge 79+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| IE 11 | ❌ | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

✅ = Full support with proper fonts installed  
⚠️ = Partial support (may need system fonts)  
❌ = Not supported

---

## Common Rendering Issues

### Issue: Boxes/Squares Instead of Characters

**Cause:** Missing font for the Unicode range

**Solution:**
1. Install Noto fonts for the specific script
2. Verify font is properly installed
3. Refresh browser/application

### Issue: Characters Display But Look Wrong

**Cause:** Font fallback to incorrect script

**Solution:**
1. Explicitly set font-family in CSS
2. Use font-specific classes for each script
3. Check font installation order

### Issue: Text Direction Incorrect

**Cause:** Bidirectional text mixing

**Solution:**
```html
<!-- Use dir attribute -->
<p dir="rtl" class="hebrew">בְּרֵאשִׁית</p>
<p dir="ltr" class="cuneiform">𒋗 𒀝 𒉪</p>
```

### Issue: Combining Marks Not Rendering

**Cause:** Font doesn't support complex text shaping

**Solution:**
1. Use fonts with OpenType support
2. Ensure text shaping engine is active
3. Try alternative fonts (Noto series recommended)

---

## Verification Tools

### Online Character Viewers
- https://www.compart.com/en/unicode/
- https://codepoints.net/
- https://www.fileformat.info/info/unicode/

### Font Verification
```bash
# Linux: Check installed fonts
fc-list | grep -i "noto"

# macOS: Check installed fonts
system_profiler SPFontsDataType | grep -i "noto"

# Windows: Check via PowerShell
Get-Font | Where-Object {$_.Name -like "*Noto*"}
```

### Unicode Range Test

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Unicode Test</title>
</head>
<body>
  <h1>Avestan (U+10B00-U+10B3F)</h1>
  <p>𐬀 𐬁 𐬂 𐬃 𐬄 𐬅 𐬆 𐬇 𐬈 𐬉 𐬊 𐬋 𐬌 𐬍 𐬎 𐬏</p>
  
  <h1>Egyptian (U+13000-U+1342F)</h1>
  <p>𓀀 𓀁 𓀂 𓀃 𓀄 𓀅 𓀆 𓀇 𓀈 𓀉 𓀊 𓀋 𓀌 𓀍 𓀎 𓀏</p>
  
  <h1>Cuneiform (U+12000-U+123FF)</h1>
  <p>𒀀 𒀁 𒀂 𒀃 𒀄 𒀅 𒀆 𒀇 𒀈 𒀉 𒀊 𒀋 𒀌 𒀍 𒀎 𒀏</p>
</body>
</html>
```

---

## Academic Resources

### Font Sources
- **Noto Fonts:** https://github.com/google/fonts
- **SBL Fonts:** https://www.sbl-site.org/educational/biblicalfonts.aspx
- **Open Richly Annotated Cuneiform Corpus:** https://oracc.org/

### Unicode Standards
- **Unicode Consortium:** https://unicode.org/
- **Unicode Charts:** https://unicode.org/charts/
- **CLDR Data:** https://cldr.unicode.org/

### Script-Specific Resources
- **Avestan:** The Avestan Digital Archive
- **Egyptian:** Thesaurus Linguae Aegyptiae
- **Cuneiform:** Cuneiform Digital Library Initiative (CDLI)

---

## License Information

All Noto fonts are licensed under the SIL Open Font License, Version 1.1.

**Summary:**
- Free for personal and commercial use
- Can be modified and redistributed
- Must retain copyright notices
- No warranty provided

Full license: https://scripts.sil.org/OFL

---

## Contact & Support

For issues with specific scripts or rendering problems:
1. Check this guide first
2. Verify font installation
3. Test with online Unicode viewers
4. Consult browser compatibility tables

For academic/corporate deployments, consider:
- Font subsetting for performance
- CDN hosting for web fonts
- Fallback font strategies
- Progressive enhancement approaches
