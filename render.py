import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class EVGridVisualizer:
    def __init__(self):
        plt.ion() # Enable interactive mode for real-time updates
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.patch.set_facecolor('#121212') # Dark background
        
        self.nodes = [
            "Silk Board", "Whitefield", "Indiranagar", "Electronic City",
            "Koramangala", "HSR Layout", "MG Road", "Malleshwaram",
            "Jayanagar", "Banashankari"
        ]
        
        # Create a graph
        self.G = nx.Graph()
        self.G.add_nodes_from(self.nodes)
        
        # Add some representative edges (the grid topology)
        edges = [
            ("Silk Board", "HSR Layout"), ("Silk Board", "Koramangala"),
            ("Silk Board", "Electronic City"), ("Koramangala", "HSR Layout"),
            ("Koramangala", "Indiranagar"), ("Indiranagar", "Whitefield"),
            ("MG Road", "Indiranagar"), ("MG Road", "Malleshwaram"),
            ("MG Road", "Jayanagar"), ("Jayanagar", "Banashankari"),
            ("Banashankari", "Silk Board")
        ]
        self.G.add_edges_from(edges)
        
        # Fixed positions for consistency
        self.pos = nx.spring_layout(self.G, seed=42)
        
    def update_grid(self, load_ratios):
        """
        load_ratios: Array of 10 floats between 0 and 1
        """
        self.ax.clear()
        self.ax.set_facecolor('#121212')
        
        node_colors = []
        for load in load_ratios:
            if load < 0.7:
                node_colors.append('#00FF00') # Green
            elif load <= 0.9:
                node_colors.append('#FFFF00') # Yellow
            else:
                node_colors.append('#FF0000') # Red
        
        nx.draw(
            self.G, self.pos, ax=self.ax,
            with_labels=True,
            node_color=node_colors,
            node_size=2000,
            font_size=10,
            font_color='white',
            edge_color='#444444',
            width=2
        )
        
        self.ax.set_title("BESCOM EV Grid Oracle - Real-time Load Monitor", color='white', fontsize=15)
        plt.draw()
        plt.pause(0.1)
