"""
Script to visualize data obtained from processed csv files. Use preprocess_csv for that.
All the data in csv format must be as following: first column is time, second column is the measured value (see xlsx file in the data folder for details)

Requires a .json file with the structure of an experiment.
json structure must be as following:
"folder" = <name of the folder to take data from>
<channel id number> = {"units" = <used units>,
                       <OPTIONAL ATTRIBUTE, default 1>, "scaler" = <coefficient to linearly scale the dat to the corresponding units>,
                       <OPTIONAL ATTRIBUTE, default 0>, "time_offset" = <offset from the start time, will shift the data timeline>
                       }
"""
from os import path
import json
import random

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_color(index: int) -> str:
    """
    Generates colors for plots
    :param index: id of the requested color
    :return: color string accepted by plotly
    """
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
    name_mapping = {"mm": "Rack position", "mm/s": "Rack velocity", "V": "Coil voltage"}
    names = [name_mapping[x] for x in units if x in name_mapping]

    position_range = (0, 0)  # used for stripes plotting

    # Define base offset step for each additional y-axis (so they don’t overlap)
    offset_step = 0.05
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
                    yaxis=f'y{i + 1}'
                ))
            if data["unit"] == 'mm':  # used for scaling stripes if the tooth pitch is drawn
                position_range = (min(data["values"]), max(data["values"]))
        new_color = get_color(i)
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
        legend=dict(orientation='h', y=-0.2)
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

if __name__ == "__main__":
    # --- available settings ---
    data_json: str = "setup_031125.json"   # name of the description file to be used by parser
    ids_to_plot: list[str | int] = [54, 55, 56, ]  # IDs of the data samples to be plotted
    enable_pitch_plotting = True  # if true plot background will be colored with stripes of pitch height

    # --- rest of the script ----
    used_data: list[dict] = []  # parsed data is stored here

    with open(data_json, 'r', encoding='utf-8') as f:  # Open and load the JSON file
        data = json.load(f)

    for data_id in ids_to_plot:
        cur_dict = data[str(data_id)]
        df = pd.read_csv(path.join(data["folder"], str(data_id) + '.csv'), header=None)
        numpy_df = df.to_numpy()
        # time = df.columns[0].to_numpy()
        # values = df.columns[1].to_numpy()
        time = numpy_df[:, 0]
        values = numpy_df[:, 1]

        time = time - np.min(time)
        time = time + float(cur_dict.get('time_offset', 0))

        values = values * float(cur_dict.get('scaler', 1))

        cur_dict["time"] = time
        cur_dict["values"] = values
        used_data.append(cur_dict)

    plot_data(used_data, enable_pitch_plotting=enable_pitch_plotting)