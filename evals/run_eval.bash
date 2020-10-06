#!/bin/bash

BASE="/media/yeeb/Data/data"
GPUID=1
PREFIX=$1
VAL_ID=$2
TEST_ID=$3

echo $1
echo $2
echo $3

echo "---------------- starting val set for "${1}"-----------------"

python data_utils.py -mode prep_gen_data -gen_fi $BASE/$PREFIX/$VAL_ID.txt -dict_pfx "roto-ie" -output_fi $BASE/$PREFIX/$VAL_ID.h5 -input_path "boxscore-json"
th extractor.lua -gpuid  $GPUID -datafile roto-ie.h5 -preddata $BASE/$PREFIX/$VAL_ID.h5 -dict_pfx "roto-ie" -just_eval
python non_rg_metrics.py $BASE/roto-gold-val.h5-tuples.txt $BASE/$PREFIX/$VAL_ID.h5-tuples.txt

echo "---------------- starting test set for "${1}"-----------------"

python data_utils.py -mode prep_gen_data -gen_fi $BASE/$PREFIX/$TEST_ID.txt -dict_pfx "roto-ie" -output_fi $BASE/$PREFIX/$TEST_ID.h5 -input_path "boxscore-json" -test
th extractor.lua -gpuid  $GPUID -datafile roto-ie.h5 -preddata $BASE/$PREFIX/$TEST_ID.h5 -dict_pfx "roto-ie" -just_eval -just_eval -test
python non_rg_metrics.py $BASE/roto-gold-test.h5-tuples.txt $BASE/$PREFIX/$TEST_ID.h5-tuples.txt -test