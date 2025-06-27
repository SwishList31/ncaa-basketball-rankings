"""
Add defensive statistics to NBA player data
This adds steals, blocks, and era information
"""

import pandas as pd

def add_defensive_stats_to_players():
    """Add defensive stats and era info to existing player data"""
    
    # Load existing data
    df = pd.read_csv('nba_goat_player_data.csv')
    
    # Add era information based on when players entered the league
    player_eras = {
        # Pre-merger (1946-1975)
        'Bill Russell': 1957, 'Wilt Chamberlain': 1959, 'Oscar Robertson': 1960,
        'Jerry West': 1960, 'Elgin Baylor': 1958, 'Bob Pettit': 1954,
        'George Mikan': 1948, 'Bob Cousy': 1950, 'Dolph Schayes': 1949,
        'Paul Arizin': 1950, 'Sam Jones': 1957, 'Hal Greer': 1958,
        'Nate Thurmond': 1963, 'Willis Reed': 1964, 'Walt Frazier': 1967,
        'Earl Monroe': 1967, 'Billy Cunningham': 1965, 'Dave Bing': 1966,
        'Lenny Wilkens': 1960, 'John Havlicek': 1962, 'Rick Barry': 1965,
        'Pete Maravich': 1970, 'Dave Cowens': 1970, 'Wes Unseld': 1968,
        'Tiny Archibald': 1970, 'Bob McAdoo': 1972, 'Artis Gilmore': 1971,
        'Julius Erving': 1971, 'George Gervin': 1972,
        
        # Early modern (1976-1984)
        'Magic Johnson': 1979, 'Larry Bird': 1979, 'Moses Malone': 1974,
        'Isiah Thomas': 1981, 'Adrian Dantley': 1976, 'Alex English': 1976,
        'Sidney Moncrief': 1979, 'Dennis Johnson': 1976, 'Gail Goodrich': 1965,
        'Jo Jo White': 1969, 'Bernard King': 1977,
        
        # Golden age (1985-1999)
        'Michael Jordan': 1984, 'Hakeem Olajuwon': 1984, 'Patrick Ewing': 1985,
        'David Robinson': 1989, 'Karl Malone': 1985, 'John Stockton': 1984,
        'Charles Barkley': 1984, 'Clyde Drexler': 1983, 'Scottie Pippen': 1987,
        'Gary Payton': 1990, 'Reggie Miller': 1987, 'Dominique Wilkins': 1982,
        'Dennis Rodman': 1986, 'Kevin McHale': 1980, 'Robert Parish': 1976,
        'Dikembe Mutombo': 1991, 'Alonzo Mourning': 1992, 'Grant Hill': 1994,
        
        # Post-Jordan (2000-2009)
        'Kobe Bryant': 1996, 'Tim Duncan': 1997, 'Shaquille O\'Neal': 1992,
        'Allen Iverson': 1996, 'Kevin Garnett': 1995, 'Dirk Nowitzki': 1998,
        'Steve Nash': 1996, 'Jason Kidd': 1994, 'Ray Allen': 1996,
        'Paul Pierce': 1998, 'Tracy McGrady': 1997, 'Vince Carter': 1998,
        'Chris Webber': 1993, 'Yao Ming': 2002, 'Ben Wallace': 1996,
        'Dwyane Wade': 2003, 'Chris Paul': 2005, 'Dwight Howard': 2004,
        'Carmelo Anthony': 2003, 'Tony Parker': 2001, 'Manu Ginobili': 2002,
        'Pau Gasol': 2001, 'LaMarcus Aldridge': 2006,
        
        # Modern (2010-2024)
        'LeBron James': 2003, 'Kevin Durant': 2007, 'Stephen Curry': 2009,
        'Giannis Antetokounmpo': 2013, 'Kawhi Leonard': 2011, 'James Harden': 2009,
        'Russell Westbrook': 2008, 'Anthony Davis': 2012, 'Damian Lillard': 2012,
        'Kyrie Irving': 2011, 'Paul George': 2010, 'Jimmy Butler': 2011,
        'Blake Griffin': 2009, 'DeMar DeRozan': 2009, 'Kyle Lowry': 2006,
        'Klay Thompson': 2011, 'Draymond Green': 2012
    }
    
    # Add start year
    df['start_year'] = df['name'].map(player_eras)
    
    # Defensive stats (steals and blocks) - these are career averages
    # Note: Steals and blocks only tracked since 1973-74 season
    defensive_stats = {
        # Guards with high steals
        'John Stockton': {'spg': 2.2, 'bpg': 0.2},
        'Gary Payton': {'spg': 1.8, 'bpg': 0.2},
        'Michael Jordan': {'spg': 2.3, 'bpg': 0.8},
        'Magic Johnson': {'spg': 1.9, 'bpg': 0.4},
        'Isiah Thomas': {'spg': 1.9, 'bpg': 0.3},
        'Chris Paul': {'spg': 2.1, 'bpg': 0.1},
        'Jason Kidd': {'spg': 1.9, 'bpg': 0.3},
        'Allen Iverson': {'spg': 2.2, 'bpg': 0.2},
        'Scottie Pippen': {'spg': 2.0, 'bpg': 0.8},
        'Clyde Drexler': {'spg': 2.0, 'bpg': 0.6},
        'Dwyane Wade': {'spg': 1.5, 'bpg': 0.8},
        'Walt Frazier': {'spg': 1.9, 'bpg': 0.2},  # Partial career
        'Alvin Robertson': {'spg': 2.7, 'bpg': 0.2},  # If included
        'Maurice Cheeks': {'spg': 2.1, 'bpg': 0.3},  # If included
        'Sidney Moncrief': {'spg': 1.5, 'bpg': 0.3},
        'Dennis Johnson': {'spg': 1.3, 'bpg': 0.4},
        'Kawhi Leonard': {'spg': 1.8, 'bpg': 0.6},
        'Larry Bird': {'spg': 1.7, 'bpg': 0.8},
        'Julius Erving': {'spg': 1.8, 'bpg': 1.5},  # ABA/NBA combined
        'Rick Barry': {'spg': 2.0, 'bpg': 0.5},  # Partial career
        'LeBron James': {'spg': 1.5, 'bpg': 0.7},
        'Kobe Bryant': {'spg': 1.4, 'bpg': 0.5},
        'Russell Westbrook': {'spg': 1.6, 'bpg': 0.3},
        'Stephen Curry': {'spg': 1.5, 'bpg': 0.2},
        'James Harden': {'spg': 1.5, 'bpg': 0.5},
        'Damian Lillard': {'spg': 0.9, 'bpg': 0.3},
        'Kyrie Irving': {'spg': 1.3, 'bpg': 0.3},
        'Jimmy Butler': {'spg': 1.6, 'bpg': 0.5},
        'Paul George': {'spg': 1.7, 'bpg': 0.4},
        
        # Big men with high blocks
        'Hakeem Olajuwon': {'spg': 1.7, 'bpg': 3.1},
        'Dikembe Mutombo': {'spg': 0.3, 'bpg': 2.8},
        'David Robinson': {'spg': 1.4, 'bpg': 3.0},
        'Patrick Ewing': {'spg': 1.0, 'bpg': 2.4},
        'Shaquille O\'Neal': {'spg': 0.6, 'bpg': 2.3},
        'Tim Duncan': {'spg': 0.7, 'bpg': 2.2},
        'Kareem Abdul-Jabbar': {'spg': 0.9, 'bpg': 2.6},  # Partial career
        'Ben Wallace': {'spg': 1.3, 'bpg': 2.0},
        'Alonzo Mourning': {'spg': 0.5, 'bpg': 2.8},
        'Dwight Howard': {'spg': 0.9, 'bpg': 1.8},
        'Anthony Davis': {'spg': 1.3, 'bpg': 2.3},
        'Kevin Garnett': {'spg': 1.3, 'bpg': 1.4},
        'Robert Parish': {'spg': 0.8, 'bpg': 1.5},
        'Artis Gilmore': {'spg': 0.5, 'bpg': 2.3},  # Partial career
        'Elvin Hayes': {'spg': 0.9, 'bpg': 2.0},  # Partial career
        'Moses Malone': {'spg': 0.8, 'bpg': 1.3},
        'Yao Ming': {'spg': 0.4, 'bpg': 1.9},
        'Karl Malone': {'spg': 1.4, 'bpg': 0.8},
        'Charles Barkley': {'spg': 1.5, 'bpg': 0.8},
        'Kevin Durant': {'spg': 1.1, 'bpg': 1.1},
        'Giannis Antetokounmpo': {'spg': 1.2, 'bpg': 1.3},
        'Dennis Rodman': {'spg': 0.7, 'bpg': 0.6},
        'Pau Gasol': {'spg': 0.6, 'bpg': 1.6},
        'LaMarcus Aldridge': {'spg': 0.7, 'bpg': 1.1},
        'Blake Griffin': {'spg': 0.9, 'bpg': 0.5},
        'Draymond Green': {'spg': 1.4, 'bpg': 0.8},
        
        # Others with some data
        'George Gervin': {'spg': 1.2, 'bpg': 0.8},
        'Dave Cowens': {'spg': 1.1, 'bpg': 0.9},  # Partial career
        'Nate Thurmond': {'spg': 0.5, 'bpg': 2.1},  # Very partial
        'Bob McAdoo': {'spg': 0.9, 'bpg': 1.5},
        'Dominique Wilkins': {'spg': 1.3, 'bpg': 0.6},
        'Grant Hill': {'spg': 1.2, 'bpg': 0.6},
        'Chris Webber': {'spg': 1.4, 'bpg': 1.4},
        'Vince Carter': {'spg': 1.0, 'bpg': 0.6},
        'Tracy McGrady': {'spg': 1.3, 'bpg': 0.9},
        'Ray Allen': {'spg': 1.1, 'bpg': 0.2},
        'Reggie Miller': {'spg': 1.1, 'bpg': 0.2},
        'Steve Nash': {'spg': 0.7, 'bpg': 0.1},
        'Dirk Nowitzki': {'spg': 0.9, 'bpg': 0.8},
        'Paul Pierce': {'spg': 1.3, 'bpg': 0.6},
        'Kevin McHale': {'spg': 0.4, 'bpg': 1.7},
        'Tiny Archibald': {'spg': 1.1, 'bpg': 0.1},  # Partial
        'Pete Maravich': {'spg': 1.4, 'bpg': 0.3},  # Partial
        'Adrian Dantley': {'spg': 1.0, 'bpg': 0.2},
        'Alex English': {'spg': 0.9, 'bpg': 0.5},
        'Bernard King': {'spg': 0.8, 'bpg': 0.3},
        'Joe Dumars': {'spg': 0.9, 'bpg': 0.2},
        'Tony Parker': {'spg': 0.8, 'bpg': 0.1},
        'Manu Ginobili': {'spg': 1.3, 'bpg': 0.3},
        'Kyle Lowry': {'spg': 1.4, 'bpg': 0.3},
        'DeMar DeRozan': {'spg': 1.0, 'bpg': 0.3},
        'Klay Thompson': {'spg': 0.8, 'bpg': 0.5},
        'Dave Bing': {'spg': 1.3, 'bpg': 0.3},  # Partial
        'Lenny Wilkens': {'spg': 1.2, 'bpg': 0.2},  # Partial
        
        # Pre-1974 players get 0.0 for both
    }
    
    # Add steals and blocks
    df['career_spg'] = df['name'].map(lambda x: defensive_stats.get(x, {}).get('spg', 0.0))
    df['career_bpg'] = df['name'].map(lambda x: defensive_stats.get(x, {}).get('bpg', 0.0))
    
    # Save updated data
    df.to_csv('nba_goat_player_data_v2.csv', index=False)
    print(f"Updated data saved with defensive stats for {len(df)} players")
    print(f"Players with steals data: {(df['career_spg'] > 0).sum()}")
    print(f"Players with blocks data: {(df['career_bpg'] > 0).sum()}")
    
    return df

if __name__ == "__main__":
    # Update the data
    df = add_defensive_stats_to_players()
    
    # Show some examples
    print("\nTop 10 by steals per game:")
    print(df[df['career_spg'] > 0].nlargest(10, 'career_spg')[['name', 'career_spg', 'career_bpg']])
    
    print("\nTop 10 by blocks per game:")
    print(df[df['career_bpg'] > 0].nlargest(10, 'career_bpg')[['name', 'career_spg', 'career_bpg']])