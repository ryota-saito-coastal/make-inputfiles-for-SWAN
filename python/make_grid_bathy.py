import xarray as xr
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# Script to generate SWAN bathymetry from GEBCO
swn_file = "../00_outputdata/INPGRID_GRID_for_SWAN.txt"
bot_file = "../00_outputdata/SWAN_output.bot"
grd_file = "../00_outputdata/SWAN_output.grd"
bot_file_swn = "./SWAN_output.bot"
grd_file_swn = "./SWAN_output.grd"

# 1. Read GEBCO data
ds = xr.open_dataset("F:/tmp/gebco_2024_n60.0_s0.0_w100.0_e180.0.nc")
lon = ds['lon'][:].values
lat = ds['lat'][:].values
depth = ds['elevation'][:].values  # variable name may differ by file

# Range of GEBCO data
lat_min_src, lat_max_src = lat.min(), lat.max()
lon_min_src, lon_max_src = lon.min(), lon.max()

# 2. Interactively set grid area and resolution
# Using input() here; widgets could be used in Jupyter
print(f"Latitude range of GEBCO data: {lat_min_src} ~ {lat_max_src}")
print(f"Longitude range of GEBCO data: {lon_min_src} ~ {lon_max_src}")
lon_min = float(input("Grid western boundary longitude: "))
lon_max = float(input("Grid eastern boundary longitude: "))
lat_min = float(input("Grid southern boundary latitude: "))
lat_max = float(input("Grid northern boundary latitude: "))
d_lon = float(input("Longitude interval (deg): "))
d_lat = float(input("Latitude interval (deg): "))

# Validate inputs (raise if out of bounds)
if not (lat_min_src <= lat_min <= lat_max_src and lat_min_src <= lat_max <= lat_max_src):
    raise ValueError(f"Latitude range must be between {lat_min_src} and {lat_max_src}")
if not (lon_min_src <= lon_min <= lon_max_src and lon_min_src <= lon_max <= lon_max_src):
    raise ValueError(f"Longitude range must be between {lon_min_src} and {lon_max_src}")

# 3. Generate cleaned grid (avoid arange pitfalls)
def make_clean_grid(start, stop, step, datamin, datamax):
    start = max(start, datamin)
    stop = min(stop, datamax)
    N = int(round((stop - start) / step)) + 1
    arr = np.linspace(start, stop, N)
    arr = np.round(arr, 5)
    return arr

grid_lon = make_clean_grid(lon_min, lon_max, d_lon, lon.min(), lon.max())
grid_lat = make_clean_grid(lat_min, lat_max, d_lat, lat.min(), lat.max())

grid_lon2d, grid_lat2d = np.meshgrid(grid_lon, grid_lat)

print(f"GEBCO lon: {lon.min()} ~ {lon.max()}")
print(f"GEBCO lat: {lat.min()} ~ {lat.max()}")
print(f"GRID  lon: {grid_lon[0]} ~ {grid_lon[-1]}")
print(f"GRID  lat: {grid_lat[0]} ~ {grid_lat[-1]}")

# 4. Interpolate from GEBCO data
interp = RegularGridInterpolator((lat[::-1], lon), depth[::-1, :])  # note lat, lon order
points = np.stack([grid_lat2d.ravel(), grid_lon2d.ravel()], axis=-1)
depth_grid = interp(points).reshape(grid_lat2d.shape)

# Convert to SWAN bathy format
bathy_grid = np.where(depth_grid < 0, -depth_grid, 0)
bathy_grid = np.nan_to_num(bathy_grid, nan=0)  # fill NaNs with 0 if any

# 5. Visualization (optional)
# 5.1. Create mask (treat 0 specially)
masked_bathy = np.ma.masked_where(bathy_grid == 0, bathy_grid)

# 5.2. Get base colormap and insert white for land
base_cmap = plt.get_cmap('viridis')  # choose any colormap you like
colors = base_cmap(np.linspace(0, 1, 256))
cmap_with_white = ListedColormap(np.vstack(([1, 1, 1, 1], colors)))  # prepend white

# 5.3. Get maximum positive depth (for colormap range)
vmax = masked_bathy.max() if np.ma.is_masked(masked_bathy) else bathy_grid.max()

# 5.4. Configure norm
boundaries = np.concatenate(([0], np.linspace(1e-5, vmax, 256)))
norm = BoundaryNorm(boundaries, cmap_with_white.N)

# 5.5. Plot
plt.figure(figsize=(8, 6))
pcm = plt.pcolormesh(grid_lon, grid_lat, bathy_grid, cmap=cmap_with_white, norm=norm)
plt.colorbar(pcm, label="Depth [m]")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("SWAN Bathymetry (white=land)")
plt.show()

# 6. Write output
# bathy_grid: shape = (NY, NX)
with open(bot_file, "w") as f:
    for j in range(bathy_grid.shape[0]):
        line = "\t".join(f"{bathy_grid[j, i]:.4f}" for i in range(bathy_grid.shape[1]))
        f.write(line + "\n")

print('Wrote bathymetry data.')

NX = grid_lon2d.shape[1]
NY = grid_lon2d.shape[0]

with open(grd_file, "w") as f:
    # Longitudes: flatten row-wise first
    for val in grid_lon2d.flatten(order='C'):  # row-major order
        f.write(f"{val:.8f}\n")
    # Latitudes as well
    for val in grid_lat2d.flatten(order='C'):
        f.write(f"{val:.8f}\n")

print('Wrote grid data.')


lines = [
    '$*************************HEADING************************',
    f"$AUTHOR Ryota SAITO, PARI 'SWAN Bathymetry Generation'",
    '$',
    "PROJ '0' '0'",
    '$',
    '$********************MODEL INPUT*************************',
    '$',
    '$** Mode settings **',
    'MODE NONSTATIONARY TWODIMENSIONAL',
    'NUMERIC STOPC 0.005 0.01 0.005 99.5 NONSTAT 10',
    '$',
    '$** Grid settings **',
    'COORDINATES SPHE CCM',
    f'CGRID CURVILINEAR {NX - 1} {NY - 1} EXCEPTION 0 CIRCLE 36 0.05 0.5 24',
    f"READGRID COORDINATES 1 '{grd_file_swn}' 3 0 FREE",
    '$',
    '$** Bathy settings **',
    f"INPGRID BOTTOM CURVILINEAR 0 0 {NX - 1} {NY - 1} EXCEPTION 0",
    f"READINP BOTTOM 1 '{bot_file_swn}' 3 0 FREE",
    '$',
    '$** Physics settings **',
    'GEN3',
    'BREAKING',
    'FRICTION',
    'TRIADS',
    'WCAPPING',
    '$',
    '$** Wind settings ** by make_SWANforcing_fromwrfout.py ...',
    '$ (add INPGRID WIND etc. here)',
    '$',
    '$** Output settings **',
    '$',
    '$',
]

# Also print to stdout
print('\n'.join(lines))

# Write to file
with open(swn_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"\nWritten .swn template to {swn_file}.")
