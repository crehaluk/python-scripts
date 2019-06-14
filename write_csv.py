#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 11:38:04 2019

@author: zhenlab
"""

import requests
from requests.auth import HTTPBasicAuth

class CatmaidApiTokenAuth(HTTPBasicAuth):
    def __init__(self, token, username=None, password=None):
        super(CatmaidApiTokenAuth, self).__init__(username, password)
        self.token = token
    def __call__(self, r):
        r.headers['X-Authorization'] = 'Token {}'.format(self.token)
        if self.username and self.password:
            super(CatmaidApiTokenAuth, self).__call__(r)
        return r




# Replace these fake values with your own.
token = '5077a5c3746ba24610f51afd1304e4357aa48af2'

project_id = 129
stack_id = 101



# Get all skeletons and their names.
assert token != '', 'Put in your token!'
annotation_response = requests.post(
    'https://catmaid.nemanode.org/' + str(project_id) + '/annotations/query-targets',
    auth=CatmaidApiTokenAuth(token)
).json()

skeleton_list = [s for s in annotation_response['entities']]

skid_to_name = {}
for skeleton in skeleton_list:
    
    if skeleton['type'] != 'neuron':
        continue
    
    skid = skeleton['skeleton_ids'][0]
    name = skeleton['name']

    skid_to_name[skid] = name
    
# Get all synapses.
connector_response = requests.post(
    'https://catmaid.nemanode.org/' + str(project_id) + '/connectors/',
    data={
        'with_partners': True,
        'relation_type': 'gapjunction_with'
    },
    auth=CatmaidApiTokenAuth(token)
).json()


synapses = {}
for connector in connector_response['connectors']:
    synapse_id, x, y, z, confidence, _, _, _, _ = connector
    synapses[synapse_id] = {'coordinates': (x, y, z)}

for synapse_id, partners in connector_response['partners'].items():
    
    if len(partners) != 2:
        print 'Warning: something is wrong with synapse', synapse_id
        continue
    
    for i, partner in enumerate(partners):
        _, _, skeleton_id, _, confidence, _, _, _ = partner
        synapses[int(synapse_id)]['neuron'+str(i+1)] = skid_to_name[skeleton_id]

from collections import defaultdict
import networkx as nx

from networkx.algorithms.operators import binary
from networkx.readwrite import gml

from load_datasets import loadCatmaid, loadDurbin



# Load_datasets.
chemical_synapses = defaultdict(nx.Graph)
gap_junctions = defaultdict(nx.Graph)
chemical_synapses, gap_junctions = loadDurbin(chemical_synapses, gap_junctions, 'data/edgelist_durbin.txt')
chemical_synapses, gap_junctions = loadCatmaid(chemical_synapses, gap_junctions, 'data/129__synapses.json', 'SEM_adult')

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


#for (pre, post) in binary.difference(SEM_adult, white_adult).edges():
#    print pre, post, SEM_adult[pre][post]['weight']
# Make links.
f1 = open("gap_junc_both.csv", "w+")
f2 = open("gap_junc_sem_only.csv", "w+")
for synapse_id in synapses:
    synapse = synapses[synapse_id]
    x, y, z = synapse['coordinates']
    link = 'https://catmaid.nemanode.org/?pid={}&zp={}&yp={}&xp={}&tool=tracingtool&sid0={}&s0=0'.format(project_id, z, y, x, stack_id)
    

    
    pre = synapse['neuron1']
    post = synapse['neuron2']
    
    if (pre, post) in binary.intersection(SEM_adult, white_adult).edges():
        print "both", pre, post, SEM_adult[pre][post]['weight'], link
        f1.write("{},{},{},{}\n".format(pre, post, SEM_adult[pre][post]['weight'], link))
    if (pre, post) in binary.difference(SEM_adult, white_adult).edges():
        print "sem_only", pre, post, SEM_adult[pre][post]['weight'], link
        f2.write("{},{},{},{}\n".format(pre, post, SEM_adult[pre][post]['weight'], link))
f1.close()
f2.close()