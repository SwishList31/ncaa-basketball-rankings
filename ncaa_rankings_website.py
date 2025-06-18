"""
NCAA Basketball Power Rankings Website
Built with Streamlit for easy deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NCAA Basketball Power Rankings",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .rank-change-up {
        color: #16a34a;
        font-weight: bold;
    }
    .rank-change-down {
        color: #dc2626;
        font-weight: bold;
    }
    .stDataFrame {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_rankings():
    """Load the rankings data"""
    try:
        df = pd.read_csv('data/final_predictive_rankings_v3.csv')
        return df
    except:
        # Return sample data if file not found
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration"""
    teams = ['Auburn', 'Houston', 'Tennessee', 'Florida', 'Duke', 
             'Gonzaga', 'Maryland', 'Iowa St.', 'Texas Tech', 'Mississippi']
    
    data = {
        'Team': teams,
        'Final_Rank': range(1, 11),
        'Final_Score': np.linspace(95, 85, 10),
        'Conference': ['SEC', 'B12', 'SEC', 'SEC', 'ACC', 'WCC', 'B10', 'B12', 'B12', 'SEC'],
        'KenPom_Rank': [2, 1, 4, 6, 3, 8, 5, 7, 10, 9],
        'AdjOE': np.linspace(120, 115, 10),
        'AdjDE': np.linspace(88, 93, 10),
        'AdjOE_Rank': range(1, 11),
        'AdjDE_Rank': range(1, 11),
        'Experience': np.random.uniform(1.5, 3.0, 10),
        'Turnover_Margin': np.random.uniform(-2, 5, 10),
        'Rank_Change': [1, -1, 1, 2, -2, 2, -2, -1, 2, -1]
    }
    
    return pd.DataFrame(data)

# Header
st.markdown('<h1 class="main-header">🏀 NCAA Basketball Power Rankings</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Predictive Model • 80.7% Accuracy</p>', unsafe_allow_html=True)

# Load data
df = load_rankings()

# Sidebar
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
    This ranking system uses an advanced predictive model that weighs:
    - **Defensive Rating (30%)**
    - **Offensive Rating (30%)**
    - **Recent Performance (20%)**
    - **Experience (15%)**
    - **Turnover Margin (5%)**
    
    Model validated at **80.7% accuracy** on 2024-25 season games.
    """)
    
    # Filter options
    st.markdown("## Filters")
    
    # Conference filter
    conferences = ['All'] + sorted(df['Conference'].unique().tolist())
    selected_conf = st.selectbox("Conference", conferences)
    
    # Rank range filter - DEFAULT TO ALL TEAMS
    rank_range = st.slider(
        "Rank Range",
        min_value=1,
        max_value=len(df),
        value=(1, len(df))  # Changed to show all by default
    )
    
    # Update info
    st.markdown("---")
    st.markdown(f"*Last Updated: {datetime.now().strftime('%B %d, %Y')}*")

# Filter data based on selections
filtered_df = df.copy()

if selected_conf != 'All':
    filtered_df = filtered_df[filtered_df['Conference'] == selected_conf]

filtered_df = filtered_df[
    (filtered_df['Final_Rank'] >= rank_range[0]) & 
    (filtered_df['Final_Rank'] <= rank_range[1])
]

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Rankings", "📈 Analysis", "🔍 Team Details", "ℹ️ Methodology"])

with tab1:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Teams Ranked", len(df))
    with col2:
        st.metric("Model Accuracy", "80.7%")
    with col3:
        top_team = df.iloc[0]['Team']
        st.metric("Current #1", top_team)
    with col4:
        avg_experience = df.head(25)['Experience'].mean()
        st.metric("Top 25 Avg Experience", f"{avg_experience:.2f} years")
    
    st.markdown("---")
    
    # Main rankings table
    st.subheader(f"Current Rankings - Showing {len(filtered_df)} Teams")
    
    # Prepare display dataframe
    display_cols = ['Final_Rank', 'Team', 'Conference', 'Final_Score', 
                    'AdjOE_Rank', 'AdjDE_Rank', 'Experience', 
                    'Turnover_Margin', 'KenPom_Rank', 'Rank_Change']
    
    display_df = filtered_df[display_cols].copy()
    
    # Rename columns for display
    display_df.columns = ['Rank', 'Team', 'Conf', 'Score', 
                         'Off Rank', 'Def Rank', 'Exp (yrs)', 
                         'TO Margin', 'KenPom', 'Change']
    
    # Format columns
    display_df['Score'] = display_df['Score'].round(1)
    display_df['Exp (yrs)'] = display_df['Exp (yrs)'].round(2)
    display_df['TO Margin'] = display_df['TO Margin'].round(1)
    
    # Create rank change symbols
    def format_change(val):
        if pd.isna(val) or val == 0:
            return "="
        elif val > 0:
            return f"↑{int(val)}"
        else:
            return f"↓{int(abs(val))}"
    
    display_df['Change'] = display_df['Change'].apply(format_change)
    
    # Display the table with larger height
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=800,  # Make it taller to show more teams
        column_config={
            "Rank": st.column_config.NumberColumn(format="%d"),
            "Score": st.column_config.NumberColumn(format="%.1f"),
            "Off Rank": st.column_config.NumberColumn(format="%d"),
            "Def Rank": st.column_config.NumberColumn(format="%d"),
            "KenPom": st.column_config.NumberColumn(format="%d"),
        }
    )

with tab2:
    st.subheader("Ranking Analysis")
    
    # Two columns for visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Conference distribution
        st.markdown("#### Conference Distribution (Top 25)")
        top_25 = df.head(25)
        conf_counts = top_25['Conference'].value_counts()
        
        fig_conf = px.pie(
            values=conf_counts.values,
            names=conf_counts.index,
            title="Top 25 Teams by Conference",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_conf.update_traces(textposition='inside', textinfo='value+percent')
        st.plotly_chart(fig_conf, use_container_width=True)
    
    with col2:
        # Offense vs Defense scatter
        st.markdown("#### Offensive vs Defensive Efficiency")
        
        fig_scatter = px.scatter(
            df.head(50),
            x='AdjOE',
            y='AdjDE',
            size='Final_Score',
            color='Conference',
            hover_data=['Team', 'Final_Rank'],
            labels={'AdjOE': 'Offensive Efficiency', 'AdjDE': 'Defensive Efficiency'},
            title="Top 50 Teams: Offense vs Defense"
        )
        fig_scatter.update_layout(
            xaxis_title="Offensive Efficiency →",
            yaxis_title="← Defensive Efficiency (Lower is Better)",
            hovermode='closest'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Model vs KenPom comparison
    st.markdown("#### Model vs KenPom Rankings")
    
    fig_comparison = go.Figure()
    
    # Add scatter plot
    fig_comparison.add_trace(go.Scatter(
        x=df['KenPom_Rank'],
        y=df['Final_Rank'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['Final_Score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Model Score")
        ),
        text=df['Team'],
        hovertemplate='%{text}<br>KenPom: %{x}<br>Our Model: %{y}<extra></extra>'
    ))
    
    # Add diagonal line
    fig_comparison.add_trace(go.Scatter(
        x=[1, len(df)],
        y=[1, len(df)],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        showlegend=False
    ))
    
    fig_comparison.update_layout(
        title="Ranking Comparison: Our Model vs KenPom",
        xaxis_title="KenPom Rank",
        yaxis_title="Our Model Rank",
        hovermode='closest',
        height=500
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)

with tab3:
    st.subheader("Team Details")
    
    # Team selector
    selected_team = st.selectbox(
        "Select a team:",
        df['Team'].tolist(),
        index=0
    )
    
    # Get team data
    team_data = df[df['Team'] == selected_team].iloc[0]
    
    # Display team info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Ranking Info")
        st.metric("Overall Rank", f"#{int(team_data['Final_Rank'])}")
        st.metric("Model Score", f"{team_data['Final_Score']:.1f}")
        st.metric("KenPom Rank", f"#{int(team_data['KenPom_Rank'])}")
        
        rank_diff = team_data['KenPom_Rank'] - team_data['Final_Rank']
        if rank_diff > 0:
            st.markdown(f"**Model ranks {int(rank_diff)} spots higher**")
        elif rank_diff < 0:
            st.markdown(f"**Model ranks {int(abs(rank_diff))} spots lower**")
        else:
            st.markdown("**Same as KenPom ranking**")
    
    with col2:
        st.markdown("### Performance Metrics")
        st.metric("Offensive Rank", f"#{int(team_data['AdjOE_Rank'])}")
        st.metric("Defensive Rank", f"#{int(team_data['AdjDE_Rank'])}")
        st.metric("Efficiency Margin", f"{team_data['AdjOE'] - team_data['AdjDE']:.1f}")
    
    with col3:
        st.markdown("### Team Characteristics")
        st.metric("Experience", f"{team_data['Experience']:.2f} years")
        st.metric("Turnover Margin", f"{team_data['Turnover_Margin']:+.1f}%")
        st.metric("Conference", team_data['Conference'])
    
    # Radar chart for team profile
    st.markdown("---")
    st.markdown("### Team Profile")
    
    # Calculate percentiles for radar chart
    metrics = {
        'Offense': (len(df) - team_data['AdjOE_Rank']) / len(df) * 100,
        'Defense': (len(df) - team_data['AdjDE_Rank']) / len(df) * 100,
        'Experience': (team_data['Experience'] - df['Experience'].min()) / 
                     (df['Experience'].max() - df['Experience'].min()) * 100,
        'TO Margin': (team_data['Turnover_Margin'] - df['Turnover_Margin'].min()) / 
                    (df['Turnover_Margin'].max() - df['Turnover_Margin'].min()) * 100,
        'Overall': (len(df) - team_data['Final_Rank']) / len(df) * 100
    }
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=list(metrics.values()),
        theta=list(metrics.keys()),
        fill='toself',
        name=selected_team
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title=f"{selected_team} Performance Profile (Percentiles)"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

with tab4:
    st.subheader("Methodology")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Model Philosophy
        
        This predictive power ranking model is built on the principle that elite college basketball 
        teams dominate across all phases of the game. The model combines multiple factors to create 
        a comprehensive evaluation of team strength.
        
        ### Factor Weights
        
        The model uses five key factors with the following weights:
        
        1. **Defensive Rating (30%)**: Adjusted defensive efficiency per 100 possessions
        2. **Offensive Rating (30%)**: Adjusted offensive efficiency per 100 possessions  
        3. **Recent Performance (20%)**: Current form and momentum
        4. **Experience (15%)**: Average years of college experience
        5. **Turnover Margin (5%)**: Ability to force turnovers while protecting the ball
        
        ### Validation
        
        The model has been validated against actual game results from the 2024-25 season:
        
        - **Overall Accuracy**: 80.7% (440/545 games predicted correctly)
        - **Close Games (Rank diff 1-10)**: 64.6% accuracy
        - **Moderate Mismatches (Rank diff 26-50)**: 82.9% accuracy
        - **Clear Favorites (Rank diff 100+)**: 99.3% accuracy
        
        This performance exceeds typical prediction models and is competitive with established 
        systems like KenPom (75-78% typical accuracy).
        
        ### Data Sources
        
        All data is sourced from KenPom.com with appropriate subscriptions and permissions.
        Rankings are updated weekly during the season.
        """)
    
    with col2:
        st.markdown("### Quick Facts")
        
        st.info("""
        **Model Highlights:**
        - 80.7% prediction accuracy
        - Validated on 545 games
        - Updates weekly
        - 364 teams ranked
        """)
        
        st.success("""
        **Unique Insights:**
        - Values veteran experience
        - Emphasizes turnover margin
        - Balanced offense/defense
        - Recent form matters
        """)
        
        st.warning("""
        **Limitations:**
        - Early season volatility
        - Injury adjustments
        - Home court variations
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    NCAA Basketball Power Rankings | Model by Mitch Watkins | 
    Data from KenPom.com | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)