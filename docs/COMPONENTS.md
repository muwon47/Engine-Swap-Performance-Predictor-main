# Component Documentation

This document explains the main components of the Engine Swap Performance Predictor mini project and how they work together.

## 1. Project Launcher

**File:** `run.py`

`run.py` is the entry point for the application. It imports `main()` from `app.server` and starts the local HTTP server.

Run it with:

```powershell
python .\run.py
```

The app starts at:

```text
http://127.0.0.1:8000
```

## 2. HTTP API and Static Server

**File:** `app/server.py`

This file provides the local backend server using Python's built-in `http.server` module. It was chosen so the mini project can run without installing external dependencies.

Main responsibilities:

- Starts a threaded local server on port `8000`.
- Serves the browser dashboard from the `static/` folder.
- Exposes JSON API routes for prediction, comparison, metadata, and example payloads.
- Converts request JSON into predictor service calls.
- Returns structured JSON responses to the UI.

API endpoints:

- `GET /api/meta` returns slide-based project metadata, available engines, available chassis, algorithm descriptions, and dataset notes.
- `GET /api/example` returns a sample prediction payload.
- `POST /api/predict` returns performance predictions, compatibility scoring, confidence intervals, feature importance, and tuning tips.
- `POST /api/compare` ranks multiple donor engines for the selected chassis.

## 3. Predictor Service

**File:** `src/predictor.py`

This is the core application service. It connects the dataset, regression model, scoring logic, and final API output format.

Main responsibilities:

- Builds deterministic training records at startup.
- Splits records into training and test sets.
- Trains three lightweight demo models: linear regression, ridge regression, and polynomial regression.
- Uses polynomial regression as the selected model for predictions.
- Calculates compatibility score and score labels.
- Builds confidence intervals from test-set residuals.
- Ranks feature importance from model coefficients.
- Generates tuning recommendations.
- Compares candidate engines and ranks them by combined performance and compatibility.

Important outputs:

- `predictions`: horsepower, torque, and 0-60 mph time.
- `compatibility`: score, label, and scoring breakdown.
- `confidence_intervals`: low and high ranges for each prediction.
- `feature_importance`: top model drivers.
- `tuning_tips`: practical recommendations based on predicted setup risks.
- `engineered_features`: computed model input features for transparency.

## 4. Dataset and Feature Engineering

**File:** `src/dataset.py`

This file contains demo engine and chassis data plus feature engineering logic.

Main data structures:

- `BASE_ENGINES`: donor engine catalog with displacement, cylinders, compression ratio, weight, horsepower, torque, forced induction, layout, and mount width.
- `CHASSIS`: recipient chassis catalog with layout, drivetrain, weight, stock horsepower, engine bay width, wheelbase, drag coefficient, gear ratio, cooling, suspension, and tire-grip indexes.
- `ENGINE_FAMILY_ENCODING`: numeric encoding for engine family categories.

Feature engineering includes:

- `power_to_weight_ratio`
- `torque_per_litre`
- `displacement_per_cylinder`
- `engine_family_encoding`
- `swap_difficulty_index`
- `drivetrain_match`
- `mount_complexity`
- cooling, tire, suspension, and gear-ratio indexes

The function `build_training_records()` creates deterministic synthetic training examples from combinations of engines and chassis. This simulates the slide datasets without requiring downloads or private data.

## 5. Regression Model

**File:** `src/linear_model.py`

This file implements a small pure-Python ridge regression model.

Main responsibilities:

- Standardizes numeric features.
- Supports linear and degree-2 polynomial features.
- Solves regression coefficients using a Gaussian-elimination linear-system solver.
- Supports multiple target outputs at once.
- Calculates R2 scores for evaluation.
- Produces coefficient-based feature importance.

Why this exists:

The slides reference scikit-learn, XGBoost, and SHAP. Those are appropriate production tools, but this mini project keeps the runnable demo dependency-free because the local environment did not have those packages installed.

Production upgrade path:

- Replace `RidgeRegressor` with scikit-learn `Pipeline`.
- Use `MultiOutputRegressor` for multi-target predictions.
- Add XGBoost for boosted-tree performance.
- Add SHAP for richer explainability.

## 6. Slide Metadata Catalog

**File:** `src/catalog.py`

This file stores structured metadata taken from the supplied slides.

It contains:

- System capabilities.
- Dataset source descriptions.
- Feature engineering list.
- Algorithm descriptions and slide R2 values.
- Tech stack categories.

The metadata is returned by `GET /api/meta` and rendered in the browser UI.

## 7. Browser Dashboard

**Files:** `static/index.html`, `static/styles.css`, `static/app.js`

The frontend is a static browser dashboard that talks to the local API.

`static/index.html` defines the page layout:

- Input form for donor engine, chassis, tune level, cooling, tire grip, suspension, and gear ratio.
- Prediction cards for horsepower, torque, and 0-60 mph.
- Compatibility score panel.
- Feature importance section.
- Tuning tips section.
- Candidate comparison section.
- Algorithm and dataset information sections.

`static/styles.css` handles the visual design:

- Dark navy slide-inspired theme.
- Red vertical accent bar.
- Orange and teal highlights.
- Responsive card layouts.
- Metric cards, score bars, and comparison rows.

`static/app.js` handles browser behavior:

- Fetches metadata from `/api/meta`.
- Fills engine and chassis dropdowns.
- Submits prediction requests to `/api/predict`.
- Renders prediction cards and confidence intervals.
- Renders compatibility scoring and feature importance bars.
- Sends comparison requests to `/api/compare`.
- Renders ranked donor engine candidates.

## 8. Sample Payload

**File:** `data/sample_request.json`

This file contains an example prediction request:

```json
{
  "engine_code": "K24A",
  "chassis_code": "MX5_NA",
  "tune_level": 0.65,
  "cooling_capacity_index": 0.74,
  "tire_grip_index": 0.78,
  "suspension_index": 0.72,
  "gear_ratio": 4.3
}
```

Use it as a reference for API testing or when building a different frontend.

## 9. Tests

**File:** `tests/test_predictor.py`

The test suite validates the core predictor service.

It checks:

- The prediction response contains horsepower, torque, and 0-60 mph.
- Compatibility score stays within the valid range.
- Feature importance is returned.
- Candidate comparison returns ranked engines in descending rank-score order.

Run tests with:

```powershell
python -m unittest discover -s tests
```

## 10. Request Flow

The typical application flow is:

```text
Browser form
  -> static/app.js
  -> POST /api/predict
  -> app/server.py
  -> src/predictor.py
  -> src/dataset.py feature engineering
  -> src/linear_model.py prediction
  -> compatibility scoring and tuning tips
  -> JSON response
  -> browser dashboard rendering
```

Candidate comparison uses the same flow, but repeats prediction for multiple donor engines and sorts the results by a combined rank score.

## 11. Design Notes

This is a mini project, so the training data is deterministic and source-inspired rather than downloaded from external datasets. That keeps the app portable and easy to run in a classroom or demo environment.

The architecture is intentionally modular:

- Replace `src/linear_model.py` when adding production ML libraries.
- Extend `src/dataset.py` when importing real datasets.
- Keep `src/predictor.py` as the service layer that controls output shape.
- Replace `app/server.py` with FastAPI if external dependencies are allowed.
- Replace the static frontend with React if the UI grows larger.
