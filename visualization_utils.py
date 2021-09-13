# -*- coding: utf-8 -*-
""" 
A visualization utility module

Function list:
- draw_contourf_map: A quite flexible function to draw a contour (choropleth) map
"""
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
import numpy as np
import math
from typing import Tuple
from pathlib import Path


def draw_contourf_map(
    lat: np.ndarray,
    lon: np.ndarray,
    data: np.ndarray,
    region_bbbox: Tuple[float] = None,
    title: str = None,
    img_path: Path = None,
    feature_kw: dict = None,
    figure_kw: dict = None,
    contour_kw: dict = None,
    cbar_kw: dict = None,
    savefig_kw: dict = None,
) -> Figure:
    """A quite flexible function to draw a contour (choropleth) map, the exposed arguments `figsize_kw`, `contour_kw` and `savefig_kw` provide the user enough control to

        1. specify the properties (dpi, figsize, etc.) to the created figure
        2. specify the behaviours (levels, colors, etc.) when creating choropleth map
        3. specify the options (dpi, bbox_inches, etc.) to save the figure

    Args:
        lat (np.ndarray): Latitude coordination vectors of shape (n_lat, )
        lon (np.ndarray): Longitude coordination vectors of shape (n_lon, )
        data (np.ndarray): 2D data to draw contour of shape (n_lon, n_lat)
        region_bbbox (Tuple[float], optional): The region bounding box (lon_min, lon_max, lat_min, lat_max), (-180, 180, -90, 90) for global. The bbox will be computed from the input arguments `lat` and `lon` automatically if not provided. Defaults to None
        title (str, optional): [description]. Titile of the figure, Defaults to None
        img_path (Path, optional): If provided, the figure will be saved into file of given path. Defaults to None
        faature_kw (dict, optional): Arguments for ploting COASTLINES, BOARDERS, STATES, like linewidth, edgecolor, facecolor etc, if the value is None instead of a dict, the feature will not be plotted. Default is { "COASTLINE": { "linewidth": 0.25 }, "BORDERS": { "linewidth": 0.25 }, "STATES": None}
        figure_kw (dict, optional): Arguments for figure. Defaults to None means {"dpi": 144, "figsize": (9.6, 7.2), "tight_layout": True}. See class (`matplotlib.figure.Figure` documentation)[https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure] for supported arguments
        contour_kw (dict, optional): Arguments to override the default arguments {"levels": 20, "cmap": plt.cm.Blues} input into function (Axes.contourf)[https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.contourf.html?highlight=contourf#matplotlib.axes.Axes.contourf]. Defaults to None. Check the link For a complete list of supported paramters
        savefig_kw (dict, optional): Arguments to override the default arguments {"bbox_inches", "tight"} input into function (savefig)[https://matplotlib.org/stable/api/figure_api.html?highlight=savefig#matplotlib.figure.Figure.savefig]. Only works when `img_path` is provided. Defaults to None. Check the link For a complete list of supported paramters

    Returns:
        Figure: The instance of the Figure
    """

    # parameters
    if region_bbbox:
        xmin, xmax, ymin, ymax = region_bbbox
    else:
        xmin, xmax = math.floor(lon.min()), math.ceil(lon.max())
        ymin, ymax = math.floor(lat.min()), math.ceil(lat.max())

    feature_kw_def = {
        "COASTLINE": {
            "linewidth": 0.25
        },
        "BORDERS": {
            "linewidth": 0.25
        },
        "STATES": None,  # { "linewidth": 0.25 }
        "RIVERS": None,
        "LAKES": None,
    }
    if feature_kw:
        feature_kw_def.update(feature_kw)

    figure_kw_def = {"dpi": 144, "figsize": (9.6, 7.2), "tight_layout": True}
    if figure_kw:
        figure_kw_def.update(figure_kw)

    contour_kw_def = {"levels": 20, "cmap": plt.cm.Blues}
    if contour_kw:
        contour_kw_def.update(contour_kw)

    cbar_kw_def = {}
    if cbar_kw:
        cbar_kw_def.update(cbar_kw)

    # create figure and axes
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(
        subplot_kw={
            "projection": proj,
            "title": title
        },
        **figure_kw_def,
    )
    # plot range and fatures
    ax.set_extent((xmin, xmax, ymin, ymax), ccrs.PlateCarree())
    if feature_kw_def["COASTLINE"] is not None:
        ax.add_feature(cfeature.COASTLINE.with_scale("10m"),
                       **feature_kw_def["COASTLINE"])
    if feature_kw_def["BORDERS"] is not None:
        ax.add_feature(cfeature.BORDERS.with_scale("10m"),
                       **feature_kw_def["BORDERS"])
    if feature_kw_def["STATES"] is not None:
        ax.add_feature(cfeature.STATES.with_scale("10m"),
                       **feature_kw_def["STATES"])
    if feature_kw_def["RIVERS"] is not None:
        ax.add_feature(cfeature.RIVERS.with_scale("10m"),
                       **feature_kw_def["RIVERS"])
    if feature_kw_def["LAKES"] is not None:
        ax.add_feature(cfeature.LAKES.with_scale("10m"),
                       **feature_kw_def["LAKES"])
    # ticks and ticklabels
    ax.set_xticks(
        np.arange(xmin, xmax + 1, np.round((xmax + 1 - xmin) / 8)),
        crs=proj,
    )
    ax.set_yticks(
        np.arange(ymin, ymax + 1, np.round((ymax + 1 - ymin) / 5)),
        crs=proj,
    )
    lon_formatter = LongitudeFormatter()
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # contour(f)
    xi, yi = np.meshgrid(lon, lat)
    cf = ax.contourf(xi, yi, data, transform=proj, **contour_kw_def)
    # colorbar
    divider = make_axes_locatable(ax)
    cax = divider.new_horizontal(size="3.3%", pad=0.05, axes_class=plt.Axes)
    fig.add_axes(cax)
    fig.colorbar(cf, cax=cax, **cbar_kw_def)
    # return / show / save
    if img_path:
        savefig_kw_def = {"bbox_inches": "tight"}
        if savefig_kw:
            savefig_kw_def.update(savefig_kw)
        fig.savefig(img_path, **savefig_kw_def)
    plt.close()
    return fig
