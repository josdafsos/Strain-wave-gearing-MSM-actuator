import customtkinter as ctk

class MethodWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Select Control Method")
        self.geometry("350x200+1100+300")
        self.resizable(False, False)
        self.method = None  # Result stored here

        # Center frame for layout consistency
        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = ctk.CTkLabel(
            frame,
            text="Choose the control mode:",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(10, 15))

        btn_individual = ctk.CTkButton(
            frame,
            text="Individual Coil Control",
            font=("Arial", 14),
            corner_radius=10,
            width=200,
            command=self.set_individual
        )
        btn_individual.pack(pady=6)

        btn_group = ctk.CTkButton(
            frame,
            text="Unified Control",
            font=("Arial", 14),
            corner_radius=10,
            width=200,
            command=self.set_group
        )
        btn_group.pack(pady=6)

        # Make this window modal → blocks interaction with the main UI
        self.grab_set()
        self.focus_force()

    def set_individual(self):
        """User selected individual control."""
        self.method = True
        self.destroy()

    def set_group(self):
        """User selected group control."""
        self.method = False
        self.destroy()
