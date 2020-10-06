# -*- coding: utf-8 -*-
import sys, codecs

SRC_FILE = sys.argv[1]
CONTENT_PLAN = sys.argv[2]
EVAL_OUTPUT = sys.argv[3]
CONTENT_PLAN_INTER = sys.argv[4]

TRAIN = True
DELIM = u"￨"

inputs = []
content_plans = []
with open(CONTENT_PLAN, "r", encoding="utf-8") as corpus_file:
	for _, line in enumerate(corpus_file):
		content_plans.append(line.split())
with open(SRC_FILE, "r", encoding="utf-8") as corpus_file:
	for _, line in enumerate(corpus_file):
		inputs.append(line.split())

outputs = []
eval_outputs = []
for i, inp in enumerate(inputs):
	content_plan = content_plans[i]
	output = []
	eval_output = []
	records = set()
	for record in content_plan:
		output.append(inp[int(record)])
		elements = inp[int(record)].split(DELIM)
		if elements[0].isdigit():
			record_type = elements[2]
			if not elements[2].startswith('TEAM'):
				record_type = 'PLAYER-'+ record_type
			eval_output.append(" ".join([f'<|{record_type}|>', elements[0], ">>", elements[1].replace("_"," "), f'<|{elements[3]}|>']))
	outputs.append(" ".join(output))
	eval_outputs.append(" ".join(eval_output))

# with open(CONTENT_PLAN_INTER, 'w', encoding="utf-8") as output_file:
#     output_file.write("\n".join(outputs))
#     output_file.write("\n")

with open(EVAL_OUTPUT, 'w', encoding="utf-8") as output_file:
	with open(CONTENT_PLAN_INTER, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		for bruh, this in zip(eval_outputs, lines): 
			output_file.write(f"{bruh} <|sosummary|> {this[:-1]} <|endoftext|>\n")
		# output_file.write("\n".join(eval_outputs))
