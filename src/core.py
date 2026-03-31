
from scipy.signal import butter, lfilter
import numpy as np

class ResonanceCore:
    """The mathematical heart of the Acoustic Resonance Protocol."""
    
    def __init__(self, sample_rate=44100, base_freq=440, freq_step=50, duration=0.3):
        self.sample_rate = sample_rate
        self.base_freq = base_freq
        self.freq_step = freq_step
        self.duration = duration
        self.samples_per_char = int(self.sample_rate * self.duration)
        # ðŸ›ï¸ COSMOLANG CHORD DEFINITIONS (Tone Chords)
        self.COSMOLANG_CHORDS = {
            'OMEGA': [1700, 2100, 2500],
            'DELTA': [1800, 2200, 2600],
            'SIGMA': [1900, 2300, 2700],
            'PSI':   [2000, 2400, 2800]
        }

    def identify_chord(self, detected_freqs, tolerance=20):
        """Identifies if a set of detected peaks matches a CosmoLang chord."""
        for chord_name, target_freqs in self.COSMOLANG_CHORDS.items():
            matches = 0
            for tf in target_freqs:
                if any(abs(df - tf) < tolerance for df in detected_freqs):
                    matches += 1
            if matches >= 2: # Exige ao menos duas notas do acorde para validaÃ§Ã£o
                return chord_name
        return None

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_filter(self, data, lowcut=400, highcut=6500):
        """Filters out frequencies outside the 440Hz - 6000Hz protocol range."""
        b, a = self.butter_bandpass(lowcut, highcut, self.sample_rate, order=5)
        y = lfilter(b, a, data)
        return y.astype(np.float32)

    def text_to_frequencies(self, text):
        return [self.base_freq + (ord(char) * self.freq_step) for char in text]

    def frequency_to_char(self, freq):
        char_code = round((freq - self.base_freq) / self.freq_step)
        if 32 <= char_code <= 126:
            return chr(char_code)
        return None

    def generate_wave(self, frequencies):
        full_signal = np.array([], dtype=np.float32)
        t = np.linspace(0, self.duration, self.samples_per_char, False)
        
        for freq in frequencies:
            tone = np.sin(freq * t * 2 * np.pi)
            # Apply Hanning-like window to prevent clicks
            envelope = np.sin(np.linspace(0, np.pi, len(tone)))
            tone = tone * envelope
            full_signal = np.concatenate((full_signal, tone))
            
        return full_signal
