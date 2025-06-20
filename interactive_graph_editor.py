import streamlit as st
import networkx as nx
import json
from streamlit.components.v1 import html

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

def create_interactive_graph_editor(graph_data, width=800, height=600):
    """Create an interactive graph editor with drag-and-drop functionality."""
    
    # Convert NetworkX graph to JSON format
    nodes = []
    edges = []
    
    # Analyze Seymour vertices
    G = nx.DiGraph()
    G.add_edges_from(graph_data.get('edges', []))
    G.add_nodes_from(graph_data.get('nodes', []))
    seymour_vertices = get_seymour_vertices(G)
    
    # Prepare nodes data
    for i, node in enumerate(graph_data.get('nodes', [])):
        nodes.append({
            'id': node,
            'x': 50 + (i % 5) * 150,  # Arrange in grid initially
            'y': 50 + (i // 5) * 120,
            'is_seymour': node in seymour_vertices
        })
    
    # Prepare edges data
    for edge in graph_data.get('edges', []):
        edges.append({'from': edge[0], 'to': edge[1]})
    
    # Get the current move mode from Streamlit session state if available
    move_mode = graph_data.get('move_mode', False)
    
    graph_json = json.dumps({'nodes': nodes, 'edges': edges, 'move_mode': move_mode})
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            #graph-canvas {{
                border: 2px solid #ccc;
                border-radius: 8px;
                cursor: grab;
                background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%), 
                           linear-gradient(-45deg, #f8f9fa 25%, transparent 25%), 
                           linear-gradient(45deg, transparent 75%, #f8f9fa 75%), 
                           linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
                background-size: 20px 20px;
                background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                user-select: none;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                touch-action: none;
                max-width: 100%;
                height: auto;
            }}
            #canvas-container {{
                position: relative;
                display: block;
                width: 100%;
                max-width: {width}px;
                margin: 0 auto;
            }}
            #instructions {{
                margin-top: 10px;
                padding: 15px;
                background: #e3f2fd;
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                max-width: 100%;
            }}
            .instruction-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 12px;
                margin-top: 10px;
            }}
            .instruction-item {{
                background: white;
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid #2196f3;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            #status-bar {{
                margin-top: 10px;
                padding: 12px 16px;
                background: linear-gradient(135deg, #2196f3, #1976d2);
                color: white;
                border-radius: 8px;
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 13px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {{
                #instructions {{
                    padding: 12px;
                    font-size: 13px;
                }}
                .instruction-grid {{
                    grid-template-columns: 1fr;
                    gap: 8px;
                }}
                .instruction-item {{
                    padding: 10px;
                    font-size: 12px;
                }}
                #status-bar {{
                    padding: 10px 12px;
                    font-size: 12px;
                }}
                #graph-canvas {{
                    max-width: calc(100vw - 40px);
                }}
            }}
            
            @media (max-width: 480px) {{
                .instruction-item {{
                    padding: 8px;
                    font-size: 11px;
                }}
                #instructions {{
                    padding: 10px;
                    font-size: 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <canvas id="graph-canvas" width="{width}" height="{height}"></canvas>
        </div>
        
        <div id="instructions">
            <strong>🎮 Interactive Graph Editor - Multiple Modes Available!</strong>
            <div class="instruction-grid">
                <div class="instruction-item">
                    <strong>🔵 Add Node:</strong> Double-click empty space
                </div>
                <div class="instruction-item">
                    <strong>🔗 Connect Mode:</strong> Drag node → node to create edge
                </div>
                <div class="instruction-item">
                    <strong>📦 Move Mode:</strong> Drag nodes to reposition them
                </div>
                <div class="instruction-item">
                    <strong>🗑️ Delete:</strong> Right-click nodes or edges
                </div>
                <div class="instruction-item">
                    <strong>✨ Visual Feedback:</strong> Orange/green lines in connect mode, purple indicator in move mode
                </div>
                <div class="instruction-item">
                    <strong>🎯 Sidebar:</strong> Toggle modes, manage nodes, view analysis
                </div>
            </div>
        </div>
        
        <div id="status-bar">Ready for editing... Red nodes = Seymour vertices</div>

        <script>
            const canvas = document.getElementById('graph-canvas');
            const ctx = canvas.getContext('2d');
            const statusBar = document.getElementById('status-bar');
            
            // Graph data
            let graphData = {graph_json};
            let selectedNode = null;
            let dragMode = false;
            let edgeMode = false;
            let sourceNode = null;
            
            // Initialize move mode from graph data
            let moveMode = graphData.move_mode || false;
            console.log('Initial graph data:', graphData);
            console.log('Initial moveMode from data:', moveMode);
            
            // Node and edge styling
            const nodeRadius = 25;
            const seymourColor = '#ff4444';
            const normalColor = '#66b3ff';
            const edgeColor = '#666666';
            const selectedColor = '#ffdd44';
            
            function updateStatus(message) {{
                statusBar.textContent = message;
            }}
            
            function getMousePos(e) {{
                const rect = canvas.getBoundingClientRect();
                return {{
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                }};
            }}
            
            function getNodeAt(x, y) {{
                for (let node of graphData.nodes) {{
                    const dist = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
                    if (dist <= nodeRadius) {{
                        return node;
                    }}
                }}
                return null;
            }}
            
            function getEdgeAt(x, y) {{
                for (let edge of graphData.edges) {{
                    const fromNode = graphData.nodes.find(n => n.id === edge.from);
                    const toNode = graphData.nodes.find(n => n.id === edge.to);
                    
                    if (fromNode && toNode) {{
                        // Check if point is near the edge line
                        const dist = distanceToLine(x, y, fromNode.x, fromNode.y, toNode.x, toNode.y);
                        if (dist <= 10) {{
                            return edge;
                        }}
                    }}
                }}
                return null;
            }}
            
            function distanceToLine(x, y, x1, y1, x2, y2) {{
                const A = x - x1;
                const B = y - y1;
                const C = x2 - x1;
                const D = y2 - y1;
                
                const dot = A * C + B * D;
                const lenSq = C * C + D * D;
                
                if (lenSq === 0) return Math.sqrt(A * A + B * B);
                
                const param = dot / lenSq;
                
                let xx, yy;
                if (param < 0) {{
                    xx = x1;
                    yy = y1;
                }} else if (param > 1) {{
                    xx = x2;
                    yy = y2;
                }} else {{
                    xx = x1 + param * C;
                    yy = y1 + param * D;
                }}
                
                const dx = x - xx;
                const dy = y - yy;
                return Math.sqrt(dx * dx + dy * dy);
            }}
            
            function drawArrow(fromX, fromY, toX, toY) {{
                const headlen = 15;
                const angle = Math.atan2(toY - fromY, toX - fromX);
                
                // Adjust end point to not overlap with node
                const adjustedToX = toX - nodeRadius * Math.cos(angle);
                const adjustedToY = toY - nodeRadius * Math.sin(angle);
                
                // Draw line
                ctx.moveTo(fromX, fromY);
                ctx.lineTo(adjustedToX, adjustedToY);
                
                // Draw arrowhead
                ctx.moveTo(adjustedToX, adjustedToY);
                ctx.lineTo(
                    adjustedToX - headlen * Math.cos(angle - Math.PI / 6),
                    adjustedToY - headlen * Math.sin(angle - Math.PI / 6)
                );
                ctx.moveTo(adjustedToX, adjustedToY);
                ctx.lineTo(
                    adjustedToX - headlen * Math.cos(angle + Math.PI / 6),
                    adjustedToY - headlen * Math.sin(angle + Math.PI / 6)
                );
            }}
            
            function render() {{
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                console.log('Rendering - Node count:', graphData.nodes.length, 'Edge count:', graphData.edges.length);
                
                // Draw edges
                ctx.strokeStyle = edgeColor;
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                for (let edge of graphData.edges) {{
                    const fromNode = graphData.nodes.find(n => n.id === edge.from);
                    const toNode = graphData.nodes.find(n => n.id === edge.to);
                    
                    if (fromNode && toNode) {{
                        drawArrow(fromNode.x, fromNode.y, toNode.x, toNode.y);
                    }}
                }}
                
                ctx.stroke();
                
                // Draw nodes
                for (let node of graphData.nodes) {{
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
                    
                    // Node color based on Seymour property
                    ctx.fillStyle = node.is_seymour ? seymourColor : normalColor;
                    ctx.fill();
                    
                    // Node border
                    ctx.strokeStyle = node === selectedNode ? selectedColor : '#000000';
                    ctx.lineWidth = node === selectedNode ? 4 : 2;
                    ctx.stroke();
                    
                    // Node label
                    ctx.fillStyle = '#000000';
                    ctx.font = 'bold 14px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(node.id.toString(), node.x, node.y);
                }}
                
                // Draw temporary visual feedback when dragging
                if (isDragging && startDragNode && !moveMode) {{
                    const mousePos = {{ x: lastMouseX, y: lastMouseY }};
                    const targetNode = getNodeAt(lastMouseX, lastMouseY);
                    
                    // Use different colors based on what we're doing
                    if (targetNode && targetNode !== startDragNode) {{
                        // Hovering over valid target - show green dashed line
                        ctx.strokeStyle = '#4caf50';
                        ctx.lineWidth = 4;
                        ctx.setLineDash([8, 4]);
                    }} else {{
                        // Just dragging - show orange line
                        ctx.strokeStyle = '#ff9800';
                        ctx.lineWidth = 3;
                        ctx.setLineDash([5, 5]);
                    }}
                    
                    ctx.beginPath();
                    
                    // Adjust start point to not overlap with node
                    const angle = Math.atan2(mousePos.y - startDragNode.y, mousePos.x - startDragNode.x);
                    const startX = startDragNode.x + nodeRadius * Math.cos(angle);
                    const startY = startDragNode.y + nodeRadius * Math.sin(angle);
                    
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(mousePos.x, mousePos.y);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // Draw a small circle at the mouse position to show the connection point
                    ctx.beginPath();
                    ctx.arc(mousePos.x, mousePos.y, 8, 0, 2 * Math.PI);
                    ctx.fillStyle = targetNode && targetNode !== startDragNode ? '#4caf50' : '#ff9800';
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }}
                
                // Draw mode indicator
                if (moveMode) {{
                    ctx.fillStyle = '#9c27b0';
                    ctx.font = 'bold 16px Arial';
                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'top';
                    ctx.fillText('MOVE MODE', 10, 10);
                }}
            }}
            
            function updateSeymourStatus() {{
                // Recalculate Seymour vertices (simplified)
                for (let node of graphData.nodes) {{
                    const outEdges = graphData.edges.filter(e => e.from === node.id);
                    const firstNeighbors = outEdges.map(e => e.to);
                    
                    let secondNeighbors = [];
                    for (let neighbor of firstNeighbors) {{
                        const secondEdges = graphData.edges.filter(e => e.from === neighbor);
                        for (let edge of secondEdges) {{
                            if (edge.to !== node.id && !firstNeighbors.includes(edge.to)) {{
                                if (!secondNeighbors.includes(edge.to)) {{
                                    secondNeighbors.push(edge.to);
                                }}
                            }}
                        }}
                    }}
                    
                    node.is_seymour = secondNeighbors.length >= firstNeighbors.length;
                }}
                
                const seymourCount = graphData.nodes.filter(n => n.is_seymour).length;
                updateStatus(`Seymour vertices: ${{seymourCount}}/${{graphData.nodes.length}} (Red nodes)`);
            }}
            
            function renumberNodes() {{
                // Renumber nodes to be consecutive starting from 0
                const sortedNodes = [...graphData.nodes].sort((a, b) => a.id - b.id);
                const idMapping = {{}};
                
                // Create mapping from old IDs to new consecutive IDs
                sortedNodes.forEach((node, index) => {{
                    idMapping[node.id] = index;
                }});
                
                // Update node IDs
                graphData.nodes.forEach(node => {{
                    node.id = idMapping[node.id];
                }});
                
                // Update edge references
                graphData.edges.forEach(edge => {{
                    edge.from = idMapping[edge.from];
                    edge.to = idMapping[edge.to];
                }});
            }}
            
            function checkForWin() {{
                const seymourCount = graphData.nodes.filter(n => n.is_seymour).length;
                if (seymourCount === 0 && graphData.nodes.length > 0) {{
                    // Player won! All nodes are blue (no Seymour vertices)
                    setTimeout(() => {{
                        const userWantsToSubmit = confirm(
                            "🎉 CONGRATULATIONS! You eliminated all red vertices!\\n\\n" +
                            "Would you like to submit your solution to Thomas for research purposes?\\n" +
                            "Your graph configuration will be sent to thomastkf02@gmail.com"
                        );
                        
                        if (userWantsToSubmit) {{
                            submitSolution();
                        }}
                    }}, 500); // Small delay to let the UI update
                    
                    return true;
                }}
                return false;
            }}
            
            function submitSolution() {{
                const solutionData = {{
                    nodes: graphData.nodes.map(n => n.id),
                    edges: graphData.edges.map(e => [e.from, e.to]),
                    timestamp: new Date().toISOString(),
                    nodeCount: graphData.nodes.length,
                    edgeCount: graphData.edges.length
                }};
                
                // Send solution to Streamlit backend for email submission
                const event = new CustomEvent('submitSolution', {{
                    detail: solutionData
                }});
                window.dispatchEvent(event);
                
                alert("Thank you! Your solution has been submitted to Thomas for research analysis.");
            }}
            
            function sendDataToStreamlit() {{
                // Send updated graph data back to Streamlit
                const event = new CustomEvent('graphUpdate', {{
                    detail: {{
                        nodes: graphData.nodes.map(n => n.id),
                        edges: graphData.edges.map(e => [e.from, e.to])
                    }}
                }});
                window.dispatchEvent(event);
            }}
            
            let lastMouseX = 0;
            let lastMouseY = 0;
            let dragStartX = 0;
            let dragStartY = 0;
            let isDragging = false;
            let startDragNode = null;
            let dragStartTime = 0;
            const DRAG_THRESHOLD = 10; // pixels to move before considering it a drag
            const EDGE_CREATE_THRESHOLD = 200; // ms to hold before switching to move mode
            
            // Mouse event handlers
            canvas.addEventListener('mousedown', (e) => {{
                e.preventDefault(); // Prevent default drag behavior
                const pos = getMousePos(e);
                lastMouseX = pos.x;
                lastMouseY = pos.y;
                const node = getNodeAt(pos.x, pos.y);
                
                if (e.button === 0) {{ // Left click
                    if (node) {{
                        selectedNode = node;
                        startDragNode = node;
                        isDragging = false;
                        dragStartTime = Date.now();
                        dragStartX = pos.x;
                        dragStartY = pos.y;
                        canvas.style.cursor = 'grab';
                        const modeInstructions = moveMode ? 
                            "drag to move this node around" : 
                            "drag to another node to connect";
                        updateStatus(`Ready to drag from node ${{node.id}} - ${{modeInstructions}}`);
                    }} else {{
                        selectedNode = null;
                        startDragNode = null;
                        isDragging = false;
                        updateStatus('Click a node to interact with it');
                    }}
                }} else if (e.button === 2) {{ // Right click
                    const node = getNodeAt(pos.x, pos.y);
                    const edge = getEdgeAt(pos.x, pos.y);
                    
                    if (node) {{
                        // Remove node and all connected edges
                        graphData.edges = graphData.edges.filter(e => e.from !== node.id && e.to !== node.id);
                        graphData.nodes = graphData.nodes.filter(n => n !== node);
                        updateSeymourStatus();
                        updateStatus(`Deleted node ${{node.id}}`);
                        sendDataToStreamlit();
                        render();
                    }} else if (edge) {{
                        // Remove edge
                        graphData.edges = graphData.edges.filter(e => e !== edge);
                        updateSeymourStatus();
                        updateStatus(`Deleted edge ${{edge.from}} → ${{edge.to}}`);
                        sendDataToStreamlit();
                        render();
                    }}
                }}
            }});
            
            canvas.addEventListener('mousemove', (e) => {{
                e.preventDefault(); // Prevent default drag behavior
                const pos = getMousePos(e);
                const currentMouseX = pos.x;
                const currentMouseY = pos.y;
                
                // Always update mouse position for drawing
                lastMouseX = currentMouseX;
                lastMouseY = currentMouseY;
                
                if (startDragNode && !isDragging) {{
                    // Calculate distance moved from the start position
                    const distanceMoved = Math.sqrt(
                        Math.pow(currentMouseX - dragStartX, 2) + 
                        Math.pow(currentMouseY - dragStartY, 2)
                    );
                    
                    if (distanceMoved > DRAG_THRESHOLD) {{
                        isDragging = true;
                        canvas.style.cursor = 'grabbing';
                        
                        if (moveMode) {{
                            console.log('Starting drag in MOVE mode for node', startDragNode.id);
                            updateStatus(`Moving node ${{startDragNode.id}}`);
                            edgeMode = false;
                        }} else {{
                            console.log('Starting drag in CONNECT mode for node', startDragNode.id);
                            edgeMode = true;
                            sourceNode = startDragNode;
                            updateStatus(`Dragging from node ${{startDragNode.id}} - drag to another node to connect`);
                        }}
                    }}
                }}
                
                if (isDragging && startDragNode) {{
                    if (moveMode) {{
                        // Move mode - update node position in real-time
                        console.log('Moving node', startDragNode.id, 'to', currentMouseX, currentMouseY);
                        startDragNode.x = currentMouseX;
                        startDragNode.y = currentMouseY;
                        updateStatus(`Moving node ${{startDragNode.id}} to (${{Math.round(currentMouseX)}}, ${{Math.round(currentMouseY)}})`);
                        render(); // Immediate visual update
                    }} else {{
                        // Connect mode - check if we're over another node for edge creation
                        const targetNode = getNodeAt(currentMouseX, currentMouseY);
                        
                        if (targetNode && targetNode !== startDragNode) {{
                            updateStatus(`Release to create edge: ${{startDragNode.id}} → ${{targetNode.id}}`);
                        }} else {{
                            updateStatus(`Drag to another node to connect from ${{startDragNode.id}}`);
                        }}
                        render(); // Update for connection line
                    }}
                }}
            }});
            
            canvas.addEventListener('mouseup', (e) => {{
                const pos = getMousePos(e);
                const targetNode = getNodeAt(pos.x, pos.y);
                
                if (isDragging && startDragNode && moveMode) {{
                    // Move mode - just update position and send data
                    sendDataToStreamlit();
                    updateStatus(`Node ${{startDragNode.id}} moved to new position`);
                }} else if (isDragging && startDragNode && !moveMode && targetNode && targetNode !== startDragNode) {{
                    // Connect mode - check for existing edge in the desired direction
                    const existingEdge = graphData.edges.find(
                        edge => edge.from === startDragNode.id && edge.to === targetNode.id
                    );
                    
                    // Check for reverse edge (potential 2-cycle)
                    const reverseEdge = graphData.edges.find(
                        edge => edge.from === targetNode.id && edge.to === startDragNode.id
                    );
                    
                    if (!existingEdge) {{
                        if (reverseEdge) {{
                            // Reverse the existing edge instead of creating a 2-cycle
                            reverseEdge.from = startDragNode.id;
                            reverseEdge.to = targetNode.id;
                            updateSeymourStatus();
                            sendDataToStreamlit();
                            updateStatus(`Reversed edge: now ${{startDragNode.id}} → ${{targetNode.id}}`);
                            
                            // Check for win condition
                            checkForWin();
                        }} else {{
                            // Create new edge
                            graphData.edges.push({{ from: startDragNode.id, to: targetNode.id }});
                            updateSeymourStatus();
                            sendDataToStreamlit();
                            updateStatus(`Created edge: ${{startDragNode.id}} → ${{targetNode.id}}`);
                            
                            // Check for win condition
                            checkForWin();
                        }}
                    }} else {{
                        updateStatus(`Edge already exists: ${{startDragNode.id}} → ${{targetNode.id}}`);
                    }}
                }} else if (isDragging && startDragNode && !moveMode) {{
                    // Connect mode but didn't end on a valid target
                    updateStatus(`Drag cancelled - must end on a different node`);
                }} else if (startDragNode && !isDragging) {{
                    // Just a click without drag
                    const modeText = moveMode ? "move it around" : "drag to another node to connect";
                    updateStatus(`Selected node ${{startDragNode.id}} - ${{modeText}}`);
                }}
                
                // Reset drag state
                isDragging = false;
                startDragNode = null;
                edgeMode = false;
                sourceNode = null;
                selectedNode = null;
                canvas.style.cursor = 'grab';
                render();
            }});
            
            canvas.addEventListener('dblclick', (e) => {{
                const pos = getMousePos(e);
                const node = getNodeAt(pos.x, pos.y);
                
                if (!node) {{
                    // Add new node
                    const newId = Math.max(...graphData.nodes.map(n => n.id), -1) + 1;
                    graphData.nodes.push({{
                        id: newId,
                        x: pos.x,
                        y: pos.y,
                        is_seymour: false
                    }});
                    updateSeymourStatus();
                    updateStatus(`Added node ${{newId}}`);
                    sendDataToStreamlit();
                    render();
                }}
            }});
            
            canvas.addEventListener('contextmenu', (e) => {{
                e.preventDefault();
                const pos = getMousePos(e);
                const node = getNodeAt(pos.x, pos.y);
                const edge = getEdgeAt(pos.x, pos.y);
                
                if (node) {{
                    // Remove node and all connected edges
                    const deletedNodeId = node.id;
                    graphData.edges = graphData.edges.filter(e => e.from !== node.id && e.to !== node.id);
                    graphData.nodes = graphData.nodes.filter(n => n !== node);
                    
                    // Renumber nodes to keep them consecutive
                    renumberNodes();
                    updateSeymourStatus();
                    updateStatus(`Deleted node ${{deletedNodeId}} and renumbered remaining nodes`);
                    sendDataToStreamlit();
                    render();
                    
                    // Check for win condition
                    checkForWin();
                }} else if (edge) {{
                    // Remove edge
                    graphData.edges = graphData.edges.filter(e => e !== edge);
                    updateSeymourStatus();
                    updateStatus(`Deleted edge ${{edge.from}} → ${{edge.to}}`);
                    sendDataToStreamlit();
                    render();
                    
                    // Check for win condition
                    checkForWin();
                }}
            }});
            
            // Check canvas initialization
            console.log('Canvas:', canvas, 'Context:', ctx);
            console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
            
            // Initial render
            updateSeymourStatus();
            render();
            
            // Set initial status based on mode
            updateStatus(moveMode ? 'Move Mode: Drag nodes to reposition them' : 'Connect Mode: Drag between nodes to create edges');
            
            // Function to toggle move mode
            function toggleMoveMode() {{
                moveMode = !moveMode;
                updateStatus(moveMode ? 'Move Mode: Drag nodes to reposition them' : 'Connect Mode: Drag between nodes to create edges');
                render();
            }}
            
            // Listen for updates from Streamlit
            window.addEventListener('graphDataUpdate', (e) => {{
                graphData = e.detail;
                // Update move mode from the new data
                if (graphData.move_mode !== undefined) {{
                    moveMode = graphData.move_mode;
                    console.log('Move mode updated from Streamlit:', moveMode);
                    updateStatus(moveMode ? 'Move Mode: Drag nodes to reposition them' : 'Connect Mode: Drag between nodes to create edges');
                }}
                updateSeymourStatus();
                render();
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def main():
    st.set_page_config(
        page_title="Seymour Vertex Research Tool - Thomas K.",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎯 Get all blue!")
    st.markdown("*Interactive graph editor for mathematical conjecture research*")
    
    # Add tabs for different sections
    tab1, tab2 = st.tabs(["🎮 Research Tool", "📚 About This Project"])
    
    with tab2:
        st.header("📚 About This Research")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🔬 The Seymour Conjecture
            
            This tool is designed to help find **counterexamples** to Seymour's theorem, which states:
            
            > *"For every directed graph, there exists at least one vertex v where the number of second neighbors |N²⁺(v)| is greater than or equal to the number of first neighbors |N⁺(v)|."*
            
            **What are Second Neighbors?**
            - **First neighbors (N⁺(v))**: Vertices directly reachable from v in one step
            - **Second neighbors (N²⁺(v))**: Vertices reachable in exactly two steps (excluding first neighbors and v itself)
            
            **The Goal:**
            Find a directed graph where **ALL vertices are blue** (no Seymour vertices exist).
            Such a graph would be a counterexample to Seymour's theorem!
            
            ### 🎯 How to Use This Tool
            1. **Red nodes** = Seymour vertices (satisfy the property)
            2. **Blue nodes** = Non-Seymour vertices 
            3. **Goal**: Make all nodes blue by editing the graph
            4. **Submit**: When you find a solution, submit it for research analysis
            
            ### 🚀 Research Impact
            Any counterexample found could contribute to important mathematical research 
            on graph theory and help advance our understanding of directed graph properties.
            """)
            
        with col2:
            st.markdown("""
            ### 👨‍🎓 About the Researcher
            
            **Thomas Kidane**  
            Rising Sophomore at Duke University
            
            📧 **Contact**: thomastkf02@gmail.com
            
            🔬 **Research Focus**:  
            Finding counterexamples to mathematical conjectures, particularly in graph theory
            
            🎯 **This Project**:  
            Developed to aid in systematic exploration of potential counterexamples to Seymour's theorem through interactive visualization and gameplay
            
            ---
            
            ### 🤝 Contribute to Research
            
            Found an interesting graph? Submit your solutions to help advance mathematical research!
            
            **All submissions are:**
            - Analyzed for research purposes
            - Credited to contributors
            - Part of ongoing academic study
            """)
    
    with tab1:
        # Initialize session state
        if 'graph_nodes' not in st.session_state:
            st.session_state.graph_nodes = [0, 1, 2, 3]
        
        if 'graph_edges' not in st.session_state:
            st.session_state.graph_edges = [(0, 1), (1, 2), (2, 0), (1, 3)]
        
        if 'moves_count' not in st.session_state:
            st.session_state.moves_count = 0
            
        if 'move_mode' not in st.session_state:
            st.session_state.move_mode = False
        
        # Navigation
        col_back, col_mode = st.columns([1, 2])
        with col_back:
            if st.button("← About", key="back_button"):
                # Simple way to go back to about tab
                st.info("💡 Use the tabs above to navigate between Research Tool and About sections")
        
        with col_mode:
            # Move mode toggle
            st.session_state.move_mode = st.toggle("📦 Move Mode", value=st.session_state.move_mode, key="move_mode_toggle")
        
        # Sidebar controls
        with st.sidebar:
            st.header("🎮 Research Controls")
            
            st.metric("Graph Moves", st.session_state.moves_count)
            
            st.header("📊 Current Graph")
            
            # Create NetworkX graph for analysis
            G = nx.DiGraph()
            G.add_nodes_from(st.session_state.graph_nodes)
            G.add_edges_from(st.session_state.graph_edges)
            
            seymour_vertices = get_seymour_vertices(G)
            
            st.metric("Total Nodes", len(st.session_state.graph_nodes))
            st.metric("Total Edges", len(st.session_state.graph_edges))
            st.metric("Seymour Vertices (Red)", len(seymour_vertices))
            
            if seymour_vertices:
                st.write("**Seymour vertices:**", seymour_vertices)
            
            # Win status
            if len(seymour_vertices) == 0 and len(st.session_state.graph_nodes) > 0:
                st.success("🎉 ALL BLUE! Perfect counterexample candidate!")
                st.balloons()
            elif len(seymour_vertices) > 0:
                st.info(f"Goal: Eliminate {len(seymour_vertices)} red vertices")
            
            st.header("🎯 Node Management")
            
            if st.session_state.graph_nodes:
                st.write("**Current Nodes:**")
                for i, node in enumerate(sorted(st.session_state.graph_nodes)):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Show node info
                        G = nx.DiGraph()
                        G.add_nodes_from(st.session_state.graph_nodes)
                        G.add_edges_from(st.session_state.graph_edges)
                        seymour_vertices = get_seymour_vertices(G)
                        
                        is_seymour = node in seymour_vertices
                        st.write(f"Node {node} {'🔴' if is_seymour else '🔵'}")
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_node_{node}", help=f"Delete node {node}"):
                            # Remove node and connected edges
                            st.session_state.graph_edges = [
                                edge for edge in st.session_state.graph_edges 
                                if edge[0] != node and edge[1] != node
                            ]
                            st.session_state.graph_nodes = [n for n in st.session_state.graph_nodes if n != node]
                            
                            # Renumber nodes
                            old_to_new = {}
                            for idx, old_node in enumerate(sorted(st.session_state.graph_nodes)):
                                old_to_new[old_node] = idx
                            
                            st.session_state.graph_nodes = list(range(len(st.session_state.graph_nodes)))
                            st.session_state.graph_edges = [
                                (old_to_new[edge[0]], old_to_new[edge[1]]) 
                                for edge in st.session_state.graph_edges
                            ]
                            
                            st.session_state.moves_count += 1
                            st.rerun()
            else:
                st.info("No nodes to manage. Add nodes by double-clicking the canvas.")
            
            st.header("⚡ Quick Actions")
            
            # Single clear button as requested
            if st.button("🧹 Clear Graph", use_container_width=True):
                st.session_state.graph_nodes = []
                st.session_state.graph_edges = []
                st.session_state.moves_count += 1
                st.rerun()
                
            if st.button("🎲 Random Graph", use_container_width=True):
                import random
                nodes = list(range(6))
                edges = []
                for i in range(6):
                    for j in range(i + 1, 6):
                        if random.random() < 0.3:
                            if random.random() < 0.5:
                                edges.append((i, j))
                            else:
                                edges.append((j, i))
                
                st.session_state.graph_nodes = nodes
                st.session_state.graph_edges = edges
                st.session_state.moves_count += 1
                st.rerun()
        
        # Main editor area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Interactive Graph Editor")
            
            # Prepare graph data for the editor
            graph_data = {
                'nodes': st.session_state.graph_nodes,
                'edges': st.session_state.graph_edges,
                'move_mode': st.session_state.move_mode
            }
            
            # Create the interactive editor
            editor_html = create_interactive_graph_editor(graph_data, width=700, height=500)
            
            # Display the editor
            html(editor_html, height=650)
        
        with col2:
            st.subheader("📈 Vertex Analysis")
            
            if st.session_state.graph_nodes:
                analysis = analyze_seymour_vertices(G)
                
                for node in sorted(st.session_state.graph_nodes):
                    if node in analysis:
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
                st.info("Add nodes to see analysis")
            
            # Instructions
            st.subheader("🎮 How to Use")
            
            mode_text = "**Current Mode:** 📦 Move Mode" if st.session_state.move_mode else "**Current Mode:** 🔗 Connect Mode"
            st.markdown(f"{mode_text}")
            
            st.markdown("""
            **Goal:** Find a graph with ALL BLUE vertices!
            
            **Controls:**
            - **Double-click**: Add node
            - **📦 Move Mode**: Drag nodes to reposition
            - **🔗 Connect Mode**: Drag node → node to create edge
            - **Right-click**: Delete nodes/edges
            - **Sidebar**: Manage individual nodes
            
            **Visual Feedback:**
            - 🧡 Orange line: Connecting (connect mode)
            - 💚 Green line: Valid target (connect mode)
            - Purple "MOVE MODE": When in move mode
            
            **Research Notes:**
            - Red = Seymour vertices (satisfy property)
            - Blue = Potential counterexample vertices
            - All blue = Submit to research!
            """)

if __name__ == "__main__":
    main() 