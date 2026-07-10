CAPABILITIES = [
    {
        "number": "01",
        "title": "Multi-Output Regression",
        "description": "Predicts horsepower, torque, and 0-60 mph from one unified model pipeline.",
    },
    {
        "number": "02",
        "title": "Compatibility Scoring",
        "description": "Scores engine-chassis compatibility from weight distribution, mount geometry, drivetrain match, and cooling readiness.",
    },
    {
        "number": "03",
        "title": "Interactive Input Interface",
        "description": "Accepts donor engine and recipient chassis specs, then returns estimates and confidence bands.",
    },
    {
        "number": "04",
        "title": "Feature Importance Ranking",
        "description": "Ranks the features that most influence the predicted swap outcome.",
    },
    {
        "number": "05",
        "title": "Comparative Analysis",
        "description": "Compares multiple engine candidates side by side and ranks predicted performance uplift.",
    },
    {
        "number": "06",
        "title": "Data-Driven Tuning Tips",
        "description": "Suggests practical tuning actions for turbo sizing, gearing, cooling, mounts, and suspension.",
    },
]


DATA_SOURCES = [
    {
        "name": "EPA Fuel Economy Dataset",
        "source": "fueleconomy.gov / Kaggle",
        "records": "~42,000 records",
        "key_features": "Engine displacement, cylinders, fuel type, city/highway MPG, CO2 output, vehicle class",
    },
    {
        "name": "Car Features & MSRP Dataset",
        "source": "Kaggle (Edmunds/Twitter)",
        "records": "~11,900 records",
        "key_features": "Make, model, year, engine HP, cylinders, transmission, driven wheels, market category",
    },
    {
        "name": "Vehicle Dynamics & Specs DB",
        "source": "Motor Trend / Auto123",
        "records": "~6,000+ records",
        "key_features": "0-60 mph, quarter mile, curb/GVWR weight, wheelbase, drag coefficient, torque curves",
    },
    {
        "name": "Engine Swap Community Logs",
        "source": "RacingJunk / LS1Tech forums",
        "records": "~3,500 swap records",
        "key_features": "Donor engine code, recipient chassis, reported post-swap HP/TQ, mods applied, swap difficulty",
    },
]


FEATURE_ENGINEERING = [
    "power_to_weight_ratio",
    "torque_per_litre",
    "displacement_per_cylinder",
    "engine_family_encoding",
    "swap_difficulty_index",
]


ALGORITHMS = [
    {
        "name": "Multiple Linear Regression",
        "tag": "Baseline",
        "slide_r2": 0.81,
        "description": "Establishes linear relationships between engine specs and performance.",
    },
    {
        "name": "Polynomial Regression",
        "tag": "Non-linear",
        "slide_r2": 0.86,
        "description": "Captures non-linear displacement-to-power curves using degree-2 features.",
    },
    {
        "name": "Ridge / Lasso Regression",
        "tag": "Regularized",
        "slide_r2": 0.87,
        "description": "Regularizes the feature space to reduce multicollinearity.",
    },
    {
        "name": "Random Forest Regressor",
        "tag": "Ensemble",
        "slide_r2": 0.93,
        "description": "Production option for mixed features and robust missing-data handling.",
    },
    {
        "name": "Gradient Boosting (XGBoost)",
        "tag": "Best Model",
        "slide_r2": 0.96,
        "description": "Production option for sequential boosted trees and high overall accuracy.",
    },
    {
        "name": "SVR (RBF Kernel)",
        "tag": "Kernel Method",
        "slide_r2": 0.89,
        "description": "Production option for smaller, non-linear datasets.",
    },
]


TECH_STACK = {
    "Languages": [
        "Python 3.10+",
        "SQL",
        "JavaScript",
        "Bash / Shell",
    ],
    "ML & Data Science Libraries": [
        "scikit-learn",
        "XGBoost",
        "Pandas & NumPy",
        "SHAP",
        "Matplotlib / Seaborn",
    ],
    "Web Framework & Infrastructure": [
        "FastAPI",
        "React.js",
        "MongoDB",
        "Docker",
        "Jupyter / VS Code",
    ],
}
