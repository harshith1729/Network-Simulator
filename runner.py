import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NetworkSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Topology Simulator")
        self.root.configure(bg='#e6f7ff')
        self.root.geometry("900x650")

        # Topology selector
        self.topology_var = tk.StringVar(value="Star")
        options = ["Star", "Bus", "Ring", "Mesh", "Tree"]

        title = tk.Label(
            root, text="Network Simulator",
            font=("Helvetica", 24, "bold"),
            bg='#e6f7ff', fg='#003366'
        )
        title.pack(pady=15)

        selector_frame = tk.Frame(root, bg='#e6f7ff')
        selector_frame.pack(pady=10)
        tk.Label(
            selector_frame, text="Select Topology:",
            font=("Helvetica", 16),
            bg='#e6f7ff', fg='black'
        ).grid(row=0, column=0, padx=10)
        ttk.OptionMenu(
            selector_frame, self.topology_var,
            options[0], *options
        ).grid(row=0, column=1, padx=10)

        # Buttons
        button_frame = tk.Frame(root, bg='#e6f7ff')
        button_frame.pack(pady=20)
        ttk.Button(
            button_frame, text="Draw Topology",
            command=self.draw_topology
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(
            button_frame, text="Simulate Data Flow",
            command=self.simulate_data_flow
        ).pack(side=tk.LEFT, padx=10)

        # Canvas setup
        self.canvas_frame = tk.Frame(root, bg='#e6f7ff')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.graph = None
        self.pos = None
        self.edge_order = []
        self.edge_artists = []
        self.current_edge_index = 0
        self._animation_id = None
        self.figure = None
        self.ax = None
        self.canvas = None

        # Initial draw
        self.draw_topology()

    def draw_topology(self):
        # Cancel any ongoing simulation
        if self._animation_id:
            self.root.after_cancel(self._animation_id)
            self._animation_id = None

        t = self.topology_var.get()
        G = nx.Graph()
        self.edge_order = []

        if t == "Star":
            G.add_node(0)
            for i in range(1, 6):
                G.add_edge(0, i)
                self.edge_order.append((0, i))
        elif t == "Bus":
            for i in range(6):
                if i > 0:
                    G.add_edge(i-1, i)
                    self.edge_order.append((i-1, i))
        elif t == "Ring":
            for i in range(6):
                j = (i + 1) % 6
                G.add_edge(i, j)
                self.edge_order.append((i, j))
        elif t == "Mesh":
            for i in range(6):
                for j in range(i+1, 6):
                    G.add_edge(i, j)
                    self.edge_order.append((i, j))
        elif t == "Tree":
            for i in range(5):
                left = 2*i + 1
                G.add_edge(i, left)
                self.edge_order.append((i, left))
                right = 2*i + 2
                if right < 10:  # Adjust based on desired node count
                    G.add_edge(i, right)
                    self.edge_order.append((i, right))

        self.graph = G
        self.pos = nx.spring_layout(G)
        self._display_graph()

    def _display_graph(self):
        # Clear previous canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.figure)

        self.figure = plt.Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.edge_artists = []  # Reset edge artists

        # Draw nodes
        if self.graph.nodes():
            nx.draw_networkx_nodes(
                self.graph, self.pos, ax=self.ax,
                node_color='#66ccff', node_size=700
            )
            nx.draw_networkx_labels(
                self.graph, self.pos, ax=self.ax,
                font_weight='bold', font_size=10
            )

            # Draw edges individually in specified order
            for u, v in self.edge_order:
                x1, y1 = self.pos[u]
                x2, y2 = self.pos[v]
                line, = self.ax.plot([x1, x2], [y1, y2], color='#3399ff')
                self.edge_artists.append(line)

        self.ax.set_title(f"{self.topology_var.get()} Topology", fontsize=16)
        self.ax.axis('off')  # Turn off axis
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def simulate_data_flow(self):
        if not self.graph or not self.edge_artists:
            return

        # Cancel any ongoing simulation
        if self._animation_id:
            self.root.after_cancel(self._animation_id)

        self.current_edge_index = 0
        self._highlight_next_edge()

    def _highlight_next_edge(self):
        if self.current_edge_index >= len(self.edge_order):
            # Reset all edges
            for artist in self.edge_artists:
                artist.set_color('#3399ff')
            self.canvas.draw()
            return

        # Get current edge from pre-ordered list
        artist = self.edge_artists[self.current_edge_index]
        artist.set_color('red')
        self.canvas.draw()

        # Schedule unhighlight
        self._animation_id = self.root.after(1000, self._unhighlight_current_edge)

    def _unhighlight_current_edge(self):
        # Reset current edge color
        artist = self.edge_artists[self.current_edge_index]
        artist.set_color('#3399ff')
        self.current_edge_index += 1
        self._animation_id = self.root.after(0, self._highlight_next_edge)

if __name__ == '__main__':
    root = tk.Tk()
    NetworkSimulator(root)
    root.mainloop()