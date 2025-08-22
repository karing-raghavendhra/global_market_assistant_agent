from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any
import json
from datetime import datetime
from config import *

class MarketAnalysisInput(BaseModel):
    product_name: str = Field(description="Name of the product to analyze")
    product_description: str = Field(description="Description of the product", default="")
    target_countries: List[str] = Field(description="List of target countries", default=["Germany", "UAE", "Canada"])

class GlobalMarketEntryAgent:
    def __init__(self):
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
        
        # Initialize Tavily search tool
        self.search_tool = TavilySearchResults(
            api_key=TAVILY_API_KEY,
            max_results=5
        )
        
        # Create tools
        self.tools = [
            self.search_tool,
            self._get_hs_code_tool(),
            self._analyze_market_tool(),
            self._get_tariff_info_tool(),
            self._get_competitor_analysis_tool(),
            self._generate_recommendations_tool(),
            self._translate_product_tool(),
            self._get_government_incentives_tool()
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Global Market Entry Analyst. Your role is to help businesses expand internationally by providing comprehensive market analysis, competitive intelligence, and strategic recommendations.

Key capabilities:
1. Product classification and HS code identification
2. Market size and growth potential analysis
3. Competitor analysis and pricing intelligence
4. Tariff and regulatory compliance assessment
5. Entry strategy recommendations
6. Government incentive identification
7. Product localization and translation

Always provide actionable, data-driven insights with specific recommendations."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    @tool
    def _get_hs_code_tool(self):
        """Determine the appropriate HS code for a product"""
        def get_hs_code(product_name: str, description: str = "") -> str:
            prompt = f"""
            Analyze this product and determine the most appropriate HS code:
            Product: {product_name}
            Description: {description}
            
            Available mappings: {HS_CODE_MAPPING}
            
            Return only the HS code in format: "XXXXXX"
            If not found in mappings, analyze the product and suggest the most appropriate HS code.
            """
            
            response = self.llm.invoke(prompt)
            hs_code = response.content.strip()
            
            # Fallback to mapping if AI doesn't return valid format
            if len(hs_code) != 6 or not hs_code.isdigit():
                for key, code in HS_CODE_MAPPING.items():
                    if key.lower() in product_name.lower():
                        return code
                return "960321"  # Default to toothbrush code
            
            return hs_code
        
        return get_hs_code
    
    @tool
    def _analyze_market_tool(self):
        """Analyze market potential for a product in specific countries"""
        def analyze_market(product_name: str, hs_code: str, countries: List[str]) -> Dict[str, Any]:
            market_data = {}
            
            for country in countries:
                # Get market size
                market_size_query = f"market size {product_name} sustainable eco-friendly {country} 2024"
                market_size_results = self.search_tool.invoke(market_size_query)
                
                # Get tariff info
                tariff_query = f"tariff rate HS code {hs_code} {country} 2024 import duty"
                tariff_results = self.search_tool.invoke(tariff_query)
                
                # Get competitor info
                competitor_query = f"competitors {product_name} sustainable {country} Amazon marketplace"
                competitor_results = self.search_tool.invoke(competitor_query)
                
                market_data[country] = {
                    "market_size": self._analyze_search_results(market_size_results, f"market size for {product_name} in {country}"),
                    "tariff_rate": self._analyze_search_results(tariff_results, f"tariff rate for HS code {hs_code} in {country}"),
                    "competitors": self._analyze_search_results(competitor_results, f"competitors for {product_name} in {country}"),
                    "entry_channels": self._get_entry_channels(country),
                    "regulations": self._get_regulations(product_name, country),
                    "incentives": GOVERNMENT_INCENTIVES.get(country, {})
                }
            
            return market_data
        
        return analyze_market
    
    @tool
    def _get_tariff_info_tool(self):
        """Get detailed tariff information for a product in specific countries"""
        def get_tariff_info(hs_code: str, country: str) -> Dict[str, Any]:
            search_query = f"tariff rate HS code {hs_code} {country} 2024 import duty customs"
            results = self.search_tool.invoke(search_query)
            
            analysis_prompt = f"""
            Based on this search data, provide detailed tariff information for HS code {hs_code} in {country}:
            {results}
            
            Return a structured analysis including:
            - Tariff rate percentage
            - Any preferential trade agreements
            - Additional duties or taxes
            - Documentation requirements
            """
            
            response = self.llm.invoke(analysis_prompt)
            return {
                "country": country,
                "hs_code": hs_code,
                "analysis": response.content,
                "raw_data": results
            }
        
        return get_tariff_info
    
    @tool
    def _get_competitor_analysis_tool(self):
        """Analyze competitors for a product in specific markets"""
        def get_competitor_analysis(product_name: str, country: str) -> Dict[str, Any]:
            search_query = f"competitors {product_name} sustainable eco-friendly {country} 2024 market leaders"
            results = self.search_tool.invoke(search_query)
            
            analysis_prompt = f"""
            Based on this search data, provide a comprehensive competitor analysis for {product_name} in {country}:
            {results}
            
            Include:
            - Top 5 competitors
            - Price ranges
            - Market positioning
            - Strengths and weaknesses
            - Market share estimates
            """
            
            response = self.llm.invoke(analysis_prompt)
            return {
                "product": product_name,
                "country": country,
                "analysis": response.content,
                "raw_data": results
            }
        
        return get_competitor_analysis
    
    @tool
    def _generate_recommendations_tool(self):
        """Generate strategic recommendations based on market analysis"""
        def generate_recommendations(market_data: Dict[str, Any], product_name: str) -> Dict[str, Any]:
            prompt = f"""
            Based on this market analysis for {product_name}, generate comprehensive strategic recommendations:
            
            Market Data: {json.dumps(market_data, indent=2)}
            
            Provide detailed recommendations for:
            1. Primary target market selection and rationale
            2. Entry strategy (timeline, channels, partnerships)
            3. Pricing strategy and positioning
            4. Marketing and branding approach
            5. Risk mitigation strategies
            6. Government incentives to leverage
            7. Resource requirements and budget estimates
            8. Success metrics and KPIs
            
            Format as a structured strategic plan.
            """
            
            response = self.llm.invoke(prompt)
            return {
                "product": product_name,
                "recommendations": response.content,
                "timestamp": datetime.now().isoformat()
            }
        
        return generate_recommendations
    
    @tool
    def _translate_product_tool(self):
        """Translate product listing for target markets"""
        def translate_product(product_name: str, description: str, target_language: str = "German") -> Dict[str, str]:
            prompt = f"""
            Translate this product listing to {target_language}:
            
            Product Name: {product_name}
            Description: {description}
            
            Make it culturally appropriate for {target_language} speakers and optimize for e-commerce platforms.
            Include relevant keywords for sustainability and eco-friendly products.
            Provide both the translated name and description.
            """
            
            response = self.llm.invoke(prompt)
            return {
                "original_name": product_name,
                "original_description": description,
                "translated_name": response.content.split("\n")[0] if "\n" in response.content else response.content,
                "translated_description": response.content,
                "target_language": target_language
            }
        
        return translate_product
    
    @tool
    def _get_government_incentives_tool(self):
        """Get government incentives for export to specific countries"""
        def get_government_incentives(country: str, product_category: str = "sustainable products") -> Dict[str, Any]:
            search_query = f"government incentives export {product_category} {country} 2024"
            results = self.search_tool.invoke(search_query)
            
            analysis_prompt = f"""
            Based on this search data and our database, provide government incentives for exporting {product_category} to {country}:
            
            Search Results: {results}
            Database Incentives: {GOVERNMENT_INCENTIVES.get(country, {})}
            
            Provide a comprehensive list of:
            - Available government programs
            - Eligibility requirements
            - Application processes
            - Funding amounts
            - Contact information
            """
            
            response = self.llm.invoke(analysis_prompt)
            return {
                "country": country,
                "product_category": product_category,
                "incentives": response.content,
                "database_incentives": GOVERNMENT_INCENTIVES.get(country, {}),
                "search_results": results
            }
        
        return get_government_incentives
    
    def _analyze_search_results(self, results: List[Dict], context: str) -> str:
        """Analyze search results using LLM"""
        prompt = f"""
        Based on this search data, provide insights for: {context}
        
        Search Results: {results}
        
        Provide a concise, actionable summary.
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def _get_entry_channels(self, country: str) -> List[str]:
        """Get market entry channels for specific country"""
        channels = {
            "Germany": [
                "Amazon.de (largest e-commerce platform)",
                "EU-based distributors (BioVital, EcoTop)",
                "Direct B2B partnerships",
                "Specialty sustainable retail chains",
                "BioMarkt and other organic chains"
            ],
            "UAE": [
                "Amazon.ae",
                "Local distributors (Al Maya Group)",
                "Dubai Multi Commodities Centre",
                "Specialty organic stores",
                "Carrefour and other major retailers"
            ],
            "Canada": [
                "Amazon.ca",
                "Canadian distributors (SustainCo)",
                "Direct partnerships with retailers",
                "Eco-friendly specialty stores",
                "Loblaws and other major chains"
            ]
        }
        
        return channels.get(country, ["E-commerce platforms", "Local distributors", "Direct partnerships"])
    
    def _get_regulations(self, product_name: str, country: str) -> List[str]:
        """Get regulatory requirements for specific country"""
        regulations = {
            "Germany": [
                "EU REACH compliance required",
                "CE marking for applicable products",
                "German packaging law compliance",
                "Organic certification for eco-claims",
                "EU Ecolabel certification"
            ],
            "UAE": [
                "Emirates Authority for Standardization and Metrology (ESMA) approval",
                "Halal certification if applicable",
                "Gulf Cooperation Council (GCC) standards",
                "Dubai Municipality requirements"
            ],
            "Canada": [
                "Health Canada approval for health products",
                "Canadian Food Inspection Agency (CFIA) for food items",
                "Environment and Climate Change Canada regulations",
                "Canadian Standards Association (CSA) certification"
            ]
        }
        
        return regulations.get(country, ["Standard import regulations apply"])
    
    def analyze_product(self, product_name: str, product_description: str = "", target_countries: List[str] = None) -> Dict[str, Any]:
        """Main method to analyze a product for global market entry"""
        
        if target_countries is None:
            target_countries = ["Germany", "UAE", "Canada"]
        
        # Create input for agent
        input_data = {
            "input": f"""
            Analyze this product for global market entry:
            Product: {product_name}
            Description: {product_description}
            Target Countries: {', '.join(target_countries)}
            
            Please provide:
            1. HS code classification
            2. Market analysis for each target country
            3. Competitor analysis
            4. Strategic recommendations
            5. Government incentives
            6. Translated product listings
            """
        }
        
        # Execute agent
        result = self.agent_executor.invoke(input_data)
        
        return {
            "product_name": product_name,
            "analysis": result["output"],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_comprehensive_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a comprehensive market entry report"""
        
        prompt = f"""
        Create a professional, comprehensive market entry report based on this analysis:
        
        {json.dumps(analysis_result, indent=2)}
        
        Structure the report with:
        1. Executive Summary
        2. Market Opportunity Analysis
        3. Competitive Landscape
        4. Entry Strategy
        5. Risk Assessment
        6. Government Incentives
        7. Financial Projections
        8. Implementation Timeline
        9. Success Metrics
        10. Next Steps
        
        Format as a professional business report suitable for executive presentation.
        """
        
        response = self.llm.invoke(prompt)
        return response.content 