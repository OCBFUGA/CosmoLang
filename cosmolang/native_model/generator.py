"""
Synthetic Task Generator for CosmoLang Native Model Training.
Generates millions of verified, non-trivial spatial reasoning tasks paired with ground-truth CosmoLang programs.
"""
from __future__ import annotations
import random
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from cosmolang.native_model.grammar import CosmoProgram, CosmoOp, CosmoGrammar

class SyntheticTaskGenerator:
    """Generates ARC-compliant demonstration tasks from formal CosmoLang programs."""
    
    UNARY_OPS = [
        'reflect_h', 'reflect_v', 'rotate_90', 'rotate_180', 'rotate_270',
        'transpose', 'crop_bbox', 'symmetrize_h', 'symmetrize_v'
    ]
    
    DIRECTIONS = ['down', 'up', 'left', 'right']

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
    def sample_random_program(cls, max_depth: int = 3, grid_colors: Optional[List[int]] = None) -> CosmoProgram:
        depth = random.randint(1, max_depth)
        prog = CosmoProgram()
        
        for _ in range(depth):
            op_type = random.choice([
                'unary', 'gravity', 'recolor', 'outline', 'filter', 
                'tile', 'scale', 'shift', 'fill_enclosed', 'invert'
            ])
            if op_type == 'unary':
                op_name = random.choice(cls.UNARY_OPS)
                prog.add(op_name)
            elif op_type == 'gravity':
                d = random.choice(cls.DIRECTIONS)
                prog.add('gravity', d)
            elif op_type == 'recolor':
                c1 = random.randint(1, 9)
                c2 = random.choice([c for c in range(1, 10) if c != c1])
                prog.add('recolor', c1, c2)
            elif op_type == 'outline':
                c = random.randint(1, 9)
                prog.add('outline_contour', c)
            elif op_type == 'filter':
                c = random.randint(1, 9)
                prog.add('filter_color', c)
            elif op_type == 'tile':
                r = random.choice([2, 3])
                c = random.choice([2, 3])
                prog.add('tile', r, c)
            elif op_type == 'scale':
                f = random.choice([2, 3])
                prog.add('scale', f)
            elif op_type == 'shift':
                dr = random.choice([-2, -1, 1, 2])
                dc = random.choice([-2, -1, 1, 2])
                prog.add('shift', dr, dc)
            elif op_type == 'fill_enclosed':
                c = random.randint(1, 9)
                prog.add('fill_enclosed', c)
            elif op_type == 'invert':
                c = random.randint(1, 9)
                prog.add('invert', 0, c)
                
        return prog

    @classmethod
    def generate_task(cls, num_train: int = 3, max_depth: int = 3, max_retries: int = 25) -> Optional[Dict[str, Any]]:
        for _ in range(max_retries):
            h = random.randint(3, 8)
            w = random.randint(3, 8)
            
            prog = cls.sample_random_program(max_depth=max_depth)
            
            train_pairs = []
            valid = True
            
            for _ in range(num_train + 1):  # train + 1 test pair
                in_grid = cls.random_grid(h, w, num_colors=random.randint(2, 4), density=random.uniform(0.25, 0.55))
                try:
                    out_grid = prog.execute(in_grid)
                except Exception:
                    valid = False
                    break
                    
                # Constrain dimensions to typical ARC boundaries (<= 30x30)
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
                    'program': prog.to_code(),
                    'depth': len(prog.ops)
                }
                
        return None

    @classmethod
    def generate_batch(cls, size: int = 100, max_depth: int = 3) -> List[Dict[str, Any]]:
        dataset = []
        for _ in range(size):
            task = cls.generate_task(max_depth=max_depth)
            if task is not None:
                dataset.append(task)
        return dataset
