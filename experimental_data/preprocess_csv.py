"""
This script preprocesses csv files obtained from an oscilloscope:
removes anything in a csv name beside number (also removes extra zeros in front).
Moves the measurement data to the columns starting from column 0. Removes header description.
"""
import glob
import os
import re
import pandas as pd


if __name__ == "__main__":
    data_folder: str = "measurements_031125"  # name of the folder for the csv files to be processed
    separator: str = ","  # column separator in csv file

    files = glob.glob(os.path.join(data_folder, '*.csv'))
    min_length: int = 30  # maximum length of a header column, everything shorter than this will be removed
    for file in files:
        df = pd.read_csv(file, header=None)  #, sep=separator, engine='python')

        # cleaning and stacking the columns
        filtered = df.loc[:, df.count() >= min_length]
        cols = [filtered[col].dropna().reset_index(drop=True) for col in filtered.columns]
        max_len = max(len(c) for c in cols)  # Determine maximum column length
        padded = [c.reindex(range(max_len)) for c in cols]  # Pad shorter columns with NaN to make them equal length
        stacked_df = pd.concat(padded, axis=1)  # Combine back into a single DataFrame
        stacked_df.columns = range(stacked_df.shape[1])  # Optional: reset column names to 0..N-1

        new_file_name = file.split('\\')[-1][:-4]  # removing the path and .csv
        new_file_name = re.sub(r'[A-Za-z]', '', new_file_name)
        new_file_name = str(int(new_file_name)) + '.csv'  # removing zeros from left

        stacked_df.to_csv(os.path.join(data_folder, new_file_name), index=False, header=False)

