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

# 📸 Project Screenshots

## ⚙️ Engine Swap Configuration

<img width="1838" height="962" alt="engine-swap-config" src="https://github.com/user-attachments/assets/09c3a1b5-868d-4d5b-b396-0b2c86352259" />
" />

Configure a custom engine swap by selecting the **donor engine**, **recipient chassis**, tuning level, cooling capacity, tire grip, suspension readiness, and drivetrain parameters before generating AI-powered predictions.

---

## 📈 Performance Prediction & Compatibility

<img width="1847" height="935" alt="performance-prediction" src="https://github.com/user-attachments/assets/fa862c73-d005-463b-9c37-e1d9b4bd49f6" />
 " />

Predicts **horsepower**, **torque**, **0–60 mph acceleration**, and calculates an overall **fitment readiness score** using machine learning while evaluating drivetrain compatibility, weight balance, cooling requirements, and suspension readiness.

---

# 🤖 AI Simulation & Analytics

## 🏁 Dyno Performance & Drag Simulation

<img width="1846" height="928" alt="dyno-performance" src="https://github.com/user-attachments/assets/1aac7fdc-0cdf-4746-aa16-4d591e53e898" />
 " />

Generates an interactive **horsepower and torque dyno curve** across the RPM range and includes a **virtual 1/4-mile drag strip simulator** for estimating acceleration and quarter-mile performance.

---

## 📊 Feature Importance & Expert Recommendations

<img width="1838" height="908" alt="feature-importance" src="https://github.com/user-attachments/assets/4f4db126-7717-4738-9659-2e00d9919cd9" />
 " />

Visualizes the contribution of engine specifications using **feature importance analysis**, performs **fitment diagnostics**, and generates intelligent tuning recommendations to improve compatibility and predicted performance.

---

# 🔧 Build Planning & Garage

## 🛠️ Installation Checklist & Cost Estimator

<img width="1838" height="908" alt="installation-checklist" src="https://github.com/user-attachments/assets/28fc2180-2861-407f-87a5-dcbaf7c90e29" />
 " />

Creates a personalized installation checklist including fabrication tasks, drivetrain modifications, ECU wiring, cooling upgrades, estimated project cost, installation time, and allows users to save build configurations.

---

# 🧠 Machine Learning Models

## 📚 Algorithms Used

<img width="1838" height="908" alt="algorithms" src="https://github.com/user-attachments/assets/30fda31d-77b5-41df-aff8-e053a8d43e94" />
 " />

Showcases the machine learning models evaluated during development, including **Linear Regression**, **Polynomial Regression**, **Ridge/Lasso Regression**, **Random Forest Regression**, **Support Vector Regression (SVR)**, and the final **Gradient Boosting (XGBoost)** model used for prediction.

---

## 📂 Training Datasets

<img width="1838" height="908" alt="datasets" src="https://github.com/user-attachments/assets/8a55705b-190d-4d90-bf10-7287dd5c1375" />" />

Displays the real-world datasets used to train the prediction models, including **EPA Fuel Economy**, **Car Features & MSRP**, **Vehicle Dynamics**, and **Engine Swap Community Logs**, providing the foundation for accurate performance estimation and compatibility analysis.

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
