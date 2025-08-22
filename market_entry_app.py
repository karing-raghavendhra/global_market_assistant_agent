import streamlit as st
from langchain_agent import GlobalMarketEntryAgent
from datetime import datetime

# --- App Config ---
st.set_page_config(
    page_title="Market Entry Analyst (LangChain)",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
st.sidebar.title("🌐 Market Entry Analyst (LangChain)")
st.sidebar.markdown("""
**Instructions:**
1. Enter your product details
2. Select target countries
3. Click 'Analyze Market Entry'
4. View insights, recommendations, and download your report

_Built with LangChain, Gemini, Tavily, and Streamlit._
""")

# --- Main App ---
st.title("🌐 AI Global Market Entry Analyst (LangChain)")
st.markdown("""
Instantly discover the best global markets, competitors, tariffs, and partners for your product—powered by AI.
""")

# --- Input Form ---
with st.form("market_entry_form"):
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
    submitted = st.form_submit_button("🔍 Analyze Market Entry")

# --- Run Analysis ---
if submitted and product_name:
    with st.spinner("Analyzing global market entry opportunities. Please wait..."):
        agent = GlobalMarketEntryAgent()
        result = agent.analyze_product(product_name, product_description, target_countries)
        analysis = result["analysis"]
        timestamp = result["timestamp"]

    st.success(f"Analysis complete! (Generated: {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')})")

    # --- Results Display ---
    st.header("📊 Market Insights & Recommendations")
    st.markdown(analysis)

    # --- Downloadable Report ---
    if st.button("📄 Generate & Download Full Report"):
        with st.spinner("Generating comprehensive report..."):
            report = agent.generate_comprehensive_report(result)
        st.download_button(
            label="Download Market Entry Report (PDF)",
            data=report,
            file_name=f"market_entry_report_{product_name.replace(' ', '_')}.txt",
            mime="text/plain"
        )

elif submitted and not product_name:
    st.error("Please enter a product name to proceed.")

# --- Footer ---
st.markdown("""
---
:rocket: _Demo MVP. For feedback or custom solutions, contact us!_
""") 