import Mongo
from pymongo import MongoClient
from datetime import datetime
import random
import os
from pprint import pprint


def validate(date_text):
    try:
        date = datetime.strptime(date_text, '%Y')
    except ValueError:
        raise ValueError("Incorrect input, must provide a four digit year")
    return date


def find_sets(db,date):
    sets = []
    for set in db.Sets.find({'Release date': {'$gte': date}}):
        sets.append(set)
    for index in range(len(sets)):
        print(sets[index]['_id'], end=", ")
        if index % 5 == 0:
            print("")


def create_booster(db, setcode):
    boosters = db.Boosters.find_one({'_id': setcode})
    weights = booster = []
    for i in range(len(boosters['Boosters'])):
        weights.append(boosters['Boosters'][i]['weight'])
        booster.append(i)
    print(random.choices(booster, weights, k=1))


client = MongoClient("127.0.0.1:27017")
db = client['MTG_Draft']

choice = input("first time setup? Y or N\n")

if choice in ["Y", "y", "Yes", "yes", "YES"]:
    # fetch all sets
    Mongo.import_all_sets()

    for filename in os.listdir("sets"):
        with open(os.path.join("sets/", filename), 'r') as f:
            set = Mongo.import_set_from_file(f)
            Mongo.load_set(db, set)
            Mongo.load_sheet(db, set)
            Mongo.load_cards(db, set)
    # TODO change config to show first time setup complete

if choice in ["N", "n", "No", "no", "NO"]:
    print('What function would you like to perform?\n'
          '1: Import sets from mtgjson\n'
          '2: Load all sets into database from files\n'
          '3: Load all boosters into database from files\n'
          '4: Update all sets\n'
          '5: Load all sheets into database from files\n'
          '6: Load all cards into database from files\n'
          '7: Create booster')
    # val = input("choose function:")
    val = "4"
    if val == "1":
        Mongo.import_all_sets()
    elif val == "2":
        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as f:
                set = Mongo.import_set_from_file(f)
                Mongo.load_set(db, set)
    elif val == "3":
        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as f:
                set = Mongo.import_set_from_file(f)
                Mongo.load_booster(db, set)
    elif val == '4':
        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as f:
                set = Mongo.import_set_from_file(f)
                Mongo.update_set(db, set)
    elif val == '5':
        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as f:
                set = Mongo.import_set_from_file(f)
                Mongo.load_sheet(db, set)
    elif val == '6':
        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as f:
                set = Mongo.import_set_from_file(f)
                Mongo.load_cards(db, set)

    # date = input("enter year:\n")
    # date = validate(date)
    # find_sets(db, date.date().strftime("%Y-%m-%d"))
    # setcode = input("enter set:\n")
    # create_booster(db, setcode)
