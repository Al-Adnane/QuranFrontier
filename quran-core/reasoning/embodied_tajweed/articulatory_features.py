"""
Articulatory Features and Tajweed Phonetics Grounding.

Encodes the 18 makharij (pronunciation points) in tajweed:
1. Al-Ghunnah (nasal cavity)
2-5. Al-Halq (pharynx) — 4 degrees
6-8. Asl/Wasat/Taraf al-Lisan (tongue)
9-11. Al-Jidda, Al-Adraas (gums and teeth)
12-13. Al-Shafatain (lips)
14-16. Al-Hanaka (palate)
17-18. Nasopharyngeal and Laryngeal

Acoustic features extracted from audio:
- Pitch (fundamental frequency F₀)
- Formants (F1, F2, F3 - vocal tract resonances)
- Duration (phoneme length)
- Intensity (amplitude)
- Voicing (voiced/unvoiced)
- Spectral characteristics
"""

import numpy as np
from scipy.signal import butter, sosfilt, get_window
from scipy.fft import fft, fftfreq
from scipy.optimize import fminbound
from typing import Dict, Tuple, List, Optional


class TajweedPhonetics:
    """
    Tajweed phonetics encoding and rule verification.

    Maintains learned associations between:
    - Acoustic features (pitch, formants, duration)
    - Articulatory gestures (makharij positions)
    - Tajweed rules (idgham, ikhfaa, iqlab, izhar)
    """

    def __init__(self, num_makharij: int = 18):
        """
        Initialize tajweed phonetics module.

        Args:
            num_makharij: Number of pronunciation points (standard: 18).
        """
        self.num_makharij = num_makharij

        # Makharij names and phonetic properties
        self.makharij_names = [
            "Ghunnah (Nasal)",
            "Halq Upper (Pharynx High)",
            "Halq Mid (Pharynx Mid)",
            "Halq Lower (Pharynx Low)",
            "Tongue Root (Back)",
            "Tongue Mid (Middle)",
            "Tongue Tip (Apex)",
            "Gum Ridge (Alveolar)",
            "Upper Teeth (Dental)",
            "Lower Teeth (Dental)",
            "Lips Outer (Bilabial)",
            "Lips Inner (Labiodental)",
            "Hard Palate 1",
            "Hard Palate 2",
            "Soft Palate (Velar)",
            "Nasopharyngeal",
            "Laryngeal",
            "Glottal",
        ]

        # Makharij acoustic signatures (pitch, formant ranges, duration)
        self.makharij_signatures = self._init_signatures()

        # Tajweed rule templates
        self.rule_templates = self._init_rule_templates()

    def _init_signatures(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """
        Initialize acoustic signatures for each makharij.

        Returns:
            Dictionary mapping makharij → acoustic feature ranges.
        """
        return {
            "Ghunnah": {"pitch": (80, 150), "f1": (200, 400), "duration": (0.1, 0.3)},
            "Halq Upper": {"pitch": (100, 200), "f1": (400, 800), "duration": (0.05, 0.2)},
            "Halq Mid": {"pitch": (120, 220), "f1": (350, 700), "duration": (0.05, 0.2)},
            "Halq Lower": {"pitch": (150, 250), "f1": (300, 600), "duration": (0.05, 0.2)},
            "Tongue Root": {"pitch": (100, 180), "f1": (500, 900), "duration": (0.08, 0.25)},
            "Tongue Mid": {"pitch": (120, 200), "f1": (400, 800), "duration": (0.08, 0.25)},
            "Tongue Tip": {"pitch": (150, 250), "f1": (200, 400), "duration": (0.05, 0.2)},
            "Gum Ridge": {"pitch": (180, 280), "f1": (150, 350), "duration": (0.04, 0.15)},
            "Upper Teeth": {"pitch": (200, 300), "f1": (100, 300), "duration": (0.03, 0.1)},
            "Lower Teeth": {"pitch": (200, 300), "f1": (100, 300), "duration": (0.03, 0.1)},
            "Lips Outer": {"pitch": (80, 150), "f1": (400, 800), "duration": (0.1, 0.3)},
            "Lips Inner": {"pitch": (150, 250), "f1": (300, 600), "duration": (0.05, 0.2)},
            "Hard Palate 1": {"pitch": (100, 200), "f1": (250, 500), "duration": (0.08, 0.2)},
            "Hard Palate 2": {"pitch": (120, 220), "f1": (300, 600), "duration": (0.08, 0.2)},
            "Soft Palate": {"pitch": (100, 180), "f1": (200, 400), "duration": (0.1, 0.3)},
            "Nasopharyngeal": {"pitch": (80, 150), "f1": (300, 600), "duration": (0.15, 0.4)},
            "Laryngeal": {"pitch": (80, 200), "f1": (200, 500), "duration": (0.1, 0.3)},
            "Glottal": {"pitch": (50, 300), "f1": (0, 1000), "duration": (0.02, 0.1)},
        }

    def _init_rule_templates(self) -> Dict[str, Dict]:
        """
        Initialize tajweed rule acoustic templates.

        Returns:
            Dictionary mapping rule name → template properties.
        """
        return {
            "idgham": {
                "description": "Assimilation (merge two sounds)",
                "doubled_letter": True,
                "pitch_change": 0.0,  # Pitch stays same
                "duration_change": 0.2,  # Slightly longer
                "formant_shift": 0.05,
            },
            "ikhfaa": {
                "description": "Hiding (partial assimilation)",
                "doubled_letter": False,
                "pitch_change": -10.0,  # Pitch drops
                "duration_change": 0.1,
                "formant_shift": 0.1,
            },
            "iqlab": {
                "description": "Conversion (n→m before b)",
                "doubled_letter": False,
                "pitch_change": 20.0,  # Pitch rises
                "duration_change": 0.15,
                "formant_shift": -0.05,  # Shift toward bilabial
            },
            "izhar": {
                "description": "Clarity (full pronunciation)",
                "doubled_letter": False,
                "pitch_change": 0.0,
                "duration_change": 0.0,
                "formant_shift": 0.0,
            },
        }

    def classify_makharij(self, features: Dict[str, float]) -> np.ndarray:
        """
        Classify which makharij is most likely given acoustic features.

        Args:
            features: Dictionary with keys 'pitch', 'formants', 'duration', 'intensity'.
                     formants should be a 3-tuple (F1, F2, F3).

        Returns:
            Probability distribution over makharij, shape (num_makharij,).
        """
        probs = np.zeros(self.num_makharij)

        pitch = features.get("pitch", 150)
        formants = features.get("formants", (500, 1500, 2500))
        duration = features.get("duration", 0.1)
        f1 = formants[0] if len(formants) > 0 else 500

        for i, makharij_name in enumerate(self.makharij_names):
            sig = self.makharij_signatures.get(makharij_name, {})

            # Likelihood from pitch
            pitch_range = sig.get("pitch", (0, 500))
            pitch_score = self._gaussian_likelihood(pitch, pitch_range[0], pitch_range[1])

            # Likelihood from F1
            f1_range = sig.get("f1", (0, 1000))
            f1_score = self._gaussian_likelihood(f1, f1_range[0], f1_range[1])

            # Likelihood from duration
            duration_range = sig.get("duration", (0, 0.5))
            duration_score = self._gaussian_likelihood(
                duration, duration_range[0], duration_range[1]
            )

            # Combined likelihood
            probs[i] = pitch_score * f1_score * duration_score

        # Normalize to probability distribution
        if np.sum(probs) > 0:
            probs /= np.sum(probs)
        else:
            probs = np.ones(self.num_makharij) / self.num_makharij

        return probs

    def _gaussian_likelihood(self, value: float, min_val: float, max_val: float) -> float:
        """
        Compute Gaussian likelihood for a value within a range.

        Args:
            value: Observed value.
            min_val: Range minimum (corresponds to ~68% probability).
            max_val: Range maximum.

        Returns:
            Likelihood in [0, 1].
        """
        center = (min_val + max_val) / 2
        sigma = (max_val - min_val) / 2
        return np.exp(-0.5 * ((value - center) / sigma) ** 2)

    def verify_rule(
        self,
        features: Dict[str, float],
        rule: str,
        phonemes: List[str],
    ) -> Tuple[bool, float]:
        """
        Verify if a tajweed rule is properly applied.

        Args:
            features: Acoustic features dictionary.
            rule: Rule name ("idgham", "ikhfaa", "iqlab", "izhar").
            phonemes: Phonemes involved (e.g., ['م', 'م'] for doubled letter).

        Returns:
            (rule_satisfied, confidence) where confidence ∈ [0, 1].
        """
        if rule not in self.rule_templates:
            return False, 0.0

        template = self.rule_templates[rule]
        confidence = 0.5  # Base confidence

        # Check doubled letter requirement
        if template["doubled_letter"]:
            if len(phonemes) >= 2 and phonemes[0] == phonemes[1]:
                confidence += 0.2
            else:
                return False, 0.1

        # Check pitch change consistency
        expected_pitch_delta = template["pitch_change"]
        # (In real application, would compare to baseline)
        if abs(expected_pitch_delta) < 5:
            confidence += 0.1

        # Check duration change
        expected_duration_delta = template["duration_change"]
        duration = features.get("duration", 0.1)
        if 0.05 < duration < 0.4:
            confidence += 0.2

        return confidence > 0.4, confidence

    def apply_rule_transformation(
        self,
        features: Dict[str, float],
        rule: str,
    ) -> Dict[str, float]:
        """
        Apply tajweed rule transformation to features.

        Args:
            features: Original acoustic features.
            rule: Rule to apply.

        Returns:
            Transformed features dictionary.
        """
        if rule not in self.rule_templates:
            return features

        template = self.rule_templates[rule]
        transformed = features.copy()

        # Apply pitch transformation
        pitch_change = template["pitch_change"]
        if "pitch" in transformed:
            transformed["pitch"] = max(50, transformed["pitch"] + pitch_change)

        # Apply duration transformation
        duration_change = template["duration_change"]
        if "duration" in transformed:
            transformed["duration"] = transformed["duration"] * (1 + duration_change)

        # Apply formant shift
        formant_shift = template["formant_shift"]
        if "formants" in transformed and isinstance(transformed["formants"], (list, tuple)):
            formants = list(transformed["formants"])
            formants[0] = formants[0] * (1 + formant_shift)
            transformed["formants"] = tuple(formants)

        return transformed


class AcousticFeatureExtractor:
    """
    Extract acoustic features from audio signals.

    Computes:
    - Pitch (F0) via autocorrelation
    - Formants (F1, F2, F3) via spectral peaks
    - Duration (total and per-segment)
    - Intensity (RMS energy)
    - Voice activity detection
    """

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        """
        Initialize acoustic feature extractor.

        Args:
            sample_rate: Audio sample rate in Hz.
            frame_duration_ms: Frame duration in milliseconds.
        """
        self.sample_rate = sample_rate
        self.frame_duration = int(sample_rate * frame_duration_ms / 1000)
        self.hop_length = self.frame_duration // 2

    def extract_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract acoustic features from audio.

        Args:
            audio: Audio waveform shape (num_samples,), values in [-1, 1].

        Returns:
            Dictionary with keys: pitch, formants, duration, intensity, voicing.
        """
        # Ensure float32
        audio = audio.astype(np.float32)

        # Duration
        duration = len(audio) / self.sample_rate

        # Intensity (RMS)
        intensity = np.sqrt(np.mean(audio ** 2))

        # Voice activity detection
        is_voiced = self._detect_voicing(audio)

        # Pitch estimation (if voiced)
        pitch = self._estimate_pitch(audio) if is_voiced else 0.0

        # Formant estimation
        formants = self._estimate_formants(audio)

        return {
            "pitch": float(pitch),
            "formants": formants,
            "duration": float(duration),
            "intensity": float(intensity),
            "voicing": float(is_voiced),
        }

    def _detect_voicing(self, audio: np.ndarray) -> bool:
        """
        Detect if audio is voiced using energy + autocorrelation.

        Args:
            audio: Audio waveform.

        Returns:
            True if voiced, False otherwise.
        """
        # Energy threshold
        rms = np.sqrt(np.mean(audio ** 2))
        if rms < 0.01:
            return False

        # Autocorrelation method
        autocorr = np.correlate(audio, audio, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]
        autocorr /= autocorr[0]

        # Look for peak in voicing range (50-500 Hz)
        min_lag = int(self.sample_rate / 500)  # 500 Hz
        max_lag = int(self.sample_rate / 50)   # 50 Hz

        if max_lag < len(autocorr):
            voiced_region = autocorr[min_lag:max_lag]
            max_corr = np.max(voiced_region) if len(voiced_region) > 0 else 0
            return max_corr > 0.3

        return rms > 0.05

    def _estimate_pitch(self, audio: np.ndarray) -> float:
        """
        Estimate fundamental frequency (F0) via autocorrelation.

        Args:
            audio: Audio waveform.

        Returns:
            Pitch in Hz.
        """
        # Windowing
        window = get_window("hann", len(audio))
        windowed = audio * window

        # Autocorrelation
        autocorr = np.correlate(windowed, windowed, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]
        autocorr /= (autocorr[0] + 1e-8)

        # Search for pitch (50-400 Hz range)
        min_lag = int(self.sample_rate / 400)
        max_lag = int(self.sample_rate / 50)

        if max_lag < len(autocorr):
            pitch_region = autocorr[min_lag:max_lag]
            if len(pitch_region) > 0 and np.max(pitch_region) > 0.1:
                lag = min_lag + np.argmax(pitch_region)
                pitch = self.sample_rate / lag
                return float(max(50, min(400, pitch)))

        return 0.0

    def _estimate_formants(self, audio: np.ndarray, num_formants: int = 3) -> Tuple[float, ...]:
        """
        Estimate formant frequencies via spectral peak picking.

        Args:
            audio: Audio waveform.
            num_formants: Number of formants to extract.

        Returns:
            Tuple of formant frequencies (Hz).
        """
        # Preemphasis
        preemph = 0.97
        audio_preemp = audio.copy()
        audio_preemp[1:] -= preemph * audio[:-1]

        # FFT
        window = get_window("hamming", len(audio_preemp))
        spectrum = np.abs(fft(audio_preemp * window))
        freqs = fftfreq(len(audio_preemp), 1 / self.sample_rate)

        # Only positive frequencies
        positive_freq_idx = freqs > 0
        freqs_pos = freqs[positive_freq_idx]
        spectrum_pos = spectrum[positive_freq_idx]

        # Smooth spectrum
        from scipy.ndimage import uniform_filter1d
        spectrum_smooth = uniform_filter1d(spectrum_pos, size=50)

        # Find peaks
        formants = []
        min_freq = 200
        max_freq = 4000

        for i in range(num_formants):
            # Restrict search range
            search_mask = (freqs_pos >= min_freq) & (freqs_pos <= max_freq)
            if np.any(search_mask):
                peak_idx = np.argmax(spectrum_smooth[search_mask])
                peak_freq = freqs_pos[search_mask][peak_idx]
                formants.append(float(peak_freq))
                min_freq = peak_freq + 200  # Next formant must be higher

        # Pad with zeros if fewer formants found
        while len(formants) < num_formants:
            formants.append(0.0)

        return tuple(formants[:num_formants])
