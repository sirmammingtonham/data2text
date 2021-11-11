import os, sys
import json
import torch
from tqdm import tqdm
import OpenNRE.opennre as opennre
from create_ie_dataset import save_tuples_for_extraction

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
		for relation in sentence:
			relation['relation'] = model.infer(relation)[0]
	return dataset

if __name__ == '__main__':
	model_name = sys.argv[1]
	_, test = save_tuples_for_extraction(data_dir="../data/rotowire", summary_dir=f"../data/{model_name}")
	extracted_tuples = extract(test)

	with open(os.path.join(f'../data/{model_name}', f'{model_name}_test_tuples.txt'), 'w+') as f:
	    f.writelines([json.dumps(x) + '\n' for x in extracted_tuples])
