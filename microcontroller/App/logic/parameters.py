def input_sync(app, coil_range=None, param_range=None, new_value=None):

    if new_value is not None and isinstance(coil_range, int) and isinstance(param_range, int) and app.lock_states[param_range]:
        for coil_id in range(app.num_coils):
            app.values[(coil_id, param_range)] = new_value
        coil_range = range(app.num_coils)

    # Convert single numbers to lists
    if isinstance(coil_range, int):
        coil_range = [coil_range]
    if isinstance(param_range, int):
        param_range = [param_range]

    # Default values if None
    if param_range is None:
        param_range = range(len(app.parameters))
    if coil_range is None:
        coil_range = range(app.num_coils)

    for coil_id in coil_range:
        for param_idx in param_range:
            new_value = app.values[(coil_id, param_idx)]
            ui = app.inputs[(coil_id, param_idx)]
            ui["slider"].set(new_value)
            ui["entry"].delete(0, "end")
            ui["entry"].insert(0, str(new_value))


def toggle_lock(app, param_idx, button):
    """
    Switch lock state and swap icon.
    """
    app.lock_states[param_idx] = not app.lock_states[param_idx]

    if app.lock_states[param_idx]:
        button.configure(image=app.locked_image)

        # When activating the lock, take the value of coil 0 as the base
        input_sync(app, 1, param_idx, 0)

    else:
        button.configure(image=app.unlocked_image)
