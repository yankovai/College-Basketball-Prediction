from pandas import *

def process_team_data(team_data_csv_filename):
	"""
	Processes csv file named 'team_data_csv_filename' containing team data. A
	csv file is output containing the following features:

	FGA, 3PA, FTA, TRB, AST, STL, BLK, TOV, PF, PTS, Team, Year, FGp, 3Pp, FTp

	All appropriate features are normalized to a 40-minute game. 
	"""

	df = read_csv('cbb_team_data2.csv', na_values = [''])
	features = ['FGA','3PA','FTA','TRB','AST','STL','BLK','TOV','PF','PTS']
	pfeatures = ['Team','Year','FGp','3Pp','FTp']
	# Fill in minutes played. Assuming 40 mins/game
	df.MP = 40.*df.G 

	df_out = df[features]
	# Normalize features by minutes played
	df_out = df_out.div(df.MP, axis = 'index')

	df_out[pfeatures] = df[pfeatures]

	# Export to csv file
	output_name = team_data_csv_filename.replace('.csv', '_processed.csv')
	df_out.to_csv(output_name, float_format = '%7.4f')  

process_team_data('cbb_team_data2.csv')
# data_out[data_out.Team == 'duke'].AST