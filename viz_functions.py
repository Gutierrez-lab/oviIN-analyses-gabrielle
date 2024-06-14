"""Functions for doing visualizations."""
# SANKEYS
import plotly.graph_objects as go
import pandas as pd
from neuprint import Client

def create_Sankey_fig(df0, title_str):
    # make a copy of the dataframe since we will be modifying it in the function
    df = df0.copy()

    # get the columns of the dataframe
    res = df.columns

    # add a column of ones to ovi_HB_chunk
    df['counts'] = 1

    # these are for the nodes and links that will be used in the sankey diagram
    nodes = []
    links = pd.DataFrame()

    # append _r0.0 to values in column '0.0' and so on
    for col in res:
        
        # rename columns after doing the above
        df[col] = df[col].astype(str) + '_r' + col

        # create a list of nodes from all the columns
        # do this after renaming the columns
        nodes = nodes + df[col].unique().tolist()

    for i in range(len(res)-1):
        # create the Sankey levels
        #df2 = df.groupby([columns[i],columns[i+1]])['counts'].count().reset_index()
        df2 = df[[res[i],res[i+1],'counts']].groupby([res[i],res[i+1]]).count().reset_index()
        df2.columns = ['source','target','value']
        links = pd.concat([links, df2], axis=0)
        
    # this is basically a mapping dictionary of nodes enumerated
    mapping_dict = {k: v for v, k in enumerate(nodes)}

    # replace source and target with enumerated values
    links['source'] = links['source'].map(mapping_dict)
    links['target'] = links['target'].map(mapping_dict)

    # turn this table into a dictionary for making the sankey diagram
    links_dict = links.to_dict(orient='list')

    # plot it
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness=20,
            #line=dict(color='blue', width=0.5),
            label = nodes,
            #color='green'
        ),
        link = dict(
        source= links_dict['source'],
        target = links_dict['target'],
        value = links_dict['value']
        )
    )
    ])
    fig.update_layout(title=title_str, height=1000)
    fig.show()



# # SKELETONS
# def get_skeleton(bodyID, color='grey'):
#     """Download a skeleton from Neuprint and return it as a DataFrame. This is based on the Neuprint tutorial for doing the same. We include the option to specify a color for the skeleton."""
#     # Add some checks and/or error messages if there is no Neuprint client, etc.

#     # Download some skeletons as DataFrames and attach columns for bodyId and color
#     skeletons = []

#     # could add more skeletons with a for loop
#     s = c.fetch_skeleton(bodyID, format='pandas')
#     s['bodyId'] = bodyID
#     s['color'] = color
#     skeletons.append(s)

#     # Combine into one big table for convenient processing
#     skeletons = pd.concat(skeletons, ignore_index=True)

#     # Join parent/child nodes for plotting as line segments below.
#     # (Using each row's 'link' (parent) ID, find the row with matching rowId.)
#     skel_segments = skeletons.merge(skeletons, 'inner',
#                             left_on=['bodyId', 'link'],
#                             right_on=['bodyId', 'rowId'],
#                             suffixes=['_child', '_parent'])
#     return skel_segments