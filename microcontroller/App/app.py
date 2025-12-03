# app.py
# Main application class

import customtkinter as ctk
import platform
from logic.serial_controller import SerialController

from config import base_data
from ui.top_bar import create_top_frame
from ui.lock_column import create_lock_column
from ui.bottom_bar import create_bottom_bar
from ui.input_section import create_coil_sections
from ui.option_panel import create_option_panel
from ui.preset_section import create_preset_window
# from ui.drop_down import create_drop_down


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.system = platform.system()

        self.title("Microcontroller App")
        self.geometry("1000x800+1000+200")

        # self.control_method = "Coil-based"

        # Message window reference
        self.text_window = None
        self._after_id = None

        self.controller = SerialController(self)

        # create_drop_down(self)
        create_top_frame(self)  # creates only the top bar

        self.create_input_section()

        create_option_panel(self)
        create_preset_window(self)

        create_bottom_bar(self)  # send button + message

        self.controller.connect_to_device("/dev/ttyUSB0")

        # self.update_idletasks()  # Calculate the required size
        # self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")


    def _clear_message(self):
        if self.text_window:
            self.text_window.configure(text="")
        self._after_id = None

    def show_message(self, msg, duration=10):
        if self.text_window:
            self.text_window.configure(text=msg)

            if self._after_id is not None:
                self.after_cancel(self._after_id)
                self._after_id = None

            self._after_id = self.after(duration*1000, self._clear_message)

    def create_input_section(self):
        if hasattr(self, "input_container"):
            self.input_container.destroy()

        self.input_container = ctk.CTkFrame(self, corner_radius=10)
        self.input_container.grid(row=1, column=0, sticky="ew", padx=5, pady=2.5)

        base_data(self)
        if self.control_method == "Coil-based":
            create_lock_column(self)
        create_coil_sections(self)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()
