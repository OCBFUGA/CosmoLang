
import scipy.io.wavfile as wav
import argparse
from core import ResonanceCore

def run_sender():
    parser = argparse.ArgumentParser(description="Î© Acoustic Sender")
    parser.add_argument("--text", type=str, required=True, help="Text to encode")
    parser.add_argument("--output", type=str, default="acoustic_cipher.wav", help="Output filename")
    args = parser.parse_args()

    engine = ResonanceCore()
    print(f"--- [ ENCODING: {args.text} ] ---")
    
    freqs = engine.text_to_frequencies(args.text)
    waveform = engine.generate_wave(freqs)
    
    # Final normalization
    final_int16 = (waveform * 32767).astype('int16')
    wav.write(args.output, engine.sample_rate, final_int16)
    print(f"--- [ SUCCESS: {args.output} saved ] ---")

if __name__ == "__main__":
    run_sender()
