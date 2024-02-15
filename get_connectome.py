"""Get the personal connectome of neuron(s) that are inputed by the user. """

# import the necessary libraries here
import pandas as pd
#import numpy as np

def get_connectome(main_neurons, exclude_main_neurons=False, connectome_type='full', weight_threshold=1):
    """Get the personal connectome of neuron or neurons that are inputed by the user. 
    This function returns a connectome dataframe that contains the weighted connections between bodyIds. The synaptic weights 
    are collapsed across ROIs. This dataframe can be used to create a graph of the connectome in NetworkX using
    from_pandas_edgelist. However, the dataframe will need to be reformatted in order to run the clustering algorithms.
    
    main_neurons: can be a single bodyId, a list of bodyIds, or NeuronCriteria

    Options:
        - include the main neurons or not
        - input, output, or full connectome
        - weight threshold for the connection strengths to include in the connectome"""
    
    from neuprint import fetch_adjacencies
    from neuprint import NeuronCriteria as NC
    from neuprint import fetch_neurons

    # the 1st df returns all the neurons involved in making the specified connections
    pre, pre_conns = fetch_adjacencies(None, main_neurons)
    post, post_conns = fetch_adjacencies(main_neurons, None)

    # it will now be necessary for main_neurons to be a list of bodyIds
    if not (isinstance(main_neurons, int) or isinstance(main_neurons, list)):
        main_neurons_df, roi_counts_df = fetch_neurons(main_neurons)
        main_neurons = main_neurons_df['bodyId'].tolist()

    if connectome_type == 'input':

        if exclude_main_neurons:
            # remove the main neurons from the pre
            pre = pre[~pre.bodyId.isin(main_neurons)]

        # get connections among neurons using the bodyIds from pre
        partners_, connectome = fetch_adjacencies(pre['bodyId'], pre['bodyId'])

    elif connectome_type == 'output':

        if exclude_main_neurons:
            # remove the main neurons from the post
            post = post[~post.bodyId.isin(main_neurons)]

        # get connections among neurons using the bodyIds from post
        partners_, connectome = fetch_adjacencies(post['bodyId'], post['bodyId'])

    elif connectome_type == 'full':
            
        # combine unique pre and post bodyIds
        partners = pd.concat([pre['bodyId'], post['bodyId']]).unique()
        # turn it back into a series
        partners = pd.Series(partners)

        if exclude_main_neurons:
            # remove the main neurons from the partners
            partners = partners[~partners.isin(main_neurons)]

        # get connections among neurons using the bodyIds from partners
        partners_, connectome = fetch_adjacencies(partners, partners)

    # get rid of the ROI column and group bodyId_pre and bodyId_post by summing weights across ROIs
    connectome = connectome.groupby(['bodyId_pre', 'bodyId_post'], as_index=False)['weight'].sum()

    # if weight_threshold is specified, remove connections with weights less than the threshold
    if weight_threshold > 1:
        connectome = connectome[connectome['weight'] >= weight_threshold]

    return connectome

# function to combine bidirectional connections and make the connectome undirected
# this function is based on code from Rhessa's notebook. I believe that Alex's read_graph function in format_edgelight.py
# does the same thing but in a different way, so this function may be redundant.
def connectome_to_undirected(connectome):
    """Combine bidirectional connections and make the connectome undirected.
    This function takes a connectome dataframe as input and returns an undirected connectome dataframe."""
    undirected_edges = {}  # Dictionary to store the undirected edges and their weights

    for index, row in connectome.iterrows():
        source = row['bodyId_pre']
        target = row['bodyId_post']
        weight = row['weight']

        # Check if the edge already exists in the reverse
        if (target, source) in undirected_edges:
            # Update the weight of the existing edge
            undirected_edges[(target, source)] += weight
        else:
            # Add a new edge to dict
            undirected_edges[(source, target)] = weight

    # Create a DataFrame from the undirected edges dictionary
    undirected_edgelist = pd.DataFrame(list(undirected_edges.keys()), columns=['source', 'target'])
    undirected_edgelist['weight'] = list(undirected_edges.values())

    return undirected_edgelist