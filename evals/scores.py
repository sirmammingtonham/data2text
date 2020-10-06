import sys
from rouge_score import rouge_scorer, scoring
from nltk.translate import meteor_score

ROUGE_KEYS = ["rouge1", "rouge2", "rougeL"]

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
        aggregator.add_scores({"meteor": scores})
    
    result = aggregator.aggregate()

    return {k: round(v.mid * 100, 4) for k, v in result.items()}


if __name__ == "__main__":
    with open(sys.argv[1], 'r', encoding='utf-8') as ref:
        with open(sys.argv[2], 'r', encoding='utf-8') as hyp:
            h = hyp.readlines()
            r = ref.readlines()
            print(calculate_rouge(h, r))
            print(calculate_meteor(h, r))