"""
Symbolic LACA Verifier for CosmoLang Native Model.
Provides deterministic, sub-millisecond hypothesis verification and MDL scoring.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
from cosmolang.native_model.grammar import CosmoProgram

@dataclass
class VerificationResult:
    is_valid_syntax: bool
    is_exact_match: bool
    pixel_accuracy: float
    depth: int
    complexity: int
    error_message: Optional[str] = None
    predicted_test_output: Optional[List[List[int]]] = None

class CosmoVerifier:
    """Validates neural candidate programs against demonstration pairs."""

    @classmethod
    def verify(cls, candidate_code: str, task: Dict[str, Any]) -> VerificationResult:
        # Clean candidate code
        code = candidate_code.strip()
        if code.startswith('cosmolang:'):
            code = code[len('cosmolang:'):].strip()
        if code.startswith('`') and code.endswith('`'):
            code = code.strip('`').strip()
            
        try:
            prog = CosmoProgram.from_code(code)
        except Exception as e:
            return VerificationResult(
                is_valid_syntax=False,
                is_exact_match=False,
                pixel_accuracy=0.0,
                depth=0,
                complexity=len(code),
                error_message=str(e)
            )

        train_pairs = task.get('train', [])
        total_pixels = 0
        correct_pixels = 0
        all_exact = True

        for pair in train_pairs:
            in_arr = np.array(pair['input'])
            expected_out = np.array(pair['output'])
            try:
                actual_out = prog.execute(in_arr)
            except Exception as e:
                return VerificationResult(
                    is_valid_syntax=True,
                    is_exact_match=False,
                    pixel_accuracy=0.0,
                    depth=len(prog.ops),
                    complexity=len(code),
                    error_message=f"Execution error: {e}"
                )

            if actual_out.shape != expected_out.shape:
                all_exact = False
                continue

            matches = np.sum(actual_out == expected_out)
            total = actual_out.size
            total_pixels += total
            correct_pixels += matches
            if matches != total:
                all_exact = False

        acc = (correct_pixels / total_pixels) if total_pixels > 0 else 0.0

        # If test pairs present, execute on test
        test_pred = None
        test_pairs = task.get('test', [])
        if test_pairs and all_exact:
            try:
                test_in = np.array(test_pairs[0]['input'])
                test_out = prog.execute(test_in)
                test_pred = test_out.tolist()
            except Exception:
                pass

        return VerificationResult(
            is_valid_syntax=True,
            is_exact_match=all_exact,
            pixel_accuracy=float(acc),
            depth=len(prog.ops),
            complexity=len(code),
            predicted_test_output=test_pred
        )
