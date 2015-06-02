# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

import sys
import StringIO

# System and cell definitions/configurations
from .system_config import systems

# Calculte measure_wait
def generate_sto(targets,
            bf_var="bf",
            num_temps=4,
            num_shutterings=3,
            num_samples=3,
            temp_tolerance=0.2,
            update_time=10):
    '''
    Generates an AMBER source turn on (STO) recipe that uses the Newton iteration
    method, assuming an Arrhenius relationship, to find the cell temperature that
    provides a desired beam equivalent pressure (BEP).

    Basic operation:
    1. Ramp to initial guess temperature.
    2. Measure the BEP several times and take the average.
    3. Calculate a new temperature guess using the last measurement and the
       activation energy for the cell (defined by the user).
    4. Ramp to the new guessed temperature.
    5. Repeat steps 2-4 as many times as desired.
    '''
    old_stdout = sys.stdout
    sys.stdout = StringIO.StringIO()

    measure_wait = update_time * 2.5
    # Define variables
    print "! *** Define Variables ***"
    print "! *** Note: if you change Tguess, you should fix the ramp up time"
    for target in targets:
        print "eval %s=%.3E" % (target.BEP_var, target.BEP)
        print "eval %s=%.1f" % (target.Tguess_var, target.Tguess)
        print "eval %s=%.1f" % (target.Tmin_var, target.Tguess - 50)
        print "eval %s=%.1f" % (target.Tmax_var, target.Tguess + 50)
        print "eval %s=%.2f" % (target.Ea_var, target.cell.Ea)
        if target.cell.diff is not None:
            print "eval %s=%.1f" % (target.Tdiff_var, target.cell.diff)
        print ""

    # Define structures (AKA subroutines)
    print "! *** Define structures ***"
    shutters = [target.cell.shutter for target in targets]
    comma_separated_shutters = ','.join(shutters)
    print "structure (pregetter)"
    print "  repeat 5"
    print "    open %s" % comma_separated_shutters
    print "    wait 30"
    print "    close %s" % comma_separated_shutters
    print "    wait 30"
    print "  er"
    print "es"
    print ""

    for target in targets:
        print "structure (getter_%s)" % (target.cell.id)
        print "  repeat 3"
        print "    open %s" % target.cell.shutter
        print "    wait 10"
        print "    close %s" % target.cell.shutter
        print "    wait 10"
        print "  er"
        print "es"
        print ""

    for target in targets:
        print "structure (ramp_%s)" % (target.cell.id)
        print "    eval low = step(%s-%s)" % (target.Tmin_var, target.T_var)
        print "    eval high = step(%s-%s)" % (target.T_var, target.Tmax_var)
        print "    eval %s = %s*(1-low)+%s*low" % (target.T_var, target.T_var,
                                                target.Tmin_var)
        print "    eval %s = %s*(1-high)+%s*high" % (target.T_var, target.T_var,
                                                   target.Tmax_var)
        print "    t %s=%s" % (target.cell.primary, target.T_var)
        print "es"
        print ""

    for target in targets:
        print "structure (wait_%s)" % (target.cell.id)
        print "    waituntil ( %s-%.1f < %s < %s+%.1f ) 30" % (target.T_var,
                                                             temp_tolerance,
                                                             target.cell.primary,
                                                             target.T_var,
                                                             temp_tolerance)
        if target.cell.dual:
            print "    waituntil ( %s+%s-%.1f < %s < %s+%s+%.1f ) 30" % (
                                                            target.T_var,
                                                            target.Tdiff_var,
                                                            temp_tolerance,
                                                            target.cell.secondary,
                                                            target.T_var,
                                                            target.Tdiff_var,
                                                            temp_tolerance)
        print "    wait 00:02:00"
        print "es"
        print ""

    # Write flux log headers
    print "! *** Write flux log headers ***"
    for target in targets:
        print 'writefile (%sFluxes; "#Cell=%s")' % (target.cell.id, target.cell.id)
        print 'writefile (%sFluxes; "#T\tBG\tP\tBEP")' % (target.cell.id)
    print ""

    # Ramp to initial temperature
    print "! *** Ramp to initial temperature ***"
    print "comment (Ramp to initial temperature)"
    # calculate the ramp times for each cell
    ramptimes = [int((target.Tguess - target.cell.idle)
                     / target.cell.ramprate * 60)
                for target in targets]
    ramptimes_and_targets = zip(ramptimes, targets)
    ramptimes_and_targets.sort(reverse=True)  # sort in place
    for i in xrange(len(ramptimes_and_targets) - 1):
        ramptime, target = ramptimes_and_targets[i]
        next_ramptime, next_target = ramptimes_and_targets[i + 1]
        waittime = ramptime - next_ramptime
        print "! %s takes %d sec to ramp up" % (target.cell.id, ramptime)
        print "eval %s=%s" % (target.T_var, target.Tguess_var)
        print "ramp_%s" % (target.cell.id)
        print "wait %d" % (waittime)
    ramptime, target = ramptimes_and_targets[-1]
    waittime = ramptime
    print "! %s takes %d sec to ramp up" % (target.cell.id, ramptime)
    print "eval %s=%s" % (target.T_var, target.Tguess_var)
    print "ramp_%s" % (target.cell.id)
    print "wait %d" % (ramptime)
    print "! stabilize for an hour"
    print "wait 01:00:00"
    print ""

    # Initial getter
    print "! *** Initial getter ***"
    print "comment (Initial getter)"
    print "pregetter"
    print ""

    # Wait to stabilize, measure the BEP 5 times, then start ramping to the
    # next temperature while doing the same for the next cell
    def take_measurement(target, i):
        id = target.cell.id
        BEP_acc = "%s_BEP_%d_acc" % (id, i)  # BEP accumulator
        BEP_avg = "%s_BEP_%d_avg" % (id, i)  # BEP average
        print "! *** %s stabilizing %d ***" % (id, i)
        print "comment (%s stabilizing %d )" % (id, i)
        print "wait_%s" % (id)
        print "getter_%s" % (id)
        print "eval %s_%d=%s" % (target.T_var, i, target.T_var)
        print "eval %s=0" % BEP_acc  # initialize the BEP accumulator
        print ""

        # Measure the BEP num_shutterings times, and write the values to the
        # flux log
        for j in xrange(1, num_shutterings + 1):
            print "! *** %s measurement %d - %d ***" % (id, i, j)
            print "comment (%s measurement %d - %d)" % (id, i, j)
            T = target.T_var
            print "open %s" % target.cell.shutter
            for k in xrange(1, num_samples + 1):
                if k == 1:
                    print "wait %d" % measure_wait
                else:
                    print "wait %d" % update_time
                P = "%s_P_%d_%d_%d" % (id, i, j, k)
                print "eval %s=%s" % (P, bf_var)
            print "close %s" % target.cell.shutter
            for k in xrange(1, num_samples + 1):
                if k == 1:
                    print "wait %d" % measure_wait
                else:
                    print "wait %d" % update_time
                P = "%s_P_%d_%d_%d" % (id, i, j, k)
                BG = "%s_BG_%d_%d_%d" % (id, i, j, k)
                BEP = "%s_BEP_%d_%d_%d" % (id, i, j, k)
                print "eval %s=%s" % (BG, bf_var)
                print "eval %s=%s-%s" % (BEP, P, BG)
                print "eval %s=%s+%s" % (BEP_acc, BEP_acc, BEP)
                print "writefile (%sFluxes; %s, %s, %s, %s)" % (id, T, BG, P, BEP)
            print ""

        # Calculate the average
        print "! *** %s calculate average BEP %d ***" % (id, i)
        print "comment (%s calculate average BEP %d)" % (id, i)
        print "eval %s=%s/%d/%d" % (BEP_avg, BEP_acc, num_shutterings,
                                    num_samples)
        print ""

    # def calculate_Ea(target, i):
    #     id = target.cell.id
    #     Ts = ["%s_%d" % (target.T_var, j) for j in xrange(1, i + 1)]
    #     BEPs = ["%s_BEP_%d_avg" % (id, j) for j in xrange(1, i + 1)]
    #     csTs = ','.join(Ts)
    #     csBEPs = ','.join(BEPs)
    #     print "! *** %s calculate Ea %d ***" % (id, i)
    #     print "comment (%s calculate Ea %d)" % (id, i)
    #     print "fitexp (%s;%s;Amp,Ea_%d)" % (csTs, csBEPs, i)
    #     print ""

    # def calculate_median(target, i):
    #     id = target.cell.id
    #     for j in range(1, num_temps + 1):
    #         for k in range(1, j) + range(j, num_temps + 1):
    #             jBEP = "%s_BEP_%d_%d" % (id, i, j)
    #             kBEP = "%s_BEP_%d_%d" % (id, i, k)
    #             # 1 (True) if jBEP > kBEP:
    #             print "eval bool_%s_BEP_%d_%d_gt_%d=st(%s-%s)" % (id, i, j, k,
    #                                                               jBEP, kBEP)
    #     print "eval bool_%s_%d_is_median=st(" % (id, i)

    def calculate_guess(target, i):
        id = target.cell.id
        # Calculate a new Amp from the most resent data point
        T = "%s_%d" % (target.T_var, i)
        BEP = "%s_BEP_%d_avg" % (id, i)  # BEP average
        print "! *** %s calculate guess %d ***" % (id, i + 1)
        print "comment (%s calculate guess %d)" % (id, i + 1)
        print "eval Amp_%d=%s*exp(%s/(8.617385E-5*(%s+273.15)))" % (i, BEP,
                                                                    target.Ea_var,
                                                                    T)
        # Calculate a new Tguess from Ea and the new Amp
        print "eval %s=-%s/(8.617385E-5*ln(%s/Amp_%d))-273.15" % (
                                                            target.Tguess_var,
                                                            target.Ea_var,
                                                            target.BEP_var, i)
        print ""


    # start looping through the iterations:
    # 1. measure
    # 2. calculate new guess
    # 3. ramp to guess
    for i in xrange(1, num_temps + 1):
        for target in targets:
            id = target.cell.id

            # measure
            take_measurement(target, i)
            calculate_guess(target, i)

            # ramp to Tguess
            print "! *** %s ramp to guess %d ***" % (id, i + 1)
            print "comment (%s ramp to guess %d)" % (id, i + 1)
            print "eval %s=%s" % (target.T_var, target.Tguess_var)
            print "ramp_%s" % (target.cell.id)
            print ""

    result = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return result
