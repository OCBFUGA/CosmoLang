
import numpy as np
import pyaudio
import time
from core import ResonanceCore

class AcousticDaemon:
    def __init__(self):
        self.engine = ResonanceCore()
        self.p = pyaudio.PyAudio()
        self.chunk_size = 4096
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.engine.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        print("--- [ LISTENING POST ACTIVE: Standby for Resonance ] ---")

    def monitor(self, trigger_sequence="OPEN"):
        detected_chars = []
        last_detect_time = 0
        noise_floor = 2.0  # Base level for silence
        alpha = 0.05      # Smoothing factor for ambient noise tracking
        
        try:
            while True:
                # 1. Capture and Filter
                raw_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(raw_data, dtype=np.float32)
                
                # Apply Butterworth Filter to clean external noise (fans/hum)
                clean_chunk = self.engine.apply_filter(audio_chunk)
                
                # 2. Spectral Analysis
                fft_res = np.abs(np.fft.fft(clean_chunk))
                freqs = np.fft.fftfreq(len(clean_chunk), 1/self.engine.sample_rate)
                
                # Extrai mÃºltiplos picos (Top 5 energias)
                positive_freqs_mask = (freqs > 400) & (freqs < 6000)
                spectrum = fft_res[positive_freqs_mask]
                spectrum_freqs = freqs[positive_freqs_mask]
                
                # Encontra os Ã­ndices dos picos mais fortes
                peak_indices = np.argsort(spectrum)[-5:]
                top_peaks = [abs(spectrum_freqs[i]) for i in peak_indices if spectrum[i] > noise_floor * 5.0]
                
                if top_peaks and (time.time() - last_detect_time > 0.8):
                    # ðŸ›ï¸ COSMOLANG CHORD DETECTION
                    chord = self.engine.identify_chord(top_peaks)
                    if chord:
                        print(f"\n--- [ ðŸ›ï¸ COSMOLANG CHORD DETECTED: {chord} ] ---")
                        last_detect_time = time.time()
                        # Aqui integrariam os scripts AIMO/FUGA disparados por sinal
                    else:
                        # Fallback para caracteres individuais (Legacy)
                        peak_freq = top_peaks[-1]
                        char = self.engine.frequency_to_char(peak_freq)
                        if char:
                            print(f"Captured Glyph: {char}")
                            last_detect_time = time.time()

        except KeyboardInterrupt:
            print("\n--- [ SHUTTING DOWN LISTENING POST ] ---")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

if __name__ == "__main__":
    daemon = AcousticDaemon()
    daemon.monitor()
