import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

folder_path = 'data/processed'
csv_files = [f
             for f in os.listdir(folder_path)
             if f.endswith('.csv')]

# Set page config
st.set_page_config(page_title="Stock Greed-Fear & Volatility Analysis", layout="wide")

def calculate_greed_fear_index(df):
    """
    Calculate a greed-fear index based on multiple technical indicators
    """
    # RSI (Relative Strength Index)
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    # Bollinger Bands position
    def bollinger_position(prices, period=20):
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        bb_position = (prices - lower_band) / (upper_band - lower_band)
        return bb_position
    
    # Volume surge indicator
    def volume_surge(volume, period=20):
        vol_sma = volume.rolling(window=period).mean()
        vol_ratio = volume / vol_sma
        return vol_ratio
    
    # Price momentum
    def price_momentum(prices, period=10):
        momentum = prices.pct_change(periods=period)
        return momentum
    
    # Calculate indicators
    df['RSI'] = calculate_rsi(df['Close'])
    df['BB_Position'] = bollinger_position(df['Close'])
    df['Volume_Surge'] = volume_surge(df['Volume'])
    df['Price_Momentum'] = price_momentum(df['Close'])
    
    # Normalize indicators to 0-100 scale
    df['RSI_Norm'] = df['RSI']
    df['BB_Norm'] = df['BB_Position'] * 100
    df['Volume_Norm'] = np.clip((df['Volume_Surge'] - 0.5) * 100, 0, 100)
    df['Momentum_Norm'] = np.clip((df['Price_Momentum'] + 0.1) * 500, 0, 100)
    
    # Calculate Greed-Fear Index (0 = Extreme Fear, 100 = Extreme Greed)
    df['Greed_Fear_Index'] = (
        df['RSI_Norm'] * 0.3 + 
        df['BB_Norm'] * 0.25 + 
        df['Volume_Norm'] * 0.25 + 
        df['Momentum_Norm'] * 0.2
    )
    
    return df

def calculate_sentiment_score(df):
    """
    Calculate sentiment score based on technical indicators and price action
    """
    # Price change sentiment
    df['Price_Change'] = df['Close'].pct_change()
    df['Price_Change_MA'] = df['Price_Change'].rolling(window=5).mean()
    
    # Volume-price relationship
    df['Volume_Price_Sentiment'] = np.where(
        df['Price_Change'] > 0,
        df['Volume'] / df['Volume'].rolling(window=20).mean(),
        -(df['Volume'] / df['Volume'].rolling(window=20).mean())
    )
    
    # Moving average sentiment
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_Sentiment'] = np.where(df['MA_5'] > df['MA_20'], 1, -1)
    
    # RSI sentiment
    df['RSI_Sentiment'] = np.where(
        df['RSI'] > 70, -1,  # Overbought (negative sentiment)
        np.where(df['RSI'] < 30, 1, 0)  # Oversold (positive sentiment)
    )
    
    # Bollinger Bands sentiment
    df['BB_Sentiment'] = np.where(
        df['BB_Position'] > 0.8, -1,  # Near upper band (negative)
        np.where(df['BB_Position'] < 0.2, 1, 0)  # Near lower band (positive)
    )
    
    # Combine sentiment indicators
    df['Technical_Sentiment'] = (
        df['MA_Sentiment'] * 0.3 +
        df['RSI_Sentiment'] * 0.25 +
        df['BB_Sentiment'] * 0.25 +
        np.sign(df['Price_Change_MA']) * 0.2
    )
    
    # Normalize to -100 to 100 scale
    df['Sentiment_Score'] = df['Technical_Sentiment'] * 100
    
    # Smooth the sentiment score
    df['Sentiment_Score'] = df['Sentiment_Score'].rolling(window=3).mean()
    
    return df

def calculate_volatility_metrics(df):
    """
    Calculate various volatility metrics
    """
    # Historical volatility (annualized)
    df['Returns'] = df['Close'].pct_change()
    df['Historical_Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252) * 100
    
    # Average True Range (ATR)
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    df['ATR_Percentage'] = (df['ATR'] / df['Close']) * 100
    
    # Bollinger Band width
    sma = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Width'] = (std * 4 / sma) * 100
    
    return df

def create_greed_fear_plot(df, title="Greed-Fear Index"):
    """
    Create greed-fear index plot with color coding
    """
    fig = go.Figure()
    
    # Define color conditions
    colors = []
    for value in df['Greed_Fear_Index']:
        if value >= 80:
            colors.append('red')  # Extreme Greed
        elif value >= 60:
            colors.append('orange')  # Greed
        elif value >= 40:
            colors.append('yellow')  # Neutral
        elif value >= 20:
            colors.append('lightblue')  # Fear
        else:
            colors.append('blue')  # Extreme Fear
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Greed_Fear_Index'],
        mode='lines+markers',
        name='Greed-Fear Index',
        line=dict(color='black', width=2),
        marker=dict(color=colors, size=6)
    ))
    
    # Add horizontal reference lines
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Extreme Greed")
    fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Greed")
    fig.add_hline(y=40, line_dash="dash", line_color="yellow", annotation_text="Neutral")
    fig.add_hline(y=20, line_dash="dash", line_color="lightblue", annotation_text="Fear")
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Greed-Fear Index (0-100)",
        height=400,
        showlegend=True
    )
    
    return fig

def create_sentiment_plot(df, title="Sentiment Score Analysis"):
    """
    Create sentiment score plot with color coding
    """
    fig = go.Figure()
    
    # Define color conditions for sentiment
    colors = []
    for value in df['Sentiment_Score']:
        if pd.isna(value):
            colors.append('gray')
        elif value >= 50:
            colors.append('darkgreen')  # Very Positive
        elif value >= 20:
            colors.append('lightgreen')  # Positive
        elif value >= -20:
            colors.append('gold')  # Neutral
        elif value >= -50:
            colors.append('orange')  # Negative
        else:
            colors.append('red')  # Very Negative
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Sentiment_Score'],
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='black', width=2),
        marker=dict(color=colors, size=6)
    ))
    
    # Add horizontal reference lines
    fig.add_hline(y=50, line_dash="dash", line_color="darkgreen", annotation_text="Very Positive")
    fig.add_hline(y=20, line_dash="dash", line_color="lightgreen", annotation_text="Positive")
    fig.add_hline(y=0, line_dash="solid", line_color="gray", annotation_text="Neutral")
    fig.add_hline(y=-20, line_dash="dash", line_color="orange", annotation_text="Negative")
    fig.add_hline(y=-50, line_dash="dash", line_color="red", annotation_text="Very Negative")
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Sentiment Score (-100 to 100)",
        height=400,
        showlegend=True
    )
    
    return fig

def create_volatility_plot(df, title="Volatility Metrics"):
    """
    Create volatility metrics plot
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Historical Volatility (%)', 'ATR Percentage (%)', 
                       'Bollinger Band Width (%)', 'Price with Volatility'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # Historical Volatility
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Historical_Volatility'], 
                  name='Historical Vol', line=dict(color='blue')),
        row=1, col=1
    )
    
    # ATR Percentage
    fig.add_trace(
        go.Scatter(x=df.index, y=df['ATR_Percentage'], 
                  name='ATR %', line=dict(color='green')),
        row=1, col=2
    )
    
    # Bollinger Band Width
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Width'], 
                  name='BB Width', line=dict(color='purple')),
        row=2, col=1
    )
    
    # Price with volatility overlay
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], 
                  name='Close Price', line=dict(color='#1f77b4', width=2)),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Historical_Volatility'], 
                  name='Vol (Right Axis)', line=dict(color='red', dash='dash')),
        row=2, col=2, secondary_y=True
    )
    
    fig.update_layout(height=900, showlegend=True)
    fig.update_yaxes(title_text="Volatility %", secondary_y=True, row=2, col=2)
    
    return fig

def main():
    st.title("📈 Stock Greed-Fear, Sentiment & Volatility Analysis")
    stock = st.selectbox("Select a Stock", [s.removesuffix(".csv") for s in csv_files])
    
    # Read the CSV file
    df = pd.read_csv(f"data/processed/{stock}.csv")
    
    st.subheader("📊 Data Preview")
    st.write(f"Data shape: {df.shape}")
    st.dataframe(df.head())
    
    # Check for required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        st.info("Required columns: Open, High, Low, Close, Volume")
        return
    
    # Date column handling
    date_column = None
    if 'Date' in df.columns:
        date_column = 'Date'
    elif 'date' in df.columns:
        date_column = 'date'
    elif 'Datetime' in df.columns:
        date_column = 'Datetime'
    
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.set_index(date_column)
    else:
        st.warning("No date column found. Using row index as time axis.")
    
    # Sector selection if available
    if 'Sector' in df.columns:
        sectors = df['Sector'].unique()
        selected_sector = st.selectbox("Select Sector", ['All'] + list(sectors))
        
        if selected_sector != 'All':
            df = df[df['Sector'] == selected_sector]
            st.info(f"Filtered data for sector: {selected_sector}")
    
    # Calculate metrics
    with st.spinner("Calculating greed-fear, sentiment, and volatility metrics..."):
        df = calculate_greed_fear_index(df)
        df = calculate_sentiment_score(df)
        df = calculate_volatility_metrics(df)
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        current_gf = df['Greed_Fear_Index'].iloc[-1]
        st.metric("Current Greed-Fear Index", f"{current_gf:.1f}")
    
    with col2:
        current_sentiment = df['Sentiment_Score'].iloc[-1]
        st.metric("Current Sentiment Score", f"{current_sentiment:.1f}")
    
    with col3:
        current_vol = df['Historical_Volatility'].iloc[-1]
        st.metric("Current Volatility", f"{current_vol:.1f}%")
    
    with col4:
        current_atr = df['ATR_Percentage'].iloc[-1]
        st.metric("Current ATR %", f"{current_atr:.2f}%")
    
    with col5:
        current_bb_width = df['BB_Width'].iloc[-1]
        st.metric("Current BB Width", f"{current_bb_width:.2f}%")
    
    # Greed-Fear Index Plot
    st.subheader("🎯 Greed-Fear Index Analysis")
    gf_plot = create_greed_fear_plot(df, "Greed-Fear Index Over Time")
    st.plotly_chart(gf_plot, use_container_width=True)
    
    # Interpretation
    current_gf_status = ""
    if current_gf >= 80:
        current_gf_status = "🔴 Extreme Greed - Market may be overextended"
    elif current_gf >= 60:
        current_gf_status = "🟠 Greed - Bullish sentiment dominates"
    elif current_gf >= 40:
        current_gf_status = "🟡 Neutral - Balanced market sentiment"
    elif current_gf >= 20:
        current_gf_status = "🔵 Fear - Bearish sentiment present"
    else:
        current_gf_status = "🟦 Extreme Fear - Market may be oversold"
    
    st.info(f"Current Status: {current_gf_status}")
    
    # Sentiment Score Analysis
    st.subheader("🎯 Sentiment Score Analysis")
    sentiment_plot = create_sentiment_plot(df, "Technical Sentiment Score Over Time")
    st.plotly_chart(sentiment_plot, use_container_width=True)
    
    # Sentiment interpretation
    current_sentiment_status = ""
    if current_sentiment >= 50:
        current_sentiment_status = "🟢 Very Positive - Strong bullish technical signals"
    elif current_sentiment >= 20:
        current_sentiment_status = "🟠 Positive - Moderate bullish signals"
    elif current_sentiment >= -20:
        current_sentiment_status = "🟡 Neutral - Mixed technical signals"
    elif current_sentiment >= -50:
        current_sentiment_status = "🔴 Negative - Bearish technical signals"
    else:
        current_sentiment_status = "⚫ Very Negative - Strong bearish signals"
    
    st.info(f"Current Sentiment: {current_sentiment_status}")
    
    # Volatility Analysis
    st.subheader("📊 Volatility Analysis")
    vol_plot = create_volatility_plot(df, "Volatility Metrics Dashboard")
    st.plotly_chart(vol_plot, use_container_width=True)
    
    # Comprehensive Dashboard
    # st.subheader("🎛️ Comprehensive Dashboard")
    # comp_plot = create_comprehensive_dashboard(df)
    # st.plotly_chart(comp_plot, use_container_width=True)
    #
    # Correlation Analysis
    st.subheader("🔗 Correlation Analysis")
    correlation_data = df[['Greed_Fear_Index', 'Sentiment_Score', 'Historical_Volatility', 'ATR_Percentage', 'BB_Width']].corr()
    
    fig_corr = px.imshow(correlation_data, 
                        text_auto=True, 
                        aspect="auto",
                        title="Correlation Matrix: All Metrics")
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Summary Statistics
    st.subheader("📈 Summary Statistics")
    summary_stats = df[['Greed_Fear_Index', 'Sentiment_Score', 'Historical_Volatility', 'ATR_Percentage', 'BB_Width']].describe()
    st.dataframe(summary_stats)
    
    # Key Insights
    st.subheader("🔍 Key Insights")
    
    # Calculate some insights
    avg_sentiment = df['Sentiment_Score'].mean()
    avg_greed_fear = df['Greed_Fear_Index'].mean()
    sentiment_volatility = df['Sentiment_Score'].std()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Sentiment Analysis:**")
        st.write(f"• Average Sentiment Score: {avg_sentiment:.1f}")
        st.write(f"• Sentiment Volatility: {sentiment_volatility:.1f}")
        st.write(f"• Sentiment Trend: {'Improving' if current_sentiment > avg_sentiment else 'Declining'}")
    
    with col2:
        st.write("**Market Psychology:**")
        st.write(f"• Average Greed-Fear: {avg_greed_fear:.1f}")
        st.write(f"• Current vs Average: {current_gf - avg_greed_fear:+.1f}")
        st.write(f"• Market State: {'Overheated' if current_gf > 70 else 'Undervalued' if current_gf < 30 else 'Balanced'}")
    
    # Download processed data
    st.subheader("💾 Download Processed Data")
    csv_data = df.to_csv()
    st.download_button(
        label="Download CSV with all calculated metrics",
        data=csv_data,
        file_name=f"{stock}_analysis_with_sentiment.csv",
        mime="text/csv"
    )
       
if __name__ == "__main__":
    main()
