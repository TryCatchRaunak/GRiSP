import pandas as pd
from crewai_tools import BaseTool

class GlobalTerrorismDatabaseTool(BaseTool):
    name = "GlobalTerrorismDatabaseTool"
    description = "Fetches recent terrorism statistics such as attacks, fatalities, and injuries for a given country."

    def __init__(self, csv_path="data/static_reports/gtd.csv"):
        super().__init__()
        self.df = pd.read_csv(csv_path, low_memory=False)

    def _run(self, country: str) -> str:
        try:
            recent_data = self.df[self.df["country_txt"] == country]
            recent_data = recent_data[recent_data["iyear"] >= (2024 - 5)]

            if recent_data.empty:
                return f"No terrorism data found for {country} in the last 5 years."

            total_attacks = recent_data.shape[0]
            fatalities = int(recent_data["nkill"].sum(skipna=True))
            injuries = int(recent_data["nwound"].sum(skipna=True))
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