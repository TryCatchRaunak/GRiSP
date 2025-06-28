import os
import requests
from crewai_tools import BaseTool

class NewsApiTool(BaseTool):
    name = "NewsApiTool"
    description = "Fetches the latest news headlines and summaries related to a country's events for sentiment and security analysis."

    def _run(self, query: str) -> str:
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            return "Error: NEWSAPI_KEY not found in environment variables."

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
            data = response.json()

            if data.get("status") != "ok":
                return f"News API error: {data.get('message')}"

            articles = data.get("articles", [])
            if not articles:
                return "No news articles found for the query."

            # Format output
            output = []
            for article in articles:
                title = article.get("title", "No Title")
                description = article.get("description", "No Description")
                source = article.get("source", {}).get("name", "Unknown Source")
                output.append(f"📰 {title} ({source}): {description}")

            return "\n\n".join(output)

        except Exception as e:
            return f"Exception occurred while fetching news: {e}"