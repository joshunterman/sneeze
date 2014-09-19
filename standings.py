#!/usr/bin/env python
import sys
import os
import getopt
#import mail
import json
import yahooapi
import pickle
import prettytable
import datetime
import ConfigParser

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def usage():
    return "test.py"

class Config():
    def __init__(self, configfile):
        self.dict={}
        config = ConfigParser.ConfigParser()
        config.read(configfile)
        sections=config.sections()
        for section in sections:
            # print section
            self[section]={}
            options = config.options(section)
            # print options
            for option in options:
                self[section][option]=config.get(section, option)

    def __getitem__(self,key):
        return self.dict[key]

    def __setitem__(self,key,value):
        self.dict[key]=value

def valueFromStat(stat):
    return stat['stat']['value']

def formatFloat(numvar,digits=2):
    s="%."+str(digits)+"f"
    return s % numvar

def teamFromStandings(team,config):
    name = team['team'][0][2]['name']
    rank = team['team'][2]['team_standings']['rank']
    points_for = team['team'][2]['team_standings']['points_for']
    points_change = team['team'][2]['team_standings']['points_change']
    points_back = team['team'][2]['team_standings']['points_back']
    # shouldn't be hard-coded:
    games = int(valueFromStat(team['team'][1]['team_stats']['stats'][1])) # stat_id : 1
    pitchingStartIndex = 1 + int(config['league']['numbattingstats'])
    batting_points = sum(map(lambda x:float(valueFromStat(x)),team['team'][1]['team_points']['stats'][1:pitchingStartIndex]))
    b_avg = batting_points / games
    b_avgStr = formatFloat(b_avg,3)
    # shouldn't be hard-coded:
    innings = float(valueFromStat(team['team'][1]['team_stats']['stats'][14])) # stat_id : 50
    pitching_points = sum(map(lambda x:float(valueFromStat(x)),team['team'][1]['team_points']['stats'][pitchingStartIndex:]))
    p_avg = pitching_points / innings
    p_avgStr = formatFloat(p_avg,3)
    projection = formatFloat(b_avg * 115 * 14 + p_avg * 1350)
    #return "%s,%s,%s,%s,%s" % (rank, name, points_for, points_change, points_back)
    return [rank, name, points_for, points_change, points_back, b_avgStr, p_avgStr, projection]

def tableFromTeams(teams):
    x = prettytable.PrettyTable(["Rank", "Name", "Points", "Change", "Back", "B_Avg", "P_Avg", "Tot_Proj"])
    x.align["Rank"] = "r"
    x.align["Name"] = "l" # Left align team names
    x.align["Points"] = "r"
    x.align["Change"] = "r"
    x.align["Back"] = "r"
    x.align["B_Avg"] = "r"
    x.align["P_Avg"] = "r"
    x.align["Tot_Proj"] = "r"
    x.padding_width = 1 # One space between column edges and contents (default)
    for team in teams:
        x.add_row(team)
    return x

def go(configfile=None):
    if(configfile):
        config = Config(configfile)
    else:
        config = Config("config")
    keyfile=config['connection']['keyfile']
    tokenfile=config['connection']['tokenfile']
    leagueid=config['league']['id']
    raw_data=None
    today = datetime.datetime.now().strftime("%Y%m%d")
    f = "cache/standings.%s" % today
    if os.path.isfile(f):
        print "reading cache for %s" % today
        with open(f,'r') as the_file:
            raw_data = pickle.load(the_file)
    else:
        print "go get data for %s" % today
        api = yahooapi.YahooAPI(keyfile,tokenfile)
        query="fantasy/v2/leagues;league_keys=%s/standings" % leagueid
        response = api.request(query)
        raw_data = json.loads(response.text)
        with open(f,'w') as the_file:
            pickle.dump(raw_data, the_file)
    standings = raw_data['fantasy_content']['leagues']['0']['league'][1]['standings'][0]['teams']
    teams = []
    numTeams=int(config['league']['numteams'])
    for i in range(numTeams):
        teams.append(teamFromStandings(standings[str(i)],config))
    teams = sorted(teams, key=lambda t: t[-1], reverse=True)
    table = tableFromTeams(teams)
    f = "results/standings.%s.txt" % today
    with open(f,'w') as the_file:
        the_file.write(str(table))
    #mail.mail(f,"Standings %s" % today,["sneeze@unterman.net"],"")
    print str(table)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hc:", ["help,config"])
        except getopt.error, msg:
            raise Usage(msg)
        c = None
        for o, a in opts:
            if o in ("-h", "--help"):
                raise Usage(usage())
            elif o in ("-c", "--config"):
                c = a
            else:
                raise Usage(usage())
        if(c != None):
            go(c)
        else:
            go()
            #raise Usage(usage())
    except Usage, err:
        print(err.msg)
        print("for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())
