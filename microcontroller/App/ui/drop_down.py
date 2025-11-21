import customtkinter as ctk

def create_drop_down(app):
    app.drop_down_container = ctk.CTkFrame(app, corner_radius=10)
    app.drop_down_container.pack(fill="x", padx=5, pady=2.5)

    # List of options
    options = ["Option 1", "Option 2", "Option 3"]

    # Function to capture the selected value
    def option_selection(value):
        print(f"You selected: {value}")

    drop_down = ctk.CTkOptionMenu(
        app.drop_down_container,
        values=options,            # correct
        command=option_selection,
        font=("Arial", 14, "bold"),
        text_color="black"
    )
    drop_down.pack(padx=5)

    # Set initial value
    drop_down.set(options[0])
