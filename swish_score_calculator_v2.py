"""
SWISH Score Calculator v2.0 - Era Adjusted
Major improvements:
- Era-adjusted statistics for fair historical comparison
- Enhanced defensive metrics integration
- Position-based adjustments where appropriate
"""

import pandas as pd
import numpy as np
from scipy import stats

class SwishScoreCalculatorV2:
    def __init__(self, player_data_path='nba_goat_player_data_complete.csv'):
        """Initialize with enhanced player data including defensive stats"""
        self.player_data = pd.read_csv(player_data_path)
        
        # Era definitions with average stats for normalization
        self.era_stats = {
            'pre_merger': {
                'years': (1946, 1975),
                'avg_ppg': 19.8,
                'avg_rpg': 5.9,
                'avg_apg': 3.2,
                'avg_fg_pct': 0.426,
                'avg_pace': 110,
                'avg_stl': 1.2,  # Estimated pre-1974
                'avg_blk': 0.8   # Estimated pre-1974
            },
            'early_modern': {
                'years': (1976, 1984),
                'avg_ppg': 18.4,
                'avg_rpg': 5.2,
                'avg_apg': 3.8,
                'avg_fg_pct': 0.461,
                'avg_pace': 103,
                'avg_stl': 1.5,
                'avg_blk': 0.7
            },
            'golden_age': {
                'years': (1985, 1999),
                'avg_ppg': 16.8,
                'avg_rpg': 4.8,
                'avg_apg': 3.5,
                'avg_fg_pct': 0.454,
                'avg_pace': 95,
                'avg_stl': 1.4,
                'avg_blk': 0.6
            },
            'post_jordan': {
                'years': (2000, 2009),
                'avg_ppg': 15.2,
                'avg_rpg': 4.4,
                'avg_apg': 3.3,
                'avg_fg_pct': 0.439,
                'avg_pace': 91,
                'avg_stl': 1.3,
                'avg_blk': 0.5
            },
            'modern': {
                'years': (2010, 2024),
                'avg_ppg': 16.5,
                'avg_rpg': 4.5,
                'avg_apg': 3.6,
                'avg_fg_pct': 0.449,
                'avg_pace': 97,
                'avg_stl': 1.2,
                'avg_blk': 0.5
            }
        }
        
        # Add era to each player
        self.assign_player_eras()
        
        # Version info for tracking
        self.swish_version = "2.1"
        
        print("SWISH Score Calculator v2.1 Initialized")
        print("Updated Weights: Championships 20% (+5%), Individual Honors 15% (-5%)")
        print(f"Loaded {len(self.player_data)} players with era adjustments")
        
    def assign_player_eras(self):
        """Assign primary era to each player based on peak years"""
        def get_player_era(row):
            # Try to use actual career years if available
            start_year = row.get('career_start', None)
            end_year = row.get('career_end', None)
            
            # If we don't have career years, estimate from other data
            if pd.isna(start_year) or pd.isna(end_year):
                # Use draft year or other indicators if available
                name = row.get('name', '')
                
                # Known player eras
                if any(n in name for n in ['Russell', 'Chamberlain', 'Robertson', 'West', 'Baylor']):
                    return 'pre_merger'
                elif any(n in name for n in ['Kareem', 'Erving', 'Moses']):
                    return 'early_modern'
                elif any(n in name for n in ['Jordan', 'Magic', 'Bird', 'Hakeem', 'Barkley', 'Malone', 'Stockton']):
                    return 'golden_age'
                elif any(n in name for n in ['Duncan', 'Kobe', 'Shaq', 'Garnett', 'Dirk', 'Nash', 'Iverson']):
                    return 'post_jordan'
                elif any(n in name for n in ['LeBron', 'Durant', 'Curry', 'Giannis', 'Kawhi', 'Harden', 'Chris Paul']):
                    return 'modern'
                else:
                    # Default based on championships if available
                    championships = row.get('championships', 0)
                    if championships > 0:
                        # Rough guess based on typical championship years
                        return 'modern'  # Safe default
                    return 'modern'
            
            # Calculate career midpoint
            career_mid = (start_year + end_year) / 2
            
            # Assign based on career midpoint
            if career_mid < 1976:
                return 'pre_merger'
            elif career_mid < 1985:
                return 'early_modern'
            elif career_mid < 2000:
                return 'golden_age'
            elif career_mid < 2010:
                return 'post_jordan'
            else:
                return 'modern'
        
        # Add era column
        self.player_data['era'] = self.player_data.apply(get_player_era, axis=1)
    
    def calculate_era_adjusted_stat(self, player_stat, stat_name, player_era):
        """Calculate era-adjusted version of a stat"""
        if pd.isna(player_stat) or player_stat == 0:
            return 0
            
        era_avg = self.era_stats[player_era].get(f'avg_{stat_name}', 1)
        
        # Calculate percentage above/below era average
        era_multiplier = player_stat / era_avg if era_avg > 0 else 1
        
        # Normalize to 0-100 scale with reasonable bounds
        if stat_name in ['ppg', 'rpg', 'apg']:
            # 150% of era average = 75 score, 200% = 100 score
            score = min(100, (era_multiplier - 1) * 150)
        elif stat_name in ['stl', 'blk']:
            # Defensive stats: 200% of era average = 75 score
            score = min(100, (era_multiplier - 1) * 100)
        else:
            # For percentages
            score = min(100, max(0, (player_stat - 0.400) * 500))
            
        return max(0, score)
    
    def calculate_peak_dominance(self):
        """Era-adjusted peak dominance score"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            era = player.get('era', 'modern')
            
            # Era-adjusted peak scoring
            peak_ppg = player.get('peak_ppg', 0)
            peak_ppg_adjusted = self.calculate_era_adjusted_stat(peak_ppg, 'ppg', era)
            
            # Peak PER (already era-neutral)
            peak_per = player.get('career_per', 15)
            per_score = min(100, ((peak_per - 15) / 16) * 100)  # 31+ PER is perfect
            
            # Peak Win Shares per 48
            games = player.get('career_games', 1)
            ws_per_48 = (player.get('career_ws', 0) / games) * 48 if games > 0 else 0
            ws48_score = min(100, (ws_per_48 / 0.250) * 100)
            
            # MVP shares in peak years
            mvp_shares = player.get('mvp_shares', 0)
            mvp_share_score = min(100, (mvp_shares / 5.0) * 100)  # 5+ MVP shares is elite
            
            # Weight the components
            peak_score = (
                0.30 * peak_ppg_adjusted +
                0.30 * per_score +
                0.25 * ws48_score +
                0.15 * mvp_share_score
            )
            
            scores.append(peak_score)
        
        return scores
    
    def calculate_career_value(self):
        """Era-adjusted career value score"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            era = player.get('era', 'modern')
            
            # Career Win Shares (era-neutral)
            career_ws = player.get('career_ws', 0)
            ws_score = min(100, (career_ws / 250.0) * 100)
            
            # Career VORP (era-neutral)
            career_vorp = player.get('career_vorp', 0)
            vorp_score = min(100, (career_vorp / 100.0) * 100)
            
            # Era-adjusted career stats
            ppg = player.get('career_ppg', 0)
            rpg = player.get('career_rpg', 0)
            apg = player.get('career_apg', 0)
            
            ppg_adjusted = self.calculate_era_adjusted_stat(ppg, 'ppg', era)
            rpg_adjusted = self.calculate_era_adjusted_stat(rpg, 'rpg', era)
            apg_adjusted = self.calculate_era_adjusted_stat(apg, 'apg', era)
            
            # Combine stats with position weighting
            position = player.get('primary_position', 'F')
            if position in ['C', 'F-C', 'C-F']:
                stats_score = (ppg_adjusted * 0.35 + rpg_adjusted * 0.45 + apg_adjusted * 0.20)
            elif position in ['G', 'G-F', 'F-G']:
                stats_score = (ppg_adjusted * 0.40 + rpg_adjusted * 0.20 + apg_adjusted * 0.40)
            else:  # Forwards
                stats_score = (ppg_adjusted * 0.40 + rpg_adjusted * 0.35 + apg_adjusted * 0.25)
            
            # Weight the components
            career_score = (
                0.40 * ws_score +
                0.35 * vorp_score +
                0.25 * stats_score
            )
            
            scores.append(career_score)
        
        return scores
    
    def calculate_championship_impact(self):
        """Championship impact with era context"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Championships (slightly era-adjusted for league size)
            rings = player.get('championships', 0)
            era = player.get('era', 'modern')
            
            # Earlier eras had fewer teams, so championships were "easier"
            era_multiplier = {'pre_merger': 0.7, 'early_modern': 0.8, 
                            'golden_age': 0.9, 'post_jordan': 1.0, 'modern': 1.0}
            
            adjusted_rings = rings * era_multiplier.get(era, 1.0)
            rings_score = min(100, (adjusted_rings / 5.0) * 100)
            
            # Finals MVPs (more valuable in modern era with more competition)
            finals_mvps = player.get('finals_mvp', 0)
            fmvp_score = min(100, (finals_mvps / 3.0) * 100)
            
            # Playoff performance elevation
            playoff_ppg = player.get('playoff_pts_per_g', 0)
            career_ppg = player.get('career_ppg', 1)
            playoff_elevation = (playoff_ppg / career_ppg) if career_ppg > 0 else 1.0
            
            # Bonus for significant elevation (>110% of regular season)
            elevation_score = 0
            if playoff_elevation > 1.10:
                elevation_score = min(100, (playoff_elevation - 1) * 500)
            
            # Playoff games (durability and success)
            playoff_games = player.get('playoff_g', 0)
            playoff_exp_score = min(100, (playoff_games / 220.0) * 100)
            
            # Weight the components
            championship_score = (
                0.35 * rings_score +
                0.30 * fmvp_score +
                0.20 * elevation_score +
                0.15 * playoff_exp_score
            )
            
            scores.append(championship_score)
        
        return scores
    
    def calculate_individual_honors(self):
        """Individual honors with defensive recognition"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # MVPs
            mvps = player.get('mvp', 0)
            mvp_score = min(100, (mvps / 4.0) * 100)
            
            # All-NBA selections
            first_team = player.get('all_nba_first', 0)
            second_team = player.get('all_nba_second', 0)
            third_team = player.get('all_nba_third', 0)
            
            all_nba_points = (first_team * 5) + (second_team * 3) + (third_team * 1)
            all_nba_score = min(100, (all_nba_points / 50.0) * 100)
            
            # All-Star selections (era-adjusted for number of teams)
            all_stars = player.get('all_star', 0)
            era = player.get('era', 'modern')
            
            era_star_target = {'pre_merger': 10, 'early_modern': 12, 
                             'golden_age': 13, 'post_jordan': 14, 'modern': 15}
            
            all_star_score = min(100, (all_stars / era_star_target.get(era, 15)) * 100)
            
            # Defensive honors (significantly weighted)
            dpoy = player.get('dpoy', 0)
            all_def_first = player.get('all_defensive_first', 0)
            all_def_second = player.get('all_defensive_second', 0)
            steals_titles = player.get('steals_leader', 0)
            blocks_titles = player.get('blocks_leader', 0)
            
            defensive_points = (
                (dpoy * 15) + 
                (all_def_first * 5) + 
                (all_def_second * 2) +
                (steals_titles * 3) +
                (blocks_titles * 3)
            )
            defensive_score = min(100, (defensive_points / 50.0) * 100)
            
            # Scoring titles
            scoring_titles = player.get('scoring_titles', 0)
            scoring_score = min(100, (scoring_titles / 7.0) * 100)
            
            # Weight the components
            honors_score = (
                0.25 * mvp_score +
                0.25 * all_nba_score +
                0.15 * all_star_score +
                0.20 * defensive_score +  # Increased weight
                0.15 * scoring_score
            )
            
            scores.append(honors_score)
        
        return scores
    
    def calculate_statistical_excellence(self):
        """Era-adjusted statistical excellence with defense"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            era = player.get('era', 'modern')
            
            # Offensive excellence (era-adjusted)
            career_ppg = player.get('career_ppg', 0)
            ppg_score = self.calculate_era_adjusted_stat(career_ppg, 'ppg', era)
            
            # Efficiency 
            ts_pct = player.get('career_ts_pct', 0.500)
            era_avg_ts = {'pre_merger': 0.470, 'early_modern': 0.520, 
                         'golden_age': 0.535, 'post_jordan': 0.525, 'modern': 0.560}
            
            ts_vs_era = (ts_pct - era_avg_ts.get(era, 0.540)) * 1000
            efficiency_score = min(100, max(0, 50 + ts_vs_era))
            
            # Defensive excellence (NEW)
            stl_pg = player.get('career_stl_per_g', 0)
            blk_pg = player.get('career_blk_per_g', 0)
            drb_pg = player.get('career_drb_per_g', 0)
            
            stl_score = self.calculate_era_adjusted_stat(stl_pg, 'stl', era)
            blk_score = self.calculate_era_adjusted_stat(blk_pg, 'blk', era)
            
            # Defensive rebounding (position-adjusted)
            position = player.get('primary_position', 'F')
            drb_target = {'C': 7.0, 'F': 5.0, 'G': 3.0}
            pos_category = 'C' if 'C' in position else 'G' if 'G' in position else 'F'
            drb_score = min(100, (drb_pg / drb_target.get(pos_category, 5.0)) * 100)
            
            defensive_stat_score = (stl_score * 0.4 + blk_score * 0.4 + drb_score * 0.2)
            
            # Advanced metrics
            per = player.get('career_per', 15)
            per_score = min(100, ((per - 15) / 12) * 100)
            
            # Weight the components
            stats_score = (
                0.25 * ppg_score +
                0.25 * efficiency_score +
                0.25 * defensive_stat_score +  # NEW
                0.25 * per_score
            )
            
            scores.append(stats_score)
        
        return scores
    
    def calculate_longevity(self):
        """Enhanced longevity with quality consideration"""
        scores = []
        
        for _, player in self.player_data.iterrows():
            # Seasons played
            seasons = player.get('seasons_played', 0)
            seasons_score = min(100, (seasons / 18.0) * 100)
            
            # Games played
            games = player.get('career_games', 0)
            games_score = min(100, (games / 1300.0) * 100)
            
            # Quality longevity - All-Stars per season
            all_stars = player.get('all_star', 0)
            quality_ratio = (all_stars / seasons) if seasons > 0 else 0
            quality_score = min(100, quality_ratio * 120)  # 0.83+ ratio is elite
            
            # Minutes per game (durability)
            mpg = player.get('career_mpg', 0)
            mpg_score = min(100, (mpg / 36.0) * 100)  # 36+ MPG shows durability
            
            # Weight the components
            longevity_score = (
                0.30 * seasons_score +
                0.30 * games_score +
                0.25 * quality_score +
                0.15 * mpg_score
            )
            
            scores.append(longevity_score)
        
        return scores
    
    def calculate_swish_score(self):
        """Calculate SWISH Score v2.0 for all players"""
        print("\nCalculating SWISH Scores v2.0...")
        
        # Calculate each component
        self.player_data['peak_dominance_score'] = self.calculate_peak_dominance()
        self.player_data['career_value_score'] = self.calculate_career_value()
        self.player_data['championship_impact_score'] = self.calculate_championship_impact()
        self.player_data['individual_honors_score'] = self.calculate_individual_honors()
        self.player_data['statistical_excellence_score'] = self.calculate_statistical_excellence()
        self.player_data['longevity_score'] = self.calculate_longevity()
        
        # Calculate final SWISH Score with updated weights
        self.player_data['SWISH_Score'] = (
            0.20 * self.player_data['peak_dominance_score'] +      # Peak Dominance: 20%
            0.20 * self.player_data['career_value_score'] +        # Career Value: 20%
            0.15 * self.player_data['individual_honors_score'] +    # Individual Honors: 15% (decreased from 20%)
            0.20 * self.player_data['championship_impact_score'] +  # Championship Impact: 20% (increased from 15%)
            0.15 * self.player_data['statistical_excellence_score'] + # Statistical Excellence: 15%
            0.10 * self.player_data['longevity_score']             # Longevity: 10%
        )
        
        # Sort by SWISH Score
        self.player_data = self.player_data.sort_values('SWISH_Score', ascending=False)
        self.player_data['GOAT_Rank'] = range(1, len(self.player_data) + 1)
        
        # Add version info
        self.player_data['swish_version'] = '2.1'
        
        return self.player_data
    
    def display_top_players(self, n=25):
        """Display the top N players with era info"""
        print(f"\n{'='*120}")
        print(f"SWISH NBA GOAT RANKINGS v2.1 - TOP {n}")
        print("Weights: Peak 20% | Career 20% | Championships 20% | Honors 15% | Stats 15% | Longevity 10%")
        print(f"{'='*120}")
        print(f"{'Rank':<6}{'Player':<25}{'Era':<12}{'SWISH':<8}{'Peak':<8}{'Career':<8}{'Honors':<8}{'Champ':<8}{'Stats':<8}{'Long':<8}")
        print(f"{'-'*120}")
        
        for idx, player in self.player_data.head(n).iterrows():
            era_display = player['era'].replace('_', ' ').title()
            print(f"{player['GOAT_Rank']:<6}{player['name']:<25}{era_display:<12}"
                  f"{player['SWISH_Score']:<8.1f}"
                  f"{player['peak_dominance_score']:<8.1f}"
                  f"{player['career_value_score']:<8.1f}"
                  f"{player['individual_honors_score']:<8.1f}"
                  f"{player['championship_impact_score']:<8.1f}"
                  f"{player['statistical_excellence_score']:<8.1f}"
                  f"{player['longevity_score']:<8.1f}")
    
    def save_rankings(self, filename='nba_goat_rankings_swish_v2.csv'):
        """Save the complete rankings to CSV"""
        # Select columns to save
        columns_to_save = [
            'GOAT_Rank', 'name', 'era', 'SWISH_Score', 'swish_version',
            'peak_dominance_score', 'career_value_score', 'championship_impact_score',
            'individual_honors_score', 'statistical_excellence_score', 'longevity_score',
            'career_ppg', 'career_rpg', 'career_apg', 'career_per', 'career_ws',
            'career_ts_pct', 'career_stl_per_g', 'career_blk_per_g',
            'championships', 'finals_mvp', 'mvp', 'all_star', 'dpoy',
            'all_defensive_first', 'all_defensive_second'
        ]
        
        # Save only columns that exist
        save_columns = [col for col in columns_to_save if col in self.player_data.columns]
        
        self.player_data[save_columns].to_csv(filename, index=False)
        print(f"\nRankings saved to {filename}")
        
        # Also save as the main file for the website
        self.player_data[save_columns].to_csv('nba_goat_rankings_swish.csv', index=False)
        print(f"Also saved to nba_goat_rankings_swish.csv for website")

# Example usage
if __name__ == "__main__":
    # Initialize calculator
    calculator = SwishScoreCalculatorV2()
    
    # Calculate rankings
    rankings = calculator.calculate_swish_score()
    
    # Display top 30
    calculator.display_top_players(30)
    
    # Show era distribution
    print("\n\nEra Distribution in Top 50:")
    era_counts = rankings.head(50)['era'].value_counts()
    for era, count in era_counts.items():
        print(f"  {era.replace('_', ' ').title()}: {count} players")
    
    # Save rankings
    calculator.save_rankings()
    
    print("\n✅ SWISH Score v2.0 calculation complete!")
    print("Era adjustments and defensive statistics have been integrated.")