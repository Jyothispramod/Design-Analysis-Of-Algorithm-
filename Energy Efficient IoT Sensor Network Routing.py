import math
import random
import tkinter as tk
from tkinter import ttk

class EnergyGridVisualizer:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "Prim's Algorithm - Minimum Energy IoT Routing Visualizer"
        )
        self.root.geometry("1200x760")
        self.root.minsize(1000, 650)

        # Style configuration for vibrant UI
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color Palette Definitions
        self.C_BG = "#0f172a"  # Slate Dark Navy
        self.C_PANEL = "#1e293b"  # Slate Panel
        self.C_CANVAS = "#f8fafc"  # Bright Off-White Canvas
        self.C_MST = "#10b981"  # Emerald Green (MST Edge)
        self.C_CANDIDATE = "#f59e0b"  # Amber Orange (Route Under Test)
        self.C_NODE_UNVISITED = "#3b82f6"  # Electric Blue
        self.C_NODE_VISITED = "#059669"  # Deep Emerald
        self.C_NODE_START = "#8b5cf6"  # Purple Accent

        # Algorithm State
        self.nodes = []  # List of dicts: [{'id': 0, 'x': x, 'y': y}]
        self.steps = []  # Execution steps
        self.current_step = 0
        self.start_node = 0
        self.delete_mode = False

        # Viewport Transformation Variables
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.setup_ui()
        self.load_default_preset()

    def setup_ui(self):
        # Main Layout Frame
        main_frame = tk.Frame(self.root, bg=self.C_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # --- LEFT CONTROL & ANALYTICS PANEL ---
        ctrl_frame = tk.Frame(main_frame, bg=self.C_PANEL, padx=12, pady=12)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        title_lbl = tk.Label(
            ctrl_frame,
            text="IoT ENERGY ROUTER",
            font=("Helvetica", 12, "bold"),
            bg=self.C_PANEL,
            fg="#f8fafc",
        )
        title_lbl.pack(anchor=tk.W, pady=(0, 2))

        sub_lbl = tk.Label(
            ctrl_frame,
            text="Prim's Algorithm | O(N²)",
            font=("Helvetica", 8),
            bg=self.C_PANEL,
            fg="#94a3b8",
        )
        sub_lbl.pack(anchor=tk.W, pady=(0, 10))

        # Node Creation Controls
        tk.Label(
            ctrl_frame,
            text="Topology Builder",
            font=("Helvetica", 9, "bold"),
            bg=self.C_PANEL,
            fg="#38bdf8",
        ).pack(anchor=tk.W, pady=(5, 2))

        tk.Button(
            ctrl_frame,
            text="+ Add Random Sensor",
            command=self.add_random_node,
            bg="#334155",
            fg="#ffffff",
            activebackground="#475569",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
        ).pack(fill=tk.X, pady=2)

        self.btn_delete = tk.Button(
            ctrl_frame,
            text="Delete Node: OFF",
            command=self.toggle_delete_mode,
            bg="#334155",
            fg="#ffffff",
            activebackground="#ef4444",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
        )
        self.btn_delete.pack(fill=tk.X, pady=2)

        tk.Button(
            ctrl_frame,
            text="Load Preset Network",
            command=self.load_default_preset,
            bg="#334155",
            fg="#ffffff",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            ctrl_frame,
            text="Clear Grid",
            command=self.reset_all,
            bg="#334155",
            fg="#ffffff",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
        ).pack(fill=tk.X, pady=2)

        tk.Frame(ctrl_frame, height=1, bg="#475569").pack(fill=tk.X, pady=8)

        # Execution Controls
        tk.Label(
            ctrl_frame,
            text="Algorithm Controls",
            font=("Helvetica", 9, "bold"),
            bg=self.C_PANEL,
            fg="#38bdf8",
        ).pack(anchor=tk.W, pady=(2, 2))

        start_frame = tk.Frame(ctrl_frame, bg=self.C_PANEL)
        start_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            start_frame,
            text="Start Node:",
            bg=self.C_PANEL,
            fg="#f8fafc",
            font=("Helvetica", 8),
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.start_node_var = tk.StringVar(value="S0")
        self.start_dropdown = ttk.Combobox(
            start_frame,
            textvariable=self.start_node_var,
            values=["S0"],
            state="readonly",
            width=5,
        )
        self.start_dropdown.pack(side=tk.LEFT)
        self.start_dropdown.bind(
            "<<ComboboxSelected>>", self.on_start_node_change
        )

        tk.Button(
            ctrl_frame,
            text="Step-by-Step (Evaluate)",
            command=self.next_step,
            bg="#10b981",
            fg="#ffffff",
            font=("Helvetica", 9, "bold"),
            relief="flat",
            bd=0,
            padx=8,
            pady=5,
        ).pack(fill=tk.X, pady=4)

        tk.Button(
            ctrl_frame,
            text="Run All Steps",
            command=self.run_all_steps,
            bg="#0284c7",
            fg="#ffffff",
            font=("Helvetica", 9, "bold"),
            relief="flat",
            bd=0,
            padx=8,
            pady=5,
        ).pack(fill=tk.X, pady=2)

        tk.Frame(ctrl_frame, height=1, bg="#475569").pack(fill=tk.X, pady=8)

        # Viewport Zoom & Fit
        tk.Label(
            ctrl_frame,
            text="Viewport Controls",
            font=("Helvetica", 9, "bold"),
            bg=self.C_PANEL,
            fg="#38bdf8",
        ).pack(anchor=tk.W, pady=(2, 2))

        zoom_btn_frame = tk.Frame(ctrl_frame, bg=self.C_PANEL)
        zoom_btn_frame.pack(fill=tk.X, pady=2)
        tk.Button(
            zoom_btn_frame,
            text="Zoom In (+)",
            width=10,
            command=self.zoom_in,
            bg="#334155",
            fg="#ffffff",
            relief="flat",
        ).pack(side=tk.LEFT, padx=1)
        tk.Button(
            zoom_btn_frame,
            text="Zoom Out (-)",
            width=10,
            command=self.zoom_out,
            bg="#334155",
            fg="#ffffff",
            relief="flat",
        ).pack(side=tk.LEFT, padx=1)
        tk.Button(
            ctrl_frame,
            text="Fit View to Screen",
            command=self.auto_fit_view,
            bg="#334155",
            fg="#ffffff",
            relief="flat",
        ).pack(fill=tk.X, pady=2)

        tk.Frame(ctrl_frame, height=1, bg="#475569").pack(fill=tk.X, pady=8)

        # Energy Savings Analytics Box
        energy_box = tk.Frame(ctrl_frame, bg="#0f172a", padx=8, pady=8)
        energy_box.pack(fill=tk.X, pady=4)

        tk.Label(
            energy_box,
            text="ENERGY SAVINGS METRICS",
            font=("Helvetica", 8, "bold"),
            bg="#0f172a",
            fg="#34d399",
        ).pack(anchor=tk.W)

        self.lbl_mst_energy = tk.Label(
            energy_box,
            text="Optimal MST: 0.00 mW",
            font=("Consolas", 8),
            bg="#0f172a",
            fg="#f8fafc",
        )
        self.lbl_mst_energy.pack(anchor=tk.W)

        self.lbl_direct_energy = tk.Label(
            energy_box,
            text="Direct Links: 0.00 mW",
            font=("Consolas", 8),
            bg="#0f172a",
            fg="#94a3b8",
        )
        self.lbl_direct_energy.pack(anchor=tk.W)

        self.lbl_savings = tk.Label(
            energy_box,
            text="Saved: 0.00 mW (0.0%)",
            font=("Consolas", 8, "bold"),
            bg="#0f172a",
            fg="#34d399",
        )
        self.lbl_savings.pack(anchor=tk.W)

        # Status Footer
        self.status_label = tk.Label(
            ctrl_frame,
            text="Ready. Click canvas to place nodes.",
            wraplength=180,
            font=("Helvetica", 8, "italic"),
            bg=self.C_PANEL,
            fg="#cbd5e1",
        )
        self.status_label.pack(anchor=tk.W, pady=(8, 0))

        # --- RIGHT DISPLAY AREA (CANVAS & COMPARISON OVERLAY) ---
        display_frame = tk.Frame(main_frame, bg=self.C_BG)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Overlay: Route & Alternate Energy Comparison Box
        self.comp_frame = tk.LabelFrame(
            display_frame,
            text=" Route Comparison & Alternate Path Penalty ",
            font=("Helvetica", 9, "bold"),
            bg=self.C_PANEL,
            fg="#f8fafc",
            padx=6,
            pady=6,
        )
        self.comp_frame.pack(fill=tk.X, pady=(0, 6))

        self.comp_labels = []
        for i in range(3):
            lbl = tk.Label(
                self.comp_frame,
                text=f"Route {i+1}: -",
                font=("Consolas", 8),
                bg="#0f172a",
                fg="#f8fafc",
                anchor="w",
                padx=6,
                pady=4,
            )
            lbl.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.comp_labels.append(lbl)

        # Main Canvas
        self.canvas = tk.Canvas(
            display_frame,
            bg=self.C_CANVAS,
            relief="flat",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

    # --- GEOMETRY & TRANSFORMATIONS ---
    def world_to_screen(self, x, y):
        cx = self.canvas.winfo_width() / 2 + self.pan_x
        cy = self.canvas.winfo_height() / 2 + self.pan_y
        sx = cx + (x - 250) * self.zoom_level
        sy = cy + (y - 200) * self.zoom_level
        return sx, sy

    def screen_to_world(self, sx, sy):
        cx = self.canvas.winfo_width() / 2 + self.pan_x
        cy = self.canvas.winfo_height() / 2 + self.pan_y
        wx = 250 + (sx - cx) / self.zoom_level
        wy = 200 + (sy - cy) / self.zoom_level
        return wx, wy

    def auto_fit_view(self):
        if not self.nodes:
            self.zoom_level = 1.0
            self.pan_x, self.pan_y = 0.0, 0.0
            self.redraw()
            return

        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)

        xs = [n["x"] for n in self.nodes]
        ys = [n["y"] for n in self.nodes]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 100)
        span_y = max(max_y - min_y, 100)

        margin = 70
        scale_x = (cw - 2 * margin) / span_x
        scale_y = (ch - 2 * margin) / span_y
        self.zoom_level = min(scale_x, scale_y, 1.8)

        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2
        self.pan_x = (250 - mid_x) * self.zoom_level
        self.pan_y = (200 - mid_y) * self.zoom_level
        self.redraw()

    def zoom_in(self):
        self.zoom_level *= 1.25
        self.redraw()

    def zoom_out(self):
        self.zoom_level *= 0.8
        self.redraw()

    # --- NODE EDITING CONTROLS ---
    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            self.btn_delete.config(
                text="Delete Mode: ON", bg="#ef4444", fg="#ffffff"
            )
            self.status_label.config(
                text="DELETE MODE: Click any node to remove it."
            )
        else:
            self.btn_delete.config(
                text="Delete Node: OFF", bg="#334155", fg="#ffffff"
            )
            self.status_label.config(
                text="ADD MODE: Click canvas to add nodes."
            )

    def remove_node_at(self, wx, wy):
        click_radius = 20 / self.zoom_level
        node_to_remove = None

        for n in self.nodes:
            dx = n["x"] - wx
            dy = n["y"] - wy
            if math.sqrt(dx * dx + dy * dy) <= click_radius:
                node_to_remove = n
                break

        if node_to_remove:
            self.nodes.remove(node_to_remove)
            for idx, n in enumerate(self.nodes):
                n["id"] = idx
            self.rebuild_algorithm()

    def load_default_preset(self):
        self.nodes = [
            {"id": 0, "x": 100, "y": 120},
            {"id": 1, "x": 260, "y": 80},
            {"id": 2, "x": 400, "y": 140},
            {"id": 3, "x": 120, "y": 300},
            {"id": 4, "x": 280, "y": 320},
            {"id": 5, "x": 420, "y": 280},
        ]
        self.rebuild_algorithm()
        self.root.after(100, self.auto_fit_view)

    def add_random_node(self):
        new_id = len(self.nodes)
        rx = random.randint(80, 420)
        ry = random.randint(80, 320)
        self.nodes.append({"id": new_id, "x": rx, "y": ry})
        self.rebuild_algorithm()

    def on_canvas_click(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        if self.delete_mode:
            self.remove_node_at(wx, wy)
        else:
            new_id = len(self.nodes)
            self.nodes.append({"id": new_id, "x": wx, "y": wy})
            self.rebuild_algorithm()

    def reset_all(self):
        self.nodes = []
        self.steps = []
        self.current_step = 0
        self.rebuild_algorithm()

    def on_start_node_change(self, event):
        val = self.start_node_var.get()
        if val.startswith("S"):
            self.start_node = int(val.replace("S", ""))
            self.rebuild_algorithm()

    # --- PRIM'S ALGORITHM CORE & ALTERNATE ROUTE ANALYSIS O(N^2) ---
    def rebuild_algorithm(self):
        node_labels = [f"S{n['id']}" for n in self.nodes]
        self.start_dropdown["values"] = node_labels if node_labels else ["S0"]
        if self.start_node >= len(self.nodes):
            self.start_node = 0
        self.start_node_var.set(
            f"S{self.start_node}" if self.nodes else "S0"
        )

        self.steps = []
        self.current_step = 0

        n_count = len(self.nodes)
        if n_count < 2:
            self.reset_comparison_labels()
            self.update_energy_savings_ui(0, 0)
            self.redraw()
            return

        visited = [False] * n_count
        visited[self.start_node] = True
        mst_edges = []

        # Iterate N-1 times
        for step_idx in range(n_count - 1):
            candidates = []

            for u in range(n_count):
                if visited[u]:
                    for v in range(n_count):
                        if not visited[v]:
                            dx = self.nodes[u]["x"] - self.nodes[v]["x"]
                            dy = self.nodes[u]["y"] - self.nodes[v]["y"]
                            dist = math.sqrt(dx * dx + dy * dy)
                            energy = (dist**2) * 0.001  # mW scaling
                            candidates.append(
                                {
                                    "u": u,
                                    "v": v,
                                    "dist": dist,
                                    "energy": energy,
                                }
                            )

            if not candidates:
                break

            candidates.sort(key=lambda x: x["energy"])
            best = candidates[0]
            visited[best["v"]] = True
            mst_edges.append((best["u"], best["v"], best["energy"]))

            self.steps.append(
                {
                    "step_num": step_idx + 1,
                    "visited": list(visited),
                    "mst_edges": list(mst_edges),
                    "top_candidates": candidates[:3],
                    "selected": best,
                }
            )

        # Compute Unoptimized Direct Energy (Direct long-range transmission from sink)
        direct_energy = 0.0
        sink_x = self.nodes[self.start_node]["x"]
        sink_y = self.nodes[self.start_node]["y"]
        for i, n in enumerate(self.nodes):
            if i != self.start_node:
                d = math.sqrt((n["x"] - sink_x) ** 2 + (n["y"] - sink_y) ** 2)
                direct_energy += (d**2) * 0.001

        mst_total_energy = sum(e[2] for e in mst_edges)
        self.update_energy_savings_ui(mst_total_energy, direct_energy)
        self.reset_comparison_labels()
        self.redraw()

    # --- EXECUTION & COMPARISON UI ---
    def next_step(self):
        if not self.steps:
            return
        if self.current_step < len(self.steps):
            self.current_step += 1
            self.update_comparison_ui()
            self.redraw()

    def run_all_steps(self):
        if not self.steps:
            return
        self.current_step = len(self.steps)
        self.update_comparison_ui()
        self.redraw()

    def reset_comparison_labels(self):
        for i, lbl in enumerate(self.comp_labels):
            lbl.config(
                text=f"Route {i+1}: -", bg="#0f172a", fg="#94a3b8"
            )

    def update_comparison_ui(self):
        if self.current_step == 0 or not self.steps:
            self.reset_comparison_labels()
            return

        step_data = self.steps[self.current_step - 1]
        top_c = step_data["top_candidates"]
        best = step_data["selected"]

        for i in range(3):
            if i < len(top_c):
                c = top_c[i]
                diff = c["energy"] - best["energy"]

                if c == best:
                    txt = f"R{i+1}: S{c['u']}->S{c['v']} | {c['energy']:.2f}mW\n★ OPTIMAL MIN ROUTE"
                    self.comp_labels[i].config(text=txt, bg="#064e3b", fg="#34d399")
                else:
                    txt = f"R{i+1}: S{c['u']}->S{c['v']} | {c['energy']:.2f}mW\n⚠️ Alternate (+{diff:.2f}mW)"
                    self.comp_labels[i].config(text=txt, bg="#451a03", fg="#fbbf24")
            else:
                self.comp_labels[i].config(
                    text=f"Route {i+1}: None", bg="#0f172a", fg="#64748b"
                )

    def update_energy_savings_ui(self, mst_e, direct_e):
        saved = direct_e - mst_e
        pct = (saved / direct_e * 100) if direct_e > 0 else 0.0

        self.lbl_mst_energy.config(text=f"Optimal MST:    {mst_e:.2f} mW")
        self.lbl_direct_energy.config(text=f"Direct Links:   {direct_e:.2f} mW")
        self.lbl_savings.config(
            text=f"Energy Saved:  {saved:.2f} mW ({pct:.1f}%)"
        )

    # --- CANVAS RENDERING ---
    def redraw(self):
        self.canvas.delete("all")
        n_count = len(self.nodes)

        if n_count == 0:
            self.status_label.config(text="Canvas empty. Click to add nodes.")
            return

        visited_nodes = [False] * n_count
        if self.start_node < n_count:
            visited_nodes[self.start_node] = True

        active_mst_edges = []
        curr_candidates = []
        selected_edge = None

        if self.current_step > 0 and self.current_step <= len(self.steps):
            st = self.steps[self.current_step - 1]
            visited_nodes = st["visited"]
            active_mst_edges = st["mst_edges"]
            curr_candidates = st["top_candidates"]
            selected_edge = st["selected"]

        # 1. Background Grid Lines (Subtle Gray Mesh)
        for i in range(n_count):
            for j in range(i + 1, n_count):
                sx1, sy1 = self.world_to_screen(
                    self.nodes[i]["x"], self.nodes[i]["y"]
                )
                sx2, sy2 = self.world_to_screen(
                    self.nodes[j]["x"], self.nodes[j]["y"]
                )
                self.canvas.create_line(
                    sx1, sy1, sx2, sy2, fill="#e2e8f0", dash=(2, 4)
                )

        # 2. Draw Alternate Candidate Routes Under Test (Amber & Magenta Dashes)
        for idx, c in enumerate(curr_candidates):
            u, v = c["u"], c["v"]
            sx1, sy1 = self.world_to_screen(
                self.nodes[u]["x"], self.nodes[u]["y"]
            )
            sx2, sy2 = self.world_to_screen(
                self.nodes[v]["x"], self.nodes[v]["y"]
            )

            color = self.C_MST if c == selected_edge else self.C_CANDIDATE
            width = 3 if c == selected_edge else 2

            self.canvas.create_line(
                sx1, sy1, sx2, sy2, fill=color, width=width, dash=(4, 2)
            )

            mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
            self.canvas.create_text(
                mx,
                my - 10,
                text=f"R{idx+1}: {c['energy']:.2f}mW",
                fill=color,
                font=("Helvetica", 8, "bold"),
            )

        # 3. Draw Confirmed Low-Energy MST Links (Solid Emerald Green)
        tot_e = 0.0
        for u, v, eng in active_mst_edges:
            tot_e += eng
            sx1, sy1 = self.world_to_screen(
                self.nodes[u]["x"], self.nodes[u]["y"]
            )
            sx2, sy2 = self.world_to_screen(
                self.nodes[v]["x"], self.nodes[v]["y"]
            )
            self.canvas.create_line(
                sx1, sy1, sx2, sy2, fill=self.C_MST, width=4
            )

        # 4. Render IoT Sensor Nodes with Vibrant Colors
        node_radius = max(9, min(14 * self.zoom_level, 20))

        for node in self.nodes:
            nid = node["id"]
            sx, sy = self.world_to_screen(node["x"], node["y"])

            if nid == self.start_node:
                fill_color = self.C_NODE_START  # Purple for Sink Node
            elif visited_nodes[nid]:
                fill_color = self.C_NODE_VISITED  # Deep Green for Connected Nodes
            else:
                fill_color = self.C_NODE_UNVISITED  # Bright Blue for Pending Nodes

            # Node Body
            self.canvas.create_oval(
                sx - node_radius,
                sy - node_radius,
                sx + node_radius,
                sy + node_radius,
                fill=fill_color,
                outline="#ffffff",
                width=2,
            )

            # Node Label Text
            self.canvas.create_text(
                sx,
                sy,
                text=f"S{nid}",
                fill="#ffffff",
                font=("Helvetica", int(node_radius * 0.75), "bold"),
            )

        mode_str = "DELETE MODE" if self.delete_mode else "ADD MODE"
        self.status_label.config(
            text=f"[{mode_str}] Step {self.current_step}/{len(self.steps)} | Connected Nodes: {sum(visited_nodes)}/{n_count}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyGridVisualizer(root)
    root.mainloop()