#!/usr/bin/env python

import argparse
import datetime
import json
import time
import warnings
from logging import getLogger
from pathlib import Path
from typing import Dict, List

import torch
from tqdm import tqdm

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from utils import calculate_bleu, calculate_rouge, chunks, parse_numeric_n_bool_cl_kwargs, use_task_specific_params


logger = getLogger(__name__)


DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def generate_summaries_or_translations(
    examples: List[str],
    out_file: str,
    model_name: str,
    batch_size: int = 8,
    device: str = DEFAULT_DEVICE,
    fp16=False,
    task="summarization",
    prefix=None,
    **generate_kwargs,
) -> Dict:
    """Save model.generate results to <out_file>, and return how long it took."""
    fout = Path(out_file).open("w", encoding="utf-8")
    model_name = str(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    if fp16:
        model = model.half()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    logger.info(f"Inferred tokenizer type: {tokenizer.__class__}")  # if this is wrong, check config.model_type.

    tokenizer.add_special_tokens({'additional_special_tokens': [
            '<|HOME|>', '<|AWAY|>',
            '<|PLAYER-START_POSITION|>', '<|PLAYER-MIN|>', '<|PLAYER-PTS|>', '<|PLAYER-FGM|>', '<|PLAYER-FGA|>', '<|PLAYER-FG_PCT|>', '<|PLAYER-FG3M|>', '<|PLAYER-FG3A|>', '<|PLAYER-FG3_PCT|>', '<|PLAYER-FTM|>', '<|PLAYER-FTA|>', '<|PLAYER-FT_PCT|>', '<|PLAYER-OREB|>', '<|PLAYER-DREB|>', '<|PLAYER-REB|>', '<|PLAYER-AST|>', '<|PLAYER-TO|>', '<|PLAYER-STL|>', '<|PLAYER-BLK|>', '<|PLAYER-PF|>', 
            '<|TEAM-PTS_QTR1|>', '<|TEAM-PTS_QTR2|>', '<|TEAM-PTS_QTR3|>', '<|TEAM-PTS_QTR4|>', '<|TEAM-PTS|>', '<|TEAM-FG_PCT|>', '<|TEAM-FG3_PCT|>', '<|TEAM-FT_PCT|>', '<|TEAM-REB|>', '<|TEAM-AST|>', '<|TEAM-TOV|>', '<|TEAM-WINS|>', '<|TEAM-LOSSES|>', '<|TEAM-CITY|>', '<|TEAM-NAME|>', 
        ]})
    # model.resize_token_embeddings(len(tokenizer))

    max_length = 600
    min_length = 275

    # update config with task specific params
    use_task_specific_params(model, task)


    start_time = time.time()

    if prefix is None:
        prefix = prefix or getattr(model.config, "prefix", "") or ""

    batch = tokenizer(prefix + examples[0], return_tensors="pt", max_length=1024, truncation=True, padding="max_length").to(device)
    summaries = model.generate(
            input_ids=batch.input_ids,
            attention_mask=batch.attention_mask,
            # num_beams=4,
            length_penalty=2.0,
            max_length=max_length + 2,  # +2 from original because we start at step=1 and stop before max_length
            min_length=min_length + 1,  # +1 from original because we start at step=1
            no_repeat_ngram_size=3,
            decoder_start_token_id=model.config.eos_token_id,
            **generate_kwargs,
        )
    print(summaries[0])
    print(len(summaries[0]))
    dec = tokenizer.batch_decode(summaries, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    for hyp in dec:
        print(hyp)

    
    
    for examples_chunk in tqdm(list(chunks(examples, batch_size))):
        examples_chunk = [prefix + text for text in examples_chunk]
        batch = tokenizer(examples_chunk, return_tensors="pt", max_length=1024, truncation=True, padding="max_length").to(device)
        summaries = model.generate(
            input_ids=batch.input_ids,
            attention_mask=batch.attention_mask,
            num_beams=4,
            length_penalty=2.0,
            max_length=max_length + 2,  # +2 from original because we start at step=1 and stop before max_length
            min_length=min_length + 1,  # +1 from original because we start at step=1
            no_repeat_ngram_size=3,
            decoder_start_token_id=model.config.eos_token_id,
            **generate_kwargs,
        )
        dec = tokenizer.batch_decode(summaries, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        for hypothesis in dec:
            fout.write(hypothesis + "\n")
            fout.flush()
    fout.close()
    runtime = int(time.time() - start_time)  # seconds
    n_obs = len(examples)
    return dict(n_obs=n_obs, runtime=runtime, seconds_per_sample=round(runtime / n_obs, 4))


def datetime_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_generate(verbose=True):
    """

    Takes input text, generates output, and then using reference calculates the BLEU scores.

    The results are saved to a file and returned to the caller, and printed out unless ``verbose=False`` is passed.

    Args:
        verbose (:obj:`bool`, `optional`, defaults to :obj:`True`): print results to stdout

    Returns:
        a tuple: ``(scores, params}``
        - ``scores``: a dict of scores data ``{'bleu': 39.6501, 'n_obs': 2000, 'runtime': 186, 'seconds_per_sample': 0.093}``
        - ``params``: a dict of custom params, e.g. ``{'num_beams': 5, 'length_penalty': 0.8}``
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str, help="like facebook/bart-large-cnn,t5-base, etc.")
    parser.add_argument("input_path", type=str, help="like cnn_dm/test.source")
    parser.add_argument("save_path", type=str, help="where to save summaries")
    parser.add_argument("--reference_path", type=str, required=False, help="like cnn_dm/test.target")
    parser.add_argument("--score_path", type=str, required=False, default="metrics.json", help="where to save metrics")
    parser.add_argument("--device", type=str, required=False, default=DEFAULT_DEVICE, help="cuda, cuda:1, cpu etc.")
    parser.add_argument(
        "--prefix", type=str, required=False, default=None, help="will be added to the begininng of src examples"
    )
    parser.add_argument("--task", type=str, default="summarization", help="used for task_specific_params + metrics")
    parser.add_argument("--bs", type=int, default=8, required=False, help="batch size")
    parser.add_argument(
        "--n_obs", type=int, default=-1, required=False, help="How many observations. Defaults to all."
    )
    parser.add_argument("--fp16", action="store_true")
    parser.add_argument("--dump-args", action="store_true", help="print the custom hparams with the results")
    parser.add_argument(
        "--info",
        nargs="?",
        type=str,
        const=datetime_now(),
        help="use in conjunction w/ --dump-args to print with the results whatever other info you'd like, e.g. lang=en-ru. If no value is passed, the current datetime string will be used.",
    )
    # Unspecified args like --num_beams=2 --decoder_start_token_id=4 are passed to model.generate
    args, rest = parser.parse_known_args()
    parsed_args = parse_numeric_n_bool_cl_kwargs(rest)
    if parsed_args and verbose:
        print(f"parsed the following generate kwargs: {parsed_args}")
    examples = [" " + x.rstrip() if "t5" in args.model_name else x.rstrip() for x in open(args.input_path).readlines()]
    if args.n_obs > 0:
        examples = examples[: args.n_obs]
    Path(args.save_path).parent.mkdir(exist_ok=True)
    if args.reference_path is None and Path(args.score_path).exists():
        warnings.warn(f"score_path {args.score_path} will be overwritten unless you type ctrl-c.")
    
    # args.prefix = "summarize: "
    runtime_metrics = generate_summaries_or_translations(
        examples,
        args.save_path,
        args.model_name,
        batch_size=args.bs,
        device=args.device,
        fp16=args.fp16,
        task=args.task,
        prefix=args.prefix,
        **parsed_args,
    )

    if args.reference_path is None:
        return {}

    # Compute scores
    score_fn = calculate_bleu if "translation" in args.task else calculate_rouge
    output_lns = [x.rstrip() for x in open(args.save_path).readlines()]
    reference_lns = [x.rstrip() for x in open(args.reference_path).readlines()][: len(output_lns)]
    scores: dict = score_fn(output_lns, reference_lns)
    scores.update(runtime_metrics)

    if args.dump_args:
        scores.update(parsed_args)
    if args.info:
        scores["info"] = args.info

    if verbose:
        print(scores)

    if args.score_path is not None:
        path = args.score_path
        json.dump(scores, open(path, "w"))

    return scores


if __name__ == "__main__":
    # Usage for MT:
    # python run_eval.py MODEL_NAME $DATA_DIR/test.source $save_dir/test_translations.txt --reference_path $DATA_DIR/test.target --score_path $save_dir/test_bleu.json  --task translation $@
    run_generate(verbose=True)
