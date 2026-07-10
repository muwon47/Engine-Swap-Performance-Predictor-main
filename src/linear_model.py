from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float], mean: float) -> float:
    variance = sum((value - mean) ** 2 for value in values) / max(len(values) - 1, 1)
    return sqrt(variance) or 1.0


def _solve_linear_system(matrix: list[list[float]], rhs: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    output_count = len(rhs[0])
    augmented = [row[:] + rhs_row[:] for row, rhs_row in zip(matrix, rhs)]

    for column in range(n):
        pivot_row = max(range(column, n), key=lambda row_index: abs(augmented[row_index][column]))
        augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]

        pivot = augmented[column][column]
        if abs(pivot) < 1e-12:
            pivot = 1e-12
            augmented[column][column] = pivot

        for item in range(column, n + output_count):
            augmented[column][item] /= pivot

        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            for item in range(column, n + output_count):
                augmented[row][item] -= factor * augmented[column][item]

    return [row[n:] for row in augmented]


@dataclass
class RidgeRegressor:
    alpha: float = 0.8
    degree: int = 1
    feature_names: list[str] = field(default_factory=list)
    target_names: list[str] = field(default_factory=list)
    means: list[float] = field(default_factory=list)
    scales: list[float] = field(default_factory=list)
    expanded_names: list[str] = field(default_factory=list)
    coefficients: list[list[float]] = field(default_factory=list)

    def fit(self, rows: list[dict[str, float]], feature_names: list[str], target_names: list[str]) -> "RidgeRegressor":
        self.feature_names = feature_names[:]
        self.target_names = target_names[:]
        columns = [[float(row[name]) for row in rows] for name in feature_names]
        self.means = [_mean(column) for column in columns]
        self.scales = [_std(column, mean) for column, mean in zip(columns, self.means)]

        x_matrix = [self._expand(self._standardize(row)) for row in rows]
        y_matrix = [[float(row[target]) for target in target_names] for row in rows]
        feature_count = len(x_matrix[0])
        target_count = len(target_names)

        xtx = [[0.0 for _ in range(feature_count)] for _ in range(feature_count)]
        xty = [[0.0 for _ in range(target_count)] for _ in range(feature_count)]

        for x_row, y_row in zip(x_matrix, y_matrix):
            for i in range(feature_count):
                for j in range(feature_count):
                    xtx[i][j] += x_row[i] * x_row[j]
                for target_index in range(target_count):
                    xty[i][target_index] += x_row[i] * y_row[target_index]

        for i in range(1, feature_count):
            xtx[i][i] += self.alpha

        self.coefficients = _solve_linear_system(xtx, xty)
        return self

    def predict_one(self, row: dict[str, float]) -> dict[str, float]:
        x_row = self._expand(self._standardize(row))
        predictions = {}
        for target_index, target in enumerate(self.target_names):
            predictions[target] = sum(
                x_value * self.coefficients[coef_index][target_index]
                for coef_index, x_value in enumerate(x_row)
            )
        return predictions

    def predict(self, rows: list[dict[str, float]]) -> list[dict[str, float]]:
        return [self.predict_one(row) for row in rows]

    def score(self, rows: list[dict[str, float]]) -> dict[str, float]:
        predictions = self.predict(rows)
        scores = {}
        for target in self.target_names:
            actual_values = [float(row[target]) for row in rows]
            predicted_values = [prediction[target] for prediction in predictions]
            actual_mean = _mean(actual_values)
            total = sum((actual - actual_mean) ** 2 for actual in actual_values)
            residual = sum((actual - predicted) ** 2 for actual, predicted in zip(actual_values, predicted_values))
            scores[target] = 1 - residual / total if total else 0.0
        scores["average"] = _mean(list(scores.values()))
        return scores

    def feature_importance(self, limit: int = 8) -> list[dict[str, float | str]]:
        totals = {name: 0.0 for name in self.feature_names}

        for expanded_index, expanded_name in enumerate(self.expanded_names):
            if expanded_name == "intercept":
                continue
            base_name = expanded_name.removesuffix("^2")
            totals[base_name] = totals.get(base_name, 0.0) + sum(
                abs(coef) for coef in self.coefficients[expanded_index]
            )

        grand_total = sum(totals.values()) or 1.0
        ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:limit]
        return [
            {
                "feature": feature,
                "importance": round(value / grand_total, 4),
                "percent": round((value / grand_total) * 100, 1),
            }
            for feature, value in ranked
        ]

    def _standardize(self, row: dict[str, float]) -> list[float]:
        return [
            (float(row[name]) - mean) / scale
            for name, mean, scale in zip(self.feature_names, self.means, self.scales)
        ]

    def _expand(self, values: list[float]) -> list[float]:
        expanded = [1.0] + values
        if self.degree >= 2:
            expanded += [value * value for value in values]
        if not self.expanded_names:
            self.expanded_names = ["intercept"] + self.feature_names[:]
            if self.degree >= 2:
                self.expanded_names += [f"{name}^2" for name in self.feature_names]
        return expanded
