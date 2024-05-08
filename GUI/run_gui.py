import tkinter as tk
from tkinter import ttk
import os

def make_confidence_label_updater(index, label):
    """Create a lambda function that updates the label with the current scale value."""
    return lambda value: label.config(text=f"Confidence Level for Motor #{index + 1}: {int(float(value))}")

def submit(name_entry, subject_number_entry, strategy_text, confidence_scales):
    """Gather data from the UI and save it to a file."""
    name = name_entry.get()
    subject_number = subject_number_entry.get()
    strategy = strategy_text.get("1.0", tk.END).strip()
    confidences = [scale.get() for scale in confidence_scales]

    # Create folder if it doesn't exist
    folder_path = "responses"
    os.makedirs(folder_path, exist_ok=True)

    # Create and write to the file
    filename = f"response for subject number {subject_number}.txt"
    with open(os.path.join(folder_path, filename), 'w') as file:
        file.write(f"Name: {name}\n")
        file.write(f"Subject Number: {subject_number}\n")
        file.write(f"Strategy: {strategy}\n")
        for i, confidence in enumerate(confidences, start=1):
            file.write(f"Confidence Level for Motor #{i}: {int(confidence)} out of 10\n")

    print("Response saved successfully!")

def main():
    root = tk.Tk()
    root.title("Navigation Strategy Questionnaire")

    tk.Label(root, text="What's your name?").grid(row=0, column=0, padx=10, pady=10)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="What is your subject number?").grid(row=1, column=0, padx=10, pady=10)
    subject_number_entry = tk.Entry(root)
    subject_number_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="What strategy did you use to navigate?").grid(row=2, column=0, padx=10, pady=10)
    strategy_text = tk.Text(root, height=4, width=40)
    strategy_text.grid(row=2, column=1, padx=10, pady=10)

    # Create scales and labels for confidence levels dynamically
    confidence_scales = []
    confidence_labels = []
    for i in range(16):
        row = 3 + i
        tk.Label(root, text=f"Confidence level for Motor #{i + 1}:").grid(row=row, column=0, padx=10, pady=5)
        scale = ttk.Scale(root, from_=1, to=10, orient="horizontal")
        scale.grid(row=row, column=1, padx=10, pady=5)
        scale.set(5)  # Set default position of scale
        confidence_scales.append(scale)
        label = tk.Label(root, text=f"Confidence Level for Motor #{i + 1}: 5")
        label.grid(row=row, column=2, padx=10, pady=5)
        confidence_labels.append(label)
        scale['command'] = make_confidence_label_updater(i, label)

    # Submit button
    submit_btn = tk.Button(root, text="Submit", command=lambda: submit(name_entry, subject_number_entry, strategy_text, confidence_scales))
    submit_btn.grid(row=19, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
