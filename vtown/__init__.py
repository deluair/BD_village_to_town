"""
Village to Town: Bangladesh Development Simulation

An agent-based model simulating the transformation of a Bangladeshi village
into a town through infrastructure development and policy interventions.
"""

from .agents import HouseholdAgent, BusinessAgent, InfrastructureAgent
from .model import TownDevelopmentModel
from .policy import PolicyEngine

__version__ = "1.0.0"
__author__ = "Village to Town Development Team"

__all__ = [
    "HouseholdAgent",
    "BusinessAgent", 
    "InfrastructureAgent",
    "TownDevelopmentModel",
    "PolicyEngine",
]
