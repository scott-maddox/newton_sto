# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

class Cell(object):
    def __init__(self, id, shutter, primary, idle, ramprate, Ea,
                 secondary=None, diff=None):
        '''
        id = identifying name e.g. "Ga"
        shutter = shutter name e.g. "Ga"
        primary = primary temperature name e.g. "GaTip"
        idle = idle temperature, e.g. 350
        ramprate = temperature ramprate, e.g. 10
        secondary = secondary temperature name if any e.g. "GaBase", None
                    otherwise
        diff = temperature difference (secondary - primary), e.g. -150
        '''
        super(Cell, self).__init__()
        self.id = id
        self.shutter = str(shutter)
        self.primary = str(primary)
        self.idle = idle
        self.ramprate = ramprate
        self.Ea = Ea
        if secondary is not None:
            self.dual = True
            self.secondary = str(secondary)
            assert diff is not None
            self.diff = diff
            self.t2 = self.secondary
        else:
            self.dual = False
            self.diff = None
