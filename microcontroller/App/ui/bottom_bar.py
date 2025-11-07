import customtkinter as ctk
from PIL import Image

def create_bottom_bar(app):
    """Send button + temporary message label."""
    bottom_frame = ctk.CTkFrame(app)
    bottom_frame.grid(row=3, column=0, columnspan=app.num_coils + 1, sticky="sew", padx=10, pady=10)
    app.grid_rowconfigure(3, weight=1)

    # Text message area
    app.text_window = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 16, "bold"))
    app.text_window.pack(fill="x", side="left", padx=10)

    # Send button
    send_image = ctk.CTkImage(Image.open("Images/send.png"), size=(25, 25))

    send_button = ctk.CTkButton(
        bottom_frame,
        text="Send",
        text_color="black",
        font=("Arial", 16, "bold"),
        image=send_image,
        compound="right",
        command=app.serial_print,
        width=100,
        height=50,
    )
    send_button.pack(side="right", padx=10, pady=10)
