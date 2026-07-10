# Engine Swap Performance Predictor

A mini project based on the supplied system-design slides. It predicts post-swap horsepower, torque, and 0-60 mph time, scores engine-to-chassis compatibility, ranks important features, compares multiple donor engines, and returns tuning tips.

The project is intentionally runnable with **Python standard library only**. The slides mention scikit-learn, XGBoost, SHAP, FastAPI, React, MongoDB, and Docker as a production stack; this mini version mirrors those ideas with a lightweight in-repo model and a simple browser UI.

## Features

- Multi-output regression for horsepower, torque, and 0-60 mph.
- Compatibility score using drivetrain match, mount geometry, cooling, suspension, and weight distribution.
- Interactive input form in the browser.
- Feature importance ranking from model coefficients.
- Side-by-side donor engine comparison.
- Data-driven tuning tips for turbo sizing, gearing, cooling, mounts, and suspension.
- Metadata pages for datasets, algorithms, and tech stack from the slides.

## Run

```powershell
python .\run.py
```

Open the URL printed in the terminal, usually:

```text
http://127.0.0.1:8000
```

## Test

```powershell
python -m unittest discover -s tests
```

## Project Structure

```text
app/        Minimal HTTP API and static file server
src/        Dataset generator, regression model, predictor service, metadata
static/     Browser dashboard
tests/      Unit tests
data/       Example API request payloads
docs/       Component-level documentation
run.py      Local launcher
```

For a detailed explanation of each component, see `docs/COMPONENTS.md`.

## API

- `GET /api/meta` returns system capabilities, datasets, algorithms, tech stack, available engines, and available chassis.
- `GET /api/example` returns a sample request body.
- `POST /api/predict` returns predictions, compatibility score, feature importance, and tuning tips.
- `POST /api/compare` ranks multiple donor engine candidates for one recipient chassis.

## Production Upgrade Ideas

- Replace the pure-Python ridge model with scikit-learn pipelines and `MultiOutputRegressor`.
- Add XGBoost for boosted-tree performance and SHAP for richer explainability.
- Persist swap records in MongoDB or SQL.
- Expose the API with FastAPI and package deployment with Docker.
- Replace the static UI with React when state and charts become more complex.
