# data2text
wip

`python ./OpenNRE/example/train_supervised_bert.py --train_file ./data/ie/rotowire_train.txt --val_file ./data/ie/rotowire_val.txt --test_file ./data/ie/rotowire_test.txt -rel2id_file ./data/ie/rotowire_rel2id.json`


`python data_utils.py -mode prep_gen_data -gen_fi ../gens/corrected/bart_test.txt -dict_pfx "roto-ie" -output_fi ./tuples/bart_test_tuples.h5 -input_path "../data/rotowire"`

```
python data_utils.py -mode make_ie_data -input_path "../data/rotowire" -output_fi "../data/ratishsp/roto-ie.h5"

python data_utils.py -mode prep_gen_data -gen_fi ../gens/corrected/bart_test.txt -dict_pfx "../data/ratishsp/roto-ie" -output_fi ./tuples/bart_test_tuples.h5 -input_path "../data/rotowire" -test


python data_utils.py -mode prep_gen_data -gen_fi ../gens/corrected/bart_test.txt -dict_pfx "../data/ratishsp/roto-ie" -output_fi ./tuples/bart_test_tuples.h5 -input_path "../data/rotowire" -test

th extractor.lua -gpuid 1 -datafile ../data/ratishsp/roto-ie.h5 -preddata tuples/bart_test_tuples.h5 -dict_pfx "../data/ratishsp/roto-ie" -just_eval -test

python non_rg_metrics.py ./tuples/roto-gold-test.h5-tuples.txt ./tuples/bart_test_tuples.h5-tuples.txt -test
```