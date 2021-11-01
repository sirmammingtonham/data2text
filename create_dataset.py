# -*- coding: utf-8 -*-
import json
import csv

def main(JSON, SOURCE_FILE, TARGET_FILE):
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


    def create_record(value, name, record_type, homeoraway, already_seen):
        record = []
        if name not in already_seen:
            record.append(f'{homeoraway} {name}')
            already_seen.add(name)
        record.append(f'<|{record_type}|> {value}')
        return record

    def box_preproc2(entry):
        already_seen = set()
        records = []

        for key in ls_keys:
            record = create_record(entry["home_line"][key], entry["home_line"]["TEAM-NAME"], key, HOME, already_seen)
            r = DELIM.join(record)
            if "N/A" not in r:
                records.append(r)
        for key in ls_keys:
            record = create_record(entry["vis_line"][key], entry["vis_line"]["TEAM-NAME"], key, AWAY, already_seen)
            r = DELIM.join(record)
            if "N/A" not in r:
                records.append(r)

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
                    record = create_record(val, player_name, key, HOME if ii == 0 else AWAY, already_seen)
                    r = DELIM.join(record)
                    if "N/A" not in r:
                        records.append(r)
        return records

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

    with open(JSON, "r", encoding="utf-8") as f:
        trdata = json.load(f)

    summaries = []
    src_instances = []

    for entry in trdata:
        records = box_preproc2(entry)
        src_instance = RECORD_DELIM.join(records)
        summary = entry['summary']

        summaries.append(summary)
        src_instances.append(src_instance)

    with open(SOURCE_FILE, 'w', encoding='utf-8') as source:
        source.write("\n".join(src_instances))
    with open(TARGET_FILE, 'w', encoding='utf-8') as target:
        target.write("\n".join([' '.join(summary) for summary in summaries]))

if __name__ == '__main__':
    main("rotowire/train.json", 'dataset/bart/train.source', 'dataset/bart/train.target')
    main("rotowire/valid.json", 'dataset/bart/val.source', 'dataset/bart/val.target')
    main("rotowire/test.json", 'dataset/bart/test.source', 'dataset/bart/test.target')
