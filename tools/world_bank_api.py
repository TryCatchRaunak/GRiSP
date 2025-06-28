import requests

class WorldBankAPI:
    BASE_URL = "https://api.worldbank.org/v2"

    def fetch_indicator(self, country_code: str, indicator: str):
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator}?format=json&per_page=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            try:
                value = data[1][0]["value"]
                year = data[1][0]["date"]
                return {
                    "indicator": indicator,
                    "value": value,
                    "year": year,
                    "source": "World Bank"
                }
            except Exception:
                return {"error": "No data found"}
        else:
            return {"error": "API request failed"}