import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Student Info")
app.geometry("400x300")

frame = ctk.CTkFrame(master=app)
frame.pack(pady=20, padx=40, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="Enter Your Details", font=("Arial", 20))
label.pack(pady=12, padx=10)

name_entry = ctk.CTkEntry(master=frame, placeholder_text="Name")
name_entry.pack(pady=12, padx=10)

age_entry = ctk.CTkEntry(master=frame, placeholder_text="Age")
age_entry.pack(pady=12, padx=10)

course_entry = ctk.CTkEntry(master=frame, placeholder_text="Course")
course_entry.pack(pady=12, padx=10)

def submit():
    name = name_entry.get()
    age = age_entry.get()
    course = course_entry.get()
    result_label.configure(text=f"Hello {name}! You are {age} years old studying {course}.")

button = ctk.CTkButton(master=frame, text="Submit", command=submit)
button.pack(pady=12, padx=10)

result_label = ctk.CTkLabel(master=frame, text="", font=("Arial", 14))
result_label.pack(pady=12, padx=10)

app.mainloop()
