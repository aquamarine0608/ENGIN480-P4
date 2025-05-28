from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80, wt_x, wt_y, wt16_x, wt16_y
from py_wake import NOJ
from py_wake.site import UniformWeibullSite
import numpy as np
import geopandas as gpd
from py_wake.wind_turbines._wind_turbines import WindTurbine
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular

###################################################################################################################################
def get_coords(file_path, epsg):
    # Load the GeoJSON layout
    layout_gdf = gpd.read_file(file_path)

    layout_gdf = layout_gdf.to_crs(epsg)

    #2249 for vineyard and revolution
    #2283 for coastal virginia
    #4326 for sofia

    # Extract the LineString coordinates
    turbine_coords = []

    for geom in layout_gdf.geometry:
        if geom.geom_type == 'LineString':
            coords = list(geom.coords)
            turbine_coords.extend(coords)
        elif geom.geom_type == 'MultiLineString':
            for line in geom:
                turbine_coords.extend(list(line.coords))

    # Separate x and y
    x, y = zip(*turbine_coords)
    x = np.array(x)
    y = np.array(y)

    return (x, y)
###################################################################################################################################

HaliadeX13 = GenericWindTurbine('G13MW', 220, 150, power_norm=13000, turbulence_intensity=.1) #vineyard wind
SG_11200DD = GenericWindTurbine('G11MW', 200, 140, power_norm=11000, turbulence_intensity=.1) #revolution southfork
SG_14222DD = GenericWindTurbine('G11MW', 222, 140, power_norm=14000, turbulence_intensity=.1) #coastal virginia & sofia

class VineyardWind(UniformWeibullSite):
    def __init__(self, ti=0.1, shear=None):
        f = np.array([560.41, 419.61, 480.66, 638.61, 625.46, 667.67, 1029.07, 1282.98, 1340.08, 1123.80, 969.42, 862.23]) #Line 6
        a = np.array([10.26, 10.44, 9.52, 8.96, 9.58, 9.72, 11.48, 13.25, 12.46, 11.40, 12.35, 10.48]) #Line 12
        k = np.array([2.225, 1.697, 1.721, 1.689, 1.525, 1.498, 1.686, 2.143, 2.369, 2.186, 2.385, 2.404]) #Line 13
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)

class RevolutionSouthFork(UniformWeibullSite):
    def __init__(self, ti=0.1, shear=None):
        f = np.array([652.94, 745.53, 622.32, 588.86, 474.39, 456.32, 717.71, 1225.30, 1385.41, 1037.11, 1158.19, 935.93]) #Line 6
        a = np.array([10.01, 10.75, 9.95, 8.96, 9.03, 8.41, 10.96, 12.56, 12.20, 11.48, 12.68, 10.26]) #Line 12
        k = np.array([2.318, 1.771, 1.881, 1.725, 1.521, 1.346, 1.635, 2.002, 2.393, 2.213, 2.885, 2.490]) #Line 13
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)

class CoastalVirgina(UniformWeibullSite):
    def __init__(self, ti=0.1, shear=None):
        f = np.array([919.38, 990.99, 908.17, 525.05, 482.52, 572.45, 1149.10, 1424.91, 930.86, 506.00, 646.52, 944.05]) #Line 6
        a = np.array([10.50, 9.94, 8.96, 8.22, 7.34, 7.94, 11.27, 13.33, 11.86, 10.03, 10.26, 11.12]) #Line 12
        k = np.array([2.260, 2.139, 1.971, 1.771, 1.521, 1.514, 1.955, 2.568, 2.775, 2.049, 1.951, 2.295]) #Line 13
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)

class Sofia(UniformWeibullSite):
    def __init__(self, ti=0.1, shear=None):
        f = np.array([560.41, 419.61, 480.66, 638.61, 625.46, 667.67, 1029.07, 1282.98, 1340.08, 1123.80, 969.42, 862.23]) #Line 6
        a = np.array([9.54, 8.11, 9.23, 11.05, 10.78, 11.29, 12.05, 13.55, 13.60, 12.66, 11.18, 10.72]) #Line 12
        k = np.array([2.146, 1.740, 2.338, 2.127, 2.053, 2.381, 1.826, 2.096, 2.361, 2.111, 2.088, 2.123]) #Line 13
        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)


#here we import the turbine, site and wake deficit model to use.
windTurbines = HaliadeX13
site = VineyardWind()

noj = NOJ(site,windTurbines)

xvine, yvine = get_coords("vineyard.geojson", 2249)
xrevsfk, yrevsfk = get_coords("revolution_southfork.geojson", 2249)
xcoast, ycoast = get_coords("coastal_virginia.geojson", 2283)
xsofia, ysofia = get_coords("sofia.geojson", 4326)


simulationResult = noj(xvine, yvine)
simulationResult.aep()

print ("Total AEP: %f GWh"%simulationResult.aep().sum())

import matplotlib.pyplot as plt

plt.figure()
aep = simulationResult.aep()
windTurbines.plot(xvine,yvine)
c =plt.scatter(xvine, yvine, c=aep.sum(['wd','ws']))
plt.colorbar(c, label='AEP [GWh]')
plt.title('AEP of each turbine')
plt.xlabel('x [m]')
plt.ylabel('[m]')

plt.figure()
aep.sum(['wt','wd']).plot()
plt.xlabel("Wind speed [m/s]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind speed')

plt.figure()
aep.sum(['wt','ws']).plot()
plt.xlabel("Wind direction [deg]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind direction')

wind_speed = 13
wind_direction = 270


flow_map = simulationResult.flow_map(ws=wind_speed, wd=wind_direction)
plt.figure(figsize=(18,10))
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.show()
