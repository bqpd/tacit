import json
import pprint
from decimal import Decimal

pp = pprint.PrettyPrinter(indent=2)

with open('tacit-collab-export.json') as data:
	data = json.load(data)
	for pilotnum in data:
		if pilotnum != "pilot3": # don't include pilot 3 (not valid data)
			pp.pprint(pilotnum)
			for user in data[pilotnum]:
				for problem in user:
					best_score = 10000
					if not "tutorial" in problem: # don't include tutorial
						events = user[problem]["events"]
						structures = user[problem]["structures"]
						meta = user[problem]["meta"]
						for structure_id in structures:
							structure = structures[structure_id]
							if (Decimal(structure["weight"])/100) < best_score:
								best_score = Decimal(structure["weight"])/100
						print best_score
