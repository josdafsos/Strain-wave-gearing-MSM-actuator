"""
Script to visualize data obtained on 25.10.2025
All the data in csv format, first column is time, second column is the measured value (see xlsx file in the data folder for details)

At the moment contains only a snippet to read and visualize data column.
"""

import pandas as pd
import plotly.express as px
from os import path

df = pd.read_csv(path.join('measuremetns_25_10_2025','TEK0002.csv'))

fig = px.line(df, x=df.columns[0], y=df.columns[1], title='test')
fig.show()