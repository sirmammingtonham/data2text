import os
import json
import torch
from tqdm import tqdm
import OpenNRE.opennre as opennre
from create_ie_dataset import get_dataset_for_extraction

sentence_encoder = opennre.encoder.TransformerEntityEncoder(
	max_length=128,
	pretrain_path='roberta-base',
	mask_entity=False
)

rel2id = json.load(open('../data/ie/rotowire_rel2id.json'))
model = opennre.model.SoftmaxNN(sentence_encoder, len(rel2id), rel2id)
model.load_state_dict(torch.load('./OpenNRE/ckpt/none_roberta-base_entity.pth.tar')['state_dict'])
model.to(torch.device('cuda:0'))

def extract(dataset):
	for sentence in tqdm(dataset):
		sentence['relation'] = model.infer(sentence)[0]
	return dataset

if __name__ == '__main__':
	for model_name in ('bart', 't5', 'pegasus'):
		print(f'Extracting relations for {model_name}')
		_, test = get_dataset_for_extraction(data_dir="../data/rotowire", summary_dir=f"../gens/original/{model_name}")
		extracted_relations = extract(test)

		with open(os.path.join(f'../gens/original/relations', f'{model_name}_test.json'), 'w+') as f:
			json.dump(extracted_relations, f)