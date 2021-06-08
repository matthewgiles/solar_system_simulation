To run the code, enter the details for the simulation into a text file. It takes the following format:

```
no_iterations timestep
Name Colour Nominal_Size Mass X_Pos Y_Pos X_Velocity Y_Velocity
Name Colour Nominal_Size Mass X_Pos Y_Pos X_Velocity Y_Velocity
```

where each line after the first corresponds to a celestial body.

The simulation must be initialised by passing it the filename. It can then be run by calling `run` and passing it the scale on which to run the simulation (such as 10e9), the name of the file that energy data should be output to, and the index in the list of celestial bodies first for the target and then for the probe. If you wish for it to be animated pass True in as the final argument.
