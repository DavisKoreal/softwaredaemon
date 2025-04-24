import tkinter as tk
from tkinter import messagebox

def submit():
    name = name_entry.get()
    age = age_entry.get()
    course = course_entry.get()
    messagebox.showinfo(\"Greeting\", f\"Hello {name}! You are {age} years old studying {course}.\")

root = tk.Tk()
root.title(\"Student Details\")
root.geometry(\"400x300\")

frame = tk.Frame(root)
frame.pack(pady=20, padx=40, fill=\"both\", expand=True)

label = tk.Label(frame, text=\"Enter Your Details\", font=(\"Arial\", 20))
label.pack(pady=12, padx=10)

name_entry = tk.Entry(frame)
name_entry.pack(pady=12, padx=10)
name_entry.insert(0, \"Name\")

age_entry = tk.Entry(frame)
age_entry.pack(pady=12, padx=10)
age_entry.insert(0, \"Age\")

course_entry = tk.Entry(frame)
course_entry.pack(pady=12, padx=10)
course_entry.insert(0, \"Course\")

button = tk.Button(frame, text=\"Submit\", command=submit)
button.pack(pady=12, padx=10)

root.mainloop()
