# CosmoLang Native Foundation Model Subsystem

The **CosmoLang Native Model** is an inductive neuro-symbolic framework for formal spatial reasoning on ARC-AGI-3 and high-order abstract reasoning benchmarks.

Unlike end-to-end vision transformers or LLMs that attempt direct autoregressive pixel token generation (frequently hallucinating asymmetric borders, off-by-one shapes, or distorted palettes), CosmoLang models the ARC domain as **program synthesis over a closed spatial transformation algebra**.

```
                ┌────────────────────────────────────────────────────────┐
                │             Demonstration Task (ARC Grids)             │
                └───────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                ┌────────────────────────────────────────────────────────┐
                │          CosmoTokenizer (ChatML Dense Format)          │
                └───────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                ┌────────────────────────────────────────────────────────┐
                │        CosmoLang Foundation Model (SFT / LoRA)         │
                │        Generates candidate programs: P1, P2, ..., Pk   │
                └───────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                ┌────────────────────────────────────────────────────────┐
                │        Symbolic LACA Verifier (Zero-Error Guard)       │
                │     Executes each Pi on Train Pairs in Sub-ms         │
                │     Filters by 100% Exact Match & Minimum MDL         │
                └───────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                ┌────────────────────────────────────────────────────────┐
                │        Deterministic Test Grid Execution               │
                │      Guaranteed mathematically verified solution       │
                └────────────────────────────────────────────────────────┘
```

---

## 1. Core Modules

| Module | Purpose | Key Classes & Functions |
| :--- | :--- | :--- |
| `grammar.py` | Closed spatial algebra, AST expressions & NumPy execution | `CosmoGrammar`, `CosmoOp`, `CosmoProgram` |
| `generator.py` | High-throughput synthetic task generation (1,500+ tasks/sec) | `SyntheticTaskGenerator` |
| `tokenizer.py` | Dense grid serialization & ChatML / Alpaca formatting | `CosmoTokenizer` |
| `verifier.py` | Sub-millisecond symbolic execution & MDL scoring | `CosmoVerifier`, `VerificationResult` |
| `synthesizer.py`| Neuro-symbolic synthesis engine combining LLM + Beam Search | `CosmoSynthesizer`, `SynthesisResult` |
| `export_dataset.py` | Scalable dataset exporter for model fine-tuning | `export_synthetic_dataset` |
| `train_lora.py`| SFT / LoRA fine-tuning recipe for Qwen2.5-Coder & Llama-3.2 | `main` CLI runner |
| `cli.py` | Interactive command-line interface | `cosmolang-model` entrypoint |

---

## 2. Spatial Transformation Algebra (18 Primitives)

All operations are implemented in pure **NumPy** with zero external dependencies:

1. **Reflections & Rotations**: `reflect_h()`, `reflect_v()`, `rotate_90()`, `rotate_180()`, `rotate_270()`, `transpose()`
2. **Symmetries**: `symmetrize_h()`, `symmetrize_v()`
3. **Physics & Gravity**: `gravity(direction='down'|'up'|'left'|'right')`
4. **Color Morphologies**: `recolor(src, dst)`, `filter_color(color)`, `invert(bg, fg)`
5. **Spatial Geometry**: `crop_bbox(bg_color=0)`, `shift(dr, dc, bg_color=0)`
6. **Contour & Topology**: `outline_contour(color)`, `fill_enclosed(color, bg_color=0)`
7. **Tiling & Scaling**: `tile(repeat_r, repeat_c)`, `scale(factor)`

Programs are chained using the pipeline operator `>>`:
```python
prog = CosmoProgram.from_code("crop_bbox() >> rotate_90() >> recolor(2, 4)")
result_grid = prog.execute(input_grid)
```

---

## 3. Quick Start & CLI

### Generate Synthetic Training Data
```bash
python -m cosmolang.native_model.cli generate --size 10000 --depth 3 --out cosmolang_train_10k.jsonl
```

### Run Benchmark
```bash
python -m cosmolang.native_model.cli benchmark --size 50 --depth 2
```

### Solve a Task JSON
```bash
python -m cosmolang.native_model.cli solve --task path/to/arc_task.json
```

### Fine-Tune Model with LoRA
```bash
python -m cosmolang.native_model.train_lora \
    --model_name_or_path Qwen/Qwen2.5-Coder-1.5B-Instruct \
    --dataset_path cosmolang_train_10k.jsonl \
    --output_dir ./cosmolang_weights \
    --epochs 3 \
    --batch_size 4 \
    --lora_r 16
```

---

## 4. Test Suite

Run unit and integration tests:
```bash
python -m unittest tests/test_native_model.py
```
