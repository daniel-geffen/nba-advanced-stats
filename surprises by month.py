import requests
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
scores_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
                  "Referer": "http://stats.nba.com/scores/"}

from calendar import month_name
from datetime import date, timedelta

months = {month_name[i]: [] for i in range(1, 13)}
dates = [[] for x in range(170)]

for year in range(2005, 2016):
    standings_url = "http://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season=" + str(year) + "-" + str(year + 1)[2:]\
                    + "&SeasonType=Regular+Season"
    response = requests.get(standings_url, headers=headers).json()["resultSets"][0]["rowSet"]
    standings = {team[2]: team[12] for team in response}
    response_headers = requests.get(standings_url, headers=headers).json()["resultSets"][0]["headers"]
    day = date(year, 11, 1)
    day_num = 1.0
    while day < date(year + 1, 4, 15):
        print(str(day))
        if day.day == 29 and day.month == 2:
            day += timedelta(1)
            continue

        scores_url = "http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=" + \
                     str(day.month).zfill(2) + "%2F" + str(day.day).zfill(2) + "%2F" + str(day.year)
        scores_response = requests.get(scores_url, headers=scores_headers).json()["resultSets"][1]["rowSet"]

        try:
            for x in range(0, len(scores_response), 2):
                if scores_response[x][21] > scores_response[x + 1][21] and standings[scores_response[x][3]] + 5 < standings[scores_response[x + 1][3]] \
                        or scores_response[x][21] < scores_response[x + 1][21] and standings[scores_response[x][3]] > standings[scores_response[x + 1][3]] + 5:
                    months[month_name[day.month]].append(1)
                    dates[int(day_num)].append(1)
                else:
                    months[month_name[day.month]].append(0)
                    dates[int(day_num)].append(0)

            day_num += 1.0
        except KeyError:
            print("All Star")

        day += timedelta(1)

for m in ["November", "December", "January", "February", "March", "April"]:
    print(m, round(sum(months[m]) / len(months[m]) * 100, 2))

from scipy.stats import gaussian_kde
import numpy
import matplotlib.pyplot as plt

kde_lst = numpy.array([[0.0, 0.0]])
day_num = 0
for x in dates:
    if len(x) > 10:
        kde_lst = numpy.concatenate((kde_lst, [[float(dates.index(x)), round(sum(x) / len(x), 3)]]))
    else:
        print(day_num)
    day_num += 1

density = gaussian_kde(kde_lst.T)
x_axis = numpy.linspace(numpy.amin(kde_lst, axis=0)[0], numpy.amax(kde_lst, axis=0)[0], 1000)
y_axis = numpy.linspace(numpy.amin(kde_lst, axis=0)[1], numpy.amax(kde_lst, axis=0)[1], 1000)
x = numpy.array([x_axis, y_axis])
numpy.savetxt("C:\\Users\\tuvia\\Documents\\Analytics\\surprises1.csv", kde_lst, delimiter=",")
numpy.savetxt("C:\\Users\\tuvia\\Documents\\Analytics\\surprises.csv", numpy.c_[numpy.asarray([x_axis, density(x).T])], delimiter=",")
plt.plot(x.T, density(x).T)
plt.show()
