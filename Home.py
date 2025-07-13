import streamlit as st
import os
import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="NASDAQ Financial Analytics Dashboard | CS661 IITK",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
current_dir = Path(__file__).parent
img_path = current_dir / "data" / "stock_bg.jpg"
with open(img_path, "rb") as f:
    img_data = base64.b64encode(f.read()).decode()


# Simplified Custom CSS for better compatibility
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap');
    .main {{
        font-family: 'Montserrat','Inter', sans-serif;
    }}

    .stApp {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(20, 30, 50, 0.65);  /* Adjust the last value (0.65) for darkness */
    z-index: 0;
    pointer-events: none;
    }}

    .stApp > div {{
        position: relative;
        z-index: 1;
    }}

    section[data-testid="stSidebar"] {{
      background: #232946;
      color: #fff;
      
    }}

    /* CSS hack: Move the first sidebar block to the top */
    section[data-testid="stSidebar"] > div:first-child {{
        order: -1;
    }}



    


    
    .hero-section {{
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        
    }}
    
    .hero-title {{  
        font-family: 'Montserrat', 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        text-align: center;
    }}
    
    .hero-subtitle {{
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 2rem;
    }}
    
    .hero-description {{
        font-size: 1.2rem;
        opacity: 0.8;
        max-width: 800px;
        text-align: center;
    }}


    .stat-card-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 5rem;
    }}
    
    .stat-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        margin: 1rem 2rem;
        width: 200px;         
        height: 200px;        
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: block;
    }}
    
    .stat-label {{
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 400;
    }}
    
    .feature-card {{
        # background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        background: black;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-top: 4px solid #667eea;
    }}
    
    .feature-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }}
    
    .feature-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
    }}
    
    .feature-description {{
        color: #4a5568;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }}
    
    .methodology-section {{
        # background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        background: black;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 3rem 0;
        border: 1px solid #e2e8f0;
    }}
    
    .methodology-card {{
        background: black;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        # border-left: 5px solid #667eea;
        margin: 1rem 0;
    }}
    
    .team-section {{
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 3rem 0;
        text-align: center;
        color: #2d3748;
    }}
    
    .section-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
        text-align: center;
    }}
    
    .section-subtitle {{
        font-size: 1.2rem;
        color: #B3C7F7;
        text-align: center;
        margin-bottom: 2rem;
    }}

    
    
    .innovation-badge {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)



with st.sidebar:
    st.markdown("<h2 style='margin-bottom: 1.5rem;'>NAVIGATION</h2>", unsafe_allow_html=True)
    

# st.markdown("""
# <h1 class="hero-title"> Welcome to the Stock Market Analyzer</h1>
# """, unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title"> NASDAQ Financial Analytics Dashboard</h1>
    <p class="hero-subtitle">Advanced Market Intelligence </p>
    <p class="hero-description", style="text-align: center;">
        A comprehensive financial data visualization suite developed for CS661 at IIT Kanpur, 
        featuring algorithms, multi-dimensional analysis, and interactive insights 
        into America's financial markets.
    </p>
</div>
""", unsafe_allow_html=True)

# Statistics Section
st.markdown('<h2 class="section-title"> Platform Statistics</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Comprehensive market coverage with unprecedented data depth</p>', unsafe_allow_html=True)

# Using Streamlit columns for better compatibility
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">1,700+</div>
        <div class="stat-label">Top NASDAQ Companies</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">50M+</div>
        <div class="stat-label">OHLCV Data Points</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">1954-2024</div>
        <div class="stat-label">Historical Data Range</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">11 Major</div>
        <div class="stat-label">Market Sectors</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">50 States</div>
        <div class="stat-label">Geographic Coverage</div>
    </div>
    """, unsafe_allow_html=True)

# Data Sources and Methodology
st.markdown("""
<div class="methodology-section">
    <h2 class="section-title">🔬 Advanced Data Integration & Methodology</h2>
    <p class="section-subtitle">
        Our platform leverages sophisticated data fusion techniques to create a unified analytical framework
    </p>
</div>
""", unsafe_allow_html=True)

# Using columns for methodology cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="methodology-card">
        <h3> Historical Stock Data</h3>
        <p>Complete OHLCV datasets for 1,700+ NASDAQ companies spanning from IPO dates to present, with advanced data cleaning and validation algorithms ensuring 99.9% accuracy.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="methodology-card">
        <h3> Macroeconomic Intelligence</h3>
        <p>70+ years of comprehensive macroeconomic data (1954-2024) including GDP, inflation rates, employment metrics, and monetary policy indicators for advanced correlation analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="methodology-card">
        <h3> Geographic Mapping</h3>
        <p>Precise company location data with zip code-level accuracy, enabling state-wise sector concentration analysis and regional economic pattern identification.</p>
    </div>
    """, unsafe_allow_html=True)

# Main Features Section
st.markdown('<h2 class="section-title"> Advanced Analytics Suite</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Four powerful modules delivering comprehensive market insights</p>', unsafe_allow_html=True)

# Feature cards using columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🗺️</span>
        <h3 class="feature-title">Interactive Sector Heatmap</h3>
        <p class="feature-description">
        </p>
        <p><strong>Key Features:</strong></p>
        <ul>
            <li>Dynamic sector filtering with real-time updates</li>
            <li>Market cap-weighted concentration metrics</li>
            <li>Interactive state-level exploration</li>
            <li>Cross-sector comparative analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">💰</span>
        <h3 class="feature-title">Money Flow Dynamics Tracker</h3>
        <p class="feature-description">
        </p>
        <p><strong>Key Features:</strong></p>
        <ul>
            <li>Monthly sector performance heatmaps</li>
            <li>Volume-weighted flow calculations</li>
            <li>Trend persistence analysis</li>
            <li>Top performer identification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <h3 class="feature-title">Stock-Macro Correlation Engine</h3>
        <p class="feature-description">
        </p>
        <p><strong>Key Features:</strong></p>
        <ul>
            <li>Real-time correlation coefficient calculations</li>
            <li>Multi-timeframe analysis capabilities</li>
            <li>Statistical significance testing</li>
            <li>Interactive date range optimization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">⚡</span>
        <h3 class="feature-title">Fear & Volatility Analysis Wizard</h3>
        <p class="feature-description">
        </p>
        <p><strong>Key Features:</strong></p>
        <ul>
            <li>Multi-dimensional volatility calculations</li>
            <li>Greed & Fear scatter plot analysis</li>
            <li>Current trend status indicators</li>
            <li>Comprehensive correlation matrices</li>
            <li>One-click data export functionality</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Innovation Highlights
st.markdown("""
<div style="text-align: center; margin: 3rem 0;">
    <h2 class="section-title"> Technical Innovation Highlights</h2>
    <div style="margin: 2rem 0;">
        <span class="innovation-badge">Advanced Statistical Modeling</span>
        <span class="innovation-badge">Interactive Visualizations</span>
        <span class="innovation-badge">Multi-source Data Fusion</span>
        <span class="innovation-badge">Correlation Analysis</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Section
st.markdown('<h2 class="section-title">🧭 Explore Our Platform</h2>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Navigate to any module to begin your analytical journey</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Sector Heatmap", key="nav1", help="Geographic sector concentration analysis"):
        st.page_link("pages/1_State-Sector_Heatmap.py",label="🎯 Navigate to: Interactive Sector Concentration Heatmap")
        st.info("Explore how different sectors are geographically distributed across US states")

with col2:
    if st.button("Stock-Macro Analysis", key="nav2", help="Integrated stock and macroeconomic analysis"):
        st.page_link("pages/2_Stock-Macro_Analysis.py",label="🎯 Navigate to: Stock-Macro Correlation Engine")
        st.info("Analyze relationships between stock performance and economic indicators")

with col3:
    if st.button("Sector-Macro Analysis", key="nav3", help="Sector money flow analysis"):
        st.page_link("pages/3_Sector-Macro_Analysis.py",label="🎯 Navigate to: Money Flow Dynamics Tracker")
        st.info("Track capital movements and identify market trends across sectors")

with col4:
    if st.button("Risk Analysis Wizard", key="nav4", help="Fear, volatility, and trend analysis"):
        st.page_link("pages/4_Risk_Analysis_Wizard.py",label="🎯 Navigate to: Fear & Volatility Analysis Wizard")
        st.info("Comprehensive risk assessment with greed/fear sentiment analysis")

# Team and Course Section
st.markdown("""
<div class="team-section">
    <h2> CS661 - Big Data and Visual Analytics Project</h2>
    <h3>Indian Institute of Technology Kanpur</h3>
    <p style="font-size: 1.3rem; margin: 2rem 0; font-weight: 500;">
        This comprehensive financial analytics platform represents the pinnacle of our academic journey, 
        combining theoretical rigor with practical innovation to deliver a world-class analytical solution.
    </p>
    <div style="margin: 2rem 0;">
        <p style="font-size: 1.1rem; margin-bottom: 1rem;"><strong> Project Achievements:</strong></p>
        <p style="font-size: 1rem; line-height: 1.6;">
            • Multi-dimensional data integration from diverse financial sources<br>
            • Advanced correlation analysis with statistical significance testing<br>
            • Geospatial information for sector concentration mapping<br>
            • Comprehensive risk assessment with sentiment analysis<br>
        </p>
    </div>

</div>
""", unsafe_allow_html=True)

# Footer Call-to-Action
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           padding: 3rem 2rem; border-radius: 20px; text-align: center; 
           color: white; margin: 3rem 0; box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);">
    <h3 style="font-size: 2rem; margin-bottom: 1rem; font-weight: 700;">
         Ready to Explore Advanced Financial Analytics?
    </h3>
    <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">
        Discover insights that drive investment decisions and market understanding
    </p>
    <p style="font-size: 1rem; opacity: 0.8;">
        Select any module from above to begin your analytical journey through America's financial markets
    </p>
</div>
""", unsafe_allow_html=True)

