import pandas as pd
from crewai.tools import BaseTool
from typing import Optional # Import Optional

class ClimateApiTool(BaseTool):
    name: str = "ClimateApiTool"
    description: str = (
        "Fetches climate vulnerability and readiness score from ND-GAIN index "
        "for a given country. Input should be a country name (e.g., 'India')."
    )

    excel_path: str = "data/static_reports/ndgain.xlsx" 
    
    # Declare 'df' as an optional field of type pandas.DataFrame
    # It will be initialized to None by default, and then populated in __init__
    df: Optional[pd.DataFrame] = None 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        
        try:
            # IMPORTANT: Replace 'ndgain' with your actual sheet name if it's different.
            # If your data is on the first sheet and you don't know its name, use sheet_name=0
            self.df = pd.read_excel(self.excel_path, sheet_name='ndgain') 
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Error: The Excel file was not found at {self.excel_path}. "
                "Please ensure the path is correct and the 'data/static_reports' directory exists. "
                "Also, confirm you've saved 'ndgain.csv' as 'ndgain.xlsx'."
            )
        except ValueError as e: # Catch ValueError specifically for sheet not found
            if "Worksheet named" in str(e) and "not found" in str(e):
                raise ValueError(
                    f"Error: The sheet named 'ndgain' was not found in '{self.excel_path}'. "
                    "Please open the Excel file and provide the exact sheet name, or use sheet_name=0 for the first sheet."
                )
            else:
                raise Exception(f"An unexpected ValueError occurred while reading the Excel file: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while reading the Excel file: {e}")

    def _run(self, country: str) -> str:
        """
        Fetches climate vulnerability and readiness score for a given country.
        Input: country name (e.g., 'India')
        """
        # Ensure that df is not None before proceeding
        if self.df is None:
            return "Error: Climate data could not be loaded. Please check the Excel file path and content."

        # Ensure country matching is case-insensitive
        row = self.df[self.df["Country"].str.lower() == country.lower()]
        
        if row.empty:
            return f"No data found for {country} in ND-GAIN dataset."

        # Get the first matching row
        row = row.iloc[0]

        # Format the output string
        return (
            f"Climate Risk Score for {country}:\n"
            f"- ND-GAIN Index: {row['ND-GAIN Index']}\n"
            f"- Vulnerability: {row['Vulnerability']}\n"
            f"- Readiness: {row['Readiness']}\n"
            f"- Year: {int(row['Year'])}"
        )