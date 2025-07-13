# CS661 Project: Stock Market Performance Analysis

**Course:** CSS661 – Big Data Visual Analytics (Summer 2024–2025)  
**Tech Stack:** Python 3.8+, Streamlit, pandas, NumPy, Plotly, SciPy

---

## 1. Introduction

This project is a multi‑page **Streamlit** dashboard that lets you visualize stock-market performance at the ticker and sector level—and directly compare those metrics against macroeconomic indicators (CPI, GDP growth, Fed rates). The dataset we used contains upto 1700 companies' stock tickers listed on the NASDAQ, along with the accompanying macroeconomic data. 

---

## 2. Achieved Tasks & Visualizations

1. **Market Overview**  
   - Aggregates `(Close – Open) × Volume` across all tickers  
   - Time‑series plot of that aggregate metric vs user-chosen macroeconomic data 

2. **Geographic market distribution**  
   - Select any sector from dropdown 
   - Plot its heatmap across different states of the US showing the distribution of markets across states.
   - Analyze the data and show the top 5 states and the state-wise distribution in the form of a table 

3. **Greed-Fear volatility index**  
   - Analyze each stock's greed-fear index based on multiple technical indicators such as volatility, Bollinger Bands and ATR.
   - Plot these to obtain sentiment for each stock at different points in time and classify them into different classes of greed/fear.
   - Showcase live sentiment based on the same indicators for the same stock. 

4. **Macroeconomic Sector-Wise Overlay**  
   - Contrast sector-wise performance via a proxy for value traded positively or negatively with macroeconomic performance for any user-chosen time frame.
   - Showcase a heatmap which denotes how each sector varies in terms of the value traded for a certain time frame.
   - Detail which sectors performed best, which performed worst, which were the most volatile, and which were the most stable, along with many other useful inferences based on these visualizations.


---

## 3. Datasets

- **Macro Data**  
  - Macro series: CPI (inflation), GDP movements, daily Fed funds rate, Unemployment rate
  - Calculate daily GDP growth rates, inflation, etc. from the macroeconomic data to visualize the effects of macroeconomic data better.

- **Processed Data (`data/processed/`)**
  - Daily OHLCV for each ticker from the yfinance API. 
  - Cleaned, merged, and feature‑engineered CSVs  
    - One file per metric (e.g., `AAPL_COxV.csv`, `TECH_sector_return.csv`, `US_CPI.csv`)  
  - Columns:  
    - For stocks: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, `COxV`  
    - For macros: `Date`, `Value`
- **geodat.csv**
  - It is a matrix of number of companies in sector-state combination
  - It is obtained by using zip code of stocks fetched using yfinance and then using uszip.csv to find the state from the zip code.
  ---

## 4. Prerequisites

- **Python 3.8+** installed and on your PATH  
- **Pip** for package management  

**Required Python packages** (install via pip):  
streamlit
pandas
numpy
matplotlib
plotly
scipy

---

## 5. Instructions to run

- Download the latest version of Git(probably the x64 systems version's .exe binary) for your specific OS and set it up following it's instructions.
- Use "git clone https://github.com/the-duckie-2/CS661_Project_Stock_Market_Performance_Analysis.git" to clone the project repository into an empty folder on your local system.
- Run "pip install -r requirements.txt" to install all the dependencies you will need to deploy the dashboard.
- Run "streamlit run Home.py" and the dashboard will open.
