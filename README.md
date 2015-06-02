A Python-Flask web app that generates Newton STO recipes for AMBER


[AMBER](http://mbecontrol.com/amber/) is a popular molecular beam epitaxy (MBE)
process control software package that accepts script-like process recipes.
This web app generates source turn on (STO) recipes that use Newton iteration
to automatically adjust effusion cell temperatures to acheive a desired beam
equivalent pressure (BEP) as measured by a hot-filament ionization gauge.


The STO recipe does the following for each cell:
1. Ramp to initial guess temperature.
2. Measure the BEP several times and take the average.
3. Calculate a new temperature guess using the last measurement and the
   activation energy for the cell (defined by the user).
4. Ramp to the new guessed temperature.
5. Repeat steps 2-4 as many times as desired.

The loops for each cell are interleaved so that one cell can be measured
while another is ramping to the new temperature.