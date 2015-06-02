# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

class Target(object):
    def __init__(self, cell, BEP, Tguess):
        super(Target, self).__init__()
        self.cell = cell
        self.BEP = BEP
        self.Tguess = Tguess
        self.T_var = '%s_T' % self.cell.id
        self.Tdiff_var = '%s_Tdiff' % self.cell.id
        self.Tmax_var = '%s_Tmax' % self.cell.id
        self.Tmin_var = '%s_Tmin' % self.cell.id
        self.BEP_var = '%s_BEP' % self.cell.id
        self.Tguess_var = '%s_Tguess' % self.cell.id
        self.Ea_var = '%s_Ea' % self.cell.id
