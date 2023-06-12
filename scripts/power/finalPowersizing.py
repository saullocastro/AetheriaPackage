#import statements
import numpy as np
import sys
import pathlib as pl
import os

sys.path.append(str(list(pl.Path(__file__).parents)[2]))
os.chdir(str(list(pl.Path(__file__).parents)[2]))

from input.data_structures import Battery, FuelCell, HydrogenTank
from input.data_structures.performanceparameters import PerformanceParameters
from modules.powersizing.powersystem import PropulsionSystem
from input.data_structures.fluid import Fluid
from input.data_structures.radiator import Radiator

#loading data
IonBlock = Battery(Efficiency= 0.9)
Pstack = FuelCell()
Tank = HydrogenTank(energyDensity=1.8e3, volumeDensity=0.6, cost= 16)
Mission = PerformanceParameters()
Mission.load()

#estimate power system mass
nu = np.arange(0,1,0.005)
Totalmass, Tankmass, FCmass, Batterymass= PropulsionSystem.mass(echo= np.copy(nu),
                             Mission= Mission,
                             Battery=IonBlock,
                             FuellCell= Pstack,
                             FuellTank= Tank )

index_min_mass = np.where(Totalmass == min(Totalmass))
NU = nu[index_min_mass][0]
powersystemmass = Totalmass[index_min_mass][0]
Batterymass = Batterymass[index_min_mass][0]
fuelcellmass = Pstack.mass






print(f"nu: {NU}")
print(f"mass: {powersystemmass} kg")
print(f"battery mass: {Batterymass} kg")