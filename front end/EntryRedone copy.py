import sys
import os
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
from io import StringIO

class ProfileCard(ctk.CTkFrame):
    def __init__(self, parent, name, command, edit_command, download_command):
        super().__init__(parent)
        self.name = name
        self.command = command
        self.edit_command = edit_command
        self.download_command = download_command
        self.initUI()
        
    def initUI(self):
        self.columnconfigure(0, weight=1)
        self.name_label = ctk.CTkLabel(self, text=self.name, anchor="w")
        self.name_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        edit_button = ctk.CTkButton(self, text="Edit", width=60, command=self.edit_name)
        edit_button.grid(row=0, column=1, padx=(0, 5))
        
        download_button = ctk.CTkButton(self, text="Download", width=80, command=self.download_data)
        download_button.grid(row=0, column=2, padx=(0, 10))
        
        self.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)
        self.configure(fg_color="#45b7ae", corner_radius=10)

    def on_click(self, event):
        self.command(self.name)

    def edit_name(self):
        self.edit_command(self)

    def download_data(self):
        self.download_command(self.name)

class ProfileSelector(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.initUI()

    def initUI(self):
        self.title("Profile Selector")
        self.geometry("800x650")
        self.configure(bg_color="#4ECDC4")
        
        self.columnconfigure(0, weight=1)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=780, height=500)
        self.scrollable_frame.grid(row=0, column=0, pady=20, sticky="nsew")
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        add_button = ctk.CTkButton(self, text="+", width=50, height=50, 
                                   font=("Arial", 20, "bold"), command=self.add_profile)
        add_button.grid(row=1, column=0, pady=10)

    def add_profile(self):
        name = f"New Profile {len(self.profiles) + 1}"
        card = ProfileCard(self.scrollable_frame, name, self.open_profile, self.edit_profile_name, self.download_data)
        card.grid(row=len(self.profiles), column=0, pady=5, sticky="ew")
        self.profiles.append({"name": name, "data": None})
        self.edit_profile_name(card)

    def open_profile(self, name):
        for profile in self.profiles:
            if profile["name"] == name:
                self.data_viewer = DataViewer(profile)
                self.data_viewer.mainloop()
                self.data_viewer.focus_force()
                break

    def edit_profile_name(self, card):
        def save_name():
            new_name = entry.get()
            if new_name:
                old_name = card.name
                card.name = new_name
                card.name_label.configure(text=new_name)
                for profile in self.profiles:
                    if profile["name"] == old_name:
                        profile["name"] = new_name
                        break
            entry.destroy()
            save_button.destroy()

        entry = ctk.CTkEntry(card, width=200)
        entry.insert(0, card.name)
        entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        entry.focus()

        save_button = ctk.CTkButton(card, text="Save", width=60, command=save_name)
        save_button.grid(row=0, column=1, padx=(0, 5))

    def download_data(self, name):
        for profile in self.profiles:
            if profile["name"] == name:
                if profile["data"] is not None:
                    profile["data"].download()
                else:
                    messagebox.showinfo("Info", "No data available for download.")
                break

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
        
        self.text_area = ctk.CTkTextbox(self, width=780, height=300)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)
        
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=10)
        
        prev_button = ctk.CTkButton(nav_frame, text="<", command=self.show_prev)
        prev_button.pack(side=tk.LEFT, padx=5)
        self.row_label = ctk.CTkLabel(nav_frame, text="Row: 0 / 0")
        self.row_label.pack(side=tk.LEFT, padx=5)
        next_button = ctk.CTkButton(nav_frame, text=">", command=self.show_next)
        next_button.pack(side=tk.LEFT, padx=5)
        
        self.radio_buttons_frame = ctk.CTkFrame(self, height=50)
        self.radio_buttons_frame.pack(pady=10, fill=tk.X)
        
        self.radio_buttons_canvas = tk.Canvas(self.radio_buttons_frame, height=50)
        self.radio_buttons_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.radio_buttons_scrollbar = ctk.CTkScrollbar(self.radio_buttons_frame, orientation="horizontal", command=self.radio_buttons_canvas.xview)
        self.radio_buttons_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.radio_buttons_canvas.configure(xscrollcommand=self.radio_buttons_scrollbar.set)
        
        self.radio_buttons_frame_interior = ctk.CTkFrame(self.radio_buttons_canvas)
        self.radio_buttons_canvas.create_window((0, 0), window=self.radio_buttons_frame_interior, anchor="nw")
        
        self.radio_buttons_frame_interior.bind("<Configure>", self.on_frame_configure)
        
        if self.profile["data"] is not None:
            self.show_current()
            self.create_radio_buttons()

    def on_frame_configure(self, event):
        self.radio_buttons_canvas.configure(scrollregion=self.radio_buttons_canvas.bbox("all"))

    def create_radio_buttons(self):
        # Clear existing widgets
        for widget in self.radio_buttons_frame_interior.winfo_children():
            widget.destroy()
            
        # Define the radio columns
        radio_columns = [col for col in self.profile["data"].columns if col.startswith("RADIO_")]
        
        # Create and place buttons in a grid
        for i, col in enumerate(radio_columns):
            button = ctk.CTkButton(self.radio_buttons_frame_interior, text=col, 
                                command=lambda c=col: self.show_bar_chart(c),
                                fg_color="#3da69e", hover_color="#2f8f84", 
                                text_color="white", font=("Arial", 12, "bold"))
            button.grid(row=0, column=i, pady=10, padx=10, sticky="ew")
        
        # Configure grid weights to ensure proper resizing
        for i in range(len(radio_columns)):
            self.radio_buttons_frame_interior.grid_columnconfigure(i, weight=1)
        self.radio_buttons_frame_interior.grid_rowconfigure(0, weight=1)
        
        # Adjust the canvas scroll region to include all buttons
        self.radio_buttons_frame_interior.update_idletasks()
        self.radio_buttons_canvas.config(scrollregion=self.radio_buttons_canvas.bbox("all"))    
        
    def load_profile(self):
        profile_path = f"{self.profile_name}.json"
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
                if profile['data']:
                    profile['data'] = pd.read_json(StringIO(profile['data']))
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

    def show_bar_chart(self, column):
        if self.profile["data"] is not None:
            data = self.profile["data"][column].value_counts()

            if self.chart_window is None or not self.chart_window.winfo_exists():
                self.chart_window = ChartWindow(self)

            self.chart_window.plot_bar_chart(data, column)
            self.chart_window.deiconify()
            self.chart_window.focus_force()

class ChartWindow(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Bar Chart")
        self.geometry("800x600")
        
        layout = ctk.CTkFrame(self)
        layout.pack(fill=tk.BOTH, expand=True)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=layout)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, layout)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        save_button = ctk.CTkButton(layout, text="Save Image", command=self.save_image)
        save_button.pack(side=tk.BOTTOM, pady=10)
        
    def plot_bar_chart(self, data, column):
        self.ax.clear()
        data.plot(kind='bar', ax=self.ax)
        self.ax.set_title(f'Bar Chart for {column}')
        self.ax.set_xlabel('Options')
        self.ax.set_ylabel('Count')
        plt.tight_layout()
        self.canvas.draw()

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        if file_path:
            self.figure.savefig(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ProfileSelector()
    app.mainloop()
