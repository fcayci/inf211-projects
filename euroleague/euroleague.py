import random
import flask
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect, url_for

from ast import literal_eval

# teams = [
#     "ALBA Berlin",
#     "Anadolu Efes Istanbul",
#     "AS Monaco",
#     "AX Armani Exchange Milan",
#     "Bitci Baskonia Vitoria-Gasteiz",
#     "Crvena Zvezda mts Belgrade",
#     "CSKA Moscow",
#     "FC Barcelona",
#     "FC Bayern Munich",
#     "Fenerbahce Beko Istanbul",
#     "LDLC ASVEL Villeurbanne",
#     "Maccabi Playtika Tel Aviv",
#     "Olympiacos Piraeus",
#     "Panathinaikos OPAP Athens",
#     "Real Madrid",
#     "UNICS Kazan",
#     "Zalgiris Kaunas",
#     "Zenit St Petersburg"
# ]

def generate_players(n):
    '''generates random names'''
    import string

    s = string.ascii_lowercase
    p = []

    for i in range(n):
        name = ''
        for j in range(random.randint(5, 10)):
            name += random.choice(s)
        lastname = ''
        for j in range(random.randint(5, 10)):
            lastname += random.choice(s)
        p.append((name.capitalize(), lastname.capitalize()))

    return p

# players = generate_players(5 * len(teams))

teams = 'teams.txt'
players = 'players.txt'
managers = 'managers.txt'

class Person:

    def __init__(self, name, lastname):
        self.name = name.capitalize()
        self.lastname = lastname.capitalize()

    def get_name(self):
        return self.name + ' ' + self.lastname

    def __str__(self):
        return self.get_name()

    def __lt__(self, other):
        if self.lastname == other.lastname:
            return self.name < other.name
        return self.lastname < other.lastname

class Player(Person):

    pid = 1

    def __init__(self, name, lastname):
        Person.__init__(self, name, lastname)

        self.player_id = Player.pid
        Player.pid += 1
        self._random_power()
        self.perf = []
        self.last_match_perf = []
        self.team = None

    def reset(self):
        self.perf.clear()

    def _random_power(self, mn=4, mx=8):
        self.power = random.randint(mn, mx)

    def get_id(self):
        return self.player_id

    def get_power(self):
        return self.power

    # def get_points_for_week(self, week_no):
    #     if week_no == 0:
    #         return 0
    #     elif len(self.perf) >= 1:
    #         return self.perf[week_no-1]
    #     else:
    #         return 0

    def set_team(self, t):
        self.team = t

    def get_team(self):
        return self.team

    def add_to_points(self, p):
        self.perf.append(p)

    def get_points_detailed(self):
        return self.perf[:]

    def get_points(self):
        return sum(self.perf)

    def __lt__(self, other):
        a = self.get_points()
        b = other.get_points()

        if a == b:
            return Person.__lt__(self, other)
        else:
            return a > b

class Manager(Person):

    mid = 1

    def __init__(self, name, lastname):

        Person.__init__(self, name, lastname)

        self.team = None
        self.manager_id = Manager.mid
        Manager.mid += 1

        self.perf = []

    def get_id(self):
        return self.manager_id

    def reset(self):
        self.perf.clear()

    def add_influence(self, i):
        self.perf.append(i)

    def get_points(self):
        return sum(self.perf)

    def get_points_detailed(self):
        return self.perf[:]

    def set_team(self, t):
        self.team = t

    def get_team(self):
        return self.team

    def __lt__(self, other):
        a = self.get_points()
        b = other.get_points()

        if a == b:
            return Person.__lt__(self, other)
        else:
            return a > b


class Team:

    tid = 1

    def __init__(self, team_name, manager, players):

        self.name = team_name
        self.manager = manager
        self.manager.set_team(self)
        self.team_id = Team.tid
        Team.tid += 1

        self.players = []
        self.matches = []
        self.wins = 0
        self.loses = 0
        self.scored = 0
        self.conceded = 0
        # self.wins = []
        self.points = 0

        for player in players:
            self.players.append(player)
            player.set_team(self)

    def reset(self):
        for p in self.players:
            p.reset()
        self.manager.reset()
        self.matches = []
        self.wins = 0
        self.loses = 0
        self.scored = 0
        self.conceded = 0
        self.points = 0
        Team.tid = 1

    def get_id(self):
        return self.team_id

    def get_name(self):
        return self.name

    def get_roster(self):
        return self.players

    def get_manager(self):
        return self.manager

    def __str__(self):
        return self.get_name()

    def __lt__(self, other):
        if self.points == other.points:
            a = self.scored - self.conceded
            b = other.scored - other.conceded
            return a > b
        else:
            return self.points > other.points

    def get_fixture(self):
        return self.matches

    def add_to_fixture(self, m):
        self.matches.append(m)

    def add_result(self, scored, conceded):
        self.scored += scored
        self.conceded += conceded
        if scored > conceded:
            self.wins += 1
            self.points += 2
        else:
            self.loses += 1
            self.points += 1

        self.players.sort()

    def get_points(self):
        return self.points

    def get_scored(self):
        return self.scored

    def get_conceded(self):
        return self.conceded

    def get_wins(self):
        return self.wins

    def get_losses(self):
        return self.loses


class Match:

    def __init__(self, home_team, away_team, week_no):

        self.home_team = home_team
        self.away_team = away_team
        self.week_no = week_no
        self._no_of_periods = 4
        self.score = []
        self.final_score = (0, 0)
        self.winner = None
        self.played = False
        self.hpscores = [0, 0, 0, 0]
        self.apscores = [0, 0, 0, 0]
        self.manscores = [0, 0, 0, 0]

    def is_played(self):
        return self.played

    def _play_one_period(self):
        if self.is_played():
            return

        home_score = 0
        for i, player in enumerate(self.home_team.get_roster()):
            ps = 0
            mood = random.randint(-5, 5)
            ps += mood
            ps += player.get_power()
            if ps > 10:
                ps = 10
            if ps < 0:
                ps = 0
            home_score += ps
            self.hpscores[i] += ps

        away_score = 0
        for i, player in enumerate(self.away_team.get_roster()):
            ps = 0
            mood = random.randint(-5, 5)
            ps += mood
            ps += player.get_power()
            if ps > 10:
                ps = 10
            if ps < 0:
                ps = 0
            away_score += ps
            self.apscores[i] += ps

        self.score.append((home_score, away_score))
        a = 0
        b = 0
        for x, y in self.score:
            a += x
            b += y
        self.final_score = (a, b)

    def play(self):
        if self.is_played():
            return

        self.hpscores = [0, 0, 0, 0, 0]
        self.apscores = [0, 0, 0, 0, 0]
        # first play 4 periods
        for i in range(self._no_of_periods):
            self._play_one_period()

        # add manager influence
        iff1 = random.randint(-10, 10)
        self.home_team.get_manager().add_influence(iff1)
        iff2 = random.randint(-10, 10)
        self.away_team.get_manager().add_influence(iff2)
        self.final_score = (self.final_score[0] + iff1, self.final_score[1] + iff2)

        # play more periods if the score is equal
        # until one winner is decided
        while self.final_score[0] == self.final_score[1]:
            self._play_one_period()

        for i, player in enumerate(self.home_team.get_roster()):
            player.add_to_points(self.hpscores[i])

        for i, player in enumerate(self.away_team.get_roster()):
            player.add_to_points(self.apscores[i])

        self.home_team.add_result(self.final_score[0], self.final_score[1])
        self.away_team.add_result(self.final_score[1], self.final_score[0])

        if self.final_score[0] > self.final_score[1]:
            self.winner = self.home_team
        else:
            self.winner = self.away_team

        self.played = True

    def get_match_score(self):
        if self.played:
            return self.final_score
        else:
            return None

    def __str__(self):
        if not self.played:
            s = f'{self.home_team.get_name()} vs. {self.away_team.get_name()}'
        else:
            s = f'{self.home_team.get_name()} ({self.final_score[0]}) vs. ({self.final_score[1]}) {self.away_team.get_name()}'
        return s

    def get_teams(self):
        return self.home_team, self.away_team

    def get_home_team(self):
        return self.home_team

    def get_away_team(self):
        return self.away_team

class Season:

    def __init__(self, team_file, managers_file, players_file):

        teams = self.read_team_file(team_file)
        players = self.read_people_file(players_file)
        managers = self.read_people_file(managers_file)
        self.teams = []
        self.players = []
        self.managers = []
        self.fixture = []
        self.next_week = 0

        for ii, team in enumerate(teams):
            manager = Manager(managers[ii][0], managers[ii][1])
            self.managers.append(manager)
            roster = []
            for i in range(5):
                x = players[5*ii+i]
                p = Player(x[0], x[1])
                roster.append(p)
                self.players.append(p)
            self.teams.append(Team(team, manager, roster))

        random.shuffle(self.teams)
        self.build_fixture()

    def read_team_file(self, filename):
        a = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                a.append(line.strip())
        return a

    def read_people_file(self, filename):
        a = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                a.append(line.strip().split(' '))

        return a

    def build_fixture(self):
        return self.build_fixture_berger()

    def build_fixture_circle(self):
        '''
        https://en.wikipedia.org/wiki/Round-robin_tournament
        '''
        self.fixture = []
        for t in self.teams:
            t.reset()

        team0 = self.teams[0]
        teams = self.teams[1:]

        # For the first half of the season

        # Go for each week
        for i in range(len(teams)):
            # Week matches
            r = []
            # Add first team
            m = Match(team0, teams[-1], i+1)
            r.append(m)
            team0.add_to_fixture(m)
            teams[-1].add_to_fixture(m)
            # Add rest of the teams
            for j in range(len(teams)//2):
                m = Match(teams[j], teams[-2-j], i+1)
                r.append(m)
                teams[j].add_to_fixture(m)
                teams[-2-j].add_to_fixture(m)
            # shuffle matches
            random.shuffle(r)
            # add week matches to the fixture
            self.fixture.append(r)
            teams = teams[1:] + [teams[0]]

        # For the second half of the season
        w = len(self.fixture)
        for i in range(w):
            # week matches
            r = []
            for match in self.fixture[i]:
                t = match.get_teams()
                m = Match(t[1], t[0], w+i+1)
                r.append(m)
                t[0].add_to_fixture(m)
                t[1].add_to_fixture(m)
            # shuffle matches
            random.shuffle(r)
            # add week matches to the fixture
            self.fixture.append(r)


    def build_fixture_berger(self):
        '''berger method'''
        self.fixture = []
        for t in self.teams:
            t.reset()
        t18 = self.teams[-1]
        teams = self.teams[:-1]

        odd = True
        # Go for each week
        for i in range(len(teams)):
            # Week matches
            r = []
            # Add first team, alternating home / away
            if odd:
                m = Match(t18, teams[0], i+1)
                odd = not odd
            else:
                m = Match(teams[0], t18, i+1)
            odd = not odd

            r.append(m)
            t18.add_to_fixture(m)
            teams[0].add_to_fixture(m)

            # Add rest of the teams
            for j in range(1, (len(teams)+1)//2):
                m = Match(teams[j], teams[-j], i+1)
                r.append(m)
                teams[j].add_to_fixture(m)
                teams[-j].add_to_fixture(m)
            # shuffle matches
            random.shuffle(r)
            # add week matches to the fixture
            self.fixture.append(r)
            teams = teams[7:] + teams[:7]

       # For the second half of the season
        w = len(self.fixture)
        for i in range(w):
            # week matches
            r = []
            for match in self.fixture[i]:
                t = match.get_teams()
                m = Match(t[1], t[0], w+i+1)
                r.append(m)
                t[0].add_to_fixture(m)
                t[1].add_to_fixture(m)
            # shuffle matches
            random.shuffle(r)
            # add week matches to the fixture
            self.fixture.append(r)

    def get_week_fixture(self, week_no):
        if week_no == 0:
            return None
        elif week_no > len(self.fixture):
            return None
        else:
            return self.fixture[week_no-1]

    def play_week(self):
        if self.next_week == len(self.fixture):
            return

        for match in self.fixture[self.next_week]:
            match.play()
        self.next_week += 1
        self.players.sort()
        self.teams.sort()
        self.managers.sort()

    def get_teams(self):
        return self.teams

    def get_players(self):
        return self.players

    def get_best_player(self):
        return self.players[0]

    def get_best_manager(self):
        return self.managers[0]

    def get_managers(self):
        return self.managers

    def get_week_no(self):
        return self.next_week

    def reset(self):
        Player.pid = 1
        Team.tid = 1
        Manager.mid = 1
        self.players = []
        self.managers = []
        self.fixture = []
        self.__init__(teams, managers, players)

app = Flask(__name__)

plays = {}
play_counter = 1


def fill_season_table():
    # These are the column names
    c = ['Team', 'GP', 'W', 'L', 'Pts+', 'Pts-', 'Diff']

    # Holds the team information
    td = {}
    for i, t in enumerate(plays[session['season']].get_teams()):
        a = t.get_scored()
        b = t.get_conceded()
        td[i] = {}

        # id will be used for navigation
        td[i]['id'] = t.get_id()

        # columns should match the column names
        td[i]['col1'] = t.get_name()
        td[i]['col2'] = t.get_wins() + t.get_losses()
        td[i]['col3'] = t.get_wins()
        td[i]['col4'] = t.get_losses()
        td[i]['col5'] = a
        td[i]['col6'] = b
        td[i]['col7'] = a-b

    # Get the week number
    w = plays[session['season']].get_week_no()

    nw = {}
    if plays[session['season']].get_week_fixture(w+1) is not None:
        for i, m in enumerate(plays[session['season']].get_week_fixture(w+1)):
            nw[i] = {'col1': m.get_home_team()}
            if m.is_played():
                s = m.get_match_score()
                nw[i]['col2'] = s[0]
                nw[i]['col4'] = s[1]
            else:
                nw[i]['col2'] = ''
                nw[i]['col4'] = ''
            nw[i]['col3'] = ' - '
            nw[i]['col5'] = m.get_away_team()


    pw = {}
    if plays[session['season']].get_week_fixture(w) is not None:
        for i, m in enumerate(plays[session['season']].get_week_fixture(w)):
            pw[i] = {'col1': m.get_home_team()}
            if m.is_played():
                s = m.get_match_score()
                pw[i]['col2'] = s[0]
                pw[i]['col4'] = s[1]
            else:
                pw[i]['col2'] = ''
                pw[i]['col4'] = ''
            pw[i]['col3'] = ' - '
            pw[i]['col5'] = m.get_away_team()

    # return all three
    return c, td, w, nw, pw


def fill_team_table(team):
    c1 = {}
    a = max(0, team.get_scored())
    b = max(0, team.get_conceded())
    c1['Games Played'] = max(0, team.get_wins() + team.get_losses())
    c1['Wins'] = max(0, team.get_wins())
    c1['Loses'] = max(0, team.get_losses())
    c1['Points Scored'] = a
    c1['Points Conceded'] = b
    c1['Points Difference'] = a - b

    c2 = []
    for player in team.get_roster():
        a = {}
        a['name'] = player.get_name()
        a['id'] = player.get_id()
        a['points'] = player.get_points()
        c2.append(a)

    c3 = {}
    for i, m in enumerate(team.get_fixture()):
        c3[i] = {'col1': m.get_home_team()}
        if m.is_played():
            s = m.get_match_score()
            c3[i]['col2'] = m.get_match_score()[0]
            c3[i]['col4'] = m.get_match_score()[1]
        else:
            c3[i]['col2'] = ''
            c3[i]['col4'] = ''
        c3[i]['col3'] = ' - '
        c3[i]['col5'] = m.get_away_team()

    w = plays[session['season']].get_week_no()
    return c1, c2, c3, w


@app.route('/', methods=['GET', 'POST'])
def start():
    global play_counter
    global plays

    if request.method == 'GET':
        if 'season' in session:
            if session['season'] not in plays.keys():
                del session['season']

        if 'season' not in session:
            print("Starting")
            session['season'] = play_counter
            plays[play_counter] = Season(teams, managers, players)
            play_counter += 1
        print('plays', plays)

    else:
        comm = request.form['command']

        if comm == 'Reset Season':
            plays[session['season']].reset()
            del plays[session['season']]
            del session['season']
            return redirect(url_for('start'))

        elif comm == 'Play Next Week':
            plays[session['season']].play_week()

        elif comm == 'Player Stats':
            return redirect(url_for('players_stats'))

        elif comm == 'Manager Stats':
            return redirect(url_for('managers_stats'))

    try:
        c, td, w, nw, pw = fill_season_table()
        return render_template('euroleague.html', week=w, columns=c, table_data=td, nw=nw, pw=pw)
    except KeyError:
        return redirect(url_for('start'))


@app.route('/team/<tid>', methods=['GET'])
def team_stats(tid):
    # Make sure we cut through all the weird ones
    if int(tid) <= 0 or int(tid) > len(plays[session['season']].get_teams()):
        return redirect(url_for('start'))

    for team in plays[session['season']].get_teams():
        if team.get_id() == int(tid):
            break

    title = team.get_name()
    ts, ps, ms, w = fill_team_table(team)

    manager = {'name' : team.get_manager().get_name(), 'id' : team.get_manager().get_id()}

    return render_template('team_stats.html', title=title, ts=ts, ps=ps, ms=ms, m=manager, week=w)


@app.route('/player/<pid>', methods=['GET'])
def player_stats(pid):
    if int(pid) <= 0 or int(pid) > len(plays[session['season']].get_players()):
        return redirect(url_for('start'))

    for player in plays[session['season']].get_players():
        if player.get_id() == int(pid):
            break

    title = player.get_name()

    ps = {}

    for i, p in enumerate(player.get_points_detailed()):
        ps['Week ' + str(i+1)] = p

    ps['Total Pts'] = player.get_points()

    t = {}
    t['name'] = player.get_team().get_name()
    t['id'] = player.get_team().get_id()

    return render_template('player_stats.html', title=title, team=t, stats=ps)

@app.route('/manager/<mid>', methods=['GET'])
def manager_stats(mid):
    if int(mid) <= 0 or int(mid) > len(plays[session['season']].get_managers()):
        return redirect(url_for('start'))

    for manager in plays[session['season']].get_managers():
        if manager.get_id() == int(mid):
            break

    title = manager.get_name()

    ps = {}

    for i, p in enumerate(manager.get_points_detailed()):
        ps['Week ' + str(i+1)] = p

    ps['Total Pts'] = manager.get_points()

    t = {}
    t['name'] = manager.get_team().get_name()
    t['id'] = manager.get_team().get_id()

    return render_template('manager_stats.html', title=title, team=t, stats=ps)

@app.route('/players', methods=['GET'])
def players_stats():
    ps = []
    for player in plays[session['season']].get_players():
        a = {}
        a['name'] = player.get_name()
        a['team'] = player.get_team()
        a['points'] = player.get_points()
        a['id'] = player.get_id()
        ps.append(a)

    title = "Players"
    return render_template('people_stats.html', title=title, ps=ps)

@app.route('/managers', methods=['GET'])
def managers_stats():
    ps = []
    for manager in plays[session['season']].get_managers():
        a = {}
        a['name'] = manager.get_name()
        a['team'] = manager.get_team()
        a['points'] = manager.get_points()
        ps.append(a)

    title = "Managers"
    return render_template('people_stats.html', title=title, ps=ps)


if __name__ == "__main__":
    app.secret_key = '12345'
    app.run(host="0.0.0.0", port=5002, debug=False)
