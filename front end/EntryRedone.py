import sys
import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class ProfileCard(ctk.CTkFrame):
    def __init__(self, parent, name, command):
        super().__init__(parent)
        self.name = name
        self.command = command
        self.initUI()
        
    def initUI(self):
        self.name_label = ctk.CTkLabel(self, text=self.name)
        self.name_label.pack(pady=10)
        self.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)
        self.configure(fg_color="#45b7ae", corner_radius=10)

    def on_click(self, event):
        self.command(self.name)

class ProfileSelector(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.initUI()

    def initUI(self):
        self.title("Profile Selector")
        self.geometry("800x600")
        self.configure(bg_color="#4ECDC4")
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=780, height=500)
        self.scrollable_frame.pack(pady=20)
        
        add_button = ctk.CTkButton(self, text="+", width=50, height=50, 
                                   font=("Arial", 20, "bold"), command=self.add_profile)
        add_button.pack(pady=10)

    def add_profile(self):
        name = ctk.CTkInputDialog(text="Enter profile name:", title="New Profile").get_input()
        if name:
            card = ProfileCard(self.scrollable_frame, name, self.open_profile)
            card.pack(pady=5)
            self.profiles.append({"name": name, "data": None})

    def open_profile(self, name):
        for profile in self.profiles:
            if profile["name"] == name:
                self.data_viewer = DataViewer(profile)
                self.data_viewer.mainloop()
                break

class ChartWindow(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Bar Chart")
        self.geometry("800x600")
        
        self.figure = Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        
        save_button = ctk.CTkButton(self, text="Save Image", command=self.save_image)
        save_button.pack(pady=10)

    def plot_bar_chart(self, data, column):
        self.ax.clear()
        data.plot(kind='bar', ax=self.ax)
        self.ax.set_title(f'Bar Chart for {column}')
        self.ax.set_xlabel('Options')
        self.ax.set_ylabel('Count')
        self.canvas.draw()

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        if file_path:
            self.figure.savefig(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")

class DataViewer(ctk.CTkToplevel):
    def __init__(self, profile):
        super().__init__()
        self.profile_name = profile["name"]
        self.profile = self.load_profile()
        self.current_row = 0
        self.chart_window = None
        self.initUI()

    def initUI(self):
        self.title(f"Data Viewer - {self.profile['name']}")
        self.geometry("800x600")
        self.configure(bg_color="#4ECDC4")
        
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10)
        
        self.input_field = ctk.CTkEntry(input_frame, width=500)
        self.input_field.pack(side=tk.LEFT, padx=10)
        load_button = ctk.CTkButton(input_frame, text="Load CSV", command=self.load_csv)
        load_button.pack(side=tk.LEFT)
        
        self.text_area = ctk.CTkTextbox(self, width=780, height=300, state=tk.DISABLED)
        self.text_area.pack(pady=10)
        
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=10)
        
        prev_button = ctk.CTkButton(nav_frame, text="<", command=self.show_prev)
        prev_button.pack(side=tk.LEFT, padx=5)
        self.row_label = ctk.CTkLabel(nav_frame, text="Row: 0 / 0")
        self.row_label.pack(side=tk.LEFT, padx=5)
        next_button = ctk.CTkButton(nav_frame, text=">", command=self.show_next)
        next_button.pack(side=tk.LEFT, padx=5)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=780, height=50)
        self.scrollable_frame.pack(pady=10)
        
        if self.profile["data"] is not None:
            self.show_current()
            self.create_radio_buttons()

    def load_profile(self):
        profile_path = f"{self.profile_name}.json"
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
                if profile['data']:
                    profile['data'] = pd.read_json(profile['data'])
                return profile
        else:
            return {"name": self.profile_name, "data": None}

    def save_profile(self):
        profile_copy = self.profile.copy()
        if isinstance(profile_copy['data'], pd.DataFrame):
            profile_copy['data'] = profile_copy['data'].to_json()
        with open(f"{self.profile_name}.json", 'w') as f:
            json.dump(profile_copy, f)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                new_data = pd.read_csv(file_path)
                if self.profile["data"] is None:
                    self.profile["data"] = new_data
                else:
                    if list(new_data.columns) == list(self.profile["data"].columns):
                        self.profile["data"] = pd.concat([self.profile["data"], new_data], ignore_index=True)
                    else:
                        raise ValueError("CSV structure does not match the existing data")
                self.current_row = 0
                self.show_current()
                self.create_radio_buttons()
                self.save_profile()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_current(self):
        if self.profile["data"] is not None and not self.profile["data"].empty:
            row_data = self.profile["data"].iloc[self.current_row]
            formatted_data = "\n".join([f"{col}: {row_data[col]}" for col in row_data.index])
            self.text_area.configure(state=tk.NORMAL)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, formatted_data)
            self.text_area.configure(state=tk.DISABLED)
            total_rows = len(self.profile["data"])
            self.row_label.configure(text=f"Row: {self.current_row + 1} / {total_rows}")

    def show_prev(self):
        if self.profile["data"] is not None and self.current_row > 0:
            self.current_row -= 1
            self.show_current()

    def show_next(self):
        if self.profile["data"] is not None and self.current_row < len(self.profile["data"]) - 1:
            self.current_row += 1
            self.show_current()

    def create_radio_buttons(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        radio_columns = [col for col in self.profile["data"].columns if col.startswith("RADIO_")]
        for col in radio_columns:
            button = ctk.CTkButton(self.scrollable_frame, text=col, 
                                   command=lambda c=col: self.show_bar_chart(c))
            button.pack(pady=5, padx=5, side=tk.LEFT)

    def show_bar_chart(self, column):
        if self.profile["data"] is not None:
            data = self.profile["data"][column].value_counts()
            
            if self.chart_window is None:
                self.chart_window = ChartWindow(self)
            
            self.chart_window.plot_bar_chart(data, column)
            self.chart_window.show()

if __name__ == "__main__":
    app = ProfileSelector()
    app.mainloop()
