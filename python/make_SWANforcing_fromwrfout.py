import argparse
import os
import shutil
import xarray as xr
import matplotlib.pyplot as plt
import csv
import glob
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd

parser = argparse.ArgumentParser(
    description="Generate SWAN wind forcing files from WRF output"
)
parser.add_argument(
    "--output-dir",
    default="../00_outputdata",
    help="Directory to store generated SWAN wind files",
)
args = parser.parse_args()

output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

# 1. Data preparation and CSV aggregation
print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir('.'))

# ▼ Obtain list of WRF time-series files
file_list = sorted(
    glob.glob(r'\\wsl.localhost\Ubuntu-22.04\home\rsaito_wsl\WRF\WRF-4.5.2-ARW\RUN\run_project_JEBI_sstupdate\wrfout_d01_2018-0*')
)
local_dir = r'F:/tmp'
os.makedirs(local_dir, exist_ok=True)
print(f"Number of target files: {len(file_list)}")

u10_list = []
v10_list = []
time_list = []

wind_csv = os.path.join(output_dir, 'SWAN_wind_timeseries_JEBI.win')
with open(wind_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t')
    for i, f in enumerate(file_list, 1):
        fname = os.path.basename(f)
        local_tmp = os.path.join(local_dir, fname)
        print(f"[{i}/{len(file_list)}] Copying: {fname} ...", end='')
        shutil.copy(f, local_tmp)
        print(" done. Processing...", end='')
        ds = xr.open_dataset(local_tmp)
        u10 = ds['U10'][0].values
        v10 = ds['V10'][0].values
        lons = ds['XLONG'][0].values  # 2D
        lats = ds['XLAT'][0].values
        u10_list.append(u10)
        v10_list.append(v10)
        val = ds['Times'][0].values
        if isinstance(val, np.ndarray):
            val = val.item()  # extract value if ndarray
        if isinstance(val, (bytes, np.bytes_)):
            timestr = val.decode('utf-8').strip()
        else:
            timestr = str(val).strip()
        print("DEBUG timestr:", repr(timestr), type(timestr))
        time_list.append(timestr)
        print('DEBUG timestr:', repr(timestr), type(timestr))
        print(ds['Times'][0])
        print(timestr)
        print(" Writing...", end='')
        for row in u10:
            writer.writerow([round(val, 2) for val in row])
        for row in v10:
            writer.writerow([round(val, 2) for val in row])
        ds.close()
        os.remove(local_tmp)
        print(" Deleted temporary file. Done.")
print("Finished writing all SWAN CSV files.")

# 2. Load data and prepare for visualization
u10_arr = np.array(u10_list)
v10_arr = np.array(v10_list)
wind_speed = np.sqrt(u10_arr**2 + v10_arr**2)

vmin, vmax = 0, 30
levels = np.arange(vmin, vmax+1, 2)
ticks  = np.arange(vmin, vmax+5, 5)
norm   = mcolors.BoundaryNorm(boundaries=levels, ncolors=256)

# 3. Visualization (map with latitude/longitude)
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.set_extent([np.min(lons), np.max(lons), np.min(lats), np.max(lats)])
ax.add_feature(
    cfeature.LAND,
    facecolor="#bb9246c7",
    edgecolor='none',
    alpha=0.8,
    zorder=10
)
ax.add_feature(
    cfeature.COASTLINE,
    edgecolor='white',
    linewidth=1.5,
    zorder=9
)

xticks = np.arange(125, 156, 5)
yticks = np.arange(25, 49, 5)
ax.set_xticks(xticks, crs=ccrs.PlateCarree())
ax.set_yticks(yticks, crs=ccrs.PlateCarree())
import cartopy.mpl.ticker as cticker
ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())

skip = 12

contourf_obj = ax.contourf(
    lons, lats, wind_speed[0],
    levels=levels, cmap='viridis', norm=norm, alpha=0.8,
    transform=ccrs.PlateCarree()
)
Q = ax.quiver(
    lons[::skip, ::skip], lats[::skip, ::skip],
    u10_arr[0][::skip, ::skip], v10_arr[0][::skip, ::skip],
    color='white', scale=8, scale_units='xy',
    width=0.004, headwidth=4, headlength=7,
    transform=ccrs.PlateCarree()
)

cb = plt.colorbar(contourf_obj, ax=ax, ticks=ticks, orientation='vertical',
                  label='Wind Speed (m/s)')
cb.set_label('Wind Speed (m/s)', fontname='Times New Roman', fontsize=16)
cb.ax.set_yticklabels([f"{int(l)}" for l in ticks], fontname='Times New Roman', fontsize=16)
ax.set_xlabel('Longitude', fontname="Times New Roman", fontsize=18)
ax.set_ylabel('Latitude', fontname="Times New Roman", fontsize=18)

def update(frame):
    while len(ax.collections) > 0:
        ax.collections[0].remove()
    global Q
    try:
        Q.remove()
    except Exception:
        pass
    ax.add_feature(
        cfeature.LAND,
        facecolor='#f7f7e8',
        edgecolor='none',
        alpha=0.8,
        zorder=10
    )
    ax.add_feature(
        cfeature.COASTLINE,
        edgecolor='white',
        linewidth=1.5,
        zorder=9
    )
    cf = ax.contourf(
        lons, lats, wind_speed[frame],
        levels=levels, cmap='viridis', norm=norm, alpha=0.6,
        transform=ccrs.PlateCarree()
    )
    Q = ax.quiver(
        lons[::skip, ::skip], lats[::skip, ::skip],
        u10_arr[frame][::skip, ::skip], v10_arr[frame][::skip, ::skip],
        color='black', scale=8, scale_units='xy',
        width=0.004, headwidth=4, headlength=7,
        transform=ccrs.PlateCarree()
    )
    dt = pd.to_datetime(time_list[frame].replace('_', ' '))
    ax.set_title(dt.strftime('%Y-%m-%d %H:%M:%S'), fontname="Times New Roman", fontsize=20)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Times New Roman")
        label.set_fontsize(16)
    return []

anim = FuncAnimation(fig, update, frames=wind_speed.shape[0], interval=400, blit=False)
anim.save(os.path.join(output_dir, 'wind_composite.gif'), writer=PillowWriter(fps=2))
plt.close(fig)
print("Saved contourf + quiver wind animation!")

# 4. Automatic generation of SWAN INPGRID WIND section (added feature)

fmt = "%Y-%m-%d_%H:%M:%S"

def wrf_to_swan_timeformat(timestr):
    t = pd.to_datetime(timestr, format=fmt)
    return t.strftime('%Y%m%d.%H%M%S')

nx, ny = lons.shape
exception_val = 0
start_time_swn = wrf_to_swan_timeformat(time_list[0])
end_time_swn = wrf_to_swan_timeformat(time_list[-1])

dt_seconds = (
    pd.to_datetime(time_list[1], format=fmt)
    - pd.to_datetime(time_list[0], format=fmt)
).total_seconds()
if dt_seconds % 3600 == 0:
    dt_val = int(dt_seconds // 3600)
    dt_unit = 'HR'
elif dt_seconds % 60 == 0:
    dt_val = int(dt_seconds // 60)
    dt_unit = 'MIN'
else:
    dt_val = int(dt_seconds)
    dt_unit = 'SEC'

wind_file = os.path.join(output_dir, 'SWAN_wind_timeseries.win')

# Display grid origin information
origin_lon = float(lons[0,0])
origin_lat = float(lats[0,0])
dx = float(lons[0,1] - lons[0,0]) if lons.shape[1] > 1 else np.nan
dy = float(lats[1,0] - lats[0,0]) if lats.shape[0] > 1 else np.nan
print(f"\n=== SWAN grid information ===")
print(f"Grid origin longitude (southwest corner): {origin_lon}")
print(f"Grid origin latitude (southwest corner): {origin_lat}")
print(f"Longitude spacing: {dx}, Latitude spacing: {dy}")
print(f"Number of grid points: nx = {nx}, ny = {ny}")

# Generate INPGRID WIND line automatically
output_dt = "20 MIN"  # Output interval (default)
calc_dt  = "30 SEC"  # BLOCK output interval (default)
output_dir = "./output"

# Core SWAN settings
swan_inpgrid_text = (
    '$** Wind settings **\n'
    "$\n"
    f"INPGRID WIND CURVILINEAR 0 0 {nx - 1} {ny - 1} EXCEPTION {exception_val} NONSTATIONARY {start_time_swn} {dt_val} {dt_unit} {end_time_swn}\n"
    f"READINP WIND 1 '{wind_file}' 1 0 0 0 FREE\n"
    "$\n"
    "$** Output settings **\n"
    "$\n"
    f"POINTS 'soo' FILE 'SOO.loc'\n"
    f"TABLE  'soo' HEAD   '{output_dir}/waves.tab' TIME DIST DEP HS RTP TM01 TM02 DSPR DIR FORCE OUTPUT {start_time_swn} {output_dt}\n"
    f"TABLE  'soo' HEAD '{output_dir}/wind.tab' TIME WIND OUTPUT {start_time_swn} {output_dt}\n"
    f"SPEC   'soo' SPEC1D '{output_dir}/1D.spc' OUTPUT {start_time_swn} {output_dt}\n"
    f"SPEC   'soo' SPEC2D '{output_dir}/2D.spc' OUTPUT {start_time_swn} {output_dt}\n"
    f"BLOCK  'COMPGRID' NOHEAD   '{output_dir}/waves.mat' HSIG TM01 OUTPUT {start_time_swn} {output_dt}\n"
    "TEST 1,0\n"
    f"COMPUTE NONSTAT {start_time_swn} {calc_dt} {end_time_swn}\n"
    "$\n"
    "STOP\n"
)

print(swan_inpgrid_text)

swan_out = os.path.join(output_dir, 'INPGRID_WIND_for_SWAN.txt')
with open(swan_out, 'w', encoding='utf-8') as f:
    f.write(swan_inpgrid_text)

print(
    f"Saved SWAN output section (INPGRID WIND + OUTPUT settings) to {swan_out}."
)
