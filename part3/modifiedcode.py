import importlib
import os
import time
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from hydesign.assembly.hpp_assembly import hpp_model
from hydesign.examples import examples_filepath

# Load example site metadata
examples_sites = pd.read_csv(f'{examples_filepath}examples_sites.csv', index_col=0, sep=';')
name = 'France_good_wind'
ex_site = examples_sites.loc[examples_sites.name == name]

longitude = ex_site['longitude'].values[0]
latitude = ex_site['latitude'].values[0]
altitude = ex_site['altitude'].values[0]

# Load time series and filter out wind direction columns
input_ts_fn = examples_filepath + ex_site['input_ts_fn'].values[0]
input_ts = pd.read_csv(input_ts_fn, index_col=0, parse_dates=True)
input_ts = input_ts[[col for col in input_ts.columns if 'WD' not in col]]

# Load simulation parameters
sim_pars_fn = examples_filepath + ex_site['sim_pars_fn'].values[0]
with open(sim_pars_fn) as file:
    sim_pars = yaml.load(file, Loader=yaml.FullLoader)

# Modified design parameters (smaller turbines, more solar-heavy)
rotor_diameter_m = 150              # Smaller turbine rotor
hub_height_m = 100
wt_rated_power_MW = 5               # Smaller turbine capacity

surface_tilt_deg = 25               # Optimized tilt for solar energy
surface_azimuth_deg = 180
DC_AC_ratio = 1.3                   # Reduced DC:AC to limit inverter oversizing

# Initialize HPP model
hpp = hpp_model(
    latitude=latitude,
    longitude=longitude,
    altitude=altitude,
    rotor_diameter_m=rotor_diameter_m,
    hub_height_m=hub_height_m,
    wt_rated_power_MW=wt_rated_power_MW,
    surface_tilt_deg=surface_tilt_deg,
    surface_azimuth_deg=surface_azimuth_deg,
    DC_AC_ratio=DC_AC_ratio,
    num_batteries=8,                # Increased battery count
    work_dir='./',
    sim_pars_fn=sim_pars_fn,
    input_ts_fn=input_ts_fn,
)

start = time.time()

# Modified system setup: prioritize solar
Nwt = 10                            # Fewer wind turbines
wind_MW_per_km2 = 5                # Less wind capacity density
solar_MW = 250                      # Increase solar capacity
b_P = 40                            # Higher battery power (MW)
b_E_h = 6                           # Longer storage duration (hours)
cost_of_batt_degr = 10             # Increased battery degradation cost

clearance = hub_height_m - rotor_diameter_m / 2
sp = 4 * wt_rated_power_MW * 10**6 / np.pi / rotor_diameter_m**2

x = [
    clearance, sp, wt_rated_power_MW, Nwt, wind_MW_per_km2,
    solar_MW, surface_tilt_deg, surface_azimuth_deg, DC_AC_ratio,
    b_P, b_E_h, cost_of_batt_degr
]

outs = hpp.evaluate(*x)
hpp.print_design(x, outs)

end = time.time()
print(f'Execution time [min]: {(end - start) / 60:.2f}')
