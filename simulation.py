#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 06 14:30:13 2021

@author: Matthew

This code simulates the interaction between celestial bodies in 
the inner solar system, using numerical integration
"""

import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the universal gravitational constant
G = 6.67e-11

# Define the number of seconds in a single orbit of the Earth
SECONDS_IN_EARTH_YEAR = 31557600

class CelestialBody(object):

    def __init__(self, name, colour, size, mass, pos_x, pos_y, v_x, v_y):
        """For the body store its name, colour and nominal size in the animation, mass, initial position and 
        initial velocity as provided. Set the initial acceleration to (0,0)"""
        self.__name = name
        self.__colour = colour
        self.__size = float(size)
        self.__previous_acceleration = self.__current_acceleration = np.array([0, 0], dtype = float)
        self.__mass = float(mass)
        self.__position = np.array([pos_x, pos_y], dtype = float)
        self.__velocity = np.array([v_x, v_y], dtype = float)
        self.__period = None # Initially we don't know the oribtal period
    
    def get_mass(self):
        return self.__mass
    
    def get_size(self):
        return self.__size

    def get_name(self):
        return self.__name
    
    def get_period(self):
        return self.__period
    
    def get_colour(self):
        return self.__colour

    def get_position(self):
        return self.__position

    def update_acceleration(self, a, first):
        # If this is the first iteration, then the previous iteration can be approximated to the current.
        if first:
            self.__current_acceleration = a
        self.__previous_acceleration = self.__current_acceleration
        self.__current_acceleration = a
    
    def update_velocity(self, dt, next_acceleration):
        # Step the velocity forwards by dt
        a_component = (2 * next_acceleration + 5 * self.__current_acceleration - self.__previous_acceleration)
        self.__velocity += (1/6 * a_component * dt)

    def update_position(self, dt, iteration):
        # Step the position forwards by dt
        a_component = 4 * self.__current_acceleration - self.__previous_acceleration
        
        """If we have not yet recorded the orbital period for the body, and the y componenty of the position
        has changed from negative to positive, then update the period by dividing the current time by seconds in 
        a year, to give the period in terms of Earth years."""
        new_position = self.__position + (self.__velocity * dt) + (1/6 * a_component * dt**2)
        if self.__period is None and (self.__position[1] < 0 and new_position[1] >= 0):
            self.__period = dt * iteration / SECONDS_IN_EARTH_YEAR
       
        self.__position = new_position
    
    def calc_KE(self):
        # Return the current kinetic energy of the body
        return 0.5 * self.__mass * norm(self.__velocity) ** 2
    

class Simulation(object):

    def __init__(self, filename):
        """Initialise the simulation with data read in from the file called 'filename'. Store the number
        of iterations, the size of a time step and the list of CelestialBody objects"""
        (time_data, bodies) = self.__read(filename)
        self.__iterations = int(time_data[0])
        self.__dt = int(time_data[1])
        
        self.__bodies = []
        for body in bodies:
            # Create a new CelestialBody instance with the array of attributes unpacked as an argument
            self.__bodies.append(CelestialBody(*body))

        # Initially we don't know the distance and time of closest approach for the target and probe
        self.__closest_approach = None
        self.__approach_time = None
    
    def __read(self, filename):
        """Read in the data file by opening it, taking the first line as the iteration and time step values
        and all following lines each representing the data for a celestial body."""
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()

        time_data = lines[0].strip().split(' ') # Strip the data to remove any trailing new line characters
        lines.pop(0) # Remove the first line once processed as this is not a body
        
        bodies = []
        # For each line left, split up its data to form a list of arguments for a new body
        for line in lines:
            bodies.append(line.strip().split(' '))

        return (time_data, bodies)
    
    def get_closest_approach(self):
        return self.__closest_approach
    
    def get_approach_time(self):
        return self.__approach_time
    
    def __calc_acceleration(self, body1):
        """Calculate the acceleration that body1 experiences currently"""
        a = np.array([0, 0], dtype = float) # Initialise the acceleration to (0, 0)
        """For all other bodies, calculate the acceleraion caused by that body on body1, and add it to the 
        total acceleration vector"""
        for body2 in self.__bodies:
            if body1 == body2: # Skip past if it is the same body, as it doesn't cause itself to acceleration
                continue
            r12 = body2.get_position() - body1.get_position() # Calculate the vector from body1 to body2
            a_body1_body2 = (r12 / norm(r12)) * G  * body2.get_mass() / (norm(r12) ** 2)
            a += a_body1_body2 # Add the acceleration body1 experiences due to body2 to the total for body1
        return a

    def __step(self, i):
        """Take a step forward in the similation. For each body calculate the current acceleration. Then
        for each body update its position after a time of dt"""
        for body in self.__bodies:
            a = self.__calc_acceleration(body)
            body.update_acceleration(a, not i)
        for body in self.__bodies:
            body.update_position(self.__dt, i)
        for body in self.__bodies:
            next_acceleration = self.__calc_acceleration(body)
            body.update_velocity(self.__dt, next_acceleration)
        
        """Calculate the distance between the target and the probe. If we have not yet calculated a closest approach
        or if this is lower than the previous closest, then update the closest approach and update the time that 
        this occurs at."""
        new_closest = norm(self.__bodies[self.__target].get_position() - self.__bodies[self.__probe].get_position())
        if self.__closest_approach is None or new_closest < self.__closest_approach:
            self.__closest_approach = new_closest
            self.__approach_time = i * self.__dt

    def __total_KE(self):
        """Sum the kinetic energies of all the bodies in the simulation"""
        KE = 0
        for body in self.__bodies:
            KE += body.calc_KE()
        return KE
    
    def __total_PE(self):
        sum = 0
        for body1 in self.__bodies:
            for body2 in self.__bodies:
                if body1 == body2:
                    continue
                sum += G * body1.get_mass() * body2.get_mass() / norm(body2.get_position() - body1.get_position())
        return -0.5 * sum
    
    def __total_energy(self):
        return self.__total_PE() + self.__total_KE()

    def __animate(self, i):
        """For each new frame, take a step forward in the simulation, and move all of the circles (each representing a body)
        to the updated position. If the current iteration is a multiple of 50, write the energy to a file."""
        self.__step(i)
        
        for body in range(0, len(self.__bodies)):
            position = self.__bodies[body].get_position()
            self.__circles[body].center = (position[0], position[1])
        
        # If the iteration is a multiple of 50, write the total energy and time to the specified file.
        if i % 50 == 0:
            self.__energy_file.write(str(i * self.__dt) + " " +  str(self.__total_energy()) + "\n")
        return self.__circles
    
    def __without_animation(self):
        """Run the simulation without animating it. So iterate the specified number of times, taking a step each
        time and writing the total energy to the file every 50 iterations."""
        for i in range(0, self.__iterations):
            self.__step(i)
            if i % 50 == 0:
                self.__energy_file.write(str(i * self.__dt) + " " +  str(self.__total_energy()) + "\n")

    def run(self, scale, energy_file, target, probe, animate = False):
        """Run the simulation. If it is to be animated, create a 2D figure to show the animation. We
        take as input a scale on which to simulate and show the animation, the file to which the energy data should
        be written, and the index of the target and probe in the list of bodies."""

        self.__target = target
        self.__probe = probe
        
        self.__energy_file = open(energy_file, "w")

        if animate:
            fig = plt.figure()
            ax = plt.axes()

            ax.set_xlim(-3 * scale, 3 * scale)
            ax.set_ylim(-3 * scale, 3 * scale)

            self.__circles = []
            """For each body create a circle to represent it with its starting position, colour, nominal size and name. Add
            the circle to a list and then add it to the axes."""
            for body in self.__bodies:
                x = body.get_position()[0]
                y = body.get_position()[1]
                circle = plt.Circle((x, y), scale / 10 * body.get_size(), animated = True, color = body.get_colour(), label = body.get_name())
                self.__circles.append(circle)
                ax.add_patch(circle)

            # Run the animation with an interval of 20, and number of frames corresponding to self.__iterations
            FuncAnimation(fig, self.__animate, frames = self.__iterations, repeat = False, interval = 5, blit = True)

            plt.legend() # Provide a legend naming each celestial body
            plt.show()
        
        else:
            self.__without_animation()

        self.__energy_file.close()

        # At the end of the simulation, print the name and orbital period in terms of Earth years for each body
        for body in self.__bodies:
            print("Body:", body.get_name())
            print("Orbital Period:", body.get_period())
            print()