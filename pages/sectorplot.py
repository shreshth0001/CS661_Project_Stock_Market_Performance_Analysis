import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pickle
import os
from datetime import datetime, timedelta
import time
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Financial Market Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
    }
    .metric-card h4 {
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .correlation-positive {
        color: #00ff88;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .correlation-negative {
        color: #ff6b6b;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .correlation-neutral {
        color: #ffd93d;
        font-weight: bold;
        font-size: 1.3rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all required data files"""
    try:
        # Load stock info
        with open('data/stock_info.pkl', 'rb') as f:
            stock_info_dict = pickle.load(f)
        
        # Convert dictionary to DataFrame
        stock_info_data = []
        for ticker, info in stock_info_dict.items():
            if len(info) >= 3 and info[2] is not None:  # Ensure we have at least 3 elements and sector is not None
                stock_info_data.append({
                    'ticker': ticker,
                    'zip_code': info[0],
                    'city': info[1],
                    'sector': info[2]
                })
        
        stock_info = pd.DataFrame(stock_info_data)
        
        # Remove any remaining None values in sector column
        stock_info = stock_info.dropna(subset=['sector'])
        
        # Load macro data
        macro_data = pd.read_csv('data/Daily_macro_interpolate_data.csv')
        macro_data['Date'] = pd.to_datetime(macro_data['Date'])
        
        # Load processed stock data
        stock_data = {}
        processed_dir = 'data/processed'
        
        for file in os.listdir(processed_dir):
            if file.endswith('.csv'):
                ticker = file.replace('.csv', '')
                df = pd.read_csv(os.path.join(processed_dir, file))
                df['Date'] = pd.to_datetime(df['Date'])
                stock_data[ticker] = df
        
        return stock_info, macro_data, stock_data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def calculate_sector_value_proxy(stock_data, stock_info, sector, start_date, end_date):
    """Calculate value proxy for a sector"""
    # Convert dates to pandas datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    sector_stocks = stock_info[stock_info['sector'] == sector]['ticker'].tolist()
    sector_data = []
    
    for ticker in sector_stocks:
        if ticker in stock_data:
            df = stock_data[ticker].copy()
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df['value_proxy'] = (df['Close'] - df['Open']) * df['Volume']
            df['ticker'] = ticker
            sector_data.append(df[['Date', 'value_proxy', 'ticker']])
    
    if sector_data:
        combined_df = pd.concat(sector_data, ignore_index=True)
        daily_sector_value = combined_df.groupby('Date')['value_proxy'].sum().reset_index()
        daily_sector_value = daily_sector_value.rename(columns={'Date': 'date'})
        return daily_sector_value
    return pd.DataFrame()

def calculate_all_sectors_value_proxy(stock_data, stock_info, start_date, end_date):
    """Calculate value proxy for all sectors"""
    # Convert dates to pandas datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    sectors = stock_info['sector'].unique()
    all_sector_data = []
    
    for sector in sectors:
        sector_value = calculate_sector_value_proxy(stock_data, stock_info, sector, start_date, end_date)
        if not sector_value.empty:
            sector_value['sector'] = sector
            all_sector_data.append(sector_value)
    
    if all_sector_data:
        return pd.concat(all_sector_data, ignore_index=True)
    return pd.DataFrame()

def process_macro_data(macro_data, macro_variable, start_date, end_date):
    """Process macro data based on variable type"""
    # Convert dates to pandas datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    df = macro_data[(macro_data['Date'] >= start_date) & (macro_data['Date'] <= end_date)].copy()
    
    if macro_variable == 'GDP':
        df['processed_value'] = df['GDP'].pct_change() * 100
        df['processed_value'] = df['processed_value'].fillna(0)
        label = 'Daily GDP Growth Rate (%)'
    elif macro_variable == 'CPI':
        df['processed_value'] = df['CPI'].pct_change() * 100
        df['processed_value'] = df['processed_value'].fillna(0)
        label = 'Daily Inflation Rate (%)'
    elif macro_variable == 'Unemployment Rate':
        df['processed_value'] = df['Unemployment Rate']
        label = 'Unemployment Rate (%)'
    elif macro_variable == 'Fed Funds Rate':
        df['processed_value'] = df['Fed Funds Rate']
        label = 'Fed Funds Rate (%)'
    else:
        df['processed_value'] = df[macro_variable]
        label = macro_variable
    
    return df[['Date', 'processed_value']], label

def create_sector_heatmap_visualization(all_sector_data, start_date, end_date):
    """Create an interactive sector performance heatmap with monthly data"""
    # Add month information to the data
    all_sector_data['month'] = all_sector_data['date'].dt.to_period('M')
    
    # Group by month and sector, then sum the value_proxy
    monthly_aggregated = all_sector_data.groupby(['month', 'sector'])['value_proxy'].sum().reset_index()
    
    if monthly_aggregated.empty:
        return None, None
    
    # Create pivot table for heatmap
    heatmap_data = monthly_aggregated.pivot(index='sector', columns='month', values='value_proxy')
    heatmap_data = heatmap_data.fillna(0)
    
    # Convert month periods to strings for better display
    heatmap_data.columns = [str(col) for col in heatmap_data.columns]
    
    # Calculate percentile ranks for color scaling (0-100 scale)
    heatmap_data_normalized = heatmap_data.rank(pct=True) * 100
    
    # Create custom hover text with actual values
    hover_text = []
    for i, sector in enumerate(heatmap_data.index):
        hover_row = []
        for j, month in enumerate(heatmap_data.columns):
            value = heatmap_data.iloc[i, j]
            percentile = heatmap_data_normalized.iloc[i, j]
            hover_row.append(f'<b>{sector}</b><br>Month: {month}<br>Value: {value:,.0f}<br>Percentile: {percentile:.1f}%')
        hover_text.append(hover_row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data_normalized.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        hovertemplate='%{text}<extra></extra>',
        text=hover_text,
        colorbar=dict(
            title="Performance Percentile",
            
            tickmode="array",
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0%", "25%", "50%", "75%", "100%"]
        )
    ))
    
    fig.update_layout(
        title='Interactive Sector Performance Heatmap - Monthly Value Proxy Percentiles',
        xaxis_title='Month',
        yaxis_title='Sector',
        height=max(600, len(heatmap_data.index) * 30),  # Dynamic height based on number of sectors
        xaxis={'side': 'bottom'},
        yaxis={'side': 'left'},
        font=dict(size=12)
    )
    
    # Calculate summary statistics for return
    summary_stats = {
        'top_performers': monthly_aggregated.groupby('sector')['value_proxy'].sum().nlargest(5),
        'most_consistent': monthly_aggregated.groupby('sector')['value_proxy'].std().nsmallest(5),
        'monthly_totals': monthly_aggregated.groupby('month')['value_proxy'].sum(),
        'sector_monthly_avg': monthly_aggregated.groupby('sector')['value_proxy'].mean().sort_values(ascending=False)
    }
    
    return fig, summary_stats

def calculate_correlation_analysis(sector_data, macro_data, sector_name, macro_variable):
    """Calculate correlation between sector and macro data"""
    if sector_data.empty or macro_data.empty:
        return None, None, None
    
    # Merge data on date
    merged_data = pd.merge(sector_data, macro_data, left_on='date', right_on='Date', how='inner')
    
    if len(merged_data) < 2:
        return None, None, None
    
    correlation, p_value = pearsonr(merged_data['value_proxy'], merged_data['processed_value'])
    
    # Determine correlation strength
    if abs(correlation) > 0.7:
        strength = "Strong"
    elif abs(correlation) > 0.3:
        strength = "Moderate"
    else:
        strength = "Weak"
    
    return correlation, p_value, strength

def main():
    st.markdown('<h1 class="main-header">📈 Financial Market Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    stock_info, macro_data, stock_data = load_data()
    
    if stock_info is None or macro_data is None or stock_data is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
   
    
    # SUBSECTION 1: Sector vs Macro Analysis
    st.markdown('<h2 class="section-header">🔍 Section 1: Sector vs Macroeconomic Analysis</h2>', unsafe_allow_html=True)
    
    # Filters for Section 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sectors = sorted(stock_info['sector'].unique())
        selected_sector = st.selectbox("Select Sector", sectors, key="sector_1")
    
    with col2:
        macro_variables = ['GDP', 'Unemployment Rate', 'CPI', 'Fed Funds Rate']
        selected_macro = st.selectbox("Select Macroeconomic Variable", macro_variables, key="macro_1")
    
    with col3:
        date_range_1 = st.date_input(
            "Select Date Range",
            value=(datetime(2020, 1, 1), datetime(2023, 12, 31)),
            min_value=datetime(2015, 1, 1),
            max_value=datetime(2024, 12, 31),
            key="date_range_1"
        )
    
    if len(date_range_1) == 2:
        start_date_1, end_date_1 = date_range_1
        
        # Calculate sector value proxy
        sector_data_1 = calculate_sector_value_proxy(stock_data, stock_info, selected_sector, start_date_1, end_date_1)
        
        # Process macro data
        macro_data_1, macro_label = process_macro_data(macro_data, selected_macro, start_date_1, end_date_1)
        
        if not sector_data_1.empty and not macro_data_1.empty:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=[f'{selected_sector} Sector Value Proxy vs Time', f'{macro_label} vs Time'],
                vertical_spacing=0.1
            )
            
            # Sector plot
            fig.add_trace(
                go.Scatter(
                    x=sector_data_1['date'],
                    y=sector_data_1['value_proxy'],
                    mode='lines+markers',
                    name=f'{selected_sector} Value Proxy',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )
            
            # Macro plot
            fig.add_trace(
                go.Scatter(
                    x=macro_data_1['Date'],
                    y=macro_data_1['processed_value'],
                    mode='lines+markers',
                    name=macro_label,
                    line=dict(color='#ff7f0e', width=2)
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=800, showlegend=True)
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Value Proxy", row=1, col=1)
            fig.update_yaxes(title_text=macro_label, row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis and insights
            st.markdown('<h3 class="section-header">📊 Analysis & Insights</h3>', unsafe_allow_html=True)
            
            # Calculate correlation
            correlation, p_value, strength = calculate_correlation_analysis(sector_data_1, macro_data_1, selected_sector, selected_macro)
            
            if correlation is not None:
                # Display correlation metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    correlation_class = "correlation-positive" if correlation > 0 else "correlation-negative"
                    st.markdown(f'<div class="metric-card"><h4>Correlation Coefficient</h4><p class="{correlation_class}">{correlation:.3f}</p></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="metric-card"><h4>Correlation Strength</h4><p class="correlation-neutral">{strength}</p></div>', unsafe_allow_html=True)
                
                with col3:
                    significance = "Significant" if p_value < 0.05 else "Not Significant"
                    st.markdown(f'<div class="metric-card"><h4>Statistical Significance</h4><p class="correlation-neutral">{significance}</p></div>', unsafe_allow_html=True)
                
                # Detailed analysis
                st.markdown("### 📈 Detailed Analysis")
                
                if abs(correlation) > 0.3:
                    direction = "positive" if correlation > 0 else "negative"
                    st.write(f"**Key Finding**: There is a {strength.lower()} {direction} correlation ({correlation:.3f}) between {selected_sector} sector performance and {selected_macro}.")
                    
                    if correlation > 0:
                        st.write(f"This suggests that when {selected_macro} increases, the {selected_sector} sector tends to perform better.")
                    else:
                        st.write(f"This suggests that when {selected_macro} increases, the {selected_sector} sector tends to perform worse.")
                else:
                    st.write(f"**Key Finding**: There is little to no correlation between {selected_sector} sector performance and {selected_macro}.")
                
                # Additional statistics
                sector_stats = sector_data_1['value_proxy'].describe()
                macro_stats = macro_data_1['processed_value'].describe()
                
                st.markdown("### 📊 Statistical Summary")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{selected_sector} Sector Statistics:**")
                    st.write(f"- Average Value Proxy: {sector_stats['mean']:,.0f}")
                    st.write(f"- Standard Deviation: {sector_stats['std']:,.0f}")
                    st.write(f"- Maximum Value: {sector_stats['max']:,.0f}")
                    st.write(f"- Minimum Value: {sector_stats['min']:,.0f}")
                
                with col2:
                    st.markdown(f"**{macro_label} Statistics:**")
                    st.write(f"- Average Value: {macro_stats['mean']:.3f}")
                    st.write(f"- Standard Deviation: {macro_stats['std']:.3f}")
                    st.write(f"- Maximum Value: {macro_stats['max']:.3f}")
                    st.write(f"- Minimum Value: {macro_stats['min']:.3f}")
    
    # SUBSECTION 2: Interactive Sector Performance Heatmap
    st.markdown('<h2 class="section-header">🔥 Section 2: Interactive Sector Performance Heatmap</h2>', unsafe_allow_html=True)
    
    # Filters for Section 2
    col1, col2 = st.columns(2)
    
    with col1:
        date_range_2 = st.date_input(
            "Select Date Range for Heatmap",
            value=(datetime(2020, 1, 1), datetime(2023, 12, 31)),
            min_value=datetime(2015, 1, 1),
            max_value=datetime(2024, 12, 31),
            key="date_range_2"
        )
    
    with col2:
        st.markdown("**🎯 Heatmap Guide:**")
        st.markdown("• **Dark colors** = High performance percentile")
        st.markdown("• **Light colors** = Low performance percentile")
        st.markdown("• **Hover** over cells for detailed values")
    
    if len(date_range_2) == 2:
        start_date_2, end_date_2 = date_range_2
        
        # Calculate all sectors data
        with st.spinner("Calculating monthly sector data for heatmap..."):
            all_sector_data = calculate_all_sectors_value_proxy(stock_data, stock_info, start_date_2, end_date_2)
        
        if not all_sector_data.empty:
            # Create heatmap visualization
            heatmap_fig, summary_stats = create_sector_heatmap_visualization(all_sector_data, start_date_2, end_date_2)
            
            if heatmap_fig is not None:
                st.plotly_chart(heatmap_fig, use_container_width=True)
                
                # Add interactive insights
                st.info("💡 **Interactive Tip**: Hover over any cell to see detailed performance data for that sector-month combination!")
                
                # Analysis for Section 2
                st.markdown('<h3 class="section-header">🎯 Heatmap Performance Analysis</h3>', unsafe_allow_html=True)
                
                # Performance insights using summary stats
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏆 Top Overall Performers")
                    for i, (sector, value) in enumerate(summary_stats['top_performers'].items()):
                        rank_emoji = ["🥇", "🥈", "🥉", "🏅", "🏅"][i]
                        st.write(f"{rank_emoji} **{sector}**: {value:,.0f}")
                
                with col2:
                    st.markdown("### 🎯 Most Consistent Performers")
                    for i, (sector, std_dev) in enumerate(summary_stats['most_consistent'].items()):
                        stability_emoji = ["🔒", "🔐", "🛡️", "⚖️", "📊"][i]
                        st.write(f"{stability_emoji} **{sector}**: σ = {std_dev:,.0f}")
                
                # Monthly performance trends
                st.markdown("### 📅 Monthly Market Activity")
                
                # Find peak performance months
                top_months = summary_stats['monthly_totals'].nlargest(5)
                st.markdown("**🔥 Highest Activity Months:**")
                for i, (month, total) in enumerate(top_months.items()):
                    st.write(f"{i+1}. **{month}**: {total:,.0f}")
                
                # Sector performance matrix insights
                st.markdown("### 🎨 Heatmap Pattern Analysis")
                
                # Calculate sector performance patterns
                all_sector_data['month'] = all_sector_data['date'].dt.to_period('M')
                monthly_pivot = all_sector_data.groupby(['month', 'sector'])['value_proxy'].sum().reset_index()
                
                # Find sectors with strongest seasonal patterns
                seasonal_analysis = {}
                for sector in all_sector_data['sector'].unique():
                    sector_data = monthly_pivot[monthly_pivot['sector'] == sector]
                    if len(sector_data) > 1:
                        monthly_values = sector_data['value_proxy'].values
                        seasonal_analysis[sector] = {
                            'coefficient_of_variation': np.std(monthly_values) / np.mean(monthly_values) if np.mean(monthly_values) != 0 else 0,
                            'max_month': sector_data.loc[sector_data['value_proxy'].idxmax(), 'month'] if not sector_data.empty else None,
                            'min_month': sector_data.loc[sector_data['value_proxy'].idxmin(), 'month'] if not sector_data.empty else None
                        }
                
                # Display seasonal insights
                if seasonal_analysis:
                    most_seasonal = max(seasonal_analysis.items(), key=lambda x: x[1]['coefficient_of_variation'])
                    least_seasonal = min(seasonal_analysis.items(), key=lambda x: x[1]['coefficient_of_variation'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🌊 Most Seasonal Sector:**")
                        sector_name, data = most_seasonal
                        st.write(f"• **{sector_name}**")
                        st.write(f"  - Seasonality Score: {data['coefficient_of_variation']:.2f}")
                        if data['max_month']:
                            st.write(f"  - Peak Month: {data['max_month']}")
                        if data['min_month']:
                            st.write(f"  - Low Month: {data['min_month']}")
                    
                    with col2:
                        st.markdown("**🎯 Most Stable Sector:**")
                        sector_name, data = least_seasonal
                        st.write(f"• **{sector_name}**")
                        st.write(f"  - Stability Score: {data['coefficient_of_variation']:.2f}")
                        st.write(f"  - Consistent across months")
                
                # Performance distribution insights
                st.markdown("### 📊 Performance Distribution Insights")
                
                # Calculate performance concentration
                total_performance = summary_stats['top_performers'].sum()
                top_3_share = summary_stats['top_performers'].head(3).sum() / total_performance * 100
                
                performance_metrics = [
                    f"🎯 **Top 3 Sectors** account for **{top_3_share:.1f}%** of total performance",
                    f"📈 **Average Monthly Performance** per sector: {summary_stats['sector_monthly_avg'].mean():,.0f}",
                    f"🏆 **Performance Leader**: {summary_stats['sector_monthly_avg'].index[0]} ({summary_stats['sector_monthly_avg'].iloc[0]:,.0f})",
                    f"📊 **Total Sectors Analyzed**: {len(summary_stats['sector_monthly_avg'])}",
                    f"⏰ **Time Period Coverage**: {len(summary_stats['monthly_totals'])} months"
                ]
                
                for metric in performance_metrics:
                    st.markdown(metric)
                
                # Interactive interpretation guide
                st.markdown("### 🔍 How to Read the Heatmap")
                
                interpretation_guide = """
                **Color Intensity Guide:**
                - **Darkest colors (90-100%)**: Top performing months for each sector
                - **Medium colors (25-75%)**: Average performance periods
                - **Lightest colors (0-25%)**: Lower performance months
                
                **Pattern Recognition:**
                - **Vertical streaks**: Sectors with consistent performance over time
                - **Horizontal streaks**: Months with widespread sector activity
                - **Isolated bright spots**: Exceptional performance events
                - **Dark regions**: Periods of sector-wide underperformance
                """
                
                st.markdown(interpretation_guide)
                
            else:
                st.warning("No data available for the selected date range.")
        else:
            st.warning("No sector data available for the selected date range.")
    else:
        st.warning("Please select both start and end dates for the heatmap.")

if __name__ == "__main__":
    main()