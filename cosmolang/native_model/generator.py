"""
Synthetic Task Generator for CosmoLang Native Model Training (v2.0).
Generates verified, non-trivial spatial reasoning tasks paired with ground-truth CosmoLang programs across all 40 Canonical Primitives.
"""
from __future__ import annotations
import random
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from cosmolang.native_model.grammar import CosmoProgram, CosmoOp
from cosmolang.native_model.primitives_v2 import CosmoGrammarV2, COSMOLANG_PRIMITIVES_V2

class SyntheticTaskGenerator:
    """Generates ARC-compliant demonstration tasks from formal CosmoLang v2.0 programs."""
    
    # 6 Canonical Families
    ISOMETRIES = [
        'reflect_h', 'reflect_v', 'rotate_90', 'rotate_180', 'rotate_270',
        'transpose', 'transpose_anti', 'identity'
    ]
    SYMMETRY_TOPOLOGY = [
        'symmetrize_h', 'symmetrize_v', 'fill_enclosed', 'hollow_object'
    ]
    MORPHOLOGY_CONTOUR = [
        'crop_bbox', 'outline_contour', 'dilate_4', 'erode_4', 'connect_points_aligned'
    ]
    PHYSICS_GRAVITY = [
        'gravity_down', 'gravity_up', 'gravity_left', 'gravity_right'
    ]
    COLOR_ALGEBRA = [
        'recolor', 'swap_colors', 'filter_color', 'mask_by_color', 'replace_background', 'invert'
    ]
    SCALE_TILING = [
        'repeat_tile', 'scale_up', 'scale_down', 'split_quadrant', 'shift'
    ]

    @classmethod
    def random_grid(cls, h: int, w: int, num_colors: int = 3, density: float = 0.3) -> np.ndarray:
        grid = np.zeros((h, w), dtype=int)
        colors = random.sample(range(1, 10), min(num_colors, 9))
        for y in range(h):
            for x in range(w):
                if random.random() < density:
                    grid[y, x] = random.choice(colors)
        return grid

    @classmethod
    def sample_random_program(cls, max_depth: int = 2) -> CosmoProgram:
        depth = random.randint(1, max_depth)
        prog = CosmoProgram()
        
        for _ in range(depth):
            family = random.choice([
                'isometry', 'symmetry', 'morphology', 'physics', 'color', 'scale_tiling'
            ])
            if family == 'isometry':
                op = random.choice(cls.ISOMETRIES)
                prog.add(op)
            elif family == 'symmetry':
                op = random.choice(cls.SYMMETRY_TOPOLOGY)
                if op == 'fill_enclosed':
                    prog.add(op, random.randint(1, 9))
                else:
                    prog.add(op)
            elif family == 'morphology':
                op = random.choice(cls.MORPHOLOGY_CONTOUR)
                if op in ['outline_contour', 'dilate_4']:
                    if random.random() < 0.5:
                        prog.add(op, random.randint(1, 9))
                    else:
                        prog.add(op)
                else:
                    prog.add(op)
            elif family == 'physics':
                op = random.choice(cls.PHYSICS_GRAVITY)
                prog.add(op)
            elif family == 'color':
                op = random.choice(cls.COLOR_ALGEBRA)
                if op == 'recolor':
                    c1 = random.randint(1, 9)
                    c2 = random.choice([c for c in range(1, 10) if c != c1])
                    prog.add(op, c1, c2)
                elif op == 'swap_colors':
                    c1 = random.randint(1, 9)
                    c2 = random.choice([c for c in range(1, 10) if c != c1])
                    prog.add(op, c1, c2)
                elif op in ['filter_color', 'mask_by_color', 'replace_background']:
                    prog.add(op, random.randint(1, 9))
                else:
                    prog.add(op)
            elif family == 'scale_tiling':
                op = random.choice(cls.SCALE_TILING)
                if op == 'repeat_tile':
                    fh = random.choice([2, 3])
                    fw = random.choice([2, 3])
                    prog.add(op, fh, fw)
                elif op in ['scale_up', 'scale_down']:
                    prog.add(op, 2)
                elif op == 'split_quadrant':
                    prog.add(op, random.randint(0, 3))
                elif op == 'shift':
                    prog.add(op, random.choice([-1, 1]), random.choice([-1, 1]))
                    
        return prog

    @classmethod
    def generate_task(cls, num_train: int = 3, max_depth: int = 2, max_retries: int = 30) -> Optional[Dict[str, Any]]:
        for _ in range(max_retries):
            h = random.randint(2, 6)
            w = random.randint(2, 6)
            
            prog = cls.sample_random_program(max_depth=max_depth)
            
            train_pairs = []
            valid = True
            
            for _ in range(num_train + 1):  # train + 1 test pair
                in_grid = cls.random_grid(h, w, num_colors=random.randint(2, 4), density=random.uniform(0.3, 0.6))
                try:
                    out_grid = prog.execute(in_grid)
                except Exception:
                    valid = False
                    break
                    
                # Boundaries constraint
                if out_grid.shape[0] > 30 or out_grid.shape[1] > 30:
                    valid = False
                    break
                    
                # Must be non-trivial
                if np.array_equal(in_grid, out_grid) or np.all(out_grid == 0):
                    valid = False
                    break
                    
                train_pairs.append({
                    'input': in_grid.tolist(),
                    'output': out_grid.tolist()
                })
                
            if valid and len(train_pairs) == num_train + 1:
                return {
                    'train': train_pairs[:num_train],
                    'test': [train_pairs[-1]],
                    'program': f"cosmolang: {prog.to_code()}",
                    'depth': len(prog.ops)
                }
                
        return None

    @classmethod
    def generate_batch(cls, size: int = 100, max_depth: int = 2) -> List[Dict[str, Any]]:
        dataset = []
        for _ in range(size):
            task = cls.generate_task(max_depth=max_depth)
            if task is not None:
                dataset.append(task)
        return dataset
