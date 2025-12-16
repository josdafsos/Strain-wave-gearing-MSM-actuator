# app.py
# Main application class

import customtkinter as ctk
import platform
from logic.serial_controller import SerialController
from config import base_data
import ui


class App(ctk.CTk):
    """
    Main application window for microcontroller control.

    Attributes:
        system (str): Operating system name (Windows, Linux, etc.).
        text_window (CTkLabel or similar): Temporary message display widget.
        _after_id (int): ID of the scheduled after() event for clearing messages.
        controller (SerialController): Handles communication with the microcontroller.
        input_container (CTkFrame): Container for the coil/sequence input section.
    """
    def __init__(self):
        super().__init__()

        # Detect operating system
        self.system = platform.system()

        # Configure main window
        self.title("Microcontroller App")

        # Window dimensions
        window_width = 1000
        window_height = 800

        # Screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Identification center position
        self.x = (screen_width * 2 // 3 - window_width // 2)
        self.y = (screen_height // 2) - (window_height // 2)

        # Set windows position and dimensions
        self.geometry(f"{window_width}x{window_height}+{self.x}+{self.y}")

        # Initialize message system
        self.text_window = None
        self._after_id = None

        # Initialize serial controller for device communication
        self.controller = SerialController(self)

        # -----------------------------
        # UI SETUP
        # -----------------------------
        ui.create_top_frame(self)  # Creates only the top bar (stop button, dropdown, theme)

        self.create_input_section()  # Creates the main input section (coil or sequence)

        ui.create_option_panel(self)  # Options like Top Value Reset, Continuous Send
        ui.create_preset_window(self)  # Preset buttons

        ui.create_bottom_bar(self)  # Bottom bar with send button + message display

        # Attempt to connect to device at default port
        self.controller.connect_to_device("/dev/ttyUSB0")

    # -----------------------------
    # MESSAGE HANDLING
    # -----------------------------
    def _clear_message(self):
        """Clears the text message in the message window."""
        if self.text_window:
            self.text_window.configure(text="")
        self._after_id = None

    def show_message(self, msg, duration=10):
        """
        Displays a temporary message in the UI.

        Args:
            msg (str): Message to display.
            duration (int): Time in seconds before message is cleared.
        """
        if self.text_window:
            self.text_window.configure(text=msg)

            # Cancel any previously scheduled clear
            if self._after_id is not None:
                self.after_cancel(self._after_id)
                self._after_id = None

            # Schedule message clearing
            self._after_id = self.after(duration*1000, self._clear_message)

    # -----------------------------
    # INPUT SECTION CREATION
    # -----------------------------
    def create_input_section(self):
        """
        Creates or refreshes the main input section for coils or sequences.

        - Destroys previous container if it exists.
        - Calls base_data() to populate default parameters.
        - Adds lock column if control method is "Coil-based".
        - Creates coil sections (sliders, entries, etc.).
        """
        if hasattr(self, "input_container"):
            self.input_container.destroy()  # Remove old input section

        # Main container frame for input section
        self.input_container = ctk.CTkFrame(self, corner_radius=10)
        self.input_container.grid(row=1, column=0, sticky="ew", padx=5, pady=2.5)

        # Populate base data (default parameters, top values, etc.)
        base_data(self)

        # Add lock column if using coil-based control
        if self.control_method == "Coil-based":
            ui.create_lock_column(self)

        # Create the main coil/sequence sliders and entries
        ui.create_coil_sections(self)


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    # Set appearance mode and theme before launching app
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # Create the main app instance and start event loop
    app = App()
    app.mainloop()
