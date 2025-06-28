import pandas as pd

class ClimateAPITool:
    def __init__(self, csv_path="data/static_reports/ndgain.csv"):
        self.df = pd.read_csv(csv_path)

    def get_climate_score(self, country: str):
        row = self.df[self.df["Country"] == country]
        if row.empty:
            return {"error": "Country not found"}
        return {
            "score": float(row["ND-GAIN Index"]),
            "vulnerability": float(row["Vulnerability"]),
            "readiness": float(row["Readiness"]),
            "year": int(row["Year"])
        }