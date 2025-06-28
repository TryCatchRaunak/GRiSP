import pandas as pd

class GTDScraper:
    def __init__(self, csv_path="data/static_reports/gtd.csv"):
        self.df = pd.read_csv(csv_path, low_memory=False)

    def get_recent_attacks(self, country: str, years=5):
        recent_data = self.df[self.df["country_txt"] == country]
        recent_data = recent_data[recent_data["iyear"] >= (2024 - years)]
        return {
            "total_attacks": recent_data.shape[0],
            "fatalities": recent_data["nkill"].sum(),
            "injuries": recent_data["nwound"].sum(),
            "top_targets": recent_data["target1"].value_counts().head(3).to_dict()
        }