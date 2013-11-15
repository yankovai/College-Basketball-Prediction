from bs4 import BeautifulSoup
import urllib2
import time
import csv

class CBB_Acquire_Team_Data(object):
    """
    Creates a csv file containing cummulative data by season for each division I
    college basketball team that played games between input 'year1' and 'year2'.
    """

    def __init__(self, year1, year2, csv_filename):
        self.year1 = year1
        self.year2 = year2
        self.get_team_names(year1, year2)
        self.csv_filename = csv_filename
        self.progress_id = 0
        self.total_work = (year2 - year1 + 1)*len(self.team_names)

    def __call__(self):
        """
        Creates the csv output file for further analysis. 
        """

        with open(self.csv_filename, 'wb') as csvfile:
            self.csvwriter = csv.writer(csvfile)
            self.csvwriter.writerow(['Team','Year','G','MP','FG','FGA','FGp', \
                                     '3P','3PA','3Pp','FT','FTA','FTp','ORB', \
                                     'DRB','TRB','AST','STL','BLK','TOV','PF',\
                                     'PTS','PTSg'])

            for year in range(self.year1, self.year2 + 1):
                for team_name in self.team_names:
                    team_stats = [team_name, year]
                    team_stats += self.get_team_stats(team_name, year)
                    self.csvwriter.writerow(team_stats)
                    self._print_progress()
                    time.sleep(1)

    def _print_progress(self):
        """
        Prints fraction of total work completed.
        """
        
        self.progress_id += 1
        print 'Completed %d of %d' %(self.progress_id, self.total_work)
        
    def get_team_stats(self, team_name, year):
        """
        Returns a list with the following cummulative data for a NCAA basketball
        team in a given year:
        
        G, MP, FG, FGA, FG%, 3P, 3PA, 3P%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL,
        BLK, TOV, PF, PTS, PTS/G

        Using standard notation to describe the returned statistics. 
        """
        
        base_url = 'http://www.sports-reference.com/cbb/schools/' + \
                        team_name + '/' + str(year) + '.html'

        response = urllib2.urlopen(base_url)
        content = response.read()
        soup = BeautifulSoup(content)
        soup_results = soup.find('td', text='Team')
        team_stats = []
        
        if soup_results:
            soup_results = soup_results.parent()
            
            for result in soup_results[1::]:
                if result.string:
                    team_stats.append(float(result.string))
                else:
                    team_stats.append(None)
        
        else:
            team_stats += [None]*21

        return team_stats 
               
    def get_team_names(self, year1, year2):
        """
        Returns a list of all team names that played games between 'year1' and
        'year2'. 
        """

        base_url = 'http://www.sports-reference.com/cbb/schools/'
        response = urllib2.urlopen(base_url)
        content = response.read()
        soup = BeautifulSoup(content)
        soup_results = soup.findAll('tr', {'class':''})
        extract_name = lambda name: name.split('/')[3]
        team_names = []
        
        for result in soup_results[1::]:
            year_span = result.findAll('td', {'align':'center'})       
            year_span = map(int, [year.text for year in year_span])

            if year_span[0] <= year1 and year_span[1] >= year2:
                team_name = result.find('a', href = True).get('href')
                team_name = extract_name(team_name)
                team_names.append(str(team_name))

        self.team_names = team_names

if __name__ == "__main__":
    # Finished 638
    cbb = CBB_Acquire_Team_Data(2003, 2013, 'cbb_team_data.csv')
    cbb()



