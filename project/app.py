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
import sys
from PIL import Image, ImageTk
import time
import PdfParser
import os
import io

class StartingScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JA assure")
        self.geometry("1000x700")
        self.configure(bg_color="#1E1E1E")  # Dark background
        self.alpha = 0.0
        self.attributes('-alpha', self.alpha)
        self.initUI()
        self.fade_in()

    def initUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=20)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Logo
        try:
            logo_image = ctk.CTkImage(Image.open('project/JAassureLOGO.png'), size=(257, 92))
            logo_label = ctk.CTkLabel(main_frame, image=logo_image, text="")
            logo_label.grid(row=0, column=0, pady=(50, 20))
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_placeholder = ctk.CTkLabel(main_frame, text="JA", font=("Arial", 72, "bold"), text_color="#4ECDC4")
            logo_placeholder.grid(row=0, column=0, pady=(50, 20))

        # JA assure text
        ja_assure_label = ctk.CTkLabel(main_frame, text="JA assure PDF Extractor", font=("Arial", 64, "bold"), text_color="#FFFFFF")
        ja_assure_label.grid(row=1, column=0, pady=20)

        # Subtitle
        subtitle_label = ctk.CTkLabel(main_frame, text="Empowering Your Data Journey", font=("Arial", 24), text_color="#4ECDC4")
        subtitle_label.grid(row=2, column=0, pady=(0, 40))

        # Start button
        start_button = ctk.CTkButton(
            main_frame, 
            text="Get Started", 
            command=self.start_app, 
            width=250, 
            height=60, 
            font=("Arial", 24),
            fg_color="#4ECDC4",
            hover_color="#45b7ae",
            corner_radius=30
        )
        start_button.grid(row=3, column=0, pady=40)

    def fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.1
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_in)

    def start_app(self):
        self.fade_out()

    def fade_out(self):
        if self.alpha > 0.0:
            self.alpha -= 0.1
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_out)
        else:
            self.destroy()
            app = ProfileSelector()
            app.mainloop()

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
                if profile.get("data") is not None:
                    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
                    if file_path:
                        profile["data"].to_csv(file_path, index=False)
                        messagebox.showinfo("Success", f"Data for {name} has been downloaded successfully!")
                else:
                    messagebox.showinfo("Info", "No data available for download.")
                break

class DataViewer(ctk.CTkToplevel):
    def __init__(self, profile):
        super().__init__()
        self.profile = profile
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
        load_button = ctk.CTkButton(input_frame, text="Load PDF", command=self.load_csv)
        load_button.pack(side=tk.LEFT)
        
        # Create a frame to hold the two columns
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Create two text areas for headers and values
        self.header_area = ctk.CTkTextbox(self.text_frame, width=380, height=300)
        self.header_area.pack(side=tk.LEFT, padx=(0, 5), fill=tk.BOTH, expand=True)
        
        self.value_area = ctk.CTkTextbox(self.text_frame, width=380, height=300)
        self.value_area.pack(side=tk.RIGHT, padx=(5, 0), fill=tk.BOTH, expand=True)
        
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=10)
        
        prev_button = ctk.CTkButton(nav_frame, text="<", command=self.show_prev)
        prev_button.pack(side=tk.LEFT, padx=5)
        self.row_label = ctk.CTkLabel(nav_frame, text="Row: 0 / 0")
        self.row_label.pack(side=tk.LEFT, padx=5)
        next_button = ctk.CTkButton(nav_frame, text=">", command=self.show_next)
        next_button.pack(side=tk.LEFT, padx=5)
        
        chart_frame = ctk.CTkFrame(self)
        chart_frame.pack(pady=10, fill=tk.X)
        
        self.chart_field = ctk.CTkEntry(chart_frame, width=300, placeholder_text="Enter column name")
        self.chart_field.pack(side=tk.LEFT, padx=10)
        
        generate_button = ctk.CTkButton(chart_frame, text="Generate", command=self.generate_chart)
        generate_button.pack(side=tk.LEFT)
        
        if self.profile["data"] is not None:
            self.show_current()

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                csv_string = PdfParser.extract_csv_from_pdf(file_path)
                csv_stringio = io.StringIO(csv_string)
                try:
                    new_data = pd.read_csv(csv_stringio, encoding='utf-8')
                except UnicodeDecodeError:
                    new_data = pd.read_csv(csv_stringio, encoding='ISO-8859-1')
            
                if self.profile["data"] is None:
                    self.profile["data"] = new_data
                else:
                    if list(new_data.columns) == list(self.profile["data"].columns):
                        self.profile["data"] = pd.concat([self.profile["data"], new_data], ignore_index=True)
                    else:
                        raise ValueError("CSV structure does not match the existing data")
                self.current_row = 0
                self.show_current()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_current(self):
        if self.profile["data"] is not None and not self.profile["data"].empty:
            row_data = self.profile["data"].iloc[self.current_row]
            
            # Clear both text areas
            self.header_area.configure(state=tk.NORMAL)
            self.header_area.delete("1.0", tk.END)
            self.value_area.configure(state=tk.NORMAL)
            self.value_area.delete("1.0", tk.END)
            
            # Insert headers and values
            for col in row_data.index:
                self.header_area.insert(tk.END, f"{col}\n")
                self.value_area.insert(tk.END, f"{row_data[col]}\n")
            
            # Disable editing for both areas
            self.header_area.configure(state=tk.DISABLED)
            self.value_area.configure(state=tk.DISABLED)
            
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

    def generate_chart(self):
        column = self.chart_field.get()
        if self.profile["data"] is not None and column in self.profile["data"].columns:
            data = self.profile["data"][column].value_counts()

            if self.chart_window is None or not self.chart_window.winfo_exists():
                self.chart_window = ChartWindow(self)

            self.chart_window.plot_bar_chart(data, column)
            self.chart_window.deiconify()
            self.chart_window.focus_force()
        else:
            messagebox.showerror("Error", "Invalid column name or no data loaded")

class ChartWindow(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Bar Chart")
        self.geometry("800x650")
        
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
    ctk.set_appearance_mode("light")
    start_screen = StartingScreen()
    start_screen.mainloop()