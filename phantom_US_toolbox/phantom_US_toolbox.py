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

import seaborn as sns
sns.set_style("darkgrid")


class load_US_data:
    def __init__(self, file_name, scanner=0):
        # Ultrasound Parameters
        self.params = self._parse_file_name(file_name)
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
        self.data_4D = self._serpentine_unravel(data)
        del data
        self.peak_to_peak = self.data_4D - \
            self.data_4D.min(axis=-1, keepdims=True)
        self.max_idx = self.get_max_channel_idx(self.peak_to_peak)

    def get_max_channel_idx(self, series):
        idx = np.argwhere(series == series.max())
        max_idx = tuple(idx[0, :-1])
        return(max_idx)

    def _get_conversion_factor(self, scanner=0):
        if scanner == 0:
            if self.params["f0"] == 500e3:
                conversion_factor = 2.660e-7
            elif self.params["f0"] == 750e3:
                self.conversion_factor = 3.409e-7
            elif self.params["f0"] == 930e3:
                conversion_factor = 2.833e-7
            elif self.params["f0"] == 1000e3:
                conversion_factor = 1.9e-7
            elif self.params["f0"] == 1180e3:
                conversion_factor = 1.192e-7
            elif self.params["f0"] == 1350e3:
                conversion_factor = 1.313e-7
            elif self.params["f0"] == 1640e3:
                conversion_factor = 1.884e-7

        # Smaller animal water tank transducer
        else:
            conversion_factor = 2.458e-7

        return(conversion_factor)

    def _serpentine_unravel(self, data):
        data_4D = np.array(data).reshape(self.params["len_z"],
                                         self.params["len_y"],
                                         self.params["len_x"],
                                         self.params["series_len"])

        # flip y on every other z
        data_4D[::2, :, :, :] = data_4D[::2, ::-1, :, :]
        data_4D[:, ::2, :, :] = data_4D[:, ::2,::-1, :]  # flip x on every other y
        data_4D[::2, :, :, :] = data_4D[::2, :,::-1, :]  # flip x on every other z
        return(data_4D)

    def _tdms_to_numpy(self, file_name):
        print("Opening File . . .")
        tdms_file = TdmsFile.read(file_name)

        if len(tdms_file.groups()) == 1:
            print("Extracting Data . . .")
            data = tdms_file.groups()[0].channels()[0][:]
            return(data)

        else:
            print("Error! Unrecognized tdms formatting.")
            return(None)

    def _parse_file_name(self, file_name):
        fid = os.path.basename(file_name.replace('\\', os.sep))
        params = {}
        params["len_x"] = int(float(fid.split("x")[0].split("_")[-1]) + 1)
        params["len_y"] = int(float(fid.split("y")[0].split("_")[-1]) + 1)
        params["len_z"] = int(float(fid.split("z")[0].split("_")[-1]) + 1)
        params["f0"] = float(fid.split("UFF")[1].split("_")[0]) * 1e3
        params["CPP"] = float(fid.split("CPP")[1].split("_")[0])
        params["pulse_number"] = float(fid.split("PN")[1].split("_")[0])
        params["sample_rate"] = float(fid.split("SR")[1].split("_")[0])
        params["PRF"] = float(fid.split("UPRF")[1].split("_")[0])
        params["input_mv"] = float(fid.split("mv")[0].split("_")[-1])
        params["series_len"] = int(float(fid.split("DL")[1].split("_")[0]))
        params["title"] = "_".join(fid.strip(".tdms").split("_")[-2:])
        return(params)

    def calc_PII(self, pulse_average=False):
        if not pulse_average:
            offset = np.where(
                self.peak_to_peak[self.max_idx] > 1.5 * self.peak_to_peak[self.max_idx].mean())[0][0]

            # Calculate the pressure of one pulse
            P_t = self.data_4D[self.max_idx][0 + offset:self.PD_samps+offset] / self.conversion_factor

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
        return(PII)

    def calc_Isppa(self):
        Isppa = self.calc_PII() / (self.PD * 10000.0)
        return(Isppa)

    def calc_Ispta(self):
        Ispta = self.calc_PII() * self.params["PRF"] / 10
        return(Ispta)

    def calc_Pmax(self):
        return(self.max_V / self.conversion_factor)

    def calc_MI(self):
        return((0.5 * (np.max(self.peak_to_peak[self.max_idx]) / self.conversion_factor) / 10**(6)) / (self.params["f0"] / 10**(6))**(0.5))

    def calc_Vpp_max(self):
        return(self.max_V)

    def plot_XY(self, param, slice_idx="max_slice", save_figures=False):
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
        df.loc["Focal Point (Z, Y, X)"] = [np.asarray(self.max_idx)]
        return(df)
