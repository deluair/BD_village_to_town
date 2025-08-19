"""
Main simulation model for the Village to Town development simulation.

This module contains the TownDevelopmentModel class which coordinates
all agents, manages the spatial environment, handles scheduling,
and collects data for analysis.
"""

import numpy as np
import pandas as pd
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from typing import Dict, List, Tuple, Any
import yaml

from .agents import HouseholdAgent, BusinessAgent, InfrastructureAgent
from .policy import PolicyEngine


class TownDevelopmentModel(Model):
    """
    Main model class for the Village to Town development simulation.
    
    Manages the spatial grid, agent scheduling, policy interventions,
    and data collection for analyzing development outcomes.
    """
    
    def __init__(self, config_path: str = None, **kwargs):
        super().__init__()
        
        # Load configuration
        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()
            
        # Override config with any provided kwargs
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                
        # Initialize model components
        self.setup_space()
        self.setup_scheduling()
        self.setup_data_collection()
        self.setup_policy_engine()
        
        # Model state
        self.step_count = 0
        self.total_population = 0
        self.total_businesses = 0
        self.infrastructure_coverage = {
            'road': 0, 'school': 0, 'clinic': 0, 'market': 0, 'utility': 0
        }
        
        # Initialize agents
        self.create_initial_population()
        self.create_initial_businesses()
        self.create_initial_infrastructure()
        
        # Start data collection
        self.datacollector.collect(self)
        
    def setup_space(self):
        """Initialize the spatial grid."""
        self.grid = MultiGrid(
            width=self.config['grid_width'],
            height=self.config['grid_height'],
            torus=False
        )
        
    def setup_scheduling(self):
        """Initialize agent scheduling."""
        self.schedule = RandomActivation(self)
        
    def setup_data_collection(self):
        """Initialize data collection system."""
        model_reporters = {
            "Step": lambda m: m.step_count,
            "Population": lambda m: m.total_population,
            "Total_Businesses": lambda m: m.total_businesses,
            "GDP_Per_Capita": self.calculate_gdp_per_capita,
            "Gini_Coefficient": self.calculate_gini_coefficient,
            "Average_Education": self.calculate_average_education,
            "Average_Health": self.calculate_average_health,
            "Urbanization_Rate": self.calculate_urbanization_rate,
            "Infrastructure_Coverage": self.calculate_infrastructure_coverage,
            "Service_Access_Rate": self.calculate_service_access_rate,
            "Agricultural_Employment": lambda m: m.count_by_sector('agriculture'),
            "Manufacturing_Employment": lambda m: m.count_by_sector('manufacturing'),
            "Services_Employment": lambda m: m.count_by_sector('services'),
            "Road_Coverage": lambda m: m.infrastructure_coverage['road'],
            "School_Coverage": lambda m: m.infrastructure_coverage['school'],
            "Clinic_Coverage": lambda m: m.infrastructure_coverage['clinic'],
            "Market_Coverage": lambda m: m.infrastructure_coverage['market'],
            "Utility_Coverage": lambda m: m.infrastructure_coverage['utility'],
        }
        
        agent_reporters = {
            "Agent_Type": lambda a: type(a).__name__,
            "Position_X": lambda a: a.pos[0] if hasattr(a, 'pos') else None,
            "Position_Y": lambda a: a.pos[1] if hasattr(a, 'pos') else None,
            "Income": lambda a: getattr(a, 'income', None),
            "Education": lambda a: getattr(a, 'education_level', None),
            "Health": lambda a: getattr(a, 'health_index', None),
            "Sector": lambda a: getattr(a, 'sector', None),
            "Savings": lambda a: getattr(a, 'savings', None),
            "Business_Type": lambda a: getattr(a, 'business_type', None),
            "Business_Size": lambda a: getattr(a, 'size', None),
            "Revenue": lambda a: getattr(a, 'revenue', None),
            "Employees": lambda a: getattr(a, 'current_employees', None),
            "Infrastructure_Type": lambda a: getattr(a, 'infrastructure_type', None),
            "Quality": lambda a: getattr(a, 'quality', None),
            "Coverage_Radius": lambda a: getattr(a, 'coverage_radius', None),
        }
        
        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )
        
    def setup_policy_engine(self):
        """Initialize the policy intervention system."""
        self.policy_engine = PolicyEngine(
            model=self,
            annual_budget=self.config['policy_budget'],
            config=self.config.get('policy_config', {})
        )
        
    def create_initial_population(self):
        """Create initial household population."""
        n_households = self.config['initial_population']
        
        for i in range(n_households):
            # Place households with some clustering
            if i < n_households * 0.7:  # 70% in rural areas
                x = np.random.randint(0, self.grid.width // 3)
                y = np.random.randint(0, self.grid.height // 3)
            else:  # 30% in initial town center
                center_x = self.grid.width // 2
                center_y = self.grid.height // 2
                x = np.random.randint(center_x - 5, center_x + 5)
                y = np.random.randint(center_y - 5, center_y + 5)
                
            x = max(0, min(x, self.grid.width - 1))
            y = max(0, min(y, self.grid.height - 1))
            
            household = HouseholdAgent(i, self, (x, y))
            self.grid.place_agent(household, (x, y))
            self.schedule.add(household)
            
        self.total_population = n_households
        
    def create_initial_businesses(self):
        """Create initial business population."""
        n_businesses = self.config['initial_businesses']
        
        for i in range(n_businesses):
            # Business type distribution
            business_type = np.random.choice(
                ['agriculture', 'manufacturing', 'services'],
                p=[0.5, 0.3, 0.2]
            )
            
            # Location based on business type
            if business_type == 'agriculture':
                x = np.random.randint(0, self.grid.width // 2)
                y = np.random.randint(0, self.grid.height // 2)
            else:
                center_x = self.grid.width // 2
                center_y = self.grid.height // 2
                x = np.random.randint(center_x - 10, center_x + 10)
                y = np.random.randint(center_y - 10, center_y + 10)
                
            x = max(0, min(x, self.grid.width - 1))
            y = max(0, min(y, self.grid.height - 1))
            
            business = BusinessAgent(
                self.total_population + i, self, (x, y), business_type
            )
            self.grid.place_agent(business, (x, y))
            self.schedule.add(business)
            
        self.total_businesses = n_businesses
        
    def create_initial_infrastructure(self):
        """Create initial infrastructure."""
        infrastructure_types = ['road', 'school', 'clinic', 'market', 'utility']
        
        # Start with basic infrastructure in town center
        center_x = self.grid.width // 2
        center_y = self.grid.height // 2
        
        agent_id = self.total_population + self.total_businesses
        
        # Place one of each infrastructure type near center
        for i, infra_type in enumerate(infrastructure_types):
            x = center_x + np.random.randint(-3, 4)
            y = center_y + np.random.randint(-3, 4)
            x = max(0, min(x, self.grid.width - 1))
            y = max(0, min(y, self.grid.height - 1))
            
            infrastructure = InfrastructureAgent(
                agent_id + i, self, (x, y), infra_type
            )
            self.grid.place_agent(infrastructure, (x, y))
            self.schedule.add(infrastructure)
            
        # Add some initial roads connecting areas
        for i in range(5):
            x = np.random.randint(0, self.grid.width)
            y = np.random.randint(0, self.grid.height)
            
            road = InfrastructureAgent(
                agent_id + len(infrastructure_types) + i, self, (x, y), 'road'
            )
            self.grid.place_agent(road, (x, y))
            self.schedule.add(road)
            
    def step(self):
        """Execute one step of the simulation."""
        self.step_count += 1
        
        # Agent actions
        self.schedule.step()
        
        # Policy interventions (every 5 steps = annually)
        if self.step_count % 5 == 0:
            self.policy_engine.execute_annual_policies()
            
        # Update model statistics
        self.update_statistics()
        
        # Collect data
        self.datacollector.collect(self)
        
    def update_statistics(self):
        """Update model-level statistics."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        businesses = [agent for agent in self.schedule.agents 
                     if isinstance(agent, BusinessAgent)]
        
        self.total_population = len(households)
        self.total_businesses = len(businesses)
        
    def calculate_gdp_per_capita(self) -> float:
        """Calculate GDP per capita."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        businesses = [agent for agent in self.schedule.agents 
                     if isinstance(agent, BusinessAgent)]
        
        total_income = sum(h.income for h in households) * 12  # Annual income
        total_business_revenue = sum(b.revenue for b in businesses) * 12
        
        total_gdp = total_income + total_business_revenue
        
        return total_gdp / max(1, self.total_population) if self.total_population > 0 else 0
        
    def calculate_gini_coefficient(self) -> float:
        """Calculate Gini coefficient for income inequality."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        if len(households) < 2:
            return 0
            
        incomes = [h.income for h in households]
        incomes.sort()
        
        n = len(incomes)
        cumsum = np.cumsum(incomes)
        
        return (n + 1 - 2 * sum((n + 1 - i) * income for i, income in enumerate(incomes, 1))) / (n * sum(incomes))
        
    def calculate_average_education(self) -> float:
        """Calculate average education level."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        if not households:
            return 0
            
        return sum(h.education_level for h in households) / len(households)
        
    def calculate_average_health(self) -> float:
        """Calculate average health index."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        if not households:
            return 0
            
        return sum(h.health_index for h in households) / len(households)
        
    def calculate_urbanization_rate(self) -> float:
        """Calculate percentage of population in urban areas."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        if not households:
            return 0
            
        center_x = self.grid.width // 2
        center_y = self.grid.height // 2
        urban_radius = 10
        
        urban_households = 0
        for h in households:
            distance = np.sqrt((h.pos[0] - center_x)**2 + (h.pos[1] - center_y)**2)
            if distance <= urban_radius:
                urban_households += 1
                
        return urban_households / len(households)
        
    def calculate_infrastructure_coverage(self) -> float:
        """Calculate overall infrastructure coverage rate."""
        total_coverage = sum(self.infrastructure_coverage.values())
        max_possible = self.total_population * 5  # 5 types of infrastructure
        
        return total_coverage / max(1, max_possible)
        
    def calculate_service_access_rate(self) -> float:
        """Calculate percentage of population with access to basic services."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        if not households:
            return 0
            
        households_with_services = 0
        for h in households:
            services_count = 0
            if h.has_road_access():
                services_count += 1
            if h.has_market_access():
                services_count += 1
            if h.has_utility_access():
                services_count += 1
                
            # Consider having access if 2+ services available
            if services_count >= 2:
                households_with_services += 1
                
        return households_with_services / len(households)
        
    def count_by_sector(self, sector: str) -> int:
        """Count households employed in a specific sector."""
        households = [agent for agent in self.schedule.agents 
                     if isinstance(agent, HouseholdAgent)]
        
        return sum(1 for h in households if h.sector == sector)
        
    def add_infrastructure(self, pos: Tuple[int, int], infrastructure_type: str) -> bool:
        """Add new infrastructure at specified position."""
        # Check if position is valid and not overcrowded
        contents = self.grid.get_cell_list_contents([pos])
        infrastructure_count = sum(1 for agent in contents 
                                 if isinstance(agent, InfrastructureAgent))
        
        if infrastructure_count >= 2:  # Max 2 infrastructure per cell
            return False
            
        # Create new infrastructure
        new_id = max([agent.unique_id for agent in self.schedule.agents]) + 1
        infrastructure = InfrastructureAgent(new_id, self, pos, infrastructure_type)
        
        self.grid.place_agent(infrastructure, pos)
        self.schedule.add(infrastructure)
        
        return True
        
    def get_model_data(self) -> pd.DataFrame:
        """Get model-level data as DataFrame."""
        return self.datacollector.get_model_vars_dataframe()
        
    def get_agent_data(self) -> pd.DataFrame:
        """Get agent-level data as DataFrame."""
        return self.datacollector.get_agent_vars_dataframe()
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration parameters."""
        return {
            'grid_width': 50,
            'grid_height': 50,
            'initial_population': 200,
            'initial_businesses': 30,
            'policy_budget': 100000,
            'policy_config': {
                'infrastructure_weights': {
                    'road': 0.3,
                    'school': 0.2,
                    'clinic': 0.2,
                    'market': 0.15,
                    'utility': 0.15
                },
                'grant_program_budget': 20000,
                'microfinance_budget': 15000
            }
        }
