# -*- coding: utf-8 -*-
from ncep_data_utils import read_daily_cpc, read_monthly_cpc
from visualization_utils import draw_contourf_map
import numpy as np
import cmaps

from datetime import date
import pandas as pd
import math


def precip_diff_demo():
    """This function demonstrates the plots of the month average precipitation difference (mm/day) with the annual mean precipitation. The region is set in (72E, 137E, 15N, 55N). The year 2020 is selected to compute the average. The month average precipitation differences (mm/day) between the average are computed in time period between 2020/08 to 2021/07 (12 months in total)., Then 12 figures, 1 for each month, will be plotted and saved into files.  

    Here are several tricks worth noting: 
    1. Select an appropriate colorbar for the color mapping of the data, we use the 'BlueWhiteOrangeRed_r` colormap from package `cmaps`
    2. Since the value 0 should be mapped to the middle color of the selected colormap (white in our case), the contour keyword arguments, including `vmin`, `vmax` and `levels`, should be carefully provided. 
    3. We compute the the maximum and minimum values to map is 0.98 and 0.02 quantile data, respectively, so the value of `extend` argument is set to be `both` to correctly map the values greater (lower) than the maximum (minimum).
    """
    factor = "precip"
    xmin, xmax, ymin, ymax = 72, 137, 15, 55
    cpc_clim_da = read_daily_cpc(factor,
                                 date(2020, 1, 1),
                                 date(2020, 12, 31),
                                 lat_range=(ymin, ymax),
                                 lon_range=(xmin,
                                            xmax)).to_array().mean(dim="time",
                                                                   skipna=True)
    cpc_da = read_monthly_cpc(factor,
                              date(2020, 8, 1),
                              date(2021, 7, 31),
                              lat_range=(ymin, ymax),
                              lon_range=(xmin, xmax)).to_array()

    cpc_diff_da = cpc_da - cpc_clim_da
    cpc_quantile_da = cpc_diff_da.quantile([0.02, 0.98], keep_attrs=False)
    lat, lon = cpc_diff_da.lat.values, cpc_diff_da.lon.values
    data = cpc_diff_da.values.squeeze()
    vmax = round(
        max(abs(cpc_quantile_da[0].item()), abs(cpc_quantile_da[1].item())))

    print(data.shape, lat.shape, lon.shape)  # Out: (12, 80, 130) (80,) (130,)

    for i, dt in enumerate(
            pd.date_range(date(2020, 8, 1), date(2021, 7, 31), freq="MS")):
        draw_contourf_map(
            lat=lat,
            lon=lon,
            data=data[i, ...],
            region_bbbox=(72, 137, 15, 55),
            title=f"Diff {factor} {dt.strftime('%Y%m')}",
            img_path=f"images/{factor}_diff_{dt.strftime('%Y%m')}.png",
            figure_kw={
                "dpi": 144,
                "figsize": (12, 9)
            },
            contour_kw={
                "levels": np.linspace(-vmax, vmax, 17),
                "vmin": -vmax,
                "vmax": vmax,
                "cmap": cmaps.BlueWhiteOrangeRed_r,
                "extend": "both"
            },
        )


def precip_demo():
    """This function demonstrates the plots of the daily average precipitation (mm/day) of the month-scale. Other settings are pretty the same as the function precip_diff_demo, go and check it out.
    """
    # load data
    factor = "precip"
    xmin, xmax, ymin, ymax = 72, 137, 15, 55
    cpc_da = read_monthly_cpc(factor,
                              date(2020, 8, 1),
                              date(2021, 7, 31),
                              lat_range=(ymin, ymax),
                              lon_range=(xmin, xmax)).to_array()

    # compute maximum value, the minimum should be 0
    cpc_quantile_da = cpc_da.quantile(0.98, keep_attrs=False)
    vmax = math.ceil(round(cpc_quantile_da.item()) / 2) * 2

    lat, lon = cpc_da.lat.values, cpc_da.lon.values
    data = cpc_da.values.squeeze()
    print(data.shape, lat.shape, lon.shape)  # Out: (12, 80, 130) (80,) (130,)

    for i, dt in enumerate(
            pd.date_range(date(2020, 8, 1), date(2021, 7, 31), freq="MS")):
        draw_contourf_map(
            lat=lat,
            lon=lon,
            data=data[i, ...],
            region_bbbox=(72, 137, 15, 55),
            title=f"Diff {factor} {dt.strftime('%Y%m')}",
            img_path=f"images/{factor}_{dt.strftime('%Y%m')}.png",
            figure_kw={
                "dpi": 144,
                "figsize": (12, 9)
            },
            contour_kw={
                "levels": np.linspace(0, vmax, 15),
                "vmin": 0,
                "vmax": vmax,
                "cmap": cmaps.MPL_YlGnBu,
                "extend": "max"
            },
            feature_kw={
                # "STATES": {
                #     "linewidth": 0.15,
                #     "edgecolor": "dimgray"
                # },
                # "LAKES": {
                #     "linewidth": 0.2,
                #     "edgecolor": "red"
                # },
                "RIVERS": {
                    "linewidth": 0.3,
                    "edgecolor": "blue"
                }
            },
        )

        break


if __name__ == "__main__":
    # Uncoment the line then run the script to see results
    # precip_diff_demo()
    precip_demo()
    print("Done!")
