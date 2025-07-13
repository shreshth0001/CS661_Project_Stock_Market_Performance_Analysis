import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.markdown("""
   <style>
   section[data-testid="stSidebar"] {
       background: #232946;
       color: #fff;
   }

   /* CSS hack: Move the first sidebar block to the top */
   section[data-testid="stSidebar"] > div:first-child {
       order: -1;
   }
   </style>
   """, unsafe_allow_html=True)

# Header with better styling
st.markdown("# 🗺️ **US Companies Geographic Distribution Dashboard**")
st.markdown("### *Explore company distribution across states by industry sector*")
st.markdown("---")

with st.sidebar:
    st.markdown("<h2 style='margin-bottom: 1.5rem;'>NAVIGATION</h2>", unsafe_allow_html=True)

# Load data
geodf = pd.read_csv("data/geodat.csv")
states = geodf['State']
sectors = geodf.columns[2:]

# Sector selection with better styling
st.markdown("####  **Select Industry Sector**")
option = st.selectbox("Choose a sector to analyze:", sectors, help="Select an industry sector to view its geographic distribution")

vals = geodf[option]

# Create DataFrame
df = pd.DataFrame({
    'state': states,
    'value': vals
})

# Convert state names to state codes (required for choropleth)
state_codes = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

df['code'] = df['state'].map(state_codes)

# Main map visualization
st.markdown(f"##  **Geographic Distribution: {option} Sector**")

# Create choropleth map
fig = px.choropleth(
    df,
    locations='code',
    locationmode="USA-states",
    color='value',
    scope="usa",
    color_continuous_scale="Viridis",
    title=f"Company Distribution Across US States - {option}",
    labels={'value': 'Number of Companies'}
)
# fig.update_geos(bgcolor='#0e1117')
fig.update_geos(bgcolor='lightblue')

fig.update_layout(
    # plot_bgcolor=plot_bgcolor,
    # paper_bgcolor=paper_bgcolor,
    # font=dict(color=font_color),
    height=600,
    title_font_size=18,
    coloraxis_colorbar=dict(
        title="Number of Companies",
        title_font_size=14
    )
)

st.plotly_chart(fig, use_container_width=True,theme="streamlit")

# Separator for better organization
st.markdown("---")

# Additional statistics section
st.markdown("##  **Key Analytics & Insights**")

# Get top 5 states first
top_5_states = df.nlargest(5, 'value')

# Create two columns for top 5 states
col_top1, col_top2 = st.columns(2)

with col_top1:
    st.markdown("###  **Top 5 Leading States**")
    
    # Display top 5 states with metrics
    for i, (idx, row) in enumerate(top_5_states.iterrows(), 1):
        st.metric(
            label=f"{i}. {row['state']}", 
            value=f"{int(row['value'])} companies"
        )

with col_top2:
    st.markdown("###  **Top 5 States Visualization**")
    
    # Create a bar chart for top 5 states
    bar_fig = px.bar(
        top_5_states,
        x='value',
        y='state',
        orientation='h',
        color='value',
        color_continuous_scale="Viridis",
        title=""
    )
    
    bar_fig.update_layout(
        height=350,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Number of Companies",
        yaxis_title="State",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)

# Statistical overview
st.markdown("###  **Sector Statistical Summary**")

col3, col4, col5, col6 = st.columns(4)

with col3:
    total_companies = df['value'].sum()
    st.metric("Total Companies", f"{int(total_companies):,}")

with col4:
    avg_companies = df['value'].mean()
    st.metric("Average per State", f"{avg_companies:.1f}")

with col5:
    max_companies = df['value'].max()
    st.metric("Maximum", f"{int(max_companies)}")

with col6:
    states_with_companies = (df['value'] > 0).sum()
    st.metric("States with Companies", f"{states_with_companies}")

# Show detailed table
st.markdown("---")
st.markdown("###  **Complete State Rankings**")

with st.expander(" **Click to view detailed data for all states**", expanded=False):
    # Sort by value in descending order
    sorted_df = df.sort_values('value', ascending=False).reset_index(drop=True)
    sorted_df.index = sorted_df.index + 1  # Start index from 1
    
    # Add some styling and additional columns
    display_df = sorted_df[['state', 'value']].rename(columns={'state': 'State', 'value': 'Number of Companies'})
    
    # Add percentage column
    total_companies = display_df['Number of Companies'].sum()
    display_df['Percentage'] = ((display_df['Number of Companies'] / total_companies) * 100).round(2)
    display_df['Percentage'] = display_df['Percentage'].astype(str) + '%'
    
    # Display the sorted dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )

# Footer
st.markdown("---")
st.markdown("* **Tip**: Use the sector dropdown to explore different industries and see how company distribution varies across the United States.*")
