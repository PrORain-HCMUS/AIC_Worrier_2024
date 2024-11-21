import tkinter as tk
from tkinter import ttk, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseButton
import KnowledgeBase as kb

class ResolutionVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Logic Reasoning Visualizer")
        self.create_widgets()
        self.canvas_widget = None
        self.current_layout = "spring"

    def create_widgets(self):
        """Tạo và cài đặt các widget trong giao diện"""
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Canvas chính để vẽ đồ thị
        self.canvas = tk.Canvas(self.frame, width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Panel điều khiển bên phải
        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Nút duyệt chọn file
        self.browse_button = ttk.Button(self.control_frame, text="Browse Input File", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Nhóm nút Reasoning Methods
        self.reasoning_frame = ttk.LabelFrame(self.control_frame, text="Reasoning Methods")
        self.reasoning_frame.pack(pady=5, padx=5, fill="x")

        # Nút Resolution
        self.plot_button = ttk.Button(self.reasoning_frame, text="Resolution Proof", command=self.plot_graph)
        self.plot_button.pack(pady=2, fill="x")

        # Nút Forward Chaining
        self.forward_button = ttk.Button(self.reasoning_frame, text="Forward Chaining", command=self.run_forward_chaining)
        self.forward_button.pack(pady=2, fill="x")

        # Nút Backward Chaining
        self.backward_button = ttk.Button(self.reasoning_frame, text="Backward Chaining", command=self.run_backward_chaining)
        self.backward_button.pack(pady=2, fill="x")

        # Nút Heuristic Search
        self.heuristic_button = ttk.Button(self.reasoning_frame, text="Heuristic Search", command=self.run_heuristic_search)
        self.heuristic_button.pack(pady=2, fill="x")

        # Layout frame và Text widget giữ nguyên như cũ
        self.layout_frame = ttk.LabelFrame(self.control_frame, text="Smart Positioning")
        self.layout_frame.pack(pady=5, padx=5, fill="x")

        # Tạo các tùy chọn layout cho đồ thị
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

        # Text widget để hiển thị các bước
        self.steps_text = tk.Text(self.control_frame, height=20, width=50)
        self.steps_text.pack(pady=5)

    def run_forward_chaining(self):
        """Chạy thuật toán Forward Chaining"""
        if not hasattr(self, 'KB'):
            tk.messagebox.showwarning("Warning", "Please load a Knowledge Base first!")
            return

        # Xóa nội dung cũ
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(tk.END, "Forward Chaining Analysis:\n\n")

        # Thực hiện Forward Chaining
        inferred_facts = self.KB.forward_chaining()

        # Hiển thị các sự kiện được suy luận
        self.steps_text.insert(tk.END, "Inferred Facts:\n")
        for fact in inferred_facts:
            self.steps_text.insert(tk.END, f"- {fact}\n")

        # Hiển thị giải thích chi tiết
        explanation = self.KB.get_reasoning_explanation(self.query[0][0])
        self.steps_text.insert(tk.END, "\nReasoning Details:\n")
        for detail in explanation:
            self.steps_text.insert(tk.END, f"• {detail}\n")

    def run_backward_chaining(self):
        """Chạy thuật toán Backward Chaining"""
        if not hasattr(self, 'KB'):
            tk.messagebox.showwarning("Warning", "Please load a Knowledge Base first!")
            return

        # Xóa nội dung cũ
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(tk.END, "Backward Chaining Analysis:\n\n")

        # Thực hiện Backward Chaining
        goal = self.query[0][0]
        result = self.KB.backward_chaining(goal)

        # Hiển thị kết quả
        self.steps_text.insert(tk.END, f"Goal: {goal}\n")
        self.steps_text.insert(tk.END, f"Proof Result: {'Proven' if result else 'Not Proven'}\n\n")

        # Hiển thị giải thích chi tiết
        explanation = self.KB.get_reasoning_explanation(goal)
        self.steps_text.insert(tk.END, "Reasoning Details:\n")
        for detail in explanation:
            self.steps_text.insert(tk.END, f"• {detail}\n")

    def run_heuristic_search(self):
        """Chạy thuật toán Heuristic Search"""
        if not hasattr(self, 'KB'):
            tk.messagebox.showwarning("Warning", "Please load a Knowledge Base first!")
            return

        # Xóa nội dung cũ
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(tk.END, "Heuristic Search Analysis:\n\n")

        # Thực hiện Heuristic Search
        goal = self.query[0][0]
        result = self.KB.heuristic_search(goal)

        # Hiển thị kết quả
        self.steps_text.insert(tk.END, f"Goal: {goal}\n")
        self.steps_text.insert(tk.END, f"Search Result: {'Goal Found' if result else 'Goal Not Found'}\n\n")

        # Hiển thị giải thích chi tiết
        explanation = self.KB.get_reasoning_explanation(goal)
        self.steps_text.insert(tk.END, "Reasoning Details:\n")
        for detail in explanation:
            self.steps_text.insert(tk.END, f"• {detail}\n")

    def browse_file(self):
        """Xử lý chọn file từ hệ thống"""
        self.filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.filepath:
            self.read_knowledge_base(self.filepath)  # Đọc cơ sở tri thức từ file đã chọn

    def read_knowledge_base(self, filename: str):
        """Đọc và phân tích cơ sở tri thức từ file"""
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            query_letter = content[0]  # Lấy ký tự truy vấn từ dòng đầu tiên
            self.query = [[query_letter]]  # Định dạng lại truy vấn
            self.KB = kb.KnowledgeBase()  # Tạo đối tượng KnowledgeBase
            
            # Parse các mệnh đề từ dòng thứ 2 trở đi
            for cnf in content[2:]:
                clause = [x for x in cnf.split() if x != 'OR']  # Chia mệnh đề thành các nguyên tử
                self.KB.insert(clause)  # Thêm mệnh đề vào cơ sở tri thức
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to read file: {str(e)}")  # Thông báo lỗi nếu không đọc được file

    def get_layout_positions(self, G):
        """Lấy vị trí các node trong đồ thị theo layout đã chọn"""
        layout_name = self.layout_var.get()  # Lấy tên layout đã chọn
        layout_functions = {
            "spring": lambda: nx.spring_layout(G, k=1.5, iterations=50),
            "hierarchical": lambda: nx.kamada_kawai_layout(G),
            "circular": lambda: nx.circular_layout(G, scale=2),
            "shell": lambda: nx.shell_layout(G, scale=2),
            "spiral": lambda: nx.spiral_layout(G, scale=2),
            "random": lambda: nx.random_layout(G),
            "spectral": lambda: nx.spectral_layout(G),
            "planar": lambda: nx.planar_layout(G)
        }
        return layout_functions.get(layout_name, layout_functions["spring"])()  # Trả về vị trí các node

    def update_layout(self):
        """Cập nhật lại đồ thị khi thay đổi layout"""
        if hasattr(self, 'G'):
            self.plot_graph(reuse_graph=True)  # Vẽ lại đồ thị

    def plot_graph(self, reuse_graph=False):
        """Vẽ đồ thị hợp giải"""
        # Xóa canvas cũ nếu có
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        if not reuse_graph:
            self.G = nx.DiGraph()  # Tạo đồ thị có hướng
            result, check = self.KB.prove_by_resolution(self.query)  # Thực hiện hợp giải

            # Cập nhật các bước hợp giải vào Text widget
            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(tk.END, f"Negated query: {self.query}\n")
            
            # Thêm các bước hợp giải vào đồ thị
            for i, (clause_i, clause_j, resolvent) in enumerate(self.KB.resolution_path):
                self.steps_text.insert(tk.END, f"Step {i+1}: Resolving {clause_i} and {clause_j} -> {resolvent}\n")
                
                # Tạo chuỗi đại diện cho các node
                clause_i_str = ' OR '.join(clause_i)
                clause_j_str = ' OR '.join(clause_j)
                resolvent_str = ' OR '.join(resolvent[0])
                
                # Thêm các node và cạnh vào đồ thị
                self.G.add_node(clause_i_str)
                self.G.add_node(clause_j_str)
                self.G.add_node(resolvent_str)
                self.G.add_edge(clause_i_str, resolvent_str, label=f'Step {i+1}')
                self.G.add_edge(clause_j_str, resolvent_str, label=f'Step {i+1}')

        # Lấy vị trí các node từ layout đã chọn
        pos = self.get_layout_positions(self.G)

        # Tạo figure và vẽ đồ thị
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Đặt màu cho các node
        node_colors = []
        for node in self.G.nodes:
            if node == ' OR '.join(self.KB.resolution_path[-1][2][0]):
                node_colors.append('lightgreen' if node == '{}' else 'lightcoral')
            else:
                node_colors.append('skyblue')

        # Vẽ đồ thị
        nx.draw(self.G, pos, with_labels=True, node_color=node_colors, 
                node_size=3000, edge_color='black', linewidths=1, 
                font_size=10, arrows=True, ax=ax)
        
        # Vẽ nhãn cho các cạnh
        edge_labels = nx.get_edge_attributes(self.G, 'label')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

        # Xử lý việc kéo thả node trên đồ thị
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

        # Kết nối các sự kiện click, di chuyển và thả chuột
        fig.canvas.mpl_connect('button_press_event', on_click)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)

        plt.tight_layout()
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()  # Tạo cửa sổ chính
    app = ResolutionVisualizer(root)  # Khởi tạo ứng dụng
    root.mainloop()  # Chạy vòng lặp chính của tkinter
