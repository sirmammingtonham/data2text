import json, os
from nltk import sent_tokenize, word_tokenize
from tqdm import tqdm

def factcheck(model_name, dataset='test'):
    relation_path = f'./gens/original/relations/{model_name}_{dataset}.json'
    summary_path = f'./gens/original/{model_name}_{dataset}.txt'

    with open(os.path.join('./data/rotowire', f'{dataset}.json'), 'r', encoding='utf-8') as f:
        orig_data = json.load(f)

    with open(relation_path, 'r') as f:
        relations = json.loads(f.read())

    with open(summary_path, 'r') as f:
        # have to word tokenize, join, then sent tokenize to avoid some small errors
        output = {i: [x.split() for x in sent_tokenize(' '.join(word_tokenize(y)))] for i, y in enumerate(f.readlines())}

    total_fixed = 0

    for relation in tqdm(relations):
        sum_idx = relation['summary']
        sent_idx = relation['sentence']
        test_json = orig_data[sum_idx]

        h_name = relation['h']['name']
        t = relation['t']['name']
        t_pos = relation['t']['pos'][0]
        rel = relation['relation']

        if rel == 'NA':
            continue
        try:
            if h_name in [f"{test_json['home_city']} {test_json['home_name']}", test_json['home_city'], test_json['home_name']]:
                correct = test_json['home_line'][rel]
            elif h_name in [f"{test_json['vis_city']} {test_json['vis_name']}", test_json['vis_city'], test_json['vis_name']]:
                correct = test_json['vis_line'][rel]
            else:
                if h_name in test_json['box_score']['FIRST_NAME'].values():
                    pid = list(test_json['box_score']['FIRST_NAME'].keys())[list(test_json['box_score']['FIRST_NAME'].values()).index(h_name)]
                elif h_name in test_json['box_score']['SECOND_NAME'].values():
                    pid = list(test_json['box_score']['SECOND_NAME'].keys())[list(test_json['box_score']['SECOND_NAME'].values()).index(h_name)]
                elif h_name in test_json['box_score']['PLAYER_NAME'].values():
                    pid = list(test_json['box_score']['PLAYER_NAME'].keys())[list(test_json['box_score']['PLAYER_NAME'].values()).index(h_name)]
                else:
                    continue
                correct = test_json['box_score'][rel.replace('PLAYER-', '')][pid]
        except Exception as e:
            print(e)
            continue

        if str(t) != correct:
            total_fixed += 1

        output[sum_idx][sent_idx][t_pos] = correct

    with open(f'./gens/corrected/{model_name}_{dataset}.txt', 'w+') as f:
        f.write('\n'.join(' '.join(' '.join(sent) for sent in summary) for summary in output.values()))

if __name__ == '__main__':
    for model_name in ('bart', 't5', 'pegasus'):
        factcheck(model_name)