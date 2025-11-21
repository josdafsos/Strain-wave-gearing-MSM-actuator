# app.py
# Main application class

import customtkinter as ctk
from logic.serial_controller import SerialController

from config import base_data
from ui.top_bar import create_top_frame, create_stop_button, create_theme_button, create_serial_monitor_button
from ui.lock_column import create_lock_column
from ui.bottom_bar import create_bottom_bar
from ui.input_section import create_coil_sections
from ui.option_panel import create_option_panel
from ui.preset_section import create_preset_window
# from ui.drop_down import create_drop_down


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Microcontroller App")
        self.geometry("1000x800+1000+200")

        self.control_method = True
        # Before building the UI, open the selection window
        # method_window = MethodWindow(self)
        # self.wait_window(method_window)  # Wait for the user to choose
        #
        # self.control_method = method_window.method

        # Message window reference
        self.text_window = None

        base_data(self)

        self.controller = SerialController(self)

        # create_drop_down(self)
        create_top_frame(self)  # creates only the top bar

        create_theme_button(self)
        create_serial_monitor_button(self)

        if self.control_method:  # individual coil
            create_lock_column(self)  # lock column UI

        create_coil_sections(self)  # sliders + entries for each coil
        create_option_panel(self)
        create_preset_window(self)
        create_bottom_bar(self)  # send button + message
        create_stop_button(self)
        #
        self.show_message("Welcome to the MSMA Microcontroller App!")

        self.controller.connect_to_device("/dev/ttyUSB0")

        # self.update_idletasks()  # Calculate the required size
        # self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

    def show_message(self, msg, duration=10000):
        """Displays temporary status messages."""
        if self.text_window:
            self.text_window.configure(text=msg)
            self.after(duration, lambda: self.text_window.configure(text=""))

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()
