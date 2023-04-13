import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import simpledialog
import pandas as pd

def map_values(x_min, x_max, y_min, y_max, x, y):
    mapped_x = (x - x_min) * 100 / (x_max - x_min)
    mapped_y = 100 - (y - y_min) * 100 / (y_max - y_min)
    return mapped_x, mapped_y

def unmap_values(x_min, x_max, y_min, y_max, mapped_x, mapped_y):
    x = mapped_x * (x_max - x_min) / 100 + x_min
    y = (100 - mapped_y) * (y_max - y_min) / 100 + y_min
    return x, y

def map(x, y):
    mapped_x, mapped_y = map_values(20, 1170, 20, 590, x, y)
    return round(mapped_x), round(mapped_y)

def unmap(map_x, map_y):
    x, y = unmap_values(20, 1170, 20, 590, map_x, map_y)
    return round(x), round(y)

class TextBox:
    def __init__(self, index, importance, urgency, text, due_date):
        self.importance = importance
        self.urgency = urgency
        self.x, self.y = unmap(self.importance, self.urgency)
        self.index = index + 1
        self.text = text
        self.selected = False
        self.deleted = False
        self.due_date = due_date

    def draw(self, canvas):
        # Create a canvas with a white background
        self.canvas = canvas
        self.canvas.place(x=self.x, y=self.y)
        # Create a text box with IBM Plex Sans font and fill it with the provided text
        font_style = font.Font(family='IBM Plex Sans', size=12)
        self.text_box = tk.Text(canvas, width=10, height=5, font=font_style, bg="white", bd=0, highlightthickness=0, wrap="word")
        self.text_box.insert(tk.END, self.text)
        self.text_box.pack(padx=5, pady=5)
        self.tag = canvas.create_text(self.x, self.y, anchor="nw", text=self.text)
        # Bind mouse events to the text box
        self.text_box.bind("<Button-1>", self.on_click)
        self.text_box.bind("<B1-Motion>", self.on_drag)
        self.text_box.bind("<Double-Button-1>", self.delete_box)
        self.on_click(None)  # Call on_click method to select the text box

    def on_click(self, event):
        self.selected = True
        if event:
            self.mouse_x = event.x
            self.mouse_y = event.y

    def on_drag(self, event):
        if self.selected:
            delta_x = event.x - self.mouse_x
            delta_y = event.y - self.mouse_y

            # constrain x value to be between 20 and 1170
            if self.x + delta_x < 20:
                self.x = 20
            elif self.x + delta_x > 1170:
                self.x = 1170
            else:
                self.x += delta_x
            
            # constrain y value to be between 20 and 590
            if self.y + delta_y < 20:
                self.y = 20
            elif self.y + delta_y > 590:
                self.y = 590
            else:
                self.y += delta_y

            self.canvas.place(x=self.x, y=self.y)

            self.importance, self.urgency = map(self.x, self.y)
            #map_x, map_y = map(self.x, self.y)
            #self.text_box.delete("1.0", tk.END)
            #self.text_box.insert(tk.END, "({}, {})".format(self.importance, self.urgency))

    def _update_position(self):
        self.canvas.place(x=self.x, y=self.y)

    def update_text(self, new_text):
        self.text = new_text
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, self.text)

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self._update_position()

    def delete_box(self, event):
        result = messagebox.askquestion("Delete Box", "Are you sure you want to delete this box?", icon='warning')
        if result == "yes":
            self.deleted = True
            self.text_box.delete("1.0", tk.END)
            self.canvas.destroy()


def quadrant_click(event):
    # Get the location of the mouse click
    x, y = event.x_root, event.y_root
    importance, urgency = map(x,y)
    
    # Create a new Toplevel window for the dialog box
    dialog = tk.Toplevel(root)
    dialog.title("Create task")
    
    # Create a label and an entry widget for user input
    label = tk.Label(dialog, text="Describe the task:")
    entry = tk.Entry(dialog)
    
    # Place the label and entry widgets in the dialog box
    label.pack(side="left")
    entry.pack(side="left")
    
    # Create an OK button to close the dialog and retrieve the user input
    def ok():
        nonlocal dialog
        global box_canvas, text_boxes
        due_date = '2023-05-01'
        text = entry.get()
        index = len(box_canvas)
        if text:
            box_canvas.append(tk.Canvas(root, bg="white", width=200, height=200))
            # print(index, importance, urgency, text)
            text_boxes.append(TextBox(index, importance, urgency, text, due_date))
            text_boxes[-1].draw(box_canvas[-1])
            box_canvas[-1].focus_set()
        dialog.destroy()
        root.focus_force()  

    # Create a Cancel button to close the dialog without adding a task
    def cancel():
        nonlocal dialog
        dialog.destroy()
        root.focus_force()

    # Create an OK button to close the dialog and retrieve the user input
    ok_button = tk.Button(dialog, text="OK", command=ok)
    ok_button.pack(side="right")
    cancel_button = tk.Button(dialog, text="Cancel", command=cancel)
    cancel_button.pack(side="right")

    # Bind the Return key to the entry widget to simulate the OK button click
    def enter_pressed(event):
        ok_button.invoke()
    entry.bind('<Return>', enter_pressed)

    # Bind the Escape key to the cancel function
    def escape_pressed(event):
        cancel_button.invoke()
    dialog.bind('<Escape>', escape_pressed)
    
    # Set the geometry of the dialog box relative to the location of the mouse click
    dialog.geometry("+{}+{}".format(x, y))
    
    # Make the dialog box modal to prevent user interaction with the parent window
    dialog.grab_set()
    entry.focus_set()
    dialog.wait_window()

root = tk.Tk()
root.geometry("1280x720")
root.title("Eisenhower Matrix")

# Create four frames to hold the quadrants with larger font size
font_size = 25
font_style = font.Font(family='IBM Plex Sans', size=font_size, weight='bold')

urgent_important_frame = tk.Frame(root, bg="#0f62fe", width=640, height=360)
urgent_not_important_frame = tk.Frame(root, bg="#002d9c", width=640, height=360)
important_not_urgent_frame = tk.Frame(root, bg="#78a9ff", width=640, height=360)
not_important_not_urgent_frame = tk.Frame(root, bg="#001141", width=640, height=360)

# Use grid to position the frames in the window and fill the space
urgent_important_frame.grid(row=0, column=1, sticky="nsew")
urgent_not_important_frame.grid(row=0, column=0, sticky="nsew")
important_not_urgent_frame.grid(row=1, column=1, sticky="nsew")
not_important_not_urgent_frame.grid(row=1, column=0, sticky="nsew")

# Set equal weights for the rows and columns to make the quadrants fill the window
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Add labels to the frames with IBM Plex Sans Bold font
urgent_important_label = tk.Label(urgent_important_frame, text="Urgent and Important", bg="#0f62fe", fg="white", font=font_style)
urgent_important_label.pack(side=tk.BOTTOM, pady=10)

urgent_not_important_label = tk.Label(urgent_not_important_frame, text="Urgent but Not Important", bg="#002d9c", fg="white", font=font_style)
urgent_not_important_label.pack(side=tk.BOTTOM, pady=10)

important_not_urgent_label = tk.Label(important_not_urgent_frame, text="Important but Not Urgent", bg="#78a9ff", fg="white", font=font_style)
important_not_urgent_label.pack(side=tk.BOTTOM, pady=10)

not_important_not_urgent_label = tk.Label(not_important_not_urgent_frame, text="Not Urgent and Not Important", bg="#001141", fg="white", font=font_style)
not_important_not_urgent_label.pack(side=tk.BOTTOM, pady=10)

# Bind the quadrant_click function to the frames
urgent_important_frame.bind("<Button-1>", quadrant_click)
urgent_not_important_frame.bind("<Button-1>", quadrant_click)
important_not_urgent_frame.bind("<Button-1>", quadrant_click)
not_important_not_urgent_frame.bind("<Button-1>", quadrant_click)

'''
box_canvas1 = tk.Canvas(root, bg="white", width=200, height=200)
t1 = TextBox(10,10,"Some text")
t1.draw(box_canvas1)
box_canvas2 = tk.Canvas(root, bg="white", width=200, height=200)
t2 = TextBox(50,50,"Some more text that is different")
t2.draw(box_canvas2)
'''

def delete_deleted_textboxes(text_boxes, df):
    deleted_indices = []
    for i, text_box in enumerate(text_boxes):
        if text_box.deleted:
            deleted_indices.append(i)
            task_name = df.loc[i, 'Task Name']
            df.drop(i, inplace=True)
            # print(f"Deleted '{task_name}' task.")
    text_boxes = [text_box for i, text_box in enumerate(text_boxes) if i not in deleted_indices]



def load_tasks_from_csv(file_path):
    """
    Loads tasks DataFrame from a CSV file.

    Parameters:
        file_path (str): Path of the CSV file to load.

    Returns:
        pandas.DataFrame: DataFrame containing the tasks information.
    """
    try:
        df = pd.read_csv(file_path)
        # Check if DataFrame has required columns
        required_cols = set(['Task Name', 'Importance', 'Urgency', 'Due Date'])
        if not required_cols.issubset(set(df.columns)):
            raise ValueError("Missing required columns in CSV file.")
        # Check if all Importance and Urgency values are numeric
        if not pd.to_numeric(df['Importance'], errors='coerce').notnull().all():
            raise ValueError("Importance values should be numeric.")
        if not pd.to_numeric(df['Urgency'], errors='coerce').notnull().all():
            raise ValueError("Urgency values should be numeric.")
        return df
    except Exception as e:
        print(f"Error while loading tasks from CSV file: {str(e)}")
        return None


def save_tasks_to_csv(df, file_path):
    """
    Saves tasks DataFrame to a CSV file.

    Parameters:
        df (pandas.DataFrame): DataFrame containing the tasks information.
        file_path (str): Path of the CSV file to save.
    """
    try:
        # Check if DataFrame has required columns
        required_cols = set(['Task Name', 'Importance', 'Urgency', 'Due Date'])
        if not required_cols.issubset(set(df.columns)):
            raise ValueError("Missing required columns in DataFrame.")
        # Check if all Importance and Urgency values are numeric
        if not pd.to_numeric(df['Importance'], errors='coerce').notnull().all():
            raise ValueError("Importance values should be numeric.")
        if not pd.to_numeric(df['Urgency'], errors='coerce').notnull().all():
            raise ValueError("Urgency values should be numeric.")
        df.to_csv(file_path, index=False)
        # print(f"Tasks saved to CSV file: {file_path}")
    except Exception as e:
        print(f"Error while saving tasks to CSV file: {str(e)}")

df = load_tasks_from_csv('my_tasks.eis')

'''
# Define a DataFrame with task information
df = pd.DataFrame({
    'Task Name': ['Write a report', 'Book a call', 'Panic','Do a handstand'],
    'Importance': [80, 50, 70, 90],
    'Urgency': [90, 60, 40, 10],
    'Due Date': ['2023-05-01', '2023-05-15', '2023-04-30', '2023-04-30']
})
'''

def text_boxes_to_df(text_boxes):
    data = []
    for box in text_boxes:
        row = {'Task Name': box.text, 'Importance': box.importance, 'Urgency': box.urgency, 'Due Date': box.due_date}
        if not box.deleted:
            data.append(row)
    new_df = pd.DataFrame(data)
    return new_df

def save_eisenhower():
    # print("This function is triggered every minute.")
    delete_deleted_textboxes(text_boxes, df)
    my_df = text_boxes_to_df(text_boxes)
    save_tasks_to_csv(my_df, "my_tasks.eis")

def trigger_function():
    save_eisenhower()
    root.after(20000, trigger_function)  # 60000 milliseconds = 1 minute


# Create the TextBoxes from the DataFrame
# Define the function to create TextBoxes from a DataFrame

text_boxes = []
box_canvas = []
# Create a canvas for each task
for i, task in df.iterrows():
    box_canvas.append(tk.Canvas(root, bg="white", width=200, height=200))
    task_name = task['Task Name']
    importance = float(task['Importance'])
    urgency = float(task['Urgency'])
    due_date = task['Due Date']
    text = task_name
    text_boxes.append(TextBox(i, importance, urgency, text, due_date))
    text_boxes[i].draw(box_canvas[i])
    index = i + 1

root.after(20000, trigger_function)

# Start the main loop
root.mainloop()