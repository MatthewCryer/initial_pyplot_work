# initial_pyplot_work
I was doing electrical device measurements that varied in a small number of ways and I wanted to write some code that plotted them all without any intervention from me. Takes the .xls outputs from a **Keithley SCS 4200** as a starting point.

In **SCS4200.py**

The variables were things like: 
- Sweep direction (or both ways)
- Current vs Time, or vs Voltage
- Multiple sweeps with different gate voltages (or multiple voltage sweeps at one gate voltage)

...it turns out that I basically spent a lot of time re-writing a highly limited and worse version of pandas from the ground up.

It makes good coders cry.

In **gradchange.py** 

Takes the same framework but is looking at a value changing over time. Uses simple statistics to identify when the gradient change is *x* sigma away from the mean, and then annotates the y value of this point on the plot.
