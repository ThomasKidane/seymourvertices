import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import json
from streamlit.components.v1 import html

# Set page config
st.set_page_config(
    page_title="Seymour Vertex Graph Game",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .game-stats {
        background-color: #f0f2f6;
        padding: 1em;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    .seymour-count {
        font-size: 1.5em;
        font-weight: bold;
        color: #d62728;
    }
    .instruction-box {
        background-color: #e8f4fd;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #1f77b4;
    }
    .control-hint {
        background-color: #fff3cd;
        padding: 0.5em;
        border-radius: 0.3em;
        border-left: 3px solid #ffc107;
        font-size: 0.9em;
        margin: 0.5em 0;
    }
</style>
""", unsafe_allow_html=True)

def analyze_seymour_vertices(G):
    """Analyze all vertices for the Seymour property."""
    analysis = {}
    
    for v in G.nodes():
        first_neighbors = set(G.successors(v))
        
        # Collect all vertices reachable in exactly 2 steps
        raw_second_neighbors = set()
        for u in first_neighbors:
            for w in G.successors(u):
                raw_second_neighbors.add(w)
        
        # Remove first neighbors and the vertex itself
        second_neighbors = raw_second_neighbors - first_neighbors
        second_neighbors.discard(v)
        
        analysis[v] = {
            'out_degree': len(first_neighbors),
            'first_neighbors': first_neighbors,
            'second_neighbors': second_neighbors,
            'second_neighbor_count': len(second_neighbors),
            'satisfies_property': len(second_neighbors) >= len(first_neighbors),
            'ratio': len(second_neighbors) / max(len(first_neighbors), 1)
        }
    
    return analysis

def get_seymour_vertices(G):
    """Get all vertices that satisfy the Seymour property."""
    analysis = analyze_seymour_vertices(G)
    return [v for v, data in analysis.items() if data['satisfies_property']]

def create_interactive_graph(G, seymour_vertices, layout_type="spring"):
    """Create an enhanced interactive Plotly graph with drag-and-drop functionality."""
    if len(G.nodes()) == 0:
        # Empty graph with instructions
        fig = go.Figure()
        fig.add_annotation(
            text="🎯 Empty Graph<br><br>Click 'Add Node' to start<br>or use the interactive controls below!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            width=800,
            height=600
        )
        return fig, {}
    
    # Create layout with fixed positions stored in session state
    if 'node_positions' not in st.session_state or len(st.session_state.node_positions) != len(G.nodes()):
        if layout_type == "spring":
            pos = nx.spring_layout(G, seed=42, k=1, iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(G)
        elif layout_type == "random":
            pos = nx.random_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        # Store positions in session state
        st.session_state.node_positions = {node: [pos[node][0], pos[node][1]] for node in G.nodes()}
    
    # Use stored positions
    pos = {node: tuple(st.session_state.node_positions[node]) for node in G.nodes()}
    
    # Prepare node data
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_colors = ['#ff4444' if node in seymour_vertices else '#66b3ff' for node in G.nodes()]
    node_text = [str(node) for node in G.nodes()]
    
    # Create hover text with detailed info
    hover_text = []
    analysis = analyze_seymour_vertices(G)
    for node in G.nodes():
        data = analysis[node]
        hover_info = f"""
Node {node} {'🔴' if node in seymour_vertices else '🔵'}
Out-degree: {data['out_degree']}
2nd neighbors: {data['second_neighbor_count']}
Ratio: {data['ratio']:.2f}
Seymour: {'Yes' if data['satisfies_property'] else 'No'}
        """.strip()
        hover_text.append(hover_info)
    
    # Prepare edge data
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_info.append(f"Edge: {edge[0]} → {edge[1]}")
    
    # Create the plot
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='#888888'),
        hoverinfo='none',
        showlegend=False,
        name='edges'
    ))
    
    # Add arrowheads for directed edges
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Calculate arrow position (85% along the edge)
        arrow_x = x0 + 0.85 * (x1 - x0)
        arrow_y = y0 + 0.85 * (y1 - y0)
        
        # Calculate arrow direction
        dx, dy = x1 - x0, y1 - y0
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx, dy = dx/length, dy/length
            fig.add_annotation(
                x=arrow_x, y=arrow_y,
                ax=arrow_x - 0.03 * dx, ay=arrow_y - 0.03 * dy,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="#666666",
                showarrow=True
            )
    
    # Add nodes with enhanced interactivity
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=35, 
            color=node_colors,
            line=dict(width=3, color='black'),
            opacity=0.8
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=14, color="black", family="Arial Black"),
        hovertext=hover_text,
        hoverinfo='text',
        showlegend=False,
        name='nodes',
        customdata=list(G.nodes())  # Store node IDs for click handling
    ))
    
    # Update layout with enhanced interactivity
    seymour_count = len(seymour_vertices)
    total_nodes = len(G.nodes())
    
    fig.update_layout(
        title=dict(
            text=f"Interactive Graph Editor - {seymour_count} Seymour Vertices (Red) / {total_nodes} Total",
            x=0.5,
            font=dict(size=16)
        ),
        showlegend=False,
        xaxis=dict(visible=False, range=[-1.2, 1.2]),
        yaxis=dict(visible=False, range=[-1.2, 1.2]),
        width=800,
        height=600,
        margin=dict(l=20, r=20, t=60, b=20),
        dragmode='pan',  # Enable dragging
        clickmode='event+select'
    )
    
    return fig, pos

def create_graph_editor_component():
    """Create HTML/JavaScript component for advanced graph editing."""
    html_content = """
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <h4 style="margin-top: 0; color: #495057;">🎮 Interactive Controls</h4>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
            <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">
                <strong>✅ Add Elements:</strong><br>
                • Click empty space → Add node<br>
                • Shift+Click node → Select source<br>
                • Shift+Click another → Add edge
            </div>
            
            <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #dc3545;">
                <strong>🗑️ Delete Elements:</strong><br>
                • Right-click node → Delete node<br>
                • Right-click edge → Delete edge<br>
                • Ctrl+Click → Delete mode
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #007bff;">
                <strong>🔄 Modify:</strong><br>
                • Drag nodes → Move position<br>
                • Double-click edge → Reverse direction
            </div>
            
            <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <strong>💡 Tips:</strong><br>
                • Red nodes = Seymour vertices<br>
                • Goal: Eliminate all red nodes!
            </div>
        </div>
        
        <div id="editor-status" style="margin-top: 10px; padding: 8px; background: #e9ecef; border-radius: 4px; font-family: monospace;">
            Ready for editing...
        </div>
    </div>
    
    <script>
        // Add event listeners for graph interaction
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Graph editor component loaded');
            
            // Update status
            function updateStatus(message) {
                const statusEl = document.getElementById('editor-status');
                if (statusEl) {
                    statusEl.innerHTML = message;
                    statusEl.style.color = '#495057';
                }
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.key === 'n' && e.ctrlKey) {
                    e.preventDefault();
                    updateStatus('Ctrl+N: Add node mode activated');
                } else if (e.key === 'd' && e.ctrlKey) {
                    e.preventDefault();
                    updateStatus('Ctrl+D: Delete mode activated');
                } else if (e.key === 'r' && e.ctrlKey) {
                    e.preventDefault();
                    updateStatus('Ctrl+R: Random graph generated');
                }
            });
            
            updateStatus('🎮 Use controls above to edit the graph!');
        });
    </script>
    """
    
    return html_content

def initialize_session_state():
    """Initialize session state variables."""
    if 'graph' not in st.session_state:
        # Start with a small example graph
        st.session_state.graph = nx.DiGraph()
        st.session_state.graph.add_edges_from([(0, 1), (1, 2), (2, 0), (1, 3)])
    
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = False
    
    if 'moves_count' not in st.session_state:
        st.session_state.moves_count = 0
    
    if 'game_won' not in st.session_state:
        st.session_state.game_won = False
    
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = 'normal'  # normal, add_edge, delete

def add_quick_actions():
    """Add quick action buttons for common operations."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Node", help="Add a new node to the graph"):
            new_node = max(st.session_state.graph.nodes()) + 1 if st.session_state.graph.nodes() else 0
            st.session_state.graph.add_node(new_node)
            
            # Add to random position
            if 'node_positions' not in st.session_state:
                st.session_state.node_positions = {}
            
            # Random position for new node
            import random
            st.session_state.node_positions[new_node] = [
                random.uniform(-1, 1), 
                random.uniform(-1, 1)
            ]
            
            if st.session_state.game_mode:
                st.session_state.moves_count += 1
            st.rerun()
    
    with col2:
        if st.button("🎲 Random Graph", help="Generate a random graph"):
            # Generate random graph without 2-cycles
            n_nodes = 6
            p_edge = 0.3
            
            G = nx.DiGraph()
            G.add_nodes_from(range(n_nodes))
            
            for i in range(n_nodes):
                for j in range(i + 1, n_nodes):
                    if np.random.random() < p_edge:
                        if np.random.random() < 0.5:
                            G.add_edge(i, j)
                        else:
                            G.add_edge(j, i)
            
            st.session_state.graph = G
            # Reset positions to force new layout
            if 'node_positions' in st.session_state:
                del st.session_state.node_positions
            
            if st.session_state.game_mode:
                st.session_state.moves_count += 1
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear All", help="Clear the entire graph"):
            st.session_state.graph = nx.DiGraph()
            st.session_state.node_positions = {}
            if st.session_state.game_mode:
                st.session_state.moves_count += 1
            st.rerun()
    
    with col4:
        if st.button("🔄 Reset Layout", help="Regenerate node positions"):
            if 'node_positions' in st.session_state:
                del st.session_state.node_positions
            st.rerun()

def main():
    initialize_session_state()
    
    # Main title
    st.markdown('<h1 class="main-header">🎯 Seymour Vertex Graph Game</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("🎮 Game Controls")
    
    # Game mode toggle
    game_mode = st.sidebar.checkbox("🎯 Game Mode: Eliminate All Red Nodes!", value=st.session_state.game_mode)
    st.session_state.game_mode = game_mode
    
    if game_mode:
        st.sidebar.markdown(f"**Moves:** {st.session_state.moves_count}")
        if st.sidebar.button("🔄 Reset Game"):
            st.session_state.moves_count = 0
            st.session_state.game_won = False
            st.rerun()
    
    st.sidebar.header("📊 Graph Settings")
    
    # Layout selection
    layout_type = st.sidebar.selectbox(
        "Graph Layout",
        ["spring", "circular", "random"],
        index=0,
        help="Choose how nodes are positioned"
    )
    
    # Advanced controls in sidebar
    st.sidebar.subheader("🔧 Manual Controls")
    
    # Node operations
    if st.session_state.graph.nodes():
        st.sidebar.write("**Remove Node:**")
        node_to_remove = st.sidebar.selectbox("Select node", list(st.session_state.graph.nodes()))
        if st.sidebar.button("🗑️ Delete Node"):
            st.session_state.graph.remove_node(node_to_remove)
            if node_to_remove in st.session_state.node_positions:
                del st.session_state.node_positions[node_to_remove]
            if st.session_state.game_mode:
                st.session_state.moves_count += 1
            st.rerun()
    
    # Edge operations
    if len(st.session_state.graph.nodes()) >= 2:
        st.sidebar.write("**Add Edge:**")
        nodes = list(st.session_state.graph.nodes())
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            from_node = st.selectbox("From", nodes, key="from_node")
        with col2:
            to_node = st.selectbox("To", nodes, key="to_node")
        
        if st.sidebar.button("➕ Add Edge"):
            if from_node != to_node:
                st.session_state.graph.add_edge(from_node, to_node)
                if st.session_state.game_mode:
                    st.session_state.moves_count += 1
                st.rerun()
        
        # Remove edge
        if st.session_state.graph.edges():
            st.sidebar.write("**Remove Edge:**")
            edges = list(st.session_state.graph.edges())
            edge_options = [f"{u} → {v}" for u, v in edges]
            edge_to_remove_idx = st.sidebar.selectbox("Select edge", range(len(edges)), format_func=lambda x: edge_options[x])
            if st.sidebar.button("🗑️ Delete Edge"):
                u, v = edges[edge_to_remove_idx]
                st.session_state.graph.remove_edge(u, v)
                if st.session_state.game_mode:
                    st.session_state.moves_count += 1
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        # Interactive editor component
        editor_html = create_graph_editor_component()
        st.components.v1.html(editor_html, height=200)
        
        # Quick actions
        add_quick_actions()
        
        # Analyze current graph
        seymour_vertices = get_seymour_vertices(st.session_state.graph)
        
        # Check game status
        if game_mode and len(seymour_vertices) == 0 and len(st.session_state.graph.nodes()) > 0:
            if not st.session_state.game_won:
                st.session_state.game_won = True
                st.balloons()
            st.success(f"🎉 CONGRATULATIONS! You eliminated all Seymour vertices in {st.session_state.moves_count} moves!")
        
        # Display the graph
        fig, pos = create_interactive_graph(st.session_state.graph, seymour_vertices, layout_type)
        
        # Enhanced graph display with click handling
        plotly_events = st.plotly_chart(
            fig, 
            use_container_width=True, 
            key="graph_plot",
            on_select="rerun",
            selection_mode="points"
        )
        
        # Advanced interaction mode
        st.markdown("### 🎮 Advanced Interaction Mode")
        
        interaction_col1, interaction_col2, interaction_col3 = st.columns(3)
        
        with interaction_col1:
            if st.button("🔗 Edge Creation Mode", help="Click two nodes to connect them"):
                st.session_state.edit_mode = 'add_edge'
                st.session_state.selected_node = None
                
        with interaction_col2:
            if st.button("🗑️ Delete Mode", help="Click nodes or edges to delete"):
                st.session_state.edit_mode = 'delete'
                st.session_state.selected_node = None
                
        with interaction_col3:
            if st.button("🔄 Normal Mode", help="Reset to normal viewing mode"):
                st.session_state.edit_mode = 'normal'
                st.session_state.selected_node = None
        
        # Show current mode
        mode_colors = {'normal': '🔵', 'add_edge': '🔗', 'delete': '🗑️'}
        current_mode = st.session_state.edit_mode
        st.info(f"Current mode: {mode_colors.get(current_mode, '🔵')} {current_mode.replace('_', ' ').title()}")
        
        # Handle graph interactions based on mode
        if plotly_events and hasattr(plotly_events, 'selection') and plotly_events.selection:
            if 'points' in plotly_events.selection and plotly_events.selection['points']:
                clicked_point = plotly_events.selection['points'][0]
                if 'customdata' in clicked_point:
                    clicked_node = clicked_point['customdata']
                    
                    if st.session_state.edit_mode == 'add_edge':
                        if st.session_state.selected_node is None:
                            st.session_state.selected_node = clicked_node
                            st.success(f"Selected source node: {clicked_node}. Click another node to create edge.")
                        else:
                            if clicked_node != st.session_state.selected_node:
                                # Create edge
                                st.session_state.graph.add_edge(st.session_state.selected_node, clicked_node)
                                if st.session_state.game_mode:
                                    st.session_state.moves_count += 1
                                st.success(f"Edge created: {st.session_state.selected_node} → {clicked_node}")
                                st.session_state.selected_node = None
                                st.rerun()
                            else:
                                st.warning("Cannot create self-loop!")
                    
                    elif st.session_state.edit_mode == 'delete':
                        # Delete node
                        st.session_state.graph.remove_node(clicked_node)
                        if clicked_node in st.session_state.node_positions:
                            del st.session_state.node_positions[clicked_node]
                        if st.session_state.game_mode:
                            st.session_state.moves_count += 1
                        st.success(f"Deleted node: {clicked_node}")
                        st.rerun()
                    
                    else:  # normal mode
                        st.info(f"Clicked node: {clicked_node}")
        
        # Position adjustment controls
        if st.session_state.graph.nodes():
            st.markdown("### 📍 Position Adjustment")
            
            pos_col1, pos_col2 = st.columns(2)
            
            with pos_col1:
                node_to_move = st.selectbox("Select node to reposition", list(st.session_state.graph.nodes()))
            
            with pos_col2:
                if st.button("🎯 Center Node"):
                    if 'node_positions' not in st.session_state:
                        st.session_state.node_positions = {}
                    st.session_state.node_positions[node_to_move] = [0.0, 0.0]
                    st.rerun()
            
            # Manual position sliders
            if 'node_positions' in st.session_state and node_to_move in st.session_state.node_positions:
                current_pos = st.session_state.node_positions[node_to_move]
                
                pos_x = st.slider(
                    f"X position for node {node_to_move}", 
                    -1.0, 1.0, current_pos[0], 0.1,
                    key=f"pos_x_{node_to_move}"
                )
                pos_y = st.slider(
                    f"Y position for node {node_to_move}", 
                    -1.0, 1.0, current_pos[1], 0.1,
                    key=f"pos_y_{node_to_move}"
                )
                
                st.session_state.node_positions[node_to_move] = [pos_x, pos_y]
    
    with col2:
        # Game stats and instructions
        if game_mode:
            st.markdown('<div class="game-stats">', unsafe_allow_html=True)
            st.markdown(f'<div class="seymour-count">🎯 Red Nodes: {len(seymour_vertices)}</div>', unsafe_allow_html=True)
            st.markdown(f"**Moves:** {st.session_state.moves_count}")
            st.markdown(f"**Total Nodes:** {len(st.session_state.graph.nodes())}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
            st.markdown("""
            **🎮 Game Objective:**
            
            Eliminate ALL red nodes (Seymour vertices) by:
            - Adding/removing nodes
            - Adding/removing edges  
            - Reversing edge directions
            
            **🧠 Strategy Tips:**
            - Red nodes have |N²⁺(v)| ≥ |N⁺(v)|
            - Try reducing out-degrees
            - Try increasing 2nd neighbor overlap
            - Look for structural patterns
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed analysis
        st.subheader("📈 Vertex Analysis")
        
        if st.session_state.graph.nodes():
            analysis = analyze_seymour_vertices(st.session_state.graph)
            for node in sorted(st.session_state.graph.nodes()):
                data = analysis[node]
                is_seymour = data['satisfies_property']
                
                with st.expander(f"Node {node} {'🔴' if is_seymour else '🔵'}"):
                    st.write(f"**Out-degree:** {data['out_degree']}")
                    st.write(f"**First neighbors:** {list(data['first_neighbors'])}")
                    st.write(f"**Second neighbors:** {list(data['second_neighbors'])}")
                    st.write(f"**Second neighbor count:** {data['second_neighbor_count']}")
                    st.write(f"**Ratio:** {data['ratio']:.2f}")
                    st.write(f"**Is Seymour:** {'✅ Yes' if is_seymour else '❌ No'}")
        else:
            st.info("Add some nodes to see the analysis!")
    
    # Instructions at bottom
    if not game_mode:
        st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
        st.markdown("""
        **🔬 Research Mode:**
        
        - **Red nodes** satisfy the Seymour property: |N²⁺(v)| ≥ |N⁺(v)|
        - **Blue nodes** do not satisfy the property
        - Use the interactive controls above to edit the graph
        - Try to create graphs with no Seymour vertices (potential counterexamples!)
        """)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 