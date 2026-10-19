# Assignment 07: memory in deep recurrent networks (5-layer RNN vs 5-layer LSTM)

Intelligent System Development, PTIT. Student: Bùi Nguyên Hoàng Việt (B23DCDT285).
Repository: <https://github.com/minorin2847/INTEL_SYS_DEV_2026>

A 5-layer RNN and a 5-layer LSTM are written as compositions of five elementary functions (matrix product, addition, tanh,
sigmoid, element-wise product), checked numerically against PyTorch and Keras, and then trained in both frameworks on two
Kaggle datasets: Amazon reviews of unlocked phones (**EC**, sentiment classification) and daily prices of S&P 500 stocks
(**ST**, next-day volatility forecasting). Two datasets × two architectures × two frameworks = 8 runs, named
`<dataset>-<framework>-<model>`, for example `EC-PT-LSTM` (`TF` = Keras/TensorFlow, `PT` = PyTorch).

## Repository layout

| Path | Content |
|---|---|
| `00_rnn_lstm_concepts.ipynb` | the five functions, the 5-layer RNN and LSTM by hand in NumPy, checks against PyTorch and Keras, parameter counts, gradient maps; writes the theory figures `C_*.png` to `report/images/` |
| `customer_review/notebook/ec_reviews.ipynb` | EC: cleaning, tokenisation, baselines, 4 runs, evaluation (accuracy, F1, ROC-AUC, errors, confidence, accuracy by length) |
| `customer_review/data/` | `Amazon_Unlocked_Mobile.csv` (downloaded, not committed) |
| `customer_review/results/` | one JSON per run (`EC-*.json`) and `EC_comparison.csv` |
| `stock_forecast/notebook/st_stocks.ipynb` | ST: features, windows, baselines, 4 runs, evaluation (RMSE, MAE, R², forecasts, calm against turbulent markets) |
| `stock_forecast/data/` | `sp500_stocks.csv` and companion files (downloaded, not committed) |
| `stock_forecast/results/` | one JSON per run (`ST-*.json`) and `ST_comparison.csv` |
| `report/` | `Assignment_07.tex` / `.pdf`, `make_tables.py`, generated `table_*.tex`, `images/` (figures saved by the notebooks), `PLAN.md` |
| `requirements.txt` | Python packages |

## Results in one table

Test sets: 22,219 reviews (EC) and 81,925 windows (ST). Times are the median seconds per training epoch on one CPU.

| Dataset | Framework | Score | RNN | LSTM | Time RNN / LSTM |
|---|---|---|---|---|---|
| EC | Keras | macro F1 | 0.9084 | 0.9161 | 43 s / 198 s |
| EC | PyTorch | macro F1 | 0.8999 | 0.9176 | 42 s / 93 s |
| ST | Keras | R² (out of sample) | 0.0884 | 0.0920 | 51 s / 138 s |
| ST | PyTorch | R² (out of sample) | 0.0871 | 0.0965 | 46 s / 70 s |

The LSTM wins in all four pairs: clearly on the long reviews of EC, only marginally on the short-memory volatility task ST.
A TF-IDF + logistic-regression baseline (macro F1 0.930) is still better than all four EC networks; the report explains why.

## Datasets

The raw files are not committed (see `.gitignore`). Download them from Kaggle into the folders below.

| Code | Dataset | Kaggle | Folder |
|---|---|---|---|
| `EC` | Amazon Reviews: Unlocked Mobile Phones (PromptCloud) | [PromptCloudHQ/amazon-reviews-unlocked-mobile-phones](https://www.kaggle.com/datasets/PromptCloudHQ/amazon-reviews-unlocked-mobile-phones) | `customer_review/data` |
| `ST` | S&P 500 Stocks (daily) | [andrewmvd/sp-500-stocks](https://www.kaggle.com/datasets/andrewmvd/sp-500-stocks) | `stock_forecast/data` |

With the Kaggle CLI (needs `~/.kaggle/kaggle.json`), from the repository root:

```
kaggle datasets download -d PromptCloudHQ/amazon-reviews-unlocked-mobile-phones -p customer_review/data --unzip
kaggle datasets download -d andrewmvd/sp-500-stocks -p stock_forecast/data --unzip
```

## Running the notebooks

```
python -m venv .venv
.venv\Scripts\activate            # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

Open the notebooks in VS Code or Jupyter and *Run All*, or run them headless. The two dataset notebooks use paths relative to
their own folder (`../data`, `../results`, `../../report/images`), so run each of them from its `notebook/` directory; the
concepts notebook is run from the repository root.

```
jupyter nbconvert --to notebook --execute --inplace 00_rnn_lstm_concepts.ipynb
cd customer_review/notebook
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 ec_reviews.ipynb
cd ../../stock_forecast/notebook
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 st_stocks.ipynb
```

On a CPU the concepts notebook takes about 15 seconds, EC about 30 minutes and ST about 25 minutes (TensorFlow 2.22,
PyTorch 2.14, one Windows PC). Every run uses seed 42, so the metrics repeat exactly; the seconds per epoch do not.

## Building the report

After the notebooks have run (they save every figure to `report/images/`):

```
cd report
python make_tables.py          # table_*.tex from the result files, and images/cmp_time.png
xelatex Assignment_07.tex      # run twice, for the table of contents and the references
```

XeLaTeX is needed because the report uses the Times New Roman font through `fontspec`.
