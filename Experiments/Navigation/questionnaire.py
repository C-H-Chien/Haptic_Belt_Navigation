import tkinter as tk
import sys
import subprocess

# Function to create pop-up for entering SubjectID
def get_subject_id():
    def on_submit():
        nonlocal subject_id
        subject_id = entry.get()
        root.destroy()

    subject_id = None
    root = tk.Tk()
    tk.Label(root, text="Enter Subject ID:").pack(side="top", fill="x", padx=20, pady=10)
    entry = tk.Entry(root)
    entry.pack(padx=20, pady=20)
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(pady=10)
    root.mainloop()
    return subject_id


if __name__ == "__main__":
    subID = get_subject_id()
    if subID is None:
        print("No Subject ID provided.")
        sys.exit(1)

    subprocess.run(["python", "scale_gui.py", str(subID)])
    subprocess.run(["python", "fill_blank_gui.py", str(subID)])