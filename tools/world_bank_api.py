import requests
from crewai.tools import BaseTool
from typing import Optional # Use Optional for consistency if you choose, but not strictly needed for a direct string default

class WorldBankApiTool(BaseTool):
    name: str = "WorldBankApiTool"
    description: str = (
        "Retrieves economic indicators like GDP, inflation, debt, etc. for a given country code using the World Bank API. "
        "Expected input format: 'country_code:indicator'. "
        "Example: 'IN:NY.GDP.MKTP.CD' → India GDP in USD."
    )

    # Declare base_url as a Pydantic field.
    # Since it has a default string value, Pydantic handles it.
    base_url: str = "https://api.worldbank.org/v2"

    def __init__(self, **kwargs):
        # Always call the parent's __init__ when inheriting from BaseTool.
        # Pydantic (via BaseTool) will automatically set self.base_url
        # because it's declared as a class field with a default value.
        super().__init__(**kwargs) 
        # No need to set self.base_url = "..." here, Pydantic does it.

    def _run(self, input_string: str) -> str:
        """
        Retrieves economic indicators for a given country and indicator code from the World Bank API.
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

            # Request for the most recent data point (last 5 years)
            # per_page=1 to get just one record (the most recent by default usually)
            # source=2 for World Development Indicators (WDI), which is a common and rich dataset.
            url = f"{self.base_url}/country/{country_code}/indicator/{indicator}?format=json&date=2020:2024&per_page=1&source=2"
            
            response = requests.get(url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # The World Bank API often returns a list, where the first element is metadata
            # and the second element is the data. If no data, the second element might be empty or missing.
            if not data or len(data) < 2 or not data[1]:
                return f"No data found for indicator '{indicator}' for country code '{country_code}' in recent years (2020-2024)."

            # Check if the data point itself is null/None, which can happen for some indicators/years
            record = data[1][0] # Access the first record from the data array
            value = record.get("value")
            year = record.get("date")
            # Get full country/indicator name if available in the metadata
            country_name = record.get("country", {}).get("value", country_code.upper()) 
            indicator_name = record.get("indicator", {}).get("value", indicator) 

            if value is None:
                return (
                    f"Data for indicator '{indicator_name}' for {country_name} "
                    f"is not available for year {year} (value is null/missing)."
                )

            # Format the value for better readability (e.g., millions/billions for large numbers)
            # Using a more robust formatting for large numbers if applicable
            if isinstance(value, (int, float)):
                if value >= 1_000_000_000_000:
                    formatted_value = f"{value/1_000_000_000_000:,.2f} Trillion"
                elif value >= 1_000_000_000:
                    formatted_value = f"{value/1_000_000_000:,.2f} Billion"
                elif value >= 1_000_000:
                    formatted_value = f"{value/1_000_000:,.2f} Million"
                elif value >= 1_000:
                    formatted_value = f"{value/1_000:,.2f} Thousand"
                else:
                    formatted_value = f"{value:,.2f}" # Default to 2 decimal places for smaller numbers
            else:
                formatted_value = str(value) # Fallback for non-numeric values

            return (
                f"World Bank Data for {country_name} ({country_code.upper()}):\n"
                f"- Indicator: {indicator_name}\n"
                f"- Year: {year}\n"
                f"- Value: {formatted_value}\n"
                f"- Source: World Bank"
            )
        except requests.exceptions.RequestException as e:
            return f"Network or API error when fetching World Bank data for '{input_string}': {str(e)}. Please check country code/indicator."
        except (IndexError, TypeError, KeyError) as e:
            # Catch errors if the JSON structure is unexpected (e.g., no data for indicator, malformed response)
            return (
                f"Error parsing World Bank API response for '{input_string}'. "
                f"It might be an invalid indicator or country code, or no data is available: {str(e)}"
            )
        except Exception as e:
            return f"An unexpected error occurred while fetching World Bank data for '{input_string}': {str(e)}"