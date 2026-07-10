import pandas as pd
from src.dataset import build_training_records

# Generate a large dataset (e.g., 5000+ records)
records = build_training_records(seed=42)
df = pd.DataFrame(records)

# Save to CSV for model training
df.to_csv("data/training_data.csv", index=False)
print("Dataset exported to data/training_data.csv")