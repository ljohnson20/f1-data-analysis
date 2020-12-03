import os
import pandas as pd
import re
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from requests_html import HTMLSession


def get_fia_data(force: bool = False):
    if not os.path.exists('data/fia'):
        os.makedirs('data/fia')

    html_list = ["https://www.fia.com/documents/season/season-2020-1059",
                 "https://www.fia.com/documents/season/season-2019-971"]

    races = pd.read_csv('data/ergast/races.csv')
    drivers = pd.read_csv('data/ergast/drivers.csv')
    standings = pd.read_csv('data/ergast/driver_standings.csv')
    session = HTMLSession()

    data = pd.DataFrame()

    for html in html_list:
        r = session.get(html)
        r.html.render()
        race_id = "Unknown"
        year = html.split("-")[-2]
        for line in r.html.text.split("\n"):
            if "Grand Prix" in line and not year in line:
                line = line.replace("Formula 1 ", "")
                race_id = races.loc[(races['year'] == int(year)) & (races['name'] == line)]
                if race_id.empty:
                    print('Warning: Missing race for ' + year + " " + line)
                # print(race_id[['raceId','year','name']])
                # print(line + " = " + race_id)
            if "Offence" in line and not "Corrected" in line:
                # print(line)
                doctored = re.sub(r"^.*?offence - ", "", line.lower())
                doctored = re.sub(r"\)$", "", doctored)
                doctored = doctored.replace(" (", " - ")
                if doctored == "car 8 parc ferme":
                    doctored_list = ["car 8", "parc ferme"]
                elif doctored == "car 26 track limits turn 10 2nd":
                    doctored_list = ["car 26", "track limits turn 18 2nd"]
                else:
                    doctored_list = doctored.split(" - ", maxsplit=1)
                if "car" in doctored_list[0]:
                    offence = pd.DataFrame([[doctored_list[0], doctored_list[1], line]],
                                           columns=["Car", "Warning", "Entire Line"])
                    driver_num = doctored_list[0].split()[1]
                    driver = drivers.loc[drivers['number'] == driver_num]
                    if len(driver) > 1:
                        correct_driver = standings.loc[(standings['raceId'] == race_id['raceId'].iloc[0]) &
                                                       (standings['driverId'].isin(list(driver['driverId'].values)))][
                            'driverId']
                        driver = driver.loc[driver['driverId'] == correct_driver.iloc[0]]
                    if driver.empty:
                        print(' Warning: No driver found for ' + driver_num)
                    else:
                        driver = driver.rename(columns={'url': 'driver_url'})
                        temp_dataframe = pd.concat([race_id.reset_index(drop=True), driver.reset_index(drop=True),
                                                    offence.reset_index(drop=True)], axis=1)
                        data = data.append(temp_dataframe, ignore_index=True)
    data.to_csv("data/fia/driver_offence.csv", index=False)


def get_f1_data(force: bool = False):
    if not os.path.exists('data/ergast'):
        os.makedirs('data/ergast')

    zipurl = 'http://ergast.com/downloads/f1db_csv.zip'
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall('data/ergast')


if __name__ == "__main__":
    get_fia_data()
