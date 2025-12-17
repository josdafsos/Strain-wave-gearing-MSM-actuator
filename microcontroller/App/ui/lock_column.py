# ui/lock_column.py

import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync

# This function is executed when the lock button is pressed
def toggle_lock(app, param_idx, button):
    # The lock state of the corresponding parameter is switched
    app.lock_states[param_idx] = not app.lock_states[param_idx]

    # If the coil are locked
    if app.lock_states[param_idx]:
        # The image is changed
        button.configure(image=app.locked_image)

        # All inputs of corresponding parameters are initialized to 0
        input_sync(app, 0, param_idx, 0)

    # If the parameters are unlocked the just the image is changed
    else:
        button.configure(image=app.unlocked_image)

def create_lock_column(app):
    """
    Creates the left column with lock icons for each parameter.
    """

    # Create the lock frame
    lock_frame = ctk.CTkFrame(app.input_container, corner_radius=10, fg_color="transparent")
    lock_frame.grid(row=0, column=0, rowspan=len(app.in_parameters) + 1, sticky="ns", padx=2.5)
    app.input_container.grid_columnconfigure(0, weight=0) # It can't expand horizontally
    app.input_container.grid_rowconfigure(0, weight=1) # It can expand vertically

    # The title is added
    title = ctk.CTkLabel(lock_frame, text="Lock", font=("Arial", 18, "bold"))
    title.grid(row=0, column=0, pady=(10, 5))

    # Load images once and store them in the app so they are not garbage collected
    app.locked_image = ctk.CTkImage(Image.open(app.resource_path("Images/locked.png")), size=(25, 25))
    app.unlocked_image = ctk.CTkImage(Image.open(app.resource_path("Images/unlocked.png")), size=(25, 25))

    # Track lock states (True = locked)
    app.lock_states = [True] * len(app.in_parameters)

    # Create the lock buttons
    for param_idx in range(len(app.in_parameters)):
        lock_frame.grid_rowconfigure(param_idx + 1, minsize=80)
        lock_button = ctk.CTkButton(
            lock_frame,
            text="",
            image=app.locked_image,
            width=50,
            height=50,
            corner_radius=10,
            command=lambda idx=param_idx, btn=None: toggle_lock(app, idx, btn)
        )
        lock_button.grid(row=param_idx + 1, column=0, padx=10)

        # Fix lambda closure after creation
        lock_button.configure(command=lambda idx=param_idx, btn=lock_button: toggle_lock(app, idx, btn))
