import json
from collections import defaultdict


def loadCatmaid(Gs_ch, Gs_gj, f_path, dataset):
    
    with open(f_path) as f:
        jsonedges = json.load(f)
        
    edges_done = []

    for edge in jsonedges:
        
        pre = edge['pre']
        post = edge['post']
        synapses = len(edge['syn'])

        # For adult datasets, only add the re-annotated NMJs.
        if 'white' in dataset and not post.startswith('BWM'):
            continue
        
          
        if edge['typ'] == 0:
            G = Gs_ch[dataset]
        elif edge['typ'] == 2:
            G = Gs_gj[dataset]
            if (post, pre) in edges_done:
                continue
            
        if G.has_edge(pre, post):
            G[pre][post]['weight'] += synapses
        else:
            G.add_edge(pre, post, weight=synapses)
            
        edges_done.append((pre, post))

    return (Gs_ch, Gs_gj)




# Load Durbin datasets.
# File is directly from wormatlas.
# - No duplicate connections are present.
# - PVT is replaced by DVB.
# - There are 48 connections between neurons that are inconstistent
#   when comparing Send(_joint) with Receive(_joint) and when 
#   comparing gap junctions. These connections were either missed in
#   one direction (35) or deviate by one or two synapses (13). Taking
#   the max should resolve both issues.

# Load txt file and make connections constistent with themselves.
def loadDurbin(Gs_ch, Gs_gj, path):   
    edges = defaultdict(int)
    
    with open(path) as f:
        for l in f:
            pre, post, typ, dataset, synapses = l.strip().split('\t')
            
            # Skip muscles as they were reannotated.
            if post == 'mu_bod':
                continue
            
            synapses = int(synapses)
            pre = pre.replace('DVB', 'PVT')
            post = post.replace('DVB', 'PVT')
    
            rev_type = {'Gap_junction': 'Gap_junction',
                        'Send': 'Receive',
                        'Receive': 'Send',
                        'Send_joint': 'Receive_joint',
                        'Receive_joint': 'Send_joint'}
    
            key = (dataset, typ, pre, post)
            rev_key = (dataset, rev_type[typ], post, pre)
            
            edges[key] = max(edges[key], synapses)
            edges[rev_key] = max(edges[rev_key], synapses)
            
        # AIA -> ASK was very clearly missed in JSH.
        edges[('JSH', 'Send', 'AIAL', 'ASKL')] = 1
        edges[('JSH', 'Send', 'AIAR', 'ASKR')] = 1
        # DVA -> ASK was very clearly missed in JSH.
        edges[('JSH', 'Send', 'DVA', 'AIZL')] = 1
        edges[('JSH', 'Send', 'DVA', 'AIZR')] = 1
        # ADLL -> ASHL was very clearly missed in JSH
        edges[('JSH', 'Send', 'ADLL', 'ASHL')] = 3
        # ADE -> RMG is present in the MoW drawings, but missed by Durbin.
        edges[('N2U', 'Send', 'ADEL', 'RMGL')] = 3
        edges[('N2U', 'Send', 'ADER', 'RMGR')] = 2
        
        edges_done = []
    
        for edge, synapses in edges.items():
            
            dataset, typ, pre, post = edge
            
            dataset = {'N2U': 'white_adult', 'JSH': 'white_l4'}[dataset]
            
            if typ in ('Receive', 'Receive_joint'):
                continue

            
            if typ == 'Gap_junction':
                G = Gs_gj[dataset]
                if (post, pre, dataset) in edges_done:
                    continue
            else:
                G = Gs_ch[dataset]
                
            if G.has_edge(pre, post):
                G[pre][post]['weight'] += synapses
            else:
                G.add_edge(pre, post, weight=synapses)
                
            edges_done.append((pre, post, dataset))
        
    
    return (Gs_ch, Gs_gj)