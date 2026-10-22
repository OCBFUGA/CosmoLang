"""
CosmoLang Native Model Command-Line Interface (CLI).
Provides tools for dataset generation, symbolic verification, and task synthesis.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from typing import Any, Dict

from cosmolang.native_model.grammar import CosmoGrammar, CosmoProgram
from cosmolang.native_model.generator import SyntheticTaskGenerator
from cosmolang.native_model.verifier import CosmoVerifier
from cosmolang.native_model.synthesizer import CosmoSynthesizer
from cosmolang.native_model.export_dataset import export_synthetic_dataset

def cmd_generate(args):
    print(f"Generating {args.size} synthetic tasks (max_depth={args.depth})...")
    t0 = time.time()
    export_synthetic_dataset(
        output_file=args.out,
        total_samples=args.size,
        max_depth=args.depth,
        format_type=args.format
    )
    dt = time.time() - t0
    print(f"Exported {args.size} tasks to {args.out} in {dt:.2f}s ({args.size/dt:.1f} tasks/sec)")

def cmd_solve(args):
    if not os.path.exists(args.task):
        print(f"Error: Task file {args.task} not found.")
        sys.exit(1)
    with open(args.task, "r", encoding="utf-8") as f:
        task = json.load(f)
    print(f"Solving task from {args.task}...")
    solver = CosmoSynthesizer()
    t0 = time.time()
    res = solver.solve(task, max_search_depth=args.max_depth)
    dt = time.time() - t0
    print(f"Result:")
    print(f"  Success:     {res.success}")
    print(f"  Program:     {res.program}")
    print(f"  Pixel Acc:   {res.pixel_accuracy * 100:.1f}%")
    print(f"  Candidates:  {res.candidates_evaluated}")
    print(f"  Solver Mode: {res.solver_mode}")
    print(f"  Time:        {dt*1000:.2f}ms")

def cmd_benchmark(args):
    print(f"Running CosmoLang Native Synthesizer Benchmark on {args.size} tasks...")
    tasks = SyntheticTaskGenerator.generate_batch(size=args.size, max_depth=args.depth)
    solver = CosmoSynthesizer()
    solved = 0
    t0 = time.time()
    for i, t in enumerate(tasks):
        res = solver.solve(t, max_search_depth=args.depth)
        if res.success:
            solved += 1
    dt = time.time() - t0
    print("=" * 60)
    print(f"BENCHMARK COMPLETED in {dt:.2f}s")
    print(f"Tasks: {len(tasks)} | Solved: {solved} ({solved/len(tasks)*100:.1f}%)")
    print(f"Average latency: {dt/len(tasks)*1000:.2f}ms per task")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="CosmoLang Native Model CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate
    p_gen = subparsers.add_parser("generate", help="Generate synthetic training datasets")
    p_gen.add_argument("--size", type=int, default=1000, help="Number of samples")
    p_gen.add_argument("--depth", type=int, default=3, help="Max composition depth")
    p_gen.add_argument("--out", type=str, default="cosmolang_train.jsonl", help="Output file path")
    p_gen.add_argument("--format", type=str, default="chatml", choices=["chatml", "alpaca"], help="Prompt format")
    p_gen.set_defaults(func=cmd_generate)

    # Solve
    p_solve = subparsers.add_parser("solve", help="Synthesize solution for a single task JSON")
    p_solve.add_argument("--task", type=str, required=True, help="Path to task JSON")
    p_solve.add_argument("--max_depth", type=int, default=2, help="Search depth")
    p_solve.set_defaults(func=cmd_solve)

    # Benchmark
    p_bench = subparsers.add_parser("benchmark", help="Benchmark synthesizer accuracy and speed")
    p_bench.add_argument("--size", type=int, default=50, help="Benchmark sample size")
    p_bench.add_argument("--depth", type=int, default=2, help="Task complexity depth")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
