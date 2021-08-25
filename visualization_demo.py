# -*- coding: utf-8 -*-
import matplotlib as plt

from ncep_data_utils import read_daily_cpc, spatial_cropping
from visualization_utils import draw_contourf_map

from datetime import date

if __name__ == "__main__":
    factor = "precip"
    xmin, xmax, ymin, ymax = 72, 137, 15, 55
    cpc_da = read_daily_cpc(factor, date(2021, 7, 19), date(2021, 7, 21)).to_array()
    cpc_da = spatial_cropping(cpc_da, (ymin, ymax), (xmin, xmax))
    # data extraction for visualization
    lat, lon = cpc_da.lat.values, cpc_da.lon.values
    data = cpc_da.sum(dim="time").values.squeeze()

    fig = draw_contourf_map(
        lat=lat,
        lon=lon,
        data=data,
        region_bbbox=(72, 137, 15, 55),
        title=factor,
        img_path=f"{factor}.svg",
        figure_kw={"dpi": 18, "figsize": (6.4, 4.8)},
        contour_kw={"levels": range(0, 451, 10), "cmap": plt.cm.Blues, "extend": "max"},
    )

    print(fig)
