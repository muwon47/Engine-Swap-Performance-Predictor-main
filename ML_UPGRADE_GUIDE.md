# 🚀 Hybrid Machine Learning Upgrade Guide

This guide details the step-by-step process to upgrade your current rule-based engine swap predictor into a **Hybrid Machine Learning Architecture**. 

A hybrid approach leverages the best of both worlds:
1. **Existing Formulae**: Continues to use your physics-based logic for deterministic factors (e.g., compatibility scoring, gear ratio math, weight distribution).
2. **Advanced ML Models**: Uses algorithms like XGBoost and Random Forest to predict complex, non-linear performance metrics (Horsepower, Torque, 0-60 times) based on training data.

---

## Phase 1: Environment & Data Preparation

Currently, your project uses the Python Standard Library. To build an advanced ML pipeline, you will need industry-standard data science libraries.

### Step 1: Install Dependencies
Open your terminal and install the required packages:
```bash
pip install pandas numpy scikit-learn xgboost joblib
```

### Step 2: Export the Training Dataset
Your `src/dataset.py` currently generates synthetic data on the fly. You need to dump a large batch of this data into a CSV file so your ML model has consistent data to train on.

Create a new file `src/export_data.py`:
```python
import pandas as pd
from src.dataset import build_training_records

# Generate a large dataset (e.g., 5000+ records)
records = build_training_records(seed=42)
df = pd.DataFrame(records)

# Save to CSV for model training
df.to_csv("data/training_data.csv", index=False)
print("Dataset exported to data/training_data.csv")
```

---

## Phase 2: Building and Training the Advanced ML Model

### Step 3: Create the Training Script
We will train an **XGBoost Regressor** (which handles complex, non-linear relationships much better than the current Ridge implementation).

Create a new file `src/train_model.py`:
```python
import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# 1. Load Data
df = pd.read_csv("data/training_data.csv")

# 2. Define Features and Targets
FEATURES = [
    "engine_displacement_l", "cylinders", "compression_ratio", "engine_weight_kg",
    "base_hp", "base_torque_nm", "forced_induction", "engine_family_encoding",
    "recipient_weight_kg", "drivetrain_match", "mount_complexity", "gear_ratio",
    "cooling_capacity_index", "suspension_index", "tire_grip_index", 
    "drag_coefficient", "swap_difficulty_index", "tune_level"
]
TARGETS = ["post_swap_hp", "post_swap_torque_nm", "zero_to_sixty_s"]

X = df[FEATURES]
y = df[TARGETS]

# 3. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Build the Pipeline
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("xgb", MultiOutputRegressor(XGBRegressor(
        n_estimators=200, 
        learning_rate=0.05, 
        max_depth=5
    )))
])

# 5. Train the Model
print("Training advanced XGBoost model...")
pipeline.fit(X_train, y_train)

# 6. Evaluate
score = pipeline.score(X_test, y_test)
print(f"Model trained! Test R^2 Score: {score:.3f}")

# 7. Save Model to Disk
joblib.dump(pipeline, "data/hybrid_xgb_model.joblib")
print("Model saved to data/hybrid_xgb_model.joblib")
```

Run this script to generate your `.joblib` model artifact.

---

## Phase 3: Implementing the Hybrid Approach in Backend

We will modify `src/predictor.py` to become a "Hybrid" service. It will still use your exact existing code for `_compatibility()` and `_tuning_tips()`, but it will use the new XGBoost model for `predict()`.

### Step 4: Update `src/predictor.py`
Import `joblib` and load the saved model into the `EngineSwapPredictor` class.

```python
import joblib
import pandas as pd

class EngineSwapPredictor:
    def __init__(self) -> None:
        # Load the advanced ML model
        try:
            self.ml_model = joblib.load("data/hybrid_xgb_model.joblib")
            self.is_hybrid = True
        except FileNotFoundError:
            # Fallback to the old linear model if file doesn't exist
            self.ml_model = None
            self.is_hybrid = False
            
        # ... keep existing __init__ logic for fallback
```

### Step 5: Route Predictions through the ML Model
Modify the `predict()` function. We calculate features exactly like before using your formulas, but we pass them to the ML model for the final numbers.

```python
    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        engine, chassis, features = self._features_from_payload(payload)
        
        # 1. Use existing formulae for compatibility (The Hybrid Aspect)
        compatibility = self._compatibility(features)
        
        # 2. Use ML Model for Performance Stats
        if self.is_hybrid:
            # Convert features dict to Pandas DataFrame for scikit-learn
            feature_df = pd.DataFrame([features], columns=FEATURES)
            raw_prediction = self.ml_model.predict(feature_df)[0]
            
            predictions = {
                "horsepower": round(raw_prediction[0], 1),
                "torque_nm": round(raw_prediction[1], 1),
                "zero_to_sixty_s": round(raw_prediction[2], 2),
            }
        else:
            # Fallback to old logic
            raw_prediction = self.model.predict_one(features)
            predictions = {
                "horsepower": round(raw_prediction["post_swap_hp"], 1),
                # ...
            }

        # 3. Combine and return
        return {
            "engine": {"code": engine["code"], "name": engine["name"]},
            "chassis": {"code": chassis["code"], "name": chassis["name"]},
            "predictions": predictions,
            "compatibility": compatibility,  # Formula-based
            "tuning_tips": self._tuning_tips(features, predictions, compatibility["score"]), # Rule-based
            # ...
        }
```

---

## Phase 4: Reflecting Changes on the Website

The beautiful thing about your current architecture is that the frontend (`app.js`) is completely decoupled from the ML engine. 

As long as your `/api/predict` route returns JSON in the same format (`predictions: { horsepower, torque_nm, zero_to_sixty_s }`), **the frontend will automatically render the new Machine Learning outputs.**

### Step 6: (Optional) Show a "Hybrid ML Active" Badge
If you want users to know they are using the advanced model, you can expose the `is_hybrid` flag in `/api/meta`.

1. In `predictor.py`, update `metadata()`:
   ```python
   def metadata(self) -> dict:
       return {
           # ... existing keys
           "hybrid_ml_active": getattr(self, 'is_hybrid', False)
       }
   ```
2. In `static/app.js` inside the `renderMeta()` function, add logic to show a badge:
   ```javascript
   if (meta.hybrid_ml_active) {
     const title = document.querySelector("h1");
     title.innerHTML += ` <span style="font-size:0.4em; background:var(--accent-primary); padding:4px 8px; border-radius:8px; vertical-align:middle;">XGBoost Active</span>`;
   }
   ```

### Step 7: Restart and Test
1. Run `python src/export_data.py`
2. Run `python src/train_model.py`
3. Run `python run.py`

When you move the "Tune Level" slider on the UI, the frontend will call the API, the backend will process the payload through the XGBoost Pipeline, merge it with your formula-based compatibility scores, and stream the results directly back to the DOM without requiring any HTML rewrites.
