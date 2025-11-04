import customtkinter as ctk

def create_slider(parent_frame, parent_app, idx):
    """
    parent_frame: il frame dove mettere slider+entry (coil_frame)
    parent_app: istanza App
    idx: indice della coil
    """
    slider_frame = ctk.CTkFrame(parent_frame, corner_radius=5)  # ora ctk è definito

    # Contenitore interno per label + entry
    text_frame = ctk.CTkFrame(slider_frame, fg_color="transparent")  # optional, solo per organizzare
    text_frame.pack(fill="x")

    # Label
    label = ctk.CTkLabel(text_frame, text="Current (mA):", font=("Arial", 16))
    label.pack(side="left", padx=(0, 5))

    # Entry
    entry_var = ctk.StringVar(value="0")
    entry = ctk.CTkEntry(text_frame, textvariable=entry_var, justify="center", width=50, font=("Arial", 18))
    entry.pack(side="left")

    # Slider
    slider = ctk.CTkSlider(
        slider_frame,
        from_=0,
        to=300,
        number_of_steps=300,
        command=lambda val, i=idx: update_from_slider(parent_app, val, i)
    )
    slider.set(0)
    slider.pack(pady=10, fill="x", padx=10)

    entry.bind("<Return>", lambda event, i=idx: update_from_entry(parent_app, i))

    # Salva i riferimenti nell'app
    parent_app.coil_labels.append(label)
    parent_app.coil_entries.append(entry)
    parent_app.coil_sliders.append(slider)

    return slider_frame


# Funzioni di aggiornamento
def update_from_slider(parent_app, value, idx):
    value = int(float(value))
    parent_app.currents[idx] = value
    parent_app.coil_entries[idx].delete(0, "end")
    parent_app.coil_entries[idx].insert(0, str(value))

def update_from_entry(parent_app, idx):
    try:
        value = int(parent_app.coil_entries[idx].get())
        if 0 <= value <= 300:
            parent_app.currents[idx] = value
            parent_app.coil_sliders[idx].set(value)
        else:
            print("Value out of range (0-300)")
    except ValueError:
        print("Please enter a valid number")
