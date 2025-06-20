# 🎯 Seymour Vertex Graph Game

An interactive web application for exploring the **Second Neighbor Problem** in graph theory through gamification!

## 🎮 What is this?

This is an interactive graph editor where you can:
- Create and edit directed graphs in real-time
- See which vertices satisfy the **Seymour property** (colored red)
- Play a game where you try to eliminate all red vertices!

## 🧠 The Science Behind It

A vertex `v` satisfies the **Seymour property** if:
```
|N²⁺(v)| ≥ |N⁺(v)|
```

Where:
- `N⁺(v)` = first neighbors (direct out-neighbors)
- `N²⁺(v)` = second neighbors (vertices reachable in exactly 2 steps, excluding first neighbors and `v` itself)

**Seymour's Theorem** states that every directed graph has at least one vertex satisfying this property. But can you find counterexamples? 🤔

## 🚀 How to Run

### Option 1: Easy Launch
```bash
python run_game.py
```

### Option 2: Direct Streamlit
```bash
streamlit run seymour_graph_game.py
```

### Option 3: Manual Installation
```bash
pip install streamlit networkx plotly numpy
streamlit run seymour_graph_game.py
```

## 🎮 Game Modes

### 🔬 Research Mode
- Interactive graph editor
- Real-time Seymour vertex highlighting
- Detailed vertex analysis
- Perfect for exploring the theory

### 🎯 Game Mode
- **Objective**: Eliminate ALL red vertices!
- Track your moves
- Get celebration when you win
- Challenge: Can you find a graph with NO Seymour vertices?

## 🛠️ Features

### Graph Editing
- ➕ Add/remove nodes
- 🔗 Add/remove edges
- 🔄 Reverse edge directions
- 🎲 Generate random graphs
- 🧹 Clear graph

### Visualization
- 🔴 Red nodes = Seymour vertices
- 🔵 Blue nodes = Non-Seymour vertices
- Interactive Plotly graphs with zoom/pan
- Multiple layout options (spring, circular, random)
- Hover tooltips with vertex info

### Analysis Tools
- Detailed vertex-by-vertex breakdown
- Out-degree and second neighbor counts
- Real-time ratio calculations
- Expandable analysis panels

## 🧩 Game Strategy Tips

To eliminate red vertices, try:

1. **Reduce out-degrees**: Remove outgoing edges from red vertices
2. **Increase second neighbor overlap**: Add edges that create shared second neighbors
3. **Structural changes**: 
   - Break long paths
   - Create cycles
   - Isolate vertices
4. **Edge reversal**: Sometimes flipping an edge direction helps

## 🔬 Research Applications

This tool is perfect for:
- **Education**: Understanding second neighbor concepts visually
- **Research**: Exploring potential counterexamples to Seymour's theorem
- **Pattern Discovery**: Finding structures that minimize/maximize Seymour vertices
- **Algorithm Testing**: Validating graph theory algorithms

## 🏆 Challenges

Try these challenges:
1. **Speedrun**: Eliminate all red vertices in minimum moves
2. **Counterexample Hunt**: Find a graph with 0 Seymour vertices (if possible!)
3. **Maximize**: Create graphs with the most Seymour vertices
4. **Structural**: Eliminate reds using only edge reversals

## 📊 Technical Details

- Built with **Streamlit** for the web interface
- **NetworkX** for graph data structures and algorithms
- **Plotly** for interactive visualizations
- **No 2-cycles**: Implementation prevents accidental bidirectional edges
- **Real-time analysis**: Seymour property calculated on every graph change

## 🤝 Contributing

Found a bug? Have ideas for new features? 
- The core algorithm is in `analyze_seymour_vertices()`
- Graph generation uses the corrected method (no 2-cycles)
- UI improvements always welcome!

## 🎓 Educational Value

Perfect for:
- Graph theory courses
- Discrete mathematics classes
- Research in theoretical computer science
- Anyone curious about the beauty of graph structures

---

**Have fun exploring the fascinating world of second neighbors!** 🎯

*Can you prove or disprove Seymour's theorem through gameplay?* 