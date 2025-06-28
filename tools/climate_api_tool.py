import os
import pandas as pd
from crewai_tools import BaseTool

class ClimateApiTool(BaseTool):
    name = "ClimateApiTool"
    description = "Fetches climate vulnerability and readiness score from ND-GAIN index for a given country."

    def __init__(self, csv_path=None):
        super().__init__()
        # Default path if none is provided
        self.csv_path = csv_path or "data/static_reports/ndgain.csv"
        self.df = pd.read_csv(self.csv_path)

    def _run(self, country: str) -> str:
        row = self.df[self.df["Country"] == country]
        if row.empty:
            return f"No data found for {country} in ND-GAIN dataset."

        row = row.iloc[0]
        return (
            f"Climate Risk Score for {country}:\n"
            f"- ND-GAIN Index: {row['ND-GAIN Index']}\n"
            f"- Vulnerability: {row['Vulnerability']}\n"
            f"- Readiness: {row['Readiness']}\n"
            f"- Year: {int(row['Year'])}"
        )