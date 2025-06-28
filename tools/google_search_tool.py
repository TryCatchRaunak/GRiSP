import os
import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import ClassVar # Import ClassVar

load_dotenv()

class GoogleSearchTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    name: ClassVar[str] = "GoogleSearchTool"
    description: ClassVar[str] = "Performs a Google Custom Search and returns a summary of top results for a given query."

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx_id = os.getenv("CX_ID")

        # Optional: Add checks for environment variables
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        if not self.cx_id:
            raise ValueError("CX_ID environment variable not set.")

    def _run(self, query: str) -> str:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx_id,
            "q": query,
            "num": 5
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if "items" not in data or not data["items"]: # Also check if items list is empty
                return f"No search results found for: {query}"

            summaries = []
            for item in data["items"]:
                title = item.get("title", "No Title")
                snippet = item.get("snippet", "No Description")
                link = item.get("link", "")
                summaries.append(f"- **{title}**: {snippet}\n  🔗 {link}") # Changed indent to 2 spaces

            return f"🔍 Top Search Results for '{query}':\n" + "\n\n".join(summaries)

        except requests.exceptions.RequestException as e:
            return f"Network or API error during search for query '{query}': {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred during search for query '{query}': {str(e)}"