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
				best_structure = None
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
								best_structure = structure
						print best_score
						best_scores_each_user.append(best_score)
						score_vs_load_count.append((best_score, user_load_count))
				first_user = False

			user1_structures.sort(key=lambda x: x["timestamp"])
			user2_structures.sort(key=lambda x: x["timestamp"])
			startdate = min(dt_from_js_datestr(user1_structures[0]["timestamp"]), dt_from_js_datestr(user2_structures[0]["timestamp"]))

			# Plot of score throughout problem
			user1_scores = [s["weight"]/100 for s in user1_structures if ("weight" in s and s["weight"]/100 < 1000)]
			user1_times_less_than_max = [(dt_from_js_datestr(s["timestamp"]) - startdate).total_seconds() for s in user1_structures if "weight" in s and s["weight"] < 100000]
			user2_scores = [s["weight"]/100 for s in user2_structures if ("weight" in s and s["weight"]/100 < 1000)]
			user2_times_less_than_max = [(dt_from_js_datestr(s["timestamp"]) - startdate).total_seconds() for s in user2_structures if "weight" in s and s["weight"] < 100000]
			mlp.clf()
			mlp.scatter(user1_times_less_than_max,user1_scores, c="b", label="User 1") 
			mlp.scatter(user2_times_less_than_max,user2_scores, c="r", label="User 2") 
			score_graph_title = "Collaboration Score vs. Time" + pilotnum
			mlp.title(score_graph_title)
			mlp.xlim(xmin=0)
			mlp.ylim(ymin=300,ymax=1000)
			mlp.ylabel("Score / Cost of Structure [$]")
			mlp.yscale('log')
			mlp.xlabel("Time [seconds]")
			mlp.legend(loc="upper right")
			score_graph_filename = "graphs/score_vs_time" + pilotnum
			mlp.savefig(score_graph_filename)

			# Plot similarity between current and best structure
			similarity_with_best1 = []
			similarity_with_best2 = []
			for structure in user1_structures:
				if "weight" in structure:
					metric = match_nodes(structure, best_structure, problem_nodes)
					similarity_with_best1.append(metric)
			for structure in user2_structures:
				if "weight" in structure:
					metric = match_nodes(structure, best_structure, problem_nodes)
					similarity_with_best2.append(metric)
			mlp.clf()
			user1_times_all = [(dt_from_js_datestr(s["timestamp"]) - startdate).total_seconds() for s in user1_structures if "weight" in s]
			user2_times_all = [(dt_from_js_datestr(s["timestamp"]) - startdate).total_seconds() for s in user2_structures if "weight" in s]
			mlp.scatter(user1_times_all, similarity_with_best1, c="b", label="User 1")
			mlp.scatter(user2_times_all, similarity_with_best2, c="r", label="User 2")
			similarity_with_best_title = "Similarity with Best Structure vs Time " + pilotnum
			mlp.title(similarity_with_best_title)
			mlp.ylim(ymin=0)
			mlp.xlim(xmin=0)
			mlp.ylabel("Similarity with Best Structure")
			mlp.xlabel("Time [seconds]")
			mlp.legend(loc="upper right")
			similarity_with_best_filename = "graphs/similiarity_with_best_vs_time" + pilotnum
			mlp.savefig(similarity_with_best_filename)

			# Plot similarity between collab structures
			i = 0
			j = 0
			similarity_data = []
			while i < len(user1_structures) and j < len(user2_structures):
				s1 = user1_structures[i]
				s2 = user2_structures[j]
				s1_timestamp = dt_from_js_datestr(s1["timestamp"])
				s2_timestamp = dt_from_js_datestr(s2["timestamp"])
				if "type" in s1:
					i += 1
					continue
				if "type" in s2:
					j += 1
					continue
				metric = match_nodes(s1, s2, problem_nodes)
				if s1_timestamp < s2_timestamp:
					i += 1
					similarity_data.append((metric, (s1_timestamp - startdate).total_seconds()))
				elif s1_timestamp > s2_timestamp:
					j += 1
					similarity_data.append((metric, (s2_timestamp - startdate).total_seconds()))
				else:
					i += 1
					j += 1
					similarity_data.append((metric, (s1_timestamp - startdate).total_seconds()))
			# Plot similarity between structures
			mlp.clf()
			similarity = [s[0] for s in similarity_data]
			times = [s[1] for s in similarity_data]
			mlp.scatter(times,similarity)
			graph_title = "Similarity Between Structures for " + pilotnum
			mlp.title(graph_title)
			mlp.ylim(ymin=0)
			mlp.xlim(xmin=0)
			mlp.ylabel("Similarity Metric")
			mlp.xlabel("Time [seconds]")
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



