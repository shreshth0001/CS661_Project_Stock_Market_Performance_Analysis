import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import glob
import os
from typing import List, Dict, Tuple
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock & Macro Data Visualization",
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
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_stock_data(data_path: str = "data/processed") -> Dict[str, pd.DataFrame]:
    """Load all stock CSV files from the specified directory."""
    stock_files = glob.glob(os.path.join(data_path, "*.csv"))
    stock_data = {}
    
    for file_path in stock_files:
        ticker = os.path.basename(file_path).replace('.csv', '')
        try:
            df = pd.read_csv(file_path)
            
            # Check if we have the required columns
            required_cols = ['Close', 'High', 'Low', 'Open', 'Volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                continue
            
            # Handle the date column - based on your CSV structure
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            else:
                # From your CSV image, it looks like the first column might be an index
                # Let's try to use the first column as date or create a date range
                first_col = df.columns[0]
                
                # Check if first column looks like a date
                if 'date' in first_col.lower():
                    df[first_col] = pd.to_datetime(df[first_col])
                    df.set_index(first_col, inplace=True)
                else:
                    # If no date column, create dates based on row count
                    # Assuming daily data starting from a reasonable date
                    start_date = '1999-01-01'  # Based on your sample data
                    df['Date'] = pd.date_range(start=start_date, periods=len(df), freq='D')
                    df.set_index('Date', inplace=True)
            
            stock_data[ticker] = df
            
        except Exception as e:
            continue
    
    return stock_data

@st.cache_data
def load_macro_data(macro_path: str = "data/Daily_macro_interpolate_data.csv") -> pd.DataFrame:
    """Load macroeconomic data from CSV file."""
    try:
        df = pd.read_csv(macro_path)
        
        # Use the Date column from the CSV
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        else:
            # Assume first column is date
            date_col = df.columns[0]
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
        
        return df
        
    except Exception as e:
        # Return dummy data for demonstration
        dates = pd.date_range(start='1980-01-01', end='2024-01-01', freq='D')
        return pd.DataFrame({
            'GDP_Growth_Rate': np.random.normal(2, 0.5, len(dates)),
            'Inflation_Rate': np.random.normal(3, 1, len(dates)),
            'Unemployment_Rate': np.random.normal(5, 1, len(dates)),
            'Fed_Funds_Rate': np.random.normal(2.5, 0.8, len(dates))
        }, index=dates)

def calculate_value_proxy(df: pd.DataFrame) -> pd.Series:
    """Calculate value traded proxy: (Close - Open) * Volume."""
    return (df['Close'] - df['Open']) * df['Volume']

def calculate_gdp_growth_rate(gdp_series: pd.Series) -> pd.Series:
    """Calculate daily GDP growth rate from GDP levels."""
    return gdp_series.pct_change() * 100

def calculate_inflation_rate(cpi_series: pd.Series) -> pd.Series:
    """Calculate daily inflation rate from CPI levels."""
    return cpi_series.pct_change() * 100

def calculate_unemployment_rate(unemployment_series: pd.Series) -> pd.Series:
    """Return unemployment rate as is (already in percentage)."""
    return unemployment_series

def calculate_fed_funds_rate(fed_funds_series: pd.Series) -> pd.Series:
    """Return fed funds rate as is (already in percentage)."""
    return fed_funds_series

def create_dual_plot(stock_data: pd.Series, macro_data: pd.Series, 
                    stock_name: str, macro_name: str, 
                    date_range: Tuple[datetime, datetime]) -> go.Figure:
    """Create dual-axis plot with stock value proxy and macro indicator."""
    
    # Filter data based on date range - handle different date ranges properly
    start_date, end_date = date_range
    
    # Filter stock data
    stock_mask = (stock_data.index >= start_date) & (stock_data.index <= end_date)
    stock_filtered = stock_data[stock_mask]
    
    # Filter macro data
    macro_mask = (macro_data.index >= start_date) & (macro_data.index <= end_date)
    macro_filtered = macro_data[macro_mask]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f'{stock_name} - Value Traded Proxy',
            f'{macro_name}'
        ),
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    # Stock value proxy plot
    if len(stock_filtered) > 0:
        fig.add_trace(
            go.Scatter(
                x=stock_filtered.index,
                y=stock_filtered.values,
                mode='lines',
                name=f'{stock_name} Value Proxy',
                line=dict(color='#1f77b4', width=2),
                fill='tonexty' if stock_filtered.min() >= 0 else 'tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)'
            ),
            row=1, col=1
        )
    
    # Macro indicator plot
    if len(macro_filtered) > 0:
        fig.add_trace(
            go.Scatter(
                x=macro_filtered.index,
                y=macro_filtered.values,
                mode='lines',
                name=f'{macro_name}',
                line=dict(color='#ff7f0e', width=2),
                fill='tonexty',
                fillcolor='rgba(255, 127, 14, 0.1)'
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Stock Value Proxy vs Macro Indicator Analysis",
            x=0.5,
            font=dict(size=24, color='#1f77b4')
        ),
        height=700,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Update x-axes
    fig.update_xaxes(
        title_text="Date",
        row=2, col=1,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray'
    )
    
    # Update y-axes
    fig.update_yaxes(
        title_text="Value Traded Proxy ($)",
        row=1, col=1,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray'
    )
    
    fig.update_yaxes(
        title_text=macro_name,
        row=2, col=1,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray'
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Stock & Macroeconomic Data Visualization</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        stock_data = load_stock_data()
        macro_data = load_macro_data()
    
    if not stock_data:
        st.error("No stock data found. Please check your data directory path.")
        st.stop()
    
    # Main controls (moved from sidebar)
    st.header("🔧 Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Stock selection
        available_stocks = list(stock_data.keys())
        selected_stock = st.selectbox(
            "Select Stock Ticker:",
            available_stocks,
            index=0 if available_stocks else None
        )
    
    with col2:
        # Macro variable selection - using specific indicators instead of variance
        macro_indicators = ['GDP_Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate', 'Fed_Funds_Rate']
        # Filter only available indicators from the data
        available_indicators = [ind for ind in macro_indicators if ind in macro_data.columns]
        # Also check for GDP and CPI columns that might have different names
        for col in macro_data.columns:
            if 'GDP' in col.upper() and col not in available_indicators:
                available_indicators.append(col)
            elif 'CPI' in col.upper() and col not in available_indicators:
                available_indicators.append(col)
            elif 'UNEMPLOYMENT' in col.upper() and col not in available_indicators:
                available_indicators.append(col)
            elif 'FED' in col.upper() and 'FUNDS' in col.upper() and col not in available_indicators:
                available_indicators.append(col)
        
        if not available_indicators:
            available_indicators = macro_data.columns.tolist()
        
        selected_macro = st.selectbox(
            "Select Macroeconomic Indicator:",
            available_indicators,
            index=0 if available_indicators else None
        )
    
    with col3:
        # Date range selection
        if selected_stock in stock_data:
            stock_df = stock_data[selected_stock]
            min_date = stock_df.index.min().date()
            max_date = stock_df.index.max().date()
            
            start_date = st.date_input(
                "Start Date:",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
            
            end_date = st.date_input(
                "End Date:",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )
    
    # Main content area (moved outside column structure)
    if selected_stock in stock_data and start_date <= end_date:
        stock_df = stock_data[selected_stock]
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate metrics
        stock_df_filtered = stock_df[
            (stock_df.index.date >= start_date) & 
            (stock_df.index.date <= end_date)
        ]
        
        value_proxy = calculate_value_proxy(stock_df_filtered)
        
        # Calculate appropriate macro indicator based on selection
        if selected_macro == 'GDP' or 'GDP' in selected_macro:
            macro_indicator = calculate_gdp_growth_rate(macro_data[selected_macro])
        elif selected_macro == 'CPI' or 'CPI' in selected_macro:
            macro_indicator = calculate_inflation_rate(macro_data[selected_macro])
        elif selected_macro == 'Unemployment_Rate' or 'UNEMPLOYMENT' in selected_macro.upper():
            macro_indicator = calculate_unemployment_rate(macro_data[selected_macro])
        elif selected_macro == 'Fed_Funds_Rate' or ('FED' in selected_macro.upper() and 'FUNDS' in selected_macro.upper()):
            macro_indicator = calculate_fed_funds_rate(macro_data[selected_macro])
        else:
            macro_indicator = macro_data[selected_macro]
        
        # Display key metrics
        with col1:
            st.metric(
                "📊 Selected Stock",
                selected_stock,
                f"{len(stock_df_filtered)} trading days"
            )
        
        with col2:
            avg_value = value_proxy.mean()
            st.metric(
                "💰 Avg Value Proxy",
                f"${avg_value:,.0f}",
                f"±${value_proxy.std():,.0f}"
            )
        
        with col3:
            macro_filtered = macro_indicator[
                (macro_indicator.index.date >= start_date) & 
                (macro_indicator.index.date <= end_date)
            ]
            avg_macro = macro_filtered.mean()
            
            # Determine display format based on indicator type
            if selected_macro == 'GDP' or 'GDP' in selected_macro:
                metric_label = f"📈 Avg Daily GDP Growth"
                metric_value = f"{avg_macro:.4f}%"
                metric_delta = f"±{macro_filtered.std():.4f}%"
            elif selected_macro == 'CPI' or 'CPI' in selected_macro:
                metric_label = f"📈 Avg Daily Inflation Rate"
                metric_value = f"{avg_macro:.4f}%"
                metric_delta = f"±{macro_filtered.std():.4f}%"
            elif selected_macro == 'Unemployment_Rate' or 'UNEMPLOYMENT' in selected_macro.upper():
                metric_label = f"📈 Avg Unemployment Rate"
                metric_value = f"{avg_macro:.2f}%"
                metric_delta = f"±{macro_filtered.std():.2f}%"
            elif selected_macro == 'Fed_Funds_Rate' or ('FED' in selected_macro.upper() and 'FUNDS' in selected_macro.upper()):
                metric_label = f"📈 Avg Fed Funds Rate"
                metric_value = f"{avg_macro:.2f}%"
                metric_delta = f"±{macro_filtered.std():.2f}%"
            else:
                metric_label = f"📈 Avg {selected_macro}"
                metric_value = f"{avg_macro:.2f}%"
                metric_delta = f"±{macro_filtered.std():.2f}%"
            
            st.metric(
                metric_label,
                metric_value,
                metric_delta
            )
        
        # Create and display the plot - now spans full width
        st.subheader("📊 Interactive Visualization")
        
        fig = create_dual_plot(
            value_proxy,
            macro_indicator,
            selected_stock,
            selected_macro,
            (datetime.combine(start_date, datetime.min.time()),
             datetime.combine(end_date, datetime.max.time()))
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional insights
        st.subheader("🔍 Data Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Stock Value Proxy Analysis:**")
            st.write(f"• Total trading days: {len(value_proxy)}")
            st.write(f"• Maximum value proxy: ${value_proxy.max():,.0f}")
            st.write(f"• Minimum value proxy: ${value_proxy.min():,.0f}")
            st.write(f"• Standard deviation: ${value_proxy.std():,.0f}")
        
        with col2:
            # Determine analysis section title based on indicator type
            if selected_macro == 'GDP' or 'GDP' in selected_macro:
                analysis_title = "**Daily GDP Growth Rate Analysis:**"
            elif selected_macro == 'CPI' or 'CPI' in selected_macro:
                analysis_title = "**Daily Inflation Rate Analysis:**"
            elif selected_macro == 'Unemployment_Rate' or 'UNEMPLOYMENT' in selected_macro.upper():
                analysis_title = "**Unemployment Rate Analysis:**"
            elif selected_macro == 'Fed_Funds_Rate' or ('FED' in selected_macro.upper() and 'FUNDS' in selected_macro.upper()):
                analysis_title = "**Fed Funds Rate Analysis:**"
            else:
                analysis_title = f"**{selected_macro} Analysis:**"
            
            st.markdown(analysis_title)
            macro_clean = macro_filtered.dropna()
            st.write(f"• Data points: {len(macro_clean)}")
            if selected_macro == 'GDP' or 'GDP' in selected_macro or selected_macro == 'CPI' or 'CPI' in selected_macro:
                st.write(f"• Maximum: {macro_clean.max():.4f}%")
                st.write(f"• Minimum: {macro_clean.min():.4f}%")
                st.write(f"• Mean: {macro_clean.mean():.4f}%")
            else:
                st.write(f"• Maximum: {macro_clean.max():.2f}%")
                st.write(f"• Minimum: {macro_clean.min():.2f}%")
                st.write(f"• Mean: {macro_clean.mean():.2f}%")
        
        # Correlation analysis
        if len(value_proxy) > 0 and len(macro_indicator) > 0:
            # Align data by date
            aligned_data = pd.DataFrame({
                'value_proxy': value_proxy,
                'macro_indicator': macro_indicator
            }).dropna()
            
            if len(aligned_data) > 1:
                correlation = aligned_data['value_proxy'].corr(aligned_data['macro_indicator'])
                st.subheader("🔗 Correlation Analysis")
                
                # Determine correlation description based on indicator type
                if selected_macro == 'GDP' or 'GDP' in selected_macro:
                    correlation_desc = f"Correlation between {selected_stock} value proxy and daily GDP growth rate: **{correlation:.4f}**"
                elif selected_macro == 'CPI' or 'CPI' in selected_macro:
                    correlation_desc = f"Correlation between {selected_stock} value proxy and daily inflation rate: **{correlation:.4f}**"
                elif selected_macro == 'Unemployment_Rate' or 'UNEMPLOYMENT' in selected_macro.upper():
                    correlation_desc = f"Correlation between {selected_stock} value proxy and unemployment rate: **{correlation:.4f}**"
                elif selected_macro == 'Fed_Funds_Rate' or ('FED' in selected_macro.upper() and 'FUNDS' in selected_macro.upper()):
                    correlation_desc = f"Correlation between {selected_stock} value proxy and Fed funds rate: **{correlation:.4f}**"
                else:
                    correlation_desc = f"Correlation between {selected_stock} value proxy and {selected_macro}: **{correlation:.4f}**"
                
                st.write(correlation_desc)
                
                if abs(correlation) > 0.3:
                    strength = "Strong" if abs(correlation) > 0.7 else "Moderate"
                    direction = "positive" if correlation > 0 else "negative"
                    st.info(f"There appears to be a {strength.lower()} {direction} correlation between the variables.")
    else:
        st.error("End date must be after start date.")
    
    # Footer
    st.markdown("---")
    

if __name__ == "__main__":
    main()