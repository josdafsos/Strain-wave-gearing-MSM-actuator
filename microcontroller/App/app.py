import customtkinter as ctk
from PIL import Image
import theme
import slider  # il modulo con la funzione create_slider

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Microcontroller App")
        self.geometry("900x900+1000+200")

        # === Variables ===
        self.num_coils = 4
        self.currents = [0] * self.num_coils

        # Liste widget
        self.coil_labels = []
        self.coil_entries = []
        self.coil_sliders = []

        # === Top frame con tema ===
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, columnspan=self.num_coils, sticky="ew")
        theme.create_theme_button(top_frame)

        # === Griglia colonne ===
        self.column_separation()

        # === Coil frames con slider ===
        self.create_all_coils()

        # === Send button ===
        self.create_send_button()

    def column_separation(self):
        for i in range(self.num_coils):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_all_coils(self):
        for i in range(self.num_coils):
            coil_frame = ctk.CTkFrame(self, corner_radius=10)
            coil_frame.grid(row=1, column=i, sticky="nsew", padx=10, pady=10)

            title = ctk.CTkLabel(coil_frame, text=f"COIL {i + 1}", font=("Arial", 18, "bold"))
            title.pack(pady=(10, 5))

            s = slider.create_slider(coil_frame, self, i)
            s.pack(pady=10, fill="x", padx=5)

    def create_send_button(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=3, column=0, columnspan=self.num_coils, sticky="ew")

        send_image = ctk.CTkImage(
            light_image=Image.open("Images/send_icon.png"),
            dark_image=Image.open("Images/send_icon.png"),
            size=(25, 25)
        )

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
        print("Currents:", self.currents)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
