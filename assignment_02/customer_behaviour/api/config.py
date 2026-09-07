"""Static configuration for the customer-behaviour API (Sephora skincare reviews).

Filesystem paths and the small pieces of metadata the web / mobile clients need to
render their form. Nothing here is fitted or learned — the fitted objects live in
``model/model_pipeline.joblib`` and the contract in ``model/input_schema.json``.

Task: predict whether the reviewer recommends the product (``is_recommended``) from
their skin profile + the product + the review text.  Model: Logistic Regression on
tabular + TF-IDF(text)  (notebook §22).
"""
from __future__ import annotations

import json
from pathlib import Path

API_DIR = Path(__file__).resolve().parent          # customer_behaviour/api
APP_DIR = API_DIR.parent                             # customer_behaviour
MODEL_DIR = APP_DIR / "model"
DATA_DIR = APP_DIR / "data" / "sephora"

MODEL_PIPELINE_PATH = MODEL_DIR / "model_pipeline.joblib"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.joblib"
MODEL_MEANS_PATH = MODEL_DIR / "feature_means.joblib"
INPUT_SCHEMA_PATH = MODEL_DIR / "input_schema.json"

# decision threshold on P(recommend); below it -> "not recommend" (the class we act on)
DECISION_THRESHOLD = 0.50

# share of reviews that were is_recommended == 1 in the cleaned training data — shown
# as context next to the model's own (class-balanced) reference point.
DATASET_BASE_RATE = 0.846

_SNAPSHOT = "2023-03-22"     # notebook build_features() reference date (max review date + 1)

# ------------------------------------------------------------------ schema-derived
_SCHEMA = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))

RAW_INPUT_FIELDS: list[str] = _SCHEMA["raw_input_fields"]
TABULAR_FEATURE_ORDER: list[str] = _SCHEMA["tabular_feature_order"]
TEXT_COLUMN: str = _SCHEMA["text_col"]
CHOSEN_MODEL: str = _SCHEMA.get("model", "LogisticRegression")
REPRESENTATION: str = _SCHEMA.get("representation", "tabular + TF-IDF(text)")
RANDOM_SEED: int = _SCHEMA["random_seed"]
SKLEARN_VERSION: str = _SCHEMA["sklearn_version"]
TARGET_DESC: str = _SCHEMA["target"]
FRAMING_NOTE: str = _SCHEMA.get("framing", "")

# ------------------------------------------------------------------ vocab (from data)
SKIN_TYPES = ["dry", "combination", "normal", "oily"]
SKIN_TONES = ["porcelain", "fair", "fairLight", "light", "lightMedium", "medium",
              "mediumTan", "tan", "olive", "deep", "rich", "dark"]
EYE_COLORS = ["brown", "blue", "hazel", "green", "gray"]
HAIR_COLORS = ["black", "brown", "brunette", "blonde", "auburn", "red", "gray"]
CATEGORIES = ["Cleansers", "Eye Care", "High Tech Tools", "Lip Balms & Treatments",
              "Masks", "Mini Size", "Moisturizers", "Self Tanners", "Sunscreen",
              "Treatments", "Value & Gift Sets", "Wellness"]
BRANDS = [
    "Peter Thomas Roth", "Dr. Jart+", "SEPHORA COLLECTION", "Supergoop!", "Skinfix",
    "Dermalogica", "KORA Organics", "WASO", "St. Tropez", "The INKEY List", "Murad",
    "Kiehl's Since 1851", "Fenty Skin", "Caudalie", "OLEHENRIKSEN", "First Aid Beauty",
    "Farmacy", "Summer Fridays", "Shiseido", "Drunk Elephant", "Youth To The People",
    "REN Clean Skincare", "fresh", "TULA Skincare", "Sunday Riley", "JLo Beauty",
    "Biossance", "Moon Juice", "La Mer", "Benefit Cosmetics", "The Ordinary", "Wishful",
    "IT Cosmetics", "Paula's Choice", "CLINIQUE", "Dior", "Herbivore", "Glow Recipe",
    "Isle of Paradise", "Origins", "KORRES", "Augustinus Bader", "Sulwhasoo", "Josie Maran",
]

# fields the client form does not ask for — filled server-side (client value still wins).
# ingredients/highlights are omitted so build_features emits NaN and the pipeline's
# median imputer fills them exactly as fitted; the edition flags default to 0; the
# engagement vote counts default to 0 (a brand-new review); submission_time -> NaN ->
# imputed median review age.
FIXED_INPUTS = {
    "limited_edition": 0, "new": 0, "online_only": 0, "sephora_exclusive": 0,
    "total_feedback_count": 0, "total_pos_feedback_count": 0, "total_neg_feedback_count": 0,
}

# one-click example review texts the client can offer as fills for the review box
REVIEW_EXAMPLES = [
    ["Best Pimple Patches",
     "These are the only pimple patches I've used that actually work on hormonal acne. Thin, invisible under makeup, and they flatten a spot overnight."],
    ["Holy grail moisturizer",
     "Completely fixed my winter dryness. Absorbs fast, no scent, layers well under sunscreen and makeup. On my third jar."],
    ["Broke me out",
     "Wanted to love this but it broke me out within a week and felt greasy all day. The fragrance is also really strong. Returned it."],
    ["Just okay for the price",
     "It's fine — hydrating enough, nothing special. For this price I expected more. Wouldn't repurchase, there are cheaper options that do the same."],
    ["Too harsh for sensitive skin",
     "Stung on application and left my cheeks red and flaky for days. Might work for tougher skin but not for me."],
]

# form metadata — the client renders its fields from this list.
#   type:  "number" | "choice" | "text" | "textarea"
#   section = form group heading
FORM_FIELDS = [
    # ------------------------- Your skin profile -------------------------
    {"field": "skin_type", "type": "choice", "label": "Skin type",
     "options": SKIN_TYPES, "required": False, "section": "Your skin profile",
     "note": "Main structured signal — a product for dry skin often disappoints oily reviewers."},
    {"field": "skin_tone", "type": "choice", "label": "Skin tone",
     "options": SKIN_TONES, "required": False, "section": "Your skin profile",
     "note": "Sephora's scale, light → deep."},
    {"field": "eye_color", "type": "choice", "label": "Eye colour",
     "options": EYE_COLORS, "required": False, "section": "Your skin profile",
     "note": "Reviewer profile; weak signal alone."},
    {"field": "hair_color", "type": "choice", "label": "Hair colour",
     "options": HAIR_COLORS, "required": False, "section": "Your skin profile",
     "note": "Reviewer profile; weak signal alone."},

    # ------------------------- The product -------------------------
    {"field": "secondary_category", "type": "choice", "label": "Product category",
     "options": CATEGORIES, "required": False, "section": "The product",
     "note": "Peels/treatments and self-tanners get fewer recommendations than moisturisers."},
    {"field": "brand_name", "type": "choice", "label": "Brand",
     "options": BRANDS, "required": False, "section": "The product",
     "note": "Recommend rate ranges ~0.56–0.97 across brands."},
    {"field": "price_usd", "type": "number", "label": "Price (US$)",
     "min": 0, "required": True, "section": "The product",
     "note": "US dollars; dataset median ~$42."},
    {"field": "loves_count", "type": "number", "label": "“Loves” on the product page",
     "min": 0, "required": False, "section": "The product",
     "note": "Shoppers who saved it — a popularity proxy."},
    {"field": "reviews", "type": "number", "label": "Total reviews on the product",
     "min": 0, "required": False, "section": "The product",
     "note": "Reviews already on the product page."},

    # ------------------------- The review -------------------------
    {"field": "review_title", "type": "text", "label": "Review title",
     "required": False, "section": "The review",
     "note": "Optional — ~31% of reviews have none."},
    {"field": "review_text", "type": "textarea", "label": "Review text",
     "required": True, "section": "The review", "examples": REVIEW_EXAMPLES,
     "note": "What the model leans on most. Written with the recommend tick, so it "
             "strongly signals the outcome (notebook §14a)."},
]

FORM_SECTIONS = ["Your skin profile", "The product", "The review"]
