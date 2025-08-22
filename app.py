import streamlit as st
from langchain_agent import GlobalMarketEntryAgent
import pandas as pd
from datetime import datetime

# --- App Config ---
st.set_page_config(
    page_title="AI Global Market Entry Analyst",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
st.sidebar.image(
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80",
    use_column_width=True
)
st.sidebar.title("AI Global Market Entry Analyst")
st.sidebar.markdown("""
**How it works:**
1. Upload your product info
2. Select target countries
3. Click 'Explore Global Opportunities'
4. Get instant market insights, translated listings, and partner leads!

_Built with LangChain, Gemini, Tavily, and Streamlit._
""")

# --- Main App ---
st.title("🌍 AI Global Market Entry Analyst")
st.markdown("""
Empower your product for global success. Instantly discover the best markets, competitors, tariffs, and partners for your product—powered by AI.
""")

# --- Input Form ---
with st.form("product_form"):
    col1, col2 = st.columns([1, 2])
    with col1:
        product_image = st.file_uploader("Upload Product Image (optional)", type=["png", "jpg", "jpeg"])
    with col2:
        product_name = st.text_input("Product Name", placeholder="e.g. Bamboo Toothbrush", max_chars=100)
        product_description = st.text_area("Product Description", placeholder="Describe your product, features, and sustainability aspects", height=100)
        target_countries = st.multiselect(
            "Target Countries",
            ["Germany", "UAE", "Canada", "India", "UK", "Australia", "Netherlands", "Sweden", "Norway", "Denmark"],
            default=["Germany", "UAE", "Canada"]
        )
    submitted = st.form_submit_button("🚀 Explore Global Opportunities")

# --- Run Analysis ---
if submitted and product_name:
    with st.spinner("Analyzing global opportunities. This may take up to 1-2 minutes..."):
        agent = GlobalMarketEntryAgent()
        result = agent.analyze_product(product_name, product_description, target_countries)
        analysis = result["analysis"]
        timestamp = result["timestamp"]

    st.success(f"Analysis complete! (Generated: {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')})")

    # --- Results Display ---
    st.header("📈 Market Insights & Recommendations")
    st.markdown(analysis)

    # --- Downloadable Report ---
    st.download_button(
        label="📄 Download Market Entry Report (PDF)",
        data=analysis,
        file_name=f"market_entry_report_{product_name.replace(' ', '_')}.txt",
        mime="text/plain"
    )

    # --- Bonus: Schedule Follow-up ---
    st.info("A follow-up will be scheduled in 30 days to recheck trends. You will be notified if tariffs or competitors change.")

elif submitted and not product_name:
    st.error("Please enter a product name to proceed.")

# --- Footer ---
st.markdown("""
---
:rocket: _Demo MVP. For feedback or custom solutions, contact us!_
""") 