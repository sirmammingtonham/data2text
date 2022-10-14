# Improving Data-to-Text Generation via Preserving High-Frequency Phrases and Fact-Checking

This repo contains code for [Improving Data-to-Text Generation via Preserving High-Frequency Phrases and Fact-Checking](https://journals.openedition.org/ijcol/909) (Joseph, Ethan, Julian Lioanag, and Mei Si. "Improving Data-to-Text Generation via Preserving High-Frequency Phrases and Fact-Checking." IJCoL. Italian Journal of Computational Linguistics 7, no. 7-1, 2 (2021): 223-244.)

## Commands for training and evaluation

```
conda create -f environment.yml
conda activate data2text

python create_dataset.py

python finetune.py --data_dir ./dataset --output_dir ./ckpt

python generate.py --source_path dataset/test.source --model_name ./ckpt --output_path ../gens/original/bart_test.txt

python create_ie_dataset.py

python ie/OpenNRE/example/train_supervised_bert.py --train_file ./data/ie/rotowire_train.txt --val_file ./data/ie/rotowire_val.txt --test_file ./data/ie/rotowire_test.txt -rel2id_file ./data/ie/rotowire_rel2id.json

python extract_relations.py

python factcheck.py

python data_utils.py -mode make_ie_data -input_path "../data/rotowire" -output_fi "../data/ratishsp/roto-ie.h5"

python data_utils.py -mode prep_gen_data -gen_fi ../gens/corrected/bart_test.txt -dict_pfx "../data/ratishsp/roto-ie" -output_fi ./tuples/bart_test_tuples.h5 -input_path "../data/rotowire" -test

th extractor.lua -gpuid 1 -datafile ../data/ratishsp/roto-ie.h5 -preddata tuples/bart_test_tuples.h5 -dict_pfx "../data/ratishsp/roto-ie" -just_eval -test

python non_rg_metrics.py ./tuples/roto-gold-test.h5-tuples.txt ./tuples/bart_test_tuples.h5-tuples.txt -test

python nlg_metrics.py --ref ..\data\rotowire\tgt_test.txt --hyp ..\gens\corrected\bart_test.txt
```

## Citation
```
@article{joseph2021improving,
  title={Improving Data-to-Text Generation via Preserving High-Frequency Phrases and Fact-Checking},
  author={Joseph, Ethan and Lioanag, Julian and Si, Mei},
  journal={IJCoL. Italian Journal of Computational Linguistics},
  volume={7},
  number={7-1, 2},
  pages={223--244},
  year={2021},
  publisher={Accademia University Press}
}
```
