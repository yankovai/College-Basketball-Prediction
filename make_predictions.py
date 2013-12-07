import numpy as np
from sklearn import cross_validation as cv
from sklearn import linear_model
from sklearn import preprocessing
import sqlite3 as lite
import cPickle
import csv

def acquire_current_season_data(current_season = 2014):
    """
    Acquires all data structures needed to make predictions on current season.
    """
    
    from cbb_acquire_team_data import CBB_Acquire_Team_Data
    from cbb_acquire_game_data import CBB_Acquire_Scoring_Data
    from prepare_for_ml import Prepare_for_ML
    from make_ratings_dict import create_ratings_dict
    
    team_data_filename = 'team_data' + str(current_season) + '.csv'
    score_data_filename = 'score_data' + str(current_season) + '.csv'
    ratings_dict_filename = 'ratings_dict' + str(current_season) + '.cpickle'
    db_filename = 'cbb_data_' + str(current_season) + '.db'
    
    # Scrape for current season data
    cbb_teamdata = CBB_Acquire_Team_Data(current_season, current_season, team_data_filename)
    cbb_teamdata() 
    cbb_scoredata = CBB_Acquire_Scoring_Data(current_season, current_season, score_data_filename)
    cbb_scoredata()
    
    # Making ratings dictionary object
    create_ratings_dict(current_season, current_season, score_data_filename, ratings_dict_filename)
    
    # Prepare for predictions
    pml = Prepare_for_ML(score_data_filename, db_filename, ratings_dict_filename)
    pml.process_raw_data(team_data_filename)

def make_tableau_file(mp, current_season = 2014):
    """
    Produces a csv file containing predicted and actual game results for the 
    current season. Tableau uses the contents of the file to produce
    visualizations.
    """
    
    score_data_filename = 'score_data' + str(current_season) + '.csv'
    
    with open('tableau_input.csv','wb') as writefile:
        tableau_write = csv.writer(writefile)
        tableau_write.writerow(['Team 1', 'Opponent','Team 1 Points', 'Opponent Points', 'True Result', 'Predicted Result', 'Confidence'])
        
        with open(score_data_filename,'rb') as readfile:
            scores = csv.reader(readfile)
            scores.next()
            
            for score in scores:
                tableau_content = score[1::]
                # Append 'True Result'
                if int(tableau_content[2]) > int(tableau_content[3]):
                    tableau_content.append(1.)
                else:
                    tableau_content.append(0.)
                # Append 'Predicted Result' and 'Confidence'
                prediction_results = mp.make_prediction(tableau_content[0], tableau_content[1])
                tableau_content += list(prediction_results)
                
                tableau_write.writerow(tableau_content)
                    
class Make_Predictions(object):
    """
    Applies machine learning techniques to the scraped colleged basketball data
    and uses the resulting model to make predictions on unplayed games.
    """

    def __init__(self, feature_file, ratings_dict_filename, cbb_db_name, scale_features_bool = True):
        data = np.load(feature_file)
        self.X = data['X']
        self.y = data['y']
        self.scale_features_bool = scale_features_bool
        self.cbb_db_name = cbb_db_name
        
        with open(ratings_dict_filename,'rb') as cpickle_file:
            self.ratings_dict = cPickle.load(cpickle_file)
            
        if self.scale_features_bool:
            self.X = self.scale_features(self.X)
          
    def train_logistic_regression(self):
        """
        """
        
        self.logreg = linear_model.LogisticRegression()
        self.logreg.fit(self.X, self.y)
        
    def make_prediction(self, team1, team2):
        """
        Using prediction model, returns 1 if the model thinks team1 will beat
        team2. Otherwise, this function will return 0. 
        """
        
        query = 'SELECT * FROM Team_Stats WHERE Team = ?'
        rd = self.ratings_dict
        rd = rd[rd.keys()[0]]
        
        con = lite.connect(self.cbb_db_name)
        with con:
            cur = con.cursor()
            cur.execute(query, (team1,))
            feature1 = list(cur.fetchone()[2::]) + rd[team1].values()
            cur.execute(query, (team2,))
            feature2 = list(cur.fetchone()[2::]) + rd[team2].values()
            feature = np.array(feature1) - np.array(feature2)
        
        # Scale feature vector
        feature = self.scale_features(feature)
        # Make prediction
        prediction_output = self.logreg.predict(feature) 
        prediction_probability = max(self.logreg.predict_proba(feature)[0])
        
        return prediction_output[0], prediction_probability
        
    def scale_features(self, X):
        """
        """

        return preprocessing.scale(X)
        
    def cval_score(self):
        """
        """
        
        scores = cv.cross_val_score(self.logreg, self.X, self.y, cv = 10)
        print scores.mean(), scores.std()
    
    def rank_teams(self):
        """
        Use the predictive model to simulate how each team would fare against
        all the other teams. Rank the teams based on their winning percentage.
        """
        
        rd = self.ratings_dict
        team_names = rd[rd.keys()[0]].keys()
        nteams = len(team_names)
        team_win_percentages = np.zeros(nteams)
        
        for team, i in zip(team_names, range(nteams)):
            nwins = 0.
            for opponent in team_names:
                nwins += self.make_prediction(team, opponent)[0]
            
            team_win_percentages[i] = (nwins - 1.)/(nteams - 1.)
        
        # Output rankings to a csv file        
        rank_indices = np.argsort(-team_win_percentages)
        with open('rankings.csv','wb') as csvfile:
            rankings_file = csv.writer(csvfile)
            rankings_file.writerow(['Team 1', 'Win Percentage'])
            for rank_index in rank_indices:
                rankings_file.writerow([team_names[rank_index], team_win_percentages[rank_index]])
                
                
if __name__ == '__main__':
    # Uncomment to acquire data to make predictions for the current season.
#    acquire_current_season_data(current_season = 2014) 

    # Uncomment to train logistic regression model using archived data. Can make
    # predictions using Make_Predictions class.
    mp = Make_Predictions('features_archive.npz', 'ratings_dict2014.cpickle', 'cbb_data_2014.db')
    mp.train_logistic_regression()
    
    # Uncomment to rank the current season's teams. Need to have 
    # Make_Predictions class initiated. 
#    mp.rank_teams()
    
    # Uncomment to create data files for tableau visualization. Need to have
    # Make_Predictions class initiated.
    make_tableau_file(mp)



