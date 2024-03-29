# %%
# -*- coding: utf-8 -*-
from typing import List, Literal, Union

import geopandas
import geopandas as gpd
import numpy as np
from cartopy.io.shapereader import natural_earth


# ANCHOR Step 5: Encapsulation
def region_geometry(
    region_level: Literal["STATE", "PROVINCE", "COUNTRY", "LAND"], region_names: Union[List[str], str]
) -> gpd.GeoDataFrame:
    """Get region geometry (in type of geopandas.GeoDataFrame) for region specified by `region_level` and `region_names`

    Args:
        region_level (Literal[): Region level. `STATE` (is the same as `PROVINCE`) is the smallest level
            LAND: 'Africa', 'Antarctica', 'Asia', 'Europe', 'North America', 'Oceania', 'Seven seas (open ocean)', 'South America'
        region_names (Union[List[str], str]): region names that in the region

    Returns:
        gpd.GeoDataFrame: A subset data from natural earth geometry in the type of geopandas.GeoDataFrame
    """
    if isinstance(region_names, str):
        region_names = [region_names]
    if region_level in ["STATE", "PROVINCE"]:
        # the loaded natural earth data (of type GeoDataFrame) has a column 'name' that denotes the name of states/provinces like Guangdong, Anhui, etc.
        shp_fpath = natural_earth("10m", "cultural", "admin_1_states_provinces_lakes")
        match_column = "name"
    elif region_level == "COUNTRY":
        shp_fpath = natural_earth("10m", "cultural", "admin_0_countries_lakes")
        match_column = "NAME"
    else:
        shp_fpath = natural_earth("10m", "cultural", "admin_0_countries")
        match_column = "CONTINENT"
        # raise NotImplementedError()
        # return geopandas.read_file(shp_fpath)

    gdf = geopandas.read_file(shp_fpath)  # load data all
    gdf = gdf.set_index(match_column)  # reset index to name
    return gdf.loc[region_names]  # subset and return


def region_mask(lats: np.ndarray, lons: np.ndarray, geometry: gpd.GeoSeries, predicate: str = "contains") -> np.ndarray:
    """Compute the region mask, a 2D numpy boolean array

    Args:
        lats (np.ndarray): Latitude of shape (n_lats, )
        lons (np.ndarray): Longitude of shape (n_lons, )
        geometry (gpd.GeoSeries): Geometry of the region
        predicate (str, optional): Name of predicate function, check geopandas.sindex.SpatialIndex.query for details. Defaults to "contains".

    Returns:
        np.ndarray: [description]
    """
    n_lats, n_lons = len(lats), len(lons)
    xi, yi = np.meshgrid(lons, lats)
    pts_gss = geopandas.GeoSeries(geopandas.points_from_xy(xi.flatten(), yi.flatten()))
    n_geoms = len(geometry)
    queried_all = list()
    for idx in range(n_geoms):
        queried = pts_gss.sindex.query(geometry.iloc[idx], predicate=predicate)
        queried_all.append(queried)
    queried_all = np.concatenate(queried_all)
    queried_all = np.unravel_index(queried_all, (n_lats, n_lons))
    mask = np.full((n_lats, n_lons), False, dtype=bool)
    mask[queried_all] = True
    return mask


def __test_province_region():
    gdf = region_geometry("PROVINCE", ["Guangdong", "Guangxi", "Hainan"])
    lats = np.arange(17.5, 27.5 + 0.1, 0.5)
    lons = np.arange(102.5, 117.5 + 0.1, 0.5)
    mask = region_mask(lats, lons, gdf.geometry)

    xi, yi = np.meshgrid(lons, lats)
    pts_gss = geopandas.GeoSeries(geopandas.points_from_xy(xi[mask].flatten(), yi[mask].flatten()))
    # NOTE: run in notebook to visualize the results
    ax = gdf.boundary.plot()
    pts_gss.plot(ax=ax, color="black", markersize=1)

    print(mask.sum() / ((mask + 1) >= 1).sum())


def __test_country_region():
    gdf = region_geometry("COUNTRY", ["China", "Taiwan"])
    lats = np.arange(15, 55 + 0.1, 1.5)
    lons = np.arange(70, 137.5 + 0.1, 1.5)
    mask = region_mask(lats, lons, gdf.geometry)

    xi, yi = np.meshgrid(lons, lats)
    pts_gss = geopandas.GeoSeries(geopandas.points_from_xy(xi[mask].flatten(), yi[mask].flatten()))
    # NOTE: run in notebook to visualize the results
    ax = gdf.boundary.plot()
    pts_gss.plot(ax=ax, color="black", markersize=1)

    print(mask.sum() / ((mask + 1) >= 1).sum())


def __test_land_region():
    gdf = region_geometry("LAND", ["Asia"])
    lats = np.arange(15, 55 + 0.1, 1.5)
    lons = np.arange(70, 137.5 + 0.1, 1.5)
    mask = region_mask(lats, lons, gdf.geometry)

    xi, yi = np.meshgrid(lons, lats)
    pts_gss = geopandas.GeoSeries(geopandas.points_from_xy(xi[mask].flatten(), yi[mask].flatten()))
    # NOTE: run in notebook to visualize the results
    ax = gdf.boundary.plot()
    pts_gss.plot(ax=ax, color="black", markersize=1)

    print(mask.sum() / ((mask + 1) >= 1).sum())


if __name__ == "__main__":
    # province/state level region
    __test_province_region()

    # country level region
    __test_country_region()

    # land/continent level region
    __test_land_region()
