"""
Script to visualize data obtained from processed csv files. Use preprocess_csv for that.
All the data in csv format must be as following: first column is time, second column is the measured value (see xlsx file in the data folder for details)

Requires a .json file with the structure of an experiment.
json structure must be as following:
"folder" = <name of the folder to take data from>
<channel id number> = {"units" = <used units>,
                       <OPTIONAL ATTRIBUTE, default 1>, "scaler" = <coefficient to linearly scale the dat to the corresponding units>,
                       <OPTIONAL ATTRIBUTE, default 0>, "time_offset" = <offset from the start time, will shift the data_description timeline>
                       <OPTIONAL ATTRIBUTE, default 0>, "start_at_zero" = <0 or 1 defines if the data must start from 0, i.e. it will be offsetted>
                       <OPTIONAL ATTRIBUTE, default 2>, "line_width" - defines the width of the plotted curve
                       }
"""
from os import path
import json
import random

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_color(index: int, units_cnt: int) -> str:
    """
    Generates colors for plots
    :param index: id of the requested color
    :return: color string accepted by plotly
    """
    if units_cnt == 1:
        return 'black'  # if only one type of unit is plotted then the axes are colored black

    colors_list = ['blue',
                   'red',
    'green',
    "rgb(130, 60, 100)"]
    if index >= len(colors_list):
        return f"rgb({random.randint(0, 200)}"
    return colors_list[index]

def plot_data(data_list: list[dict], enable_pitch_plotting: bool = False) -> None:
    """

    :param data_list: List of series to be plotted
    :param enable_pitch_plotting: if True and position is plotted,
    the plot background will be colored with stripes of pitch height
    """
    units_set = set()  # set of units in the data to be plotted
    for data in data_list:
        units_set.add(data["unit"])

    units = list(units_set)

    names = [unit_mapping[x] for x in units if x in unit_mapping]

    position_range = (0, 0)  # used for stripes plotting

    # Define base offset step for each additional y-axis (so they don’t overlap)
    offset_step = 0.070
    # Create figure
    fig = go.Figure()
    if len(units) > 2:
        fig.update_layout(
            xaxis=dict(domain=[0, 1 - offset_step * (len(units) - 2)])  # increase right margin (default ~80)
        )

    for i, (unit, name) in enumerate(zip(units, names)):
        # Define axis name
        axis_name = 'yaxis' if i == 0 else f'yaxis{i + 1}'

        # Add trace
        for data in data_list:
            if data["unit"] == unit:
                fig.add_trace(go.Scatter(
                    x=data["time"],
                    y=data["values"],
                    name=f"{name} ({unit})",
                    yaxis=f'y{i + 1}',
                    line=dict(width=data["line_width"])
                ))
            if data["unit"] == 'mm':  # used for scaling stripes if the tooth pitch is drawn
                position_range = (min(data["values"]), max(data["values"]))
        new_color = get_color(i, len(units))
        # Create corresponding y-axis
        if i == 0:
            # Primary left axis
            fig.update_layout(**{
                axis_name: dict(
                    title=f"{name} ({unit})",
                    titlefont=dict(color=new_color),
                    tickfont=dict(color=new_color),
                    gridcolor='black',
                )
            })
        else:
            # Additional right-side axes
            fig.update_layout(**{
                axis_name: dict(
                    title=f"{name} ({unit})",
                    titlefont=dict(color=new_color),
                    tickfont=dict(color=new_color),
                    gridcolor='black',
                    anchor='free',
                    overlaying='y',
                    side='right',
                    position=1 - (i - 1) * offset_step  # shift slightly to the right
                )
            })

    # General layout
    fig.update_layout(
        xaxis=dict(title='Time (s)'),
        title='Multi-Axis Time Series',
        legend=dict(orientation='h', y=-0.2),
        plot_bgcolor="white",
        font=dict(size=30)
    )

    if enable_pitch_plotting and "mm" in units:
        scaled_pitch = 0.160  # mm, rack motion caused by engagement of a single tooth plate
        fig.update_layout(
            plot_bgcolor="darkgray",  # for contrast
        )
        min_range = int(position_range[0] / scaled_pitch - 2)
        max_range = int(position_range[1] / scaled_pitch + 2)
        for i in range(min_range, max_range, 2):
            fig.add_shape(
                type="rect", xref="paper", yref="y",
                x0=0, x1=1, y0=scaled_pitch*i, y1=scaled_pitch*(i + 1),
                fillcolor="white", opacity=0.3, layer="below", line_width=0
            )

    fig.show()

def process_data(ids_to_process, data_description: dict, ):
    processed_data: list[dict] = []  # parsed data_description is stored here
    for data_id in ids_to_process:
        cur_dict = data_description[str(data_id)]
        df = pd.read_csv(path.join(cur_dict["folder"], str(data_id) + '.csv'), header=None)
        numpy_df = df.to_numpy()
        time = numpy_df[:, 0]
        values = numpy_df[:, 1]

        time = time - np.min(time)
        time = time + float(cur_dict.get('time_offset', 0))
        cur_dict["line_width"] = float(cur_dict.get('line_width', 2))

        values = values * float(cur_dict.get('scaler', 1))
        if "start_at_zero" in cur_dict and bool(cur_dict["start_at_zero"]):
            values -= values[0]

        cur_dict["time"] = time
        cur_dict["values"] = values
        processed_data.append(cur_dict)

    return processed_data

if __name__ == "__main__":
    # --- available settings ---
    ids_to_plot: list[str | int] = ["m23", "m24", "m25" ]  # IDs of the data_description samples to be plotted
    # [2, 1 ] rack velocity and position plot, low frequency
    # ["f67", ] force plot
    # ["m26", "m27", "m28" ] PWM visible, plots for 2.5 Amps current in the coil
    # ["m38", "m39", "m40"]  plots for 3 Amps current in the coil
    # plots 55, 56 are good for comparison with simulation data, first good offset "0.073" seconds.
    # ["vel1", 55, ] First "time_offset": "0.209", Second: offset "0.073" or "0.043" seconds
    enable_pitch_plotting = False  # if true plot background will be colored with stripes of pitch height

    # --- rest of the script ----
    data_json_list: list[str] = ["setup_031125.json",
                                 "simulations_description.json",
                                 "setup_251025.json",
                                 "setup_191125.json"]  # name of the description file to be used by parser
    unit_mapping = {"mm": "Rack position",
                    "mm/s": "Rack velocity",
                    "V": "Coil voltage",
                    "G": "Magnetic induction in the gap",
                    "T": "Magnetic induction in the gap",
                    "A": "Coil current",
                    "N": "Output force"}


    data_description = {}
    for data_json in data_json_list:
        with open(data_json, 'r', encoding='utf-8') as f:  # Open and load the JSON file
            tmp_dict = json.load(f)
            data_folder = tmp_dict["folder"]
            for key in tmp_dict:
                if type(tmp_dict[key]) is dict:
                    tmp_dict[key]["folder"] = data_folder
            data_description = data_description | tmp_dict

    processed_data = process_data(ids_to_plot, data_description)

    plot_data(processed_data, enable_pitch_plotting=enable_pitch_plotting)