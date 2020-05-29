import json
from num2words import num2words

t = open('rotowire/valid.json')
data = json.load(t)
t.close()

data_ct = 0
newline_ct = 0
err_list = [0] * 727

total_score_list = []
total_score_gen_list = []
total_name_list = []
score_list = []
score_gen_list = []
name_list = []
flag_worded = []
total_flag_worded = []

cat_list = []

fake_ct = 0

def search_player(name, index):
	player_keys = list(data[index]['box_score']['PLAYER_NAME'])
	player_vals = list(data[index]['box_score']['PLAYER_NAME'].values())
	for p in player_vals:
		if name in p:
			return player_keys[player_vals.index(p)]

	return 'NONE'

def search_team(name, index):
	if data[index]['home_city'] in name or data[index]['home_name'] in name:
		return 'home'
	elif data[index]['vis_city'] in name or data[index]['vis_name'] in name:
		return 'vis'
	else:
		return 'NONE'
		
with open('roto_stage2_bart_valid_update-beam5_gens.h5-tuples.txt', 'r') as f:
	ct = 0
	for line in f:
		# Debug
		# if ct == 500:
		# 	break
		# if data_ct == 5:
		# 	break

		# print(line.split('|'))
		if line != '\n':
			data_ct += newline_ct

			line = line[:-1]
			line_list = line.split('|')
			# print(line_list)

			score_gen_list.append(line_list[1])
			name_list.append(line_list[0])


			# Convert worded nums to digits
			if not line_list[1].isdigit():
				flag_worded.append(True)
			else:
				flag_worded.append(False)

			if line_list[1] == 'one':
				line_list[1] = '1'
			elif line_list[1] == 'two':
				line_list[1] = '2'
			elif line_list[1] == 'three':
				line_list[1] = '3'
			elif line_list[1] == 'four':
				line_list[1] = '4'
			elif line_list[1] == 'five':
				line_list[1] = '5'
			elif line_list[1] == 'six':
				line_list[1] = '6'
			elif line_list[1] == 'seven':
				line_list[1] = '7'
			elif line_list[1] == 'eight':
				line_list[1] = '8'
			elif line_list[1] == 'nine':
				line_list[1] = '9'
			elif line_list[1] == 'ten':
				line_list[1] = '10'


			category = line_list[2]
			# print(category)

			if category == 'TEAM-FG_PCT':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-FG_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-FG_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-FG3_PCT':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-FG3_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-FG3_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-TOV':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-TOV']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-TOV']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-WINS':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-WINS']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-WINS']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-LOSSES':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-LOSSES']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-LOSSES']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-PTS':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-PTS']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-PTS']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-PTS_QTR1':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-PTS_QTR1']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-PTS_QTR1']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-REB':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-REB']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-REB']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-FT_PCT':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-FT_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-FT_PCT']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-PTS_QTR4':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-PTS_QTR4']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-PTS_QTR4']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'TEAM-AST':
				team_type = search_team(line_list[0], data_ct)

				if team_type == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Team ' + line_list[0] + ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					if team_type == 'home':
						value = data[data_ct]['home_line']['TEAM-AST']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value, ' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

					elif team_type == 'vis':
						value = data[data_ct]['vis_line']['TEAM-AST']

						if value != line_list[1]:
							print('Index:', data_ct, line_list)
							print('\tERROR: Values do not match ', value,' vs ', line_list[1])
							err_list[data_ct] += 1

						score_list.append(value)

			elif category == 'PLAYER-STL':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['STL'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-MIN':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['MIN'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FGM':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FGM'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FG3M':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FG3M'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FGA':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FGA'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FTA':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FTA'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FGA':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FGA'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FTM':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FTM'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-PTS':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['PTS'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-BLK':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['BLK'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FG3_PCT':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FG3_PCT'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-FG3A':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['FG3A'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-TO':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['TO'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-OREB':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['OREB'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-REB':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['REB'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-PF':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['PF'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			elif category == 'PLAYER-AST':
				index = search_player(line_list[0], data_ct)

				if index == 'NONE':
					print('Index:', data_ct, line_list)
					print('\tERROR: Player ', line_list[0], ' not in match.')
					fake_ct += 1
					err_list[data_ct] += 1

					score_list.append(line_list[1])
				else:
					value = data[data_ct]['box_score']['AST'][index]

					if value != line_list[1]:
						print('Index:', data_ct, line_list)
						print('\tERROR: Values do not match ', value,' vs ', line_list[1])
						err_list[data_ct] += 1

					score_list.append(value)

			else:
				print('Index:', data_ct, line_list)
				print('\t\tWARNING: Category ', category, 'nonexistant')
				if category not in cat_list:
					cat_list.append(category)


			newline_ct = 0


		elif line == '\n':
			newline_ct += 1

			total_score_list.append(score_list)
			total_score_gen_list.append(score_gen_list)
			total_name_list.append(name_list)

			total_flag_worded.append(flag_worded)

			score_list = []
			score_gen_list = []
			name_list = []

			flag_worded = []


		ct += 1

total_score_list.append(score_list)
total_score_gen_list.append(score_gen_list)
total_name_list.append(name_list)
total_flag_worded.append(flag_worded)

# print(len(total_flag_worded), len(total_score_gen_list))

# print(err_list)
# print(len(err_list))
# print(data_ct + 1)

err_sum = 0
for count in err_list:
	err_sum += count
# print(err_sum/len(err_list))

# print(cat_list)

# assert len(total_score_list) == len(total_score_gen_list) == len(total_name_list)
# print(total_score_list)
# print(total_score_gen_list)
# print(total_name_list)
out_text = []
ct = 0

with open('bart_updated_valid.txt', 'r') as f:
	for paragraph in f:
		
		# if ct == 1:
		# 	break

		out_paragraph = ''

		# Make list of all sentences
		sentences = paragraph.split('.')
		sentences.pop(-1)
		# print(len(total_score_list[ct]))

		while len(total_score_list[ct]) > 0:
			# if ct == 0:
			# 	print(total_name_list[ct][0], total_score_gen_list[ct][0], total_score_list[ct][0])
			for index in range(len(sentences)):
				if total_name_list[ct][0] in sentences[index] and any(total_score_gen_list[ct][0] == w for w in sentences[index].split(' ')):
					if total_score_list[ct][0] == 'N/A':
						total_score_list[ct][0] = '0'

					if total_flag_worded[ct][0]:
						sentences[index] = sentences[index].replace(total_score_gen_list[ct][0], num2words(total_score_list[ct][0]), 1)
					else:
						sentences[index] = sentences[index].replace(total_score_gen_list[ct][0], total_score_list[ct][0], 1)
					break

			total_score_list[ct].pop(0)
			total_score_gen_list[ct].pop(0)
			total_name_list[ct].pop(0)

			total_flag_worded[ct].pop(0)


		for sentence in sentences:
			out_paragraph += sentence
			out_paragraph += '.'

		out_text.append(out_paragraph)

		ct += 1
		
		# print(sentences)

with open('bart_valid_corrected.txt', 'w') as f:
	f.writelines("%s\n" % par for par in out_text)