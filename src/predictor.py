from __future__ import annotations
import pandas as pd
from statistics import mean
from typing import Any
import joblib
from src.catalog import ALGORITHMS, CAPABILITIES, DATA_SOURCES, FEATURE_ENGINEERING, TECH_STACK
from src.dataset import BASE_ENGINES, CHASSIS, build_feature_record, build_training_records, clamp, get_chassis, get_engine
from src.linear_model import RidgeRegressor


FEATURES = [
    "engine_displacement_l",
    "cylinders",
    "compression_ratio",
    "engine_weight_kg",
    "base_hp",
    "base_torque_nm",
    "forced_induction",
    "engine_family_encoding",
    "recipient_weight_kg",
    "drivetrain_match",
    "mount_complexity",
    "gear_ratio",
    "cooling_capacity_index",
    "suspension_index",
    "tire_grip_index",
    "drag_coefficient",
    "swap_difficulty_index",
    "tune_level",
]

TARGETS = ["post_swap_hp", "post_swap_torque_nm", "zero_to_sixty_s"]


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
        self.records = build_training_records()
        self.train_rows = [row for index, row in enumerate(self.records) if index % 5 != 0]
        self.test_rows = [row for index, row in enumerate(self.records) if index % 5 == 0]
        self.models = {
            "Multiple Linear Regression": RidgeRegressor(alpha=0.0, degree=1).fit(self.train_rows, FEATURES, TARGETS),
            "Ridge / Lasso Regression": RidgeRegressor(alpha=1.2, degree=1).fit(self.train_rows, FEATURES, TARGETS),
            "Polynomial Regression": RidgeRegressor(alpha=2.0, degree=2).fit(self.train_rows, FEATURES, TARGETS),
        }
        self.model = self.models["Polynomial Regression"]
        self.metrics = self._build_metrics()

    def metadata(self) -> dict[str, Any]:
        return {
            "capabilities": CAPABILITIES,
            "data_sources": DATA_SOURCES,
            "feature_engineering": FEATURE_ENGINEERING,
            "algorithms": self.metrics,
            "tech_stack": TECH_STACK,
            "engines": BASE_ENGINES,
            "chassis": CHASSIS,
            "training_rows": len(self.records),
            "demo_note": "This mini project uses deterministic synthetic, source-inspired records so it runs without external datasets.",
            "hybrid_ml_active": self.is_hybrid,
        }

    def sample_request(self) -> dict[str, Any]:
        return {
            "engine_code": "K24A",
            "chassis_code": "MX5_NA",
            "tune_level": 0.65,
            "cooling_capacity_index": 0.74,
            "tire_grip_index": 0.78,
            "suspension_index": 0.72,
            "gear_ratio": 4.30,
        }

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        engine, chassis, features = self._features_from_payload(payload)
        compatibility = self._compatibility(features)
        
        if self.is_hybrid:
            # Filter features to only include the 18 used in ML training
            ml_features = {name: features[name] for name in FEATURES}
            # Convert features dict to Pandas DataFrame for scikit-learn
            feature_df = pd.DataFrame([ml_features], columns=FEATURES)
            raw_prediction = self.ml_model.predict(feature_df)[0]
            
            predictions = {
                "horsepower": round(float(raw_prediction[0]), 1),
                "torque_nm": round(float(raw_prediction[1]), 1),
                "zero_to_sixty_s": round(float(raw_prediction[2]), 2),
            }
        else:
            # Fallback to old logic
            raw_prediction = self.model.predict_one(features)
            predictions = {
                "horsepower": round(clamp(raw_prediction["post_swap_hp"], 95, 760), 1),
                "torque_nm": round(clamp(raw_prediction["post_swap_torque_nm"], 120, 900), 1),
                "zero_to_sixty_s": round(clamp(raw_prediction["zero_to_sixty_s"], 2.6, 10.5), 2),
            }

        return {
            "engine": {"code": engine["code"], "name": engine["name"]},
            "chassis": {"code": chassis["code"], "name": chassis["name"]},
            "predictions": predictions,
            "confidence_intervals": self._confidence_interval(predictions),
            "compatibility": compatibility,
            "feature_importance": self.model.feature_importance(),
            "tuning_tips": self._tuning_tips(features, predictions, compatibility["score"]),
            "engineered_features": {name: round(features[name], 4) for name in FEATURES},
        }

    def compare(self, payload: dict[str, Any]) -> dict[str, Any]:
        chassis_code = payload.get("chassis_code", "MX5_NA")
        candidate_codes = payload.get("candidate_engines") or [engine["code"] for engine in BASE_ENGINES]
        rows = []
        for engine_code in candidate_codes:
            candidate_payload = dict(payload)
            candidate_payload["engine_code"] = engine_code
            result = self.predict(candidate_payload)
            uplift = result["predictions"]["horsepower"] - get_chassis(chassis_code)["stock_hp"]
            rows.append(
                {
                    "engine": result["engine"],
                    "chassis": result["chassis"],
                    "predictions": result["predictions"],
                    "compatibility_score": result["compatibility"]["score"],
                    "performance_uplift_hp": round(uplift, 1),
                    "rank_score": round(
                        uplift * 0.62
                        + result["compatibility"]["score"] * 1.25
                        - result["predictions"]["zero_to_sixty_s"] * 8,
                        1,
                    ),
                }
            )
        rows.sort(key=lambda row: row["rank_score"], reverse=True)
        for index, row in enumerate(rows, start=1):
            row["rank"] = index
        return {"chassis_code": chassis_code, "candidates": rows}

    def _build_metrics(self) -> list[dict[str, Any]]:
        measured = {name: model.score(self.test_rows) for name, model in self.models.items()}
        rows = []
        for algorithm in ALGORITHMS:
            item = dict(algorithm)
            if algorithm["name"] in measured:
                item["demo_r2"] = round(measured[algorithm["name"]]["average"], 3)
                item["demo_target_r2"] = {
                    key: round(value, 3)
                    for key, value in measured[algorithm["name"]].items()
                    if key != "average"
                }
            else:
                item["demo_r2"] = None
                item["demo_note"] = "Production-stack algorithm shown in the slides; not required for this dependency-free demo."
            rows.append(item)
        return rows

    def _features_from_payload(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        engine = get_engine(payload.get("engine_code", "K24A"))
        chassis = get_chassis(payload.get("chassis_code", "MX5_NA"))
        engine.update(payload.get("donor_engine_overrides", {}))
        chassis.update(payload.get("recipient_chassis_overrides", {}))
        features = build_feature_record(
            engine,
            chassis,
            tune_level=float(payload.get("tune_level", 0.65)),
            cooling_capacity_index=payload.get("cooling_capacity_index"),
            tire_grip_index=payload.get("tire_grip_index"),
            suspension_index=payload.get("suspension_index"),
            gear_ratio=payload.get("gear_ratio"),
        )
        return engine, chassis, features

    def _compatibility(self, features: dict[str, float]) -> dict[str, Any]:
        drivetrain = features["drivetrain_match"] * 22
        mount = (1 - features["mount_complexity"]) * 24
        weight_balance = (1 - features["swap_difficulty_index"]) * 18
        cooling = features["cooling_capacity_index"] * 15
        suspension = features["suspension_index"] * 11
        tire = features["tire_grip_index"] * 10
        score = clamp(drivetrain + mount + weight_balance + cooling + suspension + tire, 0, 100)
        return {
            "score": round(score, 1),
            "label": "Excellent" if score >= 82 else "Good" if score >= 68 else "Risky" if score >= 52 else "High Effort",
            "breakdown": {
                "drivetrain_match": round(drivetrain, 1),
                "mount_geometry": round(mount, 1),
                "weight_distribution": round(weight_balance, 1),
                "cooling_readiness": round(cooling, 1),
                "suspension_readiness": round(suspension, 1),
                "tire_grip": round(tire, 1),
            },
        }

    def _confidence_interval(self, predictions: dict[str, float]) -> dict[str, dict[str, float]]:
        residuals = {target: [] for target in TARGETS}
        for row in self.test_rows:
            predicted = self.model.predict_one(row)
            for target in TARGETS:
                residuals[target].append(abs(row[target] - predicted[target]))
        hp_margin = mean(residuals["post_swap_hp"]) * 1.6
        torque_margin = mean(residuals["post_swap_torque_nm"]) * 1.6
        time_margin = mean(residuals["zero_to_sixty_s"]) * 1.6
        return {
            "horsepower": {"low": round(predictions["horsepower"] - hp_margin, 1), "high": round(predictions["horsepower"] + hp_margin, 1)},
            "torque_nm": {"low": round(predictions["torque_nm"] - torque_margin, 1), "high": round(predictions["torque_nm"] + torque_margin, 1)},
            "zero_to_sixty_s": {"low": round(predictions["zero_to_sixty_s"] - time_margin, 2), "high": round(predictions["zero_to_sixty_s"] + time_margin, 2)},
        }

    def _tuning_tips(self, features: dict[str, float], predictions: dict[str, float], compatibility_score: float) -> list[str]:
        tips = []
        if features["forced_induction"] or predictions["horsepower"] > 330:
            turbo_hint = round(features["engine_displacement_l"] * 17 + predictions["horsepower"] / 22)
            tips.append(f"Target a turbo or compressor flow range near {turbo_hint} lb/min before chasing more boost.")
        else:
            tips.append("Prioritize intake, header, and calibration refinement before adding forced induction.")

        if features["gear_ratio"] < 3.9 and predictions["zero_to_sixty_s"] > 5.2:
            tips.append("Use a shorter final drive around 4.10-4.30 to improve launch and 0-60 response.")
        elif features["gear_ratio"] > 4.45 and predictions["horsepower"] > 360:
            tips.append("Consider a slightly taller final drive to reduce traction loss with the higher torque output.")
        else:
            tips.append("Current gearing is within a balanced street-performance range for the predicted output.")

        if features["cooling_capacity_index"] < 0.72:
            tips.append("Upgrade radiator capacity and fan control before extended dyno or track sessions.")

        if compatibility_score < 68:
            tips.append("Budget for custom mounts, driveline alignment, and extra validation because compatibility is below the comfort zone.")
        elif features["suspension_index"] < 0.70:
            tips.append("Add spring/damper and bushing upgrades so the chassis can use the predicted power safely.")
        else:
            tips.append("Chassis readiness looks solid; focus final tuning on tire compound and alignment.")
        return tips
