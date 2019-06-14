# -*- coding: ascii -*-
from collections import defaultdict
import networkx as nx

from networkx.algorithms.operators import binary
from networkx.readwrite import gml

from load_datasets import loadCatmaid, loadDurbin



# Load_datasets.
chemical_synapses = defaultdict(nx.Graph)
gap_junctions = defaultdict(nx.Graph)
chemical_synapses, gap_junctions = loadDurbin(chemical_synapses, gap_junctions, 'data/edgelist_durbin.txt')
chemical_synapses, gap_junctions = loadCatmaid(chemical_synapses, gap_junctions, '/home/zhenlab/Dropbox/_Connectomics_paper/Data/raw_catmaid_export/SEM_ad__synapses_roi.json', 'SEM_adult')

SEM_adult = gap_junctions['SEM_adult']
white_adult = gap_junctions['white_adult']
white_l4 = gap_junctions['white_l4']


# Make all datasets compatible.
for node in SEM_adult.nodes():
    if 'fragment' in node or node == 'unknown1' or node.startswith('BWM'):
        SEM_adult.remove_node(node)
        
for node in white_adult.nodes():
    if 'DB1' in node or node == 'VA2' or node == 'GLRVR' or node == 'VB1' or node == 'GLRR' or node == 'GLRVL' or node == 'GLRL' or node == 'GLRDL' or node == 'GLRDR':
        white_adult.remove_node(node)      

SEM_adult.add_nodes_from(white_adult.nodes())
white_adult.add_nodes_from(SEM_adult.nodes())


# Compare datasets.
print 'Edges in both datasets:', binary.intersection(SEM_adult, white_adult).number_of_edges()
print 'Edges not annotated by John White:', binary.difference(SEM_adult, white_adult).number_of_edges()
print 'Edges only annotated by John White:', binary.difference(white_adult, SEM_adult).number_of_edges()


for (pre, post) in binary.difference(SEM_adult, white_adult).edges():
    print pre, post, SEM_adult[pre][post]['weight']


# Export for Cytoscape.
gml.write_gml(SEM_adult, 'data/SEM_adult.gml')
combined_graph = binary.compose(SEM_adult, white_adult)
specific_to_SEM_adult = binary.difference(SEM_adult, white_adult)
specific_to_white_adult = binary.difference(white_adult, SEM_adult)
for (pre, post) in combined_graph.edges():
    if specific_to_SEM_adult.has_edge(pre, post):
        combined_graph[pre][post]['dataset'] = 'only_SEM_adult'
    elif specific_to_white_adult.has_edge(pre, post):
        combined_graph[pre][post]['dataset'] = 'only_white_adult'
    else:
        combined_graph[pre][post]['dataset'] = 'shared'
gml.write_gml(combined_graph, 'data/combined_graph.gml')


