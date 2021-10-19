from pymongo import errors
from pymongo import MongoClient
from os.path import exists
import pymongo
import urllib3
import json
import re
import string
import random


def import_all_sets():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://mtgjson.com/api/v5/AllPrintings.json')
    data = json.loads(r.data.decode('utf-8'))
    for setname in data['data']:
        filename = "sets/" + setname + ".json"
        if exists(filename):
            print(setname + " exists")
        else:
            with open(filename, "w") as file:
                json.dump(data['data'][setname], file)


def import_set_from_file(f):
    data = json.load(f)
    return data


def load_set(db, set):
    # initial validation
    if 'isForeignOnly' in set:
        if set['isForeignOnly']:
            return

    name = set['name']
    print(name)
    if 'block' in set:
        block = set['block']
    else:
        block = ""
    code = set['code']
    date = set['releaseDate']
    onlineonly = set['isOnlineOnly']

    # _id is primary index, so calling it _id rather than code
    setinstance = {"_id": code,
                   "Name": name,
                   "Block": block,
                   "Release date": date,
                   "Online only": onlineonly}
    try:
        result = db.Sets.insert_one(setinstance)
        print(result.inserted_id)
    except pymongo.errors.DuplicateKeyError:
        print(code + " already exists, skipped")


def load_booster(db, set):
    if 'isForeignOnly' in set and set['isForeignOnly']:
        return
    if 'booster' not in set or 'default' not in set['booster']:
        return
    code = set['code']
    total_weight = set['booster']['default']['boostersTotalWeight']
    boosters = set['booster']['default']['boosters']

    boosterinstance = {"_id": code,
                       "Total weight": total_weight,
                       "Boosters": boosters}
    try:
        result = db.Boosters.insert_one(boosterinstance)
        print(result.inserted_id)
    except pymongo.errors.DuplicateKeyError:
        print(code + " already exists, skipped")


def load_sheet(db, set):
    if 'isForeignOnly' in set and set['isForeignOnly']:
        return
    if 'booster' not in set or 'default' not in set['booster']:
        return

    code = set['code']
    sheets = set['booster']['default']['sheets']
    for sheet in sheets:
        sheetinstance = {
            "_id": code + sheet,
            "Code": code,
            "Sheet": sheet,
            "Cards": sheets[sheet]['cards'],
            "Total Weight": sheets[sheet]['totalWeight']
        }
        try:
            result = db.Sheets.insert_one(sheetinstance)
            print(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            print(code + sheet + " already exists, skipped")


def load_cards(db, set):
    if 'isForeignOnly' in set and set['isForeignOnly']:
        return
    if 'booster' not in set or 'default' not in set['booster']:
        return

    for card in set['cards']:
        # explicitly declaring variables instead of modifying the existing card json
        # allows me to comment on certain variables, and not have to worry about optional fields as much
        # may be useful later
        availability = card['availability']
        coloridentity = card['colorIdentity']
        colors = card['colors']
        convertedmanacost = card['convertedManaCost']
        # for now skipping foreign data
        identifiers = card['identifiers']
        name = card['name']
        # not sure what this one does yet, but it isn't optional, so storing it for now
        purchaseurls = card['purchaseUrls']
        rarity = card['rarity']
        setcode = card['setCode']
        subtypes = card['subtypes']
        supertypes = card['supertypes']
        types = card['types']
        uuid = card['uuid']

        cardinstance = {
            '_id': uuid,
            'Availability': availability,
            'Color identity': coloridentity,
            'Colors': colors,
            'Converted mana costs': convertedmanacost,
            'Identifiers': identifiers,
            'Name': name,
            'Purchase URLs': purchaseurls,
            'Rarity': rarity,
            'Set code': setcode,
            'Subtypes': subtypes,
            'Supertypes': supertypes,
            'Types': types,
        }
        options = ['isOnlineOnly', 'isPromo', 'isReprint', 'keywords', 'loyalty', 'manaCost', 'otherFaceIds',
                   'power', 'printings', 'side', 'text', 'toughness', 'variations']
        for item in options:
            if card.get(item) is not None:
                formattedkey = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', item)).split()
                formattedkey[0] = formattedkey[0][0].upper() + formattedkey[0][1:]
                for index, value in enumerate(formattedkey):
                    if index != 0:
                        value = value[0].lower() + value[1:]
                        formattedkey[index] = value
                cardinstance[" ".join(formattedkey)] = card[item]

        try:
            result = db.Cards.insert_one(cardinstance)
            print(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            print(setcode + " already exists, skipped card " + uuid)


def update_set(db, set):
    if 'isForeignOnly' in set and set['isForeignOnly']:
        return

    name = set['name']
    print(name)
    if 'block' in set:
        block = set['block']
    else:
        block = ""
    # _id is primary index, so calling it _id rather than code
    code = set['code']
    query = {'_id': code}
    date = set['releaseDate']
    updatedict = {"Name": name,
                  "Block": block,
                  "Release date": date, }

    if "isOnlineOnly" in set:
        updatedict["Online only"] = set['isOnlineOnly']

    if "booster" in set:
        if "default" in set["booster"]:
            updatedict['Boosters'] = True

    update = {"$set": updatedict}
    result = db.Sets.update_one(query, update)
    if result.modified_count == 1:
        print("updated " + code)
    elif result.matched_count == 1:
        print(code + "has nothing to update")
    else:
        print("problem with " + code)


def get_db(MongoDBconnectString, local):
    if local:
        client = MongoClient("127.0.0.1:27017")
        db = client['MTG_Draft']
        return db
    else:
        client = MongoClient(MongoDBconnectString)
        db = client['MTG_Draft']
        return db


# creates user object, initially has no fields other than id
# user object:
#   _id:            userID, should be the discord user ID when that is set up
#   Groups:         What groups this user is a member of
#   Owned groups:   What groups this user owns
#   Boosters:       What boosters are waiting for them, this includes unopened boosters
#   Decks:          Not implemented currently
def create_user(db, userID):
    user = {'_id': userID}
    db.Users.insert_one(user)


# creates a group object
# group object:
#   _id:            7 character alphanumeric ID
#   Owner:          userID of creator of group
#   Members:        array of userIDs of members of this group
#   config:         game config variables, false if no customization
def create_group(db, userID):
    user = find_user(db, userID)
    groups = user.get('Groups', [])
    owned = user.get('Owned groups', [])
    # limit to ten groups for now
    if len(groups) > 10:
        print("You have already created 10 groups")
        return
    groupID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    Group = {'_id': groupID, 'Owner': userID, 'Members': [userID], 'config': False}
    duplicate = True
    while duplicate:
        try:
            result = db.Groups.insert_one(Group)
            duplicate = False
            groups.append(Group['_id'])
            owned.append(Group['_id'])
            db.Users.update({'_id': userID}, {"$set": {'Groups': groups, 'Owned groups': owned}})
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            print(Group['_id'] + " already exists")
            Group['_id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


# Will store a single draft booster.
# If the booster is not passed, it will store a placeholder booster to be created later
# This method does not care if the user has existing boosters
# Draft booster object
#   Set:            setcode of the booster
#   Booster:        array of all the cards in the booster, missing if the booster hasn't been opened yet
#   Group:          Group this booster has been drafted for
#   Origin:         userID of the drafter
def store_draft_booster(db, userID, groupID, setcode, booster=None):
    user = find_user(db, userID)
    boosters = user.get('Boosters', [])
    if booster is not None:
        boosters.append({'Set': setcode, 'Booster': booster, 'Group': groupID, "Origin": userID})
    else:
        boosters.append({'Set': setcode, 'Group': groupID, "Origin": userID})
    db.Users.update({'_id': userID}, {'$set': {'Boosters': boosters}})


# Will find first instance of a booster for one user in one group.
# Or false if none found, or none with the provided groupID
def find_booster(db, userID, groupID):
    user = find_user(db, userID)
    boosters = user.get('Boosters')
    if boosters is not None:
        for i in boosters:
            if groupID in i['Booster']:
                return i
        return False
    return False


def find_user(db, userID):
    result = db.Users.find_one({'_id': userID})
    return result


def find_group(db, groupID):
    result = db.Groups.find_one({'_id': groupID})
    return result


# search group for open booster with groupID
def has_open_boosters(db, origin, groupID):
    group = find_group(db, groupID)
    for userID in group['Members']:
        member = find_user(db, userID)
        for booster in member['Boosters']:
            if booster['Group'] is groupID and booster['Origin'] is origin:
                return True
    return False


# currently adds user to group, may be expanded later
def update_group(db, userID, groupID):
    group = find_group(db, groupID)
    if group is None:
        raise KeyError("No such group")
    members = group['Members']
    members.append(userID)
    result = db.Groups.update_one({'_id': groupID}, {'$set': {'Members': members}})
    return result.inserted_id


# currently adds group to user, may be expanded later
def update_user(db, userID, groupID):
    user = find_user(db, userID)
    groups = user.get('Groups', [])
    groups.append(groupID)
    result = db.Users.update({'_id': userID}, {'$set': {'Groups': groups}})
    return result.inserted_id
