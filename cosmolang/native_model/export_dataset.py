"""
Dataset Exporter for CosmoLang Native Model Fine-Tuning.
Generates balanced synthetic tasks and exports directly to JSONL (ChatML or Alpaca format).
"""
from __future__ import annotations
import argparse
import json
import os
import time
from cosmolang.native_model.generator import SyntheticTaskGenerator
from cosmolang.native_model.tokenizer import CosmoTokenizer
from cosmolang.native_model.verifier import CosmoVerifier

def export_synthetic_dataset(
    output_file: str = "cosmolang_dataset_chatml.jsonl",
    total_samples: int = 1000,
    max_depth: int = 3,
    format_type: str = "chatml"
) -> None:
    print(f"=== Generating {total_samples} Synthetic CosmoLang Training Samples ({format_type.upper()}) ===")
    start_time = time.time()
    
    saved_count = 0
    with open(output_file, "w", encoding="utf-8") as f:
        while saved_count < total_samples:
            task = SyntheticTaskGenerator.generate_task(num_train=3, max_depth=max_depth)
            if task is None:
                continue
                
            # Verify correctness
            vr = CosmoVerifier.verify(task['program'], task)
            if not vr.is_exact_match:
                continue
                
            if format_type.lower() == "alpaca":
                example = CosmoTokenizer.to_alpaca_example(task)
            else:
                example = CosmoTokenizer.to_chatml_example(task)

            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            saved_count += 1
            
            if saved_count % 500 == 0 or saved_count == total_samples:
                elapsed = time.time() - start_time
                rate = saved_count / elapsed if elapsed > 0 else 0
                print(f"[{saved_count}/{total_samples}] samples exported ({rate:.1f} samples/sec)")
                
    total_time = time.time() - start_time
    file_size_kb = os.path.getsize(output_file) / 1024
    print(f"\nSUCCESS! Exported {saved_count} samples to {output_file} ({file_size_kb:.1f} KB in {total_time:.2f}s)")

generate_and_export = export_synthetic_dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export CosmoLang Synthetic Training Dataset")
    parser.add_argument("-n", "--num", type=int, default=1000, help="Number of samples")
    parser.add_argument("-o", "--output", type=str, default="cosmolang_dataset_chatml.jsonl", help="Output file")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Max program depth")
    parser.add_argument("-f", "--format", type=str, default="chatml", choices=["chatml", "alpaca"], help="Format")
    args = parser.parse_args()
    
    export_synthetic_dataset(output_file=args.output, total_samples=args.num, max_depth=args.depth, format_type=args.format)
