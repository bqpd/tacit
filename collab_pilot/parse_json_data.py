import os
import numpy
import matplotlib.pyplot as mlp
import json
import pprint
from matplotlib.pyplot import *
from truss_similarity import *
from datetime import datetime
problem_nodes = [
    {"x": "47", "y": "72", "z": "0"},
    {"x": "47", "y": "97", "z": "0"},
    {"x": "20", "y": "1.65", "z": "0"},
    {"x": "60", "y": "1.65", "z": "0"},
]
pp = pprint.PrettyPrinter(indent=2)

best_scores_each_user = []
score_vs_load_count = []
def dt_from_js_datestr(datestr):
    date, time = datestr.split(", ")
    month, day, year = map(int, date.split("/"))
    hour, minute, second = map(int, time[:-3].split(":"))
    if time[-2:] == "PM" and hour != 12:
        hour += 12
    return datetime(year, month, day, hour, minute, second)

with open('tacit-collab-export.json') as data:
	data = json.load(data)
	for pilotnum in data:
		if pilotnum != "pilot3": # don't include pilot 3 (not valid data)
			pp.pprint(pilotnum)
			first_user = True
			user1_structures = []
			user2_structures = []
			for user in data[pilotnum]:
				for problem in user:
					best_score = 10000
					if not "tutorial" in problem: # don't include tutorial
						events = user[problem]["events"]
						structures = user[problem]["structures"]
						meta = user[problem]["meta"]

						# count number of times users loaded from teammate
						user_load_count = 0
						for event_id in events:
							event = events[event_id]
							if event["type"] == "load from teammate" or event["type"] == "load from teammate current":
								user_load_count += 1

						# find best score for user
						for structure_id in structures:
							structure = structures[structure_id]
							if first_user:
								user1_structures.append(structure)
							else:
								user2_structures.append(structure)
							if not "weight" in structure:
								# ran out of time event accidentally saved
								# in structures instead of events, fixed
								continue
							elif (float(structure["weight"])/100) < best_score:
								best_score = float(structure["weight"])/100
						best_scores_each_user.append(best_score)
						score_vs_load_count.append((best_score, user_load_count))
				first_user = False
			user1_structures.sort(key=lambda x: x["timestamp"])
			user2_structures.sort(key=lambda x: x["timestamp"])
			i = 0
			j = 0
			s1 = user1_structures[i]
			s2 = user2_structures[j]	
			s1_timestamp = dt_from_js_datestr(s1["timestamp"])
			s2_timestamp = dt_from_js_datestr(s2["timestamp"])
			similarity = []
			while i < len(user1_structures) and j < len(user2_structures):
				s1 = user1_structures[i]
				s2 = user2_structures[j]
				if "type" in s1:
					i += 1
					continue
				if "type" in s2:
					j += 1
					continue
				metric = match_nodes(s1, s2, problem_nodes)
				similarity.append(metric)
				if s1_timestamp < s2_timestamp:
					i += 1
				elif s1_timestamp > s2_timestamp:
					j += 1
				else:
					i += 1
					j += 1
			# Plot similarity between structures
			mlp.clf()
			mlp.scatter(list(range(0,len(similarity))),similarity)
			graph_title = "Similarity Between Structures for " + pilotnum
			mlp.title(graph_title)
			mlp.ylim(ymin=0)
			mlp.xlim(xmin=0)
			mlp.ylabel("Similarity Metric")
			mlp.xlabel("Structure in Chronological Order")
			filename = "graphs/similarity" + pilotnum
			mlp.savefig(filename)


# Plot individual best score CDF
#print best_scores_each_user
#n_bins = len(best_scores_each_user)
#n, bins, patches = mlp.hist(best_scores_each_user, n_bins, normed=True, histtype="step", cumulative=True)
#mlp.ylim(0,1)
#mlp.ylabel("Percentile")
#mlp.xlabel("Score [$]")
#mlp.title("Pilot Study: Individual User Best Score CDF")
#mlp.savefig("graphs/best_scores_each_user_CDF.png")

# Plot score vs. number of times user loaded from teammate
#scores = [s for (s, l) in score_vs_load_count]
#loads = [l for (s, l) in score_vs_load_count]
#mlp.scatter(loads, scores)
#mlp.xlabel("Number of Times User Loaded Teammate's Structure")
#mlp.ylabel("Score [$]")
#mlp.title("Pilot Study: Score vs. Number of Times User Loaded From Teammate")
#mlp.savefig("graphs/score_vs_num_times_load")



