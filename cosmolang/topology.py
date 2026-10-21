"""
CosmoCore AGI Swarm Language (CosmoLang) - Topology & Discrete Differential Engine
Version: 35.0 (Topological Scene Graph & Functional Role Inference Edition)
Author: Janio Gomes Ribeiro

Provides:
- Core topological invariants & discrete grid discretization
- Higher-order relational operators (raycast, line connectivity, perimeter contours)
- Semantic Scene Graph & Functional Role Inference (UCSD CoreThink inspired)
- Infinite-cost graph pruning (Least Action Cognitive Architecture - LACA)
- Internal visual-kinematic odometry with sprite occlusion immunity
- Multi-subgoal sequential planning
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from scipy import ndimage


class FunctionalRole(Enum):
    BACKGROUND = 0
    AVATAR = 1
    TRIGGER = 2
    BARRIER = 3
    GOAL = 4
    HAZARD = 5
    UNKNOWN = 6


@dataclass(frozen=True)
class GridCell:
    r: int
    c: int

    def __add__(self, other: Tuple[int, int]) -> GridCell:
        return GridCell(self.r + other[0], self.c + other[1])

    def manhattan_distance(self, other: GridCell) -> int:
        return abs(self.r - other.r) + abs(self.c - other.c)


@dataclass
class ConnectedComponent:
    id: int
    color: int
    coords: np.ndarray  # Shape (N, 2)
    bbox: Tuple[int, int, int, int]  # (min_r, min_c, max_r, max_c)
    mass: int  # Number of pixels
    centroid: Tuple[float, float]  # (center_r, center_c)
    euler_number: int = 1
    holes_count: int = 0
    symmetry_axes: List[str] = field(default_factory=list)

    @property
    def height(self) -> int:
        return self.bbox[2] - self.bbox[0] + 1

    @property
    def width(self) -> int:
        return self.bbox[3] - self.bbox[1] + 1


@dataclass
class SceneNode:
    component: ConnectedComponent
    role: FunctionalRole
    passable: bool = False


@dataclass
class SceneGraph:
    avatar: Optional[SceneNode] = None
    triggers: List[SceneNode] = field(default_factory=list)
    barriers: List[SceneNode] = field(default_factory=list)
    goals: List[SceneNode] = field(default_factory=list)
    hazards: List[SceneNode] = field(default_factory=list)


class TopologicalAnalyzer:
    """
    Computes discrete topological invariants on 2D lattice grids.
    Extracts connected components, detects grid downsampling resolution,
    higher-order relational operators, and infers Semantic Scene Graphs.
    """

    DIR_DELTAS: Dict[int, Tuple[int, int]] = {
        1: (-1, 0),  # Up
        2: (1, 0),   # Down
        3: (0, -1),  # Left
        4: (0, 1),   # Right
    }
    OPPOSITE_ACTION: Dict[int, int] = {1: 2, 2: 1, 3: 4, 4: 3}

    @staticmethod
    def extract_components(
        frame: np.ndarray,
        bg_color: Optional[int] = None,
        connectivity: int = 4
    ) -> List[ConnectedComponent]:
        if frame.ndim == 3:
            frame = frame[0]
            
        if bg_color is None:
            vals, counts = np.unique(frame, return_counts=True)
            bg_color = int(vals[np.argmax(counts)])

        structure = ndimage.generate_binary_structure(2, 1 if connectivity == 4 else 2)
        components: List[ConnectedComponent] = []
        comp_id = 0

        unique_colors = [c for c in np.unique(frame) if c != bg_color]
        for color in unique_colors:
            color_mask = (frame == color)
            labeled_arr, num_features = ndimage.label(color_mask, structure=structure)
            
            for f_idx in range(1, num_features + 1):
                coords = np.argwhere(labeled_arr == f_idx)
                if len(coords) == 0:
                    continue
                min_r, min_c = coords.min(axis=0)
                max_r, max_c = coords.max(axis=0)
                centroid = (float(coords[:, 0].mean()), float(coords[:, 1].mean()))
                mass = len(coords)

                # Euler characteristic & holes
                sub_mask = color_mask[min_r : max_r + 1, min_c : max_c + 1]
                holes = TopologicalAnalyzer.count_holes(sub_mask)
                euler = 1 - holes

                symmetries = TopologicalAnalyzer.detect_symmetries(sub_mask)

                comp = ConnectedComponent(
                    id=comp_id,
                    color=int(color),
                    coords=coords,
                    bbox=(int(min_r), int(min_c), int(max_r), int(max_c)),
                    mass=mass,
                    centroid=centroid,
                    euler_number=euler,
                    holes_count=holes,
                    symmetry_axes=symmetries,
                )
                components.append(comp)
                comp_id += 1

        return components

    @staticmethod
    def count_holes(binary_mask: np.ndarray) -> int:
        inverted = ~binary_mask
        padded = np.pad(inverted, pad_width=1, mode='constant', constant_values=True)
        _, num_inv_features = ndimage.label(padded, structure=np.ones((3, 3), dtype=bool))
        return max(0, num_inv_features - 1)

    @staticmethod
    def detect_symmetries(matrix: np.ndarray) -> List[str]:
        axes = []
        if np.array_equal(matrix, np.flipud(matrix)):
            axes.append("HORIZONTAL_AXIS")
        if np.array_equal(matrix, np.fliplr(matrix)):
            axes.append("VERTICAL_AXIS")
        if matrix.shape[0] == matrix.shape[1]:
            if np.array_equal(matrix, matrix.T):
                axes.append("MAIN_DIAGONAL")
            if np.array_equal(matrix, np.rot90(matrix, 2)):
                axes.append("ROTATIONAL_180")
        return axes

    # --- Higher-Order Relational Operators ---

    @staticmethod
    def raycast(
        grid: np.ndarray,
        origin: Tuple[int, int],
        direction: Tuple[int, int],
        stop_values: Tuple[int, ...] = (3, 4),
        max_distance: int = 64
    ) -> Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]], Optional[int]]:
        r, c = origin
        dr, dc = direction
        traversed: List[Tuple[int, int]] = []
        for _ in range(max_distance):
            r += dr
            c += dc
            if not (0 <= r < grid.shape[0] and 0 <= c < grid.shape[1]):
                return traversed, None, None
            traversed.append((r, c))
            if grid[r, c] in stop_values:
                return traversed, (r, c), int(grid[r, c])
        return traversed, None, None

    @staticmethod
    def connect_endpoints_line(
        grid: np.ndarray,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        color: int,
        avoid_values: Tuple[int, ...] = (3, 4)
    ) -> np.ndarray:
        out_grid = grid.copy()
        r1, c1 = p1
        r2, c2 = p2
        step_r = 1 if r2 >= r1 else -1
        for r in range(r1, r2 + step_r, step_r):
            if out_grid[r, c1] not in avoid_values:
                out_grid[r, c1] = color
        step_c = 1 if c2 >= c1 else -1
        for c in range(c1, c2 + step_c, step_c):
            if out_grid[r2, c] not in avoid_values:
                out_grid[r2, c] = color
        return out_grid

    @staticmethod
    def extract_perimeter_contour(binary_mask: np.ndarray) -> np.ndarray:
        eroded = ndimage.binary_erosion(binary_mask)
        return binary_mask ^ eroded

    @staticmethod
    def discretize_frame_to_grid(
        frame: np.ndarray,
        player_color: int = 9,
        bg_color: int = 5,
        border_color: int = 4
    ) -> Tuple[np.ndarray, int, Tuple[int, int]]:
        if frame.ndim == 3:
            frame = frame[0]

        p_coords = np.argwhere(frame == player_color)
        if len(p_coords) > 0:
            tile_h = int(p_coords[:, 0].max() - p_coords[:, 0].min() + 1)
            tile_w = int(p_coords[:, 1].max() - p_coords[:, 1].min() + 1)
            tile_size = max(1, max(tile_h, tile_w))
            origin_y = int(p_coords[:, 0].min() % tile_size)
            origin_x = int(p_coords[:, 1].min() % tile_size)
        else:
            tile_size = 8
            origin_y = 0
            origin_x = 0

        gh = (frame.shape[0] - origin_y) // tile_size
        gw = (frame.shape[1] - origin_x) // tile_size

        grid = np.full((gh, gw), bg_color, dtype=int)
        for r in range(gh):
            for c in range(gw):
                tile = frame[
                    origin_y + r * tile_size : origin_y + (r + 1) * tile_size,
                    origin_x + c * tile_size : origin_x + (c + 1) * tile_size,
                ]
                if tile.size > 0:
                    vals, counts = np.unique(tile, return_counts=True)
                    non_bg = [v for v in vals if v != bg_color and v != border_color]
                    if non_bg:
                        grid[r, c] = non_bg[0]
                    else:
                        grid[r, c] = vals[np.argmax(counts)]

        return grid, tile_size, (origin_y, origin_x)

    # --- Possibility C: Semantic Scene Graph Construction ---

    @staticmethod
    def build_scene_graph(
        grid: np.ndarray,
        bg_color: int = 5,
        player_pos: Optional[Tuple[int, int]] = None
    ) -> SceneGraph:
        """
        Infers high-level functional roles for connected components on the lattice.
        Separates Avatar, Triggers (switches/keys), Barriers (closed doors), and Goals.
        Inspired by UCSD compositional reasoning (CoreThink).
        """
        comps = TopologicalAnalyzer.extract_components(grid, bg_color=bg_color)
        scene = SceneGraph()

        for c in comps:
            # 1. Avatar Detection
            if c.color == 9 or (player_pos is not None and tuple(map(int, c.centroid)) == player_pos):
                scene.avatar = SceneNode(component=c, role=FunctionalRole.AVATAR, passable=True)
            # 2. Trigger Detection (Switches / Keys / Pressure Plates)
            elif c.color in (11, 10, 15):
                scene.triggers.append(SceneNode(component=c, role=FunctionalRole.TRIGGER, passable=True))
            # 3. Goal / Exit Detection
            elif c.color in (14,):
                scene.goals.append(SceneNode(component=c, role=FunctionalRole.GOAL, passable=True))
            # 4. Barrier / Door Detection
            elif c.color in (3,):
                scene.barriers.append(SceneNode(component=c, role=FunctionalRole.BARRIER, passable=False))
            # 5. Wall / Border / Hazard Detection
            elif c.color in (4, 8, 2):
                scene.hazards.append(SceneNode(component=c, role=FunctionalRole.HAZARD, passable=False))

        return scene


class InternalOdometryTracker:
    def __init__(self, player_color: int = 9):
        self.player_color = player_color
        self.pos: Optional[Tuple[int, int]] = None
        self.visited_trail: Set[Tuple[int, int]] = set()
        self.consecutive_steps_in_dir: int = 0
        self.last_action: Optional[int] = None

    def reset(self):
        self.pos = None
        self.visited_trail.clear()
        self.consecutive_steps_in_dir = 0
        self.last_action = None

    def update_with_frame(
        self,
        grid: np.ndarray,
        last_action: Optional[int] = None
    ) -> Tuple[int, int]:
        visual_pos = np.argwhere(grid == self.player_color)
        if len(visual_pos) > 0:
            self.pos = (int(visual_pos[0][0]), int(visual_pos[0][1]))
        elif last_action is not None and self.pos is not None:
            dr, dc = TopologicalAnalyzer.DIR_DELTAS.get(last_action, (0, 0))
            nr = max(0, min(grid.shape[0] - 1, self.pos[0] + dr))
            nc = max(0, min(grid.shape[1] - 1, self.pos[1] + dc))
            self.pos = (nr, nc)

        if self.pos is not None:
            self.visited_trail.add(self.pos)

        if last_action is not None:
            if last_action == self.last_action:
                self.consecutive_steps_in_dir += 1
            else:
                self.consecutive_steps_in_dir = 1
            self.last_action = last_action

        return self.pos if self.pos is not None else (0, 0)


class LeastActionGraphPlanner:
    INF_COST = 10**9

    @staticmethod
    def solve_geodesic(
        grid: np.ndarray,
        start: Tuple[int, int],
        target: Tuple[int, int],
        forbidden_cells: Optional[Set[Tuple[int, int]]] = None,
        wall_values: Tuple[int, ...] = (3, 4, 8),
        momentum_dir: Optional[int] = None,
        min_momentum_steps: int = 0,
        current_momentum_count: int = 0
    ) -> List[int]:
        if forbidden_cells is None:
            forbidden_cells = set()

        H, W = grid.shape
        pr, pc = start
        tr, tc = target

        if (pr, pc) == (tr, tc):
            return []

        start_state = ((pr, pc), momentum_dir, current_momentum_count)
        queue = deque([(start_state, [])])
        visited = {((pr, pc), momentum_dir)}

        while queue:
            ((r, c), last_dir, mom_count), path = queue.popleft()

            if (r, c) == (tr, tc):
                return path

            for act, (dr, dc) in TopologicalAnalyzer.DIR_DELTAS.items():
                nr, nc = r + dr, c + dc
                if not (0 <= nr < H and 0 <= nc < W):
                    continue

                if (nr, nc) in forbidden_cells and (nr, nc) != (tr, tc):
                    continue

                if grid[nr, nc] in wall_values and (nr, nc) != (tr, tc):
                    continue

                new_mom_count = (mom_count + 1) if (last_dir == act) else 1
                if last_dir is not None and act != last_dir:
                    if mom_count < min_momentum_steps:
                        continue

                state_key = ((nr, nc), act)
                if state_key not in visited:
                    visited.add(state_key)
                    queue.append((((nr, nc), act, new_mom_count), path + [act]))

        return []

    @staticmethod
    def solve_multi_subgoals(
        grid: np.ndarray,
        start: Tuple[int, int],
        subgoals: List[Tuple[int, int]],
        final_goal: Optional[Tuple[int, int]],
        forbidden_cells: Optional[Set[Tuple[int, int]]] = None,
        wall_values: Tuple[int, ...] = (3, 4, 8)
    ) -> List[int]:
        if forbidden_cells is None:
            forbidden_cells = set()

        cur_pos = start
        remaining = list(subgoals)
        full_plan: List[int] = []
        simulated_forbidden = set(forbidden_cells)

        while remaining:
            best_path = None
            best_target = None
            min_len = float("inf")

            for sg in remaining:
                p = LeastActionGraphPlanner.solve_geodesic(
                    grid, cur_pos, sg, simulated_forbidden, wall_values
                )
                if p and len(p) < min_len:
                    min_len = len(p)
                    best_path = p
                    best_target = sg

            if not best_path or best_target is None:
                break

            full_plan.extend(best_path)
            cur_pos = best_target
            remaining.remove(best_target)
            simulated_forbidden.add(best_target)

        if final_goal is not None and not remaining:
            final_path = LeastActionGraphPlanner.solve_geodesic(
                grid, cur_pos, final_goal, simulated_forbidden, wall_values
            )
            if final_path:
                full_plan.extend(final_path)

        return full_plan

    @staticmethod
    def plan_scene_trajectory(
        grid: np.ndarray,
        scene: SceneGraph,
        player_pos: Tuple[int, int],
        forbidden_cells: Optional[Set[Tuple[int, int]]] = None
    ) -> List[int]:
        """
        Plans optimal action trajectory directly from a high-level SceneGraph.
        Routes: Avatar -> Triggers (in greedy TSP order) -> Goal (avoiding Barriers until Triggers cleared).
        """
        subgoals = []
        for t in scene.triggers:
            coords = t.component.coords
            if len(coords) > 0:
                subgoals.append((int(coords[0][0]), int(coords[0][1])))

        goal_pos = None
        for g in scene.goals:
            coords = g.component.coords
            if len(coords) > 0:
                goal_pos = (int(coords[0][0]), int(coords[0][1]))
                break

        # Barriers block passage while triggers remain
        wall_vals = [4, 8]
        if subgoals and scene.barriers:
            for b in scene.barriers:
                wall_vals.append(b.component.color)

        return LeastActionGraphPlanner.solve_multi_subgoals(
            grid=grid,
            start=player_pos,
            subgoals=subgoals,
            final_goal=goal_pos,
            forbidden_cells=forbidden_cells,
            wall_values=tuple(set(wall_vals))
        )
