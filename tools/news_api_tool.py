import os
import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import ClassVar # Import ClassVar

load_dotenv()

class NewsApiTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    name: ClassVar[str] = "NewsApiTool"
    description: ClassVar[str] = "Fetches the latest news headlines and summaries related to a country's events for sentiment and security analysis."

    def _run(self, query: str) -> str:
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            return "Error: NEWSAPI_KEY not found in environment variables. Please set it."

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5,
            "apiKey": api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data.get("status") != "ok":
                # Provide a more detailed error message from the API if available
                return f"News API error: {data.get('code', 'Unknown Code')} - {data.get('message', 'Unknown Error')}"

            articles = data.get("articles", [])
            if not articles:
                return f"No news articles found for the query: '{query}'."

            # Format output
            output = []
            for article in articles:
                title = article.get("title", "No Title")
                description = article.get("description", "No Description")
                source = article.get("source", {}).get("name", "Unknown Source")
                url_link = article.get("url", "") # Get the URL for more context
                output.append(f"📰 {title} ({source}): {description}\n🔗 {url_link}")

            return "Top News Articles:\n\n" + "\n\n".join(output)

        except requests.exceptions.RequestException as e:
            return f"Network or API error while fetching news for query '{query}': {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred while processing news for query '{query}': {str(e)}"