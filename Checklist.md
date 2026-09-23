# "call me maybe" — Project Checklist

Function calling with constrained decoding, using Qwen/Qwen3-0.6B via `llm_sdk`.

## 1. Setup
- [X] Create repo with: `src/`, `data/input/`, `README.md`, `pyproject.toml`, `uv.lock`
- [X] Copy `llm_sdk/` package into project root (same level as `src/`)
- [X] `uv sync` must install `numpy` and `pydantic` (only allowed extra deps)
- [X] Forbidden: dspy, pytorch, transformers, huggingface, outlines, or similar
- [X] Python ≥ 3.10, flake8-compliant, full type hints, mypy clean, PEP 257 docstrings
- [-] Program entry point: `uv run python -m src [--functions_definition <f>] [--input <f>] [--output <f>]`
  - Defaults: read from `data/input/`, write to `data/output/`

## 2. Makefile (mandatory targets)
- [X] `install` — install deps (uv/pip/pipx)
- [X] `run` — run main script
- [X] `debug` — run with pdb
- [-] `clean` — remove `__pycache__`, `.mypy_cache`, etc.
- [-] `lint` — `flake8 .` + `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
- [X] `lint-strict` (optional) — `flake8 .` + `mypy . --strict`

## 3. Input handling
- [ ] Parse `data/input/function_calling_tests.json` — array of `{"prompt": "..."}`
- [ ] Parse `data/input/functions_definition.json` — function name, args (name+type), return type, description
- [ ] Handle missing files / invalid JSON gracefully (no crash, clear error message)
- [ ] Don't hardcode against example files — schema/prompts may change at review time

## 4. Core logic — constrained decoding (the actual point of the project)
- [ ] Use `Small_LLM_Model` from `llm_sdk` — only its **public** methods:
  - `get_logits_from_input_ids(input_ids) -> logits`
  - `get_path_to_vocab_file() -> str`
  - `encode(text) -> Tensor`
  - `decode(token_ids) -> str` (optional)
- [ ] Load vocab file to map token IDs ↔ token strings
- [ ] Implement token-by-token generation loop:
  1. Get logits for next token
  2. Determine which tokens are valid given current partial JSON + target schema (structural validity AND schema compliance — correct field names, correct types e.g. int/float/string/bool)
  3. Set logits of invalid tokens to `-inf`
  4. Select/sample from remaining valid tokens
  5. Append token, repeat until complete JSON object generated
- [ ] The **function must be selected by the LLM itself**, not by heuristics/keyword matching
- [ ] Must NOT just prompt the model and hope for valid JSON — decoding must be actually constrained
- [ ] All model-facing classes must use pydantic for validation

## 5. Output
- [ ] Write `data/output/function_calling_results.json`
- [ ] Array of objects, one per prompt, each with **exactly**:
  - `prompt` (string) — original request
  - `name` (string) — chosen function name
  - `parameters` (object) — args with correct types
- [ ] Output must be:
  - 100% valid, parseable JSON (no trailing commas/comments)
  - Schema-matching exactly (no extra keys, no prose)
  - All required args present with correct types

## 6. Reliability targets
- [ ] ≥90% correct function selection + argument extraction
- [ ] 100% valid/parseable JSON output
- [ ] Full test set processed in <5 min on standard hardware
- [ ] Graceful handling of edge cases: empty strings, large numbers, special chars, wrong types, ambiguous prompts, multi-param functions

## 7. Testing
- [ ] Write your own pytest/unittest tests (not graded/submitted) covering edge cases
- [ ] `.gitignore` excluding Python artifacts
- [ ] Manually verify: run program → check output file exists → validate JSON structure → verify names/types match definitions

## 8. README.md (English, at repo root)
First line (italicized): `*This activity has been created as part of the 42 curriculum by <login1>[, <login2>...]*`

Required sections:
- [ ] **Description** — goal + overview
- [ ] **Instructions** — install/run steps
- [ ] **Resources** — references + how AI was used (which tasks, which parts)
- [ ] **Algorithm explanation** — constrained decoding approach in detail
- [ ] **Design decisions** — key implementation choices
- [ ] **Performance analysis** — accuracy, speed, reliability
- [ ] **Challenges faced** — problems + solutions
- [ ] **Testing strategy** — how you validated it
- [ ] **Example usage** — clear run examples

## 9. Submission
- [ ] Repo contains: `src/`, `pyproject.toml`, `uv.lock`, `llm_sdk/`, `data/input/`, `README.md`, any other needed files
- [ ] **Do NOT** commit `data/output/` — generated during review
- [ ] Be ready for a live "brief modification" request during defense (test real understanding, not memorized code)
