import customtkinter as ctk
from PIL import Image
from config import base_data
from logic.parameters import input_sync

def create_top_frame(app):
    """Creates an independent top bar inside a container frame."""

    # -----------------------------
    # Main container frame for top bar
    # -----------------------------
    # Make the top container span full width and allow column expansion
    app.columnconfigure(0, weight=1)
    app.top_container = ctk.CTkFrame(app, corner_radius=10)
    app.top_container.grid(row=0, column=0, sticky="ew", padx=5, pady=2.5)

    # Inner frame for button grid (transparent background)
    app.top_frame = ctk.CTkFrame(app.top_container, fg_color="transparent")
    app.top_frame.pack(fill="both", expand=True)

    # Configure independent 3-column grid inside the top frame
    app.top_frame.grid_columnconfigure(0, weight=1)
    app.top_frame.grid_columnconfigure(1, weight=1)
    app.top_frame.grid_columnconfigure(2, weight=1)

    # ==========================
    # STOP BUTTON
    # ==========================
    def create_stop_button():
        """Adds the STOP button to the independent top bar."""

        # Function to reset all app parameters to 0
        def reset_all_parameters():
            for coil_id in range(app.in_columns):
                for param_id in range(len(app.in_parameters)):
                    app.values[(coil_id, param_id)] = 0

            input_sync(app)  # Sync sliders/entries with updated values
            app.controller.app_to_controller()  # Send reset values to the controller

            # Verify that all values have been reset correctly
            for coil_id in range(app.in_columns):
                for param_id in range(len(app.in_parameters)):
                    if app.values[(coil_id, param_id)] != 0 or app.controller.values[(coil_id, param_id)] != 0:
                        app.show_message("Problem in resetting, stop the power manually!".upper(), 120)
                        return

            app.show_message("All parameters have been reset!")  # Notify user of successful reset

        # Load STOP button image and recolor it to white with alpha transparency
        original_img = Image.open("Images/stop.png").convert("RGBA")
        r, g, b, alpha = original_img.split()
        white_img = Image.new("RGBA", original_img.size, (255, 255, 255, 255))
        white_img.putalpha(alpha)
        stop_image = ctk.CTkImage(white_img, size=(40, 40))

        # Create the STOP button
        stop_button = ctk.CTkButton(
            app.top_frame,
            text="",
            fg_color="red",
            image=stop_image,
            width=50,
            height=50,
            corner_radius=10,
            command=reset_all_parameters
        )
        stop_button.grid(row=0, column=0, padx=10, pady=10, stick="w")  # Place left

    # ==========================
    # THEME (LIGHT/DARK) BUTTON
    # ==========================
    def create_theme_button():
        """Adds the Light/Dark mode button to the independent top bar."""

        # Load moon icon for light mode and sun icon for dark mode
        moon_image = ctk.CTkImage(
            light_image=Image.open("Images/moon.png"),
            dark_image=Image.open("Images/sun.png"),
            size=(30, 30)
        )

        # Function to toggle between light and dark mode
        def theme_changer():
            current_mode = ctk.get_appearance_mode()
            ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

        # Create the theme toggle button
        theme_button = ctk.CTkButton(
            app.top_frame,
            text="",
            image=moon_image,
            width=50,
            height=50,
            corner_radius=10,
            command=theme_changer
        )
        theme_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")  # Place right

    # ==========================
    # CONTROL METHOD SELECTION
    # ==========================
    def control_selection():
        """Adds a dropdown menu to select control method."""

        control_methods = ["Coil-based", "Sequence-based"]
        app.control_method = control_methods[0]  # Default selection

        # Function triggered when dropdown selection changes
        def selection_changed(choice):
            app.control_method = choice
            app.create_input_section()  # Recreate input section based on new method

        # Create the dropdown option menu
        dropdown = ctk.CTkOptionMenu(
            app.top_frame,
            text_color="black",
            font=("Arial", 16, "bold"),
            values=control_methods,
            command=selection_changed,
            width=150,
            height=30,
            corner_radius=10
        )
        dropdown.grid(row=0, column=1, padx=10, pady=10)  # Place in center column

    # ==========================
    # CALL THE TOP BAR ELEMENT CREATORS
    # ==========================
    create_stop_button()   # Add STOP button
    control_selection()    # Add control method dropdown
    create_theme_button()  # Add theme toggle button
