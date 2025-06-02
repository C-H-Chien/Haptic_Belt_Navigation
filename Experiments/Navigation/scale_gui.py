import tkinter as tk
from tkinter import ttk
import os
import sys

def make_confidence_label_updater(question, label):
    """Create a lambda function that updates the label with the current scale value."""
    return lambda value: label.config(text=f"{int(float(value))} out of 7")

def submit_scaling(subID, experiment_type, confidence_scales, root):
    """Gather data from the UI, save it to a file, and close the application."""
    confidences = [scale.get() for scale in confidence_scales]

    # Create folder if it doesn't exist
    folder_path = "experiment_responses"
    os.makedirs(folder_path, exist_ok=True)

    # Create and write to the file
    filename = f"response_scale_{subID}_{experiment_type}.txt"
    with open(os.path.join(folder_path, filename), 'w') as file:
        file.write("Survey Responses:\n")
        questions = [
            "I could feel the vibrations clearly.",
            "I could match the vibrations to a direction in space.",
            "I thought my responses were accurate.",
            "It felt that the vibrations were located on my skin.",
            "It felt that the vibrations were located out in space."
        ]
        for question, confidence in zip(questions, confidences):
            file.write(f"{question} {int(confidence)} out of 7\n")

    print("Response saved successfully!")
    root.destroy()  # Close the window

def main_scaling(subID, experiment_type):
    root = tk.Tk()
    root.title("Tactile Belt Experiment Questionnaire - Scaling Questions")

    # Font configuration
    bold_large_font = ('Helvetica', 12, 'bold')

    # Introduction to scale questions with larger, bold font
    tk.Label(root, text="On a scale from 1 to 7, please indicate your response to the following questions:",
             font=bold_large_font).grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    tk.Label(root, text="1=Strongly disagree, 7=Strongly agree",
    font=bold_large_font).grid(row=1, column=1, columnspan=1, padx=10, pady=10)

    # Questions with scales
    questions = [
        "I could feel the vibrations clearly.",
        "I could match the vibrations to a direction in space.",
        "I thought my responses were accurate.",
        "It felt that the vibrations were located on my skin.",
        "It felt that the vibrations were located out in space."
    ]
    confidence_scales = []
    for i, question in enumerate(questions):
        row = 2 + i
        tk.Label(root, text=question).grid(row=row, column=0, padx=10, pady=5)
        scale = tk.Scale(root, from_=1, to=7, length=200, orient="horizontal")
        scale.grid(row=row, column=1, padx=10, pady=5)
        scale.set(4)  # Set default position of scale to the middle
        label = tk.Label(root, text=f"4 out of 7")
        #ticks_label = ttk.Label(root, text='1     2     3     4     5      6      7')
        #scale.pack(fill=X)
        label.grid(row=row, column=2, padx=10, pady=5)
        scale['command'] = make_confidence_label_updater(question, label)
        confidence_scales.append(scale)
        #ticks_label.grid(row=2, column=1, padx=10, pady=5)

    # Submit button
    submit_btn = tk.Button(root, text="Submit", command=lambda: submit_scaling(subID, experiment_type, confidence_scales, root))
    submit_btn.grid(row=8, columnspan=3, pady=20)

    root.mainloop()

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

    # Convert subject_id to integer if necessary
    try:
        subID = int(subID)
    except ValueError:
        print("Invalid Subject ID. Please enter a valid integer.")
        sys.exit(1)
    experiment_type = "impulse"

    main_scaling(subID, experiment_type)
