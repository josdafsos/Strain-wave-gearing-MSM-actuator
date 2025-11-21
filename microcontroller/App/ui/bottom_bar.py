import customtkinter as ctk
from PIL import Image

def create_bottom_bar(app):
    """Send button + temporary message label."""
    app.bottom_container = ctk.CTkFrame(app, corner_radius=10)
    app.bottom_container.pack(side="bottom", fill="x", padx=5, pady=2.5)
    app.bottom_container.grid_rowconfigure(0, weight=0)

    # Text message area
    app.text_window = ctk.CTkLabel(app.bottom_container, text="", font=("Arial", 16, "bold"))
    app.text_window.pack(fill="x", side="left", padx=10)

    # Send button
    send_image = ctk.CTkImage(Image.open("Images/send.png"), size=(25, 25))

    send_button = ctk.CTkButton(
        app.bottom_container,
        text="Send",
        text_color="black",
        font=("Arial", 16, "bold"),
        image=send_image,
        compound="right",
        command=app.controller.app_to_controller,
        width=100,
        height=50,
    )
    send_button.pack(side="right", padx=10, pady=10)
