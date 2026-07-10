import unittest

from src.predictor import EngineSwapPredictor


class EngineSwapPredictorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = EngineSwapPredictor()

    def test_prediction_contains_required_outputs(self):
        result = self.predictor.predict(self.predictor.sample_request())

        self.assertIn("horsepower", result["predictions"])
        self.assertIn("torque_nm", result["predictions"])
        self.assertIn("zero_to_sixty_s", result["predictions"])
        self.assertGreater(result["compatibility"]["score"], 0)
        self.assertLessEqual(result["compatibility"]["score"], 100)
        self.assertGreater(len(result["feature_importance"]), 0)

    def test_compare_ranks_candidates(self):
        result = self.predictor.compare(
            {
                "chassis_code": "MX5_NA",
                "candidate_engines": ["K20A", "K24A", "LS3"],
                "tune_level": 0.7,
            }
        )

        self.assertEqual(len(result["candidates"]), 3)
        self.assertEqual(result["candidates"][0]["rank"], 1)
        self.assertGreaterEqual(result["candidates"][0]["rank_score"], result["candidates"][-1]["rank_score"])


if __name__ == "__main__":
    unittest.main()
