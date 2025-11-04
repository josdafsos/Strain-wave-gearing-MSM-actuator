import customtkinter as ctk
from PIL import Image

def theme_changer():
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

def create_theme_button(parent):

    moon_image = ctk.CTkImage(
        light_image=Image.open("Images/moon_icon.png"),
        dark_image=Image.open("Images/sun_icon.png"),
        size=(30, 30)
    )

    theme_button = ctk.CTkButton(
        parent,
        text="",
        image=moon_image,
        command=theme_changer,  # usa direttamente la funzione locale
        width=50,
        height=50,
        corner_radius=10
    )
    theme_button.pack(side="right", padx=10, pady=10)
