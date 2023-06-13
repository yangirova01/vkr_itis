import networkx as nx
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


# Sidebar configuration
# st.sidebar.header("Graph Configuration")
st.sidebar.subheader("Настройки графа")
width = st.sidebar.slider("Ширина", 500, 1200, 950)
height = st.sidebar.slider("Высота", 500, 1200, 700)
directed = st.sidebar.checkbox("Направленность граф", True)
physics = st.sidebar.checkbox("Динамичность", True)
# hierarchical = st.sidebar.checkbox("Иерархический", False)
load_file = st.sidebar.file_uploader("Загрузить файл", type=["csv"])
load_data_button = st.sidebar.button('Загрузить данные')
df = pd.DataFrame()

def load_data():
    global df
    df = pd.read_csv(load_file)

if load_data_button:
    load_data()
    st.sidebar.success('Данные загружены')

st.write("## Граф связей")

def build_graph(df):
    # Create an empty graph
    G = nx.Graph()

    # Add edges to the graph
    for index, row in df.iterrows():
        source = row['ФИО1']
        target = row['ФИО2']
        news_source = row['название общей группы']
        G.add_edge(source, target, news_source=news_source)

    return G

def convert_graph_to_streamlit_format(G):
    nodes = []
    edges = []

    # Calculate centrality measures
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    for node in G.nodes:
        # Add nodes to the list
        # centrality_info = f"Степень влияния: {degree_centrality[node]:.2f}\n" \
        #                   f"Взаимосвязь: {betweenness_centrality[node]:.2f}\n" \
        #                   f"Близость: {closeness_centrality[node]:.2f}\n"\
        #                   f"индекс центральности: {nx.eigenvector_centrality(G)[node]:.2f}\n"

        nodes.append(Node(id=node, label=node, size=25, shape="circularImage", image="your_image_url_here",
                          title="Граф связей"))

    for edge in G.edges:
        source, target = edge
        # Add edges to the list
        edges.append(Edge(source=source, label=G[source][target]['news_source'], target=target))

    return nodes, edges, centrality_info

if not df.empty:
    # Create the NetworkX graph
    graph = build_graph(df)

    # Convert the graph to the format compatible with streamlit-agraph
    nodes, edges, centrality_info= convert_graph_to_streamlit_format(graph)

    # st.write(centrality_info)

    config = Config(
        width=width,
        height=height,
        directed=directed,
        physics=True,
        hierarchical=False,
    )

    # Create the agraph using streamlit-agraph
    return_value = agraph(nodes=nodes, edges=edges, config=config)
else:
    st.warning('Данные не загружены. Загрузите файл CSV.')
