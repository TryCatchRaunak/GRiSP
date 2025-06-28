import pandas as pd
from crewai.tools import BaseTool
from typing import ClassVar # Import ClassVar for class-level attributes

class GlobalTerrorismDatabaseTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    name: ClassVar[str] = "GlobalTerrorismDatabaseTool"
    description: ClassVar[str] = "Fetches recent terrorism statistics such as attacks, fatalities, and injuries for a given country."

    def __init__(self, csv_path: str = "data/static_reports/gtd.csv"): # Add type hint for csv_path
        super().__init__()
        try:
            self.df = pd.read_csv(csv_path, low_memory=False)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The GTD CSV file was not found at {csv_path}. Please ensure the path is correct.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the GTD CSV file: {e}")

    def _run(self, country: str) -> str:
        try:
            # Making country matching case-insensitive for robustness
            recent_data = self.df[self.df["country_txt"].str.lower() == country.lower()]
            
            # Assuming current year is 2025 based on the context provided.
            # You might want to make this dynamic using datetime if deployed long-term.
            current_year = 2025 # Or datetime.now().year if you import datetime
            recent_data = recent_data[recent_data["iyear"] >= (current_year - 5)]

            if recent_data.empty:
                return f"No terrorism data found for {country} in the last 5 years."

            total_attacks = recent_data.shape[0]
            # Ensure sums return 0 if there are no valid numbers, instead of NaN
            fatalities = int(recent_data["nkill"].sum(skipna=True)) if not recent_data["nkill"].isnull().all() else 0
            injuries = int(recent_data["nwound"].sum(skipna=True)) if not recent_data["nwound"].isnull().all() else 0
            
            top_targets = recent_data["target1"].value_counts().head(3).to_dict()

            top_targets_str = "\n".join([f"  - {k}: {v} times" for k, v in top_targets.items()])

            return (
                f"Recent Terrorism Stats for {country} (Last 5 Years):\n"
                f"- Total Attacks: {total_attacks}\n"
                f"- Fatalities: {fatalities}\n"
                f"- Injuries: {injuries}\n"
                f"- Top Targets:\n{top_targets_str}"
            )
        except Exception as e:
            return f"Error retrieving terrorism data for {country}: {str(e)}"