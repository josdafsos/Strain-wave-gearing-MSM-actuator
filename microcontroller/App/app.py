# app.py
# Main application class

import customtkinter as ctk


from config import base_data
from ui.top_bar import create_top_frame, create_stop_button, create_theme_button
from ui.lock_column import create_lock_column
from ui.bottom_bar import create_bottom_bar
from ui.input_section import create_coil_sections
from ui.option_panel import create_option_panel
from ui.method_selection import MethodWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Microcontroller App")
        self.geometry("1000x900+1000+200")
        self.control_method = True
        # Before building the UI, open the selection window
        # method_window = MethodWindow(self)
        # self.wait_window(method_window)  # Wait for the user to choose
        #
        # self.control_method = method_window.method

        # Message window reference
        self.text_window = None

        base_data(self)
        # === Layout ===
        create_top_frame(self)  # creates only the top bar


        create_theme_button(self)

        if self.control_method:  # individual coil
            create_lock_column(self)       # lock column UI


        create_coil_sections(self)    # sliders + entries for each coil
        create_option_panel(self)
        create_bottom_bar(self)       # send button + message
        create_stop_button(self)

        self.show_message("Welcome to the MSMA Microcontroller App!")



    def show_message(self, msg, duration=6000):
        """Displays temporary status messages."""
        if self.text_window:
            self.text_window.configure(text=msg)
            self.after(duration, lambda: self.text_window.configure(text=""))


    def serial_print(self):
        """This is where you will later send data to the microcontroller."""
        print("=== CURRENT VALUES ===")
        for coil_id in range(self.num_coils):
            print(f"COIL {coil_id + 1}:")
            for param_idx, param_name in enumerate(self.parameters):
                print(f"  {param_name}: {self.values[(coil_id, param_idx)]}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
