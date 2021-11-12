import argparse
from pathlib import Path

import torch
from tqdm import tqdm

from transformers import BartTokenizer, BartForConditionalGeneration
from d2t_bart import BartForData2TextGeneration


DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def generate_summaries(
    examples: list, out_file: str, model_name: str, batch_size: int = 8, device: str = DEFAULT_DEVICE
):
    fout = Path(out_file).open("w")
    model = BartForConditionalGeneration.from_pretrained(model_name).to(device)

    # workaround to load the checkpoint
    ckpt = torch.load('output/checkpointepoch=2.ckpt')
    state_dict = {}
    for key, value in ckpt['state_dict'].items():
        state_dict[key[6:]] = value
    model.load_state_dict(state_dict)

    tokenizer = BartTokenizer.from_pretrained("bart-large")
    tokenizer.add_special_tokens({'additional_special_tokens': [
        '<|HOME|>', '<|AWAY|>',
        '<|PLAYER-START_POSITION|>', '<|PLAYER-MIN|>', '<|PLAYER-PTS|>', '<|PLAYER-FGM|>', '<|PLAYER-FGA|>', '<|PLAYER-FG_PCT|>', '<|PLAYER-FG3M|>', '<|PLAYER-FG3A|>', '<|PLAYER-FG3_PCT|>', '<|PLAYER-FTM|>', '<|PLAYER-FTA|>', '<|PLAYER-FT_PCT|>', '<|PLAYER-OREB|>', '<|PLAYER-DREB|>', '<|PLAYER-REB|>', '<|PLAYER-AST|>', '<|PLAYER-TO|>', '<|PLAYER-STL|>', '<|PLAYER-BLK|>', '<|PLAYER-PF|>', 
        '<|TEAM-PTS_QTR1|>', '<|TEAM-PTS_QTR2|>', '<|TEAM-PTS_QTR3|>', '<|TEAM-PTS_QTR4|>', '<|TEAM-PTS|>', '<|TEAM-FG_PCT|>', '<|TEAM-FG3_PCT|>', '<|TEAM-FT_PCT|>', '<|TEAM-REB|>', '<|TEAM-AST|>', '<|TEAM-TOV|>', '<|TEAM-WINS|>', '<|TEAM-LOSSES|>', '<|TEAM-CITY|>', '<|TEAM-NAME|>', 
    ]})

    max_length = 600
    min_length = 275

    for batch in tqdm(list(chunks(examples, batch_size))):
        dct = tokenizer.batch_encode_plus(batch, max_length=1300, return_tensors="pt", pad_to_max_length=True)
        summaries = model.generate(
            input_ids=dct["input_ids"].to(device),
            attention_mask=dct["attention_mask"].to(device),
            num_beams=5,
            # temperature=0.75,
            # top_k=65,
            # top_p=0.9,
            length_penalty=2.0,
            max_length=max_length + 2,  # +2 from original because we start at step=1 and stop before max_length
            min_length=min_length + 1,  # +1 from original because we start at step=1
            no_repeat_ngram_size=3,
            early_stopping=True,
            decoder_start_token_id=model.config.eos_token_id,

            # bad_words_ids=[tokenizer.encode(bad_word, add_prefix_space=True) for bad_word in ['Atlanta Hawks', 'Orlando Magic']]
        )
        dec = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summaries]
        for hypothesis in dec:
            fout.write(hypothesis + "\n")
            fout.flush()


def run_generate():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_path", type=str, help="like cnn_dm/test.source",
    )
    parser.add_argument(
        "output_path", type=str, help="where to save summaries",
    )
    parser.add_argument(
        "model_name", type=str, default="bart-large-cnn", help="like bart-large-cnn",
    )
    parser.add_argument(
        "--device", type=str, required=False, default=DEFAULT_DEVICE, help="cuda, cuda:1, cpu etc.",
    )
    parser.add_argument(
        "--bs", type=int, default=8, required=False, help="batch size: how many to summarize at a time",
    )
    args = parser.parse_args()
    examples = [" " + x.rstrip() for x in open(args.source_path).readlines()]
    generate_summaries(examples, args.output_path, args.model_name, batch_size=args.bs, device=args.device)


if __name__ == "__main__":
    run_generate()