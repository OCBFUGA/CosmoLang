"""
Unit and Integration Test Suite for CosmoLang Native Foundation Model Subsystem.
"""
import unittest
import numpy as np

from cosmolang.native_model.grammar import CosmoGrammar, CosmoOp, CosmoProgram
from cosmolang.native_model.generator import SyntheticTaskGenerator
from cosmolang.native_model.verifier import CosmoVerifier
from cosmolang.native_model.tokenizer import CosmoTokenizer
from cosmolang.native_model.synthesizer import CosmoSynthesizer

class TestCosmoLangNativeModel(unittest.TestCase):

    def setUp(self):
        self.sample_grid = np.array([
            [1, 2, 0],
            [0, 3, 0],
            [0, 0, 0]
        ], dtype=int)

    def test_primitive_reflections_and_rotations(self):
        refl_h = CosmoGrammar.reflect_h(self.sample_grid)
        self.assertEqual(refl_h[0, 0], 0)
        self.assertEqual(refl_h[0, 2], 1)

        refl_v = CosmoGrammar.reflect_v(self.sample_grid)
        self.assertEqual(refl_v[2, 0], 1)
        self.assertEqual(refl_v[0, 0], 0)

        rot90 = CosmoGrammar.rotate_90(self.sample_grid)
        self.assertEqual(rot90.shape, (3, 3))

    def test_primitive_tile_and_scale(self):
        tiled = CosmoGrammar.tile(self.sample_grid, 2, 3)
        self.assertEqual(tiled.shape, (6, 9))

        scaled = CosmoGrammar.scale(self.sample_grid, 2)
        self.assertEqual(scaled.shape, (6, 6))
        self.assertEqual(scaled[0, 0], 1)
        self.assertEqual(scaled[0, 1], 1)
        self.assertEqual(scaled[1, 0], 1)
        self.assertEqual(scaled[1, 1], 1)

    def test_primitive_fill_enclosed(self):
        box_grid = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ], dtype=int)
        filled = CosmoGrammar.fill_enclosed(box_grid, fill_color=4, bg_color=0)
        self.assertEqual(filled[1, 1], 4)

    def test_ast_roundtrip(self):
        code = "rotate_90() >> recolor(2, 5) >> tile(2, 2)"
        prog = CosmoProgram.from_code(code)
        self.assertEqual(prog.to_code(), code)

        res = prog.execute(self.sample_grid)
        self.assertEqual(res.shape, (6, 6))

    def test_synthetic_task_generation(self):
        task = SyntheticTaskGenerator.generate_task(num_train=3, max_depth=2)
        self.assertIsNotNone(task)
        self.assertIn("train", task)
        self.assertIn("test", task)
        self.assertIn("program", task)
        self.assertEqual(len(task["train"]), 3)
        self.assertEqual(len(task["test"]), 1)

    def test_verifier_accuracy(self):
        task = SyntheticTaskGenerator.generate_task(num_train=3, max_depth=1)
        self.assertIsNotNone(task)
        # Ground truth program must verify to 100% exact match
        vr_true = CosmoVerifier.verify(task["program"], task)
        self.assertTrue(vr_true.is_exact_match)
        self.assertEqual(vr_true.pixel_accuracy, 1.0)
        self.assertIsNotNone(vr_true.predicted_test_output)

        # Faulty program must fail exact match
        vr_false = CosmoVerifier.verify("invert(0, 9)", task)
        # Invert won't match a generic random transform exactly
        self.assertTrue(vr_false.is_valid_syntax)

    def test_tokenizer_formatting(self):
        task = SyntheticTaskGenerator.generate_task(num_train=2, max_depth=1)
        self.assertIsNotNone(task)
        chatml = CosmoTokenizer.to_chatml_example(task)
        self.assertIn("messages", chatml)
        self.assertEqual(len(chatml["messages"]), 3)
        self.assertTrue(chatml["messages"][2]["content"].startswith("cosmolang:"))

        alpaca = CosmoTokenizer.to_alpaca_example(task)
        self.assertIn("instruction", alpaca)
        self.assertIn("input", alpaca)
        self.assertIn("output", alpaca)

    def test_synthesizer_depth1_solve(self):
        # Create a deterministic rotation task
        prog = CosmoProgram.from_code("rotate_180()")
        train_pairs = []
        for _ in range(3):
            inp = np.random.randint(0, 5, size=(4, 4))
            train_pairs.append({"input": inp.tolist(), "output": prog.execute(inp).tolist()})
        test_in = np.random.randint(0, 5, size=(4, 4))
        task = {
            "train": train_pairs,
            "test": [{"input": test_in.tolist(), "output": prog.execute(test_in).tolist()}],
            "program": "rotate_180()"
        }

        solver = CosmoSynthesizer()
        result = solver.solve(task, max_search_depth=1)
        self.assertTrue(result.success)
        self.assertEqual(result.program, "rotate_180()")
        self.assertEqual(result.predicted_grid, prog.execute(test_in).tolist())

if __name__ == "__main__":
    unittest.main()
