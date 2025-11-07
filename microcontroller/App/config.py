from copy import deepcopy
# def individual_control():
def base_data(app):
    if app.control_method:

        NUM_COILS = 4
        PARAMETERS = ["Current", "ON Time", "OFF Time", "Pause Time"]
        UNITS = ["mA", "ms", "ms", "ms"]
        TOP_VALUES = [3000, 1000, 1000, 1000]
    else:
        NUM_COILS = 1
        PARAMETERS = ["Frequency", "ON Time"]
        UNITS = ["Hz", "ms"]
        TOP_VALUES = [3000, 1000]

    # === Store configuration ===
    app.num_coils = NUM_COILS
    app.parameters = PARAMETERS
    app.units = UNITS
    app.top_values = TOP_VALUES
    app.top_values_orig = deepcopy(TOP_VALUES)

    app.values = {
        (coil_id, param_idx): 0
        for coil_id in range(app.num_coils)
        for param_idx, _ in enumerate(app.parameters)
    }
