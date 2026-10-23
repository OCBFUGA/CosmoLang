"""
CosmoTokenizer & Dataset Formatter for CosmoLang Native Model.
Provides dense spatial serialization and ChatML/Alpaca instruction formatting.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List
import numpy as np

class CosmoTokenizer:
    """Encodes spatial ARC grids and formats training examples for LLM Fine-Tuning."""
    
    SYSTEM_PROMPT = (
        "You are CosmoCore, an inductive neuro-symbolic spatial reasoning engine. "
        "Given the input-output demonstration grids, synthesize the exact, minimal "
        "CosmoLang program that produces the transformations."
    )

    @staticmethod
    def format_grid(grid: np.ndarray | List[List[int]]) -> str:
        arr = np.array(grid)
        rows = [' '.join(str(val) for val in row) for row in arr]
        return '[' + ' | '.join(rows) + ']'

    @classmethod
    def format_task_to_prompt(cls, task: Dict[str, Any]) -> str:
        lines = []
        for i, pair in enumerate(task['train']):
            in_str = cls.format_grid(pair['input'])
            out_str = cls.format_grid(pair['output'])
            lines.append(f"Pair {i+1}: Input {in_str} -> Output {out_str}")
        return '\n'.join(lines)

    @classmethod
    def to_chatml_example(cls, task: Dict[str, Any]) -> Dict[str, Any]:
        user_content = (
            "Induce the CosmoLang program for these demonstrations:\n"
            f"{cls.format_task_to_prompt(task)}\n\n"
            "Respond with the minimal CosmoLang program:"
        )
        prog = task['program']
        if not prog.startswith("cosmolang:"):
            prog = f"cosmolang: {prog}"
        assistant_content = prog
        
        return {
            "messages": [
                {"role": "system", "content": cls.SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ],
            "ground_truth_program": task['program'],
            "depth": task.get('depth', 1)
        }
        
    @classmethod
    def to_alpaca_example(cls, task: Dict[str, Any]) -> Dict[str, Any]:
        instruction = "Synthesize the minimal CosmoLang program for the given spatial demonstrations."
        input_text = cls.format_task_to_prompt(task)
        prog = task['program']
        if not prog.startswith("cosmolang:"):
            prog = f"cosmolang: {prog}"
        output_text = prog
        
        return {
            "instruction": instruction,
            "input": input_text,
            "output": output_text
        }
