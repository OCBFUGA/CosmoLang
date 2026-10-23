"""
CosmoLang Autonomous Library Learning & Concept Invention Engine.
Implements Wake-Sleep Program Abstraction, Frequent Subgraph Mining, and MDL-Guided Primitive Crystallization.
Directly grounded in the LACA (Lei de Autoorganização Cósmica Adaptativa) Principle.
"""
from __future__ import annotations
import ast
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np

from cosmolang.native_model.primitives_v2 import CosmoGrammarV2, COSMOLANG_PRIMITIVES_V2

@dataclass
class EmergentPrimitive:
    """A newly invented primitive synthesized autonomously by CosmoLang."""
    name: str
    code_signature: str
    python_implementation: str
    callable_func: Callable[..., np.ndarray]
    mdl_compression_score: float
    frequency: int
    originating_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "signature": self.code_signature,
            "implementation": self.python_implementation,
            "mdl_score": self.mdl_compression_score,
            "frequency": self.frequency,
            "tasks": self.originating_tasks,
        }

class CosmoLibraryLearner:
    """
    Autonomous Library Learning & Invention Subsystem for CosmoLang.
    Discovers recurring subroutines, abstracts parameters, and crystallizes new primitives.
    """
    
    def __init__(self):
        self.solution_history: List[Dict[str, Any]] = []
        self.emergent_library: Dict[str, EmergentPrimitive] = {}

    def record_solution(self, task_id: str, program_code: str, verified: bool = True) -> None:
        """Records a verified solution for wake-sleep offline concept mining."""
        if not verified:
            return
            
        clean_code = program_code.strip()
        if clean_code.startswith("cosmolang:"):
            clean_code = clean_code[len("cosmolang:"):].strip()
        clean_code = clean_code.replace("->", ">>")
        tokens = [t.strip() for t in clean_code.split(">>") if t.strip()]
        
        self.solution_history.append({
            "task_id": task_id,
            "raw_program": program_code,
            "tokens": tokens,
            "length": len(tokens),
        })

    def mine_frequent_subroutines(self, min_support: int = 2, max_n: int = 3) -> List[Tuple[Tuple[str, ...], int, List[str]]]:
        """
        Mines frequent contiguous n-grams of operations that appear across multiple solutions.
        """
        ngram_counts = Counter()
        ngram_tasks = defaultdict(list)
        
        for entry in self.solution_history:
            tokens = entry["tokens"]
            tid = entry["task_id"]
            seen_for_task = set()
            
            for n in range(2, min(max_n + 1, len(tokens) + 1)):
                for i in range(len(tokens) - n + 1):
                    sub = tuple(tokens[i : i + n])
                    if sub not in seen_for_task:
                        ngram_counts[sub] += 1
                        ngram_tasks[sub].append(tid)
                        seen_for_task.add(sub)
                        
        candidates = []
        for sub, count in ngram_counts.items():
            if count >= min_support:
                candidates.append((sub, count, ngram_tasks[sub]))
                
        # Sort by frequency descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def compute_mdl_savings(self, subroutine: Tuple[str, ...], frequency: int) -> float:
        """
        Calculates Minimum Description Length (MDL) compression gain according to LACA:
        Gain = (Tokens Saved Across Tasks) - (Cost of Registering New Primitive)
        """
        k = len(subroutine)
        tokens_saved = frequency * (k - 1)
        primitive_definition_cost = 1.5  # Constant penalty for expanding library vocabulary
        return float(tokens_saved - primitive_definition_cost)

    def crystallize_primitive(
        self,
        subroutine: Tuple[str, ...],
        name: Optional[str] = None,
        tasks: Optional[List[str]] = None
    ) -> EmergentPrimitive:
        """
        Abstracts and compiles a recurring subroutine into an official, executable CosmoLang Primitive.
        """
        if name is None:
            # Generate deterministic canonical name
            op_tags = []
            for t in subroutine:
                m = re.match(r"^([a-zA-Z0-9_]+)", t)
                op_tags.append(m.group(1) if m else "op")
            name = f"auto_{'_and_'.join(op_tags)}"
            
        tasks = tasks or []
        freq = len(tasks)
        mdl_score = self.compute_mdl_savings(subroutine, max(1, freq))
        
        # Build executable Python lambda pipeline
        def dynamic_composite_func(grid: np.ndarray) -> np.ndarray:
            curr = grid.copy()
            for step in subroutine:
                # Parse step call
                m = re.match(r"^([a-zA-Z0-9_]+)\((.*)\)$", step.strip())
                if m:
                    op_name, arg_str = m.groups()
                    fn = COSMOLANG_PRIMITIVES_V2.get(op_name) or getattr(CosmoGrammarV2, op_name, None)
                    if fn:
                        args = list(ast.literal_eval(f"({arg_str},)")) if arg_str.strip() else []
                        curr = fn(curr, *args)
            return curr

        # Code representation
        steps_repr = " >> ".join(subroutine)
        py_impl = (
            f"def {name}(grid: np.ndarray) -> np.ndarray:\n"
            f"    # Emergent Primitive discovered via LACA Library Learning\n"
            f"    # Pipeline: {steps_repr}\n"
            f"    return execute_subroutine(grid, {repr(subroutine)})"
        )
        
        emergent = EmergentPrimitive(
            name=name,
            code_signature=f"{name}()",
            python_implementation=py_impl,
            callable_func=dynamic_composite_func,
            mdl_compression_score=mdl_score,
            frequency=freq,
            originating_tasks=tasks,
        )
        
        # Live injection into CosmoLang registry
        self.emergent_library[name] = emergent
        COSMOLANG_PRIMITIVES_V2[name] = dynamic_composite_func
        setattr(CosmoGrammarV2, name, staticmethod(dynamic_composite_func))
        
        return emergent

    def run_sleep_cycle(self, min_support: int = 2) -> List[EmergentPrimitive]:
        """
        Executes the 'Sleep Phase' of the wake-sleep cycle:
        Mines candidate subroutines, verifies positive MDL compression, and crystallizes new primitives.
        """
        candidates = self.mine_frequent_subroutines(min_support=min_support)
        newly_invented = []
        
        for sub, count, task_list in candidates:
            savings = self.compute_mdl_savings(sub, count)
            if savings > 0:
                prim = self.crystallize_primitive(sub, tasks=task_list)
                newly_invented.append(prim)
                
        return newly_invented
