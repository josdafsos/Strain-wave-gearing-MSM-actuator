import customtkinter as ctk
from logic.parameters import input_sync
import time

def create_preset_window(app):
    # Create the main container for the Preset panel inside the option container
    preset_container = ctk.CTkFrame(app.option_container, corner_radius=10)
    preset_container.grid(row=0, column=1, sticky="news", padx=2.5)

    # Allow the preset panel to be centered horizontally
    preset_container.grid_columnconfigure(0, weight=1)
    preset_container.grid_columnconfigure(1, weight=0)
    preset_container.grid_columnconfigure(2, weight=1)

    # Keep items in central position
    preset_container.grid_rowconfigure(0, weight=1) # ----- Expandable row -----
    preset_container.grid_rowconfigure(1, weight=0) # Title
    preset_container.grid_rowconfigure(2, weight=0) # Button grid
    preset_container.grid_rowconfigure(3, weight=1) # ----- Expandable row -----


    # Title label for the Preset panel
    title_label = ctk.CTkLabel(preset_container, text="Presets", font=("Arial", 18, "bold"), anchor="center")
    title_label.grid(padx=10, pady=5, row=1, column=1, sticky="ew")

    # Define number of preset buttons in a grid
    num_columns = 4
    num_rows = 2

    # Container for holding all preset buttons
    buttons_container = ctk.CTkFrame(preset_container, corner_radius=10, fg_color="transparent")
    buttons_container.grid(row=2, column=1, sticky="news")

    # Grid frame inside buttons container for precise button placement
    buttons_grid = ctk.CTkFrame(buttons_container, corner_radius=10)
    buttons_grid.grid(row=0, column=0, sticky="nsew")

    # Precompute positions for buttons in a row x column grid
    buttons_pos = [(x, y) for x in range(num_rows) for y in range(num_columns)]

    # -------------------------------------------- Long Press Detection -------------------------------------------
    # Function to detect long press (≥1 second) to save the current app values into a preset
    def check_long_press(btn):
        if btn.is_pressed:
            duration = time.time() - btn.press_time  # Calculate press duration
            if duration >= 1:
                btn.value = app.values.copy()  # Save current values in the preset
                app.show_message(f"Preset {btn.id} saved with current values.")
                btn.is_pressed = False  # Prevent repeated saving
            else:
                # Check again after 50ms until long press threshold is reached
                btn.after(50, lambda: check_long_press(btn))

    # -------------------------------------------- Button Press/Release Events -------------------------------------------
    # Function to handle button press
    def on_press(event):
        btn = event.widget
        # Ascend to actual CTkButton in case the event originates from an inner canvas
        while not isinstance(btn, ctk.CTkButton):
            btn = btn.master
        btn.is_pressed = True
        btn.press_time = time.time()  # Record time of press
        check_long_press(btn)  # Start long press detection

    # Function to handle button release
    def on_release(event):
        btn = event.widget
        while not isinstance(btn, ctk.CTkButton):
            btn = btn.master
        if btn.is_pressed:
            duration = time.time() - btn.press_time
            if duration < 1:
                # Short press (<1s): apply the preset if it has saved values
                if btn.value:
                    app.values = btn.value.copy()
                    input_sync(app)
                    app.show_message(f"App values updated to preset {btn.id}.")
                else:
                    app.show_message(f"The preset option {btn.id} is empty!")
            btn.is_pressed = False  # Reset press state

    # -------------------------------------------- Create Preset Buttons -------------------------------------------
    for i, (row, col) in enumerate(buttons_pos):
        btn = ctk.CTkButton(
            buttons_grid,
            text=f"{i+1}",
            text_color="black",
            font=("Arial", 18, "bold"),
            width=50,
            height=50,
            corner_radius=10
        )
        btn.id = str(i + 1)  # Assign preset ID
        btn.value = None  # Initialize preset as empty
        btn.is_pressed = False  # Track long press state
        btn.grid(row=row, column=col, padx=10, pady=10)

        # Bind mouse events to handle press and release
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    # -------------------------------------------- Apply Preset by ID -------------------------------------------
    # Function to apply a preset based on its button ID
    def apply_preset_by_id(preset_id):
        for btn in buttons_grid.winfo_children():
            if getattr(btn, "id", None) == str(preset_id):
                if btn.value:
                    app.values = btn.value.copy()
                    input_sync(app)
                    app.show_message(f"The preset option {btn.id} has been applied!")
                else:
                    app.show_message(f"The preset option {btn.id} is empty!")
                break

    # -------------------------------------------- Keyboard Shortcuts for Presets -------------------------------------------
    # Bind Control+1..Control+8 to apply corresponding presets
    def bind_presets_shortcuts():
        for i in range(1, num_rows * num_columns + 1):
            app.bind_all(f"<Control-Key-{i}>", lambda event, preset_id=i: apply_preset_by_id(preset_id))

    # Call the shortcut binding function after creating all buttons
    bind_presets_shortcuts()
