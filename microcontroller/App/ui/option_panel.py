import customtkinter as ctk
from logic.parameters import input_sync
from PIL import Image


def create_option_panel(app):
    option_frame = ctk.CTkFrame(app, corner_radius=10)
    option_frame.grid(row=2, column=app.num_coils, sticky="new", padx=10, pady=10)
    option_frame.grid_rowconfigure(2, weight=0)

    title = ctk.CTkLabel(option_frame, text="Options", font=("Arial", 18, "bold"))
    title.pack(padx=10, pady=(10, 5))

    app.top_reset_image = ctk.CTkImage(Image.open("Images/max.png"), size=(25, 25))

    def reset_top_values():
        """
        Restores the original top_values
        and updates slider limits.
        """
        # Restore the list
        app.top_values = app.top_values_orig.copy()

        # Update each slider for every parameter
        for coil_id in range(app.num_coils):
            for param_idx in range(len(app.parameters)):
                slider = app.inputs[(coil_id, param_idx)]["slider"]
                slider.configure(to=app.top_values[param_idx])

                if app.values[(coil_id, param_idx)] > app.top_values[param_idx]:
                    app.values[(coil_id, param_idx)] = app.top_values[param_idx]

                input_sync(app, coil_id, param_idx)

        app.show_message("Top values reset to default")

    orig_top_button = ctk.CTkButton(
        option_frame,
        text="Top value reset",
        image=app.top_reset_image,
        width=50,
        height=50,
        corner_radius=10,
        command=reset_top_values
    )
    orig_top_button.pack(padx=10, pady=10)
