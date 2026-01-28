# docxbrief (Stage A)

Scan `.docx` files in a directory and generate an AsciiDoc summary (`summary.adoc`) with a changelog.
Stage A is **LLM-free** (deterministic / reproducible). Stage B will add Codex/tmux multi-agent behaviors.

---

## What this tool does

- Finds `.docx` files under `input_dir` (glob + optional filename regex)
- Extracts text from each `.docx`
- Produces an AsciiDoc report:
  - File list table (mtime/hash)
  - Per-file bullet summaries (heuristic/extractive)
  - Changelog (for updates)
- On `update`, only changed files are reprocessed (hash-based)

---

## Quick start (Mac / Linux)

### 1) Create venv & install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### 2) Initialize templates

```bash
docxbrief init
```

This creates:
- `docxbrief.yaml` (config template)
- `summary.adoc` (output template, not filled yet)
- `.docxbrief/` (state dir)

### 3) Put your docx files

Place `.docx` files under `./docs/` (default), or change `project.input_dir` in `docxbrief.yaml`.

### 4) Run

```bash
docxbrief scan
docxbrief build
```

To update later:

```bash
docxbrief update
```

---

## Configuration (docxbrief.yaml)

Default paths:
- Input: `./docs`
- Output: `./summary.adoc`
- State: `./.docxbrief/manifest.json`

Common knobs:
- `scan.include_glob` / `scan.exclude_glob`
- `filter.filename_regex` (optional, multiple allowed)
- `summarize.bullets_max`
- `update.detect_by` (recommended: `sha256`)

---

## Interactive shell (Shogun A)

A small interactive helper that proposes config edits and asks for approval:

```bash
docxbrief shell
```

Flow:
1. Shows current config
2. Lets you edit (dir/patterns/output)
3. Writes `docxbrief.yaml.proposed`
4. Shows diff
5. Applies only if you approve
6. Suggests `scan/build/update`

---

## tmux dashboard (optional)

Stage A uses tmux as a **progress dashboard** (no multi-agent communication required).

```bash
bash tools/tmux-dev.sh
```

Recommended panes:
- shell UI
- log tail
- summary preview
- manifest preview

---

## Troubleshooting

### Python version issues (especially 3.14+)
Some third-party packages may lag behind the newest Python.
If `pip install -e .` fails, try a stable Python (e.g., 3.12):

**Mac (Homebrew)**
```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Word temporary files appear
The tool ignores common Word temp files like `~$*.docx` by default.

---

## License
MIT (recommended for educational distribution)
