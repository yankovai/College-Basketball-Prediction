import pandas
import numpy as np
import cPickle

class Strength_of_Sched(object):
    """
    Calculates a metric for strength of schedule, overall rating, and margin 
    of victory. These are included as features. Strength of schedule and overall
    rating calculated using method described here:
    
    http://www.pro-football-reference.com/blog/?p=37
    """

    def __init__(self, scores_filename, year):
        self.year = year
        # Create dataframe for scoring data
        df = pandas.read_csv(scores_filename)
        df = df.dropna(how = 'any')
        self.df = df
        self.n_teams = df[df.Year == year].Team.nunique()

    def prepare_linear_system(self):
        """
        Prepares the data needed for the linear system in the strength of
        schedule methdoology.
        """

        df = self.df
        grouped =  df[df.Year == self.year].groupby('Team')

        # Store each team's unique index in a dictionary
        self.team_indices = {}
        for group, i in zip(grouped, range(self.n_teams)):
            self.team_indices.setdefault(group[0], i)

        self.margin = grouped.apply(self._get_margins)
        self.opponent_indices = grouped.apply(self._get_opponent_indices)
        	
    def _get_margins(self, group):
        """
        Given a team grouping from 'prepare_linear_system', this method returns
        the margin of victory for each game played during 'year', normalized by
        the number of games played.
        """

        n_games = float(len(group['Team_Points']))
        total_margin = np.sum(group['Team_Points'] - group['Opponent_Points'])

        return total_margin/n_games

    def _get_opponent_indices(self, group):
        """
        Given a team grouping from 'prepare_linear_system', this method returns
        the indices of all oponents played along with the number of opponents.
        """

        indices = []
        opponents = group['Opponent']
		
        for opponent in opponents:
            indice = self.team_indices.get(opponent, None)    
            if indice:
                indices.append(indice)

        n_opponents = len(indices)

        return indices, n_opponents

    def calculate_rankings(self):
        """
        Solves linear system in strength of schedule methodology.
        """
        
        A = np.zeros([self.n_teams, self.n_teams])
        margin = -1.*np.array(self.margin)
        
        for i, indices in zip(range(self.n_teams), self.opponent_indices):
            A[i, indices[0]] = 1./indices[1]
        
        A -= np.eye(self.n_teams)
        x = np.linalg.solve(A, margin)
        
        return x
        
    def __call__(self):
        """
        Returns a vector of rating values, sorted in the original order of the 
        database.          
        """
        
        self.prepare_linear_system()
        ratings = self.calculate_rankings()
        
        margin = np.array(self.margin)
        # strength of schedule
        sos = ratings - margin       
        
        team_ratings = {}
        for i in range(self.n_teams):
            dict_indx = self.team_indices.values().index(i)
            team_name = self.team_indices.keys()[dict_indx]
            team_attrb = {'sos': sos[i], 'margin': margin[i], 'rating': ratings[i]}
            team_ratings.setdefault(team_name, team_attrb)
        
        return team_ratings

if __name__ == '__main__':
    """
    Create ratings_dict dictionary. Use example:
    ratings_dict[2003]['air-force'].values()
    """
    year1 = 2003
    year2 = 2013
    ratings_dict = {}
    for year in range(year1, year2 + 1):
        ssd = Strength_of_Sched('cbb_scoring_data.csv', year)
        team_ratings = ssd()
        ratings_dict.setdefault(year, team_ratings)

    # Export to cpickle file
    with open('ratings_dict.cpickle','wb') as cpickle_file:
        cPickle.dump(ratings_dict, cpickle_file)











