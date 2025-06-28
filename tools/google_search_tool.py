import os
import requests
from crewai.tools import BaseTool
from typing import Optional # Import Optional for fields that might be None initially

class GoogleSearchTool(BaseTool):
    name: str = "GoogleSearchTool"
    description: str = (
        "Performs a Google search and returns a snippet of the top results. "
        "Useful for getting real-time information or validating facts. "
        "Input should be a concise search query string."
    )

    # Declare api_key and cx_id as optional Pydantic fields.
    # They will be loaded from environment variables in __init__.
    # Pydantic requires all instance attributes set in __init__
    # (that aren't part of the constructor's arguments) to be declared here.
    api_key: Optional[str] = None
    cx_id: Optional[str] = None

    def __init__(self, **kwargs):
        # Always call the parent's __init__ when inheriting from BaseTool
        # to ensure Pydantic fields are correctly initialized.
        super().__init__(**kwargs)
        
        # Load API key and CX ID from environment variables
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx_id = os.getenv("GOOGLE_CX_ID")

        # Add checks to ensure keys are loaded, as the tool won't work without them.
        if not self.api_key:
            # Raise a more informative error specific to missing env var
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it before running.")
        if not self.cx_id:
            # Raise a more informative error specific to missing env var
            raise ValueError("GOOGLE_CX_ID environment variable not set. Please set it before running.")

    def _run(self, query: str) -> str:
        """
        Performs a Google Custom Search for the given query.
        Input: query (str) - the search query
        """
        # Defensive check in _run in case __init__ somehow failed to set them (though it raises errors now)
        if not self.api_key or not self.cx_id:
            return "Error: Google Search API keys are not properly configured. Cannot perform search."

        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx_id, # This will now be the ID without a colon, as per your screenshot
            "q": query
        }

        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            search_results = response.json()

            if "items" not in search_results:
                # This can happen if no results are found or if the API key/CX ID is invalid
                return "No relevant Google search results found for your query or an API issue occurred (e.g., invalid key/CX ID, quota exceeded)."

            snippets = []
            for item in search_results["items"][:3]: # Get top 3 snippets
                snippet = item.get("snippet", "No snippet available.")
                link = item.get("link", "No link available.")
                snippets.append(f"Snippet: {snippet}\nLink: {link}")
            
            return "\n\n".join(snippets)

        except requests.exceptions.RequestException as e:
            # Catch network-related errors or bad HTTP responses
            return f"Error during Google Search API request: {e}. Check network connection or API key/CX ID."
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred during Google Search: {e}"