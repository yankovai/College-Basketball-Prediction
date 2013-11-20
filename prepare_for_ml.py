from pandas import *
import sqlite3 as lite
import numpy as np
import csv

class Prepare_for_ML(object):
    """
    Prepares the raw data scraped from sports-referece.com and turns it into a 
    form that can be digested by the scikit-learn classes.
    """
    
    def __init__(self, scoring_filename, cbb_db_name):
        self.scoring_filename = scoring_filename
        self.cbb_db_name = cbb_db_name
        
    def __call__(self):
        """
        Loops through the csv file 'scoring_filename' and creates a feature
        vector for each game played. The results are stored in an array 
        'features.npz' in the current directory.
        """
        
        con = lite.connect(self.cbb_db_name)
        with con:
            cur = con.cursor()
            
            features = []
            results = []
            with open(self.scoring_filename,'rb') as csvfile:
                games = csv.reader(csvfile)
                games.next()

                for game in games:
                    feature, result = self.process_game(game, cur)
                    
                    if result:
                        features.append(feature)
                        results.append(result)
        
        # Save features and results to file
        features = np.vstack(features)
        results = np.array(results)
        np.savez('features', X = features, y = results)
        
    def process_game(self, game, cursor):
        """
        The input game is a list that contains the following elements:
        
        year, team1, team2, points1, points2
        
        These elements refer to a matchup between team1 and team2 in some year.
        The result of the match is that team1 scored points1 while team2 scored
        points2. This function queries the SQL database 'cbb_db_name' and
        returns the ratio features(team1):features(team2) along with the result,
        which is 1 if team1 won or 0 otherwise.
        """
        
        query = 'SELECT * FROM Team_Stats WHERE Team = ? AND Year = ?'
        
        try:
            year, t1, t2, p1, p2 = game
            year, p1, p2 = map(int, [year, p1, p2])
            
            cursor.execute(query, (t1, year))
            feature1 = np.array(cursor.fetchone()[2::])
            cursor.execute(query, (t2, year))
            feature2 = np.array(cursor.fetchone()[2::])
            feature = feature1/feature2
            
            # Calculate result of game 
            if (p1 - p2) > 0.:
                result = 1.
            else:
                result = 0.
            
            return feature, result
            
        except ValueError:
            return None, None
        
        except TypeError:
            return None, None
    
    def process_raw_data(self, team_data_csv_filename, what_to_do, cbb_db_name = 'cbb_data.db'):
        """
        Processes csv file named 'team_data_csv_filename' containing team data. If 
        'what_to_do' is set to 'csv' then a csv file is output containing the 
        following features:
            
        Team, Year, FGA, 3PA, FTA, TRB, AST, STL, BLK, TOV, PF, PTS, FGp, 3Pp, FTp
            
        If 'what_to_do' is set to 'sql' then a sqlite table named 'Team_Stats' is 
        created in the database titled 'cbb_db_name'. All appropriate features are 
        normalized to a 40-minute game. 
        """

        df = read_csv(team_data_csv_filename, na_values = [''])
        features = ['FGA','3PA','FTA','TRB','AST','STL','BLK','TOV','PF','PTS']
        pfeatures = ['Team','Year','FGp','3Pp','FTp']
        # Fill in minutes played. Assuming 40 mins/game
        df.MP = 40.*df.G 

        df_out = df[features]
        # Normalize features by minutes played
        df_out = df_out.div(df.MP, axis = 'index')
    
        df_out.insert(0, 'Team', df['Team'])
        df_out.insert(1, 'Year', df['Year'])
        df_out[pfeatures[2::]] = df[pfeatures[2::]]
    
        if what_to_do == 'csv':
            # Export to csv file
            output_name = team_data_csv_filename.replace('.csv', '_processed.csv')
            df_out.to_csv(output_name, float_format = '%7.4f')
        elif what_to_do == 'sql':
            # Export to SQL table
            con = lite.connect(cbb_db_name)
            with con:
                cur = con.cursor()
                pandas.io.sql.write_frame(df_out, 'Team_Stats', con, if_exists = 'replace')
                # Add index to Team and Year columns
                cur.execute('CREATE INDEX tp_indx ON Team_Stats(Team, Year);')
    
if __name__ == "__main__":
    pml = Prepare_for_ML('cbb_scoring_data.csv', 'cbb_data.db')
    pml()
