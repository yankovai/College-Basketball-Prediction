from cbb_acquire_team_data import CBB_Acquire_Team_Data
from bs4 import BeautifulSoup
import urllib2
import time
import csv

class CBB_Acquire_Scoring_Data(object):
    """
    Creates a csv file containing all the matchup results between division I
    college basketball teams for all seasons between inputs 'year1' and 'year2'.
    """

    def __init__(self, year1, year2, csv_filename):
        self.cbb = CBB_Acquire_Team_Data(year1, year2, '')
        self.year1 = year1
        self.year2 = year2
        self.csv_filename = csv_filename
        
    def __call__(self, start_id=1):
        """
        Creates the csv output file for further analysis. The variable 
        'start_id' specifies which data entry out of 'total_work' to start 
        recording in the output csv file. See the 'CBB_Acquire_Team_Data' class.
        """
        
        with open(self.csv_filename, 'wb') as csvfile:
            self.csvwriter = csv.writer(csvfile)
            self.csvwriter.writerow(['Year','Team','Opponent','Team_Points', \
                                        'Opponent_Points'])
                                        
            for year in range(self.year1, self.year2 + 1):
                for team_name in self.cbb.team_names:
                    if self.cbb.progress_id >= start_id: 
                        team_scores = self.get_team_scores(team_name, year)
                        self.csvwriter.writerows(team_scores)
                        self.cbb._print_progress()
                        time.sleep(1)
                    else:
                        self.cbb.progress_id += 1
            
    def get_team_scores(self, team_name, year):
        """
        Returns a list of lists. In each sublist is the result of every matchup
        for 'team_name" in the season specified by the input 'year'. The 
        sublists contain the following entries:
        
        Year, Team_Name, Opponent, Team_Name Points, Opponent Points
        """
        
        base_url = 'http://www.sports-reference.com/cbb/schools/' + \
                        team_name + '/' + str(year) + '-schedule.html'
        extract_name = lambda name: name.split('/')[3]
        response = urllib2.urlopen(base_url)
        content = response.read()
        soup = BeautifulSoup(content)
        title = soup.find('title').text
        
        if 'Schedule and Results' in title:
            team_scores = []
            soup_results = soup.find('table', {'id': 'schedule'}).tbody.findAll('tr',{'class':''})
    
            for result in soup_results:
                try:
                    result = result.findAll('td')
                    opponent = result[4].a.get('href')
                    opponent = extract_name(opponent)
                    scores = map(int, [score.string for score in result[7:9]])
                    team_score = [year, team_name, opponent] + scores
                    team_scores.append(team_score)
                except AttributeError:
                    pass        
                except TypeError:
                    pass
                
        else:
            team_scores = [[year, team_name] + [None]*3]
        
        return team_scores

if __name__ == "__main__":
    cbb = CBB_Acquire_Scoring_Data(2003, 2013, 'cbb_scoring_data.csv')
    cbb()



