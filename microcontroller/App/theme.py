import customtkinter as ctk
from PIL import Image

def theme_changer():
    """Toggle between Light and Dark appearance modes."""
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

def create_theme_button(parent):
    """
    Create a button that toggles the app theme between Light and Dark.

    Args:
        parent: The parent frame or window where the button will be placed.
    """
    # Load images for both light and dark modes
    moon_image = ctk.CTkImage(
        light_image=Image.open("Images/moon.png"),  # for light mode
        dark_image=Image.open("Images/sun.png"),    # for dark mode
        size=(30, 30)
    )

    # Create the button
    theme_button = ctk.CTkButton(
        parent,
        text="",               # no text, just icon
        image=moon_image,
        command=theme_changer, # toggle the theme
        width=50,
        height=50,
        corner_radius=10
    )
    theme_button.pack(side="right", padx=10, pady=10)
