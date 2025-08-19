"""
Agent definitions for the Village to Town simulation.

This module defines the three main agent types:
- HouseholdAgent: Represents families making economic and social decisions
- BusinessAgent: Represents economic enterprises across different sectors  
- InfrastructureAgent: Represents infrastructure elements (roads, schools, etc.)
"""

import numpy as np
from mesa import Agent
from typing import Dict, List, Tuple, Optional


class HouseholdAgent(Agent):
    """
    Represents a household in the village/town simulation.
    
    Households make decisions about:
    - Education and health investments
    - Migration and location choices
    - Occupation and sector participation
    - Consumption and savings
    """
    
    def __init__(self, unique_id: int, model, pos: Tuple[int, int]):
        super().__init__(unique_id, model)
        self.pos = pos
        
        # Demographics
        self.household_size = np.random.randint(2, 8)
        self.age_head = np.random.randint(20, 65)
        self.gender_head = np.random.choice(['male', 'female'], p=[0.7, 0.3])
        
        # Economic status
        self.income = np.random.normal(3000, 1000)  # Monthly income in Taka
        self.savings = max(0, np.random.normal(5000, 3000))
        self.sector = np.random.choice(['agriculture', 'manufacturing', 'services'], 
                                     p=[0.6, 0.2, 0.2])
        
        # Human capital
        self.education_level = np.random.randint(0, 12)  # Years of education
        self.health_index = np.random.uniform(0.3, 1.0)  # 0-1 health index
        
        # Location preferences
        self.rural_attachment = np.random.uniform(0.2, 0.8)  # Preference for rural life
        self.migration_threshold = np.random.uniform(1.2, 2.0)  # Income multiplier to migrate
        
        # Behavioral parameters
        self.risk_tolerance = np.random.uniform(0.1, 0.9)
        self.social_capital = np.random.uniform(0.1, 1.0)
        
    def step(self):
        """Execute one step of household decision-making."""
        self.update_income()
        self.consider_migration()
        self.make_education_investment()
        self.make_health_investment()
        self.consider_sector_change()
        
    def update_income(self):
        """Update household income based on sector, location, and infrastructure access."""
        base_income = {
            'agriculture': 2500,
            'manufacturing': 4000,
            'services': 5000
        }[self.sector]
        
        # Infrastructure bonuses
        infrastructure_multiplier = 1.0
        if self.has_road_access():
            infrastructure_multiplier *= 1.2
        if self.has_market_access():
            infrastructure_multiplier *= 1.15
        if self.has_utility_access():
            infrastructure_multiplier *= 1.1
            
        # Education and health bonuses
        education_multiplier = 1 + (self.education_level * 0.05)
        health_multiplier = 0.5 + (self.health_index * 0.5)
        
        # Random variation
        random_factor = np.random.normal(1.0, 0.1)
        
        self.income = (base_income * infrastructure_multiplier * 
                      education_multiplier * health_multiplier * random_factor)
        
        # Update savings
        consumption = self.income * 0.8  # 80% consumption rate
        self.savings = max(0, self.savings + (self.income - consumption))
        
    def consider_migration(self):
        """Decide whether to migrate to a different location."""
        if self.sector == 'agriculture':
            return  # Farmers tied to land
            
        # Find best location based on income potential
        current_income_potential = self.calculate_income_potential(self.pos)
        
        # Check nearby locations
        for neighbor in self.model.grid.get_neighborhood(self.pos, moore=True, radius=2):
            neighbor_potential = self.calculate_income_potential(neighbor)
            
            if neighbor_potential > current_income_potential * self.migration_threshold:
                # Check if location is available
                if len(self.model.grid.get_cell_list_contents([neighbor])) < 5:  # Max density
                    if np.random.random() < (1 - self.rural_attachment):
                        self.model.grid.move_agent(self, neighbor)
                        break
                        
    def calculate_income_potential(self, pos: Tuple[int, int]) -> float:
        """Calculate potential income at a given position."""
        # Distance to town center (assuming center is at grid center)
        center_x, center_y = self.model.grid.width // 2, self.model.grid.height // 2
        distance_to_center = np.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2)
        
        # Urban proximity bonus
        urban_bonus = max(0, 1 - distance_to_center / 20)
        
        # Infrastructure access
        infrastructure_score = 0
        nearby_infrastructure = self.model.grid.get_neighbors(pos, moore=True, radius=3)
        for agent in nearby_infrastructure:
            if isinstance(agent, InfrastructureAgent):
                infrastructure_score += agent.get_productivity_bonus()
                
        return 1000 + (urban_bonus * 2000) + (infrastructure_score * 500)
        
    def make_education_investment(self):
        """Decide on education investments for household members."""
        if self.savings > 1000 and self.education_level < 12:
            education_cost = 500 * (self.education_level + 1)  # Increasing cost
            
            if self.savings > education_cost and np.random.random() < 0.3:
                self.savings -= education_cost
                self.education_level += 1
                
    def make_health_investment(self):
        """Decide on health investments."""
        if self.health_index < 0.8 and self.savings > 500:
            health_cost = 200
            if np.random.random() < 0.4:
                self.savings -= health_cost
                self.health_index = min(1.0, self.health_index + 0.1)
                
    def consider_sector_change(self):
        """Consider changing economic sector."""
        if self.education_level >= 8 and self.sector == 'agriculture':
            if np.random.random() < 0.1:  # 10% chance to switch
                self.sector = np.random.choice(['manufacturing', 'services'])
        elif self.education_level >= 10 and self.sector == 'manufacturing':
            if np.random.random() < 0.05:  # 5% chance to switch to services
                self.sector = 'services'
                
    def has_road_access(self) -> bool:
        """Check if household has access to roads."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=2)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'road' 
                  for agent in neighbors)
                  
    def has_market_access(self) -> bool:
        """Check if household has access to markets."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=3)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'market'
                  for agent in neighbors)
                  
    def has_utility_access(self) -> bool:
        """Check if household has access to utilities."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=2)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'utility'
                  for agent in neighbors)


class BusinessAgent(Agent):
    """
    Represents a business enterprise in the simulation.
    
    Businesses operate in different sectors and provide employment
    and economic activity in the developing town.
    """
    
    def __init__(self, unique_id: int, model, pos: Tuple[int, int], business_type: str):
        super().__init__(unique_id, model)
        self.pos = pos
        self.business_type = business_type  # 'agriculture', 'manufacturing', 'services'
        
        # Business characteristics
        self.size = np.random.choice(['small', 'medium', 'large'], p=[0.7, 0.25, 0.05])
        self.productivity = np.random.uniform(0.5, 1.5)
        self.capital = np.random.normal(50000, 20000) if self.size == 'large' else \
                      np.random.normal(20000, 10000) if self.size == 'medium' else \
                      np.random.normal(5000, 2000)
        
        # Employment
        self.max_employees = {'small': 5, 'medium': 20, 'large': 50}[self.size]
        self.current_employees = 0
        
        # Financial
        self.revenue = 0
        self.profit = 0
        
    def step(self):
        """Execute one step of business operations."""
        self.update_productivity()
        self.calculate_revenue()
        self.hire_employees()
        self.consider_expansion()
        
    def update_productivity(self):
        """Update productivity based on infrastructure access."""
        base_productivity = self.productivity
        
        # Infrastructure bonuses
        if self.has_road_access():
            base_productivity *= 1.3
        if self.has_utility_access():
            base_productivity *= 1.2
        if self.has_market_access():
            base_productivity *= 1.1
            
        self.current_productivity = base_productivity
        
    def calculate_revenue(self):
        """Calculate business revenue based on productivity and employees."""
        base_revenue = {
            'agriculture': 1000,
            'manufacturing': 2000,
            'services': 1500
        }[self.business_type]
        
        employee_factor = 1 + (self.current_employees * 0.1)
        self.revenue = base_revenue * self.current_productivity * employee_factor
        
        # Operating costs
        operating_costs = self.current_employees * 2000  # Employee wages
        infrastructure_costs = 500 if self.has_utility_access() else 200
        
        self.profit = self.revenue - operating_costs - infrastructure_costs
        
    def hire_employees(self):
        """Decide on hiring based on demand and profitability."""
        if self.profit > 5000 and self.current_employees < self.max_employees:
            # Look for available workers
            nearby_households = self.model.grid.get_neighbors(self.pos, moore=True, radius=5)
            available_workers = [agent for agent in nearby_households 
                               if isinstance(agent, HouseholdAgent) and 
                               agent.sector == self.business_type]
            
            if available_workers and np.random.random() < 0.3:
                self.current_employees += 1
                
    def consider_expansion(self):
        """Consider business expansion if profitable."""
        if self.profit > 20000 and self.size == 'small':
            if np.random.random() < 0.1:
                self.size = 'medium'
                self.max_employees = 20
                self.capital *= 2
        elif self.profit > 50000 and self.size == 'medium':
            if np.random.random() < 0.05:
                self.size = 'large'
                self.max_employees = 50
                self.capital *= 3
                
    def has_road_access(self) -> bool:
        """Check if business has access to roads."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=2)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'road'
                  for agent in neighbors)
                  
    def has_market_access(self) -> bool:
        """Check if business has access to markets."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=3)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'market'
                  for agent in neighbors)
                  
    def has_utility_access(self) -> bool:
        """Check if business has access to utilities."""
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=2)
        return any(isinstance(agent, InfrastructureAgent) and agent.infrastructure_type == 'utility'
                  for agent in neighbors)


class InfrastructureAgent(Agent):
    """
    Represents infrastructure elements in the simulation.
    
    Infrastructure includes roads, schools, clinics, markets, and utilities
    that provide services and boost productivity in their coverage areas.
    """
    
    def __init__(self, unique_id: int, model, pos: Tuple[int, int], 
                 infrastructure_type: str):
        super().__init__(unique_id, model)
        self.pos = pos
        self.infrastructure_type = infrastructure_type
        
        # Infrastructure characteristics
        self.coverage_radius = {
            'road': 1,
            'school': 3,
            'clinic': 4,
            'market': 5,
            'utility': 2
        }[infrastructure_type]
        
        self.capacity = {
            'road': 1000,  # Traffic capacity
            'school': 200,  # Students
            'clinic': 100,  # Patients per month
            'market': 50,   # Vendors
            'utility': 500  # Connections
        }[infrastructure_type]
        
        self.construction_cost = {
            'road': 10000,
            'school': 50000,
            'clinic': 30000,
            'market': 20000,
            'utility': 40000
        }[infrastructure_type]
        
        self.maintenance_cost = self.construction_cost * 0.05  # 5% annual maintenance
        self.quality = 1.0  # Degrades over time
        self.age = 0
        
    def step(self):
        """Execute one step of infrastructure operations."""
        self.age += 1
        self.degrade_quality()
        self.provide_services()
        
    def degrade_quality(self):
        """Infrastructure quality degrades over time."""
        degradation_rate = 0.02  # 2% per year
        self.quality = max(0.1, self.quality - degradation_rate)
        
    def provide_services(self):
        """Provide services to agents in coverage area."""
        coverage_area = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.coverage_radius
        )
        
        # Count served population
        served_households = [agent for agent in coverage_area 
                           if isinstance(agent, HouseholdAgent)]
        served_businesses = [agent for agent in coverage_area 
                           if isinstance(agent, BusinessAgent)]
        
        # Update model statistics
        self.model.infrastructure_coverage[self.infrastructure_type] = len(served_households)
        
    def get_productivity_bonus(self) -> float:
        """Calculate productivity bonus provided by this infrastructure."""
        base_bonus = {
            'road': 0.2,
            'school': 0.15,
            'clinic': 0.1,
            'market': 0.25,
            'utility': 0.2
        }[self.infrastructure_type]
        
        return base_bonus * self.quality
        
    def get_maintenance_cost(self) -> float:
        """Get annual maintenance cost."""
        return self.maintenance_cost * (2 - self.quality)  # Higher cost for poor quality
        
    def upgrade(self, investment: float) -> bool:
        """Upgrade infrastructure with investment."""
        upgrade_cost = self.construction_cost * 0.3  # 30% of construction cost
        
        if investment >= upgrade_cost:
            self.quality = min(1.0, self.quality + 0.3)
            self.capacity *= 1.2
            return True
        return False
