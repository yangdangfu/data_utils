# -*- coding: utf-8 -*-
""" Data reconstruction module """
import os
from datetime import date
import numpy as np
from typing import Tuple
import xarray as xr
from ncep_data_utils import read_highres_daily_sst


def daily_sst_reconstruction(start_year: int,
                             end_year: int,
                             recon_filepath_fmt: str,
                             resolution: float = 2.5):
    for year in range(start_year, end_year + 1):
        print(f"Reconstruction of year {year}...")
        s_date = date(year, 1, 1)
        e_date = date(year, 12, 31)
        # interpolation
        lats = np.arange(-90, 90 + resolution / 2, resolution)
        lons = np.arange(0, 360, resolution)
        daily_sst = read_highres_daily_sst(s_date, e_date)
        daily_sst = daily_sst.interp(lat=lats, lon=lons, method="nearest")
        recon_filepath = recon_filepath_fmt.format(year=year)
        daily_sst.to_netcdf(recon_filepath)


if __name__ == "__main__":
    from ncep_data_utils import _RECON2dot5_SST_FILEPATH_FMT
    daily_sst_reconstruction(1981, 2021, _RECON2dot5_SST_FILEPATH_FMT, 2.5)
