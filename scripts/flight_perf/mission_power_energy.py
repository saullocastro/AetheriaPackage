""""
Author: Damien & Can & Lucas

"""

import numpy as np
import sys
import pathlib as pl
import os
import json

sys.path.append(str(list(pl.Path(__file__).parents)[2]))
os.chdir(str(list(pl.Path(__file__).parents)[2]))

from modules.flight_perf.EnergyPower import *
from modules.flight_perf.transition_model import *
import input.data_structures.GeneralConstants as const
from  ISA_tool import ISA
from input.data_structures import *
WingClass = Wing()
AeroClass = Aero()
PerformanceClass = PerformanceParameters()

WingClass.load()
AeroClass.load()
PerformanceClass.load()
    
TEST = int(input("\n\nType 1 if you want to write the JSON data to your download folder instead of the repo, type 0 otherwise:\n")) # Set to true if you want to write to your downloads folders instead of rep0
dict_directory = "input/data_structures"
dict_names = ["aetheria_constants.json"]
download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

# Loop through the JSON files
for dict_name in dict_names:
    # Load data from JSON file
    with open(os.path.join(dict_directory, dict_name)) as jsonFile:
        data = json.load(jsonFile)

    atm = ISA(const.h_cruise)
    rho_cr = atm.density()
    #==========================Energy calculation ================================= 

    #----------------------- Take-off-----------------------
    
    P_takeoff = powertakeoff(data["mtom"], const.g0, const.roc_hvr, data["diskarea"], const.rho_sl)
    E_to = P_takeoff * const.t_takeoff
    

    #-----------------------Transition to climb-----------------------
    
    transition_simulation = numerical_simulation(y_start=30.5, mass=data["mtom"], g0=const.g0, S=data['S'], CL_climb=data['cl_climb_clean'],
                                alpha_climb=data['alpha_climb_clean'], CD_climb=data["cdi_climb_clean"] + data["cd0"],
                                Adisk=data["diskarea"], lod_climb=data['ld_climb'], eff_climb=data['eff'], v_stall=data['v_stall'])
    E_trans_ver2hor = transition_simulation[0]
    transition_power_max = np.max(transition_simulation[0])
    final_trans_distance = transition_simulation[3][-1]
    final_trans_altitude = transition_simulation[1][-1]
    t_trans_climb = transition_simulation[2][-1]
    

    #----------------------- Horizontal Climb --------------------------------------------------------------------
    # print("-------- horizontal climb")
    average_h_climb = (const.h_cruise  - final_trans_altitude)/2
    rho_climb = ISA(average_h_climb).density()
    v_climb = const.roc_cr/np.sin(const.climb_gradient)
    v_aft= v_exhaust(data["mtom"], const.g0, rho_climb, data["mtom"]/data["diskloading"], v_climb)
    prop_eff_var = propeff(v_aft, v_climb)
    climb_power_var = powerclimb(data["mtom"], const.g0, data["S"], rho_climb, AeroClass.ld_climb, prop_eff_var, const.roc_cr)
    t_climb = (const.h_cruise  - final_trans_altitude) / const.roc_cr
    # print('v', v_climb)
    E_climb = climb_power_var * t_climb
    print('E', E_climb)
    
    #----------------------- Transition (from horizontal to vertical)-----------------------
    # print("--------------- transition to vertical")
    transition_simulation_landing = numerical_simulation_landing(vx_start=data['v_stall_flaps20'], descend_slope=-0.04, mass=data["mtom"], g0=const.g0,
                                S=data['S'], CL=data['cl_descent_trans_flaps20'], alpha=data['alpha_descent_trans_flaps20'],
                                CD=data["cdi_descent_trans_flaps20"]+data['cd0'], Adisk=data["diskarea"])
    E_trans_hor2ver = transition_simulation_landing[0]
    transition_power_max_landing = np.max(transition_simulation_landing[4])
    final_trans_distance_landing = transition_simulation_landing[3][-1]
    final_trans_altitude_landing = transition_simulation_landing[1][-1]  
    t_trans_landing = transition_simulation_landing[2][-1]
    # print('t', t_trans_landing)


        # ----------------------- Horizontal Descend-----------------------
    P_desc = powerdescend(data["mtom"], const.g0, WingClass.surface, rho_climb, AeroClass.ld_climb, prop_eff_var, const.rod_cr)
    t_desc = (const.h_cruise - final_trans_altitude_landing)/const.rod_cr # Equal descend as ascend
    E_desc = P_desc* t_desc
    d_desc = (const.h_cruise - final_trans_altitude_landing)/const.descent_slope
    v_descend = const.rod_cr/const.descent_slope
    # print("v_desc",v_descend)

    #-----------------------------Cruise-----------------------
    # print('-------- cruise')
    P_cr = powercruise(data["mtom"], const.g0, const.v_cr, AeroClass.ld_cruise, prop_eff_var)
    d_climb = final_trans_distance + (const.h_cruise  - final_trans_altitude)/np.tan(const.climb_gradient) #check if G is correct
    d_cruise = const.mission_dist - d_desc - d_climb - final_trans_distance - final_trans_distance_landing
    t_cr = (const.mission_dist - d_desc - d_climb - final_trans_distance - final_trans_distance_landing)/const.v_cr
    E_cr = P_cr * t_cr
    # print('t', t_cr)
    # print('distance', (const.mission_dist - d_desc - d_climb - final_trans_distance_landing))

    #----------------------- Loiter cruise-----------------------
    # print('--------- loiter cruise')
    P_loit_cr = powerloiter(data["mtom"], const.g0, WingClass.surface, const.rho_cr, AeroClass.ld_climb, prop_eff_var)
    E_loit_hor = P_loit_cr * const.t_loiter
    # print('t', const.t_loiter)

    #----------------------- Loiter vertically-----------------------
    # print('------ loiter vertically')
    P_loit_land = hoverstuffopen(data["mtom"]*const.g0, const.rho_sl, data["mtom"]/data["diskloading"],data["TW"])[1]
    E_loit_vert = P_loit_land * 30 # 30 sec for hovering vertically
    # print('t', 30)

    #----------------------- Landing----------------------- 
    # print('----------- landing')
    # landing_power_var = hoverstuffopen(data["mtom"]*const.g0, const.rho_sl, data["mtom"]/data["diskloading"],data["TW"])[1]
    energy_landing_var = 0

    #---------------------------- TOTAL ENERGY CONSUMPTION ----------------------------
    E_total = E_to + E_trans_ver2hor + E_climb + E_cr + E_desc + E_loit_hor + E_loit_vert + E_trans_hor2ver + energy_landing_var
    
    #---------------------------- Writing to JSON and printing result  ----------------------------
    data["mission_energy"] = E_total
    data["power_hover"] = P_takeoff
    data["power_climb"] = climb_power_var
    data["power_cruise"] = P_cr 
    data["diskarea"] = data["mtom"]/data["diskloading"]

    data["takeoff_energy"] = E_to
    data["trans2hor_energy"] = E_trans_ver2hor
    data["climb_energy"] = E_climb
    data["cruise_energy"] = E_cr
    data["descend_energy"] = E_desc
    data["hor_loiter_energy"] = E_loit_hor
    data["trans2ver_energy"] = E_trans_hor2ver
    data["ver_loiter_energy"] = E_loit_vert
    
    
    with open(os.path.join(dict_directory, dict_name), "w") as jsonFile:
        json.dump(data, jsonFile, indent= 6)
    
    print(f"Energy consumption {data['name']} = {round(E_total/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_to/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_trans_hor2ver/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_climb/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_cr/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_desc/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption loit {data['name']} = {round((E_loit_hor+E_loit_vert)/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_trans_hor2ver/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(E_loit_vert/3.6e6, 1)} [Kwh]")
    print(f"Energy consumption {data['name']} = {round(energy_landing_var/3.6e6, 1)} [Kwh]")

