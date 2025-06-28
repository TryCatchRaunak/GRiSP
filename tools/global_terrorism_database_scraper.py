import pandas as pd
from crewai.tools import BaseTool
from typing import Optional # Import Optional

class GlobalTerrorismDatabaseTool(BaseTool):
    name: str = "GlobalTerrorismDatabaseTool"
    description: str = "Fetches recent terrorism statistics such as attacks, fatalities, and injuries for a given country."

    # Declare excel_path as a Pydantic field with a default value.
    # This is the path to your .xlsx file.
    excel_path: str = "data/static_reports/gtd.xlsx" 
    
    # Declare df as an optional Pydantic field of type pandas.DataFrame.
    # It will be initialized to None by default, and then populated in __init__.
    df: Optional[pd.DataFrame] = None

    def __init__(self, **kwargs):
        # Call the parent's __init__ method. Pydantic (via BaseTool)
        # will initialize the declared fields (name, description, excel_path).
        super().__init__(**kwargs) 
        
        try:
            # --- IMPORTANT: Replace 'YOUR_ACTUAL_GTD_SHEET_NAME' with the real sheet name from your Excel file ---
            # If your data is on the first sheet and you don't know its name, use sheet_name=0
            self.df = pd.read_excel(self.excel_path, sheet_name=0) 
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Error: The GTD Excel file was not found at {self.excel_path}. "
                "Please ensure the path is correct and the 'data/static_reports' directory exists. "
                "Also, confirm you've saved 'gtd.csv' as 'gtd.xlsx'."
            )
        except ValueError as e: # Catch ValueError specifically for sheet not found
            if "Worksheet named" in str(e) and "not found" in str(e):
                raise ValueError(
                    f"Error: The sheet named 'data' was not found in '{self.excel_path}'. "
                    "Please open the Excel file and provide the exact sheet name, or use sheet_name=0 for the first sheet."
                )
            else:
                raise Exception(f"An unexpected ValueError occurred while reading the Excel file: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while reading the Excel file: {e}")

    def _run(self, country: str) -> str:
        """
        Fetches recent terrorism statistics for a given country.
        Input: country name (e.g., 'United States')
        """
        # Ensure df is loaded before proceeding
        if self.df is None:
            return "Error: Terrorism data could not be loaded. Please check the Excel file path and content."

        try:
            # Making country matching case-insensitive for robustness
            # Ensure 'country_txt' column exists
            if "country_txt" not in self.df.columns:
                return "Error: 'country_txt' column not found in GTD data. Cannot process country query."

            recent_data = self.df[self.df["country_txt"].str.lower() == country.lower()]
            
            # Assuming current year is 2025 (adjust if needed or import datetime)
            current_year = 2025 
            
            # Ensure 'iyear' column exists and is numeric for filtering
            if "iyear" not in recent_data.columns:
                 return "Error: 'iyear' column not found in GTD data. Cannot filter by year."
            # Convert 'iyear' to numeric, coercing errors to NaN
            recent_data["iyear"] = pd.to_numeric(recent_data["iyear"], errors='coerce')
            recent_data = recent_data.dropna(subset=['iyear']) # Drop rows where 'iyear' became NaN
            recent_data = recent_data[recent_data["iyear"] >= (current_year - 5)]

            if recent_data.empty:
                return f"No terrorism data found for {country} in the last 5 years."

            total_attacks = recent_data.shape[0]
            
            # Ensure 'nkill' and 'nwound' columns exist and are numeric before summing
            fatalities = 0
            if "nkill" in recent_data.columns:
                recent_data["nkill"] = pd.to_numeric(recent_data["nkill"], errors='coerce')
                fatalities = int(recent_data["nkill"].sum(skipna=True)) if not recent_data["nkill"].isnull().all() else 0
            
            injuries = 0
            if "nwound" in recent_data.columns:
                recent_data["nwound"] = pd.to_numeric(recent_data["nwound"], errors='coerce')
                injuries = int(recent_data["nwound"].sum(skipna=True)) if not recent_data["nwound"].isnull().all() else 0
            
            # Check if 'target1' column exists before trying to get value_counts
            top_targets_str = "  - No target information available."
            if "target1" in recent_data.columns:
                # Fill NaN values in 'target1' to avoid errors in value_counts if any are present
                top_targets = recent_data["target1"].fillna("Unknown Target").value_counts().head(3).to_dict()
                if top_targets:
                    top_targets_str = "\n".join([f"  - {k}: {v} times" for k, v in top_targets.items()])


            return (
                f"Recent Terrorism Stats for {country} (Last 5 Years):\n"
                f"- Total Attacks: {total_attacks}\n"
                f"- Fatalities: {fatalities}\n"
                f"- Injuries: {injuries}\n"
                f"- Top Targets:\n{top_targets_str}"
            )
        except KeyError as e:
            return f"Error: Missing expected column in GTD data ({e}). Please check column names like 'country_txt', 'iyear', 'nkill', 'nwound', 'target1'."
        except Exception as e:
            return f"Error retrieving terrorism data for {country}: {str(e)}"