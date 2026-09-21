# Assignment 03 — From Data Representation to Deep Learning

Three intelligent applications carried over from Assignment 02, each now trained and
compared across **four models** on the same train/test split: three classical
scikit-learn models plus one deep learning model implemented **entirely from scratch
with NumPy** (no TensorFlow, PyTorch, or Keras anywhere in the implementation).

```
Raw data → Understand → Clean → Represent → Train (3 classical + 1 from-scratch DL) → Evaluate → Compare → Persist
```

| # | Application | Task | Dataset | Rows | Winning model (by primary metric) |
|---|---|---|---|---|---|
| 1 | **Diabetes** risk screening | binary classification | BRFSS 2019+2020 survey | 815,711 | From-scratch DL (Accuracy 0.7343, F1 0.4648) |
| 2 | **House price** prediction | regression | USA real estate (600K sample) | 600,000 | Random Forest (R² 0.3980) |
| 3 | **Customer behaviour** (Flipkart reviews) | binary classification | Flipkart product reviews | 363,261 | Linear SVM (Accuracy 0.9295, F1 0.9550) |

Each application is self-contained under its own folder with an identical layout:

```
<app>/
  data/            raw dataset (not committed to git, see below)
  notebook/        <app>.ipynb — EDA + 3 classical ML models + from-scratch NumPy DL
                    model + evaluation/comparison + visualizations, executed with outputs
  model/           model_pipeline.joblib (best classical model) + dl_weights.npz
                    (from-scratch DL weights) + feature_names.joblib + input_schema.json
  requirements.txt numpy, pandas, scikit-learn, matplotlib, seaborn — no DL framework
report/            Assignment_03.tex / .pdf — final report across all 3 apps
materials/         lecture slides this assignment is based on
REQUIREMENT.md     assignment brief distilled from the lecture materials
```

No `api/`, `web/`, or `mobile/` folders this round: both source lecture decks stop at the
modeling pipeline (representation → forward propagation → loss → backpropagation →
gradient descent → evaluation) and never mention deployment, so this assignment's
deliverable is notebook-level only.

The final report, **`report/Assignment_03.pdf`** (LaTeX source in
`report/Assignment_03.tex`), walks through the lecture's central equation and every
application's problem, dataset, cleaning, representation, classical models, from-scratch
deep learning model, and 4-model comparison in detail, plus a cross-application summary
and discussion of what changed from Assignment 02.

---

## Environment

| | |
|---|---|
| Python | dedicated virtual environment at `assignment_03/.venv` (registered as Jupyter kernel `assignment_03`) |
| Key packages | numpy 2.5.3, pandas 3.0.5, scikit-learn 1.9.1, scipy 1.18.1, matplotlib 3.11.2, seaborn 0.13.2, jupyter, nbconvert 7.16.6 |
| Random seed | `RANDOM_SEED = 42` everywhere: splits, shuffles, weight initialization |
| OS | Windows |

No `tensorflow`, `torch`, or `keras` import appears anywhere in the three notebooks.
scikit-learn is used only for each application's three classical models, never for the
from-scratch deep learning model itself.

```bash
cd assignment_03
python -m venv .venv
.venv/Scripts/pip install -r diabetes/requirements.txt   # same deps for all 3 apps
.venv/Scripts/python -m ipykernel install --user --name=assignment_03
```

---

## Data-representation summary (mandatory table)

| Application | Raw form | Numerical representation | Classical model input | DL model input & architecture |
|---|---|---|---|---|
| Diabetes | 2 CSVs (BRFSS 2019, 2020) | scaled continuous + passthrough ordinal + one-hot nominal + `year` flag | `X ∈ ℝ^{N×49}` dense | `X ∈ ℝ^{N×49}`, architecture `49 → 49 → 24 → 1` |
| House price | 1 CSV (US listings) | scaled continuous (incl. log-transformed heavy-tailed columns) + one-hot status/state + frequency-encoded city | `X ∈ ℝ^{N×65}` dense | `X ∈ ℝ^{N×65}`, architecture `65 → 64 → 32 → 1`, linear output (no sigmoid) |
| Customer behaviour | 1 CSV (Flipkart reviews) | TF-IDF (1–2 gram) over `Summary` text ‖ standardized `Price` | `X ∈ ℝ^{N×416{,}771}` sparse (full vocabulary) | `X ∈ ℝ^{N×5{,}001}` (5,000-term capped TF-IDF ‖ Price), architecture `5000 → 128 → 32 → 1` |

Every dimension, and the reasoning behind each representation choice, is explained in the
corresponding notebook's markdown cells and in `report/Assignment_03.pdf` §3–5.

---

## Application 1 — Diabetes

**Dataset:** Kaggle
[`spandanjit2005/brfss-diabetes-indicator-dataset`](https://www.kaggle.com/datasets/spandanjit2005/brfss-diabetes-indicator-dataset)
(`DATASET_2019.csv` + `DATASET_2020.csv`, already in `diabetes/data/`). 815,711 rows,
binary target `is_diabetic` (collapsed from a 3-class field), 15.6% positive.

**Models:** Logistic Regression, Random Forest (continuity with Assignment 02), Gradient
Boosting, and a from-scratch NumPy network (`49 → 49 → 24 → 1`, ReLU + sigmoid, binary
cross-entropy). All four trained with balanced sample weighting to correct for class
imbalance.

**Result:** the from-scratch DL model wins by F1 (0.4648), narrowly ahead of Gradient
Boosting (0.4633), Logistic Regression (0.4622), and Random Forest (0.4621) — all four
land within half a point of each other once balanced weighting is applied.

```bash
cd assignment_03/diabetes
../.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace \
    notebook/diabetes.ipynb --ExecutePreprocessor.timeout=1800
```

---

## Application 2 — House Price

**Dataset:** Kaggle
[`minorin2847/usa-real-estate-600k-sample`](https://www.kaggle.com/datasets/minorin2847/usa-real-estate-600k-sample)
(`realtor-data-sample.csv`, already in `house_price/data/`), a 600,000-row seeded sample
of
[`ahmedshahriarsakib/usa-real-estate-dataset`](https://www.kaggle.com/datasets/ahmedshahriarsakib/usa-real-estate-dataset).
Regression target `price` (USD), trained in `log1p` space.

**Models:** Linear Regression, Random Forest (continuity with Assignment 02), Gradient
Boosting, and a from-scratch NumPy network (`65 → 64 → 32 → 1`, ReLU hidden layers,
linear output, MSE loss).

**Result:** Random Forest wins on every metric (RMSE 1,004,048 / MAE 225,937 / R²
0.3980). The from-scratch DL model places third (R² −1.1044), ahead of Linear Regression
(R² −48.3632) — both suffer on this heavy-tailed target because their output layer has no
ceiling the way a tree's leaf-average prediction does.

```bash
cd assignment_03/house_price
../.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace \
    notebook/house_price.ipynb --ExecutePreprocessor.timeout=1800
```

---

## Application 3 — Customer Behaviour (Flipkart Reviews)

**Dataset:** Kaggle
[`niraliivaghani/flipkart-dataset`](https://www.kaggle.com/datasets/niraliivaghani/flipkart-dataset)
(`flipkart_reviews.csv`, already in `customer_behaviour/data/`). 363,261 rows, binary
target `is_recommended` (`Rate >= 4`). The TF-IDF representation is built from `Summary`
rather than `Review`, since `Review` turned out to be overwhelmingly repeated boilerplate
text (see the notebook's EDA section and `report/Assignment_03.pdf` §5.3 for the full
investigation).

**Models:** Logistic Regression (continuity with Assignment 02), Linear SVM, Multinomial
Naive Bayes, and a from-scratch NumPy network (`5000 → 128 → 32 → 1`, ReLU + sigmoid,
binary cross-entropy, mini-batch gradient descent).

**Result:** Linear SVM wins by F1 (0.9550), Logistic Regression close behind (0.9523),
the from-scratch DL model right there with them (0.9506) despite reading only 5,000 of
the full 416,770-term vocabulary, and Multinomial Naive Bayes trailing (0.9402, but with
the highest recall of all four at 0.9900).

```bash
cd assignment_03/customer_behaviour
../.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace \
    notebook/customer_behaviour.ipynb --ExecutePreprocessor.timeout=1800
```

---

## Reproducibility notes

- Each notebook ends with a reload-and-verify cell: it reloads `model_pipeline.joblib`
  and `dl_weights.npz` from disk and asserts their predictions match the in-memory
  versions computed during that same run, the same discipline Assignment 02 used.
- Every scaler/vectorizer is fit on the training split only, then applied unchanged to
  the test split — no leakage.
- Raw dataset CSVs are **not committed to git** (each is 40–113MB); `<app>/data/` is kept
  via `.gitkeep` and the notebooks load directly from the Kaggle-downloaded files listed
  above. Re-download with the Kaggle CLI:

  ```bash
  kaggle datasets download -d spandanjit2005/brfss-diabetes-indicator-dataset -f csv/DATASET_2019.csv -p diabetes/data --unzip
  kaggle datasets download -d spandanjit2005/brfss-diabetes-indicator-dataset -f csv/DATASET_2020.csv -p diabetes/data --unzip
  kaggle datasets download -d minorin2847/usa-real-estate-600k-sample -p house_price/data --unzip
  kaggle datasets download -d niraliivaghani/flipkart-dataset -p customer_behaviour/data --unzip
  ```
