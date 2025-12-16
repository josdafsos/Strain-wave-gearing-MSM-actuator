import customtkinter as ctk
from PIL import Image

class SerialMonitor:
    def __init__(self, app):
        # Store reference to the main app
        self.app = app
        # Register this instance in the app for easy access
        self.app.serial_monitor = self

    # ==========================
    # OPEN SERIAL MONITOR WINDOW
    # ==========================
    def open_serial_monitor(self):
        # Create a new top-level window for the serial monitor
        self.serial_window = ctk.CTkToplevel(self.app)
        self.serial_window.title("Serial Monitor")
        x = self.app.x - 1100
        y = self.app.y
        self.serial_window.geometry(f"1100x600+{x}+{y}")  # Set size and position

        # Bind the close event to handle cleanup
        self.serial_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # ==========================
        # MAIN GRID CONFIGURATION
        # ==========================
        self.serial_window.grid_rowconfigure(0, weight=1)  # Output box row expands vertically
        self.serial_window.grid_rowconfigure(1, weight=0)  # Input row stays fixed
        self.serial_window.grid_columnconfigure(0, weight=1)  # Single column expands horizontally

        # ==========================
        # TEXT AREA (OUTPUT BOX)
        # ==========================
        self.output_box = ctk.CTkTextbox(
            self.serial_window,
            font=("Consolas", 15),
            state="disabled"  # Initially read-only
        )
        self.output_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        # ==========================
        # INPUT AREA (FOR SENDING)
        # ==========================
        input_frame = ctk.CTkFrame(self.serial_window)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)  # Entry expands horizontally

        # Load icon for the clear button
        clear_image = ctk.CTkImage(Image.open("Images/clear.png"), size=(20, 20))

        clear_button = ctk.CTkButton(
            input_frame,
            text="Clear",
            text_color="black",
            font=("Arial", 16, "bold"),
            image=clear_image,
            compound="left",  # Place image to the left of text
            width=90,
            height=30,
            command=self.clear_window
        )
        clear_button.grid(row=0, column=0, padx=(0, 5))

        # Entry widget for typing messages
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            font=("Consolas", 16)
        )
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.input_entry.focus()  # Focus cursor in the entry by default
        # Bind Enter key (main keyboard and keypad) to send message
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<KP_Enter>", self.send_message)

        # Load icon for the send button
        send_image = ctk.CTkImage(Image.open("Images/send.png"), size=(18, 18))

        # Send button next to the entry field
        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            text_color="black",
            font=("Arial", 16, "bold"),
            image=send_image,
            compound="right",  # Place image to the right of text
            width=90,
            height=30,
            command=self.send_message
        )
        send_button.grid(row=0, column=2, padx=(5, 0))

    # ==========================
    # CLOSE EVENT HANDLER
    # ==========================
    def on_close(self):
        # Remove reference from the main app
        self.app.serial_monitor = None
        # Destroy the serial monitor window
        self.serial_window.destroy()

    # ==========================
    # METHOD TO DISPLAY TEXT IN THE MONITOR
    # ==========================
    def add_text(self, text: str):
        # Normalize newlines for consistency
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.output_box.configure(state="normal")  # Make editable temporarily
        self.output_box.insert("end", text + "\n")  # Append text
        self.output_box.configure(state="disabled")  # Make read-only again
        self.output_box.see("end")  # Scroll to the bottom

    # ==========================
    # SEND MESSAGE
    # ==========================
    def send_message(self, event=None):
        text = self.input_entry.get().strip()  # Get trimmed text
        if text == "":
            return  # Ignore empty input
        self.app.controller.write(text)  # Send message to the controller
        answer = self.app.controller.last_message  # Optional: retrieve last response
        self.input_entry.delete(0, "end")  # Clear the input entry

    # ==========================
    # CLEAR WINDOW
    # ==========================
    def clear_window(self):
        self.output_box.configure(state="normal")  # Make editable
        self.output_box.delete("1.0", "end")  # Delete all text
        self.output_box.configure(state="disabled")  # Make read-only again

