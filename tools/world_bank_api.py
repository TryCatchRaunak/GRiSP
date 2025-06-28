import requests
from crewai_tools import BaseTool

class WorldBankApiTool(BaseTool):
    name = "WorldBankApiTool"
    description = "Retrieves economic indicators like GDP, inflation, debt, etc. for a given country code using the World Bank API."

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.worldbank.org/v2"

    def _run(self, input: str) -> str:
        """
        Expected input format: 'country_code:indicator'
        Example: 'IN:NY.GDP.MKTP.CD' → India GDP in USD
        """
        try:
            if ":" not in input:
                return "Invalid input format. Use 'country_code:indicator'."

            country_code, indicator = input.split(":")
            url = f"{self.base_url}/country/{country_code}/indicator/{indicator}?format=json&per_page=1"

            response = requests.get(url)
            if response.status_code != 200:
                return f"World Bank API request failed with status {response.status_code}."

            data = response.json()
            value = data[1][0]["value"]
            year = data[1][0]["date"]

            return (
                f"World Bank Data for {country_code.upper()}:\n"
                f"- Indicator: {indicator}\n"
                f"- Year: {year}\n"
                f"- Value: {value}\n"
                f"- Source: World Bank"
            )
        except Exception as e:
            return f"Error fetching data: {str(e)}"