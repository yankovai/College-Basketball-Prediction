College-Basketball-Prediction
=============================

Predict the outcome when division I college basketball teams compete.


'cbb_acquire_team_data.py' 
--------------------------

The purpose of this python script is to obtain descriptive statistics of team 
performance from www.sports-reference.com/cbb. Team descriptive statistics are,
for example, points per game, free throw percentegae, and the number of blocks
per game. Within this file is a class called 'CBB_Acquire_Team_Data', which 
accepts a span of years and a csv file name as input. This class scrapes the 
sports-reference site for descriptive statistics for every division I college
basketball team that played within the span of years input by the user. The 
results are output to the specified csv file. Each descriptive statistic will be
used as a feature in a predictive model.   

'cbb_acquire_game_data.py' 
--------------------------

Scrapes www.sports-reference.com/cbb for the results of all games played during 
some span of seasons. The user inputs the starting season, an end season, and a 
csv file name to a class named 'CBB_Acquire_Scoring_Data'. For every game in the
span of season the class will output the two teams playing and points scored by
each team to the specified csv file. The results are used to form the
classification in a predictive model.

'make_ratings_dict.py'
---------------------

Using the description in http://www.pro-football-reference.com/blog/?p=37, this 
python script calculates several additional team descriptive statistics based on
the results from 'cbb_acquire_game_data.py'. Specifically, the statistics output
by the class 'Strength_of_Sched' summarize the degree of competion faced be each
team during a given season. The feature 'strength of schedule' accounts for how
easy or difficult a team's schedule has been. The feature 'margin' summarizes 
a team's margin of victory against all of its opponents. Finally, the feature 
'rating' combines both the margin and strength of schedule of each team to 
produce a coarse metric that can be used to rank all the teams. All the features
are output to a dictionary named 'ratings_dict.cpickle'. 

