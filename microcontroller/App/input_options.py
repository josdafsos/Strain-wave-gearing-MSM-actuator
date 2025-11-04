import customtkinter as ctk

def create_input(parent_frame, parent_app, coil_idx, param_idx):
    param = parent_app.parameters[param_idx]
    paramUnit = parent_app.parameterUnits[param_idx]
    top_value = parent_app.top_values[param_idx]

    slider_frame = ctk.CTkFrame(parent_frame, corner_radius=5, fg_color="transparent")

    # Container for label + entry
    text_frame = ctk.CTkFrame(slider_frame, fg_color="transparent")
    text_frame.pack(fill="x", padx=10)

    # Label
    label = ctk.CTkLabel(text_frame, text=f"{param} ({paramUnit}):", font=("Arial", 16))
    label.pack(side="left", padx=(0,5))

    # Main variable (IntVar)
    var = parent_app.values[coil_idx][param]

    # Entry not directly linked to the variable
    entry = ctk.CTkEntry(text_frame, justify="left", width=50, font=("Arial", 18))
    entry.insert(0, str(var.get()))
    entry.pack(side="right")

    # Slider directly linked to the IntVar
    slider = ctk.CTkSlider(
        slider_frame,
        from_=0,
        to=top_value,
        number_of_steps=top_value,
        variable=var  # direct binding
    )
    slider.pack(pady=10, fill="x", padx=10)

    # Update the entry only when the variable changes (e.g., via slider)
    def on_var_change(*args):
        entry.delete(0, "end")
        entry.insert(0, str(var.get()))
    var.trace_add("write", on_var_change)

    # Update the variable only when the user presses Enter in the entry
    def on_entry_return(event):
        try:
            value = int(entry.get())
            if 0 <= value <= top_value:
                parent_app.update_parameter(param_idx, value)  # update all coils if the parameter is locked
            else:
                parent_app.show_message("Error: Value out of admissible range!")
                entry.delete(0, "end")
                entry.insert(0, str(var.get()))
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, str(var.get()))
    entry.bind("<Return>", on_entry_return)
    entry.bind("<KP_Enter>", on_entry_return)  # also catch Numpad Enter

    # Slider callback: updates all coils if the parameter is locked
    def on_slider_change(val):
        parent_app.update_parameter(param_idx, int(val))
    slider.configure(command=on_slider_change)

    return slider_frame
