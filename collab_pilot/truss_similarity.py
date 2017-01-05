import operator
'''
Given two structures and a set of nodes from a problem,
create two lists of node such that nodes two nodes at the
same index are matched together.

Number of nodes in structure1 is less than or equal
to number of nodes in structure2
'''
def match_nodes(structure1, structure2, problem):
	mapping1 = []
	mapping2 = []

	# nodes from the problem must match up
	for node in problem:
		if (not node in structure1["nodeList"]) or (not node in structure2["nodeList"]):
			raise Exception("structure does not contain nodes from problem")
		mapping1.append(node)
		mapping2.append(node)
	#sort nodes by x coordinates first
	structure1["nodeList"].sort(key=operator.itemgetter("x"))
	structure2["nodeList"].sort(key=operator.itemgetter("x"))
	for node in structure1["nodeList"]:
		if not node in problem:
			mapping1.append(node)
	for node in structure2["nodeList"]:
		if not node in problem:
			mapping2.append(node)
	metric = get_node_similarity_metric(mapping1, mapping2)
	for i in range(len(mapping1)):
		for j in range(len(mapping2)):
			if i < len(problem) or j < len(problem) or i == j:
				continue
			# switch a pair of node patching
			mapping2[i], mapping2[j] = mapping2[j], mapping2[i]
			# TODO: don't have to recalculate every time, can just calculate difference
			new_metric = get_node_similarity_metric(mapping1, mapping2)
			if new_metric < metric:
				# update metric if new mapping improves it
				metric = new_metric
				continue
			else:
				# switch back if metric doesn't improve
				mapping2[i], mapping2[j] = mapping2[j], mapping2[i]
	print "node metrics: ", metric
	match_beams(mapping1, structure1, mapping2, structure2, metric)


'''
Given two list of nodes such that the nodes at the same index
are matched, return a similarity metric for beams, and a list of
beams of the two structures.

We do this by calculating length of beams needed to be added/removed
from structure1 to obtain structure2, averaged with the length of
beams needed to be added/removed from structure2 to obtain structure1.
'''
def match_beams(node_mapping1, structure1, node_mapping2, structure2, node_metric):
	beams1 = structure1["beamList"]
	beams2 = structure2["beamList"]

	# maps node indices that are connected by a beam
	beam_mapping1 = []
	beam_mapping2 = []
	for beam in beams1:
		# get node indices from structure1
		i = node_mapping1.index({"x": beam["start_x"], "y": beam["start_y"], "z": beam["start_z"]})
		j = node_mapping1.index({"x": beam["end_x"], "y": beam["end_y"], "z": beam["end_z"]})
		beam_mapping1.append((i,j))

	for beam in beams2:
		# get node indices from structure1
		i = node_mapping2.index({"x": beam["start_x"], "y": beam["start_y"], "z": beam["start_z"]})
		j = node_mapping2.index({"x": beam["end_x"], "y": beam["end_y"], "z": beam["end_z"]})
		beam_mapping2.append((i,j))

	beam_metric = 0
	num_nodes = len(node_mapping1)
	for i in range(num_nodes-1):
		for j in range(i+1, num_nodes):
			mapping1_has_beam = ((i, j) in beam_mapping1) or ((j, i) in beam_mapping1) 
			mapping2_has_beam = ((i, j) in beam_mapping2) or ((j, i) in beam_mapping2) 
			if (mapping1_has_beam and not mapping2_has_beam) or (mapping2_has_beam and not mapping1_has_beam):
				beam1 = get_euclidean_distance(node_mapping1[i], node_mapping1[j])
				#beam2 = get_euclidean_distance(node_mapping2[i], node_mapping2[j])
				#beam_metric += ((beam1 + beam2)/2)
				beam_metric += beam1
	print "beams metric: ", beam_metric
	unmatched_nodes_beams(node_mapping1, beam_mapping1, beams1, structure1, node_mapping2, beam_mapping2, beams2, structure2, beam_metric + node_metric)

'''
Take into account nodes and beams that were not mapped.

If node splits an original beam, don't increase metric -- TODO: fix it
If beams add up to original beams, remove them from metric calculation.
For each unmapped node:
	- if connected by one unmapped beam, add beam to metric
	- if more than one beam, check each pair of beams
		- if pair of beams is replacing a corresponding beam, add difference to metric
		- if pair of beams is not replacing a corresponding beam, add both beams to metric
	- each beam is added at most once, replacement takes priority
	- define replace as if two nodes connected to extra node are connected in structure1
	  and not connected in structure2.
'''
def unmatched_nodes_beams(node_mapping1, beam_mapping1, beams1, structure1, node_mapping2, beam_mapping2, beams2, structure2, metric):
	unmapped_nodes = []
	unmatched_metric = 0
	# no unmatched nodes
	if len(node_mapping1) == len(node_mapping2):
		print "no additional nodes, final metric: ", metric
		return metric
	# look at each unmapped nodes
	first_unmapped = len(node_mapping1)
	for i in range(first_unmapped, len(node_mapping2)):
		unmapped_node = node_mapping2[i]
		unmapped_nodes.append(node_mapping2[i])
	# array containing all unmapped beams
	non_replacement_beams = []
	replacement_beams = []
	# make a 2D array of lists of unmapped beam for each unmapped node
	unmapped_beams = [[] for i in range(len(unmapped_nodes))]
	for i in range(len(unmapped_nodes)):
		node = unmapped_nodes[i]
		for beam in beams2:
			if (beam["start_x"] == node["x"]) and (beam["start_y"] == node["y"]):
				non_replacement_beams.append(beam)
				unmapped_beams[i].append(beam)
			if (beam["end_x"] == node["x"]) and (beam["end_y"] == node["y"]):
				non_replacement_beams.append(beam)
				unmapped_beams[i].append(beam)
	# remove beams that replaces a beam in structure 1
	for beam_set in unmapped_beams:
		if len(beam_set) > 1:
			for i in range(len(beam_set)-1):
				for j in range(i+1, len(beam_set)):
					b1 = beam_set[i]
					b2 = beam_set[j]
					midpoint, beam = is_replacement(b1, b2, structure1, structure2)
					if beam != None:
						if b1 in non_replacement_beams:
							non_replacement_beams.remove(b1)
							replacement_beams.append(b1)
						if b2 in non_replacement_beams:
							non_replacement_beams.remove(b2)
							replacement_beams.append(b2)
						n1 = {"x": beam["start_x"], "y": beam["start_y"], "z": beam["start_z"]}
						n2 = {"x": beam["end_x"], "y": beam["end_y"], "z": beam["end_z"]}
						difference = get_difference(midpoint, n1, n2)
						unmatched_metric += difference
						unmatched_metric -= get_beam_length(beam)
		else:
			continue

	# add up beams to metric
	for beam in non_replacement_beams:
		unmatched_metric += get_beam_length(beam)
	print "FINAL METRIC: " , unmatched_metric + metric
	return unmatched_metric + metric

###################
# Helper Methods  #
###################
'''
Given a beam, return length of the beam.
'''
def get_beam_length(beam):
	start = {"x": beam["start_x"], "y": beam["start_y"], "z": beam["start_z"]}
	end = {"x": beam["end_x"], "y": beam["end_y"], "z": beam["end_z"]}
	return get_euclidean_distance(start, end)

'''
Given two nodes, calculates the Euclidean distance
between them.
'''
def get_euclidean_distance(node1, node2):
	distance = (node1["x"] - node2["x"])**2 + (node1["y"] - node2["y"])**2 + (node1["z"] - node2["z"])**2
	return distance**0.5

'''
Given lists of nodes ordered by mapping, return the sum of the 
Euclidean distance between each pair of nodes.
'''
def get_node_similarity_metric(mapping1, mapping2):
	if len(mapping2) < len(mapping1):
		temp = mapping1 
		mapping1 = mapping2 
		mapping2 = temp
	metric = 0
	for i in range(len(mapping1)):
		node1 = mapping1[i]
		node2 = mapping2[i]
		metric += get_euclidean_distance(node1, node2)
	return metric

'''
Given a node and a list of beams, returns the beam it splits if 
it splits a beam, otherwise return None.
'''
def splits_beam(node, beams):
	intersecting_beams = []
	for beam in beams:
		dx_node = node["x"] - beam["start_x"]
		dy_node = node["y"] - beam["start_y"]

		dx_beam = beam["end_x"] - beam["start_x"]
		dy_beam = beam["end_y"] - beam["start_y"]

		cross_product = dx_node * dy_beam - dx_beam * dy_node
		if abs(cross_product) <= 2e-13: # take into account errors from floats
			# don't count node as splitting beam if it's start/end node of beam
			if (node["x"] == beam["start_x"]) and (node["y"] == beam["start_y"]):
				continue
			if (node["x"] == beam["end_x"]) and (node["y"] == beam["end_y"]):
				continue
			intersecting_beams.append(beam)
	return intersecting_beams

'''
Given two beams and a third beam, return whether the two beams makes up
the third beam.
'''
def is_beam_component(beam1, beam2, beams):
	beam1_start = {"x": beam1["start_x"], "y": beam1["start_y"], "z": beam1["start_z"]}
	beam1_end = {"x": beam1["end_x"], "y": beam1["end_y"], "z": beam1["end_z"]}
	beam2_start = {"x": beam2["start_x"], "y": beam2["start_y"], "z": beam2["start_z"]}
	beam2_end = {"x": beam2["end_x"], "y": beam2["end_y"], "z": beam2["end_z"]}
	beam_start = {"x": beam["start_x"], "y": beam["start_y"], "z": beam["start_z"]}
	beam_end = {"x": beam["end_x"], "y": beam["end_y"], "z": beam["end_z"]}

	if beam1_start == beam2_start:
		if (beam1_end == beam_start and beam2_end == beam_end) or (beam1_end == beam_end and beam2_end == beam_start):
			return True
	if beam1_start == beam2_end:
		if (beam1_end == beam_start and beam2_start == beam_end) or (beam1_end == beam_end and beam2_start == beam_start):
			return True
	if beam1_end == beam2_start:
		if (beam1_start == beam_start and beam2_end == beam_end) or (beam1_start == beam_end and beam2_end == beam_start):
			return True
	if beam1_end == beam2_end:
		if (beam1_start == beam_start and beam2_start == beam_end) or (beam1_start == beam_end and beam2_start == beam_start):
			return True
	return False
'''
Given a three nodes, return the height of the triangle with the three nodes as
vertices, and first node as apex of the triangle.
'''
def get_difference(node1, node2, node3):
	area = abs(node1["x"]*(node2["y"]-node3["y"]) + node2["x"]*(node3["y"]-node1["y"]) + node3["x"]*(node1["y"]-node2["y"]))/2
	base = get_euclidean_distance(node2, node3)
	height = 2 * area / base
	return height

'''
Given two beams and a structure, return the beam in the structure that is replaced if
the two beams replaces a beam in the structure, or None otherwise, and the node where the two
beam components join.
"Replace" defined as if two nodes connected to the extra ndoe is connected in structure 1 and
not connected in structure 2.
'''
def is_replacement(beam1, beam2, structure1, structure2):
	beam1_start = {"x": beam1["start_x"], "y": beam1["start_y"], "z": beam1["start_z"]}
	beam1_end = {"x": beam1["end_x"], "y": beam1["end_y"], "z": beam1["end_z"]}
	beam2_start = {"x": beam2["start_x"], "y": beam2["start_y"], "z": beam2["start_z"]}
	beam2_end = {"x": beam2["end_x"], "y": beam2["end_y"], "z": beam2["end_z"]}

	node1 = None
	node2 = None
	midpoint = None

	if beam1_start == beam2_start:
		node1 = beam1_end
		node2 = beam2_end
		midpoint = beam1_start
	elif beam1_start == beam2_end:
		node1 = beam1_end
		node2 = beam2_start
		midpoint = beam1_start
	elif beam1_end == beam2_start:
		node1 = beam1_start
		node2 = beam2_end
		midpoint = beam1_end
	elif beam1_end == beam2_end:
		node1 = beam1_start
		node2 = beam2_start
		midpoint = beam1_end
	else:
		raise Exception("beams from same beam_set should share a node")
	if (is_connected(node1, node2, structure1) != None) and not (is_connected(node1, node2, structure2) != None):
		return (midpoint, is_connected(node1, node2, structure1))
	else:
		return (midpoint, None)
'''
Given two nodes and a structure, return whether the the beam that connects
the two nodes if the two nodes are connected, return None otherwise.
'''
def is_connected(node1, node2, structure):
	beam1 = {"start_x": node1["x"], "start_y": node1["y"], "start_z": node1["z"], "end_x": node2["x"], "end_y": node2["y"], "end_z": node2["z"]}
	beam2 = {"start_x": node2["x"], "start_y": node2["y"], "start_z": node2["z"], "end_x": node1["x"], "end_y": node1["y"], "end_z": node1["z"]}
	if beam1 in structure["beamList"]:
		return beam1
	elif beam2 in structure["beamList"]:
		return beam2
	else:
		return None

def test_splits_beam():
	node = {"x": 10, "y": 20}
	beamList = [
		# false - end node
		{"start_x": 10, "start_y": 20, "start_z": 0, "end_x": 20, "end_y": 20, "end_z": 0},
		# false - not in beam
		{"start_x": 30, "start_y": 20, "start_z": 0, "end_x": 20, "end_y": 40, "end_z": 0},
		# true - in beam
		{"start_x": 0, "start_y": 10, "start_z": 0, "end_x": 20, "end_y": 30, "end_z": 0},
	]
	print splits_beam(node, beamList)

#test_splits_beam()

def test_match_nodes():
	# test 1: two structures with identical nodes
	struct1 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 10, "y": 80, "z": 0},
			{"x": 30, "y": 40, "z": 0},
		],
		"beamList": [
			{"start_x": 10, "start_y": 80, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 10, "start_y": 80, "start_z": 0, "end_x": 42, "end_y": 97, "end_z": 0},
			{"start_x": 10, "start_y": 80, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 30, "start_y": 40, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 30, "start_y": 40, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 30, "start_y": 40, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 60, "start_y": 1.65, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
		]
	}
	struct2 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 70, "y": 82, "z": 0},
			{"x": 12, "y": 81, "z": 0},
		],
		"beamList": [
			{"start_x": 12, "start_y": 81, "start_z": 0, "end_x": 42, "end_y": 97, "end_z": 0},
			{"start_x": 12, "start_y": 81, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 12, "start_y": 81, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 70, "end_y": 82, "end_z": 0},
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 70, "end_y": 82, "end_z": 0},
			{"start_x": 60, "start_y": 1.65, "start_z": 0, "end_x": 70, "end_y": 82, "end_z": 0},
			{"start_x": 20, "start_y": 1.65, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
		]
	}
	struct3 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 35, "y": 19, "z": 0},
			{"x": 15, "y": 30, "z": 0},
			{"x": 10, "y": 65, "z": 0},
		],
		"beamList": [
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 35, "start_y": 19, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 35, "start_y": 19, "start_z": 0, "end_x": 42, "end_y": 97, "end_z": 0},
			{"start_x": 10, "start_y": 65, "start_z": 0, "end_x": 35, "end_y": 19, "end_z": 0},
			{"start_x": 15, "start_y": 30, "start_z": 0, "end_x": 35, "end_y": 19, "end_z": 0},
			{"start_x": 15, "start_y": 30, "start_z": 0, "end_x": 10, "end_y": 65, "end_z": 0},
			{"start_x": 15, "start_y": 30, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 20, "start_y": 1.65, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 60, "start_y": 1.65, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
		]
	}
	# Nodes from Road Sign problem
	problem_nodes = [
		{"x": 42, "y": 72, "z": 0},
		{"x": 42, "y": 97, "z": 0},
		{"x": 20, "y": 1.65, "z": 0},
		{"x": 60, "y": 1.65, "z": 0}
	]
	match_nodes(struct1, struct2, problem_nodes)
	match_nodes(struct1, struct3, problem_nodes)
	match_nodes(struct2, struct3, problem_nodes)


#test_match_nodes()

def test_unmatch():
	#original
	struct1 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 55, "y": 80, "z": 0},
		],
		"beamList": [
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 60, "start_y": 1.65, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
		]
	}
	struct2 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 55, "y": 80, "z": 0},
			{"x": 57.5, "y": 40.825, "z": 0},
		],
		"beamList": [
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 57.5, "start_y": 40.825, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 57.5, "start_y": 40.825, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
		]
	}
	struct3 = {
		"nodeList" : [
			{"x": 42, "y": 72, "z": 0},
			{"x": 42, "y": 97, "z": 0},
			{"x": 20, "y": 1.65, "z": 0},
			{"x": 60, "y": 1.65, "z": 0},
			{"x": 55, "y": 80, "z": 0},
			{"x": 57.5, "y": 40.825, "z": 0},
		],
		"beamList": [
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 20, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 42, "start_y": 97, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 42, "start_y": 72, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 57.5, "start_y": 40.825, "start_z": 0, "end_x": 55, "end_y": 80, "end_z": 0},
			{"start_x": 57.5, "start_y": 40.825, "start_z": 0, "end_x": 60, "end_y": 1.65, "end_z": 0},
			{"start_x": 57.5, "start_y": 40.825, "start_z": 0, "end_x": 42, "end_y": 72, "end_z": 0},
		]
	}
	problem_nodes = [
		{"x": 42, "y": 72, "z": 0},
		{"x": 42, "y": 97, "z": 0},
		{"x": 20, "y": 1.65, "z": 0},
		{"x": 60, "y": 1.65, "z": 0}
	]
	print "Structure 1 and 2:"
	match_nodes(struct1, struct2, problem_nodes)
	print "---------------------"
	print "Structure 2 and 3:"
	match_nodes(struct2, struct3, problem_nodes)
	print "---------------------"
	print "Structure 1 and 3:"
	match_nodes(struct1, struct3, problem_nodes)
	
test_unmatch()
