from bs4 import BeautifulSoup
import urllib2
import sys
import html5lib
import string
import re
import random
import time
import csv
import timeit


__author__ = 'Patrick Howell'



def get_games(game_dictionary, url, page_no, more):
    """
    Encapsulating the search through games on a given url page
    :param game_dictionary: Dictionary with game titles as the key
    :param url: URL from Metacritic to parse through
    :param more: Boolean T/F value to know to continue parsing or not
    :return: Game dictionary and an updated (or not) more value
    """
    # Need this to trick Metacritic into not realizing its a bot script
    request = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })

    try:
        page = urllib2.urlopen(request)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to reach url'
            print 'Reason: ', e.reason
            sys.exit()
        elif hasattr(e, 'code'):
            if e.code == 404:
                print 'Error: ', e.code
                sys.exit()


    content = page.read()
    soup = BeautifulSoup(content, "html5lib")

    try:
        if soup.find_all("p", class_="no_data")[0].text == 'No Results Found':
            more = False

    except:
        # Pulling the titles, with exception in order to filter out other titles that aren't part of table
        # i.e. ads for new releases
        raw_title = soup.find_all("div", class_="basic_stat product_title")
        titles = []
        for i in raw_title:
            items = i.text.split('\n')
            try:
                text = items[2].strip(" ")
            except:
                continue
            titles.append(text)

        # Extract the average Metascore
        raw_metascore = soup.find_all("div", class_=re.compile("^metascore_w"))
        metascores=[]
        for i in raw_metascore:
            metascores.append(i.text)

        # Average user score and release dates stored in the same item for extraction
        raw_user_date = soup.find_all("div", class_="more_stats condensed_stats")
        scores = []
        dates = []
        for i in raw_user_date:
            items = i.text.split('\n')
            user_score = items[4].strip(" ")  # 4th item of splitted string contains scores
            scores.append(user_score)
            release = items[9].strip(" ")  # 9th item of splitted string contains release date
            dates.append(release)


        for x in range(len(titles)):
            game_dictionary[titles[x]] = {"Metascore": metascores[x], "UserScore": scores[x], "Release": dates[x]}

        wait_time = round(max(0, 1 + random.gauss(0,0.5)), 2)
        time.sleep(wait_time)

    return game_dictionary, page_no, more




if __name__ == "__main__":
    start = timeit.default_timer()
    master = {}

    system_list = ['ps4', 'xboxone', 'ps3', 'wii-u', 'xbox360', 'pc', 'wii', '3ds',
        'vita', 'ios', 'ps2', 'xbox', 'ds', 'gamecube', 'n64', 'ps', 'gba', 'dreamcast']


    for system in system_list:

        game_dictionary = {}
        more = True
        letter_all = string.ascii_lowercase
        page_no = 0

        url = "http://www.metacritic.com/browse/games/title/%s" % system  # Gets all games that begin with numbers first
        print "Starting: #"
        game_dictionary, page_no, more = get_games(game_dictionary, url, page_no, more)
        print "Finished: #"


        for c in letter_all:
            letter = c
            print "Starting: ", letter
            page_no = 0
            more = True
            while more:
                url = "http://www.metacritic.com/browse/games/title/%s/%s?page=%d" % (system, letter, page_no)
                print url
                game_dictionary, page_no, more = get_games(game_dictionary, url, page_no, more)
                page_no += 1
            print "Finised: ", letter

        master[system] = game_dictionary

    # After having master dictionary prepared and ready:
    with open('TotalGames.csv', 'wb') as f:
        writer = csv.writer(f)
        header = ["System", "Game", "Metascore", "UserScore",  "ReleaseDate"]
        writer.writerow(header)
        for system in master:
            for game in master[system]:
                row = [system, game, master[system][game]["Metascore"], master[system][game]["UserScore"],
                       master[system][game]["Release"]]
                writer.writerow(row)

    stop = timeit.default_timer()
    print ""
    count = 0
    for system in master:
        count += len(master[system])
    print "Total number of games in dataset: ", count
    print ""
    print "Overall Time: ", stop - start
