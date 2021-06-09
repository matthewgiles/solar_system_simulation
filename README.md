This simulation is designed to simulate the inner solar system. When the simulation is run, a target body and probe body should be specified. The simulation is designed to help the user find the best initial positions and velocities for sending the probe towards the target. For example, I tried to send the Viking Probe from just above Earth to Mars.

The simulation requires data about the bodies it should model, the number of iterations it should run for and the time step (in seconds) that each iteration corresponds to. These details should be entered into a text file, such as `many_body_data.txt`. The file takes the following format:

```
no_iterations timestep
Name Colour Nominal_Size Mass X_Pos Y_Pos X_Velocity Y_Velocity
Name Colour Nominal_Size Mass X_Pos Y_Pos X_Velocity Y_Velocity
```

where each line after the first corresponds to a celestial body.

The simulation must be initialised by passing it the filename. It can then be run by calling `run` which requires arguments of the scale on which to run the simulation in metres (such as 10e9), the name of the file that energy data should be output to, and the index in the list of celestial bodies first for the target and then for the probe. If you wish for it to be animated pass True in as the final argument.
