# ui/lock_column.py

import customtkinter as ctk
from PIL import Image
from logic.parameters import toggle_lock

def create_lock_column(app):
    """
    Creates the left column with lock icons for each parameter.
    """
    lock_frame = ctk.CTkFrame(app.input_container, corner_radius=10, fg_color="transparent")
    lock_frame.grid(row=0, column=0, rowspan=len(app.in_parameters) + 1, sticky="ns", padx=2.5)
    app.input_container.grid_columnconfigure(0, weight=0)
    app.input_container.grid_rowconfigure(0, weight=1)

    title = ctk.CTkLabel(lock_frame, text="Lock", font=("Arial", 18, "bold"))
    title.grid(row=0, column=0, pady=(10, 5))

    # Load images once and store them in the app so they are not garbage collected
    app.locked_image = ctk.CTkImage(Image.open("Images/locked.png"), size=(25, 25))
    app.unlocked_image = ctk.CTkImage(Image.open("Images/unlocked.png"), size=(25, 25))

    # Track lock states (True = locked)
    app.lock_states = [True] * len(app.in_parameters)

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
