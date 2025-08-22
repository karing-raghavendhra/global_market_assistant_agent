import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Model Configuration
GEMINI_MODEL = "gemini-pro"
TAVILY_SEARCH_DEPTH = "advanced"

# Market Analysis Settings
SUPPORTED_COUNTRIES = [
    "Germany", "UAE", "Canada", "India", "UK", "Australia", 
    "Netherlands", "Sweden", "Norway", "Denmark"
]

# HS Code Mapping for Common Products
HS_CODE_MAPPING = {
    "bamboo toothbrush": "960321",
    "sustainable oral care": "960321",
    "eco toothbrush": "960321",
    "organic toothpaste": "330610",
    "natural soap": "340111",
    "eco-friendly packaging": "482390",
    "sustainable clothing": "620443",
    "organic food": "070190",
    "renewable energy": "850231",
    "biodegradable products": "391100"
}

# Government Incentive Programs
GOVERNMENT_INCENTIVES = {
    "India": {
        "MSME Export Promotion": "Up to 50% reimbursement on export promotion expenses",
        "Interest Equalization Scheme": "3% interest subvention on export credit",
        "Market Access Initiative": "Support for participation in international trade fairs"
    },
    "Germany": {
        "Green Technology Support": "Funding for sustainable product development",
        "Export Credit Guarantees": "Hermes cover for export financing",
        "Digital Export Initiative": "Support for e-commerce expansion"
    },
    "Canada": {
        "CanExport SMEs": "Up to $50,000 for export market development",
        "Trade Commissioner Service": "Free market intelligence and networking",
        "Green Export Initiative": "Support for sustainable product exports"
    }
} 