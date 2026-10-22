"""
Logic Priors & Knowledge Base for CosmoLang.
Integrates human-verified logical specifications from Karnak Arthur dataset:
`/kaggle/input/datasets/karnakbaevarthur/logic-for-each-arc-task`
"""
from __future__ import annotations
import csv
import json
import os
from typing import Dict, List, Optional, Tuple, Any

class ARCLogicPriors:
    """Manages 400 canonical task explanations and maps them to CosmoLang AST primitives."""
    
    KAGGLE_PATHS = [
        "/kaggle/input/logic-for-each-arc-task/arc_explanations.json",
        "/kaggle/input/datasets/karnakbaevarthur/logic-for-each-arc-task/arc_explanations.json",
        "karnak_dataset/arc_explanations.json"
    ]
    
    def __init__(self, data_path: Optional[str] = None):
        self.explanations: Dict[str, str] = {}
        target_path = data_path
        if target_path is None:
            for p in self.KAGGLE_PATHS:
                if os.path.exists(p):
                    target_path = p
                    break
        if target_path and os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                self.explanations = json.load(f)

    def extract_cosmolang_primitives_from_rule(self, rule_text: str) -> List[str]:
        """Detects CosmoLang primitives mentioned in the human-verified logical rule."""
        rule_lower = rule_text.lower()
        primitives = []
        
        if any(w in rule_lower for k in ['tile', 'repeat', 'pattern', 'duplicate', 'replicate'] for w in [k]):
            primitives.append("tile")
        if any(w in rule_lower for k in ['symmetr', 'mirror', 'reflect', 'flip'] for w in [k]):
            primitives.append("reflect_h")
            primitives.append("reflect_v")
        if 'rotat' in rule_lower:
            primitives.append("rotate_90")
            primitives.append("rotate_180")
        if any(w in rule_lower for k in ['enclosed', 'interior', 'hole', 'surround', 'inside'] for w in [k]):
            primitives.append("fill_enclosed")
        if any(w in rule_lower for k in ['gravit', 'drop', 'fall', 'bottom', 'down'] for w in [k]):
            primitives.append("gravity")
        if any(w in rule_lower for k in ['recolor', 'change color', 'replace color'] for w in [k]):
            primitives.append("recolor")
        if any(w in rule_lower for k in ['crop', 'extract', 'bounding', 'subgrid'] for w in [k]):
            primitives.append("crop_bbox")
        if any(w in rule_lower for k in ['contour', 'outline', 'border', 'perimeter'] for w in [k]):
            primitives.append("outline_contour")
        if any(w in rule_lower for k in ['scale', 'enlarge', 'magnif'] for w in [k]):
            primitives.append("scale")
            
        return primitives
