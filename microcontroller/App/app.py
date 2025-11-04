import customtkinter as ctk
from PIL import Image
import input_options  # module with create_input
import theme

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Microcontroller App")
        self.geometry("1000x900+1000+200")
        self.text_window = None

        # === Variables ===
        self.num_coils = 4
        self.parameters = ["Current", "ON Time", "OFF Time", "Pause Time"]
        self.parameterUnits = ["mA", "ms", "ms", "ms"]
        self.top_values = [3000, 1000, 1000, 1000]

        # Main dictionary with IntVar for each parameter
        self.values = {
            coil_id: {param: ctk.IntVar(value=0) for param in self.parameters}
            for coil_id in range(self.num_coils)
        }

        # === Top frame with theme ===
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, columnspan=self.num_coils+1, sticky="ew")
        theme.create_theme_button(top_frame)

        # === Lock column on the left ===
        self.create_lock_column()

        # === Coil frames with sliders ===
        self.create_coil_options()

        # === Send button and temporary messages ===
        self.lower_frame()
        self.show_message("Welcome to the MSMA Microcontroller App!")

    def create_lock_column(self):
        self.grid_columnconfigure(0, weight=0)
        lock_frame = ctk.CTkFrame(self, corner_radius=10)
        lock_frame.grid(row=1, column=0, rowspan=len(self.parameters) + 1, sticky="n", padx=10, pady=10)

        title = ctk.CTkLabel(lock_frame, text="Lock", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, pady=(10, 5))

        # Store images as class attributes
        self.locked_image = ctk.CTkImage(Image.open("Images/locked.png"), size=(25, 25))
        self.unlocked_image = ctk.CTkImage(Image.open("Images/unlocked.png"), size=(25, 25))

        self.lock_states = [True] * len(self.parameters)

        for param_idx in range(len(self.parameters)):
            lock_frame.grid_rowconfigure(param_idx + 1, minsize=70)

            lock_button = ctk.CTkButton(
                lock_frame,
                text="",
                image=self.locked_image,
                width=50,
                height=50,
                corner_radius=10,
            )
            lock_button.grid(row=param_idx + 1, column=0, padx=10)

            # Update the command after creating the button
            lock_button.configure(command=lambda idx=param_idx, btn=lock_button: self.toggle_lock(idx, btn))

    def update_parameter(self, param_idx, new_value):
        """
        Updates the parameter param_idx for all coils if that parameter is locked.
        """
        if self.lock_states[param_idx]:
            param_name = self.parameters[param_idx]
            for coil_id in range(self.num_coils):
                self.values[coil_id][param_name].set(new_value)

    def toggle_lock(self, idx, button):
        self.lock_states[idx] = not self.lock_states[idx]
        if self.lock_states[idx]:
            button.configure(image=self.locked_image)
            self.update_parameter(idx, 0)
        else:
            button.configure(image=self.unlocked_image)

    def create_coil_options(self):
        # Coil columns (1..num_coils) expand horizontally
        for coil_id in range(self.num_coils):
            self.grid_columnconfigure(coil_id + 1, weight=1)

            coil_frame = ctk.CTkFrame(self, corner_radius=10)
            coil_frame.grid(row=1, column=coil_id + 1, sticky="new", padx=10, pady=10)

            # Internal column expands
            coil_frame.grid_columnconfigure(0, weight=1)

            # Coil title
            title = ctk.CTkLabel(coil_frame, text=f"COIL {coil_id + 1}", font=("Arial", 18, "bold"))
            title.grid(row=0, column=0, pady=(10, 5), sticky="ew")

            # Slider + entry for each parameter
            for param_idx in range(len(self.parameters)):
                coil_frame.grid_rowconfigure(param_idx+1, minsize=70)
                input_frame = input_options.create_input(coil_frame, self, coil_id, param_idx)
                input_frame.grid(row=param_idx + 1, column=0, sticky="ew", padx=5)

            # Coil row expands vertically if window grows
            self.grid_rowconfigure(1, weight=1)

    def show_message(self, msg, duration=6000):
        if self.text_window:
            self.text_window.configure(text=msg)
            self.after(duration, lambda: self.text_window.configure(text=""))

    def lower_frame(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=3, column=0, columnspan=self.num_coils+1, sticky="ew", padx=10, pady=10)

        # Label for temporary messages
        self.text_window = ctk.CTkLabel(bottom_frame, text="", font=("Arial", 16, "bold"))
        self.text_window.pack(fill="x", side="left", padx=10)

        # Send button
        send_image = ctk.CTkImage(Image.open("Images/send.png"), size=(25, 25))

        send_button = ctk.CTkButton(
            bottom_frame,
            text="Send",
            text_color="black",
            font=("Arial", 16, "bold"),
            image=send_image,
            compound="right",
            command=self.serial_print,
            width=100,
            height=50,
            corner_radius=10
        )
        send_button.pack(side="right", padx=10, pady=10)

    def serial_print(self):
        print("=== CURRENT VALUES ===")
        for coil_id in range(self.num_coils):
            print(f"COIL {coil_id + 1}:")
            for param in self.parameters:
                val = self.values[coil_id][param].get()
                print(f"  {param}: {val}")

# === Run app ===
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
