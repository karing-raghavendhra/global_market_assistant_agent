from base_agent import BaseAgent
from tavily import TavilyClient

class StrategyRecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(required_api_keys=[
            {"name": "GOOGLE_API_KEY", "label": "Google API Key"},
            {"name": "TAVILY_API_KEY", "label": "Tavily API Key"}
        ])

    def analyze(self, product_name, product_description, target_countries):
        tavily = TavilyClient(api_key=self.get_api_key("TAVILY_API_KEY"))
        results = []
        for country in target_countries:
            query = f"best go-to-market strategies, entry channels, and partnership opportunities for {product_name} in {country} 2024"
            search = tavily.search(query=query, max_results=2)
            summary = search['results'][0]['content'] if search['results'] else 'No data found.'
            results.append(f"**{country}**: {summary}")
        return "\n\n".join(results) 