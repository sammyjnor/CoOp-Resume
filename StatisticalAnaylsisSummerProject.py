from email.utils import localtime
import tkinter as tk
import numpy as np
from tkinter import *
from datetime import datetime, timedelta
from tkinter import Canvas, ttk
import csv
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, ttk, Label, Button, Tk, messagebox
import sqlite3
from datetime import datetime

#This was a COLLABORATIVE project. Worked with four other exemplary computer engineers to complete.

global current_graph_index
global db_file
global bio_table 

current_graph_index = 0

def exit_program():
    window.destroy()

def select_file():

    global summary_file_path, metadata_file_path
    global db_file
    global bio_table
    global csv_file

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()

    # Show an instruction message
    messagebox.showinfo("Folder Selection", "Please select a folder containing both 'summary.csv' and 'metadata.csv' files.")

    # Prompt the user to select a folder containing both summary and metadata files
    folder_path = filedialog.askdirectory()

    if not folder_path:
        messagebox.showerror("Error!", "Folder not selected.")
        exit()

    # Check if "summary.csv" and "metadata.csv" files exist in the selected folder
    summary_file_path = f"{folder_path}/summary.csv"
    metadata_file_path = f"{folder_path}/metadata.csv"

    try:
        with open(summary_file_path, "r"):
            pass
    except FileNotFoundError:
        messagebox.showerror("Error!", f"'summary.csv' file not found in the selected folder.")
        exit()

    try:
        with open(metadata_file_path, "r"):
            pass
    except FileNotFoundError:
        messagebox.showerror("Error!", f"'metadata.csv' file not found in the selected folder.")
        exit()

    if summary_file_path:
        csv_file = summary_file_path
        database(csv_file, db_file, bio_table)
       

    if metadata_file_path:
        global metadata
        metadata = pd.read_csv(metadata_file_path)

    # Close the Tkinter root window
    root.destroy()



def open_metadata():

    if metadata_file_path:
        global metadata
        metadata = []  # List to store each column
        with open(metadata_file_path, "r") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if not metadata:
                    metadata = [[] for _ in row]  # Create a list for each column
                for j, value in enumerate(row):
                    if i == 0:
                        metadata[j].append(str(value) + ": ")
                    else:
                        metadata[j].append(str(value))

    popup_window = tk.Toplevel()  # Create a new popup window
    popup_window.title("Popup Window")
    popup_window.attributes("-fullscreen", True)

    # Create toolbar
    toolbar = tk.Frame(popup_window, bg="gray")
    toolbar.pack(side=tk.TOP, fill=tk.X)

    exit_button = tk.Button(toolbar, text="  X  ", command=popup_window.destroy)
    exit_button.pack(side=tk.RIGHT)

    # Create a Frame to hold the textboxes
    textbox_frame = tk.Frame(popup_window)
    textbox_frame.pack(expand=True, pady=10)

    # Add a title label
    title_label = tk.Label(textbox_frame, text="App Info", font=("Arial", 16, "bold"))
    title_label.pack()

    textboxes = []  # List to store the Entry widgets

    # Create individual textboxes for each column
    for column_data in metadata:
        textbox = tk.Entry(textbox_frame, width=50)
        textbox.pack(pady=10)
        textboxes.append(textbox)

    # Display the data in each textbox
    for i, column_data in enumerate(metadata):
        textbox = textboxes[i]
        textbox.insert(tk.END, "\n".join(column_data))

    # Center the textbox_frame and toolbar in the popup_window
    popup_window.update_idletasks()
    screen_width = popup_window.winfo_screenwidth()
    screen_height = popup_window.winfo_screenheight()
    textbox_frame_width = textbox_frame.winfo_width()
    textbox_frame_height = textbox_frame.winfo_height()
    x_offset = (screen_width - textbox_frame_width) // 2
    y_offset = (screen_height - textbox_frame_height) // 2
    textbox_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    popup_window.geometry(f"{textbox_frame_width}x{textbox_frame_height}+{x_offset}+{y_offset}")

    popup_window.mainloop()

db_file = 'database.db'
bio_table = 'biotable'


# Creates database from summary csv file
def database(csv_fle, db_file, bio_table):
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(f'DROP TABLE IF EXISTS {bio_table}')

   
    sql =f'''
        CREATE TABLE IF NOT EXISTS {bio_table} (
            localtime TEXT,
            timezone INTEGER,
            unix_timestamp INTEGER,
            acc_magnitude_avg REAL,
            eda_avg REAL,
            temp_avg REAL,
            movement_intensity INTEGER,
            steps_count INTEGER,
            rest INTEGER,
            on_wrist INTEGER
        )
    '''
    cursor.execute(sql)

    with open(summary_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            cursor.execute(f'''
                INSERT INTO {bio_table} VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (row[0], int(row[1]), int(row[2]), float(row[3]), float(row[4]),
                  float(row[5]), int(row[6]), int(row[7]), int(row[8]),
                  1 if row[9].lower() == 'true' else 0))
        # Commit the changes and close the connection

        conn.commit()
        conn.close()

    return True

select_file()

def query_db(db_file, bio_table, query):
     # Create database connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute query and fetch all results
    cursor.execute(f"SELECT {query} FROM {bio_table}")
    result = cursor.fetchall()

    # Close the connection
    conn.close()

    # Convert results to a list of tuples to a list of values
    return [item[0] for item in result]

def localtime_from_db(db_file, bio_table):
    global local_datetimes

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    
    # Create a cursor object
    cursor = conn.cursor()

    # Define a query that fetches datetime values
    query = f"SELECT localtime FROM {bio_table}"

    # Execute the query
    cursor.execute(query)

    # Fetch all results
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Extract and convert datetime values from UTC strings to datetime objects
    local_datetimes = [datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%SZ') for row in rows]
    
    # Convert datetime objects to strings in the correct format
    local_datetimes_str = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in local_datetimes]

    # Extract first and last datetime values
    global first_datetime
    global last_datetime

    first_datetime = local_datetimes[0]
    last_datetime = local_datetimes[-1]

    # Calculate the range of minutes
    minutes_range = int((last_datetime - first_datetime).total_seconds() / 60) + 1

    # Generate the datetime range
    localtime_range = [first_datetime + timedelta(minutes=x) for x in range(0, minutes_range)]

    # Convert datetime objects to strings
    localtime_strings = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in localtime_range]

    return localtime_strings

def utc_from_db(db_file, bio_table):
    global utc_datetimes

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    
    # Create a cursor object
    cursor = conn.cursor()

    # Define a query that fetches datetime values
    query = f"SELECT unix_timestamp FROM {bio_table}"

    # Execute the query
    cursor.execute(query)

     # Fetch all results
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    utc_timestamp_range = range(int(first_datetime.timestamp()), int(last_datetime.timestamp()), 60)
    utc_datetimes = [str(timestamp * 1000) for timestamp in utc_timestamp_range]

    return utc_datetimes

localtime_strings = localtime_from_db(db_file, bio_table)
utc_datetimes = utc_from_db(db_file, bio_table)

# Choose UTC or LOCAL
def update_time():
    global time_start
    global time_end
    if timeSelect.get() is True:
        time_start = start_localtime_combobox.get()
        time_end = end_localtime_combobox.get()
    else:
        time_start = start_utc_box.get()
        time_end = end_utc_box.get()

def next_graph(fig, canvas):

    global current_graph_index
    global graphsArray

    if current_graph_index < len(graphsArray) - 1:
        current_graph_index += 1  # Increment the index

        # Get the current graph
        current_graph = graphsArray[current_graph_index]

        # Clear the existing plot
        fig.clear()

        # Create a subplot in the figure
        ax = fig.add_subplot(111)
       

# Choose UTC or LOCAL 
def update_time():
    global time_start
    global time_end
    if (timeSelect.get()) is True:
        time_start = start_localtime_combobox.get()
        time_end = end_localtime_combobox.get()
    else:
        time_start = start_utc_box.get()
        time_end = end_utc_box.get()

# Download graph
def download_graph(fig, canvas, popup_window):
    save_path = filedialog.asksaveasfilename(defaultextension=".png")
    if save_path:
        fig.savefig(save_path)
        messagebox.showinfo("Download", "Graph Downloaded Successfully", parent=popup_window)

# Line graph
def plot_line_graph(fig, canvas):
    # Clear the existing plot
    fig.clear()

    # Get the current graph
    current_graph = graphsArray[current_graph_index]

    # Create a subplot in the figure
    ax = fig.add_subplot(111)
    ax.plot(xaxis, current_graph.columnData[startIndex:endIndex+1])
    ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
    ax.set_xticks(xaxis_subset)
    ax.set_xticklabels(xaxis_subset, rotation=15)
    ax.set_ylabel(current_graph.units)
    canvas.draw()

# Histogram
def plot_histogram(fig, canvas):
    # Clear the existing plot
    fig.clear()

    # Get the current graph
    current_graph = graphsArray[current_graph_index]

    # Create a subplot in the figure
    ax = fig.add_subplot(111)
    ax.hist(current_graph.columnData[startIndex:endIndex+1], bins=10)  # Adjust the number of bins as needed
    ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
    ax.set_xlabel(current_graph.units)
    ax.set_ylabel("Frequency")
    canvas.draw()

# Bar graph
def plot_bar_graph(fig, canvas):
    # Clear the existing plot
    fig.clear()

    # Get the current graph
    current_graph = graphsArray[current_graph_index]

    # Create a subplot in the figure
    ax = fig.add_subplot(111)
    ax.bar(xaxis, current_graph.columnData[startIndex:endIndex+1])
    ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
    ax.set_xticks(xaxis_subset)
    ax.set_xticklabels(xaxis_subset, rotation=15)
    ax.set_ylabel(current_graph.units)
    canvas.draw()

# Scatter plot
def plot_scatter_plot(fig, canvas):
    # Clear the existing plot
    fig.clear()

    # Get the current graph
    current_graph = graphsArray[current_graph_index]

    # Create a subplot in the figure
    ax = fig.add_subplot(111)
    ax.scatter(xaxis, current_graph.columnData[startIndex:endIndex+1])
    ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
    ax.set_xticks(xaxis_subset)
    ax.set_xticklabels(xaxis_subset, rotation=15)
    ax.set_ylabel(current_graph.units)
    canvas.draw()

# CREATE GRAPHS!!!
def get_index(datetime_list, datetime_str):
    try:
        return datetime_list.index(datetime_str)
    except ValueError:
        return -1

def create_graphs(db_file):
    update_time()
    global xaxis
    global xaxis_subset
    global current_graph_index  # Reset the current_graph_index to 0 each time the popup window is opened
    current_graph_index = 0

    popup_window = tk.Toplevel()  # Create a new popup window
    popup_window.title("Popup Window")
    popup_window.attributes("-fullscreen", True)
    popup_window.geometry("300x200")  # Set the size of the popup window

    # Create toolbar
    toolbar = tk.Frame(popup_window, bg="gray")
    toolbar.pack(side=tk.TOP, fill=tk.X, expand=True)  # Use fill=tk.X and expand=True

    exit_button = tk.Button(toolbar, text="    X    ", command=popup_window.destroy)
    exit_button.pack(side=tk.RIGHT)

    global startIndex
    global endIndex
    global timeSelect

    
    if timeSelect.get() is True:

         if time_start and time_end:
            pass
         else:
             messagebox.showerror("Error", "Please select a valid time interval.") #Vinny Change
             return

         localtime_string_start = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
         localtime_string_end = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

         timelist = localtime_from_db(db_file, bio_table)

         startIndex = get_index(timelist, localtime_string_start)
         endIndex = get_index(timelist, localtime_string_end)

    else:
        utc_string_start = time_start
        utc_string_end = time_end

        timelist = utc_from_db(db_file, bio_table)

        startIndex = get_index(timelist, utc_string_start)
        endIndex = get_index(timelist, utc_string_end)

        if time_start and time_end:
            pass
        else:
             messagebox.showerror("Error", "Please select a valid time interval.") #Vinny Change
             return
        
    try:
        xaxis = timelist[startIndex:endIndex+1]
    except:
        messagebox.showerror("Error", "Please select a valid time interval.") #Vinny Change
        return
    
    if time_start > time_end: #Vinny Change
        messagebox.showerror("Error", "Please select a valid time period with the start time coming before the end time.")
        return

    # button that displays the stats
    stat_button = tk.Button(toolbar, command=lambda: performStats(graphsArray, startIndex, endIndex), text="Perform Statistics")
    stat_button.pack(side=tk.LEFT)

    if (endIndex - startIndex == 1):
        num_ticks = 2 
        xaxis_subset = [xaxis[0], xaxis[-1]]
    else:
        num_ticks = 5

        # Calculate the step size for tick marks
        step_size = max(len(xaxis) // num_ticks,1)


        # Create a subset of xaxis with evenly spaced indices
        xaxis_subset = xaxis[::step_size]

    
    class GraphColumn:
        def __init__(self, title, column_name, display, units, db_file, bio_table):
            self.title = title
            self.display = display
            self.units = units
            self.columnData = column_from_db(db_file, bio_table, column_name)  # We change localtime_from_db to column_from_db as we want to get specific columns not only time

    def column_from_db(db_file, bio_table, column_name):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        result = cursor.execute(f"SELECT {column_name} FROM {bio_table}").fetchall()
        conn.close()
        return [i[0] for i in result]  # Return list of values in the column

    # Change your graph initialization
    acc = GraphColumn("Magnitude of Acceleration", "acc_magnitude_avg", bool_1.get(), "Meters per second squared (m/s^2)", db_file, bio_table)
    eda = GraphColumn("Average EDA", "eda_avg", bool_2.get(), "Microsiemens (uS)", db_file, bio_table)
    temp = GraphColumn("Average Temperature", "temp_avg", bool_3.get(), "Celsius (oC)", db_file, bio_table)
    move = GraphColumn("Movement", "movement_intensity", bool_4.get(), "Units of Movement", db_file, bio_table)
    step = GraphColumn("Step Count", "steps_count", bool_5.get(), "# of Steps", db_file, bio_table)
    rest = GraphColumn("Rest Interval", "rest", bool_6.get(), "Units of Rest", db_file, bio_table)

    # Create a frame to hold the navigation buttons
    button_frame = tk.Frame(popup_window, bg="gray")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    columnArray = [acc, eda, temp, move, step, rest]
    global graphsArray
    graphsArray = [graph for graph in columnArray if graph.display]

    # Create a figure and four subplots
    fig = Figure(figsize=(10, 8))

    for entry in (column_from_db(db_file, bio_table, "on_wrist"))[startIndex:endIndex+1]:
        if not entry:
            messagebox.showwarning("Warning", "During the selected time interval, the device was not ON WRIST for the entire duration. Data may not be entirely accurate.")
            break
        else:
            pass

    try:
        for entry in graphsArray[current_graph_index].columnData[startIndex:endIndex]:
            if not entry:
                break
    except:
        messagebox.showerror("Error", "Please select one or more parameters.") #Vinny Change
        return

    # Get the current graph
    if len(graphsArray) > 0:
        current_graph = graphsArray[current_graph_index]
        ax = fig.add_subplot(111)
        ax.plot(xaxis, current_graph.columnData[startIndex:endIndex+1])
        ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
        ax.set_xticks(xaxis_subset)
        ax.set_xticklabels(xaxis_subset, rotation=15)
        ax.set_ylabel(current_graph.units)

     #KATIE BETH CHANGE

    # Create a frame to hold the toolbar and navigation buttons below the graph
    toolbar_frame = tk.Frame(popup_window, bg="gray")
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Create a container frame to hold the canvas and toolbar_frame
    container_frame = tk.Frame(popup_window)
    container_frame.pack(fill=tk.BOTH, expand=True)

    # Create a frame to hold the canvas
    canvas_frame = tk.Frame(container_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    # Create the canvas inside the canvas_frame
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    #Create download button
    download_button = tk.Button(toolbar_frame, text="Download Graph", command=lambda: download_graph(fig, canvas, popup_window))
    download_button.pack(side=tk.LEFT, padx=10)

    # Create navigation buttons
    prev_button = tk.Button(toolbar_frame, text="Previous", command=lambda: previous_graph(fig, canvas))
    prev_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(toolbar_frame, text="Next", command=lambda: next_graph(fig, canvas))
    next_button.pack(side=tk.LEFT, padx=10)

    
    #KATIE BETH CHANGE
    # Create buttons for line graph, histogram, bar graph, and scatter plot
    line_button = tk.Button(toolbar_frame, text="Line Graph", command=lambda: plot_line_graph(fig, canvas))
    line_button.pack(side=tk.RIGHT, padx=10)
    histogram_button = tk.Button(toolbar_frame, text="Histogram", command=lambda: plot_histogram(fig, canvas))
    histogram_button.pack(side=tk.RIGHT, padx=10)
    bar_button = tk.Button(toolbar_frame, text="Bar Graph", command=lambda: plot_bar_graph(fig, canvas))
    bar_button.pack(side=tk.RIGHT, padx=10)
    scatter_button = tk.Button(toolbar_frame, text="Scatter Plot", command=lambda: plot_scatter_plot(fig, canvas))
    scatter_button.pack(side=tk.RIGHT, padx=10)

    popup_window.mainloop()

    # Create navigation buttons
    prev_button = tk.Button(toolbar_frame, text="Previous", command=lambda: previous_graph(fig, canvas))
    prev_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(toolbar_frame, text="Next", command=lambda: next_graph(fig, canvas))
    next_button.pack(side=tk.LEFT, padx=10)

    # Add the canvas to the Tkinter window
    canvas.get_tk_widget().pack()


def next_graph(fig, canvas):

    global current_graph_index
    global graphsArray

    if(current_graph_index < len(graphsArray)-1):
        current_graph_index += 1  # Increment the index

        # Get the current graph
        current_graph = graphsArray[current_graph_index]

        # Clear the existing plot
        fig.clear()

        # Create a subplot in the figure
        ax = fig.add_subplot(111)
        ax.plot(xaxis, current_graph.columnData[startIndex:endIndex+1])
        ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
        ax.set_xticks(xaxis_subset)
        ax.set_xticklabels(xaxis_subset, rotation=15)
        ax.set_ylabel(current_graph.units)
        canvas.draw()

def previous_graph(fig, canvas):
    global current_graph_index  # Declare as global
    global xaxis_subset

    if current_graph_index >= 1:
        current_graph_index -= 1  # Decrement the index
        current_graph = graphsArray[current_graph_index]

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(xaxis, current_graph.columnData[startIndex:endIndex+1])
        ax.set_title(current_graph.title, fontsize=10, fontweight='bold')
        ax.set_xticks(xaxis_subset)
        ax.set_xticklabels(xaxis_subset, rotation=15)
        ax.set_ylabel(current_graph.units)
        canvas.draw()

def performStats(graphsArray, startIndex, endIndex):

    #creating the window and its properties
    statswindow = tk.Toplevel()
    statswindow.title("Statistics Window")
    statswindow.geometry("1200x500") #size of window
    
    rows = 9
    statistics = ['Mean', 'Median', 'Min', 'Max', 'Standard Deviation', '25%', '75%', 'Point Count']

    # Create the new first column with the label "Statistics" and title row
    label = tk.Label(statswindow, text="Statistics", font=("Arial", 12, "bold"))
    label.grid(row=0, column=0, padx=10, pady=5)
    for j in range(len(graphsArray)):
        title_label = tk.Label(statswindow, text=graphsArray[j].title, font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=j+1, padx=10, pady=5)

    for i in range(1, rows):
        # Create Entry widgets for the statistics column
        label_text = statistics[i - 1]
        label = tk.Label(statswindow, text=label_text, font=("Arial", 12, "bold"))
        label.grid(row=i, column=0, padx=10, pady=5)

        for j in range(len(graphsArray)):
            if i == 1:
                # Display mean values for the data
                mean_val = np.mean(graphsArray[j].columnData[startIndex:endIndex + 1])
                mean_val = "{:.2f}".format(mean_val)  # Format to 2 decimal places
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, mean_val)
            elif i == 2:
                # Display median values for the data
                median_val = np.median(graphsArray[j].columnData[startIndex:endIndex + 1])
                median_val = "{:.2f}".format(median_val)  # Format to 2 decimal places
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, median_val)
            elif i == 3:
                # Display minimum values for the data
                min_val = np.min(graphsArray[j].columnData[startIndex:endIndex + 1])
                min_val = "{:.2f}".format(min_val)  # Format to 2 decimal places
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, min_val)
            elif i == 4:
                # Display maximum values for the data
                max_val = round(np.max(graphsArray[j].columnData[startIndex:endIndex + 1]), 2)
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, max_val)
            elif i == 5:
                # Display standard deviation for the data
                std_dev = round(np.std(graphsArray[j].columnData[startIndex:endIndex + 1]), 2)
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, std_dev)
            elif i == 6:
                # Display 25th percentile for the data
                percentile_25 = round(np.percentile(graphsArray[j].columnData[startIndex:endIndex + 1], 25), 2)
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, percentile_25)
            elif i == 7:
                # Display 75th percentile for the data
                percentile_75 = round(np.percentile(graphsArray[j].columnData[startIndex:endIndex + 1], 75), 2)
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, percentile_75)
            elif i == 8:
                # Display point count for the data
                point_count = len(graphsArray[j].columnData[startIndex:endIndex + 1])
                textbox = tk.Entry(statswindow, width=15, font=("Arial", 12))
                textbox.grid(row=i, column=j+1, padx=5, pady=5)
                textbox.insert(tk.END, point_count)

# Main Tkinter window
window = Tk()
window.attributes('-fullscreen', True)  # Set the window to fullscreen
window.configure(background="#D3DCED")

# Title label
title_label = tk.Label(window, text="Select Biometrics to Display", font=("ariel", 20), background="#D3DCED")

# Center the label across all six columns
title_label.grid(row=1, column=0, columnspan=6)

# Create toolbar
toolbar = tk.Frame(window, bg="gray")
toolbar.grid(row=0, column=0, columnspan=6, sticky=tk.W + tk.E)  # Span 6 columns

# Metadata buttons
meta_button = tk.Button(toolbar, text=" App Info ", command=open_metadata)
meta_button.grid(row=0, column=2, padx=5)

exit_button = tk.Button(toolbar, text="  X  ", command=window.destroy)
exit_button.grid(row=0, column=0, sticky=tk.E, padx=5)

# Boolean values
bool_1 = tk.BooleanVar()
bool_2 = tk.BooleanVar()
bool_3 = tk.BooleanVar()
bool_4 = tk.BooleanVar()
bool_5 = tk.BooleanVar()
bool_6 = tk.BooleanVar()

# Boolean check boxes
boolBox_1 = tk.Checkbutton(window, text="Magnitude of Acceleration", variable=bool_1, width=30, height=3, background="#D3DCED", anchor='w')
boolBox_2 = tk.Checkbutton(window, text="Average EDA", variable=bool_2, width=30, height=3, background="#D3DCED", anchor='w')
boolBox_3 = tk.Checkbutton(window, text="Average Temperature", variable=bool_3, width=30, height=3, background="#D3DCED", anchor='w')
boolBox_4 = tk.Checkbutton(window, text="Movement", variable=bool_4, width=30, height=3, background="#D3DCED", anchor='w')
boolBox_5 = tk.Checkbutton(window, text="Step Count", variable=bool_5, width=30, height=3, background="#D3DCED", anchor='w')
boolBox_6 = tk.Checkbutton(window, text="Rest Interval", variable=bool_6, width=30, height=3, background="#D3DCED", anchor='w')

# Check box grid alignment with padding
boolBox_1.grid(row=2, column=0, sticky='w', padx=(20, 0)) 
boolBox_2.grid(row=2, column=1, sticky='w', padx=(20, 0))  
boolBox_3.grid(row=3, column=0, sticky='w', padx=(20, 0))  
boolBox_4.grid(row=3, column=1, sticky='w', padx=(20, 0))  
boolBox_5.grid(row=4, column=0, sticky='w', padx=(20, 0))  
boolBox_6.grid(row=4, column=1, sticky='w', padx=(20, 0))  

global timeSelect
timeSelect = tk.BooleanVar()

# Radiobuttons
radio_button1 = tk.Radiobutton(window, text="UTC", variable=timeSelect, value=False)
radio_button1.grid(row=2, column=4)

radio_button2 = tk.Radiobutton(window, text="LOCAL TIME", variable=timeSelect, value=True)
radio_button2.grid(row=2, column=5)

# Radiobutton label
radio_label = tk.Label(window, text="Select Time Interval", font=("ariel", 10), background="#D3DCED")
radio_label.grid(row=2, column=3, padx=10)


# Combobox label
combo1_label = tk.Label(window, text="Select Start Time", font=("ariel", 10), background="#D3DCED")
combo1_label.grid(row=3, column=3, padx=10)
combo2_label = tk.Label(window, text="Select End Time", font=("ariel", 10), background="#D3DCED")
combo2_label.grid(row=4, column=3, padx=10)

# Combobox
start_localtime_combobox = ttk.Combobox(window, values=localtime_strings)
start_localtime_combobox.grid(row=3, column=4, columnspan=2)

end_localtime_combobox = ttk.Combobox(window, values=localtime_strings)
end_localtime_combobox.grid(row=4, column=4, columnspan=2)

start_localtime_combobox.bind("<<ComboboxSelected>>", lambda _: update_time())
end_localtime_combobox.bind("<<ComboboxSelected>>", lambda _: update_time())

start_utc_box = ttk.Combobox(window, values=utc_datetimes, background="#B4C9D6")
start_utc_box.grid(row=3, column=4)
end_utc_box = ttk.Combobox(window, values=utc_datetimes, background="#B4C9D6")
end_utc_box.grid(row=4, column=4)

start_utc_box.bind("<<ComboboxSelected>>", lambda _: update_time())
end_utc_box.bind("<<ComboboxSelected>>", lambda _: update_time())


def radio_button_changed():
    selection = timeSelect.get()
    if selection is not True:
        start_localtime_combobox.grid_remove()
        end_localtime_combobox.grid_remove()
        start_utc_box.grid(row=3, column=4, columnspan=2)  # Span two columns
        end_utc_box.grid(row=4, column=4, columnspan=2)    # Span two columns
    if selection is True:
        start_utc_box.grid_remove()
        end_utc_box.grid_remove()
        start_localtime_combobox.grid(row=3, column=4, columnspan=2)  # Span two columns
        end_localtime_combobox.grid(row=4, column=4, columnspan=2)    # Span two columns

# Set the initial values for comboboxes based on the radio button selection
radio_button_changed()

# Bind the radio button event handler to the radio variable
timeSelect.trace("w", lambda *args: radio_button_changed())

# Combobox labels
combo1_label = tk.Label(window, text="Select Start Time", font=("ariel", 10), background="#D3DCED")
combo1_label.grid(row=3, column=3, padx=10)
combo2_label = tk.Label(window, text="Select End Time", font=("ariel", 10), background="#D3DCED")
combo2_label.grid(row=4, column=3, padx=10)

# setting the title
window.title('Health Monitor')

# button that displays the plot
plot_button = Button(
    master=window,
    command=lambda: (database(csv_file, db_file, bio_table), create_graphs(db_file)),
    text="Plot Graphs",
    font=("ariel", 15),
    background="#B4C9D6"
)
plot_button.grid(row=5, column=1, columnspan=3, pady=10)

# Configure grid to make the toolbar and buttons span the entire width
for i in range(6):
    window.grid_columnconfigure(i, weight=1)

# run the main Tkinter loop
window.mainloop()