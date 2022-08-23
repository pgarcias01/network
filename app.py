
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network


def gerar_graph(got_net):
    try:
        path = '/tmp'
        got_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = '/html_files'
        got_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page

    components.html(HtmlFile.read(), height=1000, width=1000,scrolling=True)
#st.set_page_config(layout="wide")

# Read dataset (CSV)
df = pd.read_csv('final_08_08.csv')

# Set header title
st.title('Network Graph Visualization')

# Initiate PyVis network object
df_cut = df[['name', 'cb_link','site','Industries']]
df_cut = df_cut[~df_cut['Industries'].isna()].reset_index(drop=True)
df_cut['Industries'] = df_cut['Industries'].apply(lambda x: x.split(','))
df_cut = df_cut.explode('Industries').reset_index(drop=True)
df_cut['Industries'] = df_cut['Industries'].apply(lambda x: x.strip())
df_cut['weight']=1
#df_cut = df_cut.sample(1000)
ind = dict(zip(df_cut['Industries'].value_counts().index,
df_cut['Industries'].value_counts().values))
radio = st.radio("",['Todos','Visão industria'])
if radio == 'Todos':
    with open("graph.html", "rb") as file:
         btn = st.download_button(
                 label="Download HTML",
                 data=file,
                 file_name="graph.html"
               )

else:
    selected = st.multiselect('Selecionar categoria', ind.keys())
    bt_gerar1 = st.button('Gerar')
    if bt_gerar1:
        if len(selected)==0:
            st.text('Selecione ao menos uma opção')
        else:
            df_cut = df[['name', 'cb_link','site','Industries']]
            df_cut = df_cut[~df_cut['Industries'].isna()].reset_index(drop=True)
            df_cut['Industries'] = df_cut['Industries'].apply(lambda x: x.split(','))
            df_cut['Industries'] = df_cut['Industries'].apply(lambda x: [item.strip() for item in x])
            if len(selected)==1:
                mask = df_cut['Industries'].apply(lambda x: True if selected[0] in x else False)
                df_cut = df_cut[mask.values].reset_index(drop=True)
            else:
                mask = []
                for key in selected:
                    mask.append(df_cut['Industries'].apply(lambda x: True if key in x else False).values)
                mask = pd.DataFrame(pd.DataFrame(mask).sum())
                mask[0] = mask[0].apply(lambda x: True if x>=len(selected) else False)
                df_cut = df_cut[mask[0].values].reset_index(drop=True)
            df_cut_ext = df_cut.explode('Industries').reset_index(drop=True)
            df_cut_ext['Industries'] = df_cut_ext['Industries'].apply(lambda x: x.strip())
            df_cut_ext['weight']=1
            ind = dict(zip(df_cut_ext['Industries'].value_counts().index,
            df_cut_ext['Industries'].value_counts().values))
            got_net = Network(height='1000px', width='100%', bgcolor='#222222', font_color='white')

            # set the physics layout of the network
            #got_net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09, overlap=1)
            got_net.force_atlas_2based(gravity= -1800, central_gravity=0.005, spring_length=100,spring_strength=0.005,damping=0.2,overlap=0.8)
            #got_net.hrepulsion()
            #got_net.repulsion()
            got_net.inherit_edge_colors(True)
            sources = df_cut_ext['name']
            targets = df_cut_ext['Industries']
            weights = df_cut_ext['weight']
            edge_data = zip(sources, targets, weights)

            for key in ind.keys():
                size = int(ind[key])*5 if ind[key]>6 else 30
                got_net.add_node(key, key, title=key,color='orange', size=size)

            for src in sources.unique():
                got_net.add_node(src, src, title=src,size=20)

            for e in edge_data:
                src = e[0]
                dst = e[1]
                w = e[2]
                got_net.add_edge(src, dst, value=1)

            neighbor_map = got_net.get_adj_list()

            got_net.set_edge_smooth('cubicBezier')
            got_net.inherit_edge_colors(True)
            #got_net.set_edge_smooth('continuous')
            # add neighbor data to node hover data
            #for node in got_net.nodes:
            #    node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
                #node['value'] = node['size']
            got_net.show_buttons(filter_=['physics'])
            #got_net.toggle_stabilization(False)
            #got_net.show('gameofthrones.html')
            gerar_graph(got_net)
            df_show = df_cut.copy()
            df_show['Industries'] = df_show['Industries'].apply(lambda x: ', '.join(x))
            st.dataframe(df_show[['name','site','Industries']])
