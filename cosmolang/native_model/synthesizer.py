"""
Neuro-Symbolic Synthesizer for CosmoLang Native Model.
Bridges neural program proposal with deterministic symbolic execution and LACA verification.
"""
from __future__ import annotations
import itertools
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from cosmolang.native_model.grammar import CosmoGrammar, CosmoProgram, CosmoOp
from cosmolang.native_model.verifier import CosmoVerifier, VerificationResult
from cosmolang.native_model.tokenizer import CosmoTokenizer

@dataclass
class SynthesisResult:
    success: bool
    program: Optional[str]
    predicted_grid: Optional[List[List[int]]]
    pixel_accuracy: float
    depth: int
    candidates_evaluated: int
    solver_mode: str  # 'neural', 'symbolic_search', or 'hybrid'

class CosmoSynthesizer:
    """Inductive synthesis engine solving ARC tasks via CosmoLang formal algebra."""

    def __init__(self, neural_sampler: Optional[Callable[[Dict[str, Any], int], List[str]]] = None):
        """
        neural_sampler: Optional function taking (task_dict, num_samples) and returning candidate code strings.
        """
        self.neural_sampler = neural_sampler

    def solve(
        self,
        task: Dict[str, Any],
        max_search_depth: int = 2,
        neural_samples: int = 8
    ) -> SynthesisResult:
        """
        Attempts to solve the task using a hybrid strategy:
        1. Sample neural candidates if neural_sampler is provided.
        2. Fast symbolic beam/exhaustive search over atomic and composite CosmoLang operations.
        3. Verify all candidates against training demonstrations with CosmoVerifier.
        """
        candidates_checked = 0
        
        # 1. Neural Proposal Phase
        if self.neural_sampler is not None:
            try:
                candidates = self.neural_sampler(task, neural_samples)
                for cand in candidates:
                    candidates_checked += 1
                    res = CosmoVerifier.verify(cand, task)
                    if res.is_exact_match and res.predicted_test_output is not None:
                        return SynthesisResult(
                            success=True,
                            program=cand,
                            predicted_grid=res.predicted_test_output,
                            pixel_accuracy=res.pixel_accuracy,
                            depth=res.depth,
                            candidates_evaluated=candidates_checked,
                            solver_mode='neural'
                        )
            except Exception:
                pass

        # 2. Fast Symbolic Search Fallback (Depth 1 & 2)
        # Extract task colors
        colors = set()
        for p in task.get('train', []):
            colors.update(np.unique(p['input']).tolist())
            colors.update(np.unique(p['output']).tolist())
        colors.discard(0)
        sorted_colors = sorted(list(colors))

        # Depth 1: Unary & Common Operations
        depth1_ops: List[CosmoOp] = []
        for name in ['reflect_h', 'reflect_v', 'rotate_90', 'rotate_180', 'rotate_270', 'transpose', 'crop_bbox', 'symmetrize_h', 'symmetrize_v']:
            depth1_ops.append(CosmoOp(name, ()))
        for d in ['down', 'up', 'left', 'right']:
            depth1_ops.append(CosmoOp('gravity', (d,)))
        for r, c in [(2, 2), (2, 1), (1, 2), (3, 3)]:
            depth1_ops.append(CosmoOp('tile', (r, c)))
        for f in [2, 3]:
            depth1_ops.append(CosmoOp('scale', (f,)))
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0)]:
            depth1_ops.append(CosmoOp('shift', (dr, dc)))
        for c in sorted_colors:
            depth1_ops.append(CosmoOp('filter_color', (c,)))
            depth1_ops.append(CosmoOp('outline_contour', (c,)))
            depth1_ops.append(CosmoOp('fill_enclosed', (c,)))
            depth1_ops.append(CosmoOp('invert', (0, c)))
            for c_dst in sorted_colors:
                if c != c_dst:
                    depth1_ops.append(CosmoOp('recolor', (c, c_dst)))

        # Evaluate Depth 1
        best_candidate: Optional[Tuple[CosmoProgram, VerificationResult]] = None
        for op in depth1_ops:
            candidates_checked += 1
            prog = CosmoProgram([op])
            res = CosmoVerifier.verify(prog.to_code(), task)
            if res.is_exact_match and res.predicted_test_output is not None:
                return SynthesisResult(
                    success=True,
                    program=prog.to_code(),
                    predicted_grid=res.predicted_test_output,
                    pixel_accuracy=1.0,
                    depth=1,
                    candidates_evaluated=candidates_checked,
                    solver_mode='symbolic_search'
                )
            if best_candidate is None or res.pixel_accuracy > best_candidate[1].pixel_accuracy:
                best_candidate = (prog, res)

        # Depth 2: Chained Composites (if max_search_depth >= 2)
        if max_search_depth >= 2:
            # Selected fast transforms for chaining
            fast_ops = [
                CosmoOp('reflect_h', ()), CosmoOp('reflect_v', ()),
                CosmoOp('rotate_90', ()), CosmoOp('rotate_180', ()), CosmoOp('rotate_270', ()),
                CosmoOp('transpose', ()), CosmoOp('crop_bbox', ()),
                CosmoOp('gravity', ('down',)), CosmoOp('gravity', ('up',))
            ]
            for c in sorted_colors[:4]:
                fast_ops.append(CosmoOp('outline_contour', (c,)))
                fast_ops.append(CosmoOp('fill_enclosed', (c,)))
                for c_dst in sorted_colors[:4]:
                    if c != c_dst:
                        fast_ops.append(CosmoOp('recolor', (c, c_dst)))

            for op1, op2 in itertools.product(fast_ops, repeat=2):
                candidates_checked += 1
                prog = CosmoProgram([op1, op2])
                res = CosmoVerifier.verify(prog.to_code(), task)
                if res.is_exact_match and res.predicted_test_output is not None:
                    return SynthesisResult(
                        success=True,
                        program=prog.to_code(),
                        predicted_grid=res.predicted_test_output,
                        pixel_accuracy=1.0,
                        depth=2,
                        candidates_evaluated=candidates_checked,
                        solver_mode='symbolic_search'
                    )
                if best_candidate is None or res.pixel_accuracy > best_candidate[1].pixel_accuracy:
                    best_candidate = (prog, res)

        # If no 100% exact match found, return best candidate approximation
        if best_candidate is not None:
            prog, res = best_candidate
            return SynthesisResult(
                success=False,
                program=prog.to_code(),
                predicted_grid=res.predicted_test_output,
                pixel_accuracy=res.pixel_accuracy,
                depth=len(prog.ops),
                candidates_evaluated=candidates_checked,
                solver_mode='symbolic_search'
            )

        return SynthesisResult(
            success=False,
            program=None,
            predicted_grid=None,
            pixel_accuracy=0.0,
            depth=0,
            candidates_evaluated=candidates_checked,
            solver_mode='none'
        )
