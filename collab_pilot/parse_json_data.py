import os
import numpy
import matplotlib.pyplot as mlp
import json
import pprint
from matplotlib.pyplot import *

pp = pprint.PrettyPrinter(indent=2)

best_scores_each_user = []
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
							if not "weight" in structure:
								# ran out of time event accidentally saved
								# in structures instead of events, fixed
								continue
							elif (float(structure["weight"])/100) < best_score:
								best_score = float(structure["weight"])/100
						best_scores_each_user.append(best_score)
print best_scores_each_user
n_bins = len(best_scores_each_user)
n, bins, patches = mlp.hist(best_scores_each_user, n_bins, normed=True, histtype="step", cumulative=True)
mlp.ylim(0,1)
mlp.ylabel("Percentile")
mlp.xlabel("Score [$]")
mlp.title("Pilot Study: Individual User Best Score CDF")
mlp.savefig("graphs/best_scores_each_user_CDF.png")
