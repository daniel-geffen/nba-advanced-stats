import requests
import csv
from math import copysign


# Returns the score differential in the given possession.
# _index -- index of current possession.
def find_difference(_index, team):
    if _index is None:
        return float("NaN")
    while playByPlay[_index][10] is None:
        if playByPlay[_index][2] == 12:
            return 0
        _index -= 1

    if playByPlay[_index][11] == "TIE":
        diff = 0
    else:
        diff = int(playByPlay[_index][11]) if team == 4 else int(playByPlay[_index][11]) * -1
    return diff


# Counts given number of possessions from given index and returns new index.
# _index -- starting index.
# num -- number of possessions to count.
def find_x_possessions(_index, num, repeating=False):
    free_throws = [12, 15]  # if num > 0 else [11, 13]
    stops = [9, 12] if num == 0.5 else [12]
    possessions = 0
    _index += int(copysign(1, num))
    next_is_offensive_rebound = False
    while (possessions != abs(num) * 2 or next_is_offensive_rebound) and _index != len(playByPlay) - 1 \
            and playByPlay[_index][2] not in stops:
        is_free_throw = playByPlay[_index][2] == 3
        if playByPlay[_index][2] in [1, 2, 5] or (is_free_throw and playByPlay[_index][3] in free_throws):
            possessions += 1
        if next_is_offensive_rebound:
            next_is_offensive_rebound = False
            possessions -= 1
        next_is_offensive_rebound = playByPlay[_index + 1][2] == 4 and not \
            (is_free_throw and playByPlay[_index][3] in [11, 13]) and playByPlay[_index][15] in playByPlay[_index + 1]
        _index += int(copysign(1, num))

    if num == 0.5 and repeating:
        if playByPlay[_index][2] == 12:
            return _index + 2
        else:
            return _index

    if possessions < abs(num) * 2:
        return None

    if num < 0:
        not_used = 0
        original_index = _index + 1
        while playByPlay[_index][2] not in range(1, 6) or playByPlay[original_index][15] == playByPlay[_index][15] \
                and playByPlay[_index][2] in [9, 12]:
            if playByPlay[_index][2] not in [1, 2, 3, 5]:
                not_used += 1
            else:
                not_used = 0
            _index -= 1
        return _index + not_used

    extra = 0
    while playByPlay[_index + extra][2] in [6, 8]:
        extra += 1
    if playByPlay[_index + extra][2] == 3 and playByPlay[_index + extra][3] == 10:
        return _index + extra
    return _index - 1


# Returns the points scored by the given team until the given possession.
# _index -- index of current possession.
# team -- team number (4 for home team or 5 for away team)
def find_points(_index, team):
    if _index is None:
        return float("NaN")
    while playByPlay[_index][10] is None:
        if playByPlay[_index][2] == 12:
            return 0
        _index -= 1
    a = playByPlay[_index][10].index("-")
    if team == 5:
        return int(playByPlay[_index][10][:a - 1])
    return int(playByPlay[_index][10][a + 2:])


# Returns the amount of points the opponent of the given team has scored in a row.
# _index -- index of current possession.
# team -- team number (4 for home team or 5 for away team)
def find_opponent_streak(_index, team):
    _index -= 1
    original_index = _index
    while not (playByPlay[_index][10] is not None and playByPlay[_index][12] == team and not (playByPlay[_index][2] == 3 and playByPlay[_index][3] in [10, 11, 13])) and _index != 0:
        _index -= 1
    team = int(not (team - 4)) + 4
    if _index == 0:
        return find_points(original_index, team)
    return find_points(original_index, team) - find_points(_index, team)


# Returns the number of possessions from the last or to the next timeout (or end of period).
# _index -- index of current possession.
# direction -- 1 in order to count to the next timeout, -1 in order to count to the previous timeout.
def find_possessions_from_last_timeout(_index, direction):
    possessions = 0
    while playByPlay[_index][2] not in [9, 12, 13]:
        if playByPlay[_index][2] in [1, 2, 5, 7] or playByPlay[_index][2] == 3 and playByPlay[_index][3] in [10, 12,
                                                                                                             15]:
            possessions += 1
        if playByPlay[_index][2] == 4 and playByPlay[_index][15] == playByPlay[_index - 1][15]:
            possessions -= 1

        _index += direction
    return possessions / 2


# Returns the time in seconds or minutes from the timestring of the possession (if the input is HH:MM it returns
# minutes, if it is MM:SS it returns seconds).
# _index -- index of the possession.
# is_game_time -- True if the desirable time is the game time, False if real time.
def calculate_time(_index, is_game_time):
    if _index is None:
        return 720
    time_string1 = playByPlay[_index][int(is_game_time) + 5]
    if is_game_time:
        return int(time_string1[:time_string1.index(":")]) * 60 + int(time_string1[time_string1.index(":") + 1:])
    else:
        return int(time_string1[:time_string1.index(":")]) * 60 + int \
            (time_string1[time_string1.index(":") + 1: time_string1.index(" ")])


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

fieldnames = ["Team", "Game ID", "Date", "Wins", "Losses", "Period", "Minutes", "Won Game", "Timeout Taken",
              "Score Difference", "Lead or Deficit", "Opponent Streak", "Possessions From Previous Timeout",
              "Possessions To Next Timeout", "Last 5 Game Time", "Next 5 Game Time", "Last 5 Real Time",
              "Next 5 Real Time", "Difference In Last 5 Possessions", "Points In Last 5 Possessions", "-5", "-4", "-3",
              "-2", "-1", "Difference In Next 5 Possessions", "Points In Next 5 Possessions", "1", "2", "3", "4", "5",
              "Last Possession Description"]

with open('C:\\Users\\tuvia\\Documents\\Analytics\\Possessions Variables.csv', 'w') as csv_file:
    writer = csv.DictWriter(csv_file, lineterminator='\n', fieldnames=fieldnames)
    writer.writeheader()

    teamsUrl = "http://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season=2015-16&SeasonType=Regular+Season"
    teams = {x[2]: x[3] + " " + x[4] for x in requests.get(teamsUrl, headers=headers).json()["resultSets"][0]["rowSet"]}

    for season in range(5, 6):
        for game in ["0021" + str(season) + "0" + str(x).zfill(4) for x in range(1, 1231)]:
            print(game)
            infoUrl = "http://stats.nba.com/stats/boxscoresummaryv2?GameID=" + game
            response = requests.get(infoUrl, headers=headers).json()["resultSets"]
            info = response[5]["rowSet"]
            home, away, win = info[0][7], info[1][7], info[0][22] > info[1][22]
            records = {
                info[0][3]: [int(win), int(home[:home.index("-")]) - win, int(home[home.index("-") + 1:]) - (not win)],
                info[1][3]: [int(not win), int(away[:away.index("-")]) - (not win),
                             int(away[away.index("-") + 1:]) - win]}
            date = response[4]["rowSet"][0][0]

            url = "http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&EndRange=55800&GameID=" + game + "&RangeType=" \
                                                                                                         "2&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0"

            playByPlay = requests.get(url, headers=headers).json()["resultSets"][0]["rowSet"]
            play = playByPlay[2]
            time = 12
            repeat = False
            while playByPlay.index(play) < len(playByPlay) - 2:
                if play[2] not in range(12, 14):
                    try:
                        team = play[13] if play[13] in records.keys() else play[15]
                        line_dict = {}
                        line_dict["Team"] = teams[team]
                        line_dict["Game ID"] = int(game[6:])  # 2010 + season
                        line_dict["Date"] = date
                        line_dict["Wins"] = records[team][1]
                        line_dict["Losses"] = records[team][2]
                        line_dict["Period"] = play[4]
                        line_dict["Minutes"] = time
                        time = round(calculate_time(playByPlay.index(play), True) / 60, 2)
                        line_dict["Won Game"] = int(win) if team == info[0][3] else int(not win)
                        line_dict["Timeout Taken"] = int(play[2] == 9)
                        i, team = playByPlay.index(play), play[12] + 2 if play[12] < 4 else play[12]
                        gameDifference = find_difference(i - 1, team)
                        line_dict["Score Difference"] = gameDifference
                        line_dict["Lead or Deficit"] = int(gameDifference > 0) * 2 + int(not gameDifference)
                        line_dict["Opponent Streak"] = find_opponent_streak(i, team)
                        line_dict["Possessions From Previous Timeout"] = find_possessions_from_last_timeout(i - 1, -1)
                        line_dict["Possessions To Next Timeout"] = find_possessions_from_last_timeout(i + 1, 1)
                        line_dict["Difference In Last 5 Possessions"] = gameDifference - find_difference(
                            find_x_possessions(i, -5, repeat), team)
                        line_dict["Points In Last 5 Possessions"] = find_points(i - 1, team) - find_points(
                            find_x_possessions(i, -5), team)
                        for x in range(-4, 0):
                            line_dict[str(x - 1)] = find_points(find_x_possessions(i, x), team) - find_points(
                                find_x_possessions(i, x - 1), team)
                        line_dict["-1"] = find_points(i - 1, team) - find_points(find_x_possessions(i, -1), team)
                        line_dict["Difference In Next 5 Possessions"] = \
                            find_difference(find_x_possessions(i, 5), team) - find_difference(i, team)
                        line_dict["Points In Next 5 Possessions"] = \
                            find_points(find_x_possessions(i, 5), team) - find_points(i, team)
                        line_dict["1"] = find_points(find_x_possessions(i, 1), team) - find_points(i, team)
                        for x in range(2, 6):
                            line_dict[str(x)] = find_points(find_x_possessions(i, x), team) - find_points(
                                find_x_possessions(i, x - 1), team)

                        try:
                            line_dict["Last Possession Description"] = ' '.join(
                                filter(None, playByPlay[find_x_possessions(i, -0.5) + 1][7:10]))

                            line_dict["Last 5 Game Time"] = \
                                calculate_time(find_x_possessions(i, -5), True) - calculate_time(i - 1, True)
                            line_dict["Next 5 Game Time"] = \
                                calculate_time(i, True) - calculate_time(find_x_possessions(i, 5), True)
                            line_dict["Last 5 Real Time"] = \
                                calculate_time(i - 1, False) - calculate_time(find_x_possessions(i, -5), False)
                            line_dict["Next 5 Real Time"] = \
                                calculate_time(i, False) - calculate_time(find_x_possessions(i, 5), False)

                        except TypeError:
                            pass

                        writer.writerow(line_dict)

                    except (KeyError, ValueError):
                        if len(list(filter(None, play[7:10]))) > 0:
                            print(' '.join(filter(None, play[7:10])))

                if play[2] == 9:
                    new_play = find_x_possessions(playByPlay.index(play), 1)
                else:
                    new_play = find_x_possessions(playByPlay.index(play), 0.5)
                if new_play is None:
                    try:
                        play = playByPlay[find_x_possessions(playByPlay.index(play), 0.5, True)]
                    except IndexError as e:
                        print(e, playByPlay.index(play))
                        break
                else:
                    play = playByPlay[new_play]
