# ui/input_section.py

import customtkinter as ctk
from logic.parameters import input_sync

"""
 This function create a single input box, containing:
 Text label (units):   entry box      
-------------- Slider ---------- 
"""
def create_input(app, parent_frame, coil_idx, param_id):
    # Save the current parameter name and units in local variables
    param = app.in_parameters[param_id]
    unit = app.units[param_id]

    # Current app value from the dictionary keyed by (coil_idx, param_idx)
    value = app.values[(coil_idx, param_id)]

    # Create parent input box frame
    frame = ctk.CTkFrame(parent_frame, corner_radius=5, fg_color="transparent")

    # Create child text frame for label and entry box
    text_frame = ctk.CTkFrame(frame, fg_color="transparent")
    text_frame.pack(fill="x", padx=10, pady=5)

    label = ctk.CTkLabel(text_frame, text=f"{param} ({unit}):", font=("Arial", 16))
    label.pack(side="left", padx=(0, 5))

    entry = ctk.CTkEntry(
        text_frame,
        border_color="blue",
        width=70,
        font=("Arial", 16),
        justify="left"
    )
    entry.insert(0, str(value)) # Set the entry to the initial value
    entry.pack(side="right")

    # Create a second child frame for the slider
    slider = ctk.CTkSlider(frame, from_=0, to=app.top_values[param_id])
    slider.set(value) # Set the slider to the initial value
    slider.pack(pady=10, fill="x", padx=10)

    # This function updates the app when the slider is moved
    def on_slider(val):
        val = int(float(val))
        input_sync(app, coil_idx, param_id, val) # Sync of entry and app values

    # This function updates the app when an entry is input
    def on_entry(_):
        try:
            val = int(entry.get()) # Take the entry

            if val > app.top_values[param_id]:  # update max if new value exceeds previous
                app.show_message(f"New max for {param}: {val}")
                app.top_values[param_id] = val # Store the new top value
                for column_id in range(app.in_columns):
                    # Update the top value in all slider of this parameter
                    app.inputs[(column_id, param_id)]["slider"].configure(to=val)

            input_sync(app, coil_idx, param_id, val) # Sync of entry and app values
            app.focus() # Move the cursor out of the entry

        except ValueError:
            # If entry isn't valid
            entry.delete(0, "end") # The current entry is deleted
            entry.insert(0, str(app.values[(coil_idx, param_id)])) # The stored app value is typed in the entry

    slider.configure(command=on_slider) # When the slider is moved the function is called
    entry.bind("<Return>", on_entry) # When the enter key is pressed in the entry the funciton is called
    entry.bind("<KP_Enter>", on_entry) # Same with keypad enter

    # Return the created input frame so that can be placed where needed and relative input so to be stored
    return frame, slider, entry


def create_coil_sections(app):
    # Creates a frame for each coil column.
    for coil_id in range(app.in_columns):
        app.input_container.grid_columnconfigure(coil_id + 1, weight=1)

        coil_frame = ctk.CTkFrame(app.input_container, corner_radius=10, fg_color="transparent")
        coil_frame.grid(row=0, column=coil_id + 1, sticky="news", padx=2.5)
        coil_frame.grid_columnconfigure(0, weight=1)

        # If the control is coil-based a title is added for each column
        if app.control_method == "Coil-based":
            title = ctk.CTkLabel(coil_frame, text=f"COIL {coil_id + 1}", font=("Arial", 18, "bold"))
            title.grid(row=0, column=0, pady=(10, 5), sticky="new")

        for param_idx in range(len(app.in_parameters)):
            # For each column are created a number of input box equal to the number of parameters.
            coil_frame.grid_rowconfigure(param_idx + 1, minsize=80)
            frame, slider, entry = create_input(app, coil_frame, coil_id, param_idx)
            frame.grid(row=param_idx + 1, column=0, sticky="new", padx=5)

            # The entry and slider object are saved in a dictionary to modify their values in the following.
            if not hasattr(app, "inputs"):
                app.inputs = {}
            app.inputs[(coil_id, param_idx)] = {"slider": slider, "entry": entry}
