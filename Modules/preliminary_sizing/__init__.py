import sys
import os
import pathlib as pl

sys.path.append(str(list(pl.Path(__file__).parents)[2]))

from input.MainConstants import *
from .powerloading import *
from .wingloading import *