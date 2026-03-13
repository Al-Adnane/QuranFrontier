"""Autonomous Vehicles Network - Self-Driving Cars.

Inspired by: Autonomous Vehicle Technology
"""

import torch
import torch.nn as nn


class AutonomousVehiclesNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Sensing systems
        self.lidar = nn.Linear(input_dim, embed_dim)
        self.radar = nn.Linear(input_dim, embed_dim)
        self.camera = nn.Linear(input_dim, embed_dim)
        self.ultrasonic = nn.Linear(input_dim, embed_dim)
        # Decision systems
        self.path_planning = nn.Linear(input_dim, embed_dim)
        self.obstacle_avoidance = nn.Linear(input_dim, embed_dim)
        # Driving safety
        self.safety = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        sensors = [self.lidar(x), self.radar(x), self.camera(x), self.ultrasonic(x)]
        decisions = [self.path_planning(x), self.obstacle_avoidance(x)]
        return {
            'sensing_systems': {
                'lidar': self.lidar(x),
                'radar': self.radar(x),
                'camera': self.camera(x),
                'ultrasonic': self.ultrasonic(x)
            },
            'decision_systems': {
                'path_planning': self.path_planning(x),
                'obstacle_avoidance': self.obstacle_avoidance(x)
            },
            'driving_safety': torch.sigmoid(self.safety(torch.cat(sensors + decisions, -1)))
        }


def create_autonomous_vehicles_network(input_dim: int = 128, embed_dim: int = 256):
    return AutonomousVehiclesNetwork(input_dim, embed_dim)
