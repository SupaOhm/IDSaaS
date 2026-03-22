# IDSaaS — Intrusion Detection System as a Service

A minimal, modular Python prototype for researching hybrid NIDS pipelines with
lightweight deduplication. Designed for fast local experimentation.

---

## Setup Guide

### 1. Prerequisites

Make sure you have **Python 3.9+** installed. Check with:

```bash
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

---

### 2. Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from the rest of your system.

```bash
python3 -m venv .venv
```

This creates a `.venv/` folder in your project directory.

---

### 3. Activate the Virtual Environment

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Once activated, your terminal prompt will show `(.venv)` at the start.

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. What's in requirements.txt and Why

| Package | Why it's needed |
|---|---|
| `pandas` | Load and manipulate dataset CSV files (e.g. KDD Cup, CICIDS) |
| `numpy` | Numerical arrays — used for feature vectors and model I/O |
| `scikit-learn` | Evaluation helpers, preprocessing, and baseline ML utilities |
| `psutil` | Measure CPU and memory usage during experiments |
| `PyYAML` | Load config files — not strictly required now but useful for later |

> **Note:** `tensorflow` and `torch` are **commented out** in `requirements.txt` on purpose.
> The LSTM module is currently a stub. When you are ready to train a model, uncomment the one you prefer:
> - `torch` — lighter install, recommended for most research
> - `tensorflow` — heavier (~500 MB+), takes longer to install
>
> Install manually with:
> ```bash
> pip install torch
> # or
> pip install tensorflow
> ```

---

### 6. Common Install Issues

| Problem | Fix |
|---|---|
| `pip: command not found` | Use `pip3` instead of `pip` |
| `python: command not found` | Use `python3` instead of `python` |
| `tensorflow` install fails | Try `pip install tensorflow-cpu` for a smaller install |
| `torch` install is slow | Normal — it's ~200 MB. Let it finish. |
| Permission errors on Windows | Run your terminal as Administrator |

---

## Running the Project

### Run an Experiment

```bash
python3 main.py
```

Open `main.py` and change this line near the top to switch experiments:

```python
EXPERIMENT = "test_bloom_exact"   # ← change this
```

Available modes:

| Mode | Description |
|---|---|
| `test_no_dedup` | No dedup, signature detection only |
| `test_exact_hash` | ExactHashCache dedup + signature |
| `test_bloom_exact` | BloomFilter + ExactHashCache dedup + signature |
| `test_lstm_only` | LSTM detector (stub — returns 0.0 until model is trained) |
| `test_signature_only` | Rule-based detection only |
| `test_hybrid` | Signature + LSTM combined |

---

### Run the Smoke Tests

First install `pytest`:

```bash
pip install pytest
```

Then run:

```bash
pytest tests/ -v
```

All 9 tests should pass. This verifies that every core module imports correctly and behaves as expected.

---

## Project Structure

```
IDSaaS/
  src/
    bloom.py              # BloomFilter — probabilistic membership check
    exact_hash.py         # ExactHashCache — exact LRU hash store
    dedup.py              # DedupEngine — combines both, 3 strategies
    lstm_detector.py      # LSTMDetector — LSTM anomaly detection (stub)
    signature_detector.py # SignatureDetector — rule-based baseline
    hybrid_detector.py    # HybridDetector — fuses signature + LSTM
    metrics.py            # Accuracy, Precision, Recall, F1, FAR, Timer
    utils.py              # Shared helpers (hashing, CSV loader)
  main.py                 # ← Run experiments here
  data/                   # Raw datasets (not committed)
  saved_models/           # Trained LSTM weights (not committed)
  results/                # Experiment outputs (not committed)
  tests/                  # Smoke tests
  requirements.txt
  .gitignore
```

---

## Research Goals

- Compare deduplication strategies: none vs. exact cache vs. bloom + exact
- Compare detection approaches: signature vs. LSTM vs. hybrid
- Measure: Accuracy, Precision, Recall, F1, FAR, Throughput, Latency

---

## Status

Initial scaffold. LSTM training and inference not yet implemented. Signature rules are placeholder stubs. All modules are functional and importable from `src/`.
