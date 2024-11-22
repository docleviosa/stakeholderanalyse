import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class StakeholderTool(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Fensterkonfiguration
        self.title("Stakeholderanalyse-Tool")
        self.geometry("1000x600") 
        
        # Liste der Stakeholder-Objekte
        self.stakeholders = []

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)  
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Canvas und Tabelle
        self.create_canvas_area()
        self.create_table_area()

        # Grid unten
        self.create_bottom_grid()

        self.bind("<Configure>", lambda event: self.draw_grid())
        self.canvas.bind("<B1-Motion>", self.drag_stakeholder)
        self.selected_stakeholder = None  # Für Drag-and-Drop

    def create_canvas_area(self):
        self.canvas_frame = ttk.Frame(self, borderwidth=2, relief="sunken")
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#FFFFFF")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

    def create_table_area(self):
        # Tabelle zur Anzeige der Stakeholder
        self.table_frame = ttk.Frame(self, borderwidth=2, relief="sunken")
        self.table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.table = ttk.Treeview(self.table_frame, columns=("Name", "Einstellung"), show="headings")
        self.table.heading("Name", text="Name")
        self.table.heading("Einstellung", text="Einstellung")
        self.table.column("Name", width=100)
        self.table.column("Einstellung", width=100)
        self.table.pack(expand=True, fill="both")

    def update_table(self):
        # Tabelle aktualisieren
        for row in self.table.get_children():
            self.table.delete(row)
        for stakeholder in self.stakeholders:
            self.table.insert("", "end", values=(stakeholder["name"], stakeholder["attitude"]))

    def draw_grid(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.canvas.delete("all")
        
        margin_x = 100
        margin_y = 100
        usable_width = canvas_width - 2 * margin_x
        usable_height = canvas_height - 2 * margin_y

        self.canvas.create_rectangle(margin_x, margin_y, canvas_width - margin_x, canvas_height - margin_y, fill="#D0E4F2")

        influence_labels = ["","Gering","", "","Mittel","", "", "Groß", ""]
        for i in range(1, 10):
            x = margin_x + i * (usable_width / 9)
            if i in [3,6]:
                self.canvas.create_line(x, margin_y, x, canvas_height - margin_y, fill="black", width=2)
            else:
                self.canvas.create_line(x, margin_y, x, canvas_height - margin_y, fill="black")

            self.canvas.create_text(x - (usable_width / 9) + 25, canvas_height - margin_y + 20, text=influence_labels[i - 1], fill="black", font=("Arial", 10))

        attitude_labels = ["Groß", "Mittel", "Gering", "Gering", "Mittel", "Groß"]
        for j in range(1, 7):
            y = margin_y + j * (usable_height / 6)
            if j == 3:
                self.canvas.create_line(margin_x, y, canvas_width - margin_x, y, fill="black", width=2,arrow=tk.LAST)
            else:
                self.canvas.create_line(margin_x, y, canvas_width - margin_x, y, fill="black")

            self.canvas.create_text(margin_x - 30, y - (usable_height / 12), text=attitude_labels[j - 1], fill="black", font=("Arial", 10))

        self.canvas.create_text(canvas_width / 2, margin_y - 20, text="Einfluss / Macht", fill="black", font=("Arial", 12, "bold"))

        for stakeholder in self.stakeholders:
            self.draw_stakeholder(stakeholder)

    def draw_stakeholder(self, stakeholder):
        if stakeholder['attitude'] == 'positiv':
            color = "green"
        elif stakeholder['attitude'] == 'neutral':
            color = "yellow"
        elif stakeholder['attitude'] == 'negativ':
            color = "red"
        else:
            color = "black"
        text_id = self.canvas.create_text(stakeholder['x'], stakeholder['y'], text=stakeholder['name'], fill="black", font=("Arial", 12, "bold"))
        bbox = self.canvas.bbox(text_id)
        padding = 5

        background_id = self.canvas.create_rectangle(
            bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding,
            fill=color,
            outline=""
        )
        
        self.canvas.tag_lower(background_id, text_id)

        stakeholder['background_id'] = background_id
        stakeholder['text_id'] = text_id

    def create_bottom_grid(self):
        grid_frame = ttk.Frame(self, borderwidth=2, relief="sunken")
        grid_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)
        for j in range(2):
            grid_frame.rowconfigure(j, weight=1)

        label_add = ttk.Label(grid_frame, text="Stakeholder hinzufügen")
        label_add.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.text_add = ttk.Entry(grid_frame)
        self.text_add.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        options = ["positiv", "neutral", "negativ"]
        self.combobox_add = ttk.Combobox(grid_frame, values=options, state="readonly")
        self.combobox_add.set("Wähle eine Option")

        self.combobox_add.grid(row=0, column=2, padx=5, pady=5)

        button_add = ttk.Button(grid_frame, text="Hinzufügen", command=self.add_stakeholder)
        button_add.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        
        button_import = ttk.Button(grid_frame, text="Importieren", command=self.import_stakeholder)
        button_import.grid(row=0, column=4, padx=5, pady=5, sticky="nsew")

        label_remove = ttk.Label(grid_frame, text="Stakeholder entfernen")
        label_remove.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.text_remove = ttk.Entry(grid_frame)
        self.text_remove.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        button_remove = ttk.Button(grid_frame, text="Entfernen", command=self.remove_stakeholder)
        button_remove.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        
        button_export = ttk.Button(grid_frame, text="Exportieren", command=self.export_stakeholder)
        button_export.grid(row=1, column=4, padx=5, pady=5, sticky="nsew")

    def add_stakeholder(self):
        name = self.text_add.get()
        if name:
            attitude = self.combobox_add.get()
            stakeholder = {'name': name, 'x': 150, 'y': 150, 'attitude':attitude}
            self.stakeholders.append(stakeholder)
            self.draw_stakeholder(stakeholder)
            self.text_add.delete(0, tk.END)
            self.update_table()
        else:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie einen Namen ein.")

    def remove_stakeholder(self):
        name = self.text_remove.get()
        if name:
            for stakeholder in self.stakeholders:
                if stakeholder['name'] == name:
                    self.canvas.delete(stakeholder['background_id'])
                    self.canvas.delete(stakeholder['text_id'])
                    self.stakeholders.remove(stakeholder)
                    self.text_remove.delete(0, tk.END)
                    self.update_table()
                    return
            messagebox.showinfo("Nicht gefunden", f"Stakeholder '{name}' nicht gefunden.")
        else:
            messagebox.showwarning("Eingabefehler", "Bitte geben Sie einen Namen ein.")

    def import_stakeholder(self):
        file_path = filedialog.askopenfilename(title="Importiere Stakeholder", filetypes=[("JSON Dateien", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.stakeholders = json.load(file)
            self.draw_grid()
            self.update_table()

    def export_stakeholder(self):
        file_path = filedialog.asksaveasfilename(title="Exportiere Stakeholder", defaultextension=".json", filetypes=[("JSON Dateien", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.stakeholders, file)
            messagebox.showinfo("Exportiert", "Stakeholder erfolgreich exportiert.")

    def drag_stakeholder(self, event):
        for stakeholder in self.stakeholders:
            if stakeholder['text_id'] == self.canvas.find_closest(event.x, event.y)[0]:
                self.selected_stakeholder = stakeholder
                break

        if self.selected_stakeholder:
            self.canvas.coords(self.selected_stakeholder['background_id'], event.x - 50, event.y - 15, event.x + 50, event.y + 15)
            self.canvas.coords(self.selected_stakeholder['text_id'], event.x, event.y)
            self.selected_stakeholder['x'], self.selected_stakeholder['y'] = event.x, event.y
            self.update_table()

if __name__ == "__main__":
    app = StakeholderTool()
    app.mainloop()
