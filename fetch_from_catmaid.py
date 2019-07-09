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


# Make links.
# for synapse_id in synapses:
 #   synapse = synapses[synapse_id]
 #   x, y, z = synapse['coordinates']
 #   link = 'https://catmaid.nemanode.org/?pid={}&zp={}&yp={}&xp={}&tool=tracingtool&sid0={}&s0=0'.format(project_id, z, y, x, stack_id)
    
    
 #   print synapse['neuron1'], synapse['neuron2'], link
 
def get_annotation_links_single(neuron, synapses_dict):
    neuron_key = '[{0}]'.format(neuron)
    
    for synapse_id in synapses_dict:
        synapse = synapses_dict[synapse_id]
        
        if neuron == synapse['neuron1'] or neuron == synapse['neuron2'] or neuron_key == synapse['neuron1'] or neuron_key == synapse['neuron2']:
            x, y, z = synapse['coordinates']
            link = 'https://catmaid.nemanode.org/?pid={}&zp={}&yp={}&xp={}&tool=tracingtool&sid0={}&s0=0'.format(project_id, z, y, x, stack_id)
            print synapse['neuron1'], synapse['neuron2'], link

#get_annotation_links_single('PVPR', synapses)



def get_annotation_links_multi(neuron1, neuron2, synapses_dict):
    neuron_key1 = '[{0}]'.format(neuron1)
    neuron_key2 = '[{0}]'.format(neuron2)
    
    for synapse_id in synapses_dict:
        synapse = synapses_dict[synapse_id]

    
        neuron1_and_2_in_synapse = (neuron1 == synapse['neuron1'] or neuron_key1 == synapse['neuron1']) and (neuron2 == synapse['neuron2'] or neuron_key2 == synapse['neuron2'])
        neuron2_and_1_in_synapse = (neuron2 == synapse['neuron1'] or neuron_key2 == synapse['neuron1']) and (neuron1 == synapse['neuron2'] or neuron_key1 == synapse['neuron2'])    

        if neuron1_and_2_in_synapse or neuron2_and_1_in_synapse:
            x, y, z = synapse['coordinates']
            link = 'https://catmaid.nemanode.org/?pid={}&zp={}&yp={}&xp={}&tool=tracingtool&sid0={}&s0=0'.format(project_id, z, y, x, stack_id)
            print synapse['neuron1'], synapse['neuron2'], link


get_annotation_links_multi('PVPR', 'PVPL', synapses)
    
# Export to csv file for Excel.

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    