"""Static configuration for the diabetes screening API.

Feature lists, question metadata (the client renders the form from this), value
ranges, default decision thresholds, and filesystem paths. Nothing here is fitted or
learned — see APP_DESIGN.md sections 1.3, 3, 7.2.
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------- paths
API_DIR = Path(__file__).resolve().parent          # diabetes/api
APP_DIR = API_DIR.parent                            # diabetes
MODEL_DIR = APP_DIR / "model"
DATA_DIR = APP_DIR / "data"
ARTIFACT_DIR = API_DIR / "artifacts"               # regenerable, git-ignorable
RUNTIME_DIR = API_DIR / "runtime"                  # mutable state, git-ignored

MODEL_PIPELINE_PATH = MODEL_DIR / "model_pipeline.joblib"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.joblib"
INPUT_SCHEMA_PATH = MODEL_DIR / "input_schema.json"
HOLDOUT_SCORES_PATH = MODEL_DIR / "holdout_scores.joblib"

NEIGHBOR_INDEX_PATH = ARTIFACT_DIR / "neighbor_index.joblib"
SHAP_BACKGROUND_PATH = ARTIFACT_DIR / "shap_background.joblib"
BMI_TABLE_PATH = ARTIFACT_DIR / "bmi_by_age_sex.joblib"

THRESHOLDS_PATH = RUNTIME_DIR / "thresholds.json"
REQUESTS_DB_PATH = RUNTIME_DIR / "requests.sqlite"

RAW_CSV_PATH = DATA_DIR / "diabetes_012_health_indicators_BRFSS2015.csv"

ADMIN_KEY = os.environ.get("DIABETES_ADMIN_KEY", "change-me")

# ------------------------------------------------------------------- feature groups
BINARY_FEATURES = [
    "HighBP", "HighChol", "CholCheck", "Smoker", "Stroke", "HeartDiseaseorAttack",
    "PhysActivity", "Fruits", "Veggies", "HvyAlcoholConsump", "AnyHealthcare",
    "NoDocbcCost", "DiffWalk", "Sex",
]
ORDINAL_FEATURES = ["GenHlth", "Age", "Education", "Income"]
CONTINUOUS_FEATURES = ["BMI", "MentHlth", "PhysHlth"]
RAW_FEATURES = BINARY_FEATURES + ORDINAL_FEATURES + CONTINUOUS_FEATURES          # 21
ENGINEERED_FEATURES = ["TotalUnhealthyDays", "CardioRisk"]
MODEL_FEATURES = RAW_FEATURES + ENGINEERED_FEATURES                             # 23

REQUIRED_FIELDS = ["Age", "Sex"]                    # everything else may be null

# valid integer ranges for the coded fields (schema range-checks against these)
VALUE_RANGES = {
    **{f: (0, 1) for f in BINARY_FEATURES},
    "GenHlth": (1, 5),
    "Age": (1, 13),
    "Education": (1, 6),
    "Income": (1, 8),
    "MentHlth": (0, 30),
    "PhysHlth": (0, 30),
}
# BMI is the only unbounded feature; clamp to the range actually seen in training
BMI_MIN, BMI_MAX = 12.0, 98.0

# modifiable factors for the what-if / counterfactual feature: (feature -> healthy value)
MODIFIABLE_BINARY = {
    "Smoker": 0,
    "HvyAlcoholConsump": 0,
    "PhysActivity": 1,
    "Fruits": 1,
    "Veggies": 1,
}
MODIFIABLE_CONTINUOUS = ["BMI"]                     # swept, not flipped

# ------------------------------------------------------------------ default bands
# p >= HIGH_CUT -> "High"; MODERATE_CUT <= p < HIGH_CUT -> "Moderate"; else "Low"
DEFAULT_MODERATE_CUT = 0.30
DEFAULT_HIGH_CUT = 0.50
COMPLETENESS_WARN_BELOW = 0.80

# --------------------------------------------------------- questionnaire metadata
# type: "yesno" (0/1), "choice" (explicit options), "number" (free numeric)
# The client renders the form from this list; the report can quote it verbatim.
QUESTIONS = [
    # --- About you ---
    {"section": "About you", "field": "Age", "type": "choice", "required": True,
     "label": "Age group",
     "options": [[1, "18–24"], [2, "25–29"], [3, "30–34"], [4, "35–39"], [5, "40–44"],
                 [6, "45–49"], [7, "50–54"], [8, "55–59"], [9, "60–64"], [10, "65–69"],
                 [11, "70–74"], [12, "75–79"], [13, "80 or older"]],
     "modifiable": False},
    {"section": "About you", "field": "Sex", "type": "choice", "required": True,
     "label": "Sex", "options": [[0, "Female"], [1, "Male"]], "modifiable": False},
    {"section": "About you", "field": "Education", "type": "choice", "required": False,
     "label": "Highest level of school completed",
     "options": [[1, "Never attended / kindergarten only"], [2, "Grades 1–8"],
                 [3, "Grades 9–11"], [4, "High-school graduate / GED"],
                 [5, "Some college or technical school"], [6, "College graduate (4+ years)"]],
     "modifiable": False},
    {"section": "About you", "field": "Income", "type": "choice", "required": False,
     "label": "Annual household income",
     "options": [[1, "Less than $10,000"], [2, "$10,000–$15,000"], [3, "$15,000–$20,000"],
                 [4, "$20,000–$25,000"], [5, "$25,000–$35,000"], [6, "$35,000–$50,000"],
                 [7, "$50,000–$75,000"], [8, "$75,000 or more"]],
     "modifiable": False},

    # --- Body (height + weight -> BMI) ---
    {"section": "Body", "field": "height_cm", "type": "number", "required": False,
     "label": "Height (cm)", "min": 120, "max": 230, "modifiable": False,
     "note": "Used to compute BMI. Leave blank if unknown."},
    {"section": "Body", "field": "weight_kg", "type": "number", "required": False,
     "label": "Weight (kg)", "min": 30, "max": 320, "modifiable": True,
     "note": "Used to compute BMI."},
    {"section": "Body", "field": "BMI", "type": "number", "required": False,
     "label": "BMI (if already known)", "min": 12, "max": 98, "modifiable": True,
     "note": "Optional — leave blank to compute from height and weight."},

    # --- Conditions you have been told you have ---
    {"section": "Conditions", "field": "HighBP", "type": "yesno", "required": False,
     "label": "Have you been told you have high blood pressure?", "modifiable": False},
    {"section": "Conditions", "field": "HighChol", "type": "yesno", "required": False,
     "label": "Have you been told your blood cholesterol is high?", "modifiable": False},
    {"section": "Conditions", "field": "Stroke", "type": "yesno", "required": False,
     "label": "Have you ever been told you had a stroke?", "modifiable": False},
    {"section": "Conditions", "field": "HeartDiseaseorAttack", "type": "yesno", "required": False,
     "label": "Have you ever had coronary heart disease or a heart attack?", "modifiable": False},
    {"section": "Conditions", "field": "DiffWalk", "type": "yesno", "required": False,
     "label": "Do you have serious difficulty walking or climbing stairs?", "modifiable": False},

    # --- Checks & access to care ---
    {"section": "Checks & care", "field": "CholCheck", "type": "yesno", "required": False,
     "label": "Have you had a cholesterol check in the past 5 years?", "modifiable": False},
    {"section": "Checks & care", "field": "AnyHealthcare", "type": "yesno", "required": False,
     "label": "Do you have any kind of health-care coverage?", "modifiable": False},
    {"section": "Checks & care", "field": "NoDocbcCost", "type": "yesno", "required": False,
     "label": "In the past year, did you need to see a doctor but could not because of cost?",
     "modifiable": False},

    # --- Lifestyle ---
    {"section": "Lifestyle", "field": "Smoker", "type": "yesno", "required": False,
     "label": "Have you smoked at least 100 cigarettes in your life?", "modifiable": True},
    {"section": "Lifestyle", "field": "HvyAlcoholConsump", "type": "yesno", "required": False,
     "label": "Are you a heavy drinker (≥14 drinks/week for men, ≥7 for women)?",
     "modifiable": True},
    {"section": "Lifestyle", "field": "PhysActivity", "type": "yesno", "required": False,
     "label": "Any physical activity in the past 30 days (outside your job)?", "modifiable": True},
    {"section": "Lifestyle", "field": "Fruits", "type": "yesno", "required": False,
     "label": "Do you eat fruit at least once per day?", "modifiable": True},
    {"section": "Lifestyle", "field": "Veggies", "type": "yesno", "required": False,
     "label": "Do you eat vegetables at least once per day?", "modifiable": True},

    # --- How you have felt in the last 30 days ---
    {"section": "How you feel", "field": "GenHlth", "type": "choice", "required": False,
     "label": "In general, would you say your health is:",
     "options": [[1, "Excellent"], [2, "Very good"], [3, "Good"], [4, "Fair"], [5, "Poor"]],
     "modifiable": False},
    {"section": "How you feel", "field": "MentHlth", "type": "number", "required": False,
     "label": "Days in the last 30 your mental health was not good", "min": 0, "max": 30,
     "modifiable": False},
    {"section": "How you feel", "field": "PhysHlth", "type": "number", "required": False,
     "label": "Days in the last 30 your physical health was not good", "min": 0, "max": 30,
     "modifiable": False},
]

# plain-language labels used by the explanation panel (SHAP factor bars)
FEATURE_LABELS = {
    "HighBP": "High blood pressure", "HighChol": "High cholesterol",
    "CholCheck": "Recent cholesterol check", "Smoker": "Smoking history",
    "Stroke": "Stroke history", "HeartDiseaseorAttack": "Heart disease / attack history",
    "PhysActivity": "Physically active", "Fruits": "Eats fruit daily",
    "Veggies": "Eats vegetables daily", "HvyAlcoholConsump": "Heavy alcohol use",
    "AnyHealthcare": "Has health-care coverage", "NoDocbcCost": "Skipped doctor due to cost",
    "DiffWalk": "Difficulty walking", "Sex": "Sex", "GenHlth": "Self-rated general health",
    "Age": "Age group", "Education": "Education level", "Income": "Income level",
    "BMI": "Body-mass index", "MentHlth": "Poor-mental-health days",
    "PhysHlth": "Poor-physical-health days",
    "TotalUnhealthyDays": "Total poor-health days", "CardioRisk": "Cardiovascular history",
}
