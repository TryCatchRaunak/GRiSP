import requests
from crewai.tools import BaseTool
from typing import ClassVar # Import ClassVar

class WorldBankApiTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    name: ClassVar[str] = "WorldBankApiTool"
    description: ClassVar[str] = "Retrieves economic indicators like GDP, inflation, debt, etc. for a given country code using the World Bank API. Expected input format: 'country_code:indicator'. Example: 'IN:NY.GDP.MKTP.CD' → India GDP in USD."

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.worldbank.org/v2"

    def _run(self, input_string: str) -> str: # Renamed 'input' to 'input_string' to avoid conflict with built-in
        """
        Expected input format: 'country_code:indicator'
        Example: 'IN:NY.GDP.MKTP.CD' → India GDP in USD
        """
        try:
            if ":" not in input_string:
                return "Invalid input format. Use 'country_code:indicator'. Example: 'US:SP.POP.TOTL' for USA total population."

            country_code, indicator = input_string.split(":")
            # Ensure country code is uppercase for consistency, though API is often case-insensitive
            country_code = country_code.strip().upper() 
            indicator = indicator.strip() # Remove any leading/trailing whitespace from indicator

            # Request for the most recent data point
            url = f"{self.base_url}/country/{country_code}/indicator/{indicator}?format=json&date=2020:2024&per_page=1&source=2"
            # Added 'date' parameter to limit results to recent years, and 'source=2' for World Development Indicators (common)

            response = requests.get(url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # The World Bank API returns a list, where the first element is metadata
            # and the second element is the data. If no data, the second element is empty.
            if len(data) < 2 or not data[1]:
                return f"No data found for indicator '{indicator}' for country code '{country_code}'."

            # Check if the data point itself is null/None, which can happen for some indicators/years
            record = data[1][0]
            value = record.get("value")
            year = record.get("date")
            country_name = record.get("country", {}).get("value", country_code.upper()) # Get full country name if available
            indicator_name = record.get("indicator", {}).get("value", indicator) # Get full indicator name

            if value is None:
                return f"Data for indicator '{indicator_name}' for {country_name} is not available for year {year} (value is null)."

            # Format the value for better readability (e.g., millions/billions for large numbers)
            formatted_value = f"{value:,}" if isinstance(value, (int, float)) else str(value)

            return (
                f"World Bank Data for {country_name} ({country_code.upper()}):\n"
                f"- Indicator: {indicator_name}\n"
                f"- Year: {year}\n"
                f"- Value: {formatted_value}\n"
                f"- Source: World Bank"
            )
        except requests.exceptions.RequestException as e:
            return f"Network or API error when fetching World Bank data for '{input_string}': {str(e)}"
        except (IndexError, TypeError) as e:
            # Catch errors if the JSON structure is unexpected (e.g., no data for indicator)
            return f"Error parsing World Bank API response for '{input_string}'. It might be an invalid indicator or country code, or no data is available: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred while fetching World Bank data for '{input_string}': {str(e)}"