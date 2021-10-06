import Mongo
from datetime import datetime
import random
import os
from os.path import exists
import json

MongoDBconnectString = os.environ['mongo_connect_string']


def validate(date_text):
    try:
        date = datetime.strptime(date_text, '%Y')
    except ValueError:
        raise ValueError("Incorrect input, must provide a four digit year")
    return date


def find_sets(date):
    db = Mongo.get_db(MongoDBconnectString)
    sets = []
    f = open("config.json", "r+")
    config = json.load(f)
    if config['Online'] == "False":
        for set in db.Sets.find({'Release date': {'$lte': date}, 'Online only': {'$not': {'$eq': 'true'}}}):
            sets.append(set)
    else:
        for set in db.Sets.find({'Release date': {'$lte': date}}):
            sets.append(set)
    return sets


def create_booster(setcode):
    db = Mongo.get_db(MongoDBconnectString)
    boosters = db.Boosters.find_one({'_id': setcode})
    weights = []
    booster = []
    for i in range(len(boosters['Boosters'])):
        weights.append(boosters['Boosters'][i]['weight'])
        booster.append(i)
    selectedBooster = random.choices(booster, weights, k=1)
    # print(selectedBooster)
    # print(type(selectedBooster[0]))
    selectedSheets = boosters['Boosters'][selectedBooster[0]]['contents']
    createdBooster = []
    for sheet, count in selectedSheets.items():
        thisSheet = db.Sheets.find_one({'Code': setcode, 'Sheet': sheet})
        weights = []
        cards = []
        for uuid, weight in thisSheet['Cards'].items():
            cards.append(uuid)
            weights.append(weight)
        tempChoices = random.choices(cards, weights, k=count)
        for i in tempChoices:
            createdBooster.append(i)
    createdCards = []
    for i in createdBooster:
        card = db.Cards.find_one({'_id': i})
        createdCards.append([i, card['Name']])
    return createdCards


def check_setup():
    if not exists("config.json"):
        g = open("config-sample.json", "r+")
        configDefaults = json.load(g)
        f = open("config.json", "w")
        f.write(json.dumps(configDefaults))

    f = open("config.json", "r+")
    config = json.load(f)
    db = Mongo.get_db(MongoDBconnectString)

    if config['First time setup'] == "True":
        # fetch all sets
        # Mongo.import_all_sets()

        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as fileset:
                set = Mongo.import_set_from_file(fileset)
                # Mongo.load_set(db, set)
                # Mongo.load_sheet(db, set)
                # # Mongo.load_cards(db, set)
                Mongo.load_booster(db, set)
        config['First time setup'] = "False"
        f.write(json.dumps(config))
        return "database setup!"

    if config['First time setup'] == "Debug":
        print('What function would you like to perform?\n'
              '1: Import sets from mtgjson\n'
              '2: Load all sets into database from files\n'
              '3: Load all boosters into database from files\n'
              '4: Update all sets\n'
              '5: Load all sheets into database from files\n'
              '6: Load all cards into database from files\n'
              '7: Create booster')
        val = input("choose function:")
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
        elif val == '7':
            date = input("enter year:\n")
            date = validate(date)
            find_sets(date.date().strftime("%Y-%m-%d"))
            setcode = input("enter set:\n")
            create_booster(setcode)

    elif config['First time setup'] == "False":
        date = datetime.strptime(config['Date'], "%Y-%m-%d")
        find_sets(date.date().strftime("%Y-%m-%d"))
        setcode = input("enter set:\n")
        create_booster(setcode)
