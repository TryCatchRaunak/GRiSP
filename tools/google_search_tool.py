import os
import requests
from crewai_tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class GoogleSearchTool(BaseTool):
    name = "GoogleSearchTool"
    description = "Performs a Google Custom Search and returns a summary of top results for a given query."

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx_id = os.getenv("CX_ID")

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
            data = response.json()

            if "items" not in data:
                return f"No search results found for: {query}"

            summaries = []
            for item in data["items"]:
                title = item.get("title", "No Title")
                snippet = item.get("snippet", "No Description")
                link = item.get("link", "")
                summaries.append(f"- **{title}**: {snippet}\n  🔗 {link}")

            return f"🔍 Top Search Results for '{query}':\n" + "\n\n".join(summaries)

        except Exception as e:
            return f"Search failed for query '{query}': {str(e)}"