import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync
from ui.input_section import create_coil_sections
from config import base_data
from ui.lock_column import create_lock_column
from ui.bottom_bar import create_bottom_bar
from ui.option_panel import create_option_panel
from config import base_data

def create_top_frame(app):
    """Creates an independent top bar inside a container frame."""
    # Main container frame for the top bar (does not interfere with the main grid)
    app.columnconfigure(0, weight=1)
    app.top_container = ctk.CTkFrame(app, corner_radius=10)
    app.top_container.grid(row=0, column=0, sticky="ew", padx=5, pady=2.5)

    # Inner frame for the button grid
    app.top_frame = ctk.CTkFrame(app.top_container, fg_color="transparent")
    app.top_frame.pack(fill="both", expand=True)

    # Configure independent 3-column grid
    app.top_frame.grid_columnconfigure(0, weight=1)
    app.top_frame.grid_columnconfigure(1, weight=1)
    app.top_frame.grid_columnconfigure(2, weight=1)

    def create_stop_button():
        """Adds the STOP button to the independent top bar."""
        def reset_all_parameters():
            for coil_id in range(app.in_columns):
                for param_id in range(len(app.in_parameters)):
                    app.values[(coil_id, param_id)] = 0

            input_sync(app)
            app.controller.app_to_controller()

            for coil_id in range(app.in_columns):
                for param_id in range(len(app.in_parameters)):
                    if app.values[(coil_id, param_id)] != 0 or app.controller.values[(coil_id, param_id)] != 0:
                        app.show_message("Problem in resetting, stop the power manually!".upper(), 120)
                        return

            app.show_message("All parameters have been reset!")

        # Load and recolor the stop button to white
        original_img = Image.open("Images/stop.png").convert("RGBA")
        r, g, b, alpha = original_img.split()
        white_img = Image.new("RGBA", original_img.size, (255, 255, 255, 255))
        white_img.putalpha(alpha)
        stop_image = ctk.CTkImage(white_img, size=(40, 40))

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
        stop_button.grid(row=0, column=0, padx=10, pady=10, stick="w")


    def create_theme_button():
        """Adds the Light/Dark mode button to the independent top bar."""
        moon_image = ctk.CTkImage(
            light_image=Image.open("Images/moon.png"),
            dark_image=Image.open("Images/sun.png"),
            size=(30, 30)
        )

        def theme_changer():
            current_mode = ctk.get_appearance_mode()
            ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

        theme_button = ctk.CTkButton(
            app.top_frame,
            text="",
            image=moon_image,
            width=50,
            height=50,
            corner_radius=10,
            command=theme_changer
        )
        theme_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

    def control_selection():
        control_methods = ["Coil-based", "Sequence-based"]
        app.control_method = control_methods[0]

        def selection_changed(choice):
            app.control_method = choice
            app.create_input_section()

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
        dropdown.grid(row=0, column=1, padx=10, pady=10)


    create_stop_button()
    control_selection()
    create_theme_button()
