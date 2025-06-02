import tkinter as tk
import os
import sys

def submit_fill_in(subID, experiment_type, strategy_text, other_observations_text, root):
    """Gather data from the UI, save it to a file, and close the application."""
    strategy = strategy_text.get("1.0", tk.END).strip()
    other_observations = other_observations_text.get("1.0", tk.END).strip()

    # Create folder if it doesn't exist
    folder_path = "experiment_responses"
    os.makedirs(folder_path, exist_ok=True)

    # Open the file and append the additional responses
    filename = f"response_text_{subID}_{experiment_type}.txt"
    with open(os.path.join(folder_path, filename), 'a') as file:
        file.write(f"Strategy Used: {strategy}\n")
        file.write(f"Other Observations: {other_observations}\n")

    print("Response saved successfully!")
    root.destroy()  # Close the window

def main_fill_in(subID, experiment_type):
    root = tk.Tk()
    root.title("Tactile Belt Experiment Questionnaire - Fill in the Blank")

    # Text entry for strategies and observations
    tk.Label(root, text="Did you use any particular strategy in making your \nresponses? If so, please describe that strategy.").grid(row=0, column=0, padx=10, pady=10)
    strategy_text = tk.Text(root, height=4, width=40)
    strategy_text.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Is there anything else you noticed about the \nexperiment that you would like to share?").grid(row=1, column=0, padx=10, pady=10)
    other_observations_text = tk.Text(root, height=4, width=40)
    other_observations_text.grid(row=1, column=1, padx=10, pady=10)

    # Submit button
    submit_btn = tk.Button(root, text="Submit", command=lambda: submit_fill_in(subID, experiment_type, strategy_text, other_observations_text, root))
    submit_btn.grid(row=2, columnspan=2, pady=20)

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
    main_fill_in(subID, experiment_type)
