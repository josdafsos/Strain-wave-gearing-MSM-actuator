from copy import deepcopy


def base_data(app):
    """
    Initialize base configuration data for the application
    depending on the selected control method.
    """

    # === Configuration for Coil-based control ===
    if app.control_method == "Coil-based":
        # Number of input columns (one per coil)
        NUM_INPUT_COLUMNS = 4

        # Parameter names
        PARAMETERS = ["Current", "ON Time", "OFF Time", "Pause Time"]

        # Measurement units for each parameter
        UNITS = ["mA", "ms", "ms", "ms"]

        # Maximum allowed values
        TOP_VALUES = [3000, 1000, 1000, 1000]

        # Acronyms used in app-controller communication
        PARAMETERS_ACR = ["C", "TON", "TOFF", "TP"]

    # === Configuration for Sequence-based control ===
    elif app.control_method == "Sequence-based":
        # Only one input column is needed
        NUM_INPUT_COLUMNS = 1

        # Parameter names
        PARAMETERS = ["Frequency", "ON Time"]

        # Measurement units for each parameter
        UNITS = ["Hz", "ms"]

        # Maximum allowed values
        TOP_VALUES = [3000, 1000]

        # Acronyms used in app-controller communication
        PARAMETERS_ACR = ["HZ", "TON"]

    # === Store configuration in the app object ===
    app.in_columns = NUM_INPUT_COLUMNS          # Number of input columns
    app.in_parameters = PARAMETERS              # Parameter names
    app.units = UNITS                           # Units per parameter
    app.top_values = TOP_VALUES                 # Max values per parameter
    app.parameters_acr = PARAMETERS_ACR         # Abbreviations

    # Keep an untouched copy of original top values
    app.top_values_orig = deepcopy(TOP_VALUES)

    # === Initialize parameter values ===
    # Dictionary key: (coil_id, parameter_index)
    # Initial value for all parameters is 0
    # This dictionary will contain the parameters values in the app
    app.values = {
        (coil_id, param_idx): 0
        for coil_id in range(app.in_columns)
        for param_idx, _ in enumerate(app.in_parameters)
    }
