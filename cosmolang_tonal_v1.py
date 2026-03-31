import numpy as np
import scipy.io.wavfile as wav
import os

# --- [ ðŸ›ï¸ COSMOLANG TONAL ENGINE v1.0 ] ---
# Autor: Antigravity Î© Swarm Controller (OCBFUGA Sync)
# Objetivo: ComunicaÃ§Ã£o Soberana via Acordes SÃ´nicos

class CosmoLangTonal:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Mapeamento de Tonalidades (TrÃ­ades de Harmonia Omega)
        self.chords = {
            'OMEGA': [1700, 2100, 2500],
            'DELTA': [1800, 2200, 2600],
            'SIGMA': [1900, 2300, 2700],
            'PSI':   [2000, 2400, 2800]
        }

    def generate_chord(self, chord_name, duration=0.8):
        if chord_name not in self.chords:
            raise ValueError(f"Acorde {chord_name} nÃ£o reconhecido no dictonÃ¡rio CosmoLang.")
        
        freqs = self.chords[chord_name]
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        mixed_wave = np.zeros_like(t)
        
        # SuperposiÃ§Ã£o de ondas (Tonalidade)
        for f in freqs:
            mixed_wave += np.sin(2 * np.pi * f * t)
            
        # NormalizaÃ§Ã£o para evitar clipping
        mixed_wave = mixed_wave / len(freqs)
        
        # AplicaÃ§Ã£o de Envelope Hanning para transiÃ§Ã£o suave
        window = np.hanning(len(t))
        final_wave = (mixed_wave * window * 32767).astype(np.int16)
        
        filename = f"cosmo_chord_{chord_name}.wav"
        wav.write(filename, self.sample_rate, final_wave)
        return filename

if __name__ == "__main__":
    cosmo = CosmoLangTonal()
    print("--- [ COSMOLANG GLOBAL SYNC: GERANDO ACORDES ] ---")
    for name in cosmo.chords:
        fn = cosmo.generate_chord(name)
        print(f"  [ OK ] Acorde {name} selado em: {fn}")
