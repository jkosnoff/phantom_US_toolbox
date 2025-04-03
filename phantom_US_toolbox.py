 try: 
                offset = np.where(
                    self.peak_to_peak[self.max_idx] > 1.5 * self.peak_to_peak[self.max_idx].mean())[0][0]
            except IndexError:
                offset = 0
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 15:28:34 2022

@author: joshuak
"""

from nptdms import TdmsFile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
import matplotlib
import os
import glob

import seaborn as sns
sns.set_style("white")


class load_US_data:
    def __init__(self, file_name, passed_params=None, scanner=0, _print=True):
        self.print = _print
        # Ultrasound Parameters
        if passed_params == None:
            self.params = self._parse_file_name(file_name)
        else:
            self.params = passed_params
        self.conversion_factor = self._get_conversion_factor(scanner=scanner)
        self.PD = (1/self.params["f0"]) * self.params["CPP"]
        self.PD_samps = round(self.PD * self.params["sample_rate"])

        # Water Constants
        sos = 1515.0  # Speed of Sound in water [m/s]
        density = 1028.0  # Density of water [kg / m^3]
        self.Z0 = density * sos

        # Load data
        data = self._tdms_to_numpy(file_name)
        self.max_V = data.max()
        self.min_V = data.min()
        self.data_4D = self._serpentine_unravel(data)
        del data
        self.peak_to_peak = self.data_4D - \
            self.data_4D.min(axis=-1, keepdims=True)

        self.max_idx = self.get_max_channel_idx(self.peak_to_peak)

    def get_max_channel_idx(self, series):
        idx = np.argwhere(series == series.max())
        max_idx = tuple(idx[0, :-1])
        return (max_idx)

    def _get_conversion_factor(self, scanner=0):
        flag = 1
        idx = 0
        txt_file = glob.glob("[!_requirements]*.txt")[0]
        conv = pd.read_csv(txt_file)
#         print(conv)
        while flag == 1:
            try:
                conv = pd.read_csv(txt_file, delimiter="\t",
                                   header=None, skiprows=idx)
                flag = 0
            except:
                idx += 1
        # print(self.params["f0"])
        # print(conv[conv[0] == self.params["f0"] / 1000000])
        # print(conv[2][conv[0] == self.params["f0"] / 1000000])

        if self.params["f0"] / 1000000 not in conv[0].values:
            nearest_value = min(conv[0].values, key=lambda x: abs(
                x - self.params["f0"] / 1000000))
            conversion_factor = conv[2][conv[0] == nearest_value].values[0]
        else:
            conversion_factor = conv[2][conv[0] ==
                                        self.params["f0"] / 1000000].values[0]
        # print(conversion_factor)
        return (conversion_factor)

    def _serpentine_unravel(self, data):
        data_4D = np.array(data).reshape(self.params["len_z"],
                                         self.params["len_y"],
                                         self.params["len_x"],
                                         self.params["series_len"])

        # flip y on every other z
        data_4D[::2, :, :, :] = data_4D[::2, ::-1, :, :]
        data_4D[:, ::2, :, :] = data_4D[:, ::2,
                                        ::-1, :]  # flip x on every other y
        data_4D[::2, :, :, :] = data_4D[::2, :,
                                        ::-1, :]  # flip x on every other z
        return (data_4D)

    def _tdms_to_numpy(self, file_name):
        if self.print == True:
            print("Opening File . . .")
        tdms_file = TdmsFile.read(file_name)

        if len(tdms_file.groups()) == 1:
            if self.print == True:
                print("Extracting Data . . .")
            data = tdms_file.groups()[0].channels()[0][:]
            return (data)

        else:
            if self.print == True:
                print("Error! Unrecognized tdms formatting.")
            return (None)

    def _parse_file_name(self, file_name):

        fid = os.path.basename(fr"{file_name}".replace('\\', os.sep))
        params = {}
        nums = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], dtype=str)

        try:
            dx = float(fid.split("x")[1].split("_")[0])
            # print("dx: ", dx)
            params["len_x"] = int(
                (float(fid.split("x")[0].split("_")[-1]) / dx) + 1)
        except:
            params["len_x"] = 0

        try:
            dy = float(fid.split("y")[1].split("_")[0])
            # print("dy: ", dy)
            params["len_y"] = int(
                (float(fid.split("y")[0].split("_")[-1]) / dy) + 1)
        except:
            params["len_y"] = 0

        try:
            dz = float(fid.split("z")[1].split("_")[0])
            # print("dz: ", dz)
            params["len_z"] = int(
                (float(fid.split("z")[0].split("_")[-1]) / dz) + 1)
        except:
            params["len_z"] = 0

        try:
            params["f0"] = float(fid.split("UFF")[1].split("_")[0]) * 1e3
        except:
            params["f0"] = 0

        try:
            params["CPP"] = float(fid.split("CPP")[1].split("_")[0])
        except:
            params["CPP"] = 0

        try:
            params["pulse_number"] = float(fid.split("PN")[1].split("_")[0])
        except:
            params["pulse_number"] = 0

        try:
            params["sample_rate"] = float(fid.split("SR")[1].split("_")[0])
        except:
            params["sample_rate"] = 0

        try:
            params["PRF"] = float(fid.split("UPRF")[1].split("_")[0])
        except:
            params["PRF"] = 0

        try:
            input_mv = fid.split("v_")[0].split("_")[-1]
            if input_mv[-1] == "m":
                input_mv = float(input_mv)
            if input_mv[-1] in nums:
                input_mv = float(input_mv) * 1000
            params["input_mv"] = input_mv
        except:
            params["input_mv"] = 0

        try:
            params["series_len"] = int(float(fid.split("DL")[1].split("_")[0]))
        except:
            params["series_len"] = 0

        try:
            params["title"] = "_".join(fid.strip(".tdms").split("_")[-2:])
        except:
            params["title"] = 0

        return (params)

    def calc_PII(self, pulse_average=False):
        if not pulse_average:
             try: 
                offset = np.where(
                    self.peak_to_peak[self.max_idx] > 1.5 * self.peak_to_peak[self.max_idx].mean())[0][0]
            # The signal might not well defined if using lower voltages. In that case, just take the first data point.
            except IndexError:
                offset = 0

            # Calculate the pressure of one pulse
            P_t = self.data_4D[self.max_idx][0 +
                                             offset:self.PD_samps+offset] / self.conversion_factor

            # Take the integral
            timepoints = np.array([i * 1/self.params["sample_rate"] for i in range(
                self.params["series_len"])])[0+offset:self.PD_samps+offset]
            PII = metrics.auc(timepoints, (P_t)**(2) / self.Z0)

        else:
            ###
            # Code update coming soon . . . effectively get the average of every pulse instead of just using
            # the first one
            ###
            PII = None
        return (PII)

    def calc_Isppa(self):
        Isppa = self.calc_PII() / (self.PD * 10000.0)
        return (Isppa)

    def calc_Ispta(self):
        Ispta = self.calc_PII() * self.params["PRF"] / 10
        return (Ispta)

    def calc_Pmax(self):
        return (self.peak_to_peak.max() / self.conversion_factor)

    def calc_MI(self):
        return (((np.abs(self.min_V) / self.conversion_factor) / 10**(6)) / (self.params["f0"] / 10**(6))**(0.5))

    def calc_Vpp_max(self):
        return (self.max_V)

    def plot_XY(self, param, slice_idx="max_slice", save_figures=False):
        if param.lower() == "pressure":
            plot_val = (self.peak_to_peak.max(
                axis=-1, keepdims=True) / self.conversion_factor)
        elif param.lower() == "intensity":
            plot_val = (self.peak_to_peak.max(
                axis=-1, keepdims=True) / self.conversion_factor) ** (2) / self.Z0

        else:
            print(
                "Error! Unrecognized parameter type. Please enter 'Pressure', or 'Intensity'")
            return

        if slice_idx == "max_slice":
            slices = [self.max_idx[0]]
        elif slice_idx == "all":
            slices = np.array(range(0, self.params["len_z"]))
        elif type(slice_idx) == int:
            slices = [slice_idx]

        for _slice in slices:
            plt.figure()
            plt.xlabel("X (mm)")
            plt.ylabel("Y (mm)")
            plt.title(f"XY {param} at Z = {_slice}")
            plt.imshow(plot_val[_slice, :, :], cmap="jet",
                       origin="lower", interpolation="gaussian")
            fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
            fmt.set_powerlimits((0, 0))
            plt.colorbar(format=fmt)
            if save_figures == True:
                plt.savefig(self.params["title"]+f"_{param}_XY_{_slice}mm.png")
        plt.show()
        return

    def plot_XZ(self, param, slice_idx="max_slice", save_figures=False):
        if param.lower() == "pressure":
            plot_val = (self.peak_to_peak.max(
                axis=-1, keepdims=True).squeeze() / self.conversion_factor)
        elif param.lower() == "intensity":
            plot_val = (self.peak_to_peak.max(
                axis=-1, keepdims=True).squeeze() / self.conversion_factor) ** (2) / self.Z0

        else:
            print(
                "Error! Unrecognized parameter type. Please enter 'Pressure', or 'Intensity'")
            return

        if slice_idx == "max_slice":
            slices = [self.max_idx[1]]
        elif slice_idx == "all":
            slices = np.array(range(0, self.params["len_y"]))
        elif type(slice_idx) == int:
            slices = [slice_idx]

        for _slice in slices:
            plt.figure()
            plt.xlabel("X (mm)")
            plt.ylabel("Z (mm)")
            plt.title(f"XZ {param} at Y = {_slice}")
            plt.imshow(plot_val[:, _slice, :], cmap="jet",
                       origin="lower", interpolation="gaussian")
            fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
            fmt.set_powerlimits((0, 0))
            plt.colorbar(format=fmt)
            if save_figures == True:
                plt.savefig(self.params["title"]+f"_{param}_XZ_{_slice}mm.png")
        plt.show()

        return

    def return_dataframe(self):
        df = pd.DataFrame(columns=[f"{self.params['input_mv']}mv_input"])
        df.loc["Input mV"] = self.params['input_mv']
        df.loc["Isppa (W/cm^2)"] = self.calc_Isppa()
        df.loc["Ispta (mW/cm^2)"] = self.calc_Ispta()
        df.loc["MI"] = self.calc_MI()
        df.loc["Pmax (Pa)"] = self.calc_Pmax()
        df.loc["Vmin"] = self.min_V
        df.loc["PNP"] = np.abs(self.min_V) / self.conversion_factor
        df.loc["Focal Point (Z, Y, X)"] = [np.asarray(self.max_idx)]
        return (df)
