import argparse
from sacrebleu.metrics import BLEU
from rouge_score import rouge_scorer, scoring
from nltk.translate import meteor_score

parser = argparse.ArgumentParser()
parser.add_argument('--ref', help='reference file/gold standard')
parser.add_argument('--hyp', help='hypothesis/generated file')

ROUGE_KEYS = ('rouge1', 'rouge2', 'rougeL')

def calculate_bleu(output_lns, reference_lns):
    bleu = BLEU()
    return bleu.corpus_score(output_lns, (reference_lns,))

def calculate_rouge(output_lns, reference_lns, use_stemmer=True):
    scorer = rouge_scorer.RougeScorer(ROUGE_KEYS, use_stemmer=use_stemmer)
    aggregator = scoring.BootstrapAggregator()

    for reference_ln, output_ln in zip(reference_lns, output_lns):
        scores = scorer.score(reference_ln, output_ln)
        aggregator.add_scores(scores)

    result = aggregator.aggregate()
    return {k: round(v.mid.fmeasure * 100, 4) for k, v in result.items()}

def calculate_meteor(output_lns, reference_lns):
    aggregator = scoring.BootstrapAggregator()

    for reference_ln, output_ln in zip(reference_lns, output_lns):
        scores = meteor_score.single_meteor_score(reference_ln, output_ln)
        aggregator.add_scores({'meteor': scores})
    
    result = aggregator.aggregate()
    return {k: round(v.mid * 100, 4) for k, v in result.items()}


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.ref, 'r', encoding='utf-8') as ref:
        with open(args.hyp, 'r') as hyp:
            h = hyp.readlines()
            r = ref.readlines()
            print(calculate_bleu(h, r))
            print(calculate_rouge(h, r))
            print(calculate_meteor(h, r))