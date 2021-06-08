#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 04 22:34:24 2021

@author: Matthew

This code tests the simulation and produces graphs to ensure energy conservation, and shows the relationship
between a probes initial velocity and its closest approach to a target.
"""
import numpy as np
import matplotlib.pyplot as plt
from simulation import Simulation

# The line in the bodies file to add in the probe, but with the inital velocity omitted
PROBE_BASE = "Viking_Probe black 0.75 3000 149597970700 384400000 "

SECONDS_IN_EARTH_DAY = 86400

class GenerateGraphs(object):
    """This class provides methods to generate graphs from data taken from the simulation."""

    def __init__(self, body_file):
        # Store the file in which the body data is stored
        self.__body_file = body_file
    
    def __calculate_times_and_distances(self, lower, upper, step, v_y, target, probe):
        """This method calculates the time taken for the probe to reach its closest approach to the target, and the distance
        of this approach for a range of initial velocities. We are varying the velocity in the x direction, so a constant
        value for the y direction is passed as an argument."""

        # Read in the body data file
        lines = open(self.__body_file, "r").readlines()

        v_xs = []
        times = []
        distances = []
        
        """Iterate the initial velocity in the x direction from lower to upper in increments of step. Overwrite the last
        line of the file with velocity of the iteration, then run the simulation. Append to times and distances the values
        calculated in the simulations."""
        for v_x in range(lower, upper, step):
            lines[probe + 1] = PROBE_BASE + str(v_x) + " " + str(v_y)
            open(self.__body_file, "w").writelines(lines)
            
            sim = Simulation(self.__body_file)
            sim.run(10e10, "test_energy.txt", target, probe)
            
            v_xs.append(v_x)
            times.append(sim.get_approach_time())
            distances.append(sim.get_closest_approach())

        return (v_xs, times, distances)
    
    def x_velocity_graphs(self, lower, upper, step, v_y, target, probe):
        """This function produces graphs to show the variation of time and distance of closest approach against the
        initial velocity in the x direction."""

        # Get the data by running the simulation for a range of initial velocities
        v_xs, times, distances = self.__calculate_times_and_distances(lower, upper, step, v_y, target, probe)

        # Generate the plot of distance of closest approach against initial x velocity
        plt.figure(figsize = (9, 9))
        y_values = np.array(distances) / min(distances) # Give the distances relative to the lowest distance from Mars
        plt.scatter(v_xs, y_values)
        plt.plot(v_xs, y_values)
        plt.title("A graph of the probe's closest distance from the target against it's initial velocity in the positive x direction.")
        plt.xlabel("Initial Velocity in Positive X (ms^-1)")
        plt.ylabel("Distance From Mars (1/" + str(min(distances) // 1000) + " km)")
        plt.show()

        # Generate the plot of time of closest approach against initial x velocity
        plt.figure(figsize = (11, 9))
        y_values = np.array(times) / SECONDS_IN_EARTH_DAY
        plt.scatter(v_xs, y_values)
        plt.plot(v_xs, y_values)
        plt.title("A graph of the time taken for the probe to pass closest to the target against it's initial velocity in the positive x direction.")
        plt.xlabel("Initial Velocity in Positive X (ms^-1)")
        plt.ylabel("Time (Earth Days)")
        plt.show()
    
    def energy_time_graph(self, energy_file):
        """This method takes as input a file containing energies and times and plots each coordinate."""
        lines = open(energy_file, 'r').readlines()
        times = []
        energies = []

        # Each line corresponds to an energy and a time separated by a space. Split them and append each part to a list.
        for line in lines:
            line.strip()
            time, energy = line.split(" ")
            times.append(float(time))
            energies.append(energy)
        
        # Plot a graph of energy against time.
        plt.figure(figsize = (20, 10))
        times = np.array(times) / SECONDS_IN_EARTH_DAY
        plt.scatter(times, energies)
        plt.plot(times, energies)
        plt.title("A graph of the simulation's total energy against time.")
        plt.xlabel("Time (Earth Days)")
        plt.ylabel("Energy (J)")
        plt.show()

        # Find the percentage change in energy from start to end of the file.
        print("Percentage Change in Energy:", (float(energies[0]) - float(energies[-1])) / float(energies[0]) * 100)


sim = Simulation('many_body_data.txt')
sim.run(10e10, "energy.txt", 2, 5, True)

generator = GenerateGraphs('many_body_data.txt')

generator.x_velocity_graphs(8000, 20000, 1000, 30000, 2, 5)
generator.x_velocity_graphs(10000, 11000, 100, 30000, 2, 5)
generator.x_velocity_graphs(10600, 10700, 5, 30000, 2, 5)

generator.energy_time_graph('energy.txt')
