import tkinter as tk
from tkinter import ttk
import os

def make_confidence_label_updater(question, label):
    """Create a lambda function that updates the label with the current scale value."""
    return lambda value: label.config(text=f"{question}: {int(float(value))} out of 7")

def submit(name_entry, subject_number_entry, strategy_text, other_observations_text, confidence_scales, root):
    """Gather data from the UI, save it to a file, and close the application."""
    name = name_entry.get()
    subject_number = subject_number_entry.get()
    strategy = strategy_text.get("1.0", tk.END).strip()
    other_observations = other_observations_text.get("1.0", tk.END).strip()
    confidences = [scale.get() for scale in confidence_scales]

    # Create folder if it doesn't exist
    folder_path = "experiment_responses"
    os.makedirs(folder_path, exist_ok=True)

    # Create and write to the file
    filename = f"response_{subject_number}.txt"
    with open(os.path.join(folder_path, filename), 'w') as file:
        file.write(f"Name: {name}\n")
        file.write(f"Subject Number: {subject_number}\n")
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
        file.write(f"Strategy Used: {strategy}\n")
        file.write(f"Other Observations: {other_observations}\n")

    print("Response saved successfully!")
    root.destroy()  # Close the window

def main():
    root = tk.Tk()
    root.title("Vibration Sensation Experiment Questionnaire")

    # Font configuration
    bold_large_font = ('Helvetica', 12, 'bold')

    # Name and subject number
    tk.Label(root, text="What's your name?").grid(row=0, column=0, padx=10, pady=10)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Label(root, text="What is your subject number?").grid(row=1, column=0, padx=10, pady=10)
    subject_number_entry = tk.Entry(root)
    subject_number_entry.grid(row=1, column=1, padx=10, pady=10)

    # Introduction to scale questions with larger, bold font
    tk.Label(root, text="On a scale from 1 to 7 (1=Strongly disagree, 7=Strongly agree), please indicate your response to the following questions:",
             font=bold_large_font).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

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
        row = 3 + i
        tk.Label(root, text=question).grid(row=row, column=0, padx=10, pady=5)
        scale = ttk.Scale(root, from_=1, to=7, orient="horizontal")
        scale.grid(row=row, column=1, padx=10, pady=5)
        scale.set(4)  # Set default position of scale to the middle
        label = tk.Label(root, text=f"{question}: 4 out of 7")
        label.grid(row=row, column=2, padx=10, pady=5)
        scale['command'] = make_confidence_label_updater(question, label)
        confidence_scales.append(scale)

    # Text entry for strategies and observations
    tk.Label(root, text="Did you use any particular strategy in making your responses?").grid(row=8, column=0, padx=10, pady=10)
    strategy_text = tk.Text(root, height=4, width=40)
    strategy_text.grid(row=8, column=1, padx=10, pady=10)

    tk.Label(root, text="Is there anything else you noticed about the experiment?").grid(row=9, column=0, padx=10, pady=10)
    other_observations_text = tk.Text(root, height=4, width=40)
    other_observations_text.grid(row=9, column=1, padx=10, pady=10)

    # Submit button
    submit_btn = tk.Button(root, text="Submit", command=lambda: submit(name_entry, subject_number_entry, strategy_text, other_observations_text, confidence_scales, root))
    submit_btn.grid(row=10, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
