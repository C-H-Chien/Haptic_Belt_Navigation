import tkinter as tk
from tkinter import ttk
import os
import sys

def make_confidence_label_updater(question, label, font=14):
    """Create a lambda function that updates the label with the current scale value."""
    return lambda value: label.config(text=f"\n{int(float(value))}"+label['text'][2:], font=font)

def submit_scaling(subID, confidence_scales, root):
    """Gather data from the UI, save it to a file, and close the application."""
    confidences = [scale.get() for scale in confidence_scales]

    # Create folder if it doesn't exist
    folder_path = "experiment_responses"
    os.makedirs(folder_path, exist_ok=True)

    # Create and write to the file
    filename = f"response_scale_{subID}.txt"
    with open(os.path.join(folder_path, filename), 'w') as file:
        file.write("Survey Responses:\n")
        questions = [
            "I could feel the vibrations clearly.",
            "I could match the vibrations to a direction in space.",
            "I thought my responses were accurate.",
            "It felt that the vibrations were located on my skin.",
            "It felt that the vibrations were located out in space.",
            "I could feel a change in vibration when I got closer or farther away from the target.",
            "I thought the change in vibration improved my walking.",
            "I could sense the goal continuously while I was walking.",
            "I feel confident that I reached the intended goals.",
            "I think I found the best way to the goal.",
            "Navigating with vibrations became easier over time.",
            "The intensity of vibrations got weaker over time.",
            "How many different vibration patterns did you feel during the experiment?"
        ]
        for question, confidence in zip(questions, confidences):
            file.write(f"{question} {int(confidence)} out of 7\n")

    print("Response saved successfully!")
    root.destroy()  # Close the window

def main_scaling(subID):
    root = tk.Tk()
    root.title("Tactile Belt Experiment Questionnaire - Scaling Questions")

    # Font configuration
    bold_large_font = ('Arial', 16, 'bold')
    large_font = ('Arial', 16)

    # Introduction to scale questions with larger, bold font
    tk.Label(root, text="On a scale from 1 to 7, please indicate your answer by moving the slider",
             font=bold_large_font).grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    tk.Label(root, text="\t\t\t\t\t1 = Strongly disagree\t 7 = Strongly agree",
    font=bold_large_font).grid(row=1, column=0, columnspan=3)

    # Questions with scales
    questions = [
        "\nI could feel the vibrations clearly.",
        "\nI could match the vibrations to a direction in space.",
        "\nI thought my responses were accurate.",
        "\nIt felt that the vibrations were located on my skin.",
        "\nIt felt that the vibrations were located out in space.",
        "\nI could feel a change in vibration when I got \ncloser or farther away from the target.",
        "\nI thought the change in vibration improved my walking.",
        "\nI could sense the goal continuously while I was walking.",
        "\nI feel confident that I reached the intended goals.",
        "\nI think I found the best way to the goal.",
        "\nNavigating with vibrations became easier over time.",
        "\nThe intensity of vibrations got weaker over time.",
        "\nHow many different vibration patterns did you feel \nduring the experiment?"
    ]
    confidence_scales = []
    for i, question in enumerate(questions[:-1]):
        row = 2 + i
        tk.Label(root, text=question, font=large_font, justify="left").grid(row=row, column=0, padx=10, pady=5, sticky="W")
        scale = tk.Scale(root, from_=1, to=7, length=210, orient="horizontal", font=large_font)
        scale.grid(row=row, column=1, padx=0, pady=5, sticky="W")
        scale.set(4)  # Set default position of scale to the middle
        label = tk.Label(root, text=f"\n4 out of 7", font=large_font)
        #ticks_label = ttk.Label(root, text='1     2     3     4     5      6      7')
        #scale.pack(fill=X)
        label.grid(row=row, column=2, padx=10, pady=5, sticky="W")
        scale['command'] = make_confidence_label_updater(question, label, font=large_font)
        confidence_scales.append(scale)
        #ticks_label.grid(row=2, column=1, padx=10, pady=5)
    #last row with different scale
    question=questions[-1]
    row = 3 + i
    tk.Label(root, text=question, font=large_font, justify="left").grid(row=row, column=0, padx=10, pady=5, sticky="W")
    scale = tk.Scale(root, from_=1, to=4, length=120, orient="horizontal", font=large_font)
    scale.grid(row=row, column=1, padx=0, pady=5, sticky="W")
    scale.set(1)  # Set default position of scale to the middle
    label = tk.Label(root, text=f"\n1 out of 4", font=large_font)
    #ticks_label = ttk.Label(root, text='1     2     3     4     5      6      7')
    #scale.pack(fill=X)
    label.grid(row=row, column=2, padx=10, pady=5, sticky="W")
    scale['command'] = make_confidence_label_updater(question, label, font=large_font)
    confidence_scales.append(scale)

    # Submit button
    submit_btn = tk.Button(root, text="Submit",  font=large_font, command=lambda: submit_scaling(subID, confidence_scales, root))
    submit_btn.grid(row=15, columnspan=3, pady=20)

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
    
    if len(sys.argv) > 1:
        subID = sys.argv[1]
    else:
        subID = get_subject_id()
        if subID is None:
            print("No Subject ID provided.")
            sys.exit(1)

    main_scaling(subID)
