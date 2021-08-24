# -*- coding: utf-8 -*-
"""
The module provides functions including reading NCEP reanalysis I&II data in different scales (daily, monthly...), CPC global precipitation & minimum temperature & maximum temperature data, and other auxiliary utility functions like subset data selection.

Function lists:
- `read_daily_ncep`: read daily NCEP reanalysis I&II data
- `read_monthly_ncep`: read monthly NCEP reanalysis I&II data
- `read_rolled_ncep`: read rolled mean NCEP reanalysis I&II data

- `read_daily_cpc`: read daily tmax/tmin/precip data from CPC global data
- `read_monthly_cpc`: read monthly tmax/tmin/precip data from CPC global data
- `read_rolled_cpc`: read rolled mean tmax/tmin/precip data from CPC global data

- `month_select`: select data from `original_data` in dates of given `months`

Notes:
- `slp` variable in NCEP Reanalysis I is named `mslp` in NCEP Reanalysis II
"""
import calendar
from datetime import date
from typing import Dict, List, Literal, Tuple, Union
from dateutil.relativedelta import relativedelta

import os
import xarray as xr
from enum import Enum
import warnings

# ANCHOR configs
_NCEP_ROOT = {
    "NCEP_REANALYSIS":
    "/DATA/CPS_Data/ncep_reanalysis/Datasets/ncep.reanalysis.dailyavgs",
    "NCEP_REANALYSIS_II":
    "/DATA/CPS_Data/ncep_reanalysis/Datasets/ncep.reanalysis2.dailyavgs",
}
_NCEP_FACTOR_FILENAMES = {
    "slp": os.path.join("surface",
                        "slp.{year}.nc"),  # for NCEP Reanalysis I only
    "mslp": os.path.join("surface",
                         "mslp.{year}.nc"),  # for NCEP Reanalysis II only
    "pr_wtr": os.path.join("surface", "pr_wtr.eatm.{year}.nc"),
    "uwnd": os.path.join("pressure", "uwnd.{year}.nc"),
    "vwnd": os.path.join("pressure", "vwnd.{year}.nc"),
    "omega": os.path.join("pressure", "omega.{year}.nc"),
    "air": os.path.join("pressure", "air.{year}.nc"),
    "hgt": os.path.join("pressure", "hgt.{year}.nc"),
    "rhum": os.path.join("pressure", "rhum.{year}.nc"),
    "shum": os.path.join("pressure", "shum.{year}.nc"),
}

_CPC_ROOT = "/DATA/CPS_Data/ncep_reanalysis/Datasets"
_CPC_FACTOR_FILENAMES = {
    "tmax": os.path.join(_CPC_ROOT, "cpc_global_temp", "tmax.{year}.nc"),
    "tmin": os.path.join(_CPC_ROOT, "cpc_global_temp", "tmin.{year}.nc"),
    "precip": os.path.join(_CPC_ROOT, "cpc_global_precip", "precip.{year}.nc"),
}


# ANCHOR read_daily_cpc
def read_daily_ncep(
    factors: Dict[str, list],
    start_date: date,
    end_date: date,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
    source: Literal["NCEP_REANALYSIS",
                    "NCEP_REANALYSIS_II"] = "NCEP_REANALYSIS",
) -> xr.Dataset:
    """
    Function for reading daily NCEP Reanalysis I&II data

    Args:
        factors (Dict[str, list]): A dict of the factors/variables to read. The keys of the dict are the factor names such as `slp`, `air`, `uwnd`, etc. The values of the dict are the list of factor levels, like `[500, 850]`, it should be `None` if the factor doesn't have a level. An example `factors` is {"air": [500, 850], "slp": None}
        start_date (date): Start date of the data to read
        end_date (date): End date of the data to read
        lat_range (Tuple[float, float], optional): Latitude range of the data to read, which should be a subinterval of [-90, 90]. Defaults to None, which means the range is the whole [-90, 90].
        lon_range (Tuple[float, float], optional): Longitude range of the data to read, which should be a subinterval of [0, 360]. Defaults to None, which means the range is the whole [0, 360].
        source (Literal[, optional): Specify the data source. "NCEP_REANALYSIS" for NCEP Reanalysis I dataset, and "NCEP_REANALYSIS_II" for NCEP Reanalysis II dataset. Defaults to "NCEP_REANALYSIS".

    Returns:
        xr.Dataset: `daily_ds` The daily NCEP reanalysis I (or II) data of given variables & temporal & spatial range
    """
    year_start, year_end = start_date.year, end_date.year
    ds_factor = list()
    for factor in factors.keys():
        ds_time = list()
        for year in range(year_start, year_end + 1):
            nc_file = os.path.join(
                _NCEP_ROOT[source],
                _NCEP_FACTOR_FILENAMES[factor].format(year=year))
            with xr.open_dataset(nc_file) as daily_ds:
                da = daily_ds[factor]
                levels = factors[factor]
                ds_level = list()  # list of dataset
                if levels is not None:
                    for level in levels:
                        # new sub-veriable name
                        var_name = f"{factor}{level}"
                        ds_level.append(
                            xr.Dataset({
                                var_name: da.sel(level=level, drop=True)
                            }))  # drop=True丢掉只有长度只有1的level维度
                else:
                    ds_level.append(xr.Dataset({factor: da}))

                ds_time.append(xr.merge(ds_level))  # 将单个要素的分层子物理量组合起来, 放在时间列表中
        ds_factor.append(xr.concat(ds_time, dim="time",
                                   join="inner"))  # 将时间列表中所有的要素在时间维度上进行合并

    daily_ds = xr.merge(ds_factor)  # 将将所有要素的(子)物理量全部合并到一个xr.Dataset中
    # 筛选指定日期范围内的数据
    daily_ds = daily_ds.sel(time=slice(start_date, end_date))
    # 筛选指定经纬度范围内的数据
    if lat_range is not None:
        lat = daily_ds.lat
        lat_select = lat[(lat >= lat_range[0]) & (lat <= lat_range[1])]
        daily_ds = daily_ds.sel(lat=lat_select)
    if lon_range is not None:
        lon = daily_ds.lon
        lon_select = lon[(lon >= lon_range[0]) & (lon <= lon_range[1])]
        daily_ds = daily_ds.sel(lon=lon_select)
    return daily_ds


# ANCHOR read_monthly_cpc
def read_monthly_ncep(
    factors: Dict[str, list],
    start_date: date,
    end_date: date,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
    source: Literal["NCEP_REANALYSIS",
                    "NCEP_REANALYSIS_II"] = "NCEP_REANALYSIS",
) -> xr.Dataset:
    """
    Function for reading monthly NCEP Reanalysis I&II data

    Args:
        factors (Dict[str, list]): A dict of the factors/variables to read. The keys of the dict are the factor names such as `slp`, `air`, `uwnd`, etc. The values of the dict are the list of factor levels, like `[500, 850]`, it should be `None` if the factor doesn't have a level. An example `factors` is {"air": [500, 850], "slp": None}
        start_date (date): Start date of the data to read
        end_date (date): End date of the data to read
        lat_range (Tuple[float, float], optional): Latitude range of the data to read, which should be a subinterval of [-90, 90]. Defaults to None, which means the range is the whole [-90, 90].
        lon_range (Tuple[float, float], optional): Longitude range of the data to read, which should be a subinterval of [0, 360]. Defaults to None, which means the range is the whole [0, 360].
        source (Literal[, optional): Specify the data source. "NCEP_REANALYSIS" for NCEP Reanalysis I dataset, and "NCEP_REANALYSIS_II" for NCEP Reanalysis II dataset. Defaults to "NCEP_REANALYSIS".

    Returns:
        xr.Dataset: `monthly_ds` The monthly NCEP reanalysis I (or II) data of given variables & temporal & spatial range
    """
    if start_date.day != 1:
        warnings.warn(
            f"The given start date {start_date.strftime('%Y/%m/%d')} is not the first day of the month!"
        )
    if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
        warnings.warn(
            f"The given end date {end_date.strftime('%Y/%m/%d')} is not the last day of the month!"
        )
    daily_ds = read_daily_ncep(
        factors=factors,
        start_date=start_date,
        end_date=end_date,
        lat_range=lat_range,
        lon_range=lon_range,
        source=source,
    )
    monthly_ds = daily_ds.resample(time="MS").mean()
    return monthly_ds


# ANCHOR read_rolled_cpc
def read_rolled_ncep(
    factors: Dict[str, list],
    start_date: date,
    end_date: date,
    num_days: int,
    extend: bool = True,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
    source: Literal["NCEP_REANALYSIS",
                    "NCEP_REANALYSIS_II"] = "NCEP_REANALYSIS",
) -> xr.Dataset:
    """Function for reading rolled mean NCEP Reanalysis I&II data

    Args:
        factors (Dict[str, list]): same as in `read_daily_ncep`
        start_date (date): same as in `read_daily_ncep`
        end_date (date): same as in `read_daily_ncep`
        num_days (int): the roll window size (number of days)
        extend (bool, optional): whether to extend the temporal range according to the `num_days`. If True, the end date of returned data will be the date same as `end_date`; if False, the end date of the returned data will be the day `num_days-1` days before the `end_date`. Defaults to True.
        lat_range (Tuple[float, float], optional): same as in `read_daily_ncep`
        lon_range (Tuple[float, float], optional): same as in `read_daily_ncep`
        source (Literal[, optional): same as in `read_daily_ncep`

    Returns:
        xr.Dataset: `rolled_ds` The rolled mean NCEP reanalysis I (or II) data of given variables & temporal & spatial range
    """
    if extend:
        end_date = end_date + relativedelta(days=num_days - 1)
    ds = read_daily_ncep(
        factors=factors,
        start_date=start_date,
        end_date=end_date,
        lat_range=lat_range,
        lon_range=lon_range,
        source=source,
    )
    rolled_ds = (ds.rolling(time=num_days).mean().shift(
        time=-(num_days - 1)).dropna(dim="time", how="all"))
    return rolled_ds


# ANCHOR read_daily_cpc
def read_daily_cpc(
    factor: str,
    start_date: date,
    end_date: date,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
) -> xr.Dataset:
    """
    Function for reading daily CPC total precipitation / maximum temperature / minimum temperature data

    Args:
        factor (str): Variable name of the CPC data, should be one of "tmax", "tmin" and "precip"
        start_date (date): Start date of the data to read
        end_date (date): End date of the data to read
        lat_range (Tuple[float, float], optional): Latitude range of the data to read, which should be a subinterval of [-90, 90]. Defaults to None, which means the range is the whole [-90, 90]
        lon_range (Tuple[float, float], optional): Longitude range of the data to read, which should be a subinterval of [0, 360]. Defaults to None, which means the range is the whole [0, 360].

    Returns:
        xr.Dataset: `daily_ds` The daily CPC data of given variable
    """
    year_start, year_end = start_date.year, end_date.year
    ds_time = list()
    for year in range(year_start, year_end + 1):
        nc_file = os.path.join(_CPC_FACTOR_FILENAMES[factor].format(year=year))
        with xr.open_dataset(nc_file) as ds:
            ds_time.append(ds)
    # concat all datasets of years into a whole
    daily_ds = xr.concat(ds_time, dim="time", join="inner")
    # date slice
    daily_ds = daily_ds.sel(time=slice(start_date, end_date))
    # latitude & longitude crops
    if lat_range is not None:
        lat = daily_ds.lat
        lat_select = lat[(lat >= lat_range[0]) & (lat <= lat_range[1])]
        daily_ds = daily_ds.sel(lat=lat_select)
    if lon_range is not None:
        lon = daily_ds.lon
        lon_select = lon[(lon >= lon_range[0]) & (lon <= lon_range[1])]
        daily_ds = daily_ds.sel(lon=lon_select)
    return daily_ds


# ANCHOR read_monthly_cpc
def read_monthly_cpc(
    factor: str,
    start_date: date,
    end_date: date,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
):
    """
    Function for reading monthly CPC total precipitation / maximum temperature / minimum temperature data

    Args:
        factor (str): Variable name of the CPC data, should be one of "tmax", "tmin" and "precip"
        start_date (date): Start date of the data to read
        end_date (date): End date of the data to read
        lat_range (Tuple[float, float], optional): Latitude range of the data to read, which should be a subinterval of [-90, 90]. Defaults to None, which means the range is the whole [-90, 90]
        lon_range (Tuple[float, float], optional): Longitude range of the data to read, which should be a subinterval of [0, 360]. Defaults to None, which means the range is the whole [0, 360].

    Returns:
        xr.Dataset: `monthly_ds` The monthly CPC data of given variable
    """
    if start_date.day != 1:
        warnings.warn(
            f"The given start date {start_date.strftime('%Y/%m/%d')} is not the first day of the month!"
        )
    if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
        warnings.warn(
            f"The given end date {end_date.strftime('%Y/%m/%d')} is not the last day of the month!"
        )
    daily_ds = read_daily_cpc(
        factor=factor,
        start_date=start_date,
        end_date=end_date,
        lat_range=lat_range,
        lon_range=lon_range,
    )
    monthly_ds = daily_ds.resample(time="MS").mean()
    return monthly_ds


# ANCHOR read_rolled_cpc
def read_rolled_cpc(
    factor: str,
    start_date: date,
    end_date: date,
    num_days: int,
    extend: bool = True,
    lat_range: Tuple[float, float] = None,
    lon_range: Tuple[float, float] = None,
) -> xr.Dataset:
    """Function for reading rolled mean of CPC data in a given sliding window

    Args:
        factor (str): same as in `read_daily_cpc`
        start_date (date): same as in `read_daily_cpc`
        end_date (date): same as in `read_daily_cpc`
        num_days (int): [description]
        extend (bool, optional): whether to extend the temporal range according to the `num_days`. If True, the end date of returned data will be the date same as `end_date`; if False, the end date of the returned data will be the day `num_days-1` days before the `end_date`. Defaults to True
        lat_range (Tuple[float, float], optional): same as in `read_daily_cpc`
        lon_range (Tuple[float, float], optional): same as in `read_daily_cpc`

    Returns:
        xr.Dataset: `rolled_ds` The rolled mean of CPC data in given temporal & spatial range
    """
    if extend:
        end_date = end_date + relativedelta(days=num_days - 1)
    ds = read_daily_cpc(
        factor=factor,
        start_date=start_date,
        end_date=end_date,
        lat_range=lat_range,
        lon_range=lon_range,
    )
    rolled_ds = (ds.rolling(time=num_days).mean().shift(
        time=-(num_days - 1)).dropna(dim="time", how="all"))
    return rolled_ds


# ANCHOR month_select
def month_select(original_data: Union[xr.Dataset, xr.DataArray],
                 months: List[int]) -> Union[xr.Dataset, xr.DataArray]:
    """Select data from `original_data` in dates of given `months`

    Args:
        original_data (Union[xr.Dataset, xr.DataArray]): Original data of type `xr.Dataset` or `xr.Dataset`, the data should have a `time` dimension
        months (List[int]): List of months, such as [1, 2, 3]

    Returns:
        Union[xr.Dataset, xr.DataArray]: `subset_data` - The subset of the original data in dates of given `months`
    """
    time_index = original_data.time
    time_index = time_index[[dt.dt.month in months for dt in time_index]]
    subset_data = original_data.sel(time=time_index)
    return subset_data


if __name__ == "__main__":
    # ds1 = read_daily_ncep(
    #     factors={"air": [500, 850], "slp": None, "pr_wtr": None},
    #     start_date=date(2000, 1, 1),
    #     end_date=date(2002, 2, 5),
    #     source="NCEP_REANALYSIS",
    # )
    # ds2 = read_daily_ncep(
    #     factors={"air": [500, 850], "mslp": None, "pr_wtr": None},
    #     start_date=date(1979, 1, 1),
    #     end_date=date(1985, 2, 5),
    #     source="NCEP_REANALYSIS_II",
    # )

    # print(ds1)
    # print(ds2)
    # print((ds_1 - ds_2).to_array().values)
    cpc_tmax = read_monthly_cpc(
        factor="tmax",
        start_date=date(1979, 1, 1),
        end_date=date(1980, 2, 5),
    )
    # cpc_precip = read_daily_cpc(
    #     factor="precip",
    #     start_date=date(1979, 1, 1),
    #     end_date=date(1979, 2, 5),
    # )
    # cpc_monthly = read_monthly_cpc(
    #     factor="tmax",
    #     start_date=date(1979, 1, 1),
    #     end_date=date(1985, 2, 5),
    # )
    # cpc_rolled = read_rolled_cpc(
    #     factor="tmax",
    #     start_date=date(1979, 1, 1),
    #     end_date=date(1985, 2, 5),
    #     num_days=30,
    # )
    cpc_tmax_sub = month_select(cpc_tmax, [1, 2, 3])
    print(cpc_tmax_sub)
    print(cpc_tmax)
    # print(cpc_precip)
    # print(cpc_monthly)
    # print(cpc_rolled)
    # print(cpc_tmax)
