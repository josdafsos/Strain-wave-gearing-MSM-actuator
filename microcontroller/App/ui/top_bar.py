import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync
from ui.input_section import create_coil_sections
from config import base_data
from ui.lock_column import create_lock_column
from ui.bottom_bar import create_bottom_bar
from ui.option_panel import create_option_panel

def create_top_frame(app):
    """Creates the top bar and saves it in app.top_frame."""
    app.top_frame = ctk.CTkFrame(app)
    app.top_frame.grid(row=0, column=0, columnspan=app.num_coils+1, sticky="new", padx=10, pady=10)
    app.grid_rowconfigure(0, weight=0)

    # Allow internal columns to expand
    app.top_frame.grid_columnconfigure(0, weight=0)
    app.top_frame.grid_columnconfigure(1, weight=0)
    app.top_frame.grid_columnconfigure(2, weight=1)


def create_stop_button(app):
    """Adds the STOP button to the top bar."""
    def reset_all_parameters():
        for coil_id in range(app.num_coils):
            for param_id in range(len(app.parameters)):
                app.values[(coil_id, param_id)] = 0
        input_sync(app)
        app.serial_print()
        app.show_message("All parameters reset!")

    stop_image = ctk.CTkImage(Image.open("Images/stop.png"), size=(40, 40))

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
    stop_button.grid(row=0, column=0, padx=10, pady=10)


def create_theme_button(app):
    """Adds the Light/Dark mode button to the top bar."""
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
    theme_button.grid(row=0, column=2, padx=10, pady=10, stick="e")
