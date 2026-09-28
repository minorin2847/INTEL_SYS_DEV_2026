# Assignment 05: CNN-3 vs CNN-5 in TensorFlow and PyTorch

This project evaluates the impact of network depth (3 convolutional layers vs. 5 convolutional layers) across two deep learning frameworks (**TensorFlow/Keras** and **PyTorch**) on three distinct tasks: 12 CNN runs plus 1 baseline MLP model (13 experimental runs total).

| Notebook | Dataset | Run IDs |
|---|---|---|
| [`svhn/notebook/sv_svhn.ipynb`](svhn/notebook/sv_svhn.ipynb) | **SVHN** (99,289 cropped digits, 10 classes) | `SV-TF-CNN-3`, `SV-TF-CNN-5`, `SV-PT-CNN-3`, `SV-PT-CNN-5` |
| [`gtsrb/notebook/gt_gtsrb.ipynb`](gtsrb/notebook/gt_gtsrb.ipynb) | **GTSRB** (51,839 traffic sign images, 43 classes) | `GT-TF-CNN-3`, `GT-TF-CNN-5`, `GT-PT-CNN-3`, `GT-PT-CNN-5` |
| [`diabetes/notebook/db_diabetes.ipynb`](diabetes/notebook/db_diabetes.ipynb) | **Playground S5E12 Diabetes** (300,000 patient records) | `DB-TF-CNN-3`, `DB-TF-CNN-5`, `DB-PT-CNN-3`, `DB-PT-CNN-5` (+ `DB-TF-MLP` baseline) |

Each notebook is completely self-contained and executes top-to-bottom.

---

## Environment Setup

Recommended Python version: **3.10–3.12**.

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate on Windows (cmd)
.\.venv\Scripts\activate.bat

# Activate on macOS / Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Hardware Acceleration

| Platform | TensorFlow Backend | PyTorch Backend |
|---|---|---|
| **Apple Silicon (macOS)** | Apple GPU (`tensorflow-metal`) | `mps` |
| **Linux / WSL2 + NVIDIA** | NVIDIA CUDA (`tensorflow[and-cuda]`) | `cuda` |
| **Windows + NVIDIA** | Multi-threaded CPU (or WSL2 for GPU) | `cuda` (e.g. `pip install torch --index-url https://download.pytorch.org/whl/cu126`) |
| **CPU Only** | Multi-threaded CPU | CPU |

The first code cell of each notebook inspects and logs active accelerators for both frameworks.

---

## Datasets & Kaggle Download

The raw dataset files are not committed to git due to size limits. Download them directly from Kaggle and place them into the respective `<task>/data/` directories as shown below.

| Dataset | Kaggle Source | Destination Files | Details |
|---|---|---|---|
| **SVHN** | [Street View House Numbers (SVHN)](https://www.kaggle.com/datasets/sahityasetu/street-view-house-numbers-images) (~246 MB) | `svhn/data/train_32x32.mat`<br>`svhn/data/test_32x32.mat` | 99,289 cropped digit images, 32×32 RGB, 10 classes (digits 0–9). |
| **GTSRB** | [German Traffic Sign Dataset](https://www.kaggle.com/datasets/harbhajansingh21/german-traffic-sign-dataset) (~124 MB) | `gtsrb/data/train.p`<br>`gtsrb/data/valid.p`<br>`gtsrb/data/test.p`<br>`gtsrb/data/signname.csv` | 51,839 resized images across 43 classes with sign label mappings. |
| **Diabetes** | [Playground Series S5E12](https://www.kaggle.com/competitions/playground-series-s5e12/data) (~35 MB) | `diabetes/data/train.csv` | 700k clinical records; notebooks draw a stratified sample of 300k rows. |

### Download Option A: Kaggle CLI (Recommended)

Make sure your Kaggle API key is placed at `~/.kaggle/kaggle.json` (or `C:\Users\<username>\.kaggle\kaggle.json` on Windows). Run the following commands from the `assignment_05/` directory:

```bash
# 1. SVHN
kaggle datasets download -d sahityasetu/street-view-house-numbers-images -p svhn/data --unzip

# 2. GTSRB
kaggle datasets download -d harbhajansingh21/german-traffic-sign-dataset -p gtsrb/data --unzip

# 3. Diabetes Prediction (Join competition on Kaggle first)
kaggle competitions download -c playground-series-s5e12 -f train.csv -p diabetes/data
```

> **Note:** If `train.csv` downloads as `train.csv.zip`, extract it into `diabetes/data/` so that `diabetes/data/train.csv` is present.

### Download Option B: Manual Browser Download

1. Open each Kaggle link from the table above.
2. Click **Download** (for the Diabetes competition, click **Join Competition** first to accept rules).
3. Unzip the archives and place the extracted files directly into the corresponding task `data/` directory (`svhn/data/`, `gtsrb/data/`, and `diabetes/data/`).

### Deterministic Splits (`splits.npz`)

Each task contains a committed `data/splits.npz` file containing the fixed 70% train / 15% validation / 15% test stratified partition indices generated under `SEED = 42`. Both TensorFlow and PyTorch load this exact file, ensuring sample-for-sample identical evaluation.

---

## Running the Notebooks

### Interactive Execution (VS Code / Jupyter Lab)

Open any of the notebooks directly in VS Code or Jupyter Lab, select the `.venv` Python kernel, and run cells sequentially:
- `svhn/notebook/sv_svhn.ipynb`
- `gtsrb/notebook/gt_gtsrb.ipynb`
- `diabetes/notebook/db_diabetes.ipynb`

### Headless / Command-Line Execution

To run a notebook end-to-end headlessly and save the outputs in-place:

```bash
# Run SVHN
jupyter nbconvert --to notebook --execute --inplace svhn/notebook/sv_svhn.ipynb

# Run GTSRB
jupyter nbconvert --to notebook --execute --inplace gtsrb/notebook/gt_gtsrb.ipynb

# Run Diabetes
jupyter nbconvert --to notebook --execute --inplace diabetes/notebook/db_diabetes.ipynb
```

---

## Project Structure & Outputs

```
assignment_05/
├── diabetes/
│   ├── data/                 # train.csv, splits.npz
│   ├── models/               # Saved .keras and .pt model checkpoints
│   ├── notebook/             # db_diabetes.ipynb
│   └── results/              # JSON logs per run and DB_comparison.csv
├── gtsrb/
│   ├── data/                 # train.p, valid.p, test.p, signname.csv, splits.npz
│   ├── models/               # Saved .keras and .pt model checkpoints
│   ├── notebook/             # gt_gtsrb.ipynb
│   └── results/              # JSON logs per run and GT_comparison.csv
├── svhn/
│   ├── data/                 # train_32x32.mat, test_32x32.mat, splits.npz
│   ├── models/               # Saved .keras and .pt model checkpoints
│   ├── notebook/             # sv_svhn.ipynb
│   └── results/              # JSON logs per run and SV_comparison.csv
├── report/
│   └── Assignment_05.pdf     # Compiled report PDF
├── requirements.txt
└── README.md
```

### Generated Artifacts
- **Metrics Logs** (`<task>/results/<run_id>.json`): Detailed training history, per-epoch wall time, inference latency (ms per 1,000 samples), and comprehensive test set evaluation metrics.
- **Comparison Tables** (`<task>/results/<DATASET>_comparison.csv`): Aggregated metrics table comparing CNN-3 vs. CNN-5 across TensorFlow and PyTorch.
- **Saved Weights** (`<task>/models/`): Best epoch model checkpoints saved as `.keras` (TensorFlow) and `.pt` (PyTorch).
