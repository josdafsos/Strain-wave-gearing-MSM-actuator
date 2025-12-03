from copy import deepcopy
# def individual_control():


def base_data(app):
    if app.control_method == "Coil-based":
        NUM_INPUT_COLUMNS = 4
        PARAMETERS = ["Current", "ON Time", "OFF Time", "Pause Time"]
        UNITS = ["mA", "ms", "ms", "ms"]
        TOP_VALUES = [3000, 1000, 1000, 1000]
        PARAMETERS_ACR = ["C", "TON", "TOFF", "TP"]
    elif app.control_method == "Sequence-based":
        NUM_INPUT_COLUMNS = 1
        PARAMETERS = ["Frequency", "ON Time"]
        UNITS = ["Hz", "ms"]
        TOP_VALUES = [3000, 1000]
        PARAMETERS_ACR = ["HZ", "TON"]

    # === Store configuration ===
    app.in_columns = NUM_INPUT_COLUMNS
    app.in_parameters = PARAMETERS
    app.units = UNITS
    app.top_values = TOP_VALUES
    app.parameters_acr = PARAMETERS_ACR
    app.top_values_orig = deepcopy(TOP_VALUES)

    app.values = {
        (coil_id, param_idx): 0
        for coil_id in range(app.in_columns)
        for param_idx, _ in enumerate(app.in_parameters)
    }
