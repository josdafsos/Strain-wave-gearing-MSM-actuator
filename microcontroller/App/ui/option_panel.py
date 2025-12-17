from copy import deepcopy
import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync
from .serial_monitor import SerialMonitor


def create_option_panel(app):
    # Configure row 2 of the main app to be expandable
    app.rowconfigure(2, weight=1)

    # Create the main option container frame for these button and the next presets buttons
    app.option_container = ctk.CTkFrame(app, corner_radius=10, fg_color="transparent")
    app.option_container.grid(row=2, column=0, sticky="news", padx=5, pady=2.5)
    app.option_container.grid_rowconfigure(0, weight=1)
    app.option_container.grid_columnconfigure(0, weight=1)
    app.option_container.grid_columnconfigure(1, weight=1)

    # Create the child frame inside the option container
    option_frame = ctk.CTkFrame(app.option_container, corner_radius=10)
    option_frame.grid(row=0, column=0, sticky="news", padx=2.5)

    # Allow the option panel columns to expand with the parent frame (option_container)
    option_frame.grid_columnconfigure(0, weight=1)
    option_frame.grid_columnconfigure(1, weight=0)
    option_frame.grid_columnconfigure(2, weight=0)
    option_frame.grid_columnconfigure(3, weight=1)

    # Keep items in central position
    option_frame.grid_rowconfigure(0, weight=1) # ----- Expandable row -----
    option_frame.grid_rowconfigure(1, weight=0) # Title
    option_frame.grid_rowconfigure(2, weight=0) # First buttons row
    option_frame.grid_rowconfigure(3, weight=0) # Second buttons row
    option_frame.grid_rowconfigure(4, weight=1) # ----- Expandable row -----

    # Title label for the options panel
    title_label = ctk.CTkLabel(option_frame, text="Options", font=("Arial", 18, "bold"), anchor="center")
    title_label.grid(padx=10, pady=5, column=1, row=1, columnspan=2, sticky="ew")

    # Load icon for the top values reset button
    app.top_reset_icon = ctk.CTkImage(Image.open(app.resource_path("Images/max.png")), size=(25, 25))

    # -------------------------------------------- Top Values Reset -------------------------------------------
    # Function to reset all top values to their original defaults
    def reset_top_values():
        app.top_values = app.top_values_orig.copy()  # Reset top values

        # Loop through all sliders and reset their maximum values
        for coil_index in range(app.in_columns):
            for param_index in range(len(app.in_parameters)):
                slider = app.inputs[(coil_index, param_index)]["slider"]
                slider.configure(to=app.top_values[param_index])

                # Ensure current value does not exceed new maximum
                if app.values[(coil_index, param_index)] > app.top_values[param_index]:
                    app.values[(coil_index, param_index)] = app.top_values[param_index]

                # Sync entries and internal values dictionary
                input_sync(app, coil_index, param_index)

        app.show_message("Top values reset to default")  # Notify user

    # Button to trigger top values reset
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
    reset_top_button.grid(padx=10, pady=10, row=2, column=1, sticky="news")

    # -------------------------------------------- Continuous Send Button -------------------------------------------
    sync_icon_image = Image.open(app.resource_path("Images/sync.png"))  # Load icon for continuous send
    app.continuous_send_active = False  # Track state of continuous send

    # Button for continuous sending of app values to the controller
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
    continuous_send_button.grid(padx=10, pady=10, row=3, column=1, sticky="news")

    # Initialize rotation state of the button icon
    continuous_send_button.rotation_angle = 0
    last_app_values_snapshot = {"app_data": None}  # Store last snapshot of app values

    # Function to toggle continuous send mode on/off
    def toggle_continuous_send():
        app.continuous_send_active = not app.continuous_send_active

        # Function to rotate the icon while continuous send is active
        def rotate_button_icon():
            if not app.continuous_send_active:
                return  # Stop rotation if disabled

            rotated_image = sync_icon_image.rotate(continuous_send_button.rotation_angle)
            photo = ctk.CTkImage(rotated_image, size=(25, 25))
            continuous_send_button.configure(image=photo)
            continuous_send_button.rotation_angle = (continuous_send_button.rotation_angle - 10) % 360
            app.after(50, rotate_button_icon)  # Repeat every 50ms

        # Function to monitor app values and send them if needed
        def monitor_app_values():
            if not app.continuous_send_active:
                return  # Stop monitoring if disabled

            current_app_values = app.values.copy()
            current_controller_values = app.controller.values.copy()

            # Send values if controller differs from app and the app is static (values are not changing)
            if (
                current_app_values != current_controller_values
                and current_app_values == last_app_values_snapshot["app_data"]
            ):
                app.controller.app_to_controller()
            else:
                last_app_values_snapshot["app_data"] = current_app_values

            app.after(100, monitor_app_values)  # Repeat every 100ms

        # Start rotation and monitoring if toggled on
        if app.continuous_send_active:
            rotate_button_icon()
            monitor_app_values()

    # Assign the toggle function to the button
    continuous_send_button.configure(command=toggle_continuous_send)

    # -------------------------------------------- Serial monitor button -------------------------------------------
    # Function to open or close the serial monitor window
    def open_close_serial_monitor():
        if hasattr(app, "serial_monitor") and app.serial_monitor is not None:
            app.serial_monitor.on_close()  # Close monitor if it exists
        else:
            SerialMonitor(app).open_serial_monitor()  # Open a new monitor

    # Function to create the serial monitor button
    def create_serial_monitor_button():
        """Adds a button to open the Serial Monitor."""
        monitor_image = ctk.CTkImage(Image.open(app.resource_path("Images/monitor.png")), size=(30, 30))

        serial_button = ctk.CTkButton(
            option_frame,
            text="Serial\nMonitor",
            text_color="black",
            font=("Arial", 14, "bold"),
            image=monitor_image,
            width=50,
            height=50,
            corner_radius=10,
            command=open_close_serial_monitor
        )
        serial_button.grid(padx=10, pady=10, row=2, column=2, sticky="news")

    # Create the serial monitor button
    create_serial_monitor_button()

    # -------------------------------------------- Reset controller values -------------------------------------------

    def reset_to_controller():
        app.values = deepcopy(app.controller.values)
        input_sync(app)

    def create_reset_to_controller_button():
        """Adds a button to reset the app values to the current controller values.."""
        board_image = ctk.CTkImage(Image.open(app.resource_path("Images/board.png")), size=(30, 30))

        serial_button = ctk.CTkButton(
            option_frame,
            text="Reset to\ncontroller",
            text_color="black",
            font=("Arial", 14, "bold"),
            image=board_image,
            width=50,
            height=50,
            corner_radius=10,
            command=reset_to_controller
        )
        serial_button.grid(padx=10, pady=10, row=3, column=2, sticky="news")

    # Create the serial monitor button
    create_reset_to_controller_button()