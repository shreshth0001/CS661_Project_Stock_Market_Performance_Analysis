# CS661 Stock Market Performance Analysis

**Course:** CSS661 – Big Data Visual Analytics (Summer 2024–2025)  
**Author:** the‑duckie‑2 (Daksh)  
**Tech Stack:** Python 3.8+, Streamlit, pandas, NumPy, matplotlib/Plotly

---

## 1. Introduction

This project is a no‑bullshit, multi‑page **Streamlit** dashboard that lets you **slice and dice** stock-market performance at the ticker and sector level—and directly compare those metrics against macroeconomic indicators (CPI, GDP growth, Fed rates). No fluff, no convoluted pipelines: drop cleaned CSVs in the right folder, fire up the app, and get actionable visual insights.

---

## 2. Achieved Tasks & Visualizations

1. **Market Overview**  
   - Aggregates `(Close – Open) × Volume` across all tickers  
   - Time‑series plot of that aggregate metric  

2. **Individual Stock Analysis**  
   - Select any ticker from dropdown  
   - Plot its `(Close – Open) × Volume` over time  

3. **Sector‑Level Comparison**  
   - Group tickers by sector  
   - Plot sector‑aggregate returns and volatility  

4. **Macroeconomic Overlay**  
   - Load CPI, GDP growth rate, Fed funds rate CSVs  
   - Overlay those series on stock/sector plots for direct correlation  

5. **Dynamic Data Loading**  
   - Any CSV placed in `data/processed/` is auto‑detected and appears in the UI immediately

---

## 3. Datasets

- **Raw Data (`data/raw/`)**  
  - Daily OHLCV for each ticker (downloaded from your source of choice)  
  - Macro series: CPI (inflation), quarterly GDP growth, daily Fed funds rate  

- **Processed Data (`data/processed/`)**  
  - Cleaned, merged, and feature‑engineered CSVs  
    - One file per metric (e.g., `AAPL_COxV.csv`, `TECH_sector_return.csv`, `US_CPI.csv`)  
  - Columns:  
    - For stocks: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, `COxV`  
    - For macros: `Date`, `Value`  

> **Important:** File names must be descriptive. The app parses filenames to populate dropdowns and legends.

---

## 4. Prerequisites

- **Python 3.8+** installed and on your PATH  
- **Pip** for package management  

**Required Python packages** (install via pip):  
```bash
streamlit
pandas
numpy
matplotlib
plotly
