"""
This function take the new value which has been input in the app,
- update the corresponding app value dictionary and
- synchronize the input options (slider and entry box) to have the same value
"""
def input_sync(app,
               coil_id_new_value: int = None,
               param_idx_new_value: int = None,
               new_value: int = None):

    """ ===== In this first section, the function store the new value in the app dictionary ===== """

    # If a coil and parameter are specified, the function will work only on this
    if coil_id_new_value is not None and param_idx_new_value is not None:

        # If a new value is provided and the coils are locked together the app values corresponding to that parameter are all updated
        if new_value is not None and app.lock_states[param_idx_new_value]:
            for coil_id in range(app.in_columns):
                app.values[(coil_id, param_idx_new_value)] = new_value
            coil_to_sync = range(app.in_columns)

        # If instead the coils aren't locked, only one value is updated
        elif new_value is not None:
            app.values[(coil_id_new_value, param_idx_new_value)] = new_value
            coil_to_sync = [coil_id_new_value]

        else:
            # Here there isn't a new value, this function is used to just sync the input of the specified par. and coil
            coil_to_sync = [coil_id_new_value]

        param_to_sync = [param_idx_new_value]

    # If coil and parameter are not specified, the function is used to just synchronize ALL sliders and entries
    else:
        coil_to_sync = range(app.in_columns)
        param_to_sync = range(len(app.in_parameters))

    """ ===== In this second section, the value in the dictionary is used to sync the input ===== """

    for coil_id in coil_to_sync:
        for param_idx in param_to_sync:
            new_value = app.values[(coil_id, param_idx)] # Get the value from the dictionary
            ui = app.inputs[(coil_id, param_idx)]
            ui["slider"].set(new_value) # Set the correct slider value
            ui["entry"].delete(0, "end")
            ui["entry"].insert(0, str(new_value)) # Input the value in the entry
            # print(f"{new_value} - {app.controller.values[(coil_id, param_idx)]}") ¤ Print the app and controller values
            # Modify the entry border colour depending if the app and controller values are equal
            if int(new_value) != app.controller.values[(coil_id, param_idx)]:
                ui["entry"].configure(border_color="yellow")
            else:
                ui["entry"].configure(border_color="blue")



