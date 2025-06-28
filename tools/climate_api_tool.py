import pandas as pd
from crewai.tools import BaseTool
from typing import ClassVar # Import ClassVar for class-level attributes

class ClimateApiTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    # Use ClassVar if these are meant to be constant for all instances
    name: ClassVar[str] = "ClimateApiTool"
    description: ClassVar[str] = "Fetches climate vulnerability and readiness score from ND-GAIN index for a given country."

    def __init__(self, csv_path: str = None): # Add type hint for csv_path
        super().__init__()
        # Default path if none is provided
        self.csv_path = csv_path or "data/static_reports/ndgain.csv"
        try:
            self.df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The CSV file was not found at {self.csv_path}. Please ensure the path is correct.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the CSV file: {e}")

    def _run(self, country: str) -> str:
        row = self.df[self.df["Country"].str.lower() == country.lower()] # Case-insensitive country match
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