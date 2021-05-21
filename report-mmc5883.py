#!/usr/bin/python3

import argparse
from datetime import datetime
from fpdf import FPDF
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

WIDTH = 210
HEIGHT = 297

file_path = './tmp/'
if not os.path.exists(file_path):
    os.makedirs(file_path)

# TODO Can I put this into a function?
parser = argparse.ArgumentParser(description='mmc5883 test')
parser.add_argument('--input', action='store', type=str, required=True)
parser.add_argument('--output', action='store', type=str, required=True)
args = parser.parse_args()

data = pd.read_csv(args.input, header=None, sep=' ')
data.rename(columns={0: "Timestamp", 1: "Log_Type"}, inplace=True)
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='s')
print(data.head())

measurements = pd.DataFrame(data=data.query('Log_Type == 1'))

calibration = pd.DataFrame(data=data.query('Log_Type == 3'))
calibration.rename(columns={6: "X_Offset", 7: "Y_Offset", 8: "Z_Offset", 9: "T_Offset"}, inplace=True)
calib_indices = calibration.index.tolist()

num_calibs = len(calib_indices)
counter = 0
for i, row in calibration.iterrows():
    calib_x_scaled = row['X_Offset']
    calib_y_scaled = row['Y_Offset']
    calib_z_scaled = row['Z_Offset']
    calib_t_scaled = row['T_Offset']
    print("Row Index is " + str(i))
    print(calib_indices)

    # Adjust Compass Dataframe with calibration offsets
    # the logic is taking the above calib variables, adding them to each index in the range defined
    if counter + 1 < num_calibs:
        measurements.loc[(calib_indices[counter] + 1): calib_indices[counter + 1], "calib_x_scaled"] = measurements[6] + \
                                                                                                    calib_x_scaled
        measurements.loc[(calib_indices[counter] + 1): calib_indices[counter + 1], "calib_y_scaled"] = measurements[7] + \
                                                                                                    calib_y_scaled
        measurements.loc[(calib_indices[counter] + 1): calib_indices[counter + 1], "calib_z_scaled"] = measurements[8] + \
                                                                                                    calib_z_scaled
        measurements.loc[(calib_indices[counter] + 1): calib_indices[counter + 1], "calib_t_scaled"] = measurements[9] + \
                                                                                                    calib_t_scaled

    if counter + 1 >= num_calibs:
        measurements.loc[(calib_indices[counter] + 1):, "calib_x_scaled"] = measurements[6] + calib_x_scaled
        measurements.loc[(calib_indices[counter] + 1):, "calib_y_scaled"] = measurements[7] + calib_y_scaled
        measurements.loc[(calib_indices[counter] + 1):, "calib_z_scaled"] = measurements[8] + calib_z_scaled
        measurements.loc[(calib_indices[counter] + 1):, "calib_t_scaled"] = measurements[9] + calib_t_scaled

    print(measurements.head())
    counter += counter

configuration = pd.DataFrame(data=data.query('Log_Type == 2'))
configuration.rename(columns={2: "Bandwidth"}, inplace=True)

errors = pd.DataFrame(data=data.query('Log_Type == 0'))
errors.rename(columns={2: 'Error Message'}, inplace=True)


def generate_table():
    # Calib and errors
    bw_const = None
    bw = None
    error_list = None
    ts_list = None

    # TODO - make this simpler?
    if not configuration.empty:
        first_last_config = configuration.iloc[[0, -1]]
        if first_last_config['Bandwidth'].iloc[0] == first_last_config['Bandwidth'].iloc[1]:
            # gain settings unchanged during test
            bw_const = True
            bw = first_last_config['Bandwidth'].iloc[0]
        else:
            bw_const = False

    if not errors.empty:
        error_list = errors['Error Message'].tolist()
        ts_list = errors['Timestamps'].to_list()

    # Measurement table
    t_avg = str(round(np.average(measurements.loc[1:, 'calib_t_scaled']), 3))
    x_avg = str(round(np.average(measurements.loc[1:, 'calib_x_scaled']), 3))
    y_avg = str(round(np.average(measurements.loc[1:, 'calib_y_scaled']), 3))
    z_avg = str(round(np.average(measurements.loc[1:, 'calib_z_scaled']), 3))

    return t_avg, x_avg, y_avg, z_avg, bw_const, bw, error_list, ts_list


def compass_test_data():
    # Get total test time
    first_last = data['Timestamp'].iloc[[0, -1]].values
    time_delta = (first_last[1]-first_last[0])

    # Get number of measurements
    n = measurements.shape[0]

    # Get average measurement frequency
    first_last_meas = measurements['Timestamp'].iloc[[0, -1]].values
    total_delta = first_last_meas[1]-first_last_meas[0]
    total_delta = np.timedelta64(total_delta, 'ns')
    avg_freq = total_delta / n

    # Get noise measurement on x values
    # TODO - figure out a way to get time delta indices and take the average, max, and min of those X values
    # x_vals = measurement_frame['calib_x_scaled']
    delta = np.timedelta64(4, 'ms')
    res = np.searchsorted(measurements.Timestamp, measurements.Timestamp+delta)

    # Get measurement timing jitter
    # TODO - determine number of samples to gather
    return time_delta, n, avg_freq


def generate_figures(filename=args.output):
    field_list = ['calib_x_scaled', 'calib_y_scaled', 'calib_z_scaled']
    offset_list = ['X_Offset', 'Y_Offset', 'Z_Offset', 'T_Offset']
    color1 = ["#FFA630", "#4DA1A9", "#611C35", "#2E5077"]
    color2 = ["#D7E8BA"]

    measurements.plot(kind='line', x='Timestamp', y=field_list, color=color1)
    label_fig('Timestamp', 'Field Magnitude', 'Compass Magnitude over time')
    plt.savefig(fname=file_path+'compass_0.png')
    plt.close()

    measurements.plot(kind='line', x='Timestamp', y=field_list, color=color1)
    ax2 = plt.twinx()
    measurements.plot(kind='line', x='Timestamp', y='calib_t_scaled', color=color2, ax=ax2)
    ax2.legend(loc='upper left')
    label_fig('Timestamp', 'Field Magnitude', 'Compass Magnitude and Temperature')
    plt.savefig(fname=file_path+'compass_1.png')
    plt.close()

    measurements.plot(kind='line', x='Timestamp', y='calib_t_scaled', color=color2)
    label_fig('Timestamp', 'Temperature', 'Compass Temperature')
    plt.savefig(fname=file_path+'compass_2.png')
    plt.close()

    calibration.plot(kind='line', x='Timestamp', y=offset_list, color=color2)
    label_fig('Timestamp', 'Offsets', 'Offsets on Compass over Time')
    plt.savefig(fname=file_path + 'compass_3.png')
    plt.close()


def label_fig(x, y, title):
    # TODO - create dict for columns to X and Y axis labels
    plt.title(f"{title}")
    plt.ylabel(f"{y}")
    plt.xlabel(f"{x}")


def table_helper(pdf, epw, th, table_data, col_num):
    for row in table_data:
        for datum in row:
            # Enter data in columns
            pdf.cell(epw/col_num, 2 * th, str(datum), border=1)
        pdf.ln(2 * th)


def init_report(filename=args.output):
    t_avg, x_avg, y_avg, z_avg, bw_const, bw, error_list, ts_list = generate_table()

    time_delta, n, avg_freq = compass_test_data()

    config_data = [['', 'Bandwidth'], ['Value', bw], ['Constant Config', bw_const]]
    error_data = [ts_list, error_list]

    table_data = [['Parameter', 'Temp', 'X', 'Y', 'Z'], ['Average', x_avg, y_avg, z_avg, t_avg]]

    test_data = [['Total Test Time', 'Number of Measurements', 'Average Sampling Freq'], [time_delta, n, avg_freq]]

    result_data = [[None]]  # TODO add the required pass/fails for compass

    pdf = FPDF()
    epw = pdf.w - 2*pdf.l_margin
    pdf.add_page()

    pdf.set_font('Helvetica', '', 10.0)
    th = pdf.font_size

    if None not in result_data:
        pdf.set_font('Helvetica', '', 14.0)
        pdf.cell(WIDTH, 0.0, 'Results of Compass Test', align='C')
        pdf.set_font('Helvetica', '', 10.0)
        pdf.ln(5)
        table_helper(pdf, epw, th, result_data, 3)
        pdf.ln(5)

    if None not in test_data:
        pdf.set_font('Helvetica', '', 14.0)
        pdf.cell(WIDTH, 0.0, 'Summary of Compass Test', align='C')
        pdf.set_font('Helvetica', '', 10.0)
        pdf.ln(5)
        table_helper(pdf, epw, th, test_data, 3)
        pdf.ln(5)

    if None not in config_data:
        pdf.set_font('Helvetica', '', 12.0)
        pdf.cell(WIDTH, 0.0, 'Summary of Compass Test Configurations', align='C')
        pdf.set_font('Helvetica', '', 10.0)
        pdf.ln(5)
        table_helper(pdf, epw, th, config_data, 3)
        pdf.ln(5)

    if None not in error_data:
        pdf.set_font('Helvetica', '', 12.0)
        pdf.cell(WIDTH, 0.0, 'Summary of Compass Test Errors', align='C')
        pdf.set_font('Helvetica', '', 10.0)
        pdf.ln(5)
        table_helper(pdf, epw, th, error_data, len(error_list))
        pdf.ln(5)

    if None not in table_data:
        pdf.set_font('Helvetica', '', 12.0)
        pdf.cell(WIDTH, 0.0, 'Summary of Compass Test Measurements', align='C')
        pdf.set_font('Helvetica', '', 10.0)
        pdf.ln(5)
        table_helper(pdf, epw, th, table_data, 5)

    # Add images
    pdf.image("./tmp/compass_2.png", 5, 85, WIDTH/2-10)
    pdf.image("./tmp/compass_0.png", WIDTH/2, 85, WIDTH/2-10)
    pdf.image("./tmp/compass_1.png", 5, 150, WIDTH/2 - 10)
    pdf.image("./tmp/compass_3.png", WIDTH/2, 150, WIDTH/2 - 10)

    pdf.output(filename, 'F')


if __name__ == '__main__':
    print("Post-Processing Script")
    generate_table()
    generate_figures()
    init_report()
