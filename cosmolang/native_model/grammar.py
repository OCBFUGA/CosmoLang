"""
CosmoLang Formal Grammar and AST Engine for Native Model Synthesis.
Provides formal specification, parsing, serialization, and deterministic evaluation.
All operations are 100% pure NumPy with zero external dependencies.
"""
from __future__ import annotations
import ast
import re
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

@dataclass
class CosmoOp:
    name: str
    args: Tuple[Any, ...]
    
    def to_code(self) -> str:
        args_str = ', '.join(repr(a) for a in self.args)
        return f"{self.name}({args_str})"
    
    def __repr__(self) -> str:
        return self.to_code()

class CosmoGrammar:
    """Closed Spatial Transformation Algebra for CosmoLang Native Model."""
    
    @staticmethod
    def reflect_h(grid: np.ndarray) -> np.ndarray:
        return np.fliplr(grid)
        
    @staticmethod
    def reflect_v(grid: np.ndarray) -> np.ndarray:
        return np.flipud(grid)
        
    @staticmethod
    def rotate_90(grid: np.ndarray) -> np.ndarray:
        return np.rot90(grid, -1)
        
    @staticmethod
    def rotate_180(grid: np.ndarray) -> np.ndarray:
        return np.rot90(grid, 2)
        
    @staticmethod
    def rotate_270(grid: np.ndarray) -> np.ndarray:
        return np.rot90(grid, 1)
        
    @staticmethod
    def transpose(grid: np.ndarray) -> np.ndarray:
        return grid.T
        
    @staticmethod
    def gravity(grid: np.ndarray, direction: str = 'down') -> np.ndarray:
        res = np.zeros_like(grid)
        h, w = grid.shape
        if direction == 'down':
            for x in range(w):
                col = grid[:, x]
                non_zero = col[col != 0]
                res[h - len(non_zero):, x] = non_zero
        elif direction == 'up':
            for x in range(w):
                col = grid[:, x]
                non_zero = col[col != 0]
                res[:len(non_zero), x] = non_zero
        elif direction == 'left':
            for y in range(h):
                row = grid[y, :]
                non_zero = row[row != 0]
                res[y, :len(non_zero)] = non_zero
        elif direction == 'right':
            for y in range(h):
                row = grid[y, :]
                non_zero = row[row != 0]
                res[y, w - len(non_zero):] = non_zero
        return res

    @staticmethod
    def recolor(grid: np.ndarray, src: int, dst: int) -> np.ndarray:
        res = grid.copy()
        res[grid == src] = dst
        return res

    @staticmethod
    def filter_color(grid: np.ndarray, keep_color: int) -> np.ndarray:
        res = np.zeros_like(grid)
        res[grid == keep_color] = keep_color
        return res

    @staticmethod
    def crop_bbox(grid: np.ndarray, bg_color: int = 0) -> np.ndarray:
        coords = np.argwhere(grid != bg_color)
        if len(coords) == 0:
            return grid.copy()
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        return grid[y_min:y_max+1, x_min:x_max+1].copy()

    @staticmethod
    def outline_contour(grid: np.ndarray, color: int = 1) -> np.ndarray:
        h, w = grid.shape
        mask = (grid != 0)
        eroded = np.zeros_like(mask)
        for y in range(h):
            for x in range(w):
                if mask[y, x]:
                    all_n = True
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if not (0 <= ny < h and 0 <= nx < w and mask[ny, nx]):
                            all_n = False
                            break
                    if all_n:
                        eroded[y, x] = True
        contour = mask ^ eroded
        res = np.zeros_like(grid)
        res[contour] = color
        return res

    @staticmethod
    def tile(grid: np.ndarray, repeat_r: int = 2, repeat_c: int = 2) -> np.ndarray:
        return np.tile(grid, (repeat_r, repeat_c))

    @staticmethod
    def scale(grid: np.ndarray, factor: int = 2) -> np.ndarray:
        return np.repeat(np.repeat(grid, factor, axis=0), factor, axis=1)

    @staticmethod
    def symmetrize_h(grid: np.ndarray) -> np.ndarray:
        return np.concatenate([grid, np.fliplr(grid)], axis=1)

    @staticmethod
    def symmetrize_v(grid: np.ndarray) -> np.ndarray:
        return np.concatenate([grid, np.flipud(grid)], axis=0)

    @staticmethod
    def shift(grid: np.ndarray, dr: int = 0, dc: int = 0, bg_color: int = 0) -> np.ndarray:
        h, w = grid.shape
        res = np.full((h, w), bg_color, dtype=grid.dtype)
        src_r_start = max(0, -dr)
        src_r_end = min(h, h - dr)
        dst_r_start = max(0, dr)
        dst_r_end = min(h, h + dr)

        src_c_start = max(0, -dc)
        src_c_end = min(w, w - dc)
        dst_c_start = max(0, dc)
        dst_c_end = min(w, w + dc)

        if src_r_end > src_r_start and src_c_end > src_c_start:
            res[dst_r_start:dst_r_end, dst_c_start:dst_c_end] = grid[src_r_start:src_r_end, src_c_start:src_c_end]
        return res

    @staticmethod
    def fill_enclosed(grid: np.ndarray, fill_color: int = 1, bg_color: int = 0) -> np.ndarray:
        h, w = grid.shape
        visited = np.zeros((h, w), dtype=bool)
        queue = deque()

        for r in range(h):
            for c in [0, w - 1]:
                if grid[r, c] == bg_color and not visited[r, c]:
                    visited[r, c] = True
                    queue.append((r, c))
        for c in range(w):
            for r in [0, h - 1]:
                if grid[r, c] == bg_color and not visited[r, c]:
                    visited[r, c] = True
                    queue.append((r, c))

        while queue:
            cr, cc = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if not visited[nr, nc] and grid[nr, nc] == bg_color:
                        visited[nr, nc] = True
                        queue.append((nr, nc))

        res = grid.copy()
        enclosed_mask = (grid == bg_color) & (~visited)
        res[enclosed_mask] = fill_color
        return res

    @staticmethod
    def invert(grid: np.ndarray, bg: int = 0, fg: int = 1) -> np.ndarray:
        res = grid.copy()
        bg_mask = (grid == bg)
        fg_mask = (grid == fg)
        res[bg_mask] = fg
        res[fg_mask] = bg
        return res

    PRIMITIVES: Dict[str, Callable] = {
        'reflect_h': reflect_h,
        'reflect_v': reflect_v,
        'rotate_90': rotate_90,
        'rotate_180': rotate_180,
        'rotate_270': rotate_270,
        'transpose': transpose,
        'gravity': gravity,
        'recolor': recolor,
        'filter_color': filter_color,
        'crop_bbox': crop_bbox,
        'outline_contour': outline_contour,
        'tile': tile,
        'scale': scale,
        'symmetrize_h': symmetrize_h,
        'symmetrize_v': symmetrize_v,
        'shift': shift,
        'fill_enclosed': fill_enclosed,
        'invert': invert,
    }

class CosmoProgram:
    """An executable pipeline of CosmoLang primitives."""
    
    def __init__(self, ops: Optional[List[CosmoOp]] = None):
        self.ops = ops or []
        
    def add(self, name: str, *args) -> CosmoProgram:
        self.ops.append(CosmoOp(name, args))
        return self
        
    def to_code(self) -> str:
        if not self.ops:
            return "identity()"
        return ' >> '.join(op.to_code() for op in self.ops)
        
    def execute(self, grid: np.ndarray) -> np.ndarray:
        curr = grid.copy()
        for op in self.ops:
            func = CosmoGrammar.PRIMITIVES.get(op.name)
            if func is None:
                raise ValueError(f"Unknown CosmoLang primitive: {op.name}")
            curr = func(curr, *op.args)
        return curr
        
    @classmethod
    def from_code(cls, code_str: str) -> CosmoProgram:
        code_str = code_str.strip()
        if not code_str or code_str == 'identity()':
            return cls([])
        tokens = [p.strip() for p in code_str.split('>>')]
        ops = []
        for t in tokens:
            m = re.match(r'^([a-zA-Z0-9_]+)\((.*)\)$', t)
            if not m:
                continue
            name, arg_str = m.groups()
            arg_str = arg_str.strip()
            args = []
            if arg_str:
                args = list(ast.literal_eval(f"({arg_str},)"))
            ops.append(CosmoOp(name, tuple(args)))
        return cls(ops)
        
    def __repr__(self) -> str:
        return self.to_code()
