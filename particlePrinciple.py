import pygame
import random
import sys

from constants import WHITE

class ParticlePrinciple:
    def __init__(self, screen):
        self.screen = screen
        self.particles = []

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][1] += particle[2][0]
                particle[0][0] += particle[2][1]
                particle[1] -= 0.2
                pygame.draw.circle(self.screen, pygame.Color('White'), particle[0], int(particle[1]))

    def add_particles(self, position):
        pos_x, pos_y = position
        radius = 10
        direction_x = random.randint(-3, 3)
        direction_y = random.randint(-3, 3)
        particle_circle = [[pos_x, pos_y], radius, [direction_x, direction_y]]
        self.particles.append(particle_circle)

    def delete_particles(self):
        self.particles = [particle for particle in self.particles if particle[1] > 0]
