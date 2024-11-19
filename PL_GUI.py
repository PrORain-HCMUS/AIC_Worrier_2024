import tkinter as tk
from tkinter import ttk, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseButton
import kb 

class ResolutionVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("PL-Resolution Visualizer")
        self.create_widgets()
        self.canvas_widget = None
        self.current_layout = "spring"  # Track current layout

    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.browse_button = ttk.Button(self.control_frame, text="Browse Input File", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.plot_button = ttk.Button(self.control_frame, text="Plot Graph", command=self.plot_graph)
        self.plot_button.pack(pady=5)

        # Add layout selection frame
        self.layout_frame = ttk.LabelFrame(self.control_frame, text="Smart Positioning")
        self.layout_frame.pack(pady=5, padx=5, fill="x")

        # Add layout options
        self.layout_var = tk.StringVar(value="spring")
        layouts = [
            ("Spring", "spring"),
            ("Hierarchical", "hierarchical"),
            ("Circular", "circular"),
            ("Shell", "shell"),
            ("Spiral", "spiral"),
            ("Random", "random"),
            ("Spectral", "spectral"),
            ("Planar", "planar")
        ]
        
        for text, value in layouts:
            ttk.Radiobutton(self.layout_frame, text=text, value=value, 
                          variable=self.layout_var, command=self.update_layout).pack(anchor="w", padx=5)

        self.steps_text = tk.Text(self.control_frame, height=20, width=50)
        self.steps_text.pack(pady=5)

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.filepath:
            self.readKB(self.filepath)

    def readKB(self, filename):
        content = []
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read().splitlines()

        content = [line.strip() for line in content if line.strip()]
        query_letter = content[0]
        kb_size = int(content[1])
        kb_string = content[2:]
        self.query = [[query_letter]]
        self.KB = kb.KnowledgeBase()
        for cnf in kb_string:
            clause = cnf.split()
            clause = list(filter(lambda x: x != 'OR', clause))
            self.KB.addClause(clause)

    def get_layout_positions(self, G):
        layout_name = self.layout_var.get()
        if layout_name == "spring":
            return nx.spring_layout(G, k=1.5, iterations=50)
        elif layout_name == "hierarchical":
            return nx.kamada_kawai_layout(G)
        elif layout_name == "circular":
            return nx.circular_layout(G, scale=2)
        elif layout_name == "shell":
            return nx.shell_layout(G, scale=2)
        elif layout_name == "spiral":
            return nx.spiral_layout(G, scale=2)
        elif layout_name == "random":
            return nx.random_layout(G)
        elif layout_name == "spectral":
            return nx.spectral_layout(G)
        elif layout_name == "planar":
            return nx.planar_layout(G)
        return nx.spring_layout(G)  # Default fallback

    def update_layout(self):
        if hasattr(self, 'G'):  # Only update if graph exists
            self.plot_graph(reuse_graph=True)

    def plot_graph(self, reuse_graph=False):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        if not reuse_graph:
            self.G = nx.DiGraph()
            result, check = self.KB.PL_Resolution(self.query)

            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(tk.END, f"Negative query: {self.query}\n")
            for i, (clause_i, clause_j, resolvent) in enumerate(self.KB.steps):
                self.steps_text.insert(tk.END, f"Step {i+1}: Resolving {clause_i} and {clause_j} -> {resolvent}\n")

            for i, (clause_i, clause_j, resolvent) in enumerate(self.KB.steps):
                clause_i_str = ' OR '.join(clause_i)
                clause_j_str = ' OR '.join(clause_j)
                resolvent_str = ' OR '.join(resolvent[0])
                self.G.add_node(clause_i_str)
                self.G.add_node(clause_j_str)
                self.G.add_node(resolvent_str)
                self.G.add_edge(clause_i_str, resolvent_str, label=f'Step {i+1}')
                self.G.add_edge(clause_j_str, resolvent_str, label=f'Step {i+1}')

        pos = self.get_layout_positions(self.G)

        fig, ax = plt.subplots(figsize=(12, 8))
        node_colors = []
        for node in self.G.nodes:
            if node == ' OR '.join(self.KB.steps[-1][2][0]):
                if node == '{}':
                    node_colors.append('lightgreen')
                else:
                    node_colors.append('lightcoral')
            else:
                node_colors.append('skyblue')

        nx.draw(self.G, pos, with_labels=True, node_color=node_colors, 
                node_size=3000, edge_color='black', linewidths=1, 
                font_size=10, arrows=True, ax=ax)
        
        edge_labels = nx.get_edge_attributes(self.G, 'label')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

        selected_node = None

        def on_click(event):
            nonlocal selected_node
            if event.button is MouseButton.LEFT and event.xdata is not None and event.ydata is not None:
                for node in pos:
                    if (event.xdata - pos[node][0])**2 + (event.ydata - pos[node][1])**2 < 0.01:
                        selected_node = node
                        break

        def on_motion(event):
            if selected_node and event.xdata is not None and event.ydata is not None:
                pos[selected_node] = (event.xdata, event.ydata)
                ax.clear()
                nx.draw(self.G, pos, with_labels=True, node_color=node_colors, 
                       node_size=3000, edge_color='black', linewidths=1, 
                       font_size=10, arrows=True, ax=ax)
                nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_color='red', ax=ax)
                fig.canvas.draw()

        def on_release(event):
            nonlocal selected_node
            selected_node = None

        fig.canvas.mpl_connect('button_press_event', on_click)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)

        plt.tight_layout()
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResolutionVisualizer(root)
    root.mainloop()
