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
    page_title="Swish List Ratings - NCAA Basketball",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Maximize content width */
    .block-container {
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        margin-top: -10px;
        font-family: 'Arial Black', sans-serif;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
        font-weight: 500;
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
    /* Swish List brand colors */
    div[data-testid="metric-container"] {
        background-color: #FFF5F0;
        border: 1px solid #FF6B35;
        border-radius: 8px;
    }
    /* Make the dataframe area larger */
    div[data-testid="stDataFrame"] {
        height: 100% !important;
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
st.markdown('<h1 class="main-header">🏀 Swish List Ratings</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Nothing But Net Analytics • 80.7% Accuracy</p>', unsafe_allow_html=True)

# Load data
df = load_rankings()

# Sidebar
with st.sidebar:
    st.markdown("## About Swish List")
    st.markdown("""
    **Swish List Ratings** uses an advanced predictive model that analyzes:
    - **Defensive Rating (30%)**
    - **Offensive Rating (30%)**
    - **Recent Performance (20%)**
    - **Experience (15%)**
    - **Turnover Margin (5%)**
    
    Our model has been validated at **80.7% accuracy** on 2024-25 season games,
    outperforming many established ranking systems.
    """)
    
    # Filter options
    st.markdown("## Filters")
    
    # Conference filter
    conferences = ['All'] + sorted(df['Conference'].unique().tolist())
    selected_conf = st.selectbox("Conference", conferences)
    
    # Rank range filter
    rank_range = st.slider(
        "Rank Range",
        min_value=1,
        max_value=len(df),
        value=(1, 25)
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Rankings", "📈 Analysis", "🔍 Team Details", "ℹ️ Methodology", "🏀 NBA GOAT", "📧 Contact"])

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
    st.subheader("Current Rankings")
    
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
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
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

with tab5:
    st.subheader("NBA GOAT Rankings - SWISH Score")
    
    # Load NBA GOAT data
    @st.cache_data
    def load_nba_rankings():
        try:
            df = pd.read_csv('nba_goat_rankings_swish.csv')
            return df
        except:
            # Return empty dataframe if file not found
            st.error("NBA GOAT rankings file not found. Run the analysis first.")
            return pd.DataFrame()
    
    nba_df = load_nba_rankings()
    
    if not nba_df.empty:
        # Sidebar filters for NBA
        with st.sidebar:
            if st.checkbox("Show NBA Filters", value=False):
                st.markdown("### NBA Filters")
                
                # Era filter
                era_filter = st.selectbox(
                    "Filter by Era",
                    ["All Eras", "Pre-1980", "1980s-1990s", "2000s", "2010s+"]
                )
                
                # Minimum games filter
                min_games = st.slider(
                    "Minimum Games Played",
                    min_value=0,
                    max_value=1500,
                    value=500
                )
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Players Ranked", len(nba_df))
        with col2:
            goat = nba_df.iloc[0]['name'] if 'name' in nba_df.columns else "Unknown"
            st.metric("Current GOAT", goat)
        with col3:
            avg_swish = nba_df['SWISH_Score'].mean()
            st.metric("Avg SWISH Score", f"{avg_swish:.1f}")
        with col4:
            top_10_avg = nba_df.head(10)['SWISH_Score'].mean()
            st.metric("Top 10 Avg", f"{top_10_avg:.1f}")
        
        st.markdown("---")
        
        # Explanation of SWISH Score
        with st.expander("📊 What is the SWISH Score?"):
            st.markdown("""
            The **SWISH Score** is a comprehensive metric that evaluates NBA players across six key dimensions:
            
            - **Peak Dominance (20%)**: Best 5-year stretch of their career
            - **Career Value (20%)**: Total Win Shares and VORP accumulated
            - **Individual Honors (20%)**: MVPs, All-NBA selections, scoring titles, All-Defense
            - **Championship Impact (15%)**: Championships, Finals MVPs, playoff performance
            - **Statistical Excellence (15%)**: Era-adjusted statistics
            - **Longevity (10%)**: Games played, seasons, and sustained excellence
            
            Scores range from 0-100, with 90+ being all-time legendary status.
            """)
        
        # Main rankings table
        st.subheader("All-Time NBA GOAT Rankings")
        
        # Prepare display dataframe
        display_cols = ['GOAT_Rank', 'name', 'SWISH_Score', 
                       'peak_dominance_score', 'career_value_score', 
                       'individual_honors_score', 'championship_impact_score',
                       'statistical_excellence_score', 'longevity_score']
        
        # Check which columns exist
        available_cols = [col for col in display_cols if col in nba_df.columns]
        
        nba_display = nba_df[available_cols].copy()
        
        # Rename columns for display
        column_names = {
            'GOAT_Rank': 'Rank',
            'name': 'Player',
            'SWISH_Score': 'SWISH',
            'peak_dominance_score': 'Peak',
            'career_value_score': 'Career',
            'individual_honors_score': 'Honors',
            'championship_impact_score': 'Champs',
            'statistical_excellence_score': 'Stats',
            'longevity_score': 'Long'
        }
        
        nba_display.rename(columns=column_names, inplace=True)
        
        # Format scores to 1 decimal
        score_cols = ['SWISH', 'Peak', 'Career', 'Honors', 'Champs', 'Stats', 'Long']
        for col in score_cols:
            if col in nba_display.columns:
                nba_display[col] = nba_display[col].round(1)
        
        # Display the table
        st.dataframe(
            nba_display,
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "Rank": st.column_config.NumberColumn(format="%d", width="small"),
                "Player": st.column_config.TextColumn(width="medium"),
                "SWISH": st.column_config.NumberColumn(format="%.1f"),
                "Peak": st.column_config.ProgressColumn(
                    help="Peak dominance score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "Career": st.column_config.ProgressColumn(
                    help="Career value score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "Honors": st.column_config.ProgressColumn(
                    help="Individual honors score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "Champs": st.column_config.ProgressColumn(
                    help="Championship impact score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "Stats": st.column_config.ProgressColumn(
                    help="Statistical excellence score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "Long": st.column_config.ProgressColumn(
                    help="Longevity score",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
            }
        )
        
        # Analysis section
        st.markdown("---")
        st.subheader("GOAT Tier Analysis")
        
        # Create tiers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🐐 GOAT Tier (90+)")
            goat_tier = nba_df[nba_df['SWISH_Score'] >= 90]
            if not goat_tier.empty:
                for _, player in goat_tier.iterrows():
                    st.write(f"**{player['name']}** - {player['SWISH_Score']:.1f}")
            else:
                st.write("*No players in this tier*")
        
        with col2:
            st.markdown("#### 👑 Legendary (80-89)")
            legend_tier = nba_df[(nba_df['SWISH_Score'] >= 80) & (nba_df['SWISH_Score'] < 90)]
            if not legend_tier.empty:
                for _, player in legend_tier.iterrows():
                    st.write(f"**{player['name']}** - {player['SWISH_Score']:.1f}")
        
        with col3:
            st.markdown("#### ⭐ All-Time Great (70-79)")
            great_tier = nba_df[(nba_df['SWISH_Score'] >= 70) & (nba_df['SWISH_Score'] < 80)]
            if not great_tier.empty:
                for _, player in great_tier.iterrows():
                    st.write(f"**{player['name']}** - {player['SWISH_Score']:.1f}")
        
        # Fun facts
        st.markdown("---")
        st.subheader("Interesting Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Highest individual category scores
            st.markdown("#### Category Leaders")
            
            categories = [
                ('Peak Dominance', 'peak_dominance_score'),
                ('Career Value', 'career_value_score'),
                ('Individual Honors', 'individual_honors_score'),
                ('Championship Impact', 'championship_impact_score'),
                ('Statistical Excellence', 'statistical_excellence_score'),
                ('Longevity', 'longevity_score')
            ]
            
            for cat_name, cat_col in categories:
                if cat_col in nba_df.columns:
                    leader = nba_df.loc[nba_df[cat_col].idxmax()]
                    st.write(f"**{cat_name}**: {leader['name']} ({leader[cat_col]:.1f})")
        
        with col2:
            # Biggest surprises
            st.markdown("#### Notable Rankings")
            
            # Find players with biggest difference from common perception
            if 'championships' in nba_df.columns:
                # Players with 0 rings in top 20
                ringless = nba_df[(nba_df['GOAT_Rank'] <= 20) & (nba_df['championships'] == 0)]
                if not ringless.empty:
                    st.write("**Top 20 without a ring:**")
                    for _, player in ringless.iterrows():
                        st.write(f"- {player['name']} (#{int(player['GOAT_Rank'])})")
    
    else:
        st.warning("NBA GOAT rankings data not found. Please run the analysis script first.")

with tab6:
    st.subheader("Contact Swish List")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Get in Touch
        
        Have questions about the rankings? Want to report an issue? 
        Interested in collaborating? Found a bug in the model?
        
        We'd love to hear from you!
        """)
        
        st.markdown("---")
        
        # Contact info with nice formatting
        st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #FFF5F0; border-radius: 10px; border: 2px solid #FF6B35;'>
            <h3 style='color: #FF6B35; margin-bottom: 20px;'>Reach Out</h3>
            <p style='font-size: 1.2rem; margin: 10px;'>
                📧 <strong>Email:</strong> <a href='mailto:mitchwatkins@gmail.com'>mitchwatkins@gmail.com</a>
            </p>
            <p style='font-size: 1.2rem; margin: 10px;'>
                🐦 <strong>Twitter:</strong> <a href='https://twitter.com/swishlist31' target='_blank'>@swishlist31</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.info("""
        **Best for:**
        - Technical questions about the model
        - Partnership & collaboration inquiries  
        - Bug reports and data corrections
        - Media requests
        - General feedback
        
        **Response time:** Usually within 24-48 hours
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    Swish List Ratings | Created by Mitch Watkins | 
    Data from KenPom.com | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)