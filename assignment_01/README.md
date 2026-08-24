# Assignment 01 — Diabetes Risk Prediction (Intelligent System Development)

A small intelligent system that predicts whether a patient is likely diabetic from 8 clinical
measurements, built end-to-end: **raw data → feature representation → traditional ML models →
evaluation → deployed application**. See [Report.md](Report.md) for the full write-up and
[Report_Notebook.ipynb](Report_Notebook.ipynb) for the graded notebook.

## 1. What this system does

- **Input:** 8 clinical features (Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
  BMI, DiabetesPedigreeFunction, Age).
- **Representation:** invalid `0` readings imputed with the training-set median, then
  standardized (`StandardScaler`).
- **Models:** Logistic Regression, SVM (Linear), SVM (RBF), KNN, Random Forest, XGBoost — plus a
  `DummyClassifier` baseline.
- **Output:** binary prediction (Diabetic / Non-Diabetic) with confidence, served through a
  FastAPI + React web app with SHAP explanations.

## 2. Repository map — what each file/folder is, and what to submit

| Path | What it is | Submit? |
| --- | --- | --- |
| [`Report_Notebook.ipynb`](Report_Notebook.ipynb) | **Main graded notebook.** All 24 required sections (system definition → EDA → baseline → 6 models → 3 experiments → final model → application demo → reflection), already executed with real outputs. | **Yes — this is the primary deliverable.** |
| [`Report.md`](Report.md) | **Technical report.** Written answers to every required question, results tables, screenshots of the app, limitations, reflection. | **Yes.** |
| [`Requirement.md`](Requirement.md) | Copy of the assignment brief, kept for reference only. | No (reference only). |
| `diabetes_dataset.csv` | The dataset itself (Kaggle, source cited in Report.md §4). | **Yes** (dataset + source info). |
| [`image.png`](image.png), [`image-1.png`](image-1.png) | Screenshots embedded in `Report.md` §11 (app dashboard, model-detail drawer). | Yes, as part of the report's figures. |
| `Data_visualizer.ipynb`, `Model_training.ipynb`, `build_notebook.py` | **Working/source notebooks.** `build_notebook.py` assembles the two notebooks above (plus written text) into `Report_Notebook.ipynb`. Not required for grading, but kept for transparency/reproducibility — see §4 below if you want to regenerate the report notebook after an edit. | Optional (nice to keep for reproducibility, not mandatory). |
| `*.pkl` (root) | Trained model/scaler/imputer artifacts produced by the notebook (`joblib.dump(...)`). | Optional — regenerable by re-running the notebook; keep if you want graders to skip re-training. |
| [`app/`](app) | **Application source code** (FastAPI backend + React/Vite frontend, Docker Compose). | **Yes — the full `app/` folder** is the "application source code" deliverable. |
| `app/backend/*.pkl` | Copies of the trained artifacts used by the live API (kept in sync with the root ones). | Yes, part of `app/`. |
| `.ipynb_checkpoints/`, `__pycache__/`, `node_modules/` | Auto-generated junk (editor checkpoints, Python/Node caches). | **No — do not submit**, already git-ignored. |

**In short: for submission, the 4 things that matter are `Report_Notebook.ipynb`, `Report.md`,
`diabetes_dataset.csv`, and the whole `app/` folder.** Everything else in the list is either
supporting material or safely optional.

## 3. How to run — Notebook

1. Install dependencies (Python 3.11+):
   ```bash
   pip install pandas numpy scikit-learn xgboost matplotlib seaborn joblib jinja2 jupyter
   ```
2. Open [`Report_Notebook.ipynb`](Report_Notebook.ipynb) in Jupyter/VS Code and **Run All**.
   It runs top to bottom with no manual steps — loads `diabetes_dataset.csv`, trains all 6
   models, runs the 3 experiments, auto-selects the best model (by F1), and demonstrates 3
   sample predictions at the end.

## 4. How to run — Web Application

### Option A: Docker Compose (recommended, one command)
```bash
cd app
docker-compose up --build
```
- Backend (FastAPI): http://localhost:8000
- Frontend (React): http://localhost:3000

### Option B: Run manually (no Docker)
**Backend:**
```bash
cd app/backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```
**Frontend** (in a second terminal):
```bash
cd app/frontend
npm install
npm run dev
```
Then open the URL Vite prints (default `http://localhost:5173`). If the frontend can't reach the
backend, set `VITE_API_URL` in `app/frontend/.env` (e.g. `VITE_API_URL=http://localhost:8000`).

### Using the app
1. The form is pre-filled with a sample patient (editable).
2. Click **Predict Outcome** — the backend runs the patient through all 6 trained models and
   returns a ranked comparison.
3. Click any model row to open a detail drawer with its prediction, confidence, accuracy, and a
   SHAP chart explaining which features drove the prediction.

## 5. Results summary

| Model | Accuracy | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Baseline (Most Frequent) | 64.94% | 0.000 | 0.000 | 0.000 |
| Logistic Regression | 70.78% | 0.600 | 0.500 | 0.545 |
| SVM (Linear) | 70.78% | 0.605 | 0.481 | 0.536 |
| SVM (RBF) | 69.48% | 0.581 | 0.463 | 0.515 |
| KNN (k=9) | 74.03% | 0.635 | 0.611 | 0.623 |
| **Random Forest (final model)** | **76.62%** | **0.696** | **0.593** | **0.640** |
| XGBoost | 74.68% | 0.653 | 0.593 | 0.621 |

Full discussion, the 3 controlled experiments, and the reflection are in
[Report.md](Report.md).

## 6. Known limitations

- Dataset is limited to females of Pima Indian heritage (768 records) — see Report.md §12 for the
  full limitations discussion.
- The app's live `/api/predict` endpoint does not re-impute invalid `0` inputs (it assumes a
  sensible manual entry);