import numpy as np
from sklearn import cross_validation as cv
from sklearn import linear_model
from sklearn import preprocessing
import sqlite3 as lite
import cPickle

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
        
        return prediction_output, prediction_probability
        
    def scale_features(self, X):
        """
        """

        return preprocessing.scale(X)
        
    def cval_score(self):
        """
        """
        
        scores = cv.cross_val_score(self.logreg, self.X, self.y, cv = 10)
        print scores.mean(), scores.std()


mp = Make_Predictions('features_archive.npz', 'ratings_dict2014.cpickle', 'cbb_data_2014.db')
mp.train_logistic_regression()

print mp.make_prediction('indiana', 'michigan')


