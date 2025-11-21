# ui/input_section.py

import customtkinter as ctk
from logic.parameters import input_sync


def create_input(app_in, parent_frame, coil_idx, param_idx):
    param = app_in.parameters[param_idx]
    unit = app_in.units[param_idx]

    # Current value from the dictionary keyed by (coil_idx, param_idx)
    value = app_in.values[(coil_idx, param_idx)]

    frame = ctk.CTkFrame(parent_frame, corner_radius=5, fg_color="transparent")

    text_frame = ctk.CTkFrame(frame, fg_color="transparent")
    text_frame.pack(fill="x", padx=10, pady=5)

    label = ctk.CTkLabel(text_frame, text=f"{param} ({unit}):", font=("Arial", 16))
    label.pack(side="left", padx=(0, 5))

    entry = ctk.CTkEntry(
        text_frame,
        border_color="blue",
        width=70,
        font=("Arial", 16),
        justify="left"
    )
    entry.insert(0, str(value))
    entry.pack(side="right")

    slider = ctk.CTkSlider(frame, from_=0, to=app_in.top_values[param_idx])
    slider.set(value)
    slider.pack(pady=10, fill="x", padx=10)

    def on_slider(val):
        val = int(float(val))
        app_in.values[(coil_idx, param_idx)] = val
        entry.delete(0, "end")
        entry.insert(0, str(val))
        input_sync(app_in, coil_idx, param_idx, val)


    def on_entry(_):
        try:
            val = int(entry.get())
            app_in.values[(coil_idx, param_idx)] = val
            slider.set(val)

            if val > app_in.top_values[param_idx]:  # update max if new value exceeds previous
                app_in.show_message(f"New max for {param}: {val}")
                app_in.top_values[param_idx] = val
                for coil_id in range(app_in.num_coils):
                    app_in.inputs[(coil_id, param_idx)]["slider"].configure(to=val)

            input_sync(app_in, coil_idx, param_idx, val)

        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, str(app_in.values[(coil_idx, param_idx)]))

    slider.configure(command=on_slider)
    entry.bind("<Return>", on_entry)
    entry.bind("<KP_Enter>", on_entry)

    return frame, slider, entry


def create_coil_sections(app):
    """Creates a frame for each coil column."""
    for coil_id in range(app.num_coils):
        app.input_container.grid_columnconfigure(coil_id + 1, weight=1)

        coil_frame = ctk.CTkFrame(app.input_container, corner_radius=10, fg_color="transparent")
        coil_frame.grid(row=0, column=coil_id + 1, sticky="news", padx=2.5)
        coil_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(coil_frame, text=f"COIL {coil_id + 1}", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, pady=(10, 5), sticky="new")

        for param_idx in range(len(app.parameters)):
            coil_frame.grid_rowconfigure(param_idx + 1, minsize=80)
            frame, slider, entry = create_input(app, coil_frame, coil_id, param_idx)
            frame.grid(row=param_idx + 1, column=0, sticky="new", padx=5)

            if not hasattr(app, "inputs"):
                app.inputs = {}
            app.inputs[(coil_id, param_idx)] = {"slider": slider, "entry": entry}
