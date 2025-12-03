import customtkinter as ctk
from PIL import Image

class SerialMonitor:
    def __init__(self, app):
        self.app = app
        self.app.serial_monitor = self

    def open_serial_monitor(self):
        self.serial_window = ctk.CTkToplevel(self.app)
        self.serial_window.title("Serial Monitor")
        self.serial_window.geometry("1100x600+1000+200")

        # Bind the close event
        self.serial_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # ==========================
        # MAIN GRID CONFIGURATION
        # ==========================
        self.serial_window.grid_rowconfigure(0, weight=1)
        self.serial_window.grid_rowconfigure(1, weight=0)
        self.serial_window.grid_columnconfigure(0, weight=1)

        # ==========================
        # TEXT AREA (OUTPUT)
        # ==========================
        self.output_box = ctk.CTkTextbox(
            self.serial_window,
            font=("Consolas", 15),
            state="disabled"
        )
        self.output_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        # ==========================
        # INPUT AREA (FOR SENDING)
        # ==========================
        input_frame = ctk.CTkFrame(self.serial_window)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            font=("Consolas", 16)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.focus()
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<KP_Enter>", self.send_message)

        send_image = ctk.CTkImage(Image.open("Images/send.png"), size=(18, 18))

        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            text_color="black",
            font=("Arial", 16, "bold"),
            image=send_image,
            compound="right",
            width=90,
            height=30,
            command=self.send_message
        )
        send_button.grid(row=0, column=1)

    # ==========================
    # CLOSE EVENT HANDLER
    # ==========================
    def on_close(self):
        # Delete the reference in the app
        self.app.serial_monitor = None
        # Destroy the window
        self.serial_window.destroy()

    # ==========================
    # METHOD TO DISPLAY TEXT IN THE MONITOR
    # ==========================
    def add_text(self, text: str):
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.configure(state="disabled")
        self.output_box.see("end")

    # ==========================
    # SEND MESSAGE
    # ==========================
    def send_message(self, event=None):
        text = self.input_entry.get().strip()
        if text == "":
            return
        self.app.controller.write(text)
        answer = self.app.controller.last_message
        self.input_entry.delete(0, "end")
