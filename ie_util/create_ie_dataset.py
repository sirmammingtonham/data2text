import codecs, json, os
from collections import Counter, OrderedDict
from nltk import sent_tokenize, word_tokenize
import numpy as np
import random
from text2num import text2num, NumberException
import json

random.seed(2)


prons = set(["he", "He", "him", "Him", "his", "His", "they", "They", "them", "Them", "their", "Their"]) # leave out "it"
singular_prons = set(["he", "He", "him", "Him", "his", "His"])
plural_prons = set(["they", "They", "them", "Them", "their", "Their"])

number_words = set(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"])
# ordering the relations correctly
class DefaultListOrderedDict(OrderedDict):
    def __missing__(self,k):
        self[k] = []
        return self[k]

def get_ents(dat):
    players = set()
    teams = set()
    cities = set()
    for thing in dat:
        teams.add(thing["vis_name"])
        teams.add(thing["vis_line"]["TEAM-NAME"])
        teams.add(thing["vis_city"] + " " + thing["vis_name"])
        teams.add(thing["vis_city"] + " " + thing["vis_line"]["TEAM-NAME"])
        teams.add(thing["home_name"])
        teams.add(thing["home_line"]["TEAM-NAME"])
        teams.add(thing["home_city"] + " " + thing["home_name"])
        teams.add(thing["home_city"] + " " + thing["home_line"]["TEAM-NAME"])
        # special case for this
        if thing["vis_city"] == "Los Angeles":
            teams.add("LA" + thing["vis_name"])
        if thing["home_city"] == "Los Angeles":
            teams.add("LA" + thing["home_name"])
        # sometimes team_city is different
        cities.add(thing["home_city"])
        cities.add(thing["vis_city"])
        players.update(thing["box_score"]["PLAYER_NAME"].values())
        cities.update(thing["box_score"]["TEAM_CITY"].values())

    for entset in [players, teams, cities]:
        for k in list(entset):
            pieces = k.split()
            if len(pieces) > 1:
                for piece in pieces:
                    if len(piece) > 1 and piece not in ["II", "III", "Jr.", "Jr"]:
                        entset.add(piece)

    all_ents = players | teams | cities

    return all_ents, players, teams, cities


def deterministic_resolve(pron, players, teams, cities, curr_ents, prev_ents, max_back=1):
    # we'll just take closest compatible one.
    # first look in current sentence; if there's an antecedent here return None, since
    # we'll catch it anyway
    for j in range(len(curr_ents)-1, -1, -1):
        if pron in singular_prons and curr_ents[j][2] in players:
            return None
        elif pron in plural_prons and curr_ents[j][2] in teams:
            return None
        elif pron in plural_prons and curr_ents[j][2] in cities:
            return None

    # then look in previous max_back sentences
    if len(prev_ents) > 0:
        for i in range(len(prev_ents)-1, len(prev_ents)-1-max_back, -1):
            for j in range(len(prev_ents[i])-1, -1, -1):
                if pron in singular_prons and prev_ents[i][j][2] in players:
                    return prev_ents[i][j]
                elif pron in plural_prons and prev_ents[i][j][2] in teams:
                    return prev_ents[i][j]
                elif pron in plural_prons and prev_ents[i][j][2] in cities:
                    return prev_ents[i][j]
    return None


def extract_entities(sent, all_ents, prons, prev_ents=None, resolve_prons=False,
        players=None, teams=None, cities=None):
    sent_ents = []
    i = 0
    while i < len(sent):
        if sent[i] in prons:
            if resolve_prons:
                referent = deterministic_resolve(sent[i], players, teams, cities, sent_ents, prev_ents)
                if referent is None:
                    sent_ents.append((i, i+1, sent[i], True)) # is a pronoun
                else:
                    #print("replacing", sent[i], "with", referent[2], "in", " ".join(sent))
                    sent_ents.append((i, i+1, referent[2], False)) # pretend it's not a pron and put in matching string
            else:
                sent_ents.append((i, i+1, sent[i], True)) # is a pronoun
            i += 1
        elif sent[i] in all_ents: # findest longest spans; only works if we put in words...
            j = 1
            while i+j <= len(sent) and " ".join(sent[i:i+j]) in all_ents:
                j += 1
            sent_ents.append((i, i+j-1, " ".join(sent[i:i+j-1]), False))
            i += j-1
        else:
            i += 1
    return sent_ents

# fixing bug of number words handling
def annoying_number_word(sent, i):
    ignores = set(["three point", "three - point", "three - pt", "three pt", "three - pointers", "three - pointer", "three pointers"])
    return " ".join(sent[i:i + 3]) in ignores or " ".join(sent[i:i + 2]) in ignores

def extract_numbers(sent):
    sent_nums = []
    i = 0
    ignores = set(["three point", "three-point", "three-pt", "three pt"])
    #print(sent)
    while i < len(sent):
        toke = sent[i]
        a_number = False
        try:
            itoke = int(toke)
            a_number = True
        except ValueError:
            pass
        if a_number:
            sent_nums.append((i, i+1, int(toke)))
            i += 1
        elif toke in number_words and not annoying_number_word(sent, i): # get longest span  (this is kind of stupid)
            j = 1
            while i + j < len(sent) and sent[i + j] in number_words and not annoying_number_word(sent, i + j):
                j += 1
            try:
                sent_nums.append((i, i+j, text2num(" ".join(sent[i:i+j]))))
            except NumberException:
                pass
                #print(sent)
                #print(sent[i:i+j])
                #assert False
            i += j
        else:
            i += 1
    return sent_nums


def get_player_idx(bs, entname):
    keys = []
    for k, v in bs["PLAYER_NAME"].items():
         if entname == v:
             keys.append(k)
    if len(keys) == 0:
        for k,v in bs["SECOND_NAME"].items():
            if entname == v:
                keys.append(k)
        if len(keys) > 1: # take the earliest one
            keys.sort(key = lambda x: int(x))
            keys = keys[:1]
            #print("picking", bs["PLAYER_NAME"][keys[0]])
    if len(keys) == 0:
        for k,v in bs["FIRST_NAME"].items():
            if entname == v:
                keys.append(k)
        if len(keys) > 1: # if we matched on first name and there are a bunch just forget about it
            return None
    #if len(keys) == 0:
        #print("Couldn't find", entname, "in", bs["PLAYER_NAME"].values())
    assert len(keys) <= 1, entname + " : " + str(bs["PLAYER_NAME"].values())
    return keys[0] if len(keys) > 0 else None


def get_rels(entry, ents, nums, players, teams, cities):
    """
    this looks at the box/line score and figures out which (entity, number) pairs
    are candidate true relations, and which can't be.
    if an ent and number don't line up (i.e., aren't in the box/line score together),
    we give a NONE label, so for generated summaries that we extract from, if we predict
    a label we'll get it wrong (which is presumably what we want).
    N.B. this function only looks at the entity string (not position in sentence), so the
    string a pronoun corefers with can be snuck in....
    """
    rels = []
    bs = entry["box_score"]
    for i, ent in enumerate(ents):
        if ent[3]: # pronoun
            continue # for now
        entname = ent[2]
        # assume if a player has a city or team name as his name, they won't use that one (e.g., Orlando Johnson)
        if entname in players and entname not in cities and entname not in teams:
            pidx = get_player_idx(bs, entname)
            for j, numtup in enumerate(nums):
                found = False
                strnum = str(numtup[2])
                if pidx is not None: # player might not actually be in the game or whatever
                    for colname, col in bs.items():
                        if col[pidx] == strnum: # allow multiple for now
                            rels.append((ent, numtup, "PLAYER-" + colname, pidx))
                            found = True
                if not found:
                    rels.append((ent, numtup, "NONE", None))

        else: # has to be city or team
            entpieces = entname.split()
            linescore = None
            is_home = None
            if entpieces[0] in entry["home_city"] or entpieces[-1] in entry["home_name"]:
                linescore = entry["home_line"]
                is_home = True
            elif entpieces[0] in entry["vis_city"] or entpieces[-1] in entry["vis_name"]:
                linescore = entry["vis_line"]
                is_home = False
            elif "LA" in entpieces[0]:
                if entry["home_city"] == "Los Angeles":
                    linescore = entry["home_line"]
                    is_home = True
                elif entry["vis_city"] == "Los Angeles":
                    linescore = entry["vis_line"]
                    is_home = False
            for j, numtup in enumerate(nums):
                found = False
                strnum = str(numtup[2])
                if linescore is not None:
                    for colname, val in linescore.items():
                        if val == strnum:
                            #rels.append((ent, numtup, "TEAM-" + colname, is_home))
                            # apparently I appended TEAM- at some pt...
                            rels.append((ent, numtup, colname, is_home))
                            found = True
                if not found:
                    rels.append((ent, numtup, "NONE", None)) # should i specialize the NONE labels too?
    return rels

def append_candidate_rels(entry, summ, all_ents, prons, players, teams, cities, candrels):
    """
    appends tuples of form (sentence_tokens, [rels]) to candrels
    """
    sents = sent_tokenize(summ)
    for j, sent in enumerate(sents):
        #tokes = word_tokenize(sent)
        tokes = sent.split()
        ents = extract_entities(tokes, all_ents, prons)
        nums = extract_numbers(tokes)
        rels = get_rels(entry, ents, nums, players, teams, cities)
        if len(rels) > 0:
            candrels.append((tokes, rels))
    return candrels


def get_datasets(path, summary_path=None):
    with open(os.path.join(path, "train.json"), "r", encoding="utf-8") as f:
        trdata = json.load(f)

    all_ents, players, teams, cities = get_ents(trdata)

    with open(os.path.join(path, "valid.json"), "r", encoding="utf-8") as f:
        valdata = json.load(f)

    with open(os.path.join(path, "test.json"), "r", encoding="utf-8") as f:
        testdata = json.load(f)

    if summary_path is not None:
        # with open(os.path.join(summary_path, "valid.txt"), "r", encoding="utf-8") as f:
        #     for i, b in enumerate(f.readlines()):
        #         valdata[i]['summary'] = word_tokenize(b)

        with open(os.path.join(summary_path, "test.txt"), "r", encoding="utf-8") as f:
            for i, b in enumerate(f.readlines()):
                testdata[i]['summary'] = word_tokenize(b)

    extracted_stuff = []
    datasets = [trdata, valdata, testdata]
    for dataset in datasets:
        nugz = []
        for i, entry in enumerate(dataset):
            summ = " ".join(entry['summary'])
            append_candidate_rels(entry, summ, all_ents, prons, players, teams, cities, nugz)

        extracted_stuff.append(nugz)

    del all_ents
    del players
    del teams
    del cities
    return extracted_stuff

def append_tuple_data(tup, label_strat):
    """
    used for val, since we have contradictory labelings...
    tup is (sent, [rels]);
    each rel is ((ent_start, ent_end, ent_str), (num_start, num_end, num_str), label)
    """

    unique_rels = DefaultListOrderedDict()
    for rel in tup[1]:
        ent, num, label, idthing = rel
        unique_rels[ent, num].append(label)

    dataset = []

    if label_strat is None:
        for rel, label_list in unique_rels.items():
            dataset.append({
            "token": tup[0],
            "h": {"name": rel[0][2], "pos": [rel[0][0], rel[0][1]]},
            "t": {"name": rel[1][2], "pos": [rel[1][0], rel[1][1]]},
        })
    elif label_strat == 'single':
        for rel, label_list in unique_rels.items():
            dataset.append({
            "token": tup[0],
            "h": {"name": rel[0][2], "pos": [rel[0][0], rel[0][1]]},
            "t": {"name": rel[1][2], "pos": [rel[1][0], rel[1][1]]},
            "relation": label_list[0]
        })
    elif label_strat == 'multi':
        for rel, label_list in unique_rels.items():
            dataset.append({
            "token": tup[0],
            "h": {"name": rel[0][2], "pos": [rel[0][0], rel[0][1]]},
            "t": {"name": rel[1][2], "pos": [rel[1][0], rel[1][1]]},
            "relation": label_list
        })
    else:
        for rel in tup[1]:
            dataset.append({
                "token": tup[0],
                "h": {"name": rel[0][2], "pos": [rel[0][0], rel[0][1]]},
                "t": {"name": rel[1][2], "pos": [rel[1][0], rel[1][1]]},
                "relation": rel[2]
            })

    return dataset

# for full sentence IE training
def save_ie_data(data_dir, out_dir, label_strat, rename, remove):
    datasets = get_datasets(data_dir)

    max_trlen = max((len(tup[0]) for tup in datasets[0]))
    print("max tr sentence length:", max_trlen)

    train = []
    for tup in datasets[0]:
        train.append(append_tuple_data(tup, label_strat))
    print(len(train), "training examples")

    val = []
    for tup in datasets[1]:
        val.append(append_tuple_data(tup, label_strat))
    print(len(val), "validation examples")

    test = []
    for tup in datasets[2]:
        test.append(append_tuple_data(tup, label_strat))
    print(len(test), "test examples")

    train = [x for sublist in train for x in sublist]
    val = [x for sublist in val for x in sublist]
    test = [x for sublist in test for x in sublist]

    if remove:
        train = [x for x in train if x['relation'] != 'NONE']
        val = [x for x in val if x['relation'] != 'NONE']
        test = [x for x in test if x['relation'] != 'NONE']

    if rename:
        for x in train:
            if x['relation'] == 'NONE':
                x['relation'] = 'NA'
        for x in val:
            if x['relation'] == 'NONE':
                x['relation'] = 'NA'
        for x in test:
            if x['relation'] == 'NONE':
                x['relation'] = 'NA'

    labels = set([x['relation'] for x in train])
    rel2id = {label: count for count, label in enumerate(labels)}

    with open(os.path.join(out_dir, 'rotowire_rel2id.json'), 'w+') as f:
	    json.dump(rel2id, f)

    with open(os.path.join(out_dir, 'rotowire_train.json'), 'w+') as f:
	    f.writelines([json.dumps(x) + '\n' for x in train])

    with open(os.path.join(out_dir, 'rotowire_val.json'), 'w+') as f:
	    f.writelines([json.dumps(x) + '\n' for x in val])

    with open(os.path.join(out_dir, 'rotowire_test.json'), 'w+') as f:
	    f.writelines([json.dumps(x) + '\n' for x in test])

def save_tuples_for_extraction(data_dir, summary_dir):
    datasets = get_datasets(data_dir, summary_dir)

    # val = [append_tuple_data(tup, None) for tup in datasets[1]]
    val = None
    test = [append_tuple_data(tup, None) for tup in datasets[2]]

    # print(len(val), "validation examples")
    print(len(test), "test examples")

    return val, test


if __name__ == '__main__': 
    save_ie_data(data_dir="../data/rotowire", out_dir="../data/ie", label_strat='single', rename=True, remove=False)