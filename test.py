#!/usr/bin/env python
import sys
import getopt
#import mail
import json
import yahooapi
import prettytable
import datetime

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def usage():
    return "test.py"

def valueFromStat(stat):
    return stat['stat']['value']

def formatFloat(numvar):
    return "%.2f" % numvar

def teamFromStandings(team):
    name = team['team'][0][2]['name']
    rank = team['team'][2]['team_standings']['rank']
    points_for = team['team'][2]['team_standings']['points_for']
    points_change = team['team'][2]['team_standings']['points_change']
    points_back = team['team'][2]['team_standings']['points_back']
    games = int(valueFromStat(team['team'][1]['team_stats']['stats'][1])) # stat_id : 1
    batting_points = sum(map(lambda x:float(valueFromStat(x)),team['team'][1]['team_points']['stats'][1:14]))
    b_avg = formatFloat(batting_points / games)
    innings = float(valueFromStat(team['team'][1]['team_stats']['stats'][14])) # stat_id : 50
    pitching_points = sum(map(lambda x:float(valueFromStat(x)),team['team'][1]['team_points']['stats'][14:]))
    p_avg = formatFloat(pitching_points / innings)
    #return "%s,%s,%s,%s,%s" % (rank, name, points_for, points_change, points_back)
    return [rank, name, points_for, points_change, points_back, b_avg, p_avg]

def go(configfile=None):
    #f = open("keyfile", "r")
    #print f.readlines()[0]
    api = yahooapi.YahooAPI("keyfile","tokenfile")
    query='fantasy/v2/leagues;league_keys=328.l.82872/standings'
    #query='https://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys=328.l.82872/standings'
    #querystring = 'http://query.yahooapis.com/v1/yql?q==select * from fantasysports.leagues.standings where owner_guid="jwunterman" league_key="328.l.82872"'
    #query = 'http://query.yahooapis.com/v1/yql?q==select * from fantasysports.leagues.standings where league_key="328.l.82872"'
    #query = 'v1/yql?q==select * from fantasysports.leagues.standings where owner_guid="jwunterman" league_key="328.l.82872"'
    response = api.request(query)
    raw_data = json.loads(response.text)
    standings = raw_data['fantasy_content']['leagues']['0']['league'][1]['standings'][0]['teams']
    x = prettytable.PrettyTable(["Rank", "Name", "Points", "Change", "Back", "B_Avg", "P_Avg"])
    x.align["Rank"] = "r"
    x.align["Name"] = "l" # Left align team names
    x.align["Points"] = "r"
    x.align["Change"] = "r"
    x.align["Back"] = "r"
    x.align["B_Avg"] = "r"
    x.align["P_Avg"] = "r"
    x.padding_width = 1 # One space between column edges and contents (default)
    for i in range(20):
        x.add_row(teamFromStandings(standings[str(i)]))
    d = datetime.datetime.now().strftime("%Y%m%d")
    f = "results/standings.%s.txt" % d
    with open(f,'w') as the_file:        
        the_file.write(str(x))
    #mail.mail(f,"Standings %s" % d,["sneeze@unterman.net"],"")
    print str(x)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:", ["help,file"])
        except getopt.error, msg:
            raise Usage(msg)
        f = None
        for o, a in opts:
            if o in ("-h", "--help"):
                raise Usage(usage())
            elif o in ("-f", "--file"):
                f = a
            else:
                raise Usage(usage())
        if(f != None):
            go(f)
        else:
            go()
            #raise Usage(usage())
    except Usage, err:
        print(err.msg)
        print("for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())
