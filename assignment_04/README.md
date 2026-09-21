# Intelligent System Development - Assignment 04
## Comparing CNN and MLP Implementations: Scratch vs. Keras vs. PyTorch

### Student & Course Metadata
- **Course**: Intelligent System Development (`INTEL_SYS_DEV`)
- **Assignment**: Assignment 04
- **Student Name**: Bùi Nguyên Hoàng Việt
- **Student ID**: B23DCDT285
- **Class**: E23CNPM02
- **Team**: Individual Project
- **Lecturer**: Dinh Que Tran, Ph.D., Assoc. Prof.
- **Semester**: I.2026
- **Repository**: [https://github.com/minorin2847/INTEL_SYS_DEV_2026](https://github.com/minorin2847/INTEL_SYS_DEV_2026)

---

## 1. Overview & Objectives

This project conducts an empirical investigation into three distinct intelligent systems across three independent software abstraction tiers: pure vectorized NumPy developed from first principles with zero deep learning dependencies, high-level declarative TensorFlow/Keras, and modular object-oriented PyTorch.

The core objective is not merely tuning models for leaderboard accuracy, but systematically testing the central thesis of **Lecture 04**:
> When an identical learning formulation, data partition, and neural topology are strictly preserved, empirical classification accuracy remains essentially uniform across software libraries. The genuine divergence resides in algorithmic transparency, developer ergonomics, and hardware execution latency, rather than mathematical representational capacity.

### The Three Applications
1. **Diabetes Risk Screening (Tabular MLP)**:
   - **Task**: Binary metabolic risk classification using multi-year survey records from the Behavioral Risk Factor Surveillance System (BRFSS 2016-2020, $N=2,181,125$ observations).
   - **Dataset Link**: [Kaggle BRFSS Diabetes Indicator Dataset](https://www.kaggle.com/datasets/spandanjit2005/brfss-diabetes-indicator-dataset)
   - **Architecture**: Feed-forward Multi-Layer Perceptron ($50 \to 32 \to 16 \to 1$), totaling **2,177 parameters**.
   - **Characteristics**: Heterogeneous tabular features lacking spatial coordinate adjacency; requires balanced loss weighting ($w_{\text{neg}}=0.5922, w_{\text{pos}}=3.2126$) to handle severe 15.56% positive prevalence.
2. **Fashion-MNIST Apparel Categorization (Grayscale CNN)**:
   - **Task**: 10-class apparel recognition on $28\times28$ single-channel grayscale garments (60,000 train / 10,000 test).
   - **Dataset Link**: [Zalando Research Fashion-MNIST Repository](https://github.com/zalandoresearch/fashion-mnist) (also retrieved automatically via `keras.datasets.fashion_mnist`)
   - **Architecture**: Two-stage Convolutional Neural Network ($\text{Conv} \to \text{MaxPool} \to \text{Conv} \to \text{MaxPool} \to \text{Flatten} \to \text{Dense} \to \text{Dense}$), totaling **421,642 parameters**.
   - **Characteristics**: Exploits 2D spatial locality and translational invariance; implements an optimized `im2col` tensor unfolding engine in NumPy achieving a 40x speedup over naive nested coordinate loops.
3. **CIFAR-10 Photographic Object Recognition (Color CNN)**:
   - **Task**: 10-class object recognition on natural $32\times32\times3$ RGB scenes (50,000 train / 10,000 test).
   - **Dataset Link**: [University of Toronto CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html) (also retrieved automatically via `keras.datasets.cifar10`)
   - **Architecture**: Two-stage Convolutional Neural Network with 3 input channels, totaling **545,098 parameters**.
   - **Characteristics**: Multi-channel color processing with increased spatial complexity, discriminating visually challenging classes (cat vs. dog, automobile vs. truck).

---

## 2. Quantitative Summary of Experimental Results

### A. Test Classification Accuracy
| Application | Data Modality | Architecture | NumPy Scratch | TensorFlow/Keras | PyTorch | Spread |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Diabetes** | Tabular vector ($d=50$) | MLP (2,177 params) | 0.7310 | 0.7533 | **0.7819** | 5.09% |
| **Fashion-MNIST** | Grayscale image ($28\times28$) | CNN (421,642 params) | **0.8973** | 0.8603 | 0.8660 | 3.70% |
| **CIFAR-10** | Color image ($32\times32\times3$) | CNN (545,098 params) | 0.6033 | **0.6102** | 0.5696 | 4.06% |

### B. Wall-Clock Training Duration (Seconds)
| Application | NumPy Scratch | TensorFlow/Keras | PyTorch | Scratch Slowdown vs. Keras |
| :--- | :---: | :---: | :---: | :---: |
| **Diabetes (MLP)** | 69.4 s | **24.7 s** | 311.0 s | 2.8x |
| **Fashion-MNIST (CNN)** | 1,330.5 s (~22 min) | **75.6 s** | 191.5 s | **17.6x** |
| **CIFAR-10 (CNN)** | 1,875.8 s (~31 min) | **103.3 s** | 244.1 s | **18.2x** |

### Key Findings
- **Bit-Identical Parameter Parity**: Verified via programmatic assertions (`assert keras_param_count == scratch_param_count`) across all nine implementations.
- **Alternating Winners**: PyTorch led on Diabetes, Scratch on Fashion-MNIST, and Keras on CIFAR-10, demonstrating that no framework possesses an intrinsic inductive advantage.
- **Latency Inversion**: Scratch was faster than PyTorch on the compact MLP (where PyTorch's dynamic autograd graph allocation created fixed overhead), but was 17-18x slower on CNNs due to uncompiled Python execution of spatial convolutions.
- **Hidden Mechanics Surfaced**: Implementing loops from scratch exposed subtle framework behaviors, such as PyTorch's `BCEWithLogitsLoss(pos_weight=...)` scaling only the positive loss term (producing an algebraically higher loss of 0.87 vs. 0.51) and uncovering an extraneous $1/N$ gradient attenuation factor through numerical finite-difference gradient checks.

---

## 3. Repository Structure

```text
assignment_04/
├── README.md                      # Comprehensive project documentation
├── requirements.txt               # Direct package dependencies
├── diabetes/                      # Application I: Diabetes risk screening (MLP)
│   ├── data/                      # Multi-year BRFSS survey CSV files (2016-2020)
│   ├── model/                     # Serialized model weights & schema artifacts
│   │   ├── scratch_weights.npz    # Handcrafted NumPy trained parameters
│   │   ├── keras_model.keras      # Keras trained model file
│   │   ├── pytorch_model.pt       # PyTorch serialized state dictionary
│   │   ├── feature_names.joblib   # Preprocessed feature column names
│   │   └── input_schema.json      # Verified input metadata and types
│   └── notebook/
│       └── diabetes.ipynb         # Fully self-contained experiment notebook
├── fashion_mnist/                 # Application II: Fashion-MNIST categorization (CNN)
│   ├── model/                     # Serialized model artifacts
│   │   ├── scratch_weights.npz
│   │   ├── keras_model.keras
│   │   ├── pytorch_model.pt
│   │   └── input_schema.json
│   └── notebook/
│       └── fashion_mnist.ipynb    # Fully self-contained experiment notebook
├── cifar10/                       # Application III: CIFAR-10 recognition (CNN)
│   ├── model/                     # Serialized model artifacts
│   │   ├── scratch_weights.npz
│   │   ├── keras_model.keras
│   │   ├── pytorch_model.pt
│   │   └── input_schema.json
│   └── notebook/
│       └── cifar10.ipynb          # Fully self-contained experiment notebook
└── report/                        # Comprehensive LaTeX technical report
    ├── Assignment_04.tex          # Complete, granular academic paper
    ├── Assignment_04.pdf          # Compiled 34-page document
    └── images/                    # 28 high-resolution figures (300 DPI)
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.10.x (tested on Python 3.10.11)
- Windows / Linux / macOS

### Step 1: Clone the Repository
```bash
git clone https://github.com/minorin2847/INTEL_SYS_DEV_2026.git
cd INTEL_SYS_DEV_2026/assignment_04
```

### Step 2: Create and Activate Virtual Environment
```bash
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. Dataset Sources & Acquisition

| Benchmark Domain | Modality & Scale | Official Source / Repository | Acquisition & Setup |
| :--- | :--- | :--- | :--- |
| **BRFSS Diabetes** | Tabular vector ($d=50$, $N=2,181,125$) | [Kaggle BRFSS Dataset](https://www.kaggle.com/datasets/spandanjit2005/brfss-diabetes-indicator-dataset) | Download `DATASET_2016.csv` through `DATASET_2020.csv` and place in `diabetes/data/` |
| **Fashion-MNIST** | Grayscale ($28\times28\times1$, $N=70,000$) | [Zalando Research Repo](https://github.com/zalandoresearch/fashion-mnist) | Retrieved and cached automatically via `keras.datasets.fashion_mnist` on initial execution |
| **CIFAR-10** | Color RGB ($32\times32\times3$, $N=60,000$) | [University of Toronto Source](https://www.cs.toronto.edu/~kriz/cifar.html) | Retrieved and cached automatically via `keras.datasets.cifar10` on initial execution |

---

## 6. Execution Instructions

Each notebook is completely self-contained and operates autonomously without cross-referencing external notebooks.

### Interactive Execution via Jupyter
```bash
jupyter notebook
```
Navigate to any notebook (`diabetes/notebook/diabetes.ipynb`, `fashion_mnist/notebook/fashion_mnist.ipynb`, or `cifar10/notebook/cifar10.ipynb`) and run all cells sequentially.

### Headless Reproduction via `nbconvert`
To re-run any notebook headlessly from the command line:

```bash
# Execute Diabetes experiment:
python -m jupyter nbconvert --to notebook --execute --inplace diabetes/notebook/diabetes.ipynb --ExecutePreprocessor.timeout=1800

# Execute Fashion-MNIST experiment:
python -m jupyter nbconvert --to notebook --execute --inplace fashion_mnist/notebook/fashion_mnist.ipynb --ExecutePreprocessor.timeout=1800

# Execute CIFAR-10 experiment:
python -m jupyter nbconvert --to notebook --execute --inplace cifar10/notebook/cifar10.ipynb --ExecutePreprocessor.timeout=1800
```

> **Note**: Datasets for Fashion-MNIST and CIFAR-10 are automatically retrieved and cached via `keras.datasets`. For the diabetes application, the underlying BRFSS annual CSV files (`DATASET_2016.csv` through `DATASET_2020.csv`) must be located in `diabetes/data/`.

---

## 7. Artifact Verification

Every notebook concludes with an automated serialization and reload verification cell:
1. Exports model weights to `scratch_weights.npz`, `keras_model.keras`, and `pytorch_model.pt`.
2. Reloads all three artifacts from disk.
3. Asserts that predictions from reloaded models numerically match in-memory outputs computed during the same run.

---

## 8. Comprehensive Report

A full 34-page technical paper detailing the theoretical foundations, implementation mathematics, exploratory data distributions, loss trajectories, and efficiency trade-offs is available at:
- **LaTeX Source**: [`report/Assignment_04.tex`](report/Assignment_04.tex)
- **Compiled PDF**: [`report/Assignment_04.pdf`](report/Assignment_04.pdf)
- **Visualizations**: All 28 publication-ready figures are stored in [`report/images/`](report/images/).
