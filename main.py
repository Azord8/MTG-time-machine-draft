import Mongo
from datetime import datetime
import random
import os
from os.path import exists
import json

if 'mongo_connect_string' in os.environ:
    MongoDBconnectString = os.environ['mongo_connect_string']
    local = False
else:
    MongoDBconnectString = ""
    local = True

db = Mongo.get_db(MongoDBconnectString, local)


def validate(date_text):
    try:
        date = datetime.strptime(date_text, '%Y')
    except ValueError:
        raise ValueError("Incorrect input, must provide a four digit year")
    return date


def find_sets(date):
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


def find_boosters(date):
    sets = find_sets(date)
    boosters = []
    f = open("config.json", "r+")
    config = json.load(f)
    for set in sets:
        tempBooster = {'Name': set['Name'], '_id': set['_id']}
        booster = db.Boosters.find_one({'_id': set['_id']})
        if booster is not None:
            boosters.append(tempBooster)
    return boosters


def create_booster(setcode):
    boosters = db.Boosters.find_one({'_id': setcode})
    print(boosters)
    print(setcode)
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


def create_draft_booster(amount, userID, groupID, setcodes):
    existingBooster = Mongo.has_open_boosters(db, userID, groupID)
    if existingBooster:
        print("already have existing booster for this group")
    else:
        booster = create_booster(setcodes[0])
        Mongo.store_draft_booster(db, userID, groupID, setcodes[0], booster)
        for i in range(1, amount):
            Mongo.store_draft_booster(db, userID, groupID, setcodes[i])


def check_setup():
    if not exists("config.json"):
        g = open("config-sample.json", "r+")
        configDefaults = json.load(g)
        print("GET OUT!")
        f = open("config.json", "w")
        f.write(json.dumps(configDefaults))

    f = open("config.json", "r+")
    config = json.load(f)

    if config['First time setup'] == "True":
        # fetch all sets
        # Mongo.import_all_sets()

        for filename in os.listdir("sets"):
            with open(os.path.join("sets/", filename), 'r') as fileset:
                set = Mongo.import_set_from_file(fileset)
                Mongo.load_set(db, set)
                Mongo.load_sheet(db, set)
                Mongo.load_cards(db, set)
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


# handling drafting a booster and passing it to the next member
def draft_booster(userID, draftbooster, card):
    booster = draftbooster['booster']
    groupID = booster['Group']
    existingbooster = Mongo.has_open_boosters(db, userID, groupID)
    if existingbooster is not False:
        if existingbooster['Booster'] is booster:
            del booster[card]
#             handle adding card here
            if booster:
                group = Mongo.find_group(db, groupID)
                members = group['members']
                if members.index(userID) is len(members):
                    pass


def first_time_user(userID):
    Mongo.create_user(db, userID)
    result = Mongo.create_group(db, userID)
    return result


def join_group(userID, groupID):
    try:
        Mongo.update_group(db, userID, groupID)
    except KeyError as e:
        return e.message
    Mongo.update_user(db, userID, groupID)
    return "You have joined group " + groupID


def create_dummy_data():
    Mongo.create_user(db, 'Dummy')
    Mongo.create_group(db, 'Dummy')
    create_draft_booster(1, 'Dummy', '2WN6SIM', ['2ED'])
