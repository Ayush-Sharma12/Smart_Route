import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set page configuration
st.set_page_config(
    page_title="Route Optimizer & Dijkstra's Visualization",
    page_icon="🗺",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .title {
        color: #2e4053;
        text-align: center;
        padding: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2e4053;
        color: white;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .main-header {
        color: #2e4053;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #333;
        padding: 0.5rem 0;
        border-bottom: 2px solid #2e4053;
        margin: 1.5rem 0;
    }
    .algorithm-step {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: white;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .step-number {
        background: #2e4053;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
    }
    .side-info {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #2e4053;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize the graph for NetworkX visualization
if 'graph' not in st.session_state:
    st.session_state.graph = nx.Graph()
if 'positions' not in st.session_state:
    st.session_state.positions = {}
if 'saved_graphs' not in st.session_state:
    st.session_state.saved_graphs = {}

# Function to implement Dijkstra's algorithm
def dijkstra(graph, start, end):
    distances = {node: float('infinity') for node in graph}
    previous_nodes = {node: None for node in graph}
    distances[start] = 0
    nodes = list(graph)

    while nodes:
        current_node = min(nodes, key=lambda node: distances[node])
        nodes.remove(current_node)

        if distances[current_node] == float('infinity'):
            break

        for neighbor, weight in graph[current_node].items():
            alternative_route = distances[current_node] + weight
            if alternative_route < distances[neighbor]:
                distances[neighbor] = alternative_route
                previous_nodes[neighbor] = current_node

    path, current_node = [], end
    total_distance = distances[end]
    while previous_nodes[current_node] is not None:
        path.insert(0, current_node)
        current_node = previous_nodes[current_node]
    if path:
        path.insert(0, current_node)
    return path, total_distance

# Function to draw the graph using NetworkX
def draw_graph(path=None):
    plt.figure(figsize=(10, 8))
    pos = st.session_state.positions
    nx.draw(st.session_state.graph, pos, with_labels=True, 
            node_size=700, 
            node_color='lightblue',
            font_size=10,
            font_weight='bold')

    edge_labels = nx.get_edge_attributes(st.session_state.graph, 'weight')
    nx.draw_networkx_edge_labels(st.session_state.graph, pos, edge_labels=edge_labels)

    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(st.session_state.graph, pos, edgelist=path_edges, 
                             edge_color='orange', width=2)
        if len(path_edges) > 0:
            nx.draw_networkx_edges(st.session_state.graph, pos, 
                                 edgelist=[path_edges[-1]], 
                                 edge_color='red', width=3)

    plt.xlim(-1, 11)
    plt.ylim(-1, 11)
    plt.grid(True, linestyle='--', alpha=0.7)
    border = patches.Rectangle((-1, -1), 12, 12, linewidth=2, 
                             edgecolor='black', facecolor='none')
    plt.gca().add_patch(border)
    st.pyplot(plt)
    plt.close()

# Function to save the current graph
def save_graph(graph_name):
    graph_data = {
        'nodes': list(st.session_state.graph.nodes),
        'edges': [(u, v, d['weight']) for u, v, d in st.session_state.graph.edges(data=True)],
        'positions': {node: st.session_state.positions[node] for node in st.session_state.graph.nodes}
    }
    st.session_state.saved_graphs[graph_name] = graph_data
    st.success(f"✅ Graph '{graph_name}' saved successfully!")

# Function to load a saved graph
def load_graph(graph_name):
    if graph_name in st.session_state.saved_graphs:
        graph_data = st.session_state.saved_graphs[graph_name]
        st.session_state.graph.clear()
        st.session_state.positions.clear()
        
        for node in graph_data['nodes']:
            st.session_state.graph.add_node(node)
            st.session_state.positions[node] = graph_data['positions'].get(node, (0, 0))
        
        for u, v, weight in graph_data['edges']:
            st.session_state.graph.add_edge(u, v, weight=weight)
        
        st.success(f"✅ Graph '{graph_name}' loaded successfully!")
    else:
        st.error(f"❌ Graph '{graph_name}' does not exist.")

# Streamlit app
def main():
    # Create tabs
    tabs = st.tabs(["🗺 SmartPath India", "📈 Dijkstra's Visualization", "ℹ️ About"])

    with tabs[0]:
        # Header
        st.markdown("<h1 class='title'>🗺 Indian Cities Route Optimizer</h1>", unsafe_allow_html=True)
        
        # Information about the application
        with st.expander("❗ How to use:"):
            st.markdown("""
            
            1. Select your starting city
            2. Select your destination city
            3. Click 'Find Shortest Path' to see the optimal route
            """)

        # Predefined graph with coordinates and distances (in approximate hours of travel time)
        graph = {
            'Mumbai': {'Pune': 3, 'Nashik': 4, 'Ahmedabad': 8, 'Surat': 5},
            'Pune': {'Mumbai': 3, 'Nashik': 4, 'Bangalore': 12, 'Hyderabad': 9},
            'Nashik': {'Mumbai': 4, 'Pune': 4, 'Ahmedabad': 7, 'Indore': 5},
            'Ahmedabad': {'Mumbai': 8, 'Nashik': 7, 'Delhi': 12, 'Surat': 6},
            'Delhi': {'Ahmedabad': 12, 'Jaipur': 4, 'Lucknow': 7, 'Chandigarh': 5},
            'Bangalore': {'Pune': 12, 'Chennai': 6, 'Hyderabad': 8, 'Mysore': 3},
            'Chennai': {'Bangalore': 6, 'Hyderabad': 8, 'Visakhapatnam': 12},
            'Hyderabad': {'Bangalore': 8, 'Chennai': 8, 'Nagpur': 10, 'Pune': 9},
            'Jaipur': {'Delhi': 4, 'Ahmedabad': 8, 'Agra': 4},
            'Lucknow': {'Delhi': 7, 'Nagpur': 12, 'Patna': 6},
            'Nagpur': {'Hyderabad': 10, 'Lucknow': 12, 'Bhopal': 5},
            'Kolkata': {'Bhubaneswar': 6, 'Patna': 8, 'Ranchi': 7},
            'Bhubaneswar': {'Kolkata': 6, 'Visakhapatnam': 7},
            'Visakhapatnam': {'Bhubaneswar': 7, 'Hyderabad': 9, 'Chennai': 12},
            'Patna': {'Kolkata': 8, 'Lucknow': 10, 'Ranchi': 4},
            'Surat': {'Mumbai': 5, 'Ahmedabad': 6},
            'Indore': {'Bhopal': 3, 'Ahmedabad': 7, 'Nashik': 5},
            'Bhopal': {'Indore': 3, 'Nagpur': 5, 'Gwalior': 6},
            'Chandigarh': {'Delhi': 5, 'Amritsar': 4},
            'Mysore': {'Bangalore': 3, 'Coimbatore': 6},
            'Agra': {'Jaipur': 4, 'Delhi': 3},
            'Ranchi': {'Kolkata': 7, 'Patna': 4},
            'Amritsar': {'Chandigarh': 4, 'Jammu': 6},
            'Coimbatore': {'Mysore': 6, 'Chennai': 8},
            'Gwalior': {'Bhopal': 6, 'Agra': 3},
            'Jammu': {'Amritsar': 6},
            # Additional cities
            'Kanpur': {'Lucknow': 2, 'Delhi': 8},
            'Vadodara': {'Ahmedabad': 2, 'Surat': 4},
            'Ludhiana': {'Chandigarh': 3, 'Amritsar': 3},
            'Madurai': {'Chennai': 8, 'Coimbatore': 4},
            'Varanasi': {'Lucknow': 4, 'Patna': 3},
            'Meerut': {'Delhi': 2, 'Agra': 4},
            'Rajkot': {'Ahmedabad': 4, 'Surat': 5},
            'Jodhpur': {'Jaipur': 5, 'Ahmedabad': 9},
            'Raipur': {'Nagpur': 5, 'Bhubaneswar': 8},
            'Kochi': {'Coimbatore': 5, 'Bangalore': 10},
            'Guwahati': {'Kolkata': 10, 'Shillong': 3},
            'Shillong': {'Guwahati': 3},
            'Thiruvananthapuram': {'Kochi': 4, 'Madurai': 6}
        }

        coordinates = {
            'Mumbai': (19.0760, 72.8777),
            'Pune': (18.5204, 73.8567),
            'Nashik': (20.0059, 73.7897),
            'Ahmedabad': (23.0225, 72.5714),
            'Delhi': (28.6139, 77.2090),
            'Bangalore': (12.9716, 77.5946),
            'Chennai': (13.0827, 80.2707),
            'Hyderabad': (17.3850, 78.4867),
            'Jaipur': (26.9124, 75.7873),
            'Lucknow': (26.8467, 80.9462),
            'Nagpur': (21.1458, 79.0882),
            'Kolkata': (22.5726, 88.3639),
            'Bhubaneswar': (20.2961, 85.8245),
            'Visakhapatnam': (17.6868, 83.2185),
            'Patna': (25.5941, 85.1376),
            'Surat': (21.1702, 72.8311),
            'Indore': (22.7196, 75.8577),
            'Bhopal': (23.2599, 77.4126),
            'Chandigarh': (30.7333, 76.7794),
            'Mysore': (12.2958, 76.6394),
            'Agra': (27.1767, 78.0081),
            'Ranchi': (23.3441, 85.3096),
            'Amritsar': (31.6340, 74.8723),
            'Coimbatore': (11.0168, 76.9558),
            'Gwalior': (26.2183, 78.1828),
            'Jammu': (32.7266, 74.8570),
            # Additional cities
            'Kanpur': (26.4499, 80.3319),
            'Vadodara': (22.3072, 73.1812),
            'Ludhiana': (30.9010, 75.8573),
            'Madurai': (9.9252, 78.1198),
            'Varanasi': (25.3176, 82.9739),
            'Meerut': (28.9845, 77.7064),
            'Rajkot': (22.3039, 70.8022),
            'Jodhpur': (26.2389, 73.0243),
            'Raipur': (21.2514, 81.6296),
            'Kochi': (9.9312, 76.2673),
            'Guwahati': (26.1445, 91.7362),
            'Shillong': (25.5788, 91.8933),
            'Thiruvananthapuram': (8.5241, 76.9366)
        }

        # Create two columns for input
        col1, col2 = st.columns(2)

        with col1:
            start_node = st.selectbox("🚩 Select starting city:", list(graph.keys()))
            
        with col2:
            end_node = st.selectbox("🏁 Select destination city:", list(graph.keys()))

        if st.button("🔍 Find Shortest Path"):
            path, total_distance = dijkstra(graph, start_node, end_node)
            
            if path:
                # Success message with path and estimated time
                st.success(f"📍 Optimal Route: {' → '.join(path)}")
                st.info(f"⏱ Estimated travel time: {total_distance} hours")

                # Create a map
                center_lat = sum(coord[0] for coord in coordinates.values()) / len(coordinates)
                center_lng = sum(coord[1] for coord in coordinates.values()) / len(coordinates)
                m = folium.Map(location=[center_lat, center_lng], zoom_start=5, control_scale=True)

                # Add cities to the map
                for node, coord in coordinates.items():
                    color = 'red' if node in [start_node, end_node] else 'blue'
                    icon = 'flag' if node in [start_node, end_node] else 'info-sign'
                    folium.Marker(
                        coord,
                        popup=node,
                        icon=folium.Icon(color=color, icon=icon),
                        tooltip=node
                    ).add_to(m)

                # Add all routes to the map
                for node, neighbors in graph.items():
                    for neighbor in neighbors:
                        folium.PolyLine(
                            locations=[coordinates[node], coordinates[neighbor]],
                            color="gray",
                            weight=2,
                            opacity=0.5,
                            tooltip=f"{node} to {neighbor}"
                        ).add_to(m)

                # Highlight the optimal path
                path_coords = [coordinates[node] for node in path]
                folium.PolyLine(
                    locations=path_coords,
                    color="red",
                    weight=4,
                    opacity=0.8,
                    tooltip="Optimal Route"
                ).add_to(m)

                # Display the map
                st_folium(m, width=1200, height=600, returned_objects=[])

                # Display additional information
                st.markdown("### 📊 Route Details")
                route_details = []
                for i in range(len(path)-1):
                    route_details.append({
                        'From': path[i],
                        'To': path[i+1],
                        'Time (hours)': graph[path[i]][path[i+1]]
                    })
                
                if route_details:
                    st.table(pd.DataFrame(route_details))
            else:
                st.error("No path found between selected cities")

        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center'>
                <p>Created with ❤ using Streamlit and Python 🐍</p>
                
            </div>
        """, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<h1 class="main-header">Dijkstra\'s Algorithm Visualization</h1>', 
                    unsafe_allow_html=True)

        # Create three-column layout
        left_col, main_col, right_col = st.columns([1, 2, 1])

        with left_col:
            st.markdown("""
            <div class="side-info">
                <h4>Algorithm Steps</h4>
                <div class="algorithm-step">
                    <div class="step-number">1</div>
                    <div>Initialize distances</div>
                </div>
                <div class="algorithm-step">
                    <div class="step-number">2</div>
                    <div>Select minimum</div>
                </div>
                <div class="algorithm-step">
                    <div class="step-number">3</div>
                    <div>Update neighbors</div>
                </div>
                <div class="algorithm-step">
                    <div class="step-number">4</div>
                    <div>Repeat until done</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with main_col:
            # Node creation section
            st.markdown('<h3 class="section-header">Add Node</h3>', 
                       unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                x_coord = st.number_input("X Coordinate", min_value=0, max_value=10, value=0)
            with col2:
                y_coord = st.number_input("Y Coordinate", min_value=0, max_value=10, value=0)
            
            if st.button("➕ Add Node"):
                new_node = f"Node {len(st.session_state.graph.nodes) + 1}"
                st.session_state.graph.add_node(new_node)
                st.session_state.positions[new_node] = (x_coord, y_coord)
                st.success(f"✅ {new_node} added at ({x_coord}, {y_coord})")

            # Edge creation section
            st.markdown('<h3 class="section-header">Create Edge</h3>', 
                       unsafe_allow_html=True)
            if len(st.session_state.graph.nodes) >= 2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    node1 = st.selectbox("From Node", list(st.session_state.graph.nodes))
                with col2:
                    node2 = st.selectbox("To Node", 
                                       [n for n in st.session_state.graph.nodes if n != node1])
                with col3:
                    edge_cost = st.number_input("Cost", min_value=1, value=1)
                
                if st.button("🔗 Add Edge"):
                    st.session_state.graph.add_edge(node1, node2, weight=edge_cost)
                    st.success(f"✅ Edge added: {node1} ↔ {node2} (cost: {edge_cost})")
            else:
                st.info("ℹ️ Add at least two nodes to create edges.")

            # Path finding section
            st.markdown('<h3 class="section-header">Find Shortest Path</h3>', 
                       unsafe_allow_html=True)
            if len(st.session_state.graph.nodes) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    start_node = st.selectbox("Start From", list(st.session_state.graph.nodes))
                with col2:
                    end_node = st.selectbox("Go To", 
                                          [n for n in st.session_state.graph.nodes if n != start_node])
                
                if st.button("🎯 Find Path"):
                    try:
                        path = nx.dijkstra_path(st.session_state.graph, start_node, end_node)
                        total_cost = sum(st.session_state.graph[u][v]['weight'] 
                                       for u, v in zip(path[:-1], path[1:]))
                        st.success(f"✅ Shortest path: {' → '.join(path)}")
                        st.success(f"💰 Total cost: {total_cost}")
                        draw_graph(path)
                    except nx.NetworkXNoPath:
                        st.error("❌ No path exists between selected nodes!")
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")

            # Graph visualization
            st.markdown('<h3 class="section-header">Graph Visualization</h3>', 
                        unsafe_allow_html=True)
            draw_graph()

        with right_col:
            st.markdown("""
            <div class="side-info">
                <h4>Graph Statistics</h4>
                <ul>
                    <li>Nodes: {}</li>
                    <li>Edges: {}</li>
                </ul>
            </div>
            <div class="side-info">
                <h4>Did you know?</h4>
                <p>Dijkstra's algorithm is used in:</p>
                <ul>
                    <li>GPS Navigation</li>
                    <li>Social Networks</li>
                    <li>Internet Routing</li>
                    <li>Games Pathfinding</li>
                </ul>
            </div>
            """.format(len(st.session_state.graph.nodes), 
                      len(st.session_state.graph.edges)), 
            unsafe_allow_html=True)

        # Save/Load section at the bottom
        st.markdown('<h3 class="section-header">Save & Load Graphs</h3>', 
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            graph_name = st.text_input("Enter Graph Name")
            if st.button("💾 Save Graph"):
                if graph_name:
                    save_graph(graph_name)
                else:
                    st.error("❌ Please enter a graph name.")

        with col2:
            if st.session_state.saved_graphs:
                selected_graph = st.selectbox("Select Saved Graph", 
                                            list(st.session_state.saved_graphs.keys()))
                if st.button("📂 Load Graph"):
                    load_graph(selected_graph)
            else:
                st.info("ℹ️ No saved graphs available")

    with tabs[2]:
        st.markdown('<h2 class="main-header">About Dijkstra\'s Algorithm</h2>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("dijkstra.webp", caption="Edsger W. Dijkstra", use_container_width=True)
            
            st.markdown("""
            <div class="side-info">
                <h4>Timeline</h4>
                <ul>
                    <li>1956: Algorithm conceived</li>
                    <li>1959: First published</li>
                    <li>1960s: Widely adopted</li>
                    <li>Present: Essential in computing</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="side-info">
                <h4>Overview</h4>
                <p>Dijkstra's algorithm is a fundamental graph algorithm that finds the shortest 
                paths between nodes in a graph.</p>
                <div>
                <h4>Key Features</h4>
                🎯 Optimal pathfinding<br>
                ⚡ Efficient computation<br>
                🔄 Versatile applications<br>
                🏆 Industry standard<br>
                </div>
                <div>        
                <h4>Real-world Applications</h4>
                🌐 Network routing protocols<br>
                📍 GPS and navigation systems<br>
                👥 Social networks<br>
                🎮 Video game pathfinding<br>
                📦 Supply chain optimization
                </div>
            </div>
            
            <div class="side-info">
                <h4>How it Works</h4>
                    1️⃣ Initialize distances to infinity<br>
                    2️⃣ Select node with minimum distance<br>
                    3️⃣ Update neighboring distances<br>
                    4️⃣ Repeat until destination reached<br>
                    5️⃣ Reconstruct shortest path        
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 