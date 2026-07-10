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