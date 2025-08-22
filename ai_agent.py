import google.generativeai as genai
from tavily import TavilyClient
import json
import pandas as pd
from datetime import datetime, timedelta
from config import *

class GlobalMarketEntryAgent:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Initialize Tavily
        self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        
    def analyze_product(self, product_name, product_description=""):
        """Analyze product and determine HS code and market potential"""
        
        # Determine HS Code
        hs_code = self._get_hs_code(product_name, product_description)
        
        # Get market analysis
        market_data = self._analyze_global_markets(hs_code, product_name)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(market_data, product_name)
        
        return {
            "product_name": product_name,
            "hs_code": hs_code,
            "market_analysis": market_data,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_hs_code(self, product_name, description):
        """Determine HS code for the product"""
        prompt = f"""
        Analyze this product and determine the most appropriate HS code:
        Product: {product_name}
        Description: {description}
        
        Available mappings: {HS_CODE_MAPPING}
        
        Return only the HS code in format: "XXXXXX"
        If not found in mappings, analyze the product and suggest the most appropriate HS code.
        """
        
        response = self.model.generate_content(prompt)
        hs_code = response.text.strip()
        
        # Fallback to mapping if AI doesn't return valid format
        if len(hs_code) != 6 or not hs_code.isdigit():
            for key, code in HS_CODE_MAPPING.items():
                if key.lower() in product_name.lower():
                    return code
            return "960321"  # Default to toothbrush code
        
        return hs_code
    
    def _analyze_global_markets(self, hs_code, product_name):
        """Analyze global markets using Tavily search"""
        
        search_queries = [
            f"tariff rates {hs_code} Germany UAE Canada 2024",
            f"market size {product_name} sustainable eco-friendly Germany",
            f"competitor analysis {product_name} Germany Amazon.de",
            f"ESG sustainability regulations Germany {product_name}",
            f"export requirements Germany {product_name} certification",
            f"distributor networks Germany sustainable products",
            f"government incentives export Germany sustainable products"
        ]
        
        market_data = {}
        
        for country in ["Germany", "UAE", "Canada"]:
            market_data[country] = {
                "tariff_rate": self._get_tariff_rate(hs_code, country),
                "market_size": self._get_market_size(product_name, country),
                "competitors": self._get_competitors(product_name, country),
                "entry_channels": self._get_entry_channels(country),
                "regulations": self._get_regulations(product_name, country),
                "incentives": GOVERNMENT_INCENTIVES.get(country, {})
            }
        
        return market_data
    
    def _get_tariff_rate(self, hs_code, country):
        """Get tariff rate for product in specific country"""
        search_query = f"tariff rate HS code {hs_code} {country} 2024 import duty"
        
        try:
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=5
            )
            
            # Analyze search results with Gemini
            prompt = f"""
            Based on this search data, what is the approximate tariff rate for HS code {hs_code} in {country}?
            Search results: {response['results']}
            
            Return only a number (percentage) like "5.2" or "0" for duty-free.
            """
            
            result = self.model.generate_content(prompt)
            return float(result.text.strip().replace("%", "")) if result.text.strip().replace("%", "").replace(".", "").isdigit() else 5.0
            
        except Exception as e:
            print(f"Error getting tariff rate: {e}")
            return 5.0  # Default tariff rate
    
    def _get_market_size(self, product_name, country):
        """Get market size information"""
        search_query = f"market size {product_name} sustainable eco-friendly {country} 2024"
        
        try:
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=3
            )
            
            prompt = f"""
            Based on this search data, provide market size information for {product_name} in {country}:
            {response['results']}
            
            Return a brief summary of market size and growth potential.
            """
            
            result = self.model.generate_content(prompt)
            return result.text.strip()
            
        except Exception as e:
            print(f"Error getting market size: {e}")
            return f"Growing market for sustainable products in {country}"
    
    def _get_competitors(self, product_name, country):
        """Get competitor information"""
        search_query = f"competitors {product_name} sustainable {country} Amazon marketplace"
        
        try:
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=5
            )
            
            prompt = f"""
            Based on this search data, identify main competitors for {product_name} in {country}:
            {response['results']}
            
            Return a list of 3-5 main competitors with estimated price ranges.
            """
            
            result = self.model.generate_content(prompt)
            return result.text.strip()
            
        except Exception as e:
            print(f"Error getting competitors: {e}")
            return f"Competitive market with established sustainable brands in {country}"
    
    def _get_entry_channels(self, country):
        """Get market entry channels"""
        channels = {
            "Germany": [
                "Amazon.de (largest e-commerce platform)",
                "EU-based distributors (BioVital, EcoTop)",
                "Direct B2B partnerships",
                "Specialty sustainable retail chains"
            ],
            "UAE": [
                "Amazon.ae",
                "Local distributors (Al Maya Group)",
                "Dubai Multi Commodities Centre",
                "Specialty organic stores"
            ],
            "Canada": [
                "Amazon.ca",
                "Canadian distributors (SustainCo)",
                "Direct partnerships with retailers",
                "Eco-friendly specialty stores"
            ]
        }
        
        return channels.get(country, ["E-commerce platforms", "Local distributors", "Direct partnerships"])
    
    def _get_regulations(self, product_name, country):
        """Get regulatory requirements"""
        regulations = {
            "Germany": [
                "EU REACH compliance required",
                "CE marking for applicable products",
                "German packaging law compliance",
                "Organic certification for eco-claims"
            ],
            "UAE": [
                "Emirates Authority for Standardization and Metrology (ESMA) approval",
                "Halal certification if applicable",
                "Gulf Cooperation Council (GCC) standards"
            ],
            "Canada": [
                "Health Canada approval for health products",
                "Canadian Food Inspection Agency (CFIA) for food items",
                "Environment and Climate Change Canada regulations"
            ]
        }
        
        return regulations.get(country, ["Standard import regulations apply"])
    
    def _generate_recommendations(self, market_data, product_name):
        """Generate strategic recommendations"""
        
        # Find best market based on analysis
        best_market = self._find_best_market(market_data)
        
        prompt = f"""
        Based on this market analysis for {product_name}, generate strategic recommendations:
        
        Market Data: {json.dumps(market_data, indent=2)}
        Best Market: {best_market}
        
        Provide recommendations for:
        1. Primary target market and why
        2. Entry strategy (timeline, channels, partnerships)
        3. Pricing strategy
        4. Marketing approach
        5. Risk mitigation
        6. Government incentives to leverage
        
        Format as a structured recommendation report.
        """
        
        result = self.model.generate_content(prompt)
        return result.text.strip()
    
    def _find_best_market(self, market_data):
        """Find the best market based on analysis"""
        scores = {}
        
        for country, data in market_data.items():
            score = 0
            # Lower tariff is better
            tariff = data.get("tariff_rate", 5.0)
            score += (10 - min(tariff, 10)) * 2
            
            # Germany gets bonus for sustainability focus
            if country == "Germany":
                score += 5
            
            # Canada gets bonus for ease of entry
            if country == "Canada":
                score += 3
            
            scores[country] = score
        
        return max(scores, key=scores.get)
    
    def generate_report(self, analysis_result):
        """Generate comprehensive market entry report"""
        
        prompt = f"""
        Create a professional 1-page market entry report based on this analysis:
        
        {json.dumps(analysis_result, indent=2)}
        
        Include:
        1. Executive Summary
        2. Market Opportunity Analysis
        3. Competitive Landscape
        4. Entry Strategy
        5. Risk Assessment
        6. Government Incentives
        7. Next Steps
        
        Format as a professional business report.
        """
        
        result = self.model.generate_content(prompt)
        return result.text.strip()
    
    def translate_product_listing(self, product_name, description, target_language="German"):
        """Translate product listing for target market"""
        
        prompt = f"""
        Translate this product listing to {target_language}:
        
        Product Name: {product_name}
        Description: {description}
        
        Make it culturally appropriate for {target_language} speakers and optimize for e-commerce platforms.
        Include relevant keywords for sustainability and eco-friendly products.
        """
        
        result = self.model.generate_content(prompt)
        return result.text.strip()
    
    def generate_partner_list(self, target_country, product_category):
        """Generate potential partner list"""
        
        search_query = f"distributors importers {product_category} sustainable {target_country}"
        
        try:
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=10
            )
            
            prompt = f"""
            Based on this search data, create a list of potential partners for {product_category} in {target_country}:
            {response['results']}
            
            Format as a structured list with:
            - Company name
            - Contact information (if available)
            - Specialization
            - Partnership potential
            """
            
            result = self.model.generate_content(prompt)
            return result.text.strip()
            
        except Exception as e:
            print(f"Error generating partner list: {e}")
            return f"Partner research needed for {target_country} market" 