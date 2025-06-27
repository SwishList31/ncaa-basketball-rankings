"""
SWISH Score Calculator - Updated with Era Adjustments and Defense
Calculates comprehensive NBA GOAT rankings using multiple factors

Weights:
- Peak Dominance Score: 20% (Best 5-year stretch)
- Career Value Score: 20% (Total Win Shares/VORP) 
- Individual Honors Score: 20% (MVPs, All-NBAs, Scoring Titles, All-Defense)
- Championship Impact Score: 15% (Rings + Finals MVPs)
- Statistical Excellence: 15% (Era-adjusted stats INCLUDING DEFENSE)
- Longevity Score: 10% (Games, seasons, durability)
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

class SwishScoreCalculator:
    def __init__(self, player_data_path='nba_goat_player_data.csv'):
        """Initialize with player data"""
        self.player_data = pd.read_csv(player_data_path)
        
        # Era definitions for adjustments
        self.eras = {
            'pre_merger': (1946, 1975),    # Pre ABA-NBA merger
            'early_modern': (1976, 1984),   # Post merger, pre-Jordan
            'golden_age': (1985, 1999),     # Jordan era
            'post_jordan': (2000, 2009),    # Post Jordan, pre pace increase
            'modern': (2010, 2024)          # Current era
        }
        
        # Era context for statistical adjustments
        self.era_context = {
            'pre_merger': {
                'avg_ppg': 25.0, 'avg_rpg': 12.0, 'avg_apg': 4.5,
                'avg_fg_pct': 0.440, 'avg_ft_pct': 0.720,
                'pace': 115, 'avg_ts_pct': 0.480
            },
            'early_modern': {
                'avg_ppg': 22.0, 'avg_rpg': 10.0, 'avg_apg': 5.0,
                'avg_fg_pct': 0.470, 'avg_ft_pct': 0.750,
                'pace': 105, 'avg_ts_pct': 0.520
            },
            'golden_age': {
                'avg_ppg': 21.0, 'avg_rpg': 9.0, 'avg_apg': 5.0,
                'avg_fg_pct': 0.470, 'avg_ft_pct': 0.760,
                'pace': 100, 'avg_ts_pct': 0.530
            },
            'post_jordan': {
                'avg_ppg': 19.0, 'avg_rpg': 8.5, 'avg_apg': 5.0,
                'avg_fg_pct': 0.450, 'avg_ft_pct': 0.770,
                'pace': 90, 'avg_ts_pct': 0.520
            },
            'modern': {
                'avg_ppg': 20.0, 'avg_rpg': 8.0, 'avg_apg': 5.5,
                'avg_fg_pct': 0.460, 'avg_ft_pct': 0.780,
                'pace': 95, 'avg_ts_pct': 0.550
            }
        }
        
        print("SWISH Score Calculator Initialized (v2.0 - Era Adjusted)")
        print(f"Loaded {len(self.player_data)} players")
        
    def calculate_swish_score(self):
        """Calculate SWISH Score for all players"""
        print("\nCalculating SWISH Scores...")
        
        # Calculate each component
        self.player_data['peak_dominance_score'] = self.calculate_peak_dominance()
        self.player_data['career_value_score'] = self.calculate_career_value()
        self.player_data['championship_impact_score'] = self.calculate_championship_impact()
        self.player_data['individual_honors_score'] = self.calculate_individual_honors()
        self.player_data['statistical_excellence_score'] = self.calculate_statistical_excellence()
        self.player_data['longevity_score'] = self.calculate_longevity()
        
        # Calculate final SWISH Score with updated weights
        self.player_data['SWISH_Score'] = (
            0.20 * self.player_data['peak_dominance_score'] +
            0.20 * self.player_data['career_value_score'] +
            0.20 * self.player_data['individual_honors_score'] +
            0.15 * self.player_data['championship_impact_score'] +
            0.15 * self.player_data['statistical_excellence_score'] +
            0.10 * self.player_data['longevity_score']
        )
        
        # Sort by SWISH Score
        self.player_data = self.player_data.sort_values('SWISH_Score', ascending=False)
        self.player_data['GOAT_Rank'] = range(1, len(self.player_data) + 1)
        
        return self.player_data
    
    def get_player_era(self, player):
        """Determine which era a player primarily played in"""
        # Using career midpoint as proxy (you could enhance this with actual data)
        start_year = player.get('start_year', None)
        
        if start_year is None:
            # Estimate based on other data
            if player.get('name') in ['Bill Russell', 'Wilt Chamberlain', 'Jerry West', 'Oscar Robertson', 'Elgin Baylor']:
                return 'pre_merger'
            elif player.get('name') in ['Magic Johnson', 'Larry Bird', 'Julius Erving', 'Moses Malone']:
                return 'early_modern'
            elif player.get('name') in ['Michael Jordan', 'Hakeem Olajuwon', 'Karl Malone', 'David Robinson']:
                return 'golden_age'
            elif player.get('name') in ['Kobe Bryant', 'Tim Duncan', 'Shaquille O\'Neal', 'Allen Iverson']:
                return 'post_jordan'
            else:
                return 'modern'
        
        for era_name, (start, end) in self.eras.items():
            if start <= start_year <= end:
                return era_name
        
        return 'modern'
    
    def calculate_peak_dominance(self):
        """Calculate peak dominance score based on best 5-year stretch"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Use career PER as proxy for peak (would need season data for true 5-year peak)
            peak_per = player.get('career_per', 15)
            
            # Peak scoring
            peak_ppg = player.get('peak_ppg', 0)
            
            # Win shares per 48 estimate (career WS / games * 48)
            games = player.get('career_games', 1)
            ws_per_48 = (player.get('career_ws', 0) / games) * 48 if games > 0 else 0
            
            # Normalize components
            per_score = min(100, (peak_per / 31.0) * 100)  # 31+ PER is all-time great
            ppg_score = min(100, (peak_ppg / 35.0) * 100)  # 35+ PPG is historic
            ws48_score = min(100, (ws_per_48 / 0.25) * 100)  # 0.25+ WS/48 is elite
            
            # Weight the components
            peak_score = (
                0.40 * per_score +
                0.30 * ppg_score +
                0.30 * ws48_score
            )
            
            scores.append(peak_score)
        
        return scores
    
    def calculate_career_value(self):
        """Calculate career value score based on total contribution"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Career Win Shares
            career_ws = player.get('career_ws', 0)
            ws_score = min(100, (career_ws / 250.0) * 100)  # 250+ WS is all-time great
            
            # Career VORP
            career_vorp = player.get('career_vorp', 0)
            vorp_score = min(100, (career_vorp / 100.0) * 100)  # 100+ VORP is elite
            
            # Career counting stats
            ppg = player.get('career_ppg', 0)
            rpg = player.get('career_rpg', 0)
            apg = player.get('career_apg', 0)
            
            # Normalize by position (guards less rebounds, centers less assists)
            stats_score = min(100, (
                (ppg / 30.0) * 40 +  # 30+ PPG career is legendary
                (rpg / 10.0) * 30 +  # 10+ RPG
                (apg / 8.0) * 30     # 8+ APG
            ))
            
            # Weight the components
            career_score = (
                0.40 * ws_score +
                0.40 * vorp_score +
                0.20 * stats_score
            )
            
            scores.append(career_score)
        
        return scores
    
    def calculate_championship_impact(self):
        """Calculate championship impact score"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Championships
            rings = player.get('championships', 0)
            rings_score = min(100, (rings / 6.0) * 100)  # 6+ rings is Jordan level
            
            # Finals MVPs
            finals_mvps = player.get('finals_mvp', 0)
            fmvp_score = min(100, (finals_mvps / 4.0) * 100)  # 4+ FMVPs is legendary
            
            # Playoff performance
            playoff_ppg = player.get('playoff_pts_per_g', 0)
            career_ppg = player.get('career_ppg', 1)
            
            # Playoff elevation (do they get better in playoffs?)
            playoff_elevation = (playoff_ppg / career_ppg) if career_ppg > 0 else 1.0
            elevation_score = min(100, playoff_elevation * 80)  # Bonus for playoff performers
            
            # Playoff games played (experience)
            playoff_games = player.get('playoff_g', 0)
            playoff_exp_score = min(100, (playoff_games / 200.0) * 100)  # 200+ playoff games
            
            # Weight the components
            championship_score = (
                0.35 * rings_score +
                0.35 * fmvp_score +
                0.20 * elevation_score +
                0.10 * playoff_exp_score
            )
            
            scores.append(championship_score)
        
        return scores
    
    def calculate_individual_honors(self):
        """Calculate individual honors score"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # MVPs
            mvps = player.get('mvp', 0)
            mvp_score = min(100, (mvps / 5.0) * 100)  # 5+ MVPs is GOAT tier
            
            # All-NBA selections
            first_team = player.get('all_nba_first', 0)
            second_team = player.get('all_nba_second', 0)
            third_team = player.get('all_nba_third', 0)
            
            all_nba_points = (first_team * 5) + (second_team * 3) + (third_team * 1)
            all_nba_score = min(100, (all_nba_points / 60.0) * 100)  # 60+ points is elite
            
            # All-Star selections
            all_stars = player.get('all_star', 0)
            all_star_score = min(100, (all_stars / 15.0) * 100)  # 15+ All-Stars
            
            # Defensive honors (updated scoring)
            dpoy = player.get('dpoy', 0)
            all_def_first = player.get('all_defensive_first', 0)
            all_def_second = player.get('all_defensive_second', 0)
            
            defensive_points = (dpoy * 10) + (all_def_first * 3) + (all_def_second * 1.5)
            defensive_score = min(100, (defensive_points / 40.0) * 100)
            
            # Scoring titles (new)
            scoring_titles = player.get('scoring_titles', 0)
            scoring_title_points = scoring_titles * 4
            scoring_title_score = min(100, (scoring_title_points / 40.0) * 100)  # 10+ scoring titles is legendary
            
            # Weight the components (adjusted for new category)
            honors_score = (
                0.30 * mvp_score +
                0.25 * all_nba_score +
                0.15 * all_star_score +
                0.15 * defensive_score +
                0.15 * scoring_title_score
            )
            
            scores.append(honors_score)
        
        return scores
    
    def calculate_statistical_excellence(self):
        """Calculate era-adjusted statistical excellence including defense"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Determine player's era
            player_era = self.get_player_era(player)
            era_stats = self.era_context.get(player_era, self.era_context['modern'])
            
            # 1. OFFENSIVE EXCELLENCE (40%)
            offensive_score = self.calculate_offensive_excellence(player, era_stats)
            
            # 2. DEFENSIVE EXCELLENCE (30%)
            defensive_score = self.calculate_defensive_excellence(player, era_stats)
            
            # 3. OVERALL EFFICIENCY (30%)
            efficiency_score = self.calculate_efficiency_metrics(player, era_stats)
            
            # Combine all components
            stats_score = (
                0.40 * offensive_score +
                0.30 * defensive_score +
                0.30 * efficiency_score
            )
            
            scores.append(stats_score)
        
        return scores
    
    def calculate_offensive_excellence(self, player, era_stats):
        """Calculate era-adjusted offensive excellence"""
        
        # Era-adjusted scoring
        career_ppg = player.get('career_ppg', 0)
        ppg_vs_era = career_ppg / era_stats['avg_ppg'] if era_stats['avg_ppg'] > 0 else 0
        
        # Convert to percentile (1.0 = average, 1.5 = 50% above average)
        ppg_score = min(100, max(0, (ppg_vs_era - 0.5) * 100))
        
        # Era-adjusted assists
        career_apg = player.get('career_apg', 0)
        apg_vs_era = career_apg / era_stats['avg_apg'] if era_stats['avg_apg'] > 0 else 0
        apg_score = min(100, max(0, (apg_vs_era - 0.5) * 100))
        
        # Peak scoring ability (era-adjusted)
        peak_ppg = player.get('peak_ppg', 0)
        seasons_30ppg = player.get('seasons_30ppg', 0)
        seasons_25ppg = player.get('seasons_25ppg', 0)
        
        # Era-adjusted peak
        peak_vs_era = peak_ppg / era_stats['avg_ppg'] if era_stats['avg_ppg'] > 0 else 0
        peak_score = min(100, max(0, (
            (peak_vs_era - 1.0) * 50 +  # Peak vs era
            (seasons_30ppg * 8) +        # Bonus for 30+ seasons
            (seasons_25ppg * 3)          # Bonus for 25+ seasons
        )))
        
        # Combine offensive components
        offensive_score = (
            0.50 * ppg_score +
            0.25 * apg_score +
            0.25 * peak_score
        )
        
        return offensive_score
    
    def calculate_defensive_excellence(self, player, era_stats):
        """Calculate defensive excellence from available stats"""
        
        # Defensive awards and honors
        dpoy = player.get('dpoy', 0)
        all_def_first = player.get('all_defensive_first', 0)
        all_def_second = player.get('all_defensive_second', 0)
        
        # Award-based defensive score
        defensive_points = (dpoy * 15) + (all_def_first * 5) + (all_def_second * 2.5)
        award_score = min(100, (defensive_points / 50.0) * 100)
        
        # Rebounding excellence (era-adjusted)
        career_rpg = player.get('career_rpg', 0)
        rpg_vs_era = career_rpg / era_stats['avg_rpg'] if era_stats['avg_rpg'] > 0 else 0
        
        # Position adjustment for rebounding
        position_factor = 1.0
        if career_rpg < 5.0:  # Likely a guard
            position_factor = 2.0
        elif career_rpg < 8.0:  # Likely a forward
            position_factor = 1.5
        
        rebound_score = min(100, max(0, (rpg_vs_era - 0.5) * 100 * position_factor))
        
        # Steals and blocks (if available)
        spg = player.get('career_spg', 0)
        bpg = player.get('career_bpg', 0)
        
        # For pre-1974 players without steals/blocks data
        player_era = self.get_player_era(player)
        if player_era == 'pre_merger' and spg == 0 and bpg == 0:
            stocks_score = 50  # Neutral score
        else:
            stocks_score = min(100, (
                (spg / 2.0) * 50 +  # 2+ SPG is elite
                (bpg / 2.5) * 50    # 2.5+ BPG is elite
            ))
        
        # Combine defensive components
        defensive_score = (
            0.50 * award_score +
            0.30 * rebound_score +
            0.20 * stocks_score
        )
        
        return defensive_score
    
    def calculate_efficiency_metrics(self, player, era_stats):
        """Calculate overall efficiency metrics"""
        
        # 1. PER (already era-adjusted)
        career_per = player.get('career_per', 15.0)
        per_score = min(100, max(0, ((career_per - 15.0) / 10.0) * 100))
        
        # 2. True Shooting % (estimate if not available)
        career_ts_pct = player.get('career_ts_pct', None)
        
        if career_ts_pct:
            ts_vs_era = career_ts_pct / era_stats['avg_ts_pct']
            ts_score = min(100, max(0, (ts_vs_era - 0.85) * 100 / 0.3))
        else:
            # Estimate from FG% and FT%
            fg_pct = player.get('career_fg_pct', 0.450)
            ft_pct = player.get('career_ft_pct', 0.750)
            
            # Simple TS% estimate
            estimated_ts = fg_pct + (0.5 * ft_pct * 0.2)
            ts_vs_era = estimated_ts / era_stats['avg_ts_pct'] if era_stats['avg_ts_pct'] > 0 else 0
            ts_score = min(100, max(0, (ts_vs_era - 0.85) * 100 / 0.3))
        
        # 3. Turnover rate (use neutral if not available)
        tov_pct = player.get('career_tov_pct', None)
        if tov_pct:
            tov_score = min(100, max(0, (20 - tov_pct) * 5))
        else:
            tov_score = 50  # Neutral if not available
        
        # Combine efficiency components
        efficiency_score = (
            0.50 * per_score +
            0.35 * ts_score +
            0.15 * tov_score
        )
        
        return efficiency_score
    
    def calculate_longevity(self):
        """Calculate longevity score"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Seasons played
            seasons = player.get('seasons_played', 0)
            seasons_score = min(100, (seasons / 20.0) * 100)  # 20+ seasons is exceptional
            
            # Games played
            games = player.get('career_games', 0)
            games_score = min(100, (games / 1400.0) * 100)  # 1400+ games is elite durability
            
            # Late career effectiveness (using All-Star selections as proxy)
            all_stars = player.get('all_star', 0)
            late_career_score = min(100, (all_stars / seasons * 100) if seasons > 0 else 0)
            
            # Weight the components
            longevity_score = (
                0.40 * seasons_score +
                0.40 * games_score +
                0.20 * late_career_score
            )
            
            scores.append(longevity_score)
        
        return scores
    
    def display_top_players(self, n=25):
        """Display the top N players with their scores"""
        print(f"\n{'='*100}")
        print(f"SWISH NBA GOAT RANKINGS - TOP {n}")
        print(f"{'='*100}")
        print(f"{'Rank':<6}{'Player':<25}{'SWISH':<8}{'Peak':<8}{'Career':<8}{'Honors':<8}{'Champ':<8}{'Stats':<8}{'Long':<8}")
        print(f"{'-'*100}")
        
        for idx, player in self.player_data.head(n).iterrows():
            print(f"{player['GOAT_Rank']:<6}{player['name']:<25}"
                  f"{player['SWISH_Score']:<8.1f}"
                  f"{player['peak_dominance_score']:<8.1f}"
                  f"{player['career_value_score']:<8.1f}"
                  f"{player['individual_honors_score']:<8.1f}"
                  f"{player['championship_impact_score']:<8.1f}"
                  f"{player['statistical_excellence_score']:<8.1f}"
                  f"{player['longevity_score']:<8.1f}")
    
    def save_rankings(self, filename='nba_goat_rankings_swish.csv'):
        """Save the complete rankings to CSV"""
        # Select columns to save
        columns_to_save = [
            'GOAT_Rank', 'name', 'SWISH_Score',
            'peak_dominance_score', 'career_value_score', 'championship_impact_score',
            'individual_honors_score', 'statistical_excellence_score', 'longevity_score',
            'career_ppg', 'career_rpg', 'career_apg', 'career_per', 'career_ws',
            'championships', 'finals_mvp', 'mvp', 'all_star'
        ]
        
        # Save only columns that exist
        save_columns = [col for col in columns_to_save if col in self.player_data.columns]
        
        self.player_data[save_columns].to_csv(filename, index=False)
        print(f"\nRankings saved to {filename}")
    
    def get_player_breakdown(self, player_name):
        """Get detailed breakdown for a specific player"""
        player = self.player_data[self.player_data['name'].str.contains(player_name, case=False)]
        
        if player.empty:
            print(f"Player '{player_name}' not found")
            return None
        
        player = player.iloc[0]
        
        print(f"\n{'='*60}")
        print(f"SWISH SCORE BREAKDOWN: {player['name']}")
        print(f"{'='*60}")
        print(f"Overall Rank: #{int(player['GOAT_Rank'])}")
        print(f"SWISH Score: {player['SWISH_Score']:.2f}\n")
        
        print("Component Scores:")
        print(f"  Peak Dominance (20%):        {player['peak_dominance_score']:.2f}")
        print(f"  Career Value (20%):          {player['career_value_score']:.2f}")
        print(f"  Individual Honors (20%):     {player['individual_honors_score']:.2f}")
        print(f"  Championship Impact (15%):   {player['championship_impact_score']:.2f}")
        print(f"  Statistical Excellence (15%): {player['statistical_excellence_score']:.2f}")
        print(f"  Longevity (10%):            {player['longevity_score']:.2f}")
        
        print(f"\nKey Stats:")
        print(f"  Career: {player.get('career_ppg', 0):.1f} PPG, {player.get('career_rpg', 0):.1f} RPG, {player.get('career_apg', 0):.1f} APG")
        print(f"  Career PER: {player.get('career_per', 0):.1f}")
        print(f"  Championships: {int(player.get('championships', 0))}")
        print(f"  MVPs: {int(player.get('mvp', 0))}")
        print(f"  All-Star: {int(player.get('all_star', 0))}")
        
        return player

# Example usage
if __name__ == "__main__":
    # Calculate SWISH Scores
    calculator = SwishScoreCalculator()
    rankings = calculator.calculate_swish_score()
    
    # Display results
    calculator.display_top_players(100)
    
    # Get detailed breakdown
    calculator.get_player_breakdown('Jordan')
    calculator.get_player_breakdown('Russell')
    
    # Save rankings
    calculator.save_rankings()