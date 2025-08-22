import streamlit as st
from market_research_agent import MarketResearchAgent
from competitive_intelligence_agent import CompetitiveIntelligenceAgent
from cultural_intelligence_agent import CulturalIntelligenceAgent
from financial_analysis_agent import FinancialAnalysisAgent
from regulatory_compliance_agent import RegulatoryComplianceAgent
from strategy_recommendation_agent import StrategyRecommendationAgent

AGENT_CLASSES = {
    "Market Research": MarketResearchAgent,
    "Competitive Intelligence": CompetitiveIntelligenceAgent,
    "Cultural Intelligence": CulturalIntelligenceAgent,
    "Financial Analysis": FinancialAnalysisAgent,
    "Regulatory Compliance": RegulatoryComplianceAgent,
    "Strategy Recommendation": StrategyRecommendationAgent,
}

st.set_page_config(
    page_title="Multi-Agent Market Entry Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🤖 Multi-Agent Market Entry Analyst")
st.sidebar.markdown("""
Select an agent, enter your product details, and analyze global opportunities from different perspectives!
""")

agent_name = st.sidebar.selectbox("Choose Analysis Agent", list(AGENT_CLASSES.keys()))
AgentClass = AGENT_CLASSES[agent_name]

st.title(f"{agent_name} - AI Market Entry Analyst")

with st.form("multi_agent_form"):
    col1, col2 = st.columns([1, 2])
    with col1:
        product_name = st.text_input("Product Name", placeholder="e.g. Bamboo Toothbrush", max_chars=100)
        product_description = st.text_area("Product Description", placeholder="Describe your product, features, and sustainability aspects", height=100)
    with col2:
        target_countries = st.multiselect(
            "Target Countries",
            ["Germany", "UAE", "Canada", "India", "UK", "Australia", "Netherlands", "Sweden", "Norway", "Denmark"],
            default=["Germany", "UAE", "Canada"]
        )
    submitted = st.form_submit_button(f"🔍 Analyze with {agent_name}")

if submitted and product_name:
    with st.spinner(f"{agent_name} is analyzing your product..."):
        agent = AgentClass()
        result = agent.analyze(product_name, product_description, target_countries)
    st.success("Analysis complete!")
    st.header("Result")
    st.markdown(result)
elif submitted and not product_name:
    st.error("Please enter a product name to proceed.")

st.markdown("""
---
:rocket: _Demo MVP. For feedback or custom solutions, contact us!_
""") 