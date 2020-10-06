# -*- coding: utf-8 -*-
from text_to_num import text2num
import codecs, json
import csv

# TOKEN_FILE = 'dataset/tokens.csv'
# SRC_FILE = 'rotowire/src_train.txt'  # src file input to first stage
# TRAIN_TGT_FILE = "rotowire/tgt_train.txt"  # tgt file of second stage
# CONTENT_PLAN_OUT = 'rotowire/train_content_plan.txt'  # content plan output of first stage:

def main(JSON, ORACLE_IE_OUTPUT, GPT2_TRAIN, CP_INPUT, CP_OUTPUT, xlnet=False):

    # RECORD_DELIM = " <|endofstat|> "
    RECORD_DELIM = " "
    DELIM = " "
    NUM_PLAYERS = 13

    HOME = "<|HOME|>"
    AWAY = "<|AWAY|>"

    bs_keys = ["PLAYER-START_POSITION", "PLAYER-MIN", "PLAYER-PTS",
        "PLAYER-FGM", "PLAYER-FGA", "PLAYER-FG_PCT", "PLAYER-FG3M", "PLAYER-FG3A",
        "PLAYER-FG3_PCT", "PLAYER-FTM", "PLAYER-FTA", "PLAYER-FT_PCT", "PLAYER-OREB",
        "PLAYER-DREB", "PLAYER-REB", "PLAYER-AST", "PLAYER-TO", "PLAYER-STL", "PLAYER-BLK",
        "PLAYER-PF", "PLAYER-FIRST_NAME", "PLAYER-SECOND_NAME"]

    ls_keys = ["TEAM-PTS_QTR1", "TEAM-PTS_QTR2", "TEAM-PTS_QTR3", "TEAM-PTS_QTR4",
        "TEAM-PTS", "TEAM-FG_PCT", "TEAM-FG3_PCT", "TEAM-FT_PCT", "TEAM-REB",
        "TEAM-AST", "TEAM-TOV", "TEAM-WINS", "TEAM-LOSSES", "TEAM-CITY", "TEAM-NAME"]

    def box_preproc2(entry):
        records = []

        home_players, vis_players = get_player_idxs(entry)
        for ii, player_list in enumerate([home_players, vis_players]):
            for j in range(NUM_PLAYERS):
                player_key = player_list[j] if j < len(player_list) else None
                player_name = entry["box_score"]['PLAYER_NAME'][player_key] if player_key is not None else "N/A"
                for key in bs_keys:
                    if key == "PLAYER-FIRST_NAME" or key == "PLAYER-SECOND_NAME":
                        continue
                    rulkey = key.split('-')[1]
                    val = entry["box_score"][rulkey][player_key] if player_key is not None else "N/A"
                    record = []
                    record.append(f'<|{key}|>')
                    record.append(player_name.replace(" ","_"))
                    record.append('>>')
                    record.append(val.replace(" ","_"))
                    record.append(HOME if ii == 0 else AWAY)
                    records.append(DELIM.join(record))

        for key in ls_keys:
            record = []
            record.append(f'<|{key}|>')
            record.append(entry["home_line"]["TEAM-NAME"].replace(" ","_"))
            record.append('>>')
            record.append(entry["home_line"][key].replace(" ","_"))
            record.append(HOME)
            records.append(DELIM.join(record))
        for key in ls_keys:
            record = []
            record.append(f'<|{key}|>')
            record.append(entry["vis_line"][key].replace(" ","_"))
            record.append('>>')
            record.append(entry["vis_line"]["TEAM-NAME"].replace(" ","_"))
            record.append(AWAY)
            records.append(DELIM.join(record))
        return records

    def get_ents(thing):
        players = set()
        teams = set()
        cities = set()
        total_teams = set()

        teams.add(thing["vis_name"])
        teams.add(thing["vis_line"]["TEAM-NAME"])
        teams.add(thing["vis_city"] + " " + thing["vis_name"])
        teams.add(thing["vis_city"] + " " + thing["vis_line"]["TEAM-NAME"])

        total_teams.add(thing["vis_city"] + " " + thing["vis_name"])
        total_teams.add(thing["vis_city"] + " " + thing["vis_line"]["TEAM-NAME"])
        teams.add(thing["home_name"])
        teams.add(thing["home_line"]["TEAM-NAME"])
        teams.add(thing["home_city"] + " " + thing["home_name"])
        teams.add(thing["home_city"] + " " + thing["home_line"]["TEAM-NAME"])

        total_teams.add(thing["home_city"] + " " + thing["home_name"])
        total_teams.add(thing["home_city"] + " " + thing["home_line"]["TEAM-NAME"])
        # special case for this
        if thing["vis_city"] == "Los Angeles":
            teams.add("LA" + thing["vis_name"])
        if thing["home_city"] == "Los Angeles":
            teams.add("LA" + thing["home_name"])
        if thing["vis_city"] == "LA":
            teams.add("Los Angeles " + thing["vis_name"])
        if thing["home_city"] == "LA":
            teams.add("Los Angeles " + thing["home_name"])
        # sometimes team_city is different
        cities.add(thing["home_city"])
        cities.add(thing["vis_city"])
        players.update(thing["box_score"]["PLAYER_NAME"].values())
        cities.update(thing["box_score"]["TEAM_CITY"].values())
        total_players = players.copy()
        total_cities = cities.copy()
        for entset in [players, teams, cities]:
            for k in list(entset):
                pieces = k.split()
                if len(pieces) > 1:
                    for piece in pieces:
                        if len(piece) > 1 and piece not in ["II", "III", "Jr.", "Jr"]:
                            entset.add(piece)

        all_ents = players | teams | cities

        return all_ents, players, teams, cities, total_players, total_teams, total_cities


    def resolve_name(name, total_players):
        for player_name in total_players:
            if name in player_name.split():
                return player_name
        return name
    def resolve_team_name(name, total_teams):
        for team_name in total_teams:
            if name in team_name.split():
                return team_name
            elif len(team_name.split())>2 and ((name == " ".join(team_name.split()[1:3])) or (name == " ".join(team_name.split()[0:2]))):
                return team_name
        return name

    def get_player_idxs(entry):
        nplayers = 0
        home_players, vis_players = [], []
        for _ in entry["box_score"]["PTS"].items():
            nplayers += 1

        num_home, num_vis = 0, 0
        for i in range(nplayers):
            player_city = entry["box_score"]["TEAM_CITY"][str(i)]
            if player_city == entry["home_city"]:
                if len(home_players) < NUM_PLAYERS:
                    home_players.append(str(i))
                    num_home += 1
            else:
                if len(vis_players) < NUM_PLAYERS:
                    vis_players.append(str(i))
                    num_vis += 1

        if entry["home_city"] == entry["vis_city"] and entry["home_city"] == "Los Angeles":
            home_players, vis_players = [], []
            num_home, num_vis = 0, 0
            for i in range(nplayers):
                if len(vis_players) < NUM_PLAYERS:
                    vis_players.append(str(i))
                    num_vis += 1
                elif len(home_players) < NUM_PLAYERS:
                    home_players.append(str(i))
                    num_home += 1

        return home_players, vis_players

    def replace(input):
        return input.replace(" ", "_")

    with codecs.open(JSON, "r", "utf-8") as f:
        trdata = json.load(f)

    output_instances = []
    instance_count = -1 #exclude the first blank line of output
    output = []
    outputs =[]
    exists = set()
    name_exists = set()
    summaries = []
    src_instances = []
    src_instance = ''
    summary = ''
    special_tokens = set()

    def create_record(value, name, record_type, homeoraway, output):
        # if "_NAME" in record_type:
        #     return ['']
        record = []
        first = True
        for x in output:
            if name in x:
                first = False
                break
        if first:
            record.append(f'{homeoraway} {name}')
        record.append(f'<|{record_type}|> {value}')
        # record.append(f'<|sorecord|>{name.replace(" ", "_")}<|eorecord|>')
        # special_tokens.add(f'<|{name.replace(" ", "_")}|>')
        # record.append(f'<|sovalue|>{value}<|eovalue|>')
        # record.append(homeoraway)
        return record


    for line in open(ORACLE_IE_OUTPUT):
        if len(line.strip())==0:
            exists = set()
            name_exists = set()
            instance_count += 1
            if instance_count>=1:
                if len(output)>0:
                    outputs.append(RECORD_DELIM.join(output))
                    summaries.append(summary)
                    src_instances.append(src_instance)
                output = []
                src_instance = ''
                summary = ''

            entry = trdata[instance_count]
            records = box_preproc2(entry)
            src_instance = RECORD_DELIM.join(records)
            all_ents, players, teams, cities, total_players, total_teams, total_cities = get_ents(entry)
            home_players, vis_players = get_player_idxs(entry)
            box_score = entry["box_score"]
            player_name_map = {y: x for x, y in box_score['PLAYER_NAME'].items()}
            home_line_score = entry["home_line"]
            vis_line_score = entry["vis_line"]
            summary = entry['summary']
        else:
            args = line.split("|")
            name = args[0]
            record_type = args[2].strip()
            value = args[1]
            if not value.isdigit():
                value = text2num(value, 'en')
            if record_type.startswith("PLAYER-"):
                record_type = record_type[len("PLAYER-"):]

            name = name.replace("UNK","").strip()
            if name == 'Los Angeles' and 'LA' in total_cities:
                name = 'LA'
            if name in total_players:
                pass
            elif name in total_teams:
                pass
            elif name in players:
                name = resolve_name(name, total_players)
            elif name == 'Los Angeles Clippers' and 'LA Clippers' in total_teams:
                name = 'LA Clippers'
            elif name in teams:
                name = resolve_team_name(name, total_teams)
            elif name in total_cities:
                name = resolve_team_name(name, total_teams)

            record_added = False
            if not (name, record_type, int(value)) in exists:
                if name in player_name_map and record_type in box_score and box_score[record_type][player_name_map[name]].isdigit() and  int(box_score[record_type][player_name_map[name]]) == int(value):
                    homeoraway = ""
                    if player_name_map[name] in home_players:
                        homeoraway = HOME
                    elif player_name_map[name] in vis_players:
                        homeoraway = AWAY

                    record = create_record(str(value), name, record_type, homeoraway, output)
                    output.append(DELIM.join(record))
                    record_added = True
                elif name.endswith(home_line_score['TEAM-NAME']) and int(home_line_score[record_type]) == int(value):
                    if name not in name_exists:
                        record = create_record(home_line_score['TEAM-CITY'].replace(" ", "_"),
                                            home_line_score['TEAM-NAME'].replace(" ", "_"), "TEAM-CITY", HOME, output)
                        output.append(DELIM.join(record))

                    record = create_record(str(value), home_line_score['TEAM-NAME'].replace(" ", "_"), record_type, HOME, output)
                    output.append(DELIM.join(record))
                    record_added = True
                elif name.endswith(vis_line_score['TEAM-NAME']) and int(vis_line_score[record_type]) == int(value):
                    if name not in name_exists:
                        record = create_record(vis_line_score['TEAM-CITY'].replace(" ", "_"),
                                            vis_line_score['TEAM-NAME'].replace(" ", "_"), "TEAM-CITY", AWAY, output)
                        output.append(DELIM.join(record))

                    record = create_record(str(value), vis_line_score['TEAM-NAME'].replace(" ", "_"), record_type, AWAY, output)
                    output.append(DELIM.join(record))
                    record_added = True
                if record_added:
                    exists.add((name, record_type, int(value)))
                    name_exists.add(name)

    outputs.append(RECORD_DELIM.join(output))
    summaries.append(summary)
    src_instances.append(src_instance)

    if xlnet:
        with open(GPT2_TRAIN, 'w', encoding='utf-8') as gpt_finetune:
            for src_instance, summary in zip(src_instances, summaries):
                # write the record part
                gpt_finetune.write(src_instance)
                # write the summary part
                gpt_finetune.write(' <|sosummary|> ')
                gpt_finetune.write(' '.join(summary))
                # end with token
                gpt_finetune.write(' <|endoftext|>\n')
    else:
        with open(GPT2_TRAIN, 'w', encoding='utf-8') as gpt_finetune:
            for output, summary in zip(outputs, summaries):
                # write the record part
                gpt_finetune.write(output)
                # write the summary part
                gpt_finetune.write(' <|sosummary|> ')
                gpt_finetune.write(' '.join(summary))
                # end with token
                # gpt_finetune.write(' <|eosummary|> <|endoftext|>\n')
                gpt_finetune.write(' <|endoftext|>\n')

                ## testing sentence level generation (fail)
                # stats = output.split('<SPLIT>')
                # summ = [x + '.' for x in (' '.join(summary)).split('.')]
                # for i in range(0, len(stats)):
                #     output_file.write(stats[i])
                #     output_file.write(summ[i])
                # output_file.write('<|endoftext|>')
        with open(CP_INPUT, 'w', encoding='utf-8') as cp_input:
            for src_instance in src_instances:
                cp_input.write(src_instance)
                cp_input.write("\n")

        with open(CP_OUTPUT, 'w', encoding='utf-8') as cp_output:
            for output in outputs:
                cp_output.write(output)
                cp_output.write('\n')


if __name__ == '__main__':
    # main("rotowire/train.json", 'rotowire/roto_train-beam5_gens.h5-tuples.txt', 'dataset/xlnet/train.txt', '', '', True)
    # main("rotowire/valid.json", 'rotowire/roto-gold-val.h5-tuples.txt', 'dataset/xlnet/valid.txt', '', '', True)
    # main("rotowire/test.json", 'rotowire/roto-gold-test.h5-tuples.txt', 'dataset/xlnet/test.txt', '', '',  True)

    main("rotowire/train.json", 'rotowire/roto_train-beam5_gens.h5-tuples.txt', 'dataset/train_gpt.txt', 'dataset/train_cp_in.txt', 'dataset/train_cp_out.txt')
    main("rotowire/valid.json", 'rotowire/roto-gold-val.h5-tuples.txt', 'dataset/valid_gpt.txt', 'dataset/valid_cp_in.txt', 'dataset/valid_cp_out.txt')
    main("rotowire/test.json", 'rotowire/roto-gold-test.h5-tuples.txt', 'dataset/test_gpt.txt', 'dataset/test_cp_in.txt', 'dataset/test_cp_out.txt')