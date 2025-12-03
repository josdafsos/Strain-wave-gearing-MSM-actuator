import customtkinter as ctk
from PIL import Image
from logic.parameters import input_sync
import time

def create_preset_window(app):
    preset_container = ctk.CTkFrame(app.option_container, corner_radius=10)
    preset_container.grid(row=0, column=1, sticky="news", padx=2.5)

    title_label = ctk.CTkLabel(preset_container, text="Preset", font=("Arial", 18, "bold"))
    title_label.pack(padx=10, pady=5)

    num_columns = 4
    num_rows = 2
    buttons_container = ctk.CTkFrame(preset_container, corner_radius=10, fg_color="transparent")
    buttons_container.pack()

    buttons_grid = ctk.CTkFrame(buttons_container, corner_radius=10)
    buttons_grid.grid(row=0, column=0, sticky="nsew")

    buttons_pos = [(x, y) for x in range(num_rows) for y in range(num_columns)]

    # Function for long press detection
    def check_long_press(btn):
        if btn.is_pressed:
            duration = time.time() - btn.press_time
            if duration >= 1:
                # Long press: save current app values in the preset
                btn.value = app.values.copy()
                app.show_message(f"Preset {btn.id} saved with current values")
                btn.is_pressed = False  # prevent repeated execution
            else:
                btn.after(50, lambda: check_long_press(btn))

    # Button press event
    def on_press(event):
        btn = event.widget
        # ascend to the actual button if the event comes from an inner canvas
        while not isinstance(btn, ctk.CTkButton):
            btn = btn.master
        btn.is_pressed = True
        btn.press_time = time.time()
        check_long_press(btn)

    # Button release event
    def on_release(event):
        btn = event.widget
        while not isinstance(btn, ctk.CTkButton):
            btn = btn.master
        if btn.is_pressed:
            duration = time.time() - btn.press_time
            if duration < 1:
                # Short press: load values from the preset
                if btn.value:
                    app.values = btn.value.copy()
                    input_sync(app)
                    app.show_message(f"The preset option {btn.id} has been applied!")
                else:
                    app.show_message(f"The preset option {btn.id} is empty!")
            btn.is_pressed = False

    # Create preset buttons
    for i, (row, col) in enumerate(buttons_pos):
        btn = ctk.CTkButton(
            buttons_grid,
            text=f"{i+1}",
            text_color="black",
            font=("Arial", 18, "bold"),
            width=50,
            height=50,
            corner_radius=10
        )
        btn.id = str(i + 1)
        btn.value = None
        btn.is_pressed = False
        btn.grid(row=row, column=col, padx=10, pady=10)

        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    # Function to apply a preset by button ID
    def apply_preset_by_id(preset_id):
        for btn in buttons_grid.winfo_children():
            if getattr(btn, "id", None) == str(preset_id):
                if btn.value:
                    app.values = btn.value.copy()
                    input_sync(app)
                    app.show_message(f"The preset option {btn.id} has been applied!")
                else:
                    app.show_message(f"The preset option {btn.id} is empty!")
                break

    # Bind keyboard shortcuts Control+1..Control+8 for presets
    def bind_presets_shortcuts():
        for i in range(1, num_rows * num_columns + 1):
            app.bind_all(f"<Control-Key-{i}>", lambda event, preset_id=i: apply_preset_by_id(preset_id))

    # Call the shortcut binding after creating the preset window
    bind_presets_shortcuts()
