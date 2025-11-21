import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync


def create_option_panel(app):
    app.option_container = ctk.CTkFrame(app, corner_radius=10, fg_color="transparent")
    app.option_container.pack(fill="both", expand=True, padx=5, pady=2.5)
    app.option_container.grid_rowconfigure(0, weight=1)
    app.option_container.grid_columnconfigure(0, weight=1)
    app.option_container.grid_columnconfigure(1, weight=1)
    option_frame = ctk.CTkFrame(app.option_container, corner_radius=10)
    option_frame.grid(row=0, column=0, sticky="nesw", padx=2.5)

    title_label = ctk.CTkLabel(option_frame, text="Options", font=("Arial", 18, "bold"))
    title_label.pack(padx=10, pady=5)

    app.top_reset_icon = ctk.CTkImage(Image.open("Images/max.png"), size=(25, 25))

    def reset_top_values():
        """
        Restores the original top values and updates slider limits.
        """
        app.top_values = app.top_values_orig.copy()

        for coil_index in range(app.num_coils):
            for param_index in range(len(app.parameters)):
                slider = app.inputs[(coil_index, param_index)]["slider"]
                slider.configure(to=app.top_values[param_index])

                if app.values[(coil_index, param_index)] > app.top_values[param_index]:
                    app.values[(coil_index, param_index)] = app.top_values[param_index]

                input_sync(app, coil_index, param_index)

        app.show_message("Top values reset to default")

    reset_top_button = ctk.CTkButton(
        option_frame,
        text="Top Value\nReset",
        text_color="black",
        font=("Arial", 14, "bold"),
        image=app.top_reset_icon,
        width=50,
        height=50,
        corner_radius=10,
        command=reset_top_values
    )
    reset_top_button.pack(padx=10, pady=10)

    # -------------------------------------------- Continuous Send Button -------------------------------------------
    sync_icon_image = Image.open("Images/sync.png")
    app.continuous_send_active = False

    continuous_send_button = ctk.CTkButton(
        option_frame,
        text="Continuous\nSend",
        text_color="black",
        font=("Arial", 14, "bold"),
        image=ctk.CTkImage(sync_icon_image, size=(25, 25)),
        width=50,
        height=50,
        corner_radius=10,
    )
    continuous_send_button.pack(padx=10, pady=10)

    continuous_send_button.rotation_angle = 0
    last_app_values_snapshot = {"app_data": None}

    def toggle_continuous_send():
        app.continuous_send_active = not app.continuous_send_active

        def rotate_button_icon():
            if not app.continuous_send_active:
                return

            rotated_image = sync_icon_image.rotate(continuous_send_button.rotation_angle)
            photo = ctk.CTkImage(rotated_image, size=(25, 25))
            continuous_send_button.configure(image=photo)
            continuous_send_button.rotation_angle = (continuous_send_button.rotation_angle - 10) % 360
            app.after(50, rotate_button_icon)

        def monitor_app_values():
            if not app.continuous_send_active:
                return

            current_app_values = app.values.copy()
            current_controller_values = app.controller.values.copy()

            # If the controller and app differ but sliders haven't moved → send app values to controller
            if (
                current_app_values != current_controller_values
                and current_app_values == last_app_values_snapshot["app_data"]
            ):
                app.controller.app_to_controller()
            else:
                last_app_values_snapshot["app_data"] = current_app_values

            app.after(100, monitor_app_values)

        if app.continuous_send_active:
            rotate_button_icon()
            monitor_app_values()

    continuous_send_button.configure(command=toggle_continuous_send)
