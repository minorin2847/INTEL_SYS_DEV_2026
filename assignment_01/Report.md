# Assignment 1: Diabetes System Report
- Name: Bùi Nguyên Hoàng Việt
- Student ID: B23DCDT285
- Github repo: [https://github.com/minorin2847/INTEL_SYS_DEV_2026](https://github.com/minorin2847/INTEL_SYS_DEV_2026)

## 1. Introduction
Diabetes is one of the most common chronic conditions worldwide, and catching it early makes a real difference in how manageable it is. This report walks through an intelligent system that was built to help with that: given a handful of routine clinical measurements, it predicts whether a female patient is likely to have diabetes. The report covers how the problem was framed, how the data was turned into something a model can learn from, which traditional machine learning models were trained and compared, and what the resulting system can (and can't) actually do.

## 2. System Definition

### System Statement
The system is best described as a diagnostic assistant. It takes a patient's clinical and demographic data — things like glucose level, BMI, and age — and predicts whether that patient has diabetes. It isn't meant to replace a doctor's judgment; rather, it's a fast, low-cost first pass that flags high-risk patients so a clinician knows where to look more closely.

### System Diagram
![System Diagram](System_Diagram.png)

## 3. Problem Definition
- **What real-world problem does the system address?** Early, low-cost detection of diabetes, so timely medical intervention and lifestyle changes can reduce long-term health complications down the line.
- **What information does the system receive?** A patient's age plus a set of clinical measurements: number of pregnancies, glucose level, blood pressure, skin thickness, insulin level, BMI, and a diabetes pedigree function score (a rough proxy for genetic risk).
- **How is that information represented internally?** As a structured feature vector of real numbers. Zero readings that are physiologically impossible (like a Glucose or BMI of 0) are treated as missing and imputed with the training-set median, and the resulting vector is standardized so every feature sits on comparable footing.
- **What does the model learn?** The statistical relationship — the decision boundary — between the input clinical features and the historic diagnosis, i.e. which patterns in the data tend to show up alongside a diabetes diagnosis.
- **What decision or prediction does it produce?** A binary classification: 1 (Diabetic) or 0 (Non-Diabetic).
- **Who or what uses the prediction?** Healthcare professionals, and, through a screening application, potentially patients themselves — as a preliminary signal that further testing may be warranted, not a final word.

## 4. Dataset
- **Dataset Source:** Kaggle - Diabetes Dataset (https://www.kaggle.com/datasets/hasibur013/diabetes-dataset)
- **What real-world phenomenon is represented?** The physiological and demographic factors associated with diabetes onset in a population of female patients of Pima Indian heritage.
- **What is one observation?** A single patient's medical record at one point in time — a snapshot, not a history.
- **What are the features?** Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age.
- **What is the target?** `Outcome` (the diagnosis).
- **Is the target numerical or categorical?** Categorical (binary).
- **Is this regression or classification?** Classification.
- **How many observations are available?** 768.
- **How many features are available?** 8.
- **Which features are numerical?** All 8 — some continuous, some discrete integers.
- **Which features are categorical?** None of the input features; only the target `Outcome` is categorical.

## 5. Data Representation

+--------------------------+-----------+----------------+---------------------------------------------------+
| Feature                  | Type      | Representation | Meaning                                            
+==========================+===========+================+===================================================+
| Pregnancies              | Numerical | Integer        | Number of times pregnant                           
+--------------------------+-----------+----------------+---------------------------------------------------+
| Glucose                  | Numerical | Real value     | Plasma glucose concentration a 2 hours in an oral  
|                          |           |                | glucose tolerance test                             
+--------------------------+-----------+----------------+---------------------------------------------------+
| BloodPressure            | Numerical | Real value     | Diastolic blood pressure (mm Hg)                   
+--------------------------+-----------+----------------+---------------------------------------------------+
| SkinThickness            | Numerical | Real value     | Triceps skin fold thickness (mm)                   
+--------------------------+-----------+----------------+---------------------------------------------------+
| Insulin                  | Numerical | Real value     | 2-Hour serum insulin (mu U/ml)                     
+--------------------------+-----------+----------------+---------------------------------------------------+
| BMI                      | Numerical | Real value     | Body mass index (weight in kg/(height              
|                          |           |                | in m)^2)                                           
+--------------------------+-----------+----------------+---------------------------------------------------+
| DiabetesPedigreeFunction | Numerical | Real value     | Diabetes pedigree function (genetic risk)          
+--------------------------+-----------+----------------+---------------------------------------------------+
| Age                      | Numerical | Integer        | Age in years                                       
+--------------------------+-----------+----------------+---------------------------------------------------+

There are no categorical features to encode here, but the pipeline still transforms the data twice before it reaches a model. Invalid `0` readings for things like Glucose and BMI are first replaced with the training-set median (never the test-set median — the imputer and scaler are both `fit()` on the training split only and `transform()`-ed onto the test split, so no test-set information ever leaks into preprocessing). The whole vector is then standardized to mean 0 and variance 1. So a single feature actually passes through three distinct forms along the pipeline: the **raw feature** (possibly an invalid 0), the **imputed feature** (0 replaced by the train-only median), and the **model input** (the imputed feature standardized for distance-based models, or left unscaled for tree-based models, which don't need it).

## 6. Traditional ML Methods

### 1. Logistic Regression
- **What representation does it receive?** Scaled numerical feature vectors.
- **What relationship does it try to learn?** A linear relationship between the features and the log-odds of the patient being diabetic.
- **What parameters or structures are learned?** A weight (coefficient) per feature, plus a bias term.
- **What criterion guides learning?** Maximizing the likelihood of the training data — equivalently, minimizing log-loss.
- **What assumptions does the model make?** That the log-odds relationship is roughly linear, and that features aren't too collinear.
- **What are its strengths?** Fast, easy to interpret, and gives calibrated probabilities rather than just hard labels.
- **What are its weaknesses?** Struggles once the true decision boundary is meaningfully non-linear.

### 2. Support Vector Machine (Linear Kernel)
- **What representation does it receive?** Scaled numerical feature vectors.
- **What relationship does it try to learn?** The straight hyperplane that maximizes the margin of separation between diabetic and non-diabetic patients.
- **What parameters or structures are learned?** The hyperplane weights, and the support vectors — the handful of data points closest to the boundary that actually determine it.
- **What criterion guides learning?** Maximizing margin while penalizing points on the wrong side (hinge loss), tuned via the regularization parameter C.
- **What assumptions does the model make?** That the classes are close to linearly separable.
- **What are its strengths?** Robust to outliers when properly regularized, and effective in high-dimensional spaces.
- **What are its weaknesses?** Scales poorly to very large datasets, and can't capture curved decision boundaries.

### 3. Support Vector Machine (RBF Kernel)
- **What representation does it receive?** Scaled numerical feature vectors.
- **What relationship does it try to learn?** A non-linear boundary, found by projecting the data into a higher-dimensional space via a Radial Basis Function.
- **What parameters or structures are learned?** Support vectors, their weights, and a gamma parameter controlling how far each support vector's influence reaches.
- **What criterion guides learning?** Maximizing margin — in the transformed space this time.
- **What assumptions does the model make?** That points close together in the transformed space belong to the same class.
- **What are its strengths?** Considerably more capable of modeling complex, non-linear relationships than its linear cousin.
- **What are its weaknesses?** Less interpretable, heavier to train, and genuinely sensitive to hyperparameter choices.

### 4. K-Nearest Neighbors (KNN)
- **What representation does it receive?** Scaled numerical feature vectors.
- **What relationship does it try to learn?** None, globally — it assumes similar inputs have similar outputs based on spatial distance.
- **What parameters or structures are learned?** None up front; KNN is a "lazy learner" that simply memorizes the training data.
- **What criterion guides learning?** Proximity (Euclidean distance) — a new patient's class comes from a majority vote of its *k* closest neighbors.
- **What assumptions does the model make?** That nearby points in feature space share the same label, and that every feature contributes equally to that distance — which is exactly why scaling isn't optional here.
- **What are its strengths?** Simple, handles non-linear boundaries naturally, and needs no real training phase.
- **What are its weaknesses?** Slow at prediction time on large datasets, and sensitive to irrelevant features and the curse of dimensionality.

### 5. Random Forest
- **What representation does it receive?** Unscaled numerical feature vectors — trees don't care about feature magnitude.
- **What relationship does it try to learn?** A complex, non-linear decision structure, built by combining many independent decision trees.
- **What parameters or structures are learned?** An ensemble of trees, each with its own hierarchy of threshold-based splitting rules.
- **What criterion guides learning?** Minimizing impurity (Gini or entropy) at each split, for each individual tree.
- **What assumptions does the model make?** Very few about the data distribution — mainly that averaging many independently-trained, imperfect trees reduces variance.
- **What are its strengths?** Strong accuracy, robust to outliers, and picks up non-linear interactions with no feature engineering.
- **What are its weaknesses?** Individual trees can overfit if left too deep, and the ensemble as a whole is a black box that's hard to interpret directly.

### 6. XGBoost (Extreme Gradient Boosting)
- **What representation does it receive?** Unscaled numerical feature vectors.
- **What relationship does it try to learn?** A non-linear decision boundary, built by sequentially combining trees where each new one targets the errors left by the ones before it.
- **What parameters or structures are learned?** A sequence of trees, with split points and leaf weights tuned via gradient descent.
- **What criterion guides learning?** Minimizing a differentiable loss function (log-loss) via gradient descent over the ensemble.
- **What assumptions does the model make?** That the residual errors from earlier trees are themselves learnable patterns that later trees can correct.
- **What are its strengths?** Often near state-of-the-art on tabular data, handles missing values natively, and is highly optimized.
- **What are its weaknesses?** Easy to overfit without careful tuning, harder to interpret than a single tree, and more expensive to tune well than Random Forest.

## 7. Experimental Design

### Experiment 1: Model Comparison
**Question:** Which of the traditional machine learning models performs best at classifying diabetes when all six are trained and evaluated under identical conditions?

**Setup:** Logistic Regression, SVM (Linear), SVM (RBF), KNN, Random Forest, and XGBoost are all trained on the same 80/20 train-test split, with scaled data going to the distance-based models (LR, SVM, KNN) and unscaled data to the tree models (Random Forest, XGBoost). Each is evaluated with Accuracy, Precision, Recall, and F1-score.

### Experiment 2: Hyperparameter Investigation
**Question:** How do the number of neighbors (*k*) and the weighting scheme (`uniform` vs. `distance`) affect KNN's performance on this dataset?

**Setup:** A 5-fold `GridSearchCV` sweeps *k* $\in$ {3, 5, 7, 9} $\times$ weights $\in$ {uniform, distance}, and rather than only reporting the single best combination, the **full** `cv_results_` grid is inspected to see how cross-validated accuracy actually moves across it.

**Result:** The best configuration turned out to be *k*=9 with `weights='uniform'`, reaching a CV accuracy of 0.7607. Accuracy spread 0.0342 across all 8 combinations tested — enough to say *k* is a genuinely meaningful hyperparameter here rather than something safe to leave at a default. The trend climbs from *k*=3 up to *k*=9 in this range, which lines up with the usual story: small *k* overfits to a few noisy neighbors (high variance), while a larger *k* smooths the decision boundary — trading some bias for lower variance, which suits this dataset's amount of class overlap.

### Experiment 3: Representation / Feature Investigation
**Question:** Does standardizing (scaling) the feature vectors actually improve performance for a distance-based model like KNN?

**Setup:** A KNN classifier (*k*=5) is trained twice — once on the raw, unscaled feature vectors, and once on the standardized ones — and the two test accuracies are compared directly.

**Result:** Unscaled accuracy came out to **67.53%**, scaled accuracy to **75.32%** — a **+7.8 point** jump from standardization alone. That matches expectations: raw features have wildly different ranges (Pedigree Function stays below 1, while Insulin can exceed 100), so unscaled Euclidean distance is effectively dominated by whichever feature happens to have the largest range. Standardizing forces every feature to contribute proportionally, which is exactly why the representation choice discussed in Section 5 isn't a cosmetic detail — it's a real determinant of model quality.

## 8. Results

*Reproduced end-to-end by executing [Report_Notebook.ipynb](Report_Notebook.ipynb)*

| Model | Accuracy | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Baseline (Most Frequent) | 64.94% | 0.000 | 0.000 | 0.000 |
| Logistic Regression | 70.78% | 0.600 | 0.500 | 0.545 |
| SVM (Linear) | 70.78% | 0.605 | 0.481 | 0.536 |
| SVM (RBF) | 69.48% | 0.581 | 0.463 | 0.515 |
| KNN (Best k=9, uniform) | 74.03% | 0.635 | 0.611 | 0.623 |
| **Random Forest** | **76.62%** | **0.696** | **0.593** | **0.640** |
| XGBoost | 74.68% | 0.653 | 0.593 | 0.621 |

The baseline's Precision, Recall, and F1 all land at **0.000** because `DummyClassifier(strategy='most_frequent')` always predicts "Non-Diabetic" — it never identifies a single diabetic patient, yet it still racks up 64.94% accuracy simply because that's the non-diabetic proportion of the dataset. This is precisely why a baseline matters here: accuracy alone would make this useless strategy look "pretty good," while Precision, Recall, and F1 correctly reveal it has zero diagnostic value.

**Appropriate Metrics:** For a medical screening tool like this, **Recall** arguably matters most — high recall keeps False Negatives down, i.e., it minimizes the number of diabetic patients who get told they're healthy. Accuracy still gives a useful overall picture, but **F1-score** (the harmonic mean of precision and recall) is what's used to rank models and automatically pick the final one, since it's far more informative than raw accuracy on a dataset that's roughly 65% non-diabetic and 35% diabetic.

## 9. Model Comparison
Random Forest came out on top across the board — 76.62% accuracy, 0.696 precision, and the best F1-score at 0.640 — and it was selected as the final model. As an ensemble method, it naturally picked up on non-linear relationships and interactions between features like Glucose, BMI, and Age in a way the linear models (Logistic Regression and Linear SVM) couldn't quite match. KNN (k=9) and XGBoost trailed closely behind (F1 = 0.623 and 0.621), which suggests both instance-based and boosted-tree approaches are genuinely competitive on this kind of tabular data once the features are properly represented — imputed and scaled correctly. SVM (RBF) was the weakest of the trained models (F1 = 0.515), barely edging out the baseline; its non-linear kernel simply didn't uncover structure beyond what the simpler linear models already captured here.

## 10. Representation Analysis
- **Why is your feature-vector representation appropriate?** The medical data itself already arrives as independent tabular measurements, so a fixed-length feature vector captures each patient's discrete clinical readings without forcing anything into an unnatural shape.
- **What information does it preserve?** The exact magnitude and statistical distribution of the clinical tests.
- **What information might it lose?** Time. A single feature vector is a snapshot, so it can't show whether a patient's BMI or glucose has been climbing or falling over the past several years.
- **Could the same problem be represented as an image?** Not really — unless the dataset included something inherently visual, like retinal scans for diabetic retinopathy or ultrasound imagery of organs, in which case an image representation would make sense.
- **Could it be represented as a sequence?** Yes — if multiple visits per patient were available, that would open the door to RNNs or LSTMs that model a patient's trajectory over time.
- **Could it be represented as a graph?** Yes, if genetic family trees or social/environmental proximity data were included, to see whether diabetes clusters within families or communities.
- **Could it be represented using learned embeddings?** Only really useful if the input were something unstructured, like raw clinical notes in text form — for the numerical features used here, embeddings would be overkill.
- **What would change if the representation changed?** The model family would have to change too — CNNs for images, RNNs for sequences, GNNs for graphs — generally at the cost of both more computation and less interpretability than the straightforward feature-vector approach used here.

## 11. Intelligent Application
The trained models are wired into a full-stack application (`app/` directory: FastAPI backend + React frontend, with SHAP-based per-feature explanations). A user enters a patient's clinical data once, and the backend `/api/predict` endpoint runs that same patient through all six trained models at once, returning a ranked comparison — effectively Experiment 1 reproduced live — instead of a single black-box answer.

![Dashboard interface](Dashboard.png)
Selecting any row in the ranking opens a detail drawer with that model's prediction, confidence, and a SHAP feature-attribution chart.

![Model Result](Model_Result.png)
![Model Breakdown](Breakdown.png)

To verify the complete input-to-prediction path end to end, three patient profiles covering a range of risk levels were entered directly into the application:

- **Low-risk profile** — a young patient (22) with a normal glucose reading (85 mg/dL), a healthy BMI (26.6), 1 prior pregnancy, and a low pedigree score (0.351). None of the values suggest elevated risk.
![Low Risk Profile](Low_Risk_Predict.png)
![Low Risk Result](Low_Risk_Result.png)
![Low Risk Breakdown](Low_Risk_Breakdown.png)
- **Borderline profile** — a mid-30s patient (34) with mildly elevated glucose (130 mg/dL), a BMI in the overweight range (31.2), 3 prior pregnancies, and a moderate pedigree score (0.523). This is the kind of profile where a screening tool is most useful, since it isn't obviously healthy or obviously high-risk.
![Borderline Profile](Border_Predict.png)
![Borderline Result](Border_Result.png)
![Borderline Breakdown](Border_Breakdown.png)
- **High-risk profile** — an older patient (51) with clearly elevated glucose (183 mg/dL), an obese BMI (39.5), 8 prior pregnancies, and a high pedigree score (1.288) indicating a strong family history. Several risk factors stack together here.
![High Risk Profile](High_Risk_Predict.png)
![High Risk Result](High_Risk_Result.png)
![High Risk Breakdown](High_Risk_Breakdown.png)

The predicted diabetes probability should rise in step with these accumulating risk factors — a useful sanity check that the pipeline behaves the way the clinical reasoning behind it would predict.

## 12. Limitations
- **Data Bias:** The dataset is limited to females of Pima Indian heritage, so the model is unlikely to generalize well to male patients or to populations with different genetic backgrounds and dietary patterns.
- **Temporal Blindness:** Because it's a point-in-time assessment, the model has no way to factor in a patient's trajectory — say, recent rapid weight loss or a sudden change in glucose control.
- **False Negatives:** The model doesn't achieve 100% recall, so it will still miss some diabetic patients — a real and significant risk in a healthcare context.

## 13. Reflection
- **What information does your system receive?** Eight numerical clinical and demographic measurements per patient — Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, and Age. Nothing about a patient's history, symptoms, or context beyond those eight numbers ever reaches the model.
- **What is the internal representation?** Those eight raw readings get cleaned (impossible zeros imputed with a training-only median) and standardized into a single scaled, 8-dimensional feature vector — that's the entire "world" the model ever sees. There is no notion of the patient as a person, only as a point in an 8-dimensional space.
- **What does the model learn from examples?** By comparing thousands of these feature vectors against their known outcomes, the model learns statistical boundaries — hyperplanes for the linear models, distance neighborhoods for KNN, sequences of threshold splits for the tree ensembles — that separate diabetic from non-diabetic profiles. It is, in effect, learning a compressed summary of "what combinations of glucose, BMI, age, and the rest tend to co-occur with a diabetes diagnosis in this population," not a causal or biological explanation of why.
- **What prediction or decision does it make?** A discrete binary decision: 0 (non-diabetic) or 1 (diabetic), optionally alongside a probability score that expresses how confident the model is.
- **Why can it handle an unseen input?** Because it never memorized specific patient rows — it generalized a rule, like "high BMI combined with high glucose tends to raise risk," that extends naturally to new combinations of the same eight features, even ones no training patient exhibited exactly.
- **What part of the system can reasonably be called "intelligent"?** Mainly the training phase: the process by which an algorithm autonomously adjusts its internal parameters — weights, splits, support vectors — to reduce error on the examples it's given, without a human hand-writing the diagnostic rules. Choosing which models to try, tuning their hyperparameters, and deciding which metric should govern final-model selection also involved a kind of designed intelligence, but that part is human, not the model's.
- **What limitations prevent it from being a more capable intelligent system?** It has no contextual awareness — it can't ask a follow-up question the way a doctor would, it knows nothing about a patient's actual family history beyond a single pedigree-function number, it can't factor in symptoms, medications, or recent trends, and on its own it can't explain its reasoning in a way a clinician would find intuitive (which is why a separate tool like SHAP had to be bolted on to get any explanation at all). Fundamentally, it is pattern recognition over a fixed set of numbers, not anything resembling clinical reasoning — which is exactly why it's positioned as a screening aid rather than a diagnostic authority.

## 14. Conclusion
This project set out to build an intelligent system for predicting diabetes from routine clinical measurements, and it delivers on that goal end to end — from raw data, through representation and preprocessing, to six trained models and a working application. Along the way, a train/test leakage issue in the imputation step was caught and fixed (the median is now computed strictly from the training split), and full Precision/Recall/F1 reporting was added for every model rather than relying on accuracy alone. Random Forest came out ahead on held-out data (76.62% accuracy, 0.640 F1) and was selected automatically as the final model.

The three controlled experiments reinforced a few things worth remembering: every trained model clearly beats the zero-F1 baseline, KNN's accuracy is genuinely sensitive to the choice of *k* (a 0.034 spread across the grid), and standardizing features lifts KNN's accuracy by 7.8 points — a reminder that representation choices, not just model choice, materially shape the outcome. The system shows real value as a preliminary screening tool, verified end-to-end with three sample patients, but it should be deployed with its limitations in plain view: it was trained on a narrow demographic (Pima Indian females), it has no sense of time, and the entire pipeline rests on just 768 records.
