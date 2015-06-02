# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

from .cell import Cell

# System and cell definitions/configurations
systems = {
    'Bravo' : {
               'In' : Cell(id='In', shutter='In',
                           primary='InTip', idle=350, ramprate=5, Ea=2.7,
                           secondary='InBase', diff= -175),
               'Ga' : Cell(id='Ga', shutter='Ga',
                           primary='GaTip', idle=350, ramprate=10, Ea=3.2,
                           secondary='GaBase', diff= -150),
               'Al' : Cell(id='Al', shutter='Al', ramprate=10, Ea=3.0,
                           primary='AlBase', idle=800),
              },
    'Echo'  : {
                'In' : Cell(id='In', shutter='In',
                           primary='InTip', idle=350, ramprate=10, Ea=2.7,
                           secondary='InBase', diff= -150),
                'Ga' : Cell(id='Ga', shutter='Ga', ramprate=10, Ea=3.2,
                           primary='GaTip', idle=350,
                           secondary='GaBase', diff= -150),
              }
}
