# Recurrent Neural Networks on Sequential Time Series: From Scratch, in Keras and in PyTorch

**Course:** Intelligent System Development (Assignment 06)  
**Institution:** Posts and Telecommunications Institute of Technology (PTIT)  
**Lecturer:** Assoc. Prof. Dinh Que Tran, Ph.D. (`quetd@ptit.edu.vn`)  
**Author:** Bùi Nguyên Hoàng Việt  
**Student ID:** B23DCDT285  
**Class:** E23CNPM02  
**GitHub Repository:** [https://github.com/minorin2847/INTEL_SYS_DEV_2026](https://github.com/minorin2847/INTEL_SYS_DEV_2026)

---

## 1. Project Overview

This repository contains an end-to-end comparative study of Recurrent Neural Networks (RNNs) applied to real-world sequence modeling tasks. The core vanilla RNN architecture is evaluated across three software paradigms to examine framework abstractions and numerical parity:

1. **Pure NumPy from Scratch (`SC`):** Fully vectorized forward recurrence, analytical Backpropagation Through Time (BPTT), global gradient norm clipping, and an Adam optimizer with first and second moment tracking.
2. **TensorFlow Keras (`TF`):** High-level declarative layer abstractions using `layers.SimpleRNN`, compiled with custom epoch profiling callbacks and early stopping.
3. **PyTorch (`PT`):** Modular object-oriented implementation using `torch.nn.RNN`, featuring an explicit manual training loop, custom mini-batch permutation, and dual-bias alignment.

In addition to vanilla RNNs, gated recurrent architectures (Long Short-Term Memory, **LSTM**, and Gated Recurrent Unit, **GRU**) are benchmarked in both Keras and PyTorch to evaluate the practical trade-offs between gating complexity, parameter counts, CPU execution latency, and predictive performance.

The investigation is carried out on two distinct empirical domains with radically different signal-to-noise ratios:
- **E-Commerce Retail Fulfillment:** Multi-product next-day unit order forecasting displaying weekly rhythm and holiday seasonality.
- **Financial Stock Returns:** Multi-asset next-day equity log return prediction under efficient market conditions.

---

## 2. Datasets and Kaggle Sources

Both datasets are sourced from open Kaggle repositories and preprocessed into supervised sliding windows using strict chronological train/validation/test partitions (70% train, 15% validation, 15% out-of-sample test).

### 2.1 E-Commerce Retail Demand (`EC`)
- **Dataset Source:** [Online Retail II UCI on Kaggle](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
- **Local File Path:** `ec_retail/dataset/online_retail_II.csv`
- **Volume:** Over 800,000 transaction records across two calendar years (2009–2011).
- **Domain Framing:** Forecasting next-day physical order volume across the top 750 most active items over 604 open warehouse operating days. Closed days (Saturdays and Christmas holidays) are preserved as an explicit temporal gap feature rather than zero-filled.
- **Window Formulation:** Lookback horizon $T = 28$ days, $F = 10$ features per time step (current sales, cancellation units, transaction frequencies, gap days, and one-hot day-of-week indicators). Total sliding windows: **431,250**.

### 2.2 Financial Stock Returns (`ST`)
- **Dataset Source:** [S&P 500 Stock Data on Kaggle](https://www.kaggle.com/datasets/camnugent/sandp500)
- **Local File Path:** `st_sp500/dataset/all_stocks_5yr.csv`
- **Volume:** 1,258 trading days (2013–2018) across S&P 500 member companies.
- **Domain Framing:** Forecasting next-day percentage log returns across 350 liquid equities. The raw price levels are strictly excluded from inputs to eliminate non-stationarity and avoid spurious baseline illusions.
- **Window Formulation:** Lookback horizon $T = 30$ trading days, $F = 4$ stationary features per day (log return, normalized daily trading volume, high-low intraday range, and open-close price spread). Total sliding windows: **429,800**.

---

## 3. Repository Architecture

```text
assignment_06/
├── README.md                        # Comprehensive project documentation
├── requirements.txt                 # Exact Python dependency specifications
├── ec_retail/                       # Case Study 1: Retail Demand Forecasting
│   ├── dataset/
│   │   ├── online_retail_II.csv     # Extracted raw transactions
│   │   └── ec_splits.npz            # Processed chronological train/val/test splits
│   ├── notebook/
│   │   ├── ec_retail.ipynb          # Production executed notebook (EDA, models, eval)
│   │   └── results/                 # Serialized JSON metrics and EC_comparison.csv
├── st_sp500/                        # Case Study 2: Financial Returns Prediction
│   ├── dataset/
│   │   ├── all_stocks_5yr.csv       # Extracted raw OHLCV equity bars
│   │   └── st_splits.npz            # Processed chronological train/val/test splits
│   ├── notebook/
│   │   ├── st_sp500.ipynb           # Production executed notebook (EDA, models, eval)
│   │   └── results/                 # Serialized JSON metrics and ST_comparison.csv
└── report/                          # Technical Report
    └── Assignment_06.pdf            # Complete 17-page PDF technical report
```

---

## 4. Framework Parity and Mathematical Equivalence

A critical component of this study is validating that high-level deep learning frameworks evaluate the exact mathematical functions intended:

- **Exact Weight Alignment:** A single random weight dictionary $W_0$ is generated in NumPy and converted into Keras and PyTorch tensor formats. PyTorch's secondary bias vector (`bias_hh_l0`) is explicitly zeroed out and frozen (`requires_grad_(False)`), ensuring an identical parameter budget across all three environments:
  - Retail: exactly **1,409** trainable parameters ($10 \times 32 + 32 \times 32 + 32 + 32 + 1$).
  - Stocks: exactly **1,217** trainable parameters ($4 \times 32 + 32 \times 32 + 32 + 32 + 1$).
- **Forward Output Parity:** When evaluated on identical mini-batches using $W_0$, the maximum absolute discrepancy between any framework pair satisfies:
  $$\max |\hat{y}_A - \hat{y}_B| < 3.6 \times 10^{-7}$$
  confirming exact numerical agreement within 32-bit floating-point precision.
- **Analytical Gradient Verification:** Backpropagation Through Time in pure NumPy is verified against central finite differences in float64 precision:
  $$\max \left| \frac{\partial L}{\partial \theta}_{\text{analytical}} - \frac{\partial L}{\partial \theta}_{\text{numerical}} \right| < 3.0 \times 10^{-6}$$

---

## 5. Empirical Benchmark Results

All models were trained on CPU with mini-batch size 128, Adam optimizer ($\text{lr} = 10^{-3}$, $\epsilon = 10^{-7}$), and global gradient clipping at $1.0$.

### 5.1 Retail Demand Forecasting Performance

| Run ID | Framework | Model | Trainable Params | Test RMSE (Units) | Test MAE (Units) | Out-of-Sample $R^2$ | Time / Epoch | Inference (ms / 1k) |
|---|---|---|---|---|---|---|---|---|
| *Baseline: persistence* | Heuristic | $y_t = y_{t-1}$ | -- | 82.68 | 23.91 | -0.044 | -- | -- |
| *Baseline: seasonal naive* | Heuristic | $y_t = y_{t-6}$ | -- | 81.06 | 23.19 | -0.030 | -- | -- |
| *Baseline: training mean* | Constant | $\bar{y}_{\text{train}}$ | -- | 67.88 | 19.26 | 0.000 | -- | -- |
| **`EC-SC-RNN`** | Pure NumPy | Vanilla RNN | 1,409 | 62.51 | 15.90 | 0.439 | 3.4 s | 5.39 ms |
| **`EC-TF-RNN`** | TensorFlow | Vanilla RNN | 1,409 | 62.82 | 15.99 | 0.439 | 4.8 s | 7.53 ms |
| **`EC-PT-RNN`** | PyTorch | Vanilla RNN | 1,409 | 62.84 | 16.00 | 0.439 | 5.9 s | 2.26 ms |
| **`EC-TF-LSTM`** | TensorFlow | LSTM | 5,537 | 61.74 | 15.88 | 0.445 | 10.7 s | 15.46 ms |
| **`EC-PT-LSTM`** | PyTorch | LSTM | 5,665 | 62.03 | 15.83 | 0.447 | 8.9 s | 3.75 ms |
| **`EC-TF-GRU`** | TensorFlow | GRU | 4,257 | 61.73 | 15.78 | 0.448 | 10.8 s | 13.48 ms |
| **`EC-PT-GRU`** | PyTorch | GRU | 4,257 | 62.24 | 15.87 | 0.448 | 18.8 s | 6.19 ms |

*Retail Finding:* Recurrent models successfully extract operational signals, beating naive baselines by over 18 units of RMSE ($R^2 \approx 0.44$). Framework implementations converge to within 0.5% RMSE of each other. Gating mechanisms provide a modest 1.2% reduction in RMSE at the expense of a 3–4× increase in parameter count and training latency.

---

### 5.2 S&P 500 Equity Returns Prediction Performance

| Run ID | Framework | Model | Trainable Params | Test RMSE (Log Return) | Directional Accuracy | Information Coeff (IC) | Time / Epoch | Inference (ms / 1k) |
|---|---|---|---|---|---|---|---|---|
| *Baseline: zero return* | Heuristic | $\hat{y} = 0$ | -- | 0.01572 | -- | -- | -- | -- |
| *Baseline: always up* | Heuristic | $\hat{y} = +10^{-6}$ | -- | 0.01572 | -- | -- | -- | -- |
| *Baseline: previous-day* | Heuristic | $\hat{y}_t = y_{t-1}$ | -- | 0.02232 | 49.20% | -0.0107 | -- | -- |
| *Baseline: training mean* | Constant | $\bar{y}_{\text{train}}$ | -- | 0.01572 | 53.06% | -- | -- | -- |
| **`ST-SC-RNN`** | Pure NumPy | Vanilla RNN | 1,217 | 0.01585 | 50.84% | -0.0153 | 4.0 s | 6.13 ms |
| **`ST-TF-RNN`** | TensorFlow | Vanilla RNN | 1,217 | 0.01594 | 48.41% | -0.0348 | 6.4 s | 6.44 ms |
| **`ST-PT-RNN`** | PyTorch | Vanilla RNN | 1,217 | 0.01585 | 49.58% | -0.0271 | 6.9 s | 2.67 ms |
| **`ST-TF-LSTM`** | TensorFlow | LSTM | 4,769 | 0.01585 | 48.02% | -0.0251 | 11.9 s | 15.67 ms |
| **`ST-PT-LSTM`** | PyTorch | LSTM | 4,897 | 0.01581 | 49.27% | -0.0223 | 8.8 s | 3.84 ms |
| **`ST-TF-GRU`** | TensorFlow | GRU | 3,681 | 0.01588 | 48.27% | -0.0299 | 12.2 s | 14.21 ms |
| **`ST-PT-GRU`** | PyTorch | GRU | 3,681 | 0.01582 | 48.53% | -0.0278 | 20.2 s | 6.43 ms |

*Financial Finding:* Under a stationary log-return formulation, no recurrent neural model outperforms the trivial baseline of predicting zero return ($R^2 \approx 0$). Directional classification accuracy remains near 49–50%, illustrating that financial market efficiency renders daily equity price changes statistically indistinguishable from a random walk.

---

## 6. How to Reproduce

### 6.1 Environment Setup
1. Create and activate a dedicated virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # Linux / macOS
   source .venv/bin/activate
   ```
2. Install the validated dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 6.2 Acquiring Datasets
Place the CSV files into their respective directories:
- `ec_retail/dataset/online_retail_II.csv` (from [Online Retail II on Kaggle](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci))
- `st_sp500/dataset/all_stocks_5yr.csv` (from [S&P 500 on Kaggle](https://www.kaggle.com/datasets/camnugent/sandp500))

### 6.3 Executing the Notebooks
Execute each notebook top to bottom within Jupyter Lab or run headless:
```bash
# Run retail demand experiment
jupyter execute ec_retail/notebook/ec_retail.ipynb

# Run S&P 500 equity experiment
jupyter execute st_sp500/notebook/st_sp500.ipynb
```
Both notebooks automatically save evaluation metrics to their local `results/` directories and output evaluation plots to their respective `report/images/` directories.

